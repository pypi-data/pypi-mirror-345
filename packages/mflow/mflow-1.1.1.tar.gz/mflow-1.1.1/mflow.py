import argparse
import asyncio
import logging
import mimetypes
import os
import re
import random

from typing import Dict, Optional, Tuple, Set
from urllib.parse import unquote, urlparse, quote, urlunparse
from aiohttp import (
    web,
    TCPConnector,
    ClientSession,
    ClientTimeout,
    ClientError,
)
from colorama import init as colorama_init, Fore, Style

# Constants
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
)
CHUNK_SIZE = 1 << 20  # 1 MB
MAX_WORKERS = 4  # 并行下载数
MAX_REDIRECTS = 3  # 最大重定向次数
MAX_RETRIES = 4  # 每个块最大重试次数
LOG_LEVEL = "INFO"
PORT = 80


# Colored logging formatter
class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN,
        logging.INFO: Fore.WHITE,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, "")
        msg = super().format(record)
        return f"{color}{msg}{Style.RESET_ALL}"


def get_base_url(url: str, have_path=True) -> str:
    """
    返回不包含参数(query)和锚点(fragment)的 URL 部分。
    """
    parts = urlparse(url)
    if have_path:
        return urlunparse((parts.scheme, parts.netloc, parts.path, "", "", ""))
    else:
        return urlunparse((parts.scheme, parts.netloc, "", "", "", ""))


class LinkInfo:
    def __init__(self, url: str, client=None):
        self.original_url = url
        self.redirect_url = url
        self.support_range = False
        self.filesize: Optional[int] = None
        self.filename: Optional[str] = None
        self.minetype = "application/octet-stream"
        self.client = (
            ClientSession(
                connector=TCPConnector(limit=MAX_WORKERS, keepalive_timeout=60),
                timeout=ClientTimeout(total=None),
                headers={"User-Agent": USER_AGENT},
            )
            if client is None
            else client
        )
        logger.debug(f"LinkInfo initialized for {url}")

    async def close(self):
        await self.client.close()
        logger.debug(f"LinkInfo closed for {self.original_url}")


async def update_info(info: LinkInfo, request_id: str) -> Optional[web.Response]:
    sess = info.client
    current_url = info.original_url
    try:
        logger.debug(
            f"[{request_id}] Checking resource info: {str(get_base_url(current_url))}"
        )
        resp = await sess.head(current_url, allow_redirects=False)
        depth = 0

        # 处理重定向
        while resp.status in (301, 302, 303, 307, 308) and depth < MAX_REDIRECTS:
            loc = resp.headers.get("Location")
            if not loc:
                logger.warning(f"[{request_id}] Redirect without Location")
                return web.HTTPBadGateway(reason="Invalid redirect")
            current_url = loc
            resp = await sess.head(current_url, allow_redirects=False)
            depth += 1

        if info.redirect_url != current_url:
            info.redirect_url = current_url
            logger.info(
                f"[{request_id}] Redirected to {str(get_base_url(current_url))}"
            )

        # 检查是否支持 Range
        headers = {"Range": "bytes=0-"}
        async with sess.get(info.redirect_url, headers=headers) as r2:
            info.support_range = r2.status == 206 and "Content-Range" in r2.headers
            info.filesize = int(r2.headers.get("Content-Length", "0")) or None
            logger.info(
                f"[{request_id}] Range supported={info.support_range}, size={info.filesize}"
            )
            # 文件名解析逻辑
            cd = r2.headers.get("content-disposition", "")
            filename = None
            if cd:
                # 解析filename*
                if m := re.search(
                    r"filename\*\s*=\s*(UTF-8|utf-8)?''?([^;]+)", cd, re.IGNORECASE
                ):
                    filename = unquote(m.group(2))
                # 解析普通filename
                elif m := re.search(r'filename\s*=\s*"([^"]+)"', cd, re.IGNORECASE):
                    filename = m.group(1)

            # 回落到URL路径
            if not filename:
                parsed = urlparse(info.redirect_url)
                filename = unquote(parsed.path.rsplit("/", 1)[-1] or "download")

            # 补充扩展名
            base, ext = os.path.splitext(filename)
            if not ext:
                ct = r2.headers.get("content-type", "").split(";")[0].strip()
                if guessed := mimetypes.guess_extension(ct):
                    filename += guessed

            # 清理非法字符
            filename = re.sub(r'[\x00<>:"/\\|?*]', "_", filename).strip()

            # 更新MIME
            mime_type, _ = mimetypes.guess_type(filename)
            if (
                r2.headers.get("content-type", "application/oct-stream")
                != "application/oct-stream"
            ):
                info.minetype = r2.headers["content-type"]
            elif mime_type:
                info.minetype = mime_type

            info.filename = filename[:255]  # 限制最大长度

            logger.info(f"[{request_id}] Filename resolved: {info.filename}")
        return None

    except ClientError as e:
        logger.warning(f"[{request_id}] ClientError during info update: {e}")
        return web.HTTPBadGateway(reason="Upstream error")
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}", exc_info=True)
        return web.HTTPInternalServerError()


def parse_range(header: str) -> Tuple[int, Optional[int]]:
    m = re.match(r"bytes=(\d+)-(\d+)?", header or "")
    if not m:
        return 0, None
    start = int(m.group(1))
    end = int(m.group(2)) if m.group(2) else None
    return start, end


# Custom exception for incomplete chunks
class IncompleteChunkError(Exception):
    pass


# Custom exception for incomplete response
class IncompleteResponseError(Exception):
    pass


class MultiFlow:
    def __init__(self):
        self.link_cache: Dict[str, LinkInfo] = {}
        self.client_cache: Dict[str, ClientSession] = {}
        self.request_counter = 0
        logger.info("MultiFlow controller initialized")

    async def close(self):
        logger.info(f"Closing {len(self.link_cache)} link connections")
        for info in self.link_cache.values():
            await info.close()
        self.link_cache.clear()
        logger.info("All link connections closed")

    async def handle_request(self, request: web.Request) -> web.StreamResponse:
        # 生成两位 request_id
        self.request_counter += 1
        request_id = f"{self.request_counter % 100:02d}"

        key = "?url="
        idx = str(request.url).find(key)
        if idx == -1:
            url = ""
        else:
            url = str(request.url)[idx + len(key) :]
        # url = request.query.get("url")
        if not url:
            return web.HTTPBadRequest(reason="Missing url parameter")
        logger.info(f"[{request_id}] Incoming stream request: {str(get_base_url(url))}")

        # 解析 Range
        range_hdr = request.headers.get("Range", "")
        start, end = parse_range(range_hdr)
        logger.info(
            f"[{request_id}] Range header: {range_hdr or 'NONE'} -> {start}-{end or 'EOF'}"
        )

        # 获取或创建 LinkInfo
        if url not in self.link_cache:
            logger.info(f"[{request_id}] Link miss, init LinkInfo")
            base_url = get_base_url(url, False)
            if base_url in self.client_cache:
                logger.info(f"[{request_id}] Client hit, share ClientSession")
                info = LinkInfo(url, self.client_cache[base_url])
            else:
                logger.info(f"[{request_id}] Client miss, init ClientSession")
                info = LinkInfo(url)
            err = await update_info(info, request_id)
            if err:
                await info.close()
                return err
            if info.support_range:
                self.link_cache[url] = info
                self.client_cache[base_url] = info.client
            else:
                logger.error("URL unsupport range")
                return web.HTTPForbidden()
        else:
            info = self.link_cache[url]
            logger.info(f"[{request_id}] Cache hit: {info.filename}")

        if info.filesize is None:
            return web.HTTPBadGateway(reason="Content length unknown")

        # 计算边界
        end = end or (info.filesize - 1)
        end = min(end, info.filesize - 1)
        if start < 0 or start > end or start >= info.filesize:
            return web.HTTPBadRequest(
                headers={"Content-Range": f"bytes */{info.filesize}"},
                reason="Range not satisfiable",
            )

        total_len = end - start + 1
        headers = {
            "Content-Type": info.minetype,
            "Accept-Ranges": "bytes",
            "Content-Length": str(total_len),
        }
        if info.filename:
            headers["Content-Disposition"] = (
                f"inline; filename*=UTF-8''{quote(info.filename)}"
            )
        status = 206 if (start > 0 or end < info.filesize - 1) else 200
        if status == 206:
            headers["Content-Range"] = f"bytes {start}-{end}/{info.filesize}"

        # 准备响应
        resp = web.StreamResponse(status=status, headers=headers)
        await resp.prepare(request)
        logger.info(f"[{request_id}] Response prepared, streaming...")

        next_chunk_start = start
        in_flight: Set[asyncio.Task] = set()
        chunk_id = 1
        stream_chunk_id = 1
        lock = asyncio.Lock()
        updateInfo = True

        # 下载一个 chunk 的协程
        async def fetch_chunk(chunk_start: int, id: int):
            nonlocal stream_chunk_id, updateInfo
            chunk_end = min(chunk_start + CHUNK_SIZE - 1, end)
            current_start = chunk_start
            buffer = bytearray()
            buffer_written = False

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    async with info.client.get(
                        info.redirect_url,
                        headers={"Range": f"bytes={current_start}-{chunk_end}"},
                    ) as r:
                        if r.status != 206:
                            r.release()
                            raise IncompleteChunkError(
                                f"bad response status {r.status}"
                            )
                        updateInfo = False

                        async def data_generator():
                            async for data in r.content.iter_any():
                                if data:
                                    yield data
                            while True:
                                yield b""

                        async for data in data_generator():
                            await lock.acquire()
                            if stream_chunk_id != id:
                                lock.release()
                                buffer.extend(data)
                                current_start += len(data)
                                await asyncio.sleep(0.1)
                                continue
                            try:
                                if not buffer_written:
                                    await resp.write(buffer)
                                    buffer_written = True
                                if data:
                                    await resp.write(data)
                                    current_start += len(data)
                                else:
                                    stream_chunk_id += 1
                                    break
                            except Exception as e:
                                raise IncompleteResponseError(str(e))
                            finally:
                                lock.release()

                        if current_start - 1 == chunk_end:
                            logger.debug(
                                f"[{request_id}] Chunk({id}) {chunk_start}-{chunk_end} OK"
                            )
                            return
                        else:
                            raise IncompleteChunkError("bad data length")

                except (ClientError, IncompleteChunkError) as e:
                    backoff = 0.8 * (2 ** (attempt - 1))
                    jitter = random.uniform(0, 0.1 * attempt)
                    delay = backoff + jitter
                    logger.warning(
                        f"[{request_id}] Chunk({id}) "
                        f"attempt {attempt}/{MAX_RETRIES} failed: {e}. "
                        f"retry after {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)

                except asyncio.CancelledError:
                    # 取消时直接退出
                    return

                except IncompleteResponseError:
                    raise

                except Exception as e:
                    logger.error(f"[{request_id}] Chunk({id}) unknown error: {e}")

            raise IncompleteChunkError(
                f"[{request_id}] Chunk {chunk_start}-{chunk_end} failed after "
                f"{MAX_RETRIES} attempts"
            )

        # 取消所有挂起任务
        async def cancel_all():
            for t in in_flight:
                t.cancel()
            await asyncio.gather(*in_flight, return_exceptions=True)

        # 启动初始下载任务
        try:
            # 启动并行下载
            while len(in_flight) < MAX_WORKERS and next_chunk_start <= end:
                t = asyncio.create_task(fetch_chunk(next_chunk_start, chunk_id))
                in_flight.add(t)
                next_chunk_start += CHUNK_SIZE
                chunk_id += 1
                # 保持优先级
                await asyncio.sleep(0.1)

            # 滑动窗口以创建任务
            while in_flight:
                done, _ = await asyncio.wait(
                    in_flight, return_when=asyncio.FIRST_COMPLETED
                )
                for t in done:
                    in_flight.remove(t)
                    await t

                # 补充新任务
                while len(in_flight) < MAX_WORKERS and next_chunk_start <= end:
                    t = asyncio.create_task(fetch_chunk(next_chunk_start, chunk_id))
                    in_flight.add(t)
                    next_chunk_start += CHUNK_SIZE
                    chunk_id += 1

            logger.info(f"[{request_id}] Streaming done, sent {total_len} bytes")

        except Exception as e:
            logger.error(f"[{request_id}] Streaming error: {e}")

        await cancel_all()
        logger.info(f"[{request_id}] Response end")

        if updateInfo:
            logger.warning(f"[{request_id}] Too many errors, try to update LinkInfo")
            await update_info(info, request_id)

        return resp


def init_var():
    global CHUNK_SIZE, PORT, LOG_LEVEL, MAX_WORKERS, MAX_RETRIES

    parser = argparse.ArgumentParser(
        description="Multi Flow - Concurrent Streaming Proxy"
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=PORT,
        help=f"Port to listen on (default: {PORT})",
    )
    parser.add_argument(
        "-r",
        "--retry",
        default=MAX_RETRIES,
        help=f"Maximum number of retries (default: {MAX_RETRIES})",
    )
    parser.add_argument(
        "-c",
        "--connections",
        type=int,
        default=MAX_WORKERS,
        help=f"Number of concurrent connections per stream (default: {MAX_WORKERS})",
    )
    parser.add_argument(
        "-s",
        "--chunk-size",
        type=str,
        default=f"{CHUNK_SIZE // 1024 // 1024}M",
        help="Size of chunks for parallel downloads (e.g., 1M, 512K) (default: 1M)",
    )
    parser.add_argument(
        "--log-level",
        default=LOG_LEVEL,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"Set logging level (default: {LOG_LEVEL})",
    )
    args = parser.parse_args()
    if hasattr(args, "help"):
        return None

    # --- Parse Chunk Size ---
    size_str: str = args.chunk_size.upper()
    try:
        if size_str.endswith("K"):
            args.chunk_size = int(size_str[:-1]) * 1024
        elif size_str.endswith("M"):
            args.chunk_size = int(size_str[:-1]) * 1024 * 1024
        else:
            args.chunk_size = int(size_str)
    except ValueError:
        parser.error(
            f"Invalid chunk size format: {args.chunk_size}. Use numbers, K, or M."
        )
        return False

    # Only change in there
    PORT = int(args.port)
    CHUNK_SIZE = int(args.chunk_size)
    MAX_WORKERS = int(args.connections)
    MAX_RETRIES = int(args.retry)
    LOG_LEVEL = str(args.log_level)

    return True


def init_app():
    global logger

    # Initialize colorama
    colorama_init(autoreset=True)
    # Configure logger
    logger = logging.getLogger("Mflow")
    handler = logging.StreamHandler()
    handler.setFormatter(
        ColoredFormatter(fmt="%(asctime)s [%(levelname).4s] %(message)s")
    )
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(LOG_LEVEL)
    logger.info("Initializing application")

    mf = MultiFlow()
    app = web.Application()
    app.router.add_get("/stream", mf.handle_request)
    app.on_cleanup.append(lambda app: mf.close())

    logger.info(f"Starting server on 0.0.0.0:{PORT}")
    return app


def main():
    if init_var():
        web.run_app(init_app(), host="0.0.0.0", port=PORT, access_log=None, print=None)


if __name__ == "__main__":
    LOG_LEVEL = "DEBUG"
    web.run_app(init_app(), host="0.0.0.0", port=PORT, access_log=None, print=None)

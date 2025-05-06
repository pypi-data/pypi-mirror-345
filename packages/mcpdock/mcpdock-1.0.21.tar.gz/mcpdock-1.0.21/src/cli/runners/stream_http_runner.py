"""
Streamable HTTP Runner implementation for remote MCP servers (streaming HTTP transport, stdio proxy)
"""
import json
import asyncio
import signal
import sys
import time
from typing import Dict, Any, Optional, Awaitable

from rich import print as rprint
from ..utils.logger import verbose
import aiohttp

IDLE_TIMEOUT = 10 * 60  # 10分钟，单位：秒
MAX_RETRIES = 5
RETRY_DELAY = 2  # 秒，指数退避基数


async def create_stream_http_runner(
    base_url: str,
    config: Dict[str, Any],
    api_key: Optional[str] = None
) -> Awaitable[None]:
    """
    Creates a streamable HTTP runner for connecting to a remote server using stdio as proxy.
    """
    retry_count = 0
    stdin_buffer = ""
    is_ready = False
    is_shutting_down = False
    is_client_initiated_close = False
    last_activity = time.time()
    idle_check_task = None
    session = None
    post_task = None
    response_task = None
    stop_event = asyncio.Event()

    def log_with_timestamp(msg):
        verbose(f"[Runner] {msg}")

    def update_last_activity():
        nonlocal last_activity
        last_activity = time.time()

    async def cleanup():
        nonlocal is_shutting_down, is_client_initiated_close, idle_check_task, session, post_task, response_task
        if is_shutting_down:
            log_with_timestamp("Cleanup already in progress, skipping duplicate cleanup...")
            return
        log_with_timestamp("Starting cleanup process...")
        is_shutting_down = True
        is_client_initiated_close = True
        if idle_check_task:
            idle_check_task.cancel()
        if post_task:
            post_task.cancel()
        if response_task:
            response_task.cancel()
        if session:
            await session.close()
        log_with_timestamp("Cleanup completed")
        stop_event.set()

    async def handle_exit(*_):
        log_with_timestamp("Received exit signal, initiating shutdown...")
        await cleanup()
        sys.exit(0)

    def start_idle_check():
        nonlocal idle_check_task

        async def idle_checker():
            while True:
                await asyncio.sleep(60)
                idle_time = time.time() - last_activity
                if idle_time >= IDLE_TIMEOUT:
                    log_with_timestamp(f"Connection idle for {int(idle_time // 60)} minutes, initiating shutdown")
                    await handle_exit()
                    break
        idle_check_task = asyncio.create_task(idle_checker())

    async def post_stream():
        nonlocal is_ready, retry_count, session, response_task
        log_with_timestamp(f"Connecting to HTTP stream endpoint: {base_url}")
        url = base_url  # TODO: 按需拼接 config/api_key
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        # 用队列做流式输入
        input_queue = asyncio.Queue()

        async def stdin_reader():
            nonlocal stdin_buffer
            while not is_shutting_down:
                data = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.buffer.readline)
                if not data:
                    log_with_timestamp("STDIN closed (client disconnected)")
                    await handle_exit()
                    break
                update_last_activity()
                stdin_buffer += data.decode("utf-8")
                lines = stdin_buffer.split("\n")
                stdin_buffer = lines.pop() if lines else ""
                for line in [l for l in lines if l.strip()]:
                    try:
                        await input_queue.put(json.loads(line))
                    except Exception as e:
                        log_with_timestamp(f"Failed to parse stdin line: {e}")

        async def gen():
            # 先发 config
            yield json.dumps({"config": config}) + "\n"
            while not is_shutting_down:
                msg = await input_queue.get()
                yield json.dumps(msg) + "\n"
        session = aiohttp.ClientSession()
        try:
            resp = await session.post(url, data=gen(), headers=headers, timeout=None)
            is_ready = True
            log_with_timestamp("HTTP stream connection established")
            start_idle_check()
            # 启动响应流处理
            response_task = asyncio.create_task(response_stream(resp))
            # 启动stdin读取
            await stdin_reader()
        except Exception as e:
            log_with_timestamp(f"HTTP stream error: {e}")
            await handle_exit()

    async def response_stream(resp):
        try:
            async for line in resp.content:
                update_last_activity()
                try:
                    # 只处理非空行
                    s = line.decode("utf-8").strip()
                    if not s:
                        continue
                    # 允许服务端返回多行JSON
                    for l in s.split("\n"):
                        if l.strip():
                            print(l)
                except Exception as e:
                    log_with_timestamp(f"Error handling response: {e}")
        except Exception as e:
            log_with_timestamp(f"HTTP response stream error: {e}")
            await handle_exit()

    # 信号处理
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(handle_exit()))
        except NotImplementedError:
            signal.signal(sig, lambda *_: asyncio.create_task(handle_exit()))

    # 启动主流式POST任务
    post_task = asyncio.create_task(post_stream())
    rprint(f"[green]Streamable HTTP connection established: {base_url}[/green]")
    rprint("Press Ctrl+C to stop the connection")
    await stop_event.wait()

# 用法示例：
# await create_stream_http_runner("https://example.com/stream", {"foo": "bar"}, api_key="xxx")

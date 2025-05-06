"""
STDIO Runner implementation for local MCP servers

This module provides functionality for creating and managing a connection with an MCP server
through standard input/output pipes.
"""
import json
import asyncio
from logging import error
import mcp.types as types
import signal
import sys
import os
import anyio
import threading
from typing import Dict, Any, Optional, Awaitable
from contextlib import AsyncExitStack

from ..utils.logger import verbose
from ..types.registry import RegistryServer
from ..utils.runtime import get_runtime_environment
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

# 导入工具模块
from ..utils.process_utils import find_server_process_by_command, save_pid_to_file
from ..utils.mcp_utils import (
    process_client_request,
    handle_single_server_message,
    initialize_session
)


async def create_stdio_runner(
    server_details: RegistryServer,
    config: Dict[str, Any],
    api_key: Optional[str] = None,
    analytics_enabled: bool = False
) -> Awaitable[None]:
    """创建并运行 STDIO 代理服务器"""
    verbose(f"Starting STDIO proxy runner: {server_details.qualifiedName}")
    is_shutting_down = False
    exit_stack = AsyncExitStack()

    def handle_error(error: Exception, context: str) -> Exception:
        verbose(f"[Runner] {context}: {error}")
        return error

    async def cleanup() -> None:
        nonlocal is_shutting_down
        if is_shutting_down:
            verbose("[Runner] Cleanup already in progress, skipping...")
            return
        verbose("[Runner] Starting cleanup...")
        is_shutting_down = True
        try:
            # Remove PID by server name and client name
            from ..utils.process_utils import remove_pid_by_server_name

            # 尝试获取第三级进程作为客户端标识 - 与保存时使用相同的逻辑
            client_name = "unknown_client"
            try:
                import psutil
                current_process = psutil.Process()

                # 收集完整的进程链
                process_chain = []
                process = current_process
                while process:
                    process_chain.append(process.name())
                    process = process.parent()

                # 打印完整进程链用于调试
                verbose(f"[Runner] 清理时的完整进程链: {' -> '.join(reversed(process_chain))}")

                # 尝试获取第四级进程（如果存在）
                if len(process_chain) >= 3:
                    client_name = process_chain[2]
                    verbose(f"[Runner] 清理时使用第四级进程作为客户端: {client_name}")
                else:
                    # 如果进程链不够长，使用最后一个进程（顶层进程）
                    client_name = process_chain[-1] if process_chain else "unknown_client"
                    verbose(f"[Runner] 清理时进程链不够长，使用顶层进程作为客户端: {client_name}")
            except Exception as e:
                verbose(f"[Runner] 清理时获取客户端进程名称失败: {e}，使用默认值: {client_name}")

            remove_pid_by_server_name(server_details.qualifiedName, client_name)
            verbose(f"[Runner] 已从PID文件中移除服务器 '{server_details.qualifiedName}' 的客户端 '{client_name}' 记录")

            await exit_stack.aclose()
            verbose("[Runner] Resources closed successfully")
        except Exception as error:
            handle_error(error, "Error during cleanup")
        verbose("[Runner] Cleanup completed")

    async def handle_sigint():
        verbose("[Runner] Received interrupt signal, shutting down...")
        await cleanup()
        # 立即打印一条确认消息，让用户知道CTRL+C已被捕获
        verbose("\n[CTRL+C] 正在关闭服务，请稍候...")
        # 可选：设置一个短暂的超时，然后强制退出
        import threading
        threading.Timer(2.0, lambda: os._exit(0)).start()

    # 获取连接配置
    stdio_connection = next((conn for conn in server_details.connections if conn.type == "stdio"), None)
    if not stdio_connection:
        raise ValueError("No STDIO connection found")

    from ..utils.config import build_runtime_args_and_env
    # 运行阶段：根据元数据和 config 组装最终 args/env
    final_args, final_env = build_runtime_args_and_env(stdio_connection, config)
    command = stdio_connection.stdioFunction[0] if stdio_connection.stdioFunction else "python"
    env = get_runtime_environment(final_env)
    verbose(f"Using environment: {json.dumps({k: '***' if k.lower().endswith('key') else v for k, v in env.items()})}")
    verbose(f"Executing: {command} {' '.join(final_args)}")

    try:
        # 创建服务器进程
        server_params = StdioServerParameters(
            command=command,
            args=final_args,
            env=env,
            encoding="utf-8"
        )

        verbose(f"Setting up stdio proxy client for {server_details.qualifiedName}")
        async with stdio_client(server_params, errlog=sys.stderr) as (read_stream, write_stream):
            verbose("Stdio proxy client connection established")

            # 查找服务器进程ID - 优先使用父子进程关系
            from ..utils.process_utils import find_server_process_by_command, save_pid_to_file, find_server_process_from_current

            # 首先尝试通过父子进程关系查找
            is_found_from_current, current_pid, cmd_str = find_server_process_from_current()
            if is_found_from_current and current_pid:
                verbose(f"[Runner] 通过父子进程关系找到服务器进程，PID: {current_pid}")
                server_pid = current_pid
            else:
                # 如果父子进程关系查找失败，尝试通过命令行查找
                server_pid = find_server_process_by_command(command, final_args)

            if server_pid:
                verbose(f"[Runner] 已找到MCP服务器进程，PID: {server_pid}")

                # 将进程ID写入PID文件
                # 尝试获取第四级进程作为客户端标识
                client_name = "unknown_client"
                try:
                    import psutil
                    current_process = psutil.Process()

                    # 收集完整的进程链
                    process_chain = []
                    process = current_process
                    while process:
                        process_chain.append(process.name())
                        process = process.parent()

                    # 打印完整进程链用于调试
                    verbose(f"[Runner] 完整进程链: {' -> '.join(reversed(process_chain))}")

                    # 尝试获取第四级进程（如果存在）
                    if len(process_chain) >= 3:
                        client_name = process_chain[2]
                        verbose(f"[Runner] 使用第三级进程作为客户端: {client_name}")
                    else:
                        # 如果进程链不够长，使用最后一个进程（顶层进程）
                        client_name = process_chain[-1] if process_chain else "unknown_client"
                        verbose(f"[Runner] 进程链不够长，使用顶层进程作为客户端: {client_name}")
                except Exception as e:
                    verbose(f"[Runner] 获取客户端进程名称失败: {e}，使用默认值: {client_name}")

                verbose(f"[Runner] 使用 '{client_name}' 作为客户端标识")
                pid_file_path = save_pid_to_file(server_pid, server_details.qualifiedName,
                                                 client_name, command, final_args)
                if pid_file_path:
                    verbose(f"[Runner] 已将服务器PID信息安全地保存到: {pid_file_path}")
            else:
                verbose(f"[Runner] 未能找到MCP服务器进程，将无法获取其PID")

            # 创建 MCP 客户端会话
            from mcp import ClientSession
            session = await exit_stack.enter_async_context(ClientSession(read_stream, write_stream))

            # 注册消息处理回调
            def handle_server_message(msg):
                verbose(f"[magenta][server][/magenta] {json.dumps(msg, ensure_ascii=False)}")
            session.on_message = handle_server_message

            # 初始化 MCP 协议
            if not await initialize_session(session):
                return

            # 使用简单的同步阻塞循环处理输入和服务器消息
            verbose("[Runner] 开始处理循环，使用同步阻塞模式")

            # 打印启动消息
            verbose("[cyan]MCP client running. Press Ctrl+C to stop.[/cyan]")

            # 获取事件循环并在主任务中添加信号处理程序
            loop = asyncio.get_event_loop()
            loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(handle_sigint()))

            # 循环处理客户端请求，直到关闭
            while not is_shutting_down:
                try:
                    # 从标准输入读取一行 (同步阻塞)
                    line = sys.stdin.readline()
                    if not line:
                        verbose("[Runner] 标准输入关闭，结束处理")
                        break

                    # 处理客户端请求
                    message = json.loads(line)
                    verbose(f"[stdin] Received message: {line.strip()}")

                    method = message.get("method", "")
                    # 根据消息类型处理
                    if "id" in message:  # 这是请求，需要响应
                        response = await process_client_request(message, session)
                        sys.stdout.write(response + "\n")
                        sys.stdout.flush()
                        verbose(f"[stdin] Response sent for method: {method}")
                    else:  # 这是通知，不需要响应
                        # 创建通知对象并发送
                        # notification_obj = create_request_object(message, method)
                        # await session.send_notification(notification_obj)
                        await session.send_notification(
                            types.ClientNotification(
                                types.InitializedNotification(method=method)
                            )
                        )
                        verbose(f"[stdin] Notification sent for method: {method}")

                    verbose(f"[stdin] Processed: {line.strip()}")

                except json.JSONDecodeError as e:
                    error(f"[stdin] JSON decode error: {e}")
                except Exception as e:
                    error(f"[stdin] Error processing input: {e}")
                    # 如果是请求(有ID)，才需要发送错误响应
                    try:
                        if 'message' in locals() and isinstance(message, dict) and "id" in message:
                            error_resp = json.dumps({
                                "jsonrpc": "2.0",
                                "id": message.get("id"),
                                "error": {
                                    "code": -32700,
                                    "message": f"Parse error: {str(e)}"
                                }
                            })
                            sys.stdout.write(error_resp + "\n")
                            sys.stdout.flush()
                            verbose(f"[stdin] Sent error response for parse error")
                    except Exception as err:
                        error(f"[stdin] Failed to send error response: {err}")

                # 检查是否有服务器消息需要处理
                # 注意：这部分仍需异步，因为我们需要非阻塞地检查服务器消息
                try:
                    # 使用超时机制非阻塞地检查服务器消息
                    with anyio.fail_after(0.1):  # 设置很短的超时
                        message = await read_stream.receive()
                        await handle_single_server_message(message)
                except TimeoutError:
                    # 超时表示没有消息，继续处理客户端请求
                    pass
                except Exception as e:
                    error(f"[Runner] 处理服务器消息异常: {e}")

            verbose("[Runner] 处理循环结束")

    except Exception as e:
        verbose(f"[red]Error running stdio proxy: {e}[/red]")
        raise
    finally:
        await cleanup()

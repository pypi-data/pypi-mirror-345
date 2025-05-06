"""
MCP 协议请求/响应处理工具模块

该模块提供了处理 MCP 协议请求和响应的工具函数，包括：
- 创建请求对象
- 发送请求并处理超时
- 处理服务器消息
"""
import json
import anyio
import traceback
from typing import Dict, Any, Optional
from logging import error
import sys

from ..utils.logger import verbose
from mcp.types import ClientRequest, ServerRequest
from pydantic import BaseModel

# 定义一个通用的 Model，用于接收任何 JSON 响应


class DictModel(BaseModel):
    @classmethod
    def model_validate(cls, value):
        if isinstance(value, dict):
            return value
        return dict(value)


def create_request_object(message: Dict[str, Any], method: str):
    """
    根据方法类型创建适当的请求对象

    Args:
        message: JSON-RPC 消息
        method: 请求方法名

    Returns:
        MCP 请求对象
    """
    # 作为代理，我们不需要严格验证方法是否符合标准列表
    # 直接创建ClientRequest对象，透明转发所有请求
    msg = dict(message)
    msg.pop("jsonrpc", None)  # 移除 jsonrpc 字段，SDK会自动添加
    msg.pop("id", None)       # 移除 id 字段，我们会在响应中重新添加

    try:
        # 尝试创建 ClientRequest
        return ClientRequest(**msg)
    except Exception as e:
        verbose('---------------------------------------')
        verbose(msg)
        verbose('---------------------------------------')
        # 如果创建失败，记录详细错误信息并回退到 ServerRequest
        verbose(f"[Runner] 创建 ClientRequest 失败，错误信息: {str(e)}，回退到 ServerRequest")
        return ServerRequest(method=method, params=message.get("params", {}))


async def send_request_with_timeout(session, req_obj, original_id, timeout_seconds=60):
    """
    发送请求并处理超时和错误情况

    Args:
        session: MCP 客户端会话
        req_obj: 请求对象
        original_id: 原始请求ID
        timeout_seconds: 超时时间(秒)

    Returns:
        JSON-RPC 响应字符串
    """
    try:
        # 初始化 resp 为 None，防止超时时未定义
        resp = None
        # 使用超时机制
        with anyio.move_on_after(timeout_seconds):
            # 记录请求信息
            verbose(f"[Runner] 发送请求，原始ID={original_id}, 方法={req_obj.method if hasattr(req_obj, 'method') else '未知'}")

            # 发送请求并等待响应
            resp = await session.send_request(req_obj, DictModel)

        if resp:
            # 直接使用原始ID构造响应
            return json.dumps({
                "id": original_id,
                "jsonrpc": "2.0",
                "result": resp
            })
        else:
            return json.dumps({
                "id": original_id,
                "jsonrpc": "2.0",
                "error": {
                    "code": -32000,
                    "message": "Request timed out or empty response"
                }
            })

    except Exception as e:
        # 处理请求错误
        error_msg = str(e)
        error_code = -32603

        # 分类错误类型
        if "timed out" in error_msg.lower():
            error_code = -32001
        elif "connection" in error_msg.lower():
            error_code = -32002

        return json.dumps({
            "id": original_id,
            "jsonrpc": "2.0",
            "error": {
                "code": error_code,
                "message": f"Request failed: {error_msg}"
            }
        })


async def process_client_request(message, session):
    """
    处理从客户端接收的请求并转发到服务器

    Args:
        message: 客户端请求消息
        session: MCP 客户端会话

    Returns:
        响应字符串
    """
    original_id = message.get("id")
    method = message.get("method")
    params = message.get("params", {})

    # 添加特殊处理，记录初始化请求的详细信息
    if method == "initialize":
        verbose(f"[Runner] 收到初始化请求 ID: {original_id}, 详细内容: {json.dumps(message)}")

        # 对初始化请求使用SDK的initialize方法，而不是简单转发
        try:
            verbose("[Runner] 使用SDK的initialize方法处理初始化请求")
            # 先创建正确的请求对象
            req_obj = create_request_object(message, method)

            # 发送实际的初始化请求到下游服务器
            verbose("[Runner] 向下游服务器发送初始化请求")
            init_result = await session.send_request(req_obj, DictModel)
            verbose(
                f"[Runner] 收到下游服务器初始化响应: {json.dumps(init_result)[:200] if isinstance(init_result, dict) else str(init_result)[:200]}...")

            # 确保我们有一个有效的响应
            if init_result is None:
                verbose("[Runner] 收到空的初始化响应，创建默认响应")
                init_result = {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "mcpy-proxy",
                        "version": "1.0.0"
                    }
                }

            # 构造完整的JSON-RPC响应
            response = json.dumps({
                "jsonrpc": "2.0",
                "id": original_id,
                "result": init_result
            })

            verbose(f"[Runner] 构造的初始化响应: {response[:200]}...")
            return response
        except Exception as e:
            error(f"[Runner] 初始化请求处理失败: {str(e)}")
            error(f"[Runner] 异常堆栈: {traceback.format_exc()}")
            # 如果处理失败，回退到常规请求处理
            verbose("[Runner] 回退到常规请求处理方式")

    verbose(f"[stdin] Processing request with id: {original_id}, method: {method}")

    # 常规请求处理：确定请求类型和构建请求对象
    req_obj = create_request_object(message, method)

    # 发送请求并处理响应
    try:
        verbose(f"[Runner] 向下游服务器发送请求，method: {method}, id: {original_id}")
        result = await send_request_with_timeout(session, req_obj, original_id)

        if method == "initialize":
            verbose(f"[Runner] 收到初始化响应: {result}")

        return result
    except Exception as e:
        error(f"[Runner] 请求处理异常 ({method}): {str(e)}")
        raise


async def handle_single_server_message(data):
    """
    处理单个从服务器接收的消息并输出到标准输出

    Args:
        data: 服务器消息数据
    """
    try:
        # 记录接收到的原始数据类型，帮助调试
        verbose(f"[server_raw] Received data type: {type(data)}")

        # 尝试获取原始数据的字符串表示用于调试
        raw_data_str = str(data)
        if len(raw_data_str) > 500:
            raw_data_str = raw_data_str[:500] + "..."
        verbose(f"[server_raw] 原始数据: {raw_data_str}")

        # 根据数据类型进行处理
        if hasattr(data, "model_dump"):
            content = data.model_dump()
            verbose(f"[server_raw] Processed pydantic v2 model: {type(data)}")
        elif hasattr(data, "dict"):
            content = data.dict()
            verbose(f"[server_raw] Processed pydantic v1 model: {type(data)}")
        elif isinstance(data, dict):
            content = data
            verbose(f"[server_raw] Processed dict with {len(data)} keys")
        else:
            # 尝试转换为字符串，然后解析为JSON
            try:
                content = json.loads(str(data))
                verbose(f"[server_raw] Converted to JSON: {type(data)}")
            except:
                content = {"data": str(data)}
                verbose(f"[server_raw] Used raw string for unknown type: {type(data)}")

        # 检查是否是初始化响应
        is_init_response = False
        if isinstance(content, dict):
            if "result" in content and isinstance(content["result"], dict):
                result = content["result"]
                if "protocolVersion" in result or "serverInfo" in result:
                    is_init_response = True
                    verbose(f"[server] 检测到初始化响应: {json.dumps(content)[:200]}...")

                # 特别检查是否包含tools字段，这对于VSCode非常重要
                if "tools" in result:
                    verbose(f"[server] 检测到tools字段，工具数量: {len(result['tools'])}")

        # 检查数据是否已经是标准的 JSON-RPC 消息
        if isinstance(content, dict):
            if "jsonrpc" in content and ("id" in content or "method" in content):
                # 已经是标准格式，直接输出
                output = json.dumps(content)
                verbose(f"[server] Standard JSON-RPC message detected, id: {content.get('id')}")

            elif "result" in content and not "jsonrpc" in content:
                # 是结果但缺少 jsonrpc 字段，构造标准响应
                output = json.dumps({
                    "jsonrpc": "2.0",
                    "id": 1,  # 默认ID，应该不会被用到
                    "result": content["result"] if "result" in content else content
                })
                verbose(f"[server] Fixed response format by adding jsonrpc")

            else:
                # 其他类型的消息，包装为通知
                output = json.dumps(content)
                verbose("[server] Passing through data as-is")
        else:
            # 非字典类型，直接序列化
            output = json.dumps(content)

        # 写入 stdout 并立即刷新，确保 VS Code 能收到
        sys.stdout.write(output + "\n")
        sys.stdout.flush()
        verbose(f"[server] Response sent to stdout: {output}")

    except Exception as e:
        error(f"[server] Error processing server message: {e}")
        error(f"[server] 异常堆栈: {traceback.format_exc()}")
        # 尝试发送错误响应
        try:
            error_resp = json.dumps({
                "jsonrpc": "2.0",
                "id": 1,  # 使用默认ID
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            })
            sys.stdout.write(error_resp + "\n")
            sys.stdout.flush()
            verbose(f"[server] Sent error response due to: {e}")
        except:
            error("[server] Failed to send error response")


async def initialize_session(session):
    """
    初始化 MCP 协议会话，转发上游客户端的初始化请求到下游服务器

    Args:
        session: MCP 客户端会话

    Returns:
        初始化是否成功
    """
    try:
        # 关键点: 作为代理，我们不应该主动调用 session.initialize()
        # 上游客户端会发送初始化请求，我们应该在 handle_stdin 函数中处理
        verbose("[Runner] MCP 代理准备就绪，等待上游客户端的初始化请求...")
        return True
    except Exception as init_error:
        error_msg = f"代理初始化失败: {str(init_error)}"
        error(f"[Runner] {error_msg}")
        return False

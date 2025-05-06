"""
Registry module for MCP servers.

This module handles resolving package names to server metadata and fetching configuration.
"""
from typing import Dict, Any, Tuple, Optional
import json
import os
import aiohttp
from cli.config.app_config import API_BASE  # 添加 HTTP 客户端库

from .utils.logger import verbose
from .types.registry import (
    RegistryServer, ConnectionDetails, ConfigSchema, ConfigSchemaProperty
)


MOCK_SERVERS_PATH = os.path.join(os.path.dirname(__file__), "mock_servers.json")


def _load_mock_servers():
    with open(MOCK_SERVERS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _dict_to_registry_server(data):
    # Helper to recursively convert dict to dataclasses
    def _to_config_schema_property(prop):
        return ConfigSchemaProperty(**prop)

    def _to_config_schema(schema):
        env = {k: _to_config_schema_property(v) for k, v in schema.get("env", {}).items()}
        return ConfigSchema(env=env, required=schema.get("required", []), args=schema.get("args"))

    def _to_connection_details(conn):
        config_schema = None
        if "configSchema" in conn and conn["configSchema"]:
            config_schema = _to_config_schema(conn["configSchema"])
        return ConnectionDetails(
            type=conn["type"],
            stdioFunction=conn.get("stdioFunction"),
            deploymentUrl=conn.get("deploymentUrl"),
            published=conn.get("published"),
            configSchema=config_schema
        )
    return RegistryServer(
        qualifiedName=data["qualifiedName"],
        displayName=data["displayName"],
        remote=data["remote"],
        connections=[_to_connection_details(c) for c in data["connections"]]
    )


mock_servers_data = _load_mock_servers()


# 定义 API 基础 URL
# API_BASE_URL = "http://your-php-api-url"  # 替换为您实际的 PHP API URL
API_BASE_URL = f"{API_BASE}/api/v1"


async def resolve_package(package_name: str) -> RegistryServer:
    """
    Resolves a package name to server metadata by calling the PHP API.

    Args:
        package_name: The qualified name of the package to resolve

    Returns:
        RegistryServer object with the server metadata
    """
    verbose(f"Resolving package {package_name} via API")

    try:
        async with aiohttp.ClientSession() as session:
            # 调用 PHP 的 getByQualifiedName API
            async with session.get(f"{API_BASE_URL}/mcp-servers/{package_name}") as response:
                if response.status == 200:
                    # 获取响应数据 - PHP API 直接返回原始数据，不被 data 字段包裹
                    server_data = await response.json()

                    # 将 API 响应数据转换为 RegistryServer 对象
                    return _dict_to_registry_server(server_data)
                else:
                    verbose(f"API error: {response.status} - {await response.text()}")

                    # 如果 API 调用失败，可以选择回退到本地 mock 数据
                    verbose("Falling back to mock data")
                    # Find server by qualifiedName in the array
                    data = next(
                        (server for server in mock_servers_data if server["qualifiedName"] == package_name), None)
                    if not data:
                        # Fallback to default if available
                        data = next(
                            (server for server in mock_servers_data if server["qualifiedName"] == "default"), None)
                    if not data:
                        # If still not found and we have at least one server, use the first one as fallback
                        data = mock_servers_data[0] if mock_servers_data else None

                    return _dict_to_registry_server(data) if data else None
    except Exception as e:
        verbose(f"Error calling API: {str(e)}")
        # 发生异常时回退到 mock 数据
        verbose("Falling back to mock data due to exception")
        data = next((server for server in mock_servers_data if server["qualifiedName"] == package_name), None)
        if not data:
            data = next((server for server in mock_servers_data if server["qualifiedName"] == "default"), None)
        if not data:
            data = mock_servers_data[0] if mock_servers_data else None

        return _dict_to_registry_server(data) if data else None


async def fetch_connection(
    package_name: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fetches server connection details for a package with given configuration.

    This function uses the package name to resolve the server details and then
    formats the connection configuration based on the schema and user provided config.

    Args:
        package_name: The name of the package to fetch connection details for
        config: User-provided configuration values

    Returns:
        Dictionary containing command, args and env configuration for the connection
    """
    verbose(f"Fetching connection details for {package_name} with config: {config}")

    # Get server metadata first
    server_data = await resolve_package(package_name)

    # Find stdio connection
    stdio_connection = next((conn for conn in server_data.connections if conn.type == "stdio"), None)
    if not stdio_connection:
        verbose("No stdio connection found in server metadata")
        return {}

    # Get command type (npx, uv, etc.) from stdioFunction
    command = "python"  # Default as fallback
    if stdio_connection.stdioFunction and len(stdio_connection.stdioFunction) > 0:
        command = stdio_connection.stdioFunction[0]

    # Get args from the connection schema
    args = []
    if stdio_connection.configSchema and stdio_connection.configSchema.args:
        args = stdio_connection.configSchema.args
    else:
        # Fallback default
        args = ["-m", package_name]

    # Return formatted connection config
    connection_config = {
        "command": command,
        "args": args,
        "env": config  # User-provided environment variables
    }

    verbose(f"Formatted connection config: {connection_config}")
    return connection_config


async def fetch_config_with_api_key(
    package_name: str,
    api_key: str
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Fetches server and configuration information using an API key.

    Args:
        package_name: The name of the package to fetch configuration for
        api_key: The API key to authenticate with

    Returns:
        A tuple containing (server_info, config_info)
    """
    verbose(f"Mock fetching config for {package_name} using API key")

    # This is a placeholder implementation
    # In a real implementation, this would make an API call
    # to retrieve the server and configuration information

    return {}, {}  # Empty dicts for now as placeholder

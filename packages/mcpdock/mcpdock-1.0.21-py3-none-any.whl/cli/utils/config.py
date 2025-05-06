import json
import os
from cli.utils.logger import verbose
import questionary
from rich import print as verbose
from typing import Any, Dict, List, Optional, Set, Tuple, TypeVar
from ..config.app_config import APP_ENV


# Import proper types from registry module
from ..types.registry import (
    ConnectionDetails, RegistryServer,
    ServerConfig, ConfiguredServer, ConfigSchemaProperty
)


def convert_value_to_type(value: Any, type_str: Optional[str]) -> Any:
    """Converts a value to the specified type string."""
    if not type_str:
        return value

    def invalid(expected: str):
        raise ValueError(f"Invalid {expected} value: {json.dumps(value)}")

    try:
        if type_str == "boolean":
            str_val = str(value).lower()
            if str_val == "true":
                return True
            if str_val == "false":
                return False
            invalid("boolean")
        elif type_str == "number":
            return float(value)
        elif type_str == "integer":
            return int(value)
        elif type_str == "string":
            return str(value)
        elif type_str == "array":
            if isinstance(value, list):
                return value
            return [v.strip() for v in str(value).split(",")]
        else:
            return value
    except (ValueError, TypeError):
        invalid(type_str)


def format_config_values(
    connection: ConnectionDetails,
    config_values: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Formats and validates config values based on the connection's schema."""
    formatted_values: Dict[str, Any] = {}
    missing_required: List[str] = []
    config_values = config_values or {}

    schema = connection.configSchema or {}
    env = schema.env if schema else {}
    if not env:
        return config_values

    required: Set[str] = set(schema.required if schema else [])

    for property_name, prop_details in env.items():
        value = config_values.get(property_name)
        prop_type = prop_details.type

        if value is None:
            if property_name in required:
                missing_required.append(property_name)
            else:
                formatted_values[property_name] = prop_details.default
        else:
            try:
                formatted_values[property_name] = convert_value_to_type(value, prop_type)
            except ValueError as e:
                # If conversion fails but it's not required, set to default or None
                if property_name not in required:
                    formatted_values[property_name] = prop_details.default
                else:
                    # Re-raise or handle error if conversion fails for a required field
                    # For now, let's add to missing required to indicate an issue
                    verbose(f"Warning: Could not convert required value for {property_name}: {e}")
                    missing_required.append(f"{property_name} (invalid format)")

    if missing_required:
        raise ValueError(
            f"Missing or invalid required config values: {', '.join(missing_required)}"
        )

    return formatted_values


def validate_config(
    connection: ConnectionDetails,
    saved_config: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Validates saved config against the connection schema."""
    schema = connection.configSchema or {}
    env = schema.env if schema else {}
    if not env:
        return True, {}

    saved_config = saved_config or {}

    try:
        formatted_config = format_config_values(connection, saved_config)
        required = set(schema.required if schema else [])
        has_all_required = all(
            key in formatted_config and formatted_config[key] is not None
            for key in required
        )
        return has_all_required, formatted_config
    except ValueError:
        # Attempt to return partially valid config if formatting fails
        try:
            partial_config = {
                k: v for k, v in saved_config.items() if v is not None
            }
            # Check if the partial config *still* satisfies required fields *that are present*
            # This is tricky, maybe just return False and the original partial config
            return False, partial_config
        except Exception:
            return False, None


async def prompt_for_config_value(
    key: str,
    schema_prop: ConfigSchemaProperty,
    required: Set[str],
) -> Any:
    """Prompts the user for a single config value based on schema property."""
    is_required = key in required
    required_text = " [red](required)[/red]" if is_required else " (optional)"
    message = f"{schema_prop.description or f'Enter value for {key}'}{required_text}"
    prop_type = schema_prop.type
    default_value = schema_prop.default

    # Determine questionary prompt type
    if key.lower().endswith("key") or key.lower().endswith("secret") or key.lower().endswith("token"):
        prompt_method = questionary.password
    elif prop_type == "boolean":
        prompt_method = questionary.confirm
        # questionary confirm default needs bool or None
        if default_value is not None:
            default_value = str(default_value).lower() == 'true'
        else:
            default_value = None  # Or False if you prefer
    elif prop_type == "number" or prop_type == "integer":
        # Using text prompt with validation for numbers
        prompt_method = questionary.text
    elif prop_type == "array":
        message += " (comma-separated)"
        prompt_method = questionary.text
    else:
        prompt_method = questionary.text

    # Validation function
    def validate_input(text: str) -> bool | str:
        if is_required and not text:
            return "This field is required."
        if prop_type == "number" or prop_type == "integer":
            try:
                if prop_type == "integer":
                    int(text)
                else:
                    float(text)
                return True
            except ValueError:
                return "Please enter a valid number."
        return True

    # Use appropriate prompt method
    if prompt_method == questionary.confirm:
        # Handle confirm separately as it doesn't take validate
        # Note: questionary.confirm returns True/False directly
        # We need to handle the case where the user might skip an optional confirm
        # For simplicity, let's assume confirm always gets an answer if prompted
        answer = await prompt_method(message, default=default_value).ask_async()
        # If it's required and they somehow skip (e.g., Ctrl+C), handle appropriately
        if is_required and answer is None:
            verbose("[bold red]Required field cannot be skipped.[/bold red]")
            # Re-prompt or exit - for now, return None which might fail later validation
            return None
        return answer
    else:
        # For text, password
        q = prompt_method(
            message,
            default=str(default_value) if default_value is not None else "",
            validate=validate_input
        )
        result = await q.ask_async()
        if result is None and is_required:
            verbose("[bold red]Required field cannot be skipped.[/bold red]")
            return None  # Or raise an error / re-prompt
        # Convert back if needed (e.g., for numbers, arrays)
        if result is not None:
            try:
                return convert_value_to_type(result, prop_type)
            except ValueError:
                verbose(
                    f"[yellow]Warning: Could not convert input '{result}' to type '{prop_type}'. Using raw input.[/yellow]")
                return result  # Return raw input if conversion fails after prompt
        return result  # Return None if skipped (and not required)


async def collect_config_values(
    connection: ConnectionDetails,
    existing_values: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Collects config values from existing values or user prompts."""
    schema = connection.configSchema or {}
    env = schema.env if schema else {}
    if not env:
        return {}

    base_config: Dict[str, Any] = {}

    # Validate existing values first
    if existing_values:
        is_valid, validated_config = validate_config(connection, existing_values)
        if is_valid and validated_config is not None:
            return validated_config
        # Use partially validated config as base if validation failed
        base_config = validated_config or {}

    required = set(schema.required if schema else [])

    verbose("[bold blue]Please provide the following configuration values:[/bold blue]")

    for key, prop_details in env.items():
        # Skip if value already exists and is not None in the base_config
        if key in base_config and base_config[key] is not None:
            continue

        # Prompt if missing
        value = await prompt_for_config_value(key, prop_details, required)

        # Handle skipped required fields after prompt
        if value is None and key in required:
            # This case should ideally be handled within prompt_for_config_value
            # but as a fallback:
            verbose(f"[bold red]Error: Required configuration '{key}' was not provided.[/bold red]")
            raise ValueError(f"Missing required configuration: {key}")

        # Assign even if None (for optional fields skipped)
        base_config[key] = value

    # Final format and validation after collecting all values
    try:
        return format_config_values(connection, base_config)
    except ValueError as e:
        verbose(f"[bold red]Configuration error:[/bold red] {e}")
        # Return the collected (potentially incomplete/invalid) config
        # or raise the error depending on desired strictness
        return base_config


def choose_stdio_connection(connections: List[ConnectionDetails]) -> Optional[ConnectionDetails]:
    """Chooses the best stdio connection from a list based on priority."""
    stdio_connections = [conn for conn in connections if conn.type == "stdio"]
    if not stdio_connections:
        return None

    priority_order = ["npx", "uvx", "docker"]  # Assuming similar priority in Python context

    # Prioritize published connections first
    for priority in priority_order:
        for conn in stdio_connections:
            stdio_func = conn.stdioFunction
            if (
                conn.published
                and isinstance(stdio_func, list)
                and stdio_func
                and isinstance(stdio_func[0], str)
                and stdio_func[0].startswith(priority)
            ):
                return conn

    # If no published connection found, check non-published
    for priority in priority_order:
        for conn in stdio_connections:
            stdio_func = conn.stdioFunction
            if (
                isinstance(stdio_func, list)
                and stdio_func
                and isinstance(stdio_func[0], str)
                and stdio_func[0].startswith(priority)
            ):
                return conn

    # Fallback to the first stdio connection if no priority match
    return stdio_connections[0]


def choose_connection(server: RegistryServer) -> ConnectionDetails:
    """Chooses the most suitable connection for a server."""
    connections = server.connections  # Directly access the dataclass attribute
    if not connections:
        raise ValueError(f"No connection configurations found for server {server.qualifiedName}")

    # Prefer stdio for local servers if available
    if not server.remote:  # Directly access the dataclass attribute
        stdio_connection = choose_stdio_connection(connections)
        if stdio_connection:
            return stdio_connection

    # Otherwise, look for WebSocket (ws) connection
    ws_connection = next((conn for conn in connections if conn.type == "ws"), None)
    if ws_connection:
        return ws_connection

    # Fallback: try stdio again (even for remote, if ws wasn't found)
    stdio_connection = choose_stdio_connection(connections)
    if stdio_connection:
        return stdio_connection

    # Final fallback: return the first connection whatever it is
    return connections[0]


def normalize_server_id(server_id: str) -> str:
    """Normalizes server ID by replacing the first slash after '@' with a dash."""
    if server_id.startswith("@"):
        parts = server_id.split("/", 1)
        if len(parts) == 2:
            return f"{parts[0]}-{parts[1]}"
    return server_id


def denormalize_server_id(normalized_id: str) -> str:
    """Converts a normalized server ID back to its original form (with slash)."""
    if normalized_id.startswith("@"):
        parts = normalized_id.split("-", 1)  # Split only on the first dash
        # Check if the first part looks like a scope (@scope)
        if len(parts) == 2 and parts[0].startswith("@") and "/" not in parts[0]:
            return f"{parts[0]}/{parts[1]}"
    return normalized_id


def get_server_name(server_id: str) -> str:
    """Extracts the server name part from a potentially scoped server ID."""
    if server_id.startswith("@") and "/" in server_id:
        return server_id.split("/", 1)[1]
    return server_id


def format_run_config_values(
    connection: ConnectionDetails,
    config_values: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Formats config values specifically for the 'run' command,
       allowing empty strings for missing required fields."""
    formatted_values: Dict[str, Any] = {}
    config_values = config_values or {}

    schema = connection.configSchema or {}
    env = schema.env if schema else {}
    if not env:
        return config_values

    required: Set[str] = set(schema.required if schema else [])

    for key, prop_details in env.items():
        value = config_values.get(key)
        prop_type = prop_details.type
        final_value: Any

        if value is not None:
            final_value = value
        elif key not in required:
            final_value = prop_details.default
        else:
            # Key is required but value is missing: use empty string
            final_value = ""

        # Handle cases where even the default might be None
        if final_value is None:
            # If required use empty string, otherwise None is acceptable for optional
            formatted_values[key] = "" if key in required else None
            continue

        try:
            formatted_values[key] = convert_value_to_type(final_value, prop_type)
        except ValueError:
            # If conversion fails, use empty string if required, None otherwise
            formatted_values[key] = "" if key in required else None

    return formatted_values

# Implementation for formatServerConfig with proxy command support


def build_dev_config(qualified_name: str,
                     user_config: Dict[str, Any],
                     api_key: Optional[str] = None,
                     config_needed: bool = True):
    """
    Formats server config for development environment.

    Creates a command that runs the Python module with the server name, config and API key,
    with platform-specific handling for Windows vs Unix-like systems.

    Args:
        qualified_name: The package identifier 
        user_config: User configuration values
        api_key: Optional API key
        config_needed: Whether config flag is needed
    """
    import sys
    import os

    # 检测是否为Windows系统
    is_windows = sys.platform == "win32"

    # 使用固定的CLI项目目录（开发环境）
    cli_dir = os.path.abspath(os.path.join(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))))))

    if is_windows:
        # Windows使用cmd作为命令解释器
        command = "cmd"

        # 构建完整的Windows命令行
        # 使用 /c 选项指示执行完命令后退出cmd，& 为Windows命令连接符
        cmd = f"cd /d {cli_dir} & PYTHONPATH=src python -m src run {qualified_name}"

        # 添加配置（如果需要）
        if config_needed and user_config:
            # Windows中JSON字符串使用双引号包裹，需要转义
            json_config = json.dumps(user_config).replace('"', '\\"')
            cmd += f' --config "{json_config}"'

        # 添加 API 密钥（如果有提供）
        if api_key:
            cmd += f" --api-key {api_key}"

        # 构建参数列表
        args = ["/c", cmd]
    else:
        # Unix/macOS使用sh作为命令解释器
        command = "sh"

        # 构建完整的shell命令
        cmd = f"cd {cli_dir} && PYTHONPATH=src python3 -m src run {qualified_name}"

        # 添加配置（如果需要）
        if config_needed and user_config:
            # 将配置对象转为JSON字符串，并用单引号包裹（适用于shell命令）
            json_config = json.dumps(user_config)
            cmd += f" --config '{json_config}'"

        # 添加 API 密钥（如果有提供）
        if api_key:
            cmd += f" --api-key {api_key}"

        # 构建参数列表
        args = ["-c", cmd]

    return command, args


def build_test_config(qualified_name: str,
                      user_config: Dict[str, Any],
                      api_key: Optional[str] = None,
                      config_needed: bool = True,
                      package_version: str = "1.0.21"):
    """
    Formats server config for test environment.
    Uses uvx to run a specific version of mcpdock from test.pypi.org.

    Args:
        qualified_name: The package identifier
        user_config: User configuration values
        api_key: Optional API key
        config_needed: Whether config flag is needed
        package_version: The version of py-mcpdock-cli to use

    Returns:
        Tuple containing command and args
    """
    # 使用uvx从测试PyPI获取指定版本
    command = "uvx"

    # 构建参数列表
    args = [
        "--from",
        f"mcpdock=={package_version}",
        "--index-url",
        "https://test.pypi.org/simple/",
        "--extra-index-url",
        "https://pypi.org/simple/",
        '--index-strategy',
        'unsafe-best-match',
        "mcpdock",
        "run",
        qualified_name
    ]

    # 添加配置（如果需要）
    if config_needed and user_config:
        args.append("--config")
        json_config = json.dumps(user_config)
        args.append(json_config)

    # 添加 API 密钥（如果有提供）
    if api_key:
        args.append("--api-key")
        args.append(api_key)

    return command, args


def build_prod_config(qualified_name: str,
                      user_config: Dict[str, Any],
                      api_key: Optional[str] = None,
                      config_needed: bool = True):
    """
    Formats server config into a command structure with proxy command support.
    Cross-platform compatible for both Windows and Unix-like systems.

    Args:
        qualified_name: The package identifier (被代理的命令标识)
        user_config: User configuration values
        api_key: Optional API key
        config_needed: Whether config flag is needed

    Returns:
        Tuple containing command and args
    """
    import sys

    # 检测是否为Windows系统
    is_windows = sys.platform == "win32"

    # 根据系统选择合适的包管理工具命令
    if is_windows:
        # Windows下更常用npx而非uvx
        command = "npx"
    else:
        # Unix-like系统使用uvx
        command = "uvx"

    proxy_package = "@mcpspace/proxy"  # 默认代理包

    # 构建参数列表
    args = ["-y"]

    # 添加代理包标识符
    args.append(proxy_package)

    # 添加 run 命令
    args.append("run")

    # 添加实际的包标识符（被代理的命令）
    args.append(qualified_name)

    # 添加配置（如果需要）
    if config_needed and user_config:
        args.append("--config")
        # 在Windows上，可能需要特别处理JSON字符串中的引号
        json_config = json.dumps(user_config)
        if is_windows:
            json_config = json_config.replace('"', '\\"')
        args.append(json_config)

    # 添加 API 密钥（如果有提供）
    if api_key:
        args.append("--api-key")
        args.append(api_key)
    return command, args


def format_server_config(
    qualified_name: str,
    user_config: Dict[str, Any],
    api_key: Optional[str] = None,
    config_needed: bool = True,
) -> ConfiguredServer:
    command, args = None, None
    if APP_ENV == 'dev':
        command, args = build_dev_config(qualified_name, user_config, api_key, config_needed)
    elif APP_ENV == 'test':
        command, args = build_test_config(qualified_name, user_config, api_key, config_needed)
    else:
        # prod环境或其他环境
        command, args = build_prod_config(qualified_name, user_config, api_key, config_needed)
    return ConfiguredServer(
        command=command,
        args=args,
        env=user_config
    )


def build_runtime_args_and_env(connection: ConnectionDetails, config: Dict[str, Any]) -> Tuple[list, dict]:
    """
    运行阶段：根据 configSchema.args 和 config 生成最终命令行参数列表和环境变量。
    - args: 字符串直接加入，对象从 config 取值并拼接 --name=value。
    - env: 只取 config 里在 configSchema.env 里定义的 key。
    """
    schema = connection.configSchema or {}
    args_schema = schema.args or []
    env_schema = schema.env if schema else {}
    final_args = []
    for arg in args_schema:
        if isinstance(arg, str):
            final_args.append(arg)
        elif isinstance(arg, dict):
            name = arg.get("name")
            if name and name in config:
                value = config[name]
                final_args.append(f"--{name}")
                final_args.append(str(value))
    # 只保留 env_schema 里定义的 key
    final_env = {k: v for k, v in config.items() if k in env_schema}
    return final_args, final_env

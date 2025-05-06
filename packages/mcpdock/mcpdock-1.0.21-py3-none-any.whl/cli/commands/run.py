import click
import json
import asyncio
from typing import Dict, Any, Optional

from rich import print as verbose
from rich.console import Console

from ..utils.logger import verbose
from ..registry import resolve_package
from ..utils.config import choose_connection, format_run_config_values
from ..utils.runtime import check_and_notify_remote_server
from ..types.registry import RegistryServer, ConnectionDetails
from ..runners import create_stdio_runner, create_ws_runner, run_package_with_command, create_stream_http_runner


# These runner functions have been moved to their respective modules in the runners package

async def pick_server_and_run(
    server_details: RegistryServer,
    config: Dict[str, Any],
    api_key: Optional[str] = None,
    analytics_enabled: bool = False
) -> None:
    """
    Selects the appropriate runner and starts the server.
    """
    connection = choose_connection(server_details)

    if connection.type == "ws":
        if not connection.deploymentUrl:
            raise ValueError("Missing deployment URL")
        await create_ws_runner(connection.deploymentUrl, config, api_key)
    elif connection.type == "stdio":
        await create_stdio_runner(server_details, config, api_key, analytics_enabled)
    elif connection.type == "stream-http":
        await create_stream_http_runner(server_details, config, api_key, analytics_enabled)
    else:
        raise ValueError(f"Unsupported connection type: {connection.type}")


async def run_server(
    qualified_name: str,
    config: Dict[str, Any],
    api_key: Optional[str] = None
) -> None:
    """
    Runs a server with the specified configuration.

    The qualified_name can be in these formats:
    - Standard MCP server name: "company/package"
    - uv command: "uv:package_name [args]" 
    - npx command: "npx:package_name [args]"
    """
    try:
        # # Check if this is a special command format (uv: or npx:)
        # if qualified_name.startswith("uv:") or qualified_name.startswith("npx:"):
        #     command_parts = qualified_name.split(":", 1)
        #     command_type = command_parts[0].lower()
        #     package_spec = command_parts[1]

        #     # Extract package name and args if provided
        #     package_parts = package_spec.split(" ", 1)
        #     package_name = package_parts[0]
        #     args = package_parts[1].split() if len(package_parts) > 1 else []

        #     verbose(f"Running {command_type} command for package: {package_name}")
        #     await run_package_with_command(
        #         command_type,
        #         package_name,
        #         args,
        #         config,
        #         api_key
        #     )
        #     return

        # Initialize settings for regular MCP server
        verbose("Initializing runtime environment settings")

        # Resolve server package
        verbose(f"Resolving server package: {qualified_name}")
        resolved_server = await resolve_package(qualified_name)

        if not resolved_server:
            raise ValueError(f"Could not resolve server: {qualified_name}")

        # Format the final configuration with validation
        connection = choose_connection(resolved_server)
        validated_env = format_run_config_values(connection, config)
        # 合并 env 校验结果和原 config，优先保留 env 校验后的值
        final_config = {**config, **validated_env}

        # Inform about remote server if applicable
        # check_and_notify_remote_server(resolved_server)

        verbose(f"[blue][Runner] Connecting to server:[/blue] {resolved_server.qualifiedName}")
        verbose(f"Connection types: {[c.type for c in resolved_server.connections]}")

        # Assume analytics is disabled for now
        analytics_enabled = False

        # Run the server with the appropriate runner
        await pick_server_and_run(
            resolved_server,
            final_config,
            api_key,
            analytics_enabled
        )
    except Exception as e:
        verbose(f"[red][Runner] Fatal error:[/red] {str(e)}")
        raise


@click.command("run")
@click.argument("mcp_server", type=click.STRING)
@click.option("--config", "config_json", type=click.STRING, help="Provide JSON format configuration")
@click.option("--api-key", type=click.STRING, help="API key for retrieving saved configuration")
def run(mcp_server: str, config_json: Optional[str], api_key: Optional[str]):
    """Run an AI MCP server."""
    verbose(f"Attempting to run {mcp_server}...")
    server_config = None

    # Parse command line provided configuration
    if config_json:
        try:
            verbose(config_json)
            server_config = json.loads(config_json)
            verbose(f"Using provided config: {server_config}")
        except json.JSONDecodeError as e:
            verbose(f"Error: Invalid JSON provided for --config: {e}")
            return 1
    # If no config provided, use empty dict
    if server_config is None:
        verbose("No config provided, running with empty config")
        server_config = {}

    if api_key:
        verbose(f"API key provided: {'*' * len(api_key)}")

    try:
        # with console.status(f"Starting {mcp_server}...", spinner="dots") as status:
        # Run the server asynchronously
        verbose('running server....')
        asyncio.run(run_server(mcp_server, server_config, api_key))
        # status.update(f"Successfully started {mcp_server}")
    except Exception as e:
        verbose(f"Run failed: {str(e)}")
        return 1

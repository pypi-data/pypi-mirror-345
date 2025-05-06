import click
import os
import sys
import json
import subprocess
from typing import Optional, Dict, Any, List

from ..utils.logger import verbose, info, error, warning
from ..config.client_config import read_config, write_config, get_config_target
from ..types.registry import ClientConfig
from ..utils.process_utils import check_server_by_package_name, remove_pid_by_server_name, is_process_running


def get_server_name(package_identifier: str) -> str:
    """
    Normalizes a package identifier to use as a key in the configuration.

    Args:
        package_identifier: The package identifier (e.g., '@org/package-name')

    Returns:
        A normalized server name to use as a key
    """
    # Handle scoped packages (@org/name format)
    if package_identifier.startswith('@') and '/' in package_identifier:
        # For scoped packages, use the part after the slash
        return package_identifier.split('/', 1)[1]
    return package_identifier


async def is_client_running(client: Optional[str] = None) -> bool:
    """
    Check if the specified client is currently running.

    Args:
        client: The client name to check

    Returns:
        Whether the client is running
    """
    if not client:
        return False

    # Map of client names to process names to check
    client_process_map = {
        "claude": "Claude",
        "vscode": "Code",
        "vscode-insiders": "Code - Insiders",
        "cline": "Cline",
        "cursor": "Cursor"
        # Add more mappings as needed
    }

    process_name = client_process_map.get(client.lower())
    if not process_name:
        verbose(f"Unknown client: {client}, can't check if it's running")
        return False

    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            if process_name.lower() in proc.info['name'].lower():
                verbose(f"Client {client} is running (process {proc.info['name']})")
                return True

        verbose(f"Client {client} is not running")
        return False
    except Exception as e:
        verbose(f"Error checking if client is running: {str(e)}")
        return False


async def restart_client(client: str) -> None:
    """
    Attempt to restart the specified client application.

    Args:
        client: The client name to restart
    """
    # Map client names to the commands that can restart them
    client_restart_map = {
        "claude": "open -a Claude",
        "vscode": "code",
        "vscode-insiders": "code-insiders",
        "cline": "cline",
        "cursor": "open -a Cursor"
        # Add more mappings as needed
    }

    restart_cmd = client_restart_map.get(client.lower())
    if not restart_cmd:
        verbose(f"No restart command available for {client}")
        return

    try:
        verbose(f"Attempting to restart {client} with command: {restart_cmd}")
        subprocess.run(restart_cmd, shell=True, check=True)
        info(f"Restarted {client}")
    except subprocess.SubprocessError as e:
        error(f"Failed to restart {client}: {str(e)}")


async def prompt_for_restart(client: Optional[str] = None) -> bool:
    """
    Ask the user if they want to restart the client after configuration changes.

    Args:
        client: The client name that might need restarting

    Returns:
        True if the client was restarted, False otherwise
    """
    if not client:
        return False

    # Check if the client is currently running
    is_running = await is_client_running(client)
    if not is_running:
        verbose(f"Client {client} is not running, no need to restart")
        return False

    # In CLI, we need to prompt the user for confirmation
    # from rich.prompt import Confirm
    # should_restart = Confirm.ask(f"Would you like to restart {client} to apply changes?")
    should_restart = True
    if should_restart:
        await restart_client(client)
        return True
    else:
        info(f"Please restart {client} manually to apply changes")
        return False


async def uninstall_server(package_identifier: str, client: Optional[str] = None) -> None:
    """
    Uninstalls a server for the specified client by removing it from the client's configuration.

    Args:
        package_identifier: The server package to uninstall
        client: The client to uninstall the server from
    """
    try:
        client_name = client or "claude"  # Default to Claude if no client specified
        verbose(f"Uninstalling {package_identifier} from {client_name}")

        # Get configuration target to determine how to handle the uninstallation
        target = get_config_target(client_name)
        if target["type"] == "command":
            info(f"Uninstallation is currently not supported for {client_name}")
            return

        # Read current configuration
        verbose(f"Reading configuration for client: {client_name}")
        client_config = read_config(client_name)

        # Get normalized server name to use as key
        server_name = get_server_name(package_identifier)
        verbose(f"Normalized server ID: {server_name}")

        # Check if server exists in config
        if not hasattr(client_config, 'mcpServers') or not isinstance(client_config.mcpServers, dict):
            verbose(f"Client {client_name} has no MCP servers configured")
            info(f"Server {package_identifier} is not installed for {client_name}")
            return

        if server_name not in client_config.mcpServers:
            verbose(f"Server {server_name} not found in configuration for {client_name}")
            info(f"Server {package_identifier} is not installed for {client_name}")
            return

        # Remove the server from configuration
        verbose(f"Removing server {server_name} from configuration")
        del client_config.mcpServers[server_name]

        # Write updated configuration
        verbose("Writing updated configuration...")
        write_config(client_config, client_name)

        # Check if the server process is running and clean up PID records
        is_running, pid = check_server_by_package_name(package_identifier)
        if is_running and pid:
            verbose(f"Found running server process with PID {pid}")
            # Remove from PID file but don't kill the process automatically
            remove_pid_by_server_name(server_name, client_name)
            info(f"Note: The server process (PID: {pid}) is still running. You may want to restart your client.")

        info(f"Successfully uninstalled {package_identifier} from {client_name}")

        # Prompt user to restart client to apply changes
        await prompt_for_restart(client_name)

    except Exception as e:
        error(f"Failed to uninstall {package_identifier}: {str(e)}")
        # Structured error output for upstream processes
        error_obj = {
            "error_type": type(e).__name__,
            "message": str(e),
            "traceback": __import__('traceback').format_exc()
        }
        print(json.dumps(error_obj, ensure_ascii=False), file=sys.stderr)
        return 1


@click.command("uninstall")
@click.argument("mcp_server", type=click.STRING)
@click.option("--client", type=click.STRING, help="Specify the target AI client")
def uninstall(mcp_server: str, client: Optional[str]):
    """Uninstall an AI mcp-server from the specified client."""
    verbose(f"Attempting to uninstall {mcp_server}...")

    try:
        # Run the async uninstallation process
        import asyncio
        asyncio.run(uninstall_server(mcp_server, client))
    except Exception as e:
        # Output structured JSON error information for upstream processes
        import sys
        import traceback
        error_obj = {
            "error_type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        print(json.dumps(error_obj, ensure_ascii=False), file=sys.stderr)
        return 1

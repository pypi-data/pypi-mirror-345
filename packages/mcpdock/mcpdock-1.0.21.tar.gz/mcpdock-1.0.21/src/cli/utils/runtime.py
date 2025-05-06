import subprocess
import sys
import shutil
import os
from typing import Dict, Optional, List
import questionary
from rich import print as rprint

from ..types.registry import ConnectionDetails, RegistryServer # Assuming RegistryServer includes connections
from .logger import verbose


def check_command_installed(command: str) -> bool:
    """Checks if a command is available in the system's PATH."""
    if not shutil.which(command):
        verbose(f"Command '{command}' not found in PATH.")
        return False
    # Optionally, run a version command to be more certain
    try:
        # Use shell=True if command might be an alias or shell function, but be cautious
        # Using the direct path from shutil.which is safer if possible
        cmd_path = shutil.which(command)
        if not cmd_path:
             return False # Should not happen if which found it, but safety check
        result = subprocess.run([cmd_path, "--version"], capture_output=True, text=True, timeout=5, check=False)
        verbose(f"'{command} --version' exited with code {result.returncode}")
        # Check return code - 0 usually means success
        return result.returncode == 0
    except (subprocess.TimeoutExpired, OSError, FileNotFoundError) as e:
        verbose(f"Error checking version for '{command}': {e}")
        # If version check fails, assume it might still work or is problematic
        return False # Treat version check failure as potentially not installed correctly
    except Exception as e:
        verbose(f"Unexpected error checking '{command}': {e}")
        return False

async def prompt_for_install(command: str, install_url: str, command_name: str) -> bool:
    """Asks the user if they want to install a missing command."""
    should_install = await questionary.confirm(
        f"{command_name} is required for this operation. Would you like to attempt installation?",
        default=True
    ).ask_async()

    if not should_install:
        rprint(f"[yellow]{command_name} installation declined. You can install it manually from {install_url}[/yellow]")
        return False

    return await install_command(command, install_url, command_name)

async def install_command(command: str, install_url: str, command_name: str) -> bool:
    """Attempts to install a command using provided curl/powershell scripts."""
    rprint(f"Attempting to install {command_name}...")
    try:
        if sys.platform == "win32":
            ps_command = f"powershell -ExecutionPolicy ByPass -NoProfile -Command \"irm '{install_url}/install.ps1' | iex\""
            verbose(f"Running install command (Windows): {ps_command}")
            # Using shell=True for powershell pipeline
            result = subprocess.run(ps_command, shell=True, capture_output=True, text=True, check=True)
        else:
            sh_command = f"curl -LsSf '{install_url}/install.sh' | sh"
            verbose(f"Running install command (Unix): {sh_command}")
            # Using shell=True for curl pipeline
            result = subprocess.run(sh_command, shell=True, capture_output=True, text=True, check=True)

        verbose(f"Installation stdout:\n{result.stdout}")
        if result.stderr:
             verbose(f"Installation stderr:\n{result.stderr}")
        rprint(f"[green]✓ {command_name} installed successfully.[/green]")
        return True
    except subprocess.CalledProcessError as e:
        rprint(f"[red]Failed to install {command_name}.[/red]")
        rprint(f"Stderr:\n{e.stderr}")
        rprint(f"You can try installing it manually from {install_url}")
        return False
    except Exception as e:
        rprint(f"[red]An unexpected error occurred during installation: {e}[/red]")
        rprint(f"You can try installing it manually from {install_url}")
        return False

def is_command_required(connection: ConnectionDetails, command: str) -> bool:
    """Checks if a command is listed in the stdioFunction for a stdio connection."""
    return (
        connection.type == "stdio" and
        isinstance(connection.stdioFunction, list) and
        command in connection.stdioFunction
    )

async def ensure_command_installed(
    connection: ConnectionDetails,
    command: str,
    command_name: str,
    install_url: str,
) -> bool:
    """Checks if a required command is installed, prompts to install if not."""
    if is_command_required(connection, command):
        verbose(f"{command_name} installation check required for connection type {connection.type}.")
        if not check_command_installed(command):
            rprint(f"[yellow]Required command '{command_name}' ('{command}') not found or not working.[/yellow]")
            installed = await prompt_for_install(command, install_url, command_name)
            if not installed:
                rprint(f"[yellow]Warning: {command_name} is not installed. The server might fail to launch.[/yellow]")
                return False
            # Re-check after installation attempt
            if not check_command_installed(command):
                 rprint(f"[red]Error: {command_name} installation seemed to succeed, but '{command}' is still not working correctly.[/red]")
                 return False
            return True # Installed successfully
        else:
            verbose(f"Command '{command_name}' ('{command}') is installed.")
            return True # Already installed
    else:
        verbose(f"Command '{command_name}' not required for this connection.")
        return True # Not required for this connection

async def ensure_uv_installed(connection: ConnectionDetails) -> bool:
    """Ensures UV (uvx command) is installed if required by the connection."""
    # Assuming uvx is the command to check for uv
    return await ensure_command_installed(connection, "uvx", "UV", "https://astral.sh/uv")

async def ensure_bun_installed(connection: ConnectionDetails) -> bool:
    """Ensures Bun (bunx command) is installed if required by the connection."""
    # Assuming bunx is the command to check for bun
    return await ensure_command_installed(connection, "bunx", "Bun", "https://bun.sh")

def get_runtime_environment(base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Gets runtime environment variables.

    Placeholder: This function needs to replicate the behavior of
    `@modelcontextprotocol/sdk/client/stdio.js#getDefaultEnvironment`
    if specific environment variables are required by the MCP servers.
    Currently, it merges provided base_env with the current process environment.
    """
    default_env = os.environ.copy()
    verbose("Using current process environment as default runtime environment.")
    # --- Placeholder Start ---
    # TODO: Determine if specific MCP environment variables are needed
    # and set them here if possible.
    # Example: default_env["MCP_PYTHON_CLIENT"] = "1"
    # --- Placeholder End ---

    if base_env:
        return {**default_env, **base_env}
    else:
        return default_env

def check_and_notify_remote_server(server: RegistryServer) -> bool:
    """Checks if the server is remote and prints a security notice if it is."""
    # Determine if remote based on connections or explicit flag
    is_remote = (
        any(conn.type == "ws" and conn.deploymentUrl for conn in server.connections)
        and server.remote is not False # Explicitly false overrides ws check
    )

    if is_remote:
        verbose("Remote server detected, showing security notice")
        rprint(
            "[blue]Installing remote server. Please ensure you trust the server author, "
            "especially when sharing sensitive data.[/blue]"
        )
        # Add link if available
        # rprint(f"[blue]For information on data policy, please visit: [underline]https://example.com/data-policy[/underline][/blue]")

    return is_remote
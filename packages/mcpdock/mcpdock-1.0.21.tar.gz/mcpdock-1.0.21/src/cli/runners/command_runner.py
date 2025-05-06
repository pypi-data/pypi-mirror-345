"""
Command Runners implementation for running Python or Node.js packages
"""
import json
import asyncio
import signal
import sys
import os
from typing import Dict, Any, Optional, List

from rich import print as rprint

from ..utils.logger import verbose


async def run_command_process(cmd: List[str], env: Optional[Dict[str, str]] = None) -> None:
    """
    Run a command as a subprocess and handle its output asynchronously

    Args:
        cmd: Command and arguments as a list
        env: Optional environment variables
    """
    verbose(f"Running command: {' '.join(cmd)}")

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env
    )

    # Setup signal handling for graceful shutdown
    def handle_sigint(sig, frame):
        rprint("[yellow]Received stop signal, terminating command...[/yellow]")
        process.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_sigint)

    # Process output in real-time
    async def read_stream(stream, prefix):
        while True:
            line = await stream.readline()
            if not line:
                break
            try:
                decoded_line = line.decode('utf-8').rstrip()
                if prefix == "stdout":
                    rprint(f"[blue]{decoded_line}[/blue]")
                else:
                    rprint(f"[yellow]{decoded_line}[/yellow]")
            except UnicodeDecodeError:
                rprint(f"[red]Error decoding output from {prefix}[/red]")

    # Create tasks for stdout and stderr
    stdout_task = asyncio.create_task(read_stream(process.stdout, "stdout"))
    stderr_task = asyncio.create_task(read_stream(process.stderr, "stderr"))

    # Wait for process to complete
    exit_code = await process.wait()

    # Wait for output to be fully processed
    await stdout_task
    await stderr_task

    if exit_code != 0:
        rprint(f"[red]Command exited with code {exit_code}[/red]")
    else:
        rprint(f"[green]Command completed successfully[/green]")


async def create_uv_runner(
    package_name: str,
    args: List[str],
    config: Dict[str, Any],
    api_key: Optional[str] = None
) -> None:
    """
    Creates a runner for executing Python packages with uv package manager

    Args:
        package_name: Name of the Python package to run
        args: Additional arguments to pass to the package
        config: Configuration options
        api_key: Optional API key for authentication
    """
    verbose(f"Starting uv runner for package: {package_name}")
    rprint(f"[blue]Running Python package with uv: {package_name}[/blue]")

    # Prepare environment variables from config
    env = os.environ.copy()
    for key, value in config.items():
        if isinstance(value, str):
            env[f"MCP_{key.upper()}"] = value
        else:
            env[f"MCP_{key.upper()}"] = json.dumps(value)

    if api_key:
        env["MCP_API_KEY"] = api_key

    # Build the uv command
    cmd = ["uv", "run", "-m", package_name]
    if args:
        cmd.extend(args)

    await run_command_process(cmd, env)


async def create_npx_runner(
    package_name: str,
    args: List[str],
    config: Dict[str, Any],
    api_key: Optional[str] = None
) -> None:
    """
    Creates a runner for executing Node.js packages with npx

    Args:
        package_name: Name of the Node.js package to run
        args: Additional arguments to pass to the package
        config: Configuration options
        api_key: Optional API key for authentication
    """
    verbose(f"Starting npx runner for package: {package_name}")
    rprint(f"[blue]Running Node.js package with npx: {package_name}[/blue]")

    # Prepare environment variables from config
    env = os.environ.copy()
    for key, value in config.items():
        if isinstance(value, str):
            env[f"MCP_{key.upper()}"] = value
        else:
            env[f"MCP_{key.upper()}"] = json.dumps(value)

    if api_key:
        env["MCP_API_KEY"] = api_key

    # Build the npx command
    cmd = ["npx", package_name]
    if args:
        cmd.extend(args)

    await run_command_process(cmd, env)


async def run_package_with_command(
    command_type: str,
    package_name: str,
    args: List[str],
    config: Dict[str, Any],
    api_key: Optional[str] = None
) -> None:
    """
    Run a package with the specified command runner (uv or npx)

    Args:
        command_type: Type of command runner to use ("uv" or "npx")
        package_name: Name of the package to run
        args: Additional arguments to pass to the package
        config: Configuration options
        api_key: Optional API key for authentication

    Raises:
        ValueError: If an unsupported command type is provided
    """
    if command_type.lower() == "uv":
        await create_uv_runner(package_name, args, config, api_key)
    elif command_type.lower() == "npx":
        await create_npx_runner(package_name, args, config, api_key)
    else:
        raise ValueError(f"Unsupported command type: {command_type}")

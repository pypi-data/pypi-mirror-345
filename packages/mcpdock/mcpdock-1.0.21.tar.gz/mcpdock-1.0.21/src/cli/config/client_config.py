import os
import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Literal, TypedDict

# Import types from the registry module
from ..types.registry import ClientConfig, ConfiguredServer
# Import logger
from ..utils.logger import verbose

# Define types for configuration targets


class ClientFileTarget(TypedDict):
    type: Literal["file"]
    path: Path


class ClientCommandTarget(TypedDict):
    type: Literal["command"]
    command: str
    # Potentially add args template if needed later


ClientInstallTarget = Union[ClientFileTarget, ClientCommandTarget]

# Determine platform-specific paths using pathlib
home_dir = Path.home()

if sys.platform == "win32":
    base_dir = Path(os.environ.get("APPDATA", home_dir / "AppData" / "Roaming"))
    vscode_storage_path = Path("Code") / "User" / "globalStorage"
    code_command = "code.cmd"
    code_insiders_command = "code-insiders.cmd"
elif sys.platform == "darwin":
    base_dir = home_dir / "Library" / "Application Support"
    vscode_storage_path = Path("Code") / "User" / "globalStorage"
    code_command = "code"
    code_insiders_command = "code-insiders"
else:  # Assume Linux/other Unix-like
    base_dir = Path(os.environ.get("XDG_CONFIG_HOME", home_dir / ".config"))
    vscode_storage_path = Path("Code/User/globalStorage")  # Note: Path combines these
    code_command = "code"
    code_insiders_command = "code-insiders"

default_claude_path = base_dir / "Claude" / "claude_desktop_config.json"

# Define client paths using platform-specific base directories
# Using lowercase keys for normalization
CLIENT_PATHS: Dict[str, ClientInstallTarget] = {
    "claude": {"type": "file", "path": default_claude_path},
    "trae": {"type": "file", "path": base_dir / "Trae" / "User" / "mcp.json"},
    "cline": {
        "type": "file",
        "path": base_dir / vscode_storage_path / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json",
    },
    "roo-cline": {
        "type": "file",
        "path": base_dir / vscode_storage_path / "rooveterinaryinc.roo-cline" / "settings" / "cline_mcp_settings.json",
    },
    "windsurf": {"type": "file", "path": home_dir / ".codeium" / "windsurf" / "mcp_config.json"},
    "witsy": {"type": "file", "path": base_dir / "Witsy" / "settings.json"},
    "enconvo": {"type": "file", "path": home_dir / ".config" / "enconvo" / "mcp_config.json"},
    "cursor": {"type": "file", "path": home_dir / ".cursor" / "mcp.json"},
    "vscode": {"type": "command", "command": code_command},
    "vscode-insiders": {"type": "command", "command": code_insiders_command},
}


def get_config_target(client: Optional[str] = None) -> ClientInstallTarget:
    """Gets the configuration target (file path or command) for a given client."""
    normalized_client = (client or "claude").lower()
    verbose(f"Getting config target for client: {normalized_client}")

    target = CLIENT_PATHS.get(normalized_client)

    if target:
        verbose(f"Config target resolved to: {target}")
        return target
    else:
        # Fallback for unknown clients (similar to JS version)
        fallback_path = default_claude_path.parent.parent / (client or "claude") / f"{normalized_client}_config.json"
        fallback_target: ClientFileTarget = {"type": "file", "path": fallback_path}
        verbose(f"Client '{normalized_client}' not predefined, using fallback path: {fallback_target}")
        return fallback_target


def read_config(client: Optional[str] = None) -> ClientConfig:
    """Reads the configuration for the specified client."""
    client_name = (client or "claude").lower()
    verbose(f"Reading config for client: {client_name}")
    target = get_config_target(client_name)

    if target["type"] == "command":
        verbose(f"Client '{client_name}' uses command-based config. Reading not supported.")
        # Command-based installers don't support reading config back easily
        return ClientConfig(mcpServers={})

    config_path = target["path"]
    verbose(f"Checking if config file exists at: {config_path}")
    if not config_path.exists():
        verbose("Config file not found, returning default empty config.")
        return ClientConfig(mcpServers={})

    try:
        verbose("Reading config file content.")
        raw_content = config_path.read_text(encoding="utf-8")
        raw_config = json.loads(raw_content)
        verbose(f"Config loaded successfully: {json.dumps(raw_config, indent=2)}")

        # Ensure mcpServers key exists, return as ClientConfig object
        mcp_servers_data = raw_config.get("mcpServers", {})
        # Basic validation/conversion if needed, assuming structure matches ConfiguredServer for now
        configured_servers = {
            name: ConfiguredServer(**server_data)
            for name, server_data in mcp_servers_data.items()
            if isinstance(server_data, dict) and "command" in server_data and "args" in server_data
        }

        # Include other top-level keys from the config file
        other_config = {k: v for k, v in raw_config.items() if k != "mcpServers"}

        return ClientConfig(mcpServers=configured_servers, **other_config)

    except json.JSONDecodeError as e:
        verbose(f"Error decoding JSON from {config_path}: {e}")
        return ClientConfig(mcpServers={})
    except Exception as e:
        verbose(f"Error reading config file {config_path}: {e}")
        return ClientConfig(mcpServers={})


def _write_config_command(config: ClientConfig, target: ClientCommandTarget) -> None:
    """Writes configuration using a command (e.g., for VS Code)."""
    command = target["command"]
    args: List[str] = []

    # Convert ConfiguredServer back to dict for JSON stringify
    for name, server in config.mcpServers.items():
        server_dict = {"command": server.command, "args": server.args, "name": name}
        args.extend(["--add-mcp", json.dumps(server_dict)])

    full_command = [command] + args
    verbose(f"Running command: {' '.join(full_command)}")

    try:
        # Use shell=True cautiously if command might not be directly executable
        # Or better, ensure the command is in PATH
        result = subprocess.run(full_command, capture_output=True, text=True, check=True, encoding='utf-8')
        verbose(f"Executed command successfully. Output:\n{result.stdout}")
        if result.stderr:
            verbose(f"Command stderr:\n{result.stderr}")
    except FileNotFoundError:
        verbose(f"Error: Command '{command}' not found. Make sure it is installed and in your PATH.")
        raise FileNotFoundError(f"Command '{command}' not found.")
    except subprocess.CalledProcessError as e:
        verbose(f"Error executing command. Return code: {e.returncode}")
        verbose(f"Stdout:\n{e.stdout}")
        verbose(f"Stderr:\n{e.stderr}")
        raise RuntimeError(f"Command '{command}' failed: {e.stderr or e.stdout}")
    except Exception as e:
        verbose(f"An unexpected error occurred while running the command: {e}")
        raise


def _write_config_file(config: ClientConfig, target: ClientFileTarget) -> None:
    """Writes configuration to a file, merging with existing content."""
    config_path = target["path"]
    config_dir = config_path.parent

    verbose(f"Ensuring config directory exists: {config_dir}")
    config_dir.mkdir(parents=True, exist_ok=True)

    existing_config_data: Dict[str, Any] = {}
    if config_path.exists():
        try:
            verbose("Reading existing config file for merging.")
            existing_config_data = json.loads(config_path.read_text(encoding="utf-8"))
            verbose(f"Existing config loaded: {json.dumps(existing_config_data, indent=2)}")
        except json.JSONDecodeError as e:
            verbose(f"Error reading existing config file {config_path} for merge: {e}. Will overwrite.")
        except Exception as e:
            verbose(f"Error reading existing config file {config_path}: {e}. Will overwrite.")

    # Prepare the config to be written (convert dataclasses back to dicts)
    config_to_write = {
        **config.__dict__,  # Include other top-level keys if ClientConfig has them
        "mcpServers": {
            name: {"command": server.command, "args": server.args, "env": server.env}
            for name, server in config.mcpServers.items()
        }
    }

    # Merge configurations
    verbose("Merging configurations.")

    # Determine if this is an uninstall operation by checking for keys in existing_config that are missing in config_to_write
    existing_servers = existing_config_data.get("mcpServers", {})
    new_servers = config_to_write.get("mcpServers", {})
    is_uninstall = False

    if existing_servers and new_servers:
        # Check if some server keys in existing config are missing in new config
        deleted_servers = set(existing_servers.keys()) - set(new_servers.keys())
        is_uninstall = len(deleted_servers) > 0
        if is_uninstall:
            verbose(f"Detected uninstall operation. Servers to remove: {deleted_servers}")

    # If this is an uninstall, we should not merge old server configs back in
    if is_uninstall:
        merged_config = {
            **existing_config_data,
            **config_to_write,
            # For uninstall: Don't merge old server configs, only use the new (updated) config
            "mcpServers": new_servers,
        }
    else:
        # For normal install: Merge configurations, new configs have precedence
        merged_config = {
            **existing_config_data,
            **config_to_write,
            # Ensure mcpServers are merged correctly
            "mcpServers": {
                **(existing_config_data.get("mcpServers") or {}),
                **(config_to_write.get("mcpServers") or {}),
            }
        }
    verbose(f"Merged config: {json.dumps(merged_config, indent=2)}")

    try:
        verbose(f"Writing config to file: {config_path}")
        config_path.write_text(json.dumps(merged_config, indent=2), encoding="utf-8")
        verbose(f"Configuration successfully written to {config_path}")
    except Exception as e:
        verbose(f"Error writing config file {config_path}: {e}")
        raise IOError(f"Failed to write configuration to {config_path}") from e


def write_config(config: ClientConfig, client: Optional[str] = None) -> None:
    """Writes the configuration for the specified client, either to a file or via command."""
    client_name = (client or "claude").lower()
    verbose(f"Writing config for client: {client_name}")
    verbose(f"Config data: {config}")  # Dataclass repr is usually good

    if not isinstance(config, ClientConfig) or not isinstance(config.mcpServers, dict):
        verbose("Invalid config object provided.")
        raise TypeError("Invalid ClientConfig object provided to write_config")

    target = get_config_target(client_name)

    if target["type"] == "command":
        _write_config_command(config, target)
    else:
        # Prepare the configuration to be written
        cleaned_config = {
            **config.__dict__,
            "mcpServers": {
                name: server.__dict__ for name, server in config.mcpServers.items()
            }
        }
        # Deserialize back into ConfiguredServer objects after writing
        deserialized_config = ClientConfig(
            **{
                **cleaned_config,
                "mcpServers": {
                    name: ConfiguredServer(**server) for name, server in cleaned_config["mcpServers"].items()
                }
            }
        )
        _write_config_file(deserialized_config, target)

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

# Using dataclasses for structured type definitions


@dataclass
class ConfigSchemaProperty:
    # Represents a single property within the configSchema
    # Using Any for now, can be refined if specific property types are known
    type: Optional[str] = None
    description: Optional[str] = None
    default: Any = None
    required: Optional[bool] = None  # 新增，兼容 mock_servers.json
    # Add other potential schema attributes if needed


@dataclass
class ConfigSchema:
    env: Dict[str, ConfigSchemaProperty] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    args: Optional[List[str]] = None


@dataclass
class ConnectionDetails:
    type: str
    stdioFunction: Optional[List[str]] = None
    deploymentUrl: Optional[str] = None
    published: Optional[bool] = None
    configSchema: Optional[ConfigSchema] = None  # Use the nested dataclass


@dataclass
class ConfiguredServer:
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None


@dataclass
class MCPConfig:
    # Represents the overall configuration structure potentially saved
    mcpServers: Dict[str, ConfiguredServer] = field(default_factory=dict)


@dataclass
class ServerConfig:
    # Represents the configuration *for* a specific server instance
    # Using a general dict for extra keys corresponding to `[key: string]: unknown`
    qualifiedName: str
    connections: List[ConnectionDetails]
    remote: Optional[bool] = None
    additional_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClientConfig:
    # Represents the client-side configuration (e.g., installed servers)
    # Using Dict[str, Any] for flexibility as the TS type was Record<string, unknown>
    mcpServers: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegistryServer:
    # Represents a server as listed in a registry
    qualifiedName: str
    connections: List[ConnectionDetails]
    displayName: Optional[str] = None
    remote: Optional[bool] = None

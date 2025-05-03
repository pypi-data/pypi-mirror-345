# MCP Proxy Adapter

## Overview

MCP Proxy Adapter is a specialized adapter for integrating Command Registry with MCP Proxy (Model Control Protocol Proxy). It allows using commands from Command Registry as tools for artificial intelligence models, providing a unified JSON-RPC interface for interacting with commands.

## Key Features

- **JSON-RPC interface** for executing commands from the registry
- **Automatic configuration generation** for MCPProxy
- **OpenAPI schema optimization** for working with AI models
- **Enhanced error handling** with detailed logging
- **Parameter type validation** to prevent runtime errors
- **Integration with any FastAPI applications**

## Installation

```bash
pip install mcp-proxy-adapter
```

## Quick Start

### Basic Integration

```python
from fastapi import FastAPI
from command_registry import CommandRegistry
from mcp_proxy_adapter.adapter import MCPProxyAdapter

# Create FastAPI application
app = FastAPI()

# Create command registry
registry = CommandRegistry()

# Register commands
registry.register_command("search_by_text", search_function, 
                          description="Search by text query")

# Create MCP Proxy adapter
adapter = MCPProxyAdapter(registry)

# Register endpoints in FastAPI application
adapter.register_endpoints(app)

# Save MCP Proxy configuration to file
adapter.save_config_to_file("mcp_proxy_config.json")
```

### Working with External Loggers

```python
import logging
from mcp_proxy_adapter.adapter import configure_logger

# Create application logger
app_logger = logging.getLogger("my_application")
app_logger.setLevel(logging.DEBUG)

# Configure handler for logger
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
app_logger.addHandler(handler)

# Integrate application logger with adapter
adapter_logger = configure_logger(app_logger)

# Now all messages from adapter will go through application logger
```

## Architecture

### Core Components

MCP Proxy Adapter consists of the following components:

1. **MCPProxyAdapter** — main class providing integration with Command Registry and FastAPI
2. **JsonRpcRequest/JsonRpcResponse** — models for working with JSON-RPC requests and responses
3. **SchemaOptimizer** — OpenAPI schema optimizer for working with MCP Proxy
4. **MCPProxyConfig/MCPProxyTool** — models for forming MCP Proxy configuration

### Technical Implementation Details

Based on code analysis, the following was discovered:

1. **Implementation duplication** — MCPProxyAdapter is present in two files:
   - `src/adapter.py` (394 lines) — main adapter implementation
   - `src/adapters/mcp_proxy_adapter.py` — specialized version

2. **OpenAPI Schemas** — a significant part of the codebase consists of OpenAPI schemas:
   - `src/openapi_schema/rest_schema.py` (506 lines)
   - `src/openapi_schema/rpc_schema.py` (414 lines)

3. **Method Call Chains**:
   - `__init__` calls `_generate_router` for FastAPI router setup
   - `save_config_to_file` uses `generate_mcp_proxy_config`
   - `get_openapi_schema` uses `_generate_basic_schema`
   - `execute_command` uses `_validate_param_types` for type checking

### Interaction Diagram

```
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│    MCP Proxy    │      │  MCPProxyAdapter   │      │ CommandRegistry │
│                 │◄─────┤                    │◄─────┤                 │
└─────────────────┘      └────────────────────┘      └─────────────────┘
        ▲                         ▲                          ▲
        │                         │                          │
        │                ┌────────┴───────┐                  │
        │                │                │                  │
        └────────────────┤  FastAPI App   │──────────────────┘
                         │                │
                         └────────────────┘
```

## Adapter API

### Initialization

```python
def __init__(
    self, 
    registry: CommandRegistry,
    cmd_endpoint: str = "/cmd",
    include_schema: bool = True,
    optimize_schema: bool = True
)
```

* **registry** — CommandRegistry instance for integration
* **cmd_endpoint** — path for command execution endpoint
* **include_schema** — whether to include OpenAPI schema generation
* **optimize_schema** — whether to optimize schema for MCP Proxy

### Main Methods

* **register_endpoints(app: FastAPI)** — registers endpoints in FastAPI application
* **generate_mcp_proxy_config()** — generates configuration for MCP Proxy
* **save_config_to_file(filename: str)** — saves configuration to file
* **_generate_router()** — internal method for generating FastAPI router
* **_validate_param_types(command, params)** — checks parameter types before command execution
* **_generate_basic_schema()** — creates basic OpenAPI schema when generator is absent
* **_optimize_schema(schema)** — optimizes OpenAPI schema for MCP Proxy

## Implementation Features

Code analysis revealed the following important implementation aspects:

1. **Parameter Validation** occurs in several stages:
   - First, command presence in registry is checked
   - Then, presence of all required parameters is verified
   - After that, types of all passed parameters are checked

2. **Error Handling** is implemented using an extensive try/except mechanism that:
   - Catches specific exceptions (TypeError, KeyError)
   - Handles general exceptions through Exception block
   - Formats all errors in JSON-RPC format with appropriate codes

3. **Schema Optimization** includes several steps:
   - Removing redundant information from OpenAPI schema
   - Adding JSON-RPC components
   - Preparing schema for use with MCP Proxy

## JSON-RPC Protocol

### Request Format

```json
{
  "jsonrpc": "2.0",
  "method": "command_name",
  "params": {
    "param1": "value1",
    "param2": "value2"
  },
  "id": "request_id"
}
```

### Successful Response Format

```json
{
  "jsonrpc": "2.0",
  "result": {
    // Command execution result
  },
  "id": "request_id"
}
```

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32603,
    "message": "Error description"
  },
  "id": "request_id"
}
```

## Error Handling

The adapter handles and logs the following error types:

1. **Non-existent Command** (-32601) — calling a command not registered in the registry
2. **Missing Required Parameters** (-32602) — required command parameters not specified
3. **Parameter Type Errors** (-32602) — parameter type doesn't match expected type
4. **Command Execution Errors** (-32603) — exceptions occurring during execution
5. **Internal Server Errors** (-32603) — unexpected errors in adapter operation

## Usage Examples

### Integration with Existing FastAPI Application

```python
from fastapi import FastAPI
from command_registry import CommandRegistry
from mcp_proxy_adapter.adapter import MCPProxyAdapter, configure_logger

# Create main application
app = FastAPI(title="My Application API")

# Create command registry
registry = CommandRegistry()

# Register commands from different modules
registry.scan_module("myapp.commands.search")
registry.scan_module("myapp.commands.analytics")

# Configure project logger and integrate it with adapter
logger = logging.getLogger("myapp")
adapter_logger = configure_logger(logger)

# Create MCP Proxy adapter
adapter = MCPProxyAdapter(registry)

# Register endpoints in application
adapter.register_endpoints(app)

# Save configuration for MCP Proxy
adapter.save_config_to_file("config/mcp_proxy_config.json")
```

### Parameter Type Validation
``` 
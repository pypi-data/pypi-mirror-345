# Command Registry

## Overview

Command Registry is a high-level system for centralized command management in applications. It provides a unified mechanism for defining, registering, executing, and documenting commands through various interfaces.

## Key Features

- **Single access point** for application commands
- **Automatic metadata extraction** from Python docstrings and type hints
- **Integration with various protocols** (REST, JSON-RPC, WebSockets)
- **API documentation generation** based on command metadata
- **Input parameters and output values validation**
- **Metadata compliance verification** with actual function signatures
- **Extensibility** through interfaces for dispatchers, adapters, and schema generators
- **AI model integration** via MCP Proxy Adapter

## Getting Started

### Installation

```bash
pip install command-registry
```

For MCP Proxy integration, also install:

```bash
pip install mcp-proxy-adapter
```

### Simple Example

```python
from command_registry import CommandRegistry

# Create a command registry instance
registry = CommandRegistry()

# Define a command
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        Sum of numbers a and b
    """
    return a + b

# Register the command
registry.register_command("add", add_numbers)

# Execute the command
result = registry.execute("add", {"a": 5, "b": 3})  # Returns 8
```

### FastAPI Export

```python
from fastapi import FastAPI
from command_registry.adapters import RESTAdapter

app = FastAPI()
adapter = RESTAdapter(registry)
adapter.register_endpoints(app)
```

### MCP Proxy Integration for AI Models

```python
from fastapi import FastAPI
from mcp_proxy_adapter.adapter import MCPProxyAdapter

app = FastAPI()
adapter = MCPProxyAdapter(registry)
adapter.register_endpoints(app)

# Create configuration for MCP Proxy
adapter.save_config_to_file("mcp_proxy_config.json")
```

### Automatic Command Registration from Module

```python
# Scan module and register all found commands
registry.scan_module("myapp.commands")
```

## Documentation

- [Architecture](architecture.md) - detailed component description
- [Command Development Guide](command_development.md) - best practices
- [Examples](examples.md) - usage examples for various scenarios
- [Validation](validation.md) - command validation mechanisms
- [MCP Proxy Adapter](mcp_proxy_adapter.md) - AI model integration via MCP Proxy

## Project Structure

```
command_registry/
  ├── __init__.py            # Main public API
  ├── core.py                # Core CommandRegistry logic
  ├── dispatchers/           # Command dispatchers
  │   ├── __init__.py
  │   ├── base_dispatcher.py  # Abstract base class
  │   └── command_dispatcher.py  # Main implementation
  ├── metadata/              # Metadata extraction
  │   ├── __init__.py
  │   ├── docstring_parser.py  # Docstring parser
  │   └── type_analyzer.py   # Type analyzer
  ├── validators/            # Validators
  │   ├── __init__.py
  │   └── parameter_validator.py  # Parameter validation
  ├── adapters/              # Protocol adapters
  │   ├── __init__.py
  │   ├── rest_adapter.py    # REST API
  │   └── json_rpc_adapter.py  # JSON-RPC
  └── schema/                # Schema generators
      ├── __init__.py
      ├── openapi_generator.py  # OpenAPI
      └── json_schema_generator.py  # JSON Schema
```

## Integration with Existing Systems

Command Registry is designed for easy integration with existing systems and frameworks:

- **FastAPI** - via RESTAdapter
- **Flask** - via RESTAdapter with modifications
- **aiohttp** - via WebSockets adapter
- **Click** - via CLI adapter
- **GraphQL** - via GraphQL adapter
- **MCP Proxy** - via MCPProxyAdapter for AI model integration

## Usage Examples

### REST API

```python
from fastapi import FastAPI
from command_registry import CommandRegistry
from command_registry.adapters import RESTAdapter

app = FastAPI()
registry = CommandRegistry()
registry.scan_module("myapp.commands")

adapter = RESTAdapter(registry)
adapter.register_endpoints(app)
```

### JSON-RPC via MCP Proxy Adapter

```python
from fastapi import FastAPI
from command_registry import CommandRegistry
from mcp_proxy_adapter.adapter import MCPProxyAdapter

app = FastAPI()
registry = CommandRegistry()
registry.scan_module("myapp.commands")

adapter = MCPProxyAdapter(registry)
adapter.register_endpoints(app)
```

## License

MIT 
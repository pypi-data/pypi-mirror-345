# Command Registry Architecture

This document describes the architecture of the Command Registry system, its key components, their interactions, and extension principles.

## Architecture Overview

Command Registry is a modular system built around the concept of centralized command storage and management. The architecture ensures flexibility, extensibility, and adherence to SOLID principles.

Key system capabilities:

1. **Defining commands as Python functions** using type hints and docstrings
2. **Metadata extraction** from function signatures and their documentation
3. **Command registration** in a central registry
4. **Providing a unified interface** for command execution
5. **API documentation generation** based on command metadata
6. **Command export** through various protocols (REST, JSON-RPC, CLI, etc.)

## System Components

![Components Diagram](../diagrams/command_registry_components.png)

### Core Components:

1. **Command Definition** - Command definition (Python function with type hints and docstrings)
2. **Dispatcher Component** - Command dispatcher responsible for registration and execution
3. **Metadata Extractor** - Extracts metadata from docstrings and function signatures
4. **Protocol Adapter** - Adapter for exporting commands through various protocols

### CommandRegistry

The central system component that:

- Initializes and configures dispatchers
- Provides an interface for command registration
- Manages command metadata
- Coordinates interaction between components

## Command Lifecycle

### 1. Command Definition

```python
def calculate_total(
    prices: List[float], 
    discount: float = 0.0,
    tax_rate: float = 0.0
) -> float:
    """
    Calculates total cost including discount and tax.
    
    Args:
        prices: List of item prices
        discount: Discount percentage (0-100)
        tax_rate: Tax rate percentage (0-100)
        
    Returns:
        Total cost including discount and tax
    """
    subtotal = sum(prices)
    discounted = subtotal * (1 - discount / 100)
    total = discounted * (1 + tax_rate / 100)
    return round(total, 2)
```

### 2. Command Registration

```python
from command_registry import CommandRegistry
from command_registry.dispatchers import CommandDispatcher

# Create command registry
registry = CommandRegistry(CommandDispatcher())

# Register command
registry.register_command("calculate_total", calculate_total)
```

### 3. Command Execution

```python
# Execute command
result = registry.execute(
    "calculate_total", 
    {
        "prices": [10.0, 20.0, 30.0],
        "discount": 10.0,
        "tax_rate": 7.0
    }
)
print(result)  # 57.33
```

### 4. API Export

```python
from fastapi import FastAPI
from command_registry.adapters import RESTAdapter

app = FastAPI()
adapter = RESTAdapter(registry)
adapter.register_endpoints(app)
```

## Data Flow Diagrams

### Command Registration Process

```
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│  Python Function├─────►│  Metadata Extractor ├─────►│  Metadata      │
│                 │      │                    │      │                 │
└─────────────────┘      └────────────────────┘      └────────┬────────┘
                                                              │
                                                              ▼
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│  CommandRegistry│◄─────┤  Data Validation   │◄─────┤  Parameters    │
│                 │      │                    │      │                 │
└────────┬────────┘      └────────────────────┘      └─────────────────┘
         │
         ▼
┌─────────────────┐
│                 │
│  Dispatcher     │
│                 │
└─────────────────┘
```

### Command Execution Process

```
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│  Command Name   │      │                    │      │  Parameter      │
│  + Parameters   ├─────►│  CommandRegistry   ├─────►│  Validation    │
│                 │      │                    │      │                 │
└─────────────────┘      └────────────────────┘      └────────┬────────┘
                                                              │
                                                              ▼
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│  Result         │◄─────┤  Error Handling    │◄─────┤  Dispatcher     │
│                 │      │                    │      │  (execution)    │
└─────────────────┘      └────────────────────┘      └─────────────────┘
```

### API Documentation Generation

```
┌─────────────────┐      ┌────────────────────┐      ┌─────────────────┐
│                 │      │                    │      │                 │
│  Command        │      │  Schema Generator  │      │  OpenAPI/       │
│  Metadata       ├─────►│                    ├─────►│  JSON Schema    │
│                 │      │                    │      │                 │
└─────────────────┘      └────────────────────┘      └────────┬────────┘
                                                              │
                                                              ▼
                                                     ┌─────────────────┐
                                                     │                 │
                                                     │  API Docs UI    │
                                                     │  (Swagger/      │
                                                     │   ReDoc)        │
                                                     └─────────────────┘
```

## System Extension

### Creating a Custom Dispatcher

```python
from command_registry.dispatchers import BaseDispatcher
from typing import Dict, Any, List, Optional, Callable

class MyCustomDispatcher(BaseDispatcher):
    def __init__(self):
        self._commands = {}
        self._info = {}
        
    def register_handler(
        self, 
        command_name: str,
        handler: Callable,
        description: str = None,
        summary: str = None,
        params: Dict[str, Any] = None
    ) -> None:
        self._commands[command_name] = handler
        self._info[command_name] = {
            "description": description,
            "summary": summary,
            "params": params or {}
        }
        
    def execute(self, command_name: str, params: Dict[str, Any] = None) -> Any:
        if command_name not in self._commands:
            raise ValueError(f"Command '{command_name}' not found")
        
        handler = self._commands[command_name]
        return handler(**params or {})
    
    def get_valid_commands(self) -> List[str]:
        return list(self._commands.keys())
    
    def get_command_info(self, command_name: str) -> Optional[Dict[str, Any]]:
        return self._info.get(command_name)
    
    def get_commands_info(self) -> Dict[str, Dict[str, Any]]:
        return self._info
```

### Creating a Custom Protocol Adapter

```python
from command_registry import CommandRegistry
from typing import Dict, Any

class GraphQLAdapter:
    def __init__(self, registry: CommandRegistry):
        self.registry = registry
        
    def generate_schema(self) -> str:
        """Generates GraphQL schema based on command metadata."""
        commands_info = self.registry.get_all_commands_info()
        schema_types = []
        query_fields = []
        
        for cmd_name, info in commands_info.items():
            # Generate types for input and output data
            input_type = self._generate_input_type(cmd_name, info["params"])
            output_type = self._generate_output_type(cmd_name, info.get("returns"))
            
            schema_types.extend([input_type, output_type])
            
            # Add field to Query
            query_fields.append(
                f"{cmd_name}(input: {cmd_name}Input): {cmd_name}Output"
            )
        
        # Form final schema
        schema = "\n".join(schema_types)
        schema += f"\ntype Query {{\n  {chr(10).join(query_fields)}\n}}"
        
        return schema
    
    def _generate_input_type(self, cmd_name: str, params: Dict[str, Any]) -> str:
        fields = []
        for name, param_info in params.items():
            field_type = self._map_type(param_info.get("type", "String"))
            required = "!" if param_info.get("required", False) else ""
``` 
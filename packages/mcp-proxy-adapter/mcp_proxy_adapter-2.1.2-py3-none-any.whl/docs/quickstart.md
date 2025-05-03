# Command Registry Quick Start

This guide will help you quickly get started with the Command Registry system and integrate it into your application.

## Installation

Install the package using pip:

```bash
pip install command-registry
```

## Basic Usage

### 1. Defining a Command

Create a `commands.py` file with your commands:

```python
from typing import List, Dict, Any, Optional

def add_item(
    item_name: str,
    quantity: int = 1,
    properties: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Adds a new item to the system.
    
    Args:
        item_name: Name of the item
        quantity: Item quantity (default 1)
        properties: Additional item properties
        
    Returns:
        Information about the created item
    """
    # In a real application, this would be code for
    # saving the item to a database
    item_id = "item_" + str(hash(item_name))
    item = {
        "id": item_id,
        "name": item_name,
        "quantity": quantity,
        "properties": properties or {}
    }
    return item

def get_items(
    search_term: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Gets a list of items with search and pagination capabilities.
    
    Args:
        search_term: String to search by name (optional)
        limit: Maximum number of items to return
        offset: Offset for result pagination
        
    Returns:
        List of items matching search criteria
    """
    # In a real application, this would be code for
    # retrieving items from a database
    items = [
        {"id": f"item_{i}", "name": f"Item {i}", "quantity": i % 10}
        for i in range(offset, offset + limit)
    ]
    
    if search_term:
        items = [item for item in items if search_term.lower() in item["name"].lower()]
        
    return items
```

### 2. Creating Command Registry

Create an `app.py` file with Command Registry initialization:

```python
from command_registry import CommandRegistry
from command_registry.dispatchers import CommandDispatcher
import commands

# Create dispatcher instance
dispatcher = CommandDispatcher()

# Create command registry
registry = CommandRegistry(dispatcher)

# Register commands
registry.register_command("add_item", commands.add_item)
registry.register_command("get_items", commands.get_items)

# Automatic registration of all commands from module (alternative way)
# registry.scan_module(commands)
```

### 3. Executing Commands

Add code to `app.py` for executing commands:

```python
# Execute add_item command
result = registry.execute(
    "add_item", 
    {
        "item_name": "Laptop",
        "quantity": 5,
        "properties": {"brand": "SuperLaptop", "color": "silver"}
    }
)
print("add_item result:", result)

# Execute get_items command
items = registry.execute(
    "get_items", 
    {
        "search_term": "Item",
        "limit": 5
    }
)
print(f"Found {len(items)} items:")
for item in items:
    print(f"- {item['name']} (ID: {item['id']}, Quantity: {item['quantity']})")
```

### 4. Command Information

```python
# Get list of available commands
commands = registry.get_valid_commands()
print("Available commands:", commands)

# Get information about specific command
info = registry.get_command_info("add_item")
print("Information about add_item command:")
print(f"- Description: {info['description']}")
print(f"- Parameters: {list(info['params'].keys())}")
```

## Web Framework Integration

### FastAPI

```python
from fastapi import FastAPI
from command_registry.adapters import RESTAdapter

app = FastAPI(title="Command Registry API")

# Create REST adapter
rest_adapter = RESTAdapter(registry)

# Register endpoints in FastAPI
rest_adapter.register_endpoints(app)

# Run application
# uvicorn app:app --reload
```

### Flask

```python
from flask import Flask
from command_registry.adapters import FlaskRESTAdapter

app = Flask(__name__)

# Create REST adapter for Flask
flask_adapter = FlaskRESTAdapter(registry)

# Register endpoints in Flask
flask_adapter.register_endpoints(app)

# Run application
# app.run(debug=True)
```

### aiohttp

```python
from aiohttp import web
from command_registry.adapters import AioHttpAdapter

app = web.Application()

# Create aiohttp adapter
aiohttp_adapter = AioHttpAdapter(registry)

# Register endpoints
aiohttp_adapter.register_endpoints(app)

# Run application
# web.run_app(app)
```

## Using JSON-RPC

```python
from fastapi import FastAPI
from command_registry.adapters import JSONRPCAdapter

app = FastAPI(title="Command Registry JSON-RPC API")

# Create JSON-RPC adapter
jsonrpc_adapter = JSONRPCAdapter(registry)

# Register JSON-RPC endpoint
jsonrpc_adapter.register_endpoint(app, "/api/jsonrpc")

# Run application
# uvicorn app:app --reload
```

## Command Line Integration

```python
from command_registry.adapters import ClickAdapter
import click

# Create adapter for Click
cli_adapter = ClickAdapter(registry)

# Create CLI application
cli = click.Group()

# Register commands
cli_adapter.register_commands(cli)

# Run CLI
if __name__ == "__main__":
    cli()
```

## Error Handling

```python
from command_registry.exceptions import (
    CommandNotFoundError,
    ValidationError,
    CommandExecutionError
)

try:
    result = registry.execute("non_existent_command", {})
except CommandNotFoundError as e:
    print(f"Error: Command not found - {e}")
``` 
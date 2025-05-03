"""
Example of creating an OpenAPI server using MCP Proxy Adapter.

Usage:
    python examples/openapi_server.py

Server will be available at: http://localhost:8000
"""
import os
import sys
import logging
from typing import Dict, List, Any

# Add project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI, Query, Path, Body, Request
from pydantic import BaseModel, Field
import uvicorn

# Import MCP Proxy Adapter
from mcp_proxy_adapter.adapter import MCPProxyAdapter

# Import models for JSON-RPC
from mcp_proxy_adapter.models import JsonRpcRequest, JsonRpcResponse

# Import MockRegistry from tests for example
# (in a real project, CommandRegistry would be used)
from tests.test_mcp_proxy_adapter import MockRegistry

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Data model definitions
class Item(BaseModel):
    """Data model for an item."""
    id: int = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Item name")
    description: str = Field(None, description="Item description")
    price: float = Field(..., description="Item price")
    is_available: bool = Field(True, description="Item availability")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Super Product",
                "description": "Best product on the market",
                "price": 99.99,
                "is_available": True
            }
        }
    }

# Example data
items_db = [
    {
        "id": 1,
        "name": "Smartphone X",
        "description": "Latest smartphone with cutting-edge technology",
        "price": 999.99,
        "is_available": True
    },
    {
        "id": 2,
        "name": "Laptop Y",
        "description": "Powerful laptop for professionals",
        "price": 1499.99,
        "is_available": True
    },
    {
        "id": 3,
        "name": "Tablet Z",
        "description": "Compact tablet for creativity",
        "price": 599.99,
        "is_available": False
    }
]

# Define commands for MockRegistry
class MockDispatcher:
    """Mock for command dispatcher in example."""
    
    def __init__(self):
        self.commands = {
            "get_items": self.get_items,
            "get_item": self.get_item,
            "create_item": self.create_item,
            "update_item": self.update_item,
            "delete_item": self.delete_item,
            "search_items": self.search_items,
            "execute": self.execute_command
        }
        self.commands_info = {
            "get_items": {
                "description": "Get list of all items",
                "params": {}
            },
            "get_item": {
                "description": "Get item by ID",
                "params": {
                    "item_id": {
                        "type": "integer",
                        "description": "Item ID to search for",
                        "required": True
                    }
                }
            },
            "create_item": {
                "description": "Create new item",
                "params": {
                    "item": {
                        "type": "object",
                        "description": "Item data",
                        "required": True
                    }
                }
            },
            "update_item": {
                "description": "Update item by ID",
                "params": {
                    "item_id": {
                        "type": "integer",
                        "description": "Item ID to update",
                        "required": True
                    },
                    "updated_data": {
                        "type": "object",
                        "description": "Updated data",
                        "required": True
                    }
                }
            },
            "delete_item": {
                "description": "Delete item by ID",
                "params": {
                    "item_id": {
                        "type": "integer",
                        "description": "Item ID to delete",
                        "required": True
                    }
                }
            },
            "search_items": {
                "description": "Search items by keyword",
                "params": {
                    "keyword": {
                        "type": "string",
                        "description": "Search keyword",
                        "required": True
                    }
                }
            },
            "execute": {
                "description": "Universal command for executing queries",
                "params": {
                    "query": {
                        "type": "string",
                        "description": "Query to execute",
                        "required": False
                    },
                    "subcommand": {
                        "type": "string",
                        "description": "Subcommand to execute",
                        "required": False
                    }
                }
            }
        }
    
    def execute(self, command, **params):
        """Executes command with specified parameters."""
        if command not in self.commands:
            raise KeyError(f"Unknown command: {command}")
        return self.commands[command](**params)
        
    def execute_command(self, **params):
        """Universal method for executing commands."""
        query = params.get("query", "")
        subcommand = params.get("subcommand", "")
        
        # Debug logging
        logger.info(f"Executing universal command with query={query}, subcommand={subcommand}, params={params}")
        
        # Handle different command types
        if query.lower() in ["list", "all", "items"]:
            # Return list of all items
            return self.get_items()
        elif query.lower() == "search" and "keyword" in params:
            # Search by keyword
            return self.search_items(params["keyword"])
        elif query.isdigit() or (isinstance(query, int) and query > 0):
            # If query looks like an ID, return item by ID
            try:
                return self.get_item(int(query))
            except ValueError:
                return {"error": f"Item with ID {query} not found"}
        else:
            # By default return information about available commands
            commands = list(self.commands.keys())
            return {
                "available_commands": commands,
                "message": "Use one of the available commands or specify query for executing query",
                "received_params": params
            }
    
    def get_valid_commands(self):
        """Returns list of available commands."""
        return list(self.commands.keys())
    
    def get_command_info(self, command):
        """Returns information about command."""
        return self.commands_info.get(command)
    
    def get_commands_info(self):
        """Returns information about all commands."""
        return self.commands_info
    
    # Command implementations
    def get_items(self):
        """Get list of all items."""
        return items_db
    
    def get_item(self, item_id):
        """Get item by ID."""
        for item in items_db:
            if item["id"] == item_id:
                return item
        raise ValueError(f"Item with ID {item_id} not found")
    
    def create_item(self, item):
        """Create new item."""
        # Find maximum ID
        max_id = max([i["id"] for i in items_db]) if items_db else 0
        # Create new item with increased ID
        new_item = {**item, "id": max_id + 1}
        items_db.append(new_item)
        return new_item
    
    def update_item(self, item_id, updated_data):
        """Update item by ID."""
        for i, item in enumerate(items_db):
            if item["id"] == item_id:
                # Update item, keeping original ID
                updated_item = {**item, **updated_data, "id": item_id}
                items_db[i] = updated_item
                return updated_item
        raise ValueError(f"Item with ID {item_id} not found")
    
    def delete_item(self, item_id):
        """Delete item by ID."""
        for i, item in enumerate(items_db):
            if item["id"] == item_id:
                del items_db[i]
                return {"message": f"Item with ID {item_id} successfully deleted"}
        raise ValueError(f"Item with ID {item_id} not found")
    
    def search_items(self, keyword):
        """Search items by keyword."""
        keyword = keyword.lower()
        return [
            item for item in items_db
            if keyword in item["name"].lower() or 
               (item["description"] and keyword in item["description"].lower())
        ]

class CustomMockRegistry(MockRegistry):
    """Custom command registry for example."""
    
    def __init__(self):
        """Initialization with custom dispatcher."""
        self.dispatcher = MockDispatcher()
        self.generators = []

def main():
    """Main function to start server."""
    # Create command registry
    registry = CustomMockRegistry()
    
    # Create FastAPI object
    app = FastAPI(
        title="OpenAPI Server Example",
        description="Example OpenAPI server with MCP Proxy Adapter integration",
        version="1.0.0"
    )
    
    # Configure CORS
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow requests from all sources
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    )
    
    # Create MCP Proxy adapter with explicit endpoint
    adapter = MCPProxyAdapter(registry, cmd_endpoint="/cmd")
    
    # Register adapter endpoints
    adapter.register_endpoints(app)
    
    # Save MCP Proxy configuration to file
    config_path = os.path.join(os.path.dirname(__file__), "mcp_proxy_config.json")
    adapter.save_config_to_file(config_path)
    logger.info(f"MCP Proxy configuration saved to {config_path}")
    
    # Define REST endpoints for example (not related to MCP Proxy)
    @app.get("/")
    def read_root():
        """Root endpoint."""
        return {
            "message": "OpenAPI Server Example with MCP Proxy Adapter integration",
            "endpoints": {
                "items": "/items",
                "item": "/items/{item_id}",
                "search": "/items/search",
                "mcp_proxy": "/cmd"
            }
        }
    
    @app.get("/items", response_model=List[Item])
    def read_items():
        """Get all items."""
        return items_db
    
    @app.get("/items/{item_id}", response_model=Item)
    def read_item(item_id: int = Path(..., description="Item ID", gt=0)):
        """Get item by ID."""
        try:
            return registry.dispatcher.get_item(item_id)
        except ValueError as e:
            return {"error": str(e)}
    
    @app.post("/items", response_model=Item)
    def create_new_item(item: Item = Body(..., description="Data of new item")):
        """Create new item."""
        return registry.dispatcher.create_item(item.model_dump())
    
    @app.put("/items/{item_id}", response_model=Item)
    def update_existing_item(
        item_id: int = Path(..., description="Item ID to update", gt=0),
        item: Item = Body(..., description="Updated item data")
    ):
        """Update item by ID."""
        try:
            return registry.dispatcher.update_item(item_id, item.model_dump())
        except ValueError as e:
            return {"error": str(e)}
    
    @app.delete("/items/{item_id}")
    def delete_existing_item(item_id: int = Path(..., description="Item ID to delete", gt=0)):
        """Delete item by ID."""
        try:
            return registry.dispatcher.delete_item(item_id)
        except ValueError as e:
            return {"error": str(e)}
    
    @app.get("/items/search", response_model=List[Item])
    def search_items_by_keyword(keyword: str = Query(..., description="Search keyword")):
        """Search items by keyword."""
        return registry.dispatcher.search_items(keyword)
    
    # Start server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main() 
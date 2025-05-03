"""
Example of basic MCPProxyAdapter integration with an existing FastAPI application.
"""
import logging
import os
import sys
from typing import Dict, Any, List, Optional

# Add parent directory to import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel

# Import from installed package or local file
try:
    from mcp_proxy_adapter.adapter import MCPProxyAdapter, configure_logger
    from mcp_proxy_adapter.registry import CommandRegistry
except ImportError:
    from src.adapter import MCPProxyAdapter, configure_logger
    from src.registry import CommandRegistry

# Configure project logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create project logger
project_logger = logging.getLogger("my_project")
project_logger.setLevel(logging.DEBUG)

# Configure adapter logger using project logger
adapter_logger = configure_logger(project_logger)

# Create FastAPI application
app = FastAPI(
    title="My API with MCP Proxy Integration",
    description="API with Command Registry integration, supporting MCP Proxy",
    version="1.0.0"
)

# Define existing endpoints
router = APIRouter()

class Item(BaseModel):
    name: str
    price: float
    is_active: bool = True

@router.get("/items", response_model=List[Item])
async def get_items():
    """Returns list of items."""
    return [
        {"name": "Item 1", "price": 10.5, "is_active": True},
        {"name": "Item 2", "price": 20.0, "is_active": False},
        {"name": "Item 3", "price": 30.0, "is_active": True},
    ]

@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Returns item information by ID."""
    items = [
        {"name": "Item 1", "price": 10.5, "is_active": True},
        {"name": "Item 2", "price": 20.0, "is_active": False},
        {"name": "Item 3", "price": 30.0, "is_active": True},
    ]
    
    if item_id < 1 or item_id > len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    
    return items[item_id - 1]

# Add existing endpoints to application
app.include_router(router)

# Define commands for Command Registry
def list_items() -> List[Dict[str, Any]]:
    """
    Returns list of all items.
    
    Returns:
        List[Dict[str, Any]]: List of items
    """
    return [
        {"name": "Item 1", "price": 10.5, "is_active": True},
        {"name": "Item 2", "price": 20.0, "is_active": False},
        {"name": "Item 3", "price": 30.0, "is_active": True},
    ]

def get_item_by_id(item_id: int) -> Dict[str, Any]:
    """
    Returns item information by ID.
    
    Args:
        item_id: Item ID
        
    Returns:
        Dict[str, Any]: Item information
        
    Raises:
        ValueError: If item is not found
    """
    items = list_items()
    
    if item_id < 1 or item_id > len(items):
        raise ValueError(f"Item with ID {item_id} not found")
    
    return items[item_id - 1]

def search_items(query: str, min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Dict[str, Any]]:
    """
    Searches for items by name and price range.
    
    Args:
        query: Search query for name
        min_price: Minimum price (optional)
        max_price: Maximum price (optional)
        
    Returns:
        List[Dict[str, Any]]: List of found items
    """
    items = list_items()
    
    # Filter by name
    filtered_items = [item for item in items if query.lower() in item["name"].lower()]
    
    # Filter by minimum price
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] >= min_price]
    
    # Filter by maximum price
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item["price"] <= max_price]
    
    return filtered_items

# Create CommandRegistry instance
registry = CommandRegistry()

# Register commands
registry.register_command("list_items", list_items)
registry.register_command("get_item", get_item_by_id)
registry.register_command("search_items", search_items)

# Create MCP Proxy adapter
adapter = MCPProxyAdapter(registry)

# Register endpoints in existing application
adapter.register_endpoints(app)

# Save configuration for MCP Proxy
adapter.save_config_to_file("mcp_proxy_config.json")

# Entry point for running the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
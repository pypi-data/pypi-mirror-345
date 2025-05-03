# Command Registry Usage Examples

This section provides practical examples of using Command Registry for various scenarios.

## Contents

- [Basic Examples](#basic-examples)
- [FastAPI Integration](#fastapi-integration)
- [JSON-RPC Integration](#json-rpc-integration)
- [Creating CLI](#creating-cli)
- [Complete Project Example](#complete-project-example)

## Basic Examples

### Example 1: Creating and Registering a Command

```python
from typing import Dict, Any, List

# Create a simple command
def search_by_keywords(keywords: List[str], limit: int = 10) -> Dict[str, Any]:
    """
    Search records by keywords.
    
    Args:
        keywords: List of keywords
        limit: Maximum number of results
        
    Returns:
        Dict[str, Any]: Search results
    """
    # Here would be real search code
    results = [
        {"id": 1, "title": "Result 1", "score": 0.95},
        {"id": 2, "title": "Result 2", "score": 0.87}
    ]
    return {"results": results[:limit], "total": len(results)}

# Register the command
from command_registry import CommandRegistry

registry = CommandRegistry()
registry.register_command("search_by_keywords", search_by_keywords)

# Execute the command
result = registry.dispatcher.execute(
    "search_by_keywords", 
    keywords=["python", "api"],
    limit=5
)
print(result)
```

### Example 2: Using Metadata Dictionary

```python
# Command with explicit metadata
def filter_data(filter_params: Dict[str, Any]) -> Dict[str, Any]:
    """Filter data by parameters"""
    # Implementation...
    pass

# Command metadata dictionary
COMMAND = {
    "description": "Filter data by various parameters",
    "parameters": {
        "filter_params": {
            "type": "object",
            "description": "Filter parameters",
            "required": True,
            "properties": {
                "date_from": {
                    "type": "string",
                    "format": "date",
                    "description": "Start date (YYYY-MM-DD)"
                },
                "date_to": {
                    "type": "string",
                    "format": "date",
                    "description": "End date (YYYY-MM-DD)"
                },
                "categories": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of categories"
                }
            }
        }
    },
    "responses": {
        "success": {
            "description": "Filtered data",
            "schema": {
                "type": "object",
                "properties": {
                    "results": {
                        "type": "array",
                        "items": {"type": "object"}
                    },
                    "total": {"type": "integer"}
                }
            }
        }
    }
}
```

## FastAPI Integration

### Creating REST API Based on Commands

```python
from fastapi import FastAPI
from command_registry import CommandRegistry
from command_registry.generators import RestApiGenerator

# Create FastAPI application
app = FastAPI(title="Example API")

# Create command registry
registry = CommandRegistry()

# Specify modules to search for commands
registry.scan_modules(["commands.search", "commands.filter"])

# Register all commands
registry.register_all_commands()

# Create REST API generator
rest_generator = RestApiGenerator(app)

# Generate endpoints for all commands
endpoints = rest_generator.generate_all_endpoints()

# Information about created endpoints
print(f"Created {len(endpoints)} REST endpoints:")
for endpoint in endpoints:
    print(f"- {endpoint}")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

This approach will automatically create REST endpoints for all your commands:

```
GET /help                   # API Help
POST /search_by_keywords    # Search by keywords
POST /filter_data           # Filter data
```

## JSON-RPC Integration

### Creating JSON-RPC Server

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

from command_registry import CommandRegistry

# Create FastAPI application
app = FastAPI(title="JSON-RPC API")

# Create command registry
registry = CommandRegistry()

# Register commands
registry.scan_modules(["commands"])
registry.register_all_commands()

# JSON-RPC request model
class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[str] = None

# Endpoint for handling JSON-RPC requests
@app.post("/rpc")
async def rpc_endpoint(request: JsonRpcRequest):
    try:
        # Extract request parameters
        method = request.method
        params = request.params or {}
        req_id = request.id
        
        # Check if command exists
        if method not in registry.dispatcher.get_valid_commands():
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                },
                "id": req_id
            })
        
        # Execute command
        result = registry.dispatcher.execute(method, **params)
        
        # Return successful response
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "result": result,
            "id": req_id
        })
    except Exception as e:
        # Return error
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": str(e)
            },
            "id": request.id
        })

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
```

Example of using JSON-RPC API:

```json
// Request
{
  "jsonrpc": "2.0",
  "method": "search_by_keywords",
  "params": {
    "keywords": ["python", "api"],
    "limit": 5
  },
  "id": "1"
}

// Response
{
  "jsonrpc": "2.0",
  "result": {
    "results": [
      {"id": 1, "title": "Result 1", "score": 0.95},
      {"id": 2, "title": "Result 2", "score": 0.87}
    ],
    "total": 2
  },
  "id": "1"
} 
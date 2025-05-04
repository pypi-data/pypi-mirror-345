"""
Client for testing interaction with OpenAPI server through MCP Proxy.

This script demonstrates how a client can send JSON-RPC requests
to MCP Proxy, which forwards them to the OpenAPI server.

Usage:
    python examples/mcp_proxy_client.py
"""
import os
import sys
import json
import requests
from typing import Dict, Any, Optional

def send_jsonrpc_request(
    endpoint: str, 
    method: str, 
    params: Optional[Dict[str, Any]] = None, 
    request_id: int = 1
) -> Dict[str, Any]:
    """
    Sends JSON-RPC request to specified endpoint.
    
    Args:
        endpoint (str): Endpoint URL
        method (str): Method name to call
        params (Optional[Dict[str, Any]], optional): Method parameters. Defaults to None.
        request_id (int, optional): Request ID. Defaults to 1.
        
    Returns:
        Dict[str, Any]: Server response
    """
    # Form JSON-RPC request
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "id": request_id
    }
    
    # Add parameters if they exist
    if params:
        payload["params"] = params
    
    # Send request
    response = requests.post(endpoint, json=payload)
    
    # Return response in JSON format
    return response.json()

def print_response(response: Dict[str, Any]) -> None:
    """
    Prints response in formatted view.
    
    Args:
        response (Dict[str, Any]): Server response
    """
    print("Response:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    print("-" * 50)

def main():
    """Main function for demonstrating work with MCP Proxy."""
    # Base server URL
    server_url = "http://localhost:8000"
    
    # JSON-RPC endpoint (should match cmd_endpoint in MCPProxyAdapter)
    jsonrpc_endpoint = f"{server_url}/api/command"
    
    print("=== Testing JSON-RPC requests through MCP Proxy ===\n")
    
    # Example 1: Get all items
    print("1. Getting all items:")
    response = send_jsonrpc_request(jsonrpc_endpoint, "get_items")
    print_response(response)
    
    # Example 2: Get item by ID
    print("2. Getting item by ID:")
    response = send_jsonrpc_request(jsonrpc_endpoint, "get_item", {"item_id": 1})
    print_response(response)
    
    # Example 3: Create new item
    print("3. Creating new item:")
    new_item = {
        "name": "Test Item",
        "description": "Item for API testing",
        "price": 123.45,
        "is_available": True
    }
    response = send_jsonrpc_request(jsonrpc_endpoint, "create_item", {"item": new_item})
    print_response(response)
    
    # Get created item ID for further operations
    if "result" in response:
        created_item_id = response["result"]["id"]
    else:
        # Use fixed ID in case of error
        created_item_id = 4
    
    # Example 4: Update item
    print(f"4. Updating item with ID {created_item_id}:")
    updated_data = {
        "name": "Updated Item",
        "price": 199.99
    }
    response = send_jsonrpc_request(
        jsonrpc_endpoint, 
        "update_item", 
        {"item_id": created_item_id, "updated_data": updated_data}
    )
    print_response(response)
    
    # Example 5: Search items
    print("5. Searching items by keyword:")
    response = send_jsonrpc_request(jsonrpc_endpoint, "search_items", {"keyword": "updated"})
    print_response(response)
    
    # Example 6: Delete item
    print(f"6. Deleting item with ID {created_item_id}:")
    response = send_jsonrpc_request(jsonrpc_endpoint, "delete_item", {"item_id": created_item_id})
    print_response(response)
    
    # Example 7: Check after deletion
    print("7. Checking items list after deletion:")
    response = send_jsonrpc_request(jsonrpc_endpoint, "get_items")
    print_response(response)
    
    print("Testing completed.")

if __name__ == "__main__":
    main() 
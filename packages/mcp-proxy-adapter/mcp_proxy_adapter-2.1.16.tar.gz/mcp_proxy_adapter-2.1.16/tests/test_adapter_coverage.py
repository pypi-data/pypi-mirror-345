"""
Tests for MCPProxyAdapter code coverage.
"""
import sys
import os
import pytest
import json
import logging
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List, Optional

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import tested modules
try:
    from mcp_proxy_adapter.adapter import MCPProxyAdapter, CommandRegistry
    from mcp_proxy_adapter.models import JsonRpcRequest, JsonRpcResponse, MCPProxyConfig
except ImportError:
    from src.adapter import MCPProxyAdapter, CommandRegistry
    from src.models import JsonRpcRequest, JsonRpcResponse, MCPProxyConfig

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Mock for command dispatcher
class MockDispatcher:
    """Mock for command dispatcher in tests."""
    
    def __init__(self):
        self.commands = {
            "success": lambda value=1: {"result": value * 2},
            "error": lambda: exec('raise ValueError("Test error")'),
            "execute": self.execute_from_params
        }
        self.commands_info = {
            "success": {
                "description": "Successful command",
                "params": {
                    "value": {
                        "type": "integer",
                        "description": "Input value",
                        "required": False,
                        "default": 1
                    }
                }
            },
            "error": {
                "description": "Command with error",
                "params": {}
            },
            "execute": {
                "description": "Universal command for executing other commands",
                "params": {
                    "query": {
                        "type": "string",
                        "description": "Command or query to execute",
                        "required": False
                    }
                }
            }
        }
    
    def execute_from_params(self, **params):
        """Executes command based on parameters."""
        if "query" in params and params["query"] in self.commands:
            command = params.pop("query")
            return self.execute(command, **params)
        return {
            "available_commands": self.get_valid_commands(),
            "received_params": params
        }
    
    def execute(self, command, **params):
        """Executes command with specified parameters."""
        if command not in self.commands:
            raise KeyError(f"Unknown command: {command}")
        return self.commands[command](**params)
    
    def get_valid_commands(self):
        """Returns list of available commands."""
        return list(self.commands.keys())
    
    def get_command_info(self, command):
        """Returns information about command."""
        return self.commands_info.get(command)
    
    def get_commands_info(self):
        """Returns information about all commands."""
        return self.commands_info

# Mock for CommandRegistry
class MockRegistry:
    """Mock for CommandRegistry in tests."""
    
    def __init__(self):
        self.dispatcher = MockDispatcher()
        self.generators = []
    
    def get_commands_info(self):
        """Returns command information from dispatcher."""
        return self.dispatcher.get_commands_info()
    
    def add_generator(self, generator):
        """Adds API generator."""
        self.generators.append(generator)

# Tests targeting uncovered code sections in adapter.py
def test_openapi_generator_import_error():
    """Test for simulating OpenApiGenerator import error situation."""
    # Use more specific patch for OpenApiGenerator import
    with patch('mcp_proxy_adapter.adapter.OpenApiGenerator', side_effect=ImportError("Mocked import error")):
        registry = MockRegistry()
        adapter = MCPProxyAdapter(registry)
        
        # Check that adapter was created and works even without OpenApiGenerator
        assert adapter.openapi_generator is None
        
        # Create application and check functionality
        app = FastAPI()
        adapter.register_endpoints(app)
        client = TestClient(app)
        
        # Check that API commands work
        response = client.get("/api/commands")
        assert response.status_code == 200
        assert "commands" in response.json()

def test_protocol_errors():
    """Test for working with disabled schema."""
    registry = MockRegistry()
    
    # Test without schema inclusion
    adapter = MCPProxyAdapter(registry, include_schema=False, optimize_schema=False)
    
    # Check that adapter has no OpenAPI schema endpoint
    # For this we look at router routes
    routes = [route for route in adapter.router.routes if hasattr(route, 'path')]
    openapi_routes = [route for route in routes if route.path == "/openapi.json"]
    
    # Make sure OpenAPI route is absent
    assert len(openapi_routes) == 0

def test_api_endpoints():
    """Test for checking API endpoints."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    
    app = FastAPI()
    adapter.register_endpoints(app)
    client = TestClient(app)
    
    # Check /api/commands endpoint
    response = client.get("/api/commands")
    assert response.status_code == 200
    data = response.json()
    assert "commands" in data

def test_exception_handling():
    """Test for handling exceptions during command execution."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    
    app = FastAPI()
    adapter.register_endpoints(app)
    client = TestClient(app)
    
    # Test error during JSON parsing
    response = client.post("/cmd", content="invalid json")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "Invalid JSON format" in data["error"]["message"]

def test_mcp_proxy_format():
    """Test for checking MCP Proxy format."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    
    app = FastAPI()
    adapter.register_endpoints(app)
    client = TestClient(app)
    
    # Test MCP Proxy format
    response = client.post("/cmd", json={
        "command": "success",
        "params": {"value": 10}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"] == {"result": 20}

def test_query_subcommand():
    """Test for extracting command from query with / separator."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    
    # Patch execute method for test
    registry.dispatcher.execute = MagicMock(return_value={"subcommand_executed": True})
    
    app = FastAPI()
    adapter.register_endpoints(app)
    client = TestClient(app)
    
    # Test command extraction from query with / separator
    response = client.post("/cmd", json={
        "params": {"query": "success/subcommand"}
    })
    
    assert response.status_code == 200
    registry.dispatcher.execute.assert_called_once()

def test_only_params_with_command():
    """Test for request with only params containing command."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    
    app = FastAPI()
    adapter.register_endpoints(app)
    client = TestClient(app)
    
    # Test request with command in params
    response = client.post("/cmd", json={
        "params": {"command": "success", "value": 15}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"] == {"result": 30}

def test_error_responses():
    """Test for checking response formats for different errors."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    
    app = FastAPI()
    adapter.register_endpoints(app)
    client = TestClient(app)
    
    # Test unknown command
    response = client.post("/cmd", json={
        "command": "unknown",
        "params": {}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "Unknown command" in data["error"]["message"]

def test_register_endpoints_order():
    """Test for checking order of endpoint registration."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    
    # Create mock for router and include_router
    app = FastAPI()
    original_include_router = app.include_router
    app.include_router = MagicMock()
    
    # Register endpoints
    adapter.register_endpoints(app)
    
    # Check that include_router was called
    app.include_router.assert_called_once()
    
    # Restore original method
    app.include_router = original_include_router 
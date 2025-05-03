"""
Tests for MCPProxyAdapter, checking integration with CommandRegistry
and correct handling of different types of errors.
"""
import json
import logging
import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List, Optional, Callable, Type
import inspect
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Add parent directory to import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import tested modules
try:
    from mcp_proxy_adapter.models import JsonRpcRequest, JsonRpcResponse, MCPProxyConfig
    from mcp_proxy_adapter.adapter import MCPProxyAdapter, configure_logger
    from mcp_proxy_adapter.registry import CommandRegistry
except ImportError:
    from src.models import JsonRpcRequest, JsonRpcResponse, MCPProxyConfig
    from src.adapter import MCPProxyAdapter, configure_logger
    from src.registry import CommandRegistry

# Test command functions
def success_command(value: int = 1) -> dict:
    """Test command that completes successfully."""
    return {"result": value * 2}

def error_command() -> None:
    """Test command that generates an error."""
    raise ValueError("Test error")

def param_command(required_param: str, optional_param: int = 0) -> dict:
    """Test command with required and optional parameters."""
    return {"required": required_param, "optional": optional_param}

# Base class for dispatcher, define it here for tests
class BaseDispatcher:
    """Base class for command dispatcher."""
    
    def execute(self, command, **params):
        """Executes a command with specified parameters."""
        raise NotImplementedError("Method must be overridden in subclass")
    
    def get_valid_commands(self):
        """Returns a list of available commands."""
        raise NotImplementedError("Method must be overridden in subclass")
    
    def get_command_info(self, command):
        """Returns information about a command."""
        raise NotImplementedError("Method must be overridden in subclass")
    
    def get_commands_info(self):
        """Returns information about all commands."""
        raise NotImplementedError("Method must be overridden in subclass")

# Mock for command dispatcher
class MockDispatcher(BaseDispatcher):
    """Mock for command dispatcher in tests."""
    
    def __init__(self):
        self.commands = {
            "success": success_command,
            "error": error_command,
            "param": param_command,
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
            "param": {
                "description": "Command with parameters",
                "params": {
                    "required_param": {
                        "type": "string",
                        "description": "Required parameter",
                        "required": True
                    },
                    "optional_param": {
                        "type": "integer",
                        "description": "Optional parameter",
                        "required": False,
                        "default": 0
                    }
                }
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
        if command not in self.commands:
            raise KeyError(f"Unknown command: {command}")
        return self.commands[command](**params)
    
    def get_valid_commands(self):
        return list(self.commands.keys())
    
    def get_command_info(self, command):
        return self.commands_info.get(command)
    
    def get_commands_info(self):
        return self.commands_info

# Mock for CommandRegistry
class MockRegistry:
    """Mock for CommandRegistry in tests."""
    
    def __init__(self):
        self.dispatcher = MockDispatcher()
        self.generators = []
    
    def get_commands_info(self):
        """Returns command information from the dispatcher."""
        return self.dispatcher.get_commands_info()
    
    def add_generator(self, generator):
        """Adds an API generator."""
        self.generators.append(generator)
        if hasattr(generator, 'set_dispatcher'):
            generator.set_dispatcher(self.dispatcher)

# Fixtures for tests
@pytest.fixture
def registry():
    """Returns a mock command registry."""
    return MockRegistry()

@pytest.fixture
def adapter(registry):
    """Returns a configured adapter for tests."""
    return MCPProxyAdapter(registry)

@pytest.fixture
def test_app(adapter):
    """Creates a test FastAPI application with configured adapter."""
    app = FastAPI()
    adapter.register_endpoints(app)
    return TestClient(app)

@pytest.fixture
def custom_endpoint_adapter(registry):
    """Returns an adapter with custom endpoint."""
    return MCPProxyAdapter(registry, cmd_endpoint="/api/execute")

@pytest.fixture
def custom_endpoint_app(custom_endpoint_adapter):
    """Creates a test application with an adapter having a custom endpoint."""
    app = FastAPI()
    custom_endpoint_adapter.register_endpoints(app)
    return TestClient(app)

@pytest.fixture
def custom_logger():
    """Creates a custom logger for tests."""
    logger = logging.getLogger("mcp_proxy_adapter")
    logger.setLevel(logging.DEBUG)
    
    # Clear handlers if they were added in previous tests
    if logger.handlers:
        logger.handlers = []
    
    # Add handler that will record messages to list
    log_records = []
    
    class ListHandler(logging.Handler):
        def emit(self, record):
            log_records.append(self.format(record))
    
    handler = ListHandler()
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger, log_records

# Tests for adapter
def test_successful_command_execution(test_app):
    """Test successful command execution."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "success",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == {"result": 10}

def test_error_command_execution(test_app):
    """Test error handling when executing a command."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "error",
        "id": 1
    })
    assert response.status_code == 200  # JSON-RPC always returns 200
    data = response.json()
    assert "error" in data
    assert "Test error" in data["error"]["message"]

def test_unknown_command(test_app):
    """Test handling of unknown command."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "unknown_command",
        "id": 1
    })
    assert response.status_code == 200  # JSON-RPC always returns 200
    data = response.json()
    assert "error" in data
    assert "Unknown command" in data["error"]["message"]

def test_missing_required_parameter(test_app):
    """Test handling of missing required parameter."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "param",
        "params": {},  # Missing required parameter required_param
        "id": 1
    })
    assert response.status_code == 200  # JSON-RPC always returns 200
    data = response.json()
    assert "error" in data
    assert "required_param" in data["error"]["message"].lower()

def test_custom_endpoint(custom_endpoint_app):
    """Test adapter working with custom endpoint."""
    # Check that custom endpoint works
    response = custom_endpoint_app.post("/api/execute", json={
        "jsonrpc": "2.0",
        "method": "success",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"] == {"result": 10}

    # Also test standard endpoint, which is now also available
    # with our changes in register_endpoints
    response = custom_endpoint_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "success",
        "params": {"value": 3},
        "id": 2
    })
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"] == {"result": 6}

def test_adapter_config_with_custom_endpoint(custom_endpoint_adapter):
    """Test adapter configuration with custom endpoint."""
    config = custom_endpoint_adapter.generate_mcp_proxy_config()
    
    # Check that custom endpoint is used in configuration
    assert len(config.routes) > 0
    for route in config.routes:
        assert route["endpoint"] == "/api/execute"

def test_custom_logger_integration(registry, custom_logger):
    """Test integration with external logger."""
    logger, log_records = custom_logger
    
    # Patch logger in adapter module with correct path to module
    with patch('src.adapter.logger', logger):
        adapter = MCPProxyAdapter(registry)
        
        # Create application for tests
        app = FastAPI()
        adapter.register_endpoints(app)
        client = TestClient(app)
        
        # Execute command with error to trigger logging
        client.post("/cmd", json={
            "jsonrpc": "2.0",
            "method": "error",
            "id": 1
        })
        
        # DEBUG: print log_records if test fails
        if not any("error" in record.lower() for record in log_records):
            print("LOG RECORDS:", log_records)
        assert any("error" in record.lower() for record in log_records), f"No error in log_records: {log_records}"

def test_schema_generation(adapter):
    """Test schema generation."""
    # Create mock for schema generator
    adapter.openapi_generator = MagicMock()
    adapter.openapi_generator.generate_schema.return_value = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {}
    }

    # Patch schema_optimizer
    original_optimize = adapter.schema_optimizer.optimize
    adapter.schema_optimizer.optimize = MagicMock(side_effect=lambda schema, *args, **kwargs: schema)

    # Create application and client for tests
    app = FastAPI(title="Test API")
    adapter.register_endpoints(app)
    client = TestClient(app)

    # Request schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
    
    # Restore original method
    adapter.schema_optimizer.optimize = original_optimize

def test_schema_generation_without_generator(registry):
    """Test schema generation without generator."""
    # Create adapter without schema generator
    adapter = MCPProxyAdapter(registry)
    adapter.openapi_generator = None

    # Patch _generate_basic_schema
    original_method = adapter._generate_basic_schema
    mock_schema = {
        "openapi": "3.0.0",
        "info": {"title": "Basic API", "version": "1.0.0"},
        "paths": {}
    }
    adapter._generate_basic_schema = MagicMock(return_value=mock_schema)

    # Patch schema_optimizer
    original_optimize = adapter.schema_optimizer.optimize
    adapter.schema_optimizer.optimize = MagicMock(side_effect=lambda schema, *args, **kwargs: schema)

    # Create application and client for tests
    app = FastAPI(title="Basic API")
    adapter.register_endpoints(app)
    client = TestClient(app)

    # Request schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
    
    # Restore original methods
    adapter._generate_basic_schema = original_method
    adapter.schema_optimizer.optimize = original_optimize

def test_config_generation(adapter):
    """Test configuration generation for MCP Proxy."""
    # Generate configuration
    config = adapter.generate_mcp_proxy_config()
    # Check configuration structure (устойчивая проверка)
    assert type(config).__name__ == "MCPProxyConfig"
    assert hasattr(config, "tools") and isinstance(config.tools, list)
    assert hasattr(config, "routes") and isinstance(config.routes, list)
    assert hasattr(config, "version") and config.version == "1.0"
    # Check presence of tools
    assert len(config.tools) > 0
    # Check presence of routes
    assert len(config.routes) > 0
    # Check tools and routes correspondence
    tool_names = [tool.name for tool in config.tools]
    route_tools = [route["tool_name"] for route in config.routes]
    assert all(name in tool_names for name in route_tools)

def test_save_config_to_file(adapter, tmp_path):
    """Test saving configuration to file."""
    # Create temporary file for test
    config_file = tmp_path / "config.json"
    
    # Save configuration to file
    adapter.save_config_to_file(str(config_file))
    
    # Check that file was created
    assert config_file.exists()
    
    # Load configuration from file and check
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    assert "version" in config
    assert "tools" in config
    assert len(config["tools"]) == 4  # Corrected: now we have 4 commands
    assert "routes" in config
    assert len(config["routes"]) == 4  # Corrected: now we have 4 routes, corresponding to commands

def test_parameter_type_validation(test_app):
    """Test parameter type validation."""
    # Test with incorrect parameter type
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "param",
        "params": {
            "required_param": 123,  # Should be string, but passing number
            "optional_param": 1
        },
        "id": 1
    })
    
    assert response.status_code == 200  # JSON-RPC always returns 200
    data = response.json()
    assert "error" in data
    assert "Invalid parameter types" in data["error"]["message"]

def test_type_error_handling(test_app):
    """Test type error handling when executing a command."""
    # Create request with incorrect types for checking TypeError handling
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "success",
        "params": {"value": "not a number"},  # success_command expects int
        "id": 1
    })
    
    assert response.status_code == 200  # JSON-RPC always returns 200
    data = response.json()
    assert "error" in data
    assert "Invalid parameter types" in data["error"]["message"]

def test_unexpected_error_handling(test_app):
    """Test handling of unexpected error when executing a request."""
    # Here we pass invalid JSON, which will cause an error when parsing
    response = test_app.post("/cmd", content="invalid json")
    
    assert response.status_code == 200  # Now we return 200 with error information
    data = response.json()
    assert "error" in data
    assert "Invalid JSON format" in data["error"]["message"]

def test_from_registry_classmethod(registry):
    """Test creating adapter through from_registry class method."""
    # Create adapter with custom parameters through from_registry
    adapter = MCPProxyAdapter.from_registry(
        registry, 
        cmd_endpoint="/custom",
        tool_name_prefix="test_"
    )
    
    # Check that parameters were passed correctly
    assert adapter.cmd_endpoint == "/custom"
    assert adapter.tool_name_prefix == "test_"
    assert adapter.registry == registry

def test_configure_logger():
    """Test configure_logger function."""
    # Create parent logger
    parent_logger = logging.getLogger("parent")
    
    # Configure child logger
    child_logger = configure_logger(parent_logger)
    
    # Check that logger was configured as child
    assert child_logger.name == "parent.mcp_proxy_adapter"
    
    # Check configuration without parent logger
    default_logger = configure_logger()
    assert default_logger.name == "mcp_proxy_adapter"

def test_params_only_format(test_app):
    """Test request format with only params."""
    # Test request with only params field
    response = test_app.post("/cmd", json={
        "params": {"query": "success", "value": 5}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"] == {"result": 10}
    
    # Test request with command in params
    response = test_app.post("/cmd", json={
        "params": {"command": "success", "value": 7}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert data["result"] == {"result": 14}
    
    # Test request without explicitly specifying command
    response = test_app.post("/cmd", json={
        "params": {"unknown_param": "value"}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "available_commands" in data["result"]
    assert "received_params" in data["result"] 
"""
Tests for MCPProxyAdapter - Extended parameter validation and error handling.
"""
import json
import logging
import sys
import os
import pytest
import tempfile
from unittest.mock import MagicMock, patch

# Add path to source files
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI, APIRouter
from fastapi.testclient import TestClient

# Import directly from src
from mcp_proxy_adapter.adapter import MCPProxyAdapter, configure_logger, SchemaOptimizer
from mcp_proxy_adapter.models import JsonRpcRequest, JsonRpcResponse, MCPProxyConfig, MCPProxyTool

# Import common test components
from tests.test_mcp_proxy_adapter import (
    MockDispatcher, 
    MockRegistry, 
    MockOpenApiGenerator,
    success_command, 
    error_command, 
    param_command,
    complex_param_command,
    type_error_command
)

# Переопределяем MockDispatcher для этого файла, чтобы добавить complex_param и type_error
class PatchedMockDispatcher(MockDispatcher):
    def __init__(self):
        super().__init__()
        self.commands["complex_param"] = complex_param_command
        self.commands["type_error"] = type_error_command
        self.commands_info["complex_param"] = {
            "description": "Command with complex parameters",
            "params": {
                "array_param": {
                    "type": "array",
                    "description": "Array of values",
                    "required": True
                },
                "object_param": {
                    "type": "object",
                    "description": "Object",
                    "required": True
                },
                "bool_param": {
                    "type": "boolean",
                    "description": "Boolean value",
                    "required": False,
                    "default": True
                }
            }
        }
        self.commands_info["type_error"] = {
            "description": "Command that will raise TypeError",
            "params": {
                "param": {
                    "type": "integer",
                    "description": "Integer parameter",
                    "required": True
                }
            }
        }

class PatchedMockRegistry(MockRegistry):
    def __init__(self):
        super().__init__()
        self.dispatcher = PatchedMockDispatcher()

@pytest.fixture
def registry():
    return PatchedMockRegistry()

@pytest.fixture
def adapter(registry):
    """Returns a configured adapter for tests."""
    return MCPProxyAdapter(registry)

@pytest.fixture
def test_app(adapter):
    """Creates a FastAPI test application with a configured adapter."""
    app = FastAPI()
    adapter.register_endpoints(app)
    return TestClient(app)

@pytest.fixture
def custom_endpoint_adapter(registry):
    """Returns an adapter with a custom endpoint."""
    return MCPProxyAdapter(registry, cmd_endpoint="/api/execute")

@pytest.fixture
def custom_endpoint_app(custom_endpoint_adapter):
    """Creates a test application with an adapter having a custom endpoint."""
    app = FastAPI()
    custom_endpoint_adapter.register_endpoints(app)
    return TestClient(app)

@pytest.fixture
def no_schema_adapter(registry):
    """Returns an adapter without including OpenAPI schema."""
    return MCPProxyAdapter(registry, include_schema=False)

@pytest.fixture
def adapter_with_openapi(registry):
    """Returns an adapter with OpenAPI support for tests."""
    with patch('mcp_proxy_adapter.adapter.OpenApiGenerator', MockOpenApiGenerator):
        return MCPProxyAdapter(registry)

@pytest.fixture
def custom_prefix_adapter(registry):
    """Returns an adapter with a custom tool prefix."""
    return MCPProxyAdapter(registry, tool_name_prefix="custom_")

@pytest.fixture
def custom_logger():
    """Creates a custom logger for tests."""
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    
    # Clear handlers if they were added in previous tests
    if logger.handlers:
        logger.handlers = []
    
    # Add handler that will write messages to list
    log_records = []
    
    class ListHandler(logging.Handler):
        def emit(self, record):
            log_records.append(self.format(record))
    
    handler = ListHandler()
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger, log_records

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
    assert "Тестовая ошибка" in data["error"]["message"] or "Test error" in data["error"]["message"]

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
    # Проверяем, что стандартный эндпоинт доступен
    response = custom_endpoint_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "success",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == {"result": 10}
    
    # Проверяем, что кастомный эндпоинт работает
    response = custom_endpoint_app.post("/api/execute", json={
        "jsonrpc": "2.0",
        "method": "success",
        "params": {"value": 5},
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == {"result": 10}

# Test parameter type validation
def test_string_parameter_validation(test_app):
    """Test string parameter validation."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "param",
        "params": {
            "required_param": 123,  # Must be a string
            "optional_param": 0
        },
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "required_param" in data["error"]["message"]
    assert "must be a string" in data["error"]["message"]

def test_integer_parameter_validation(test_app):
    """Test integer parameter validation."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "param",
        "params": {
            "required_param": "test",
            "optional_param": "not_integer"  # Must be an integer
        },
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "optional_param" in data["error"]["message"]
    assert "must be an integer" in data["error"]["message"]

def test_array_parameter_validation(test_app):
    """Test array parameter validation."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "complex_param",
        "params": {
            "array_param": "not_array",  # Must be an array
            "object_param": {}
        },
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "array_param" in data["error"]["message"]
    assert "must be an array" in data["error"]["message"]

def test_object_parameter_validation(test_app):
    """Test object parameter validation."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "complex_param",
        "params": {
            "array_param": [1, 2, 3],
            "object_param": "not_object"  # Must be an object
        },
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "object_param" in data["error"]["message"]
    assert "must be an object" in data["error"]["message"]

def test_boolean_parameter_validation(test_app):
    """Test boolean parameter validation."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "complex_param",
        "params": {
            "array_param": [1, 2, 3],
            "object_param": {"key": "value"},
            "bool_param": "not_boolean"  # Must be a boolean value
        },
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "bool_param" in data["error"]["message"]
    assert "must be a boolean" in data["error"]["message"]

# Test error handling
def test_type_error_command(test_app):
    """Test TypeError handling when executing a command."""
    response = test_app.post("/cmd", json={
        "jsonrpc": "2.0",
        "method": "type_error",
        "params": {
            "param": "not_int"  # Will cause TypeError inside function
        },
        "id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] in [400, -32602, 404]  # Acceptable codes
    assert "param" in data["error"]["message"]
    assert "must be an integer" in data["error"]["message"]

def test_unexpected_error_handling(test_app):
    """Test handling of unexpected error."""
    with patch.object(MockDispatcher, 'execute', side_effect=Exception("Unexpected error")):
        response = test_app.post("/cmd", json={
            "jsonrpc": "2.0",
            "method": "success",
            "params": {"value": 5},
            "id": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] in [500, -32603]
        assert "Unexpected error" in data["error"]["message"]

# Test configuration and schema generation
def test_no_schema_endpoint(no_schema_adapter):
    """Test absence of schema endpoint if include_schema=False."""
    # Check that adapter is configured correctly
    assert not no_schema_adapter.include_schema
    
    # Check that there is no OpenAPI schema endpoint in routes
    routes = [route.path for route in no_schema_adapter.router.routes]
    assert "/openapi.json" not in routes

def test_schema_endpoint(test_app):
    """Test presence of schema endpoint if include_schema=True."""
    response = test_app.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data

def test_openapi_generator_integration(adapter_with_openapi):
    """Test OpenApiGenerator integration."""
    schema = adapter_with_openapi._generate_basic_schema()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

def test_schema_without_openapi_generator(adapter):
    """Test schema generation without OpenApiGenerator."""
    schema = adapter._generate_basic_schema()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema

def test_config_generation(adapter):
    """Test configuration generation for MCPProxy."""
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

def test_config_with_custom_prefix(custom_prefix_adapter):
    """Test configuration generation with custom prefix."""
    config = custom_prefix_adapter.generate_mcp_proxy_config()
    tool_names = [tool.name for tool in config.tools]
    for name in tool_names:
        assert name.startswith("custom_")
    
def test_save_config_to_file():
    """Test saving configuration to file."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter(registry)
    
    with tempfile.NamedTemporaryFile(suffix='.json') as temp_file:
        adapter.save_config_to_file(temp_file.name)
        
        # Check that file is not empty
        assert os.path.getsize(temp_file.name) > 0
        
        # Load and check content
        with open(temp_file.name, 'r') as f:
            config_data = json.load(f)
            assert "routes" in config_data
            assert "tools" in config_data

def test_from_registry_classmethod():
    """Test creating adapter through from_registry class method."""
    registry = MockRegistry()
    adapter = MCPProxyAdapter.from_registry(registry, cmd_endpoint="/custom", tool_name_prefix="test_")
    
    assert adapter.cmd_endpoint == "/custom"
    assert adapter.tool_name_prefix == "test_"

def test_logger_configuration():
    """Test logger configuration."""
    # Test with creating new logger
    logger1 = configure_logger()
    assert logger1.name == "mcp_proxy_adapter"
    
    # Test with parent logger
    parent_logger = logging.getLogger("parent")
    logger2 = configure_logger(parent_logger)
    assert logger2.name == "parent.mcp_proxy_adapter"

def test_custom_logger_integration(custom_logger):
    """Test integration with custom logger."""
    logger, log_records = custom_logger
    
    # Configure adapter with custom logger
    with patch('mcp_proxy_adapter.adapter.logger', logger):
        registry = MockRegistry()
        adapter = MCPProxyAdapter(registry)
        
        # Create test application
        app = FastAPI()
        adapter.register_endpoints(app)
        client = TestClient(app)
        
        # Call unknown command to trigger logging
        client.post("/cmd", json={
            "jsonrpc": "2.0",
            "method": "unknown_command",
            "id": 1
        })
        
        # Check that message was logged
        assert any("unknown_command" in record for record in log_records)

# Test edge cases
def test_command_with_empty_info(test_app):
    """Test command with empty parameter information."""
    # Patch get_command_info to return empty dictionary
    with patch.object(MockDispatcher, 'get_command_info', return_value={}):
        response = test_app.post("/cmd", json={
            "jsonrpc": "2.0",
            "method": "success",
            "params": {"value": 5},
            "id": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert "result" in data

def test_command_with_none_info(test_app):
    """Test command with missing information."""
    # Patch get_command_info to return None
    with patch.object(MockDispatcher, 'get_command_info', return_value=None):
        response = test_app.post("/cmd", json={
            "jsonrpc": "2.0",
            "method": "success",
            "params": {"value": 5},
            "id": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert "result" in data

def test_command_info_without_params(test_app):
    """Test command with information, not containing parameters."""
    # Patch get_command_info to return dictionary without params
    with patch.object(MockDispatcher, 'get_command_info', return_value={"description": "Test"}):
        response = test_app.post("/cmd", json={
            "jsonrpc": "2.0",
            "method": "success",
            "params": {"value": 5},
            "id": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert "result" in data

def test_command_params_without_type(test_app):
    """Test command parameters without type indication."""
    # Create command information with parameter without type
    command_info = {
        "description": "Test",
        "params": {
            "value": {
                "description": "Value without type",
                "required": True
            }
        }
    }
    
    # Patch get_command_info
    with patch.object(MockDispatcher, 'get_command_info', return_value=command_info):
        response = test_app.post("/cmd", json={
            "jsonrpc": "2.0",
            "method": "success",
            "params": {"value": "test"},
            "id": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert "result" in data

def test_api_commands_endpoint(test_app):
    """Test endpoint for getting information about all commands."""
    response = test_app.get("/api/commands")
    assert response.status_code == 200
    # In real adapter commands may be in different structure, 
    # let's check more general case - presence of answer in JSON format
    data = response.json()
    assert isinstance(data, dict)
    # Check that returned data about commands (without specific structure)
    assert len(data) > 0
    assert "success" in str(data)  # Command name must be present somewhere in answer

if __name__ == "__main__":
    pytest.main(["-v", __file__])

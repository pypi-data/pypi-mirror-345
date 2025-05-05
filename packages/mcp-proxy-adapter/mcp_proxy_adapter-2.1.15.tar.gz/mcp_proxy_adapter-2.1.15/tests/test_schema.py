"""
Tests for SchemaOptimizer, checking OpenAPI schema optimization for MCP Proxy.
"""
import json
import sys
import os
import pytest
from typing import Dict, Any

# Add path to source files
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(project_root, 'src'))

from mcp_proxy_adapter.schema import SchemaOptimizer

# Test fixtures
@pytest.fixture
def base_schema() -> Dict[str, Any]:
    """Returns base OpenAPI schema for tests."""
    return {
        "openapi": "3.0.2",
        "info": {
            "title": "Test API",
            "description": "Test API for SchemaOptimizer",
            "version": "1.0.0"
        },
        "paths": {
            "/test": {
                "get": {
                    "summary": "Test endpoint",
                    "description": "Test endpoint for SchemaOptimizer",
                    "responses": {
                        "200": {
                            "description": "Successful response"
                        }
                    }
                }
            }
        }
    }

@pytest.fixture
def commands_info() -> Dict[str, Dict[str, Any]]:
    """Returns command information for tests."""
    return {
        "test_command": {
            "description": "Test command",
            "params": {
                "param1": {
                    "type": "string",
                    "description": "String parameter",
                    "required": True
                },
                "param2": {
                    "type": "integer",
                    "description": "Numeric parameter",
                    "required": False,
                    "default": 42
                },
                "param3": {
                    "type": "boolean",
                    "description": "Boolean parameter",
                    "required": False,
                    "default": False
                }
            }
        },
        "no_params_command": {
            "description": "Command without parameters",
            "params": {}
        },
        "enum_params_command": {
            "description": "Command with enumerations",
            "params": {
                "enum_param": {
                    "type": "string",
                    "description": "Enumeration parameter",
                    "required": True,
                    "enum": ["value1", "value2", "value3"]
                }
            }
        },
        "example_command": {
            "description": "Command with example",
            "params": {
                "example_param": {
                    "type": "string",
                    "description": "Parameter with example",
                    "required": True,
                    "example": "example_value"
                }
            }
        }
    }

# Tests for SchemaOptimizer
def test_optimize_basic(base_schema, commands_info):
    """Test basic schema optimization."""
    optimizer = SchemaOptimizer()
    cmd_endpoint = "/cmd"
    
    optimized = optimizer.optimize(base_schema, cmd_endpoint, commands_info)
    
    # Check basic structure
    assert "openapi" in optimized
    assert "info" in optimized
    assert "paths" in optimized
    assert cmd_endpoint in optimized["paths"]
    assert "post" in optimized["paths"][cmd_endpoint]
    
    # Check presence of components
    assert "components" in optimized
    assert "schemas" in optimized["components"]
    assert "CommandRequest" in optimized["components"]["schemas"]
    assert "CommandResponse" in optimized["components"]["schemas"]
    
    # Check presence of parameter schemas for each command
    for cmd_name in commands_info.keys():
        param_schema_name = f"{cmd_name.capitalize()}Params"
        assert param_schema_name in optimized["components"]["schemas"]

def test_optimize_with_examples(base_schema, commands_info):
    """Test optimization with examples."""
    optimizer = SchemaOptimizer()
    cmd_endpoint = "/cmd"
    
    optimized = optimizer.optimize(base_schema, cmd_endpoint, commands_info)
    
    # Check presence of examples
    assert "examples" in optimized["components"]
    
    for cmd_name in commands_info.keys():
        example_id = f"{cmd_name}_example"
        assert example_id in optimized["components"]["examples"]
        
        # Check example correctness
        example = optimized["components"]["examples"][example_id]
        assert "value" in example
        assert "command" in example["value"]
        assert example["value"]["command"] == cmd_name
        
        # For commands with parameters check that params is present
        if commands_info[cmd_name]["params"]:
            assert "params" in example["value"]
        # For commands without parameters check that params is absent
        else:
            assert "params" not in example["value"]

def test_optimize_command_request_schema(base_schema, commands_info):
    """Test CommandRequest schema."""
    optimizer = SchemaOptimizer()
    cmd_endpoint = "/cmd"
    
    optimized = optimizer.optimize(base_schema, cmd_endpoint, commands_info)
    
    command_request = optimized["components"]["schemas"]["CommandRequest"]
    
    # Check basic structure
    assert "properties" in command_request
    assert "command" in command_request["properties"]
    assert "params" in command_request["properties"]
    
    # Check enum in command
    assert "enum" in command_request["properties"]["command"]
    for cmd_name in commands_info.keys():
        assert cmd_name in command_request["properties"]["command"]["enum"]
    
    # Check oneOf in params
    assert "oneOf" in command_request["properties"]["params"]
    
    # Last element in oneOf should be null for commands without parameters
    last_oneof = command_request["properties"]["params"]["oneOf"][-1]
    assert ("type" in last_oneof and last_oneof["type"] == "null") or last_oneof.get("nullable") is True or "$ref" in last_oneof
    
    # Check references to parameter schemas
    param_refs = [ref["$ref"].split("/")[-1] for ref in command_request["properties"]["params"]["oneOf"][:-1] if "$ref" in ref]
    for cmd_name in commands_info.keys():
        param_schema_name = f"{cmd_name.capitalize()}Params"
        if commands_info[cmd_name]["params"]:  # Проверяем только если есть параметры
            assert param_schema_name in param_refs

def test_optimize_parameter_schemas(base_schema, commands_info):
    """Test parameter schemas."""
    optimizer = SchemaOptimizer()
    cmd_endpoint = "/cmd"
    
    optimized = optimizer.optimize(base_schema, cmd_endpoint, commands_info)
    
    # Check parameter schemas for each command
    for cmd_name, cmd_info in commands_info.items():
        param_schema_name = f"{cmd_name.capitalize()}Params"
        param_schema = optimized["components"]["schemas"][param_schema_name]
        
        assert "properties" in param_schema
        
        # Check parameters
        for param_name, param_info in cmd_info.get("params", {}).items():
            assert param_name in param_schema["properties"]
            assert "type" in param_schema["properties"][param_name]
            assert param_schema["properties"][param_name]["type"] == param_info["type"]
            
            # Check description
            assert "description" in param_schema["properties"][param_name]
            assert param_schema["properties"][param_name]["description"] == param_info["description"]
            
            # Check default if present
            if "default" in param_info:
                assert "default" in param_schema["properties"][param_name]
                assert param_schema["properties"][param_name]["default"] == param_info["default"]
            
            # Check enum if present
            if "enum" in param_info:
                assert "enum" in param_schema["properties"][param_name]
                assert param_schema["properties"][param_name]["enum"] == param_info["enum"]
        
        # Check required if there are required parameters
        required_params = [
            param_name for param_name, param_info in cmd_info.get("params", {}).items()
            if param_info.get("required", False)
        ]
        
        if required_params:
            assert "required" in param_schema
            assert set(param_schema["required"]) == set(required_params)

def test_add_tool_descriptions(base_schema, commands_info):
    """Test adding tool descriptions."""
    optimizer = SchemaOptimizer()
    cmd_endpoint = "/cmd"
    
    optimized = optimizer.optimize(base_schema, cmd_endpoint, commands_info)
    
    # Check presence of x-mcp-tools
    assert "x-mcp-tools" in optimized
    assert isinstance(optimized["x-mcp-tools"], list)
    
    # Check tool descriptions
    for cmd_name, cmd_info in commands_info.items():
        # Find corresponding tool
        tool = next((t for t in optimized["x-mcp-tools"] if t["name"] == f"mcp_{cmd_name}"), None)
        
        assert tool is not None
        assert "description" in tool
        assert "parameters" in tool
        assert "type" in tool["parameters"]
        assert tool["parameters"]["type"] == "object"
        assert "properties" in tool["parameters"]
        
        # Check parameters
        for param_name, param_info in cmd_info.get("params", {}).items():
            assert param_name in tool["parameters"]["properties"]
            
            # Check type and description
            assert "type" in tool["parameters"]["properties"][param_name]
            assert tool["parameters"]["properties"][param_name]["type"] == param_info["type"]
            assert "description" in tool["parameters"]["properties"][param_name]
            
            # Check enum if present
            if "enum" in param_info:
                assert "enum" in tool["parameters"]["properties"][param_name]
                assert tool["parameters"]["properties"][param_name]["enum"] == param_info["enum"]
            
            # Check default if present
            if "default" in param_info:
                assert "default" in tool["parameters"]["properties"][param_name]
                assert tool["parameters"]["properties"][param_name]["default"] == param_info["default"]
        
        # Check required
        required_params = [
            param_name for param_name, param_info in cmd_info.get("params", {}).items()
            if param_info.get("required", False)
        ]
        
        if required_params:
            assert "required" in tool["parameters"]
            assert set(tool["parameters"]["required"]) == set(required_params)

def test_optimize_with_empty_schema():
    """Test optimization with empty schema."""
    optimizer = SchemaOptimizer()
    empty_schema = {}
    cmd_endpoint = "/cmd"
    commands_info = {
        "test_command": {
            "description": "Test command",
            "params": {}
        }
    }
    
    optimized = optimizer.optimize(empty_schema, cmd_endpoint, commands_info)
    
    # Ensure that optimizer created a valid schema even from empty
    assert "openapi" in optimized
    assert "info" in optimized
    assert "paths" in optimized
    assert cmd_endpoint in optimized["paths"]
    assert "components" in optimized
    assert "schemas" in optimized["components"]
    assert "CommandRequest" in optimized["components"]["schemas"]
    assert "CommandResponse" in optimized["components"]["schemas"]

def test_optimize_command_with_all_param_types(base_schema):
    """Test optimization of command with all parameter types."""
    optimizer = SchemaOptimizer()
    cmd_endpoint = "/cmd"
    commands_info = {
        "all_types": {
            "description": "Command with all parameter types",
            "params": {
                "string_param": {
                    "type": "string",
                    "description": "String parameter",
                    "required": True
                },
                "integer_param": {
                    "type": "integer",
                    "description": "Integer parameter",
                    "required": False,
                    "default": 0
                },
                "number_param": {
                    "type": "number",
                    "description": "Numeric parameter",
                    "required": False,
                    "default": 0.0
                },
                "boolean_param": {
                    "type": "boolean",
                    "description": "Boolean parameter",
                    "required": False,
                    "default": False
                },
                "array_param": {
                    "type": "array",
                    "description": "Array",
                    "required": False
                },
                "object_param": {
                    "type": "object",
                    "description": "Object",
                    "required": False
                }
            }
        }
    }
    
    optimized = optimizer.optimize(base_schema, cmd_endpoint, commands_info)
    
    # Check parameter schema
    param_schema = optimized["components"]["schemas"]["All_typesParams"]
    
    # Check parameter types
    assert param_schema["properties"]["string_param"]["type"] == "string"
    assert param_schema["properties"]["integer_param"]["type"] == "integer"
    assert param_schema["properties"]["number_param"]["type"] == "number"
    assert param_schema["properties"]["boolean_param"]["type"] == "boolean"
    assert param_schema["properties"]["array_param"]["type"] == "array"
    assert param_schema["properties"]["object_param"]["type"] == "object" 
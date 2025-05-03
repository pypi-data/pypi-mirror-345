"""
RPC schema generator from REST schema.
Creates RPC components for all REST endpoints.
"""
from typing import Dict, Any, List, Optional

def generate_rpc_schema(rest_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates RPC schema based on REST schema.
    
    Args:
        rest_schema: REST OpenAPI schema
        
    Returns:
        Generated RPC OpenAPI schema
    """
    # List of available commands (will be filled from REST endpoints)
    available_commands = []
    
    # Create base RPC schema structure
    rpc_schema = {
        "paths": {
            "/cmd": {
                "post": {
                    "summary": "Universal RPC endpoint for executing commands",
                    "description": "**Main system interaction interface**. The endpoint accepts a structured JSON-RPC 2.0 request with command and parameters, executes the specified operation and returns the result. Only supports working with fixed-dimension vectors of size 384.",
                    "operationId": "executeCommand",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CommandRequest"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Command execution result (regardless of success or error). API always returns code 200 and uses 'success' field to indicate operation success.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/JsonRpcResponse"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {},
            "examples": {}
        }
    }
    
    # Process paths from REST schema and create corresponding commands
    command_schemas = {}
    command_examples = {}
    
    for path, path_info in rest_schema["paths"].items():
        # Skip path if it starts with /cmd (to avoid RPC endpoint duplication)
        if path.startswith("/cmd"):
            continue
            
        # Remove leading slash for command name
        command_name = path[1:] if path.startswith('/') else path
        # Replace remaining slashes with underscores for command name
        command_name = command_name.replace("/", "_")
        
        # Add command to available list
        available_commands.append(command_name)
        
        # Process each HTTP method (GET, POST etc.)
        for method, method_info in path_info.items():
            # Get operation description
            operation_id = method_info.get("operationId", f"{method}_{command_name}")
            summary = method_info.get("summary", f"Operation {command_name}")
            description = method_info.get("description", f"Executes operation {command_name}")
            
            # Create parameter schema for command
            param_schema_name = f"{command_name.title()}Params"
            param_schema = {
                "type": "object",
                "title": param_schema_name,
                "description": f"Parameters for command {command_name}",
                "properties": {},
                "required": []
            }
            
            # Process request parameters
            if "parameters" in method_info:
                for param in method_info["parameters"]:
                    param_name = param["name"]
                    param_schema["properties"][param_name] = {
                        "type": param["schema"].get("type", "string"),
                        "description": param.get("description", f"Parameter {param_name}")
                    }
                    
                    # Add additional properties from parameter schema
                    for prop in ["enum", "default", "format", "minimum", "maximum"]:
                        if prop in param["schema"]:
                            param_schema["properties"][param_name][prop] = param["schema"][prop]
                    
                    # If parameter is required, add it to required list
                    if param.get("required", False):
                        param_schema["required"].append(param_name)
            
            # Process request body parameters
            if "requestBody" in method_info and "content" in method_info["requestBody"]:
                content = method_info["requestBody"]["content"]
                if "application/json" in content and "schema" in content["application/json"]:
                    body_schema = content["application/json"]["schema"]
                    
                    # If request body schema contains reference to another schema
                    if "$ref" in body_schema:
                        ref_name = body_schema["$ref"].split("/")[-1]
                        if ref_name in rest_schema["components"]["schemas"]:
                            ref_schema = rest_schema["components"]["schemas"][ref_name]
                            
                            # Copy properties from request body schema
                            if "properties" in ref_schema:
                                for prop_name, prop_info in ref_schema["properties"].items():
                                    # Process references to other schemas in properties
                                    if "$ref" in prop_info:
                                        ref_prop_name = prop_info["$ref"].split("/")[-1]
                                        if ref_prop_name in rest_schema["components"]["schemas"]:
                                            prop_schema = rest_schema["components"]["schemas"][ref_prop_name]
                                            param_schema["properties"][prop_name] = {
                                                "type": prop_schema.get("type", "object"),
                                                "description": prop_schema.get("description", f"Parameter {prop_name}")
                                            }
                                            # If schema contains oneOf or anyOf, process them
                                            for prop in ["oneOf", "anyOf"]:
                                                if prop in prop_schema:
                                                    param_schema["properties"][prop_name][prop] = prop_schema[prop]
                                    else:
                                        param_schema["properties"][prop_name] = prop_info
                            
                            # Copy required fields list
                            if "required" in ref_schema:
                                param_schema["required"].extend(ref_schema["required"])
            
            # Save parameter schema
            command_schemas[param_schema_name] = param_schema
            
            # Create command usage example
            example = {
                "summary": summary,
                "value": {
                    "jsonrpc": "2.0",
                    "command": command_name,
                    "params": {},
                    "id": command_name
                }
            }
            
            # Fill example with default parameters
            for param_name, param_info in param_schema["properties"].items():
                if "default" in param_info:
                    example["value"]["params"][param_name] = param_info["default"]
                elif "enum" in param_info and param_info["enum"]:
                    example["value"]["params"][param_name] = param_info["enum"][0]
                elif param_info["type"] == "string":
                    example["value"]["params"][param_name] = f"example_{param_name}"
                elif param_info["type"] == "integer" or param_info["type"] == "number":
                    example["value"]["params"][param_name] = 1
                elif param_info["type"] == "boolean":
                    example["value"]["params"][param_name] = True
                elif param_info["type"] == "array":
                    example["value"]["params"][param_name] = []
                elif param_info["type"] == "object":
                    example["value"]["params"][param_name] = {}
            
            # Save example
            command_examples[f"{command_name}_example"] = example
    
    # Special processing for help command
    if "help" in available_commands:
        # Create examples for help command usage
        command_examples["help_all_commands"] = {
            "summary": "Get list of all available commands",
            "value": {
                "jsonrpc": "2.0",
                "command": "help",
                "params": {},
                "id": "help_all"
            }
        }
        
        # Examples for specific commands
        for command in available_commands:
            if command != "help":
                command_examples[f"help_{command}_command"] = {
                    "summary": f"Get help for command {command}",
                    "value": {
                        "jsonrpc": "2.0",
                        "command": "help",
                        "params": {
                            "command": command
                        },
                        "id": f"help_{command}"
                    }
                }
    
    # Create base schema for CommandRequest
    rpc_schema["components"]["schemas"]["CommandRequest"] = {
        "properties": {
            "jsonrpc": {
                "type": "string",
                "description": "JSON-RPC protocol version",
                "enum": ["2.0"],
                "default": "2.0"
            },
            "id": {
                "type": ["string", "number", "null"],
                "description": "Request identifier, used to match requests and responses"
            },
            "command": {
                "type": "string",
                "title": "Command",
                "description": "Command name to execute",
                "enum": available_commands
            },
            "params": {
                "title": "Params",
                "description": "Command parameters",
                "oneOf": [schema for schema in command_schemas.values()] + [{"type": "null"}]
            }
        },
        "type": "object",
        "required": ["command", "jsonrpc"],
        "title": "CommandRequest",
        "description": "Command execution request via JSON-RPC 2.0"
    }
    
    # Create schema for JSON-RPC response
    rpc_schema["components"]["schemas"]["JsonRpcResponse"] = {
        "type": "object",
        "required": ["jsonrpc", "success"],
        "properties": {
            "jsonrpc": {
                "type": "string",
                "description": "JSON-RPC protocol version",
                "enum": ["2.0"],
                "default": "2.0"
            },
            "success": {
                "type": "boolean",
                "description": "Operation success indicator",
                "default": False
            },
            "result": {
                "description": "Operation result. Present only on successful execution (success=True). Result format depends on the executed command."
            },
            "error": {
                "description": "Error information. Present only when error occurs (success=false).",
                "type": "object",
                "required": ["code", "message"],
                "properties": {
                    "code": {
                        "type": "integer",
                        "description": "Error code (internal code, not HTTP status)",
                        "example": 400
                    },
                    "message": {
                        "type": "string",
                        "description": "Error message description",
                        "example": "Record does not exist: ID 12345"
                    }
                }
            },
            "id": {
                "type": ["string", "number", "null"],
                "description": "Request identifier (if specified in request)"
            }
        },
        "example": {
            "jsonrpc": "2.0",
            "success": True,
            "result": {"id": "550e8400-e29b-41d4-a716-446655440000"},
            "id": "request-1"
        }
    }
    
    # Add all parameter schemas
    rpc_schema["components"]["schemas"].update(command_schemas)
    
    # Add all examples
    rpc_schema["components"]["examples"] = command_examples
    
    # Add all necessary components from REST schema
    for component_type, components in rest_schema["components"].items():
        if component_type not in rpc_schema["components"]:
            rpc_schema["components"][component_type] = {}
        
        for component_name, component in components.items():
            # Skip components that already exist in RPC schema
            if component_name in rpc_schema["components"].get(component_type, {}):
                continue
                
            # Add component to RPC schema
            rpc_schema["components"][component_type][component_name] = component
    
    return rpc_schema 
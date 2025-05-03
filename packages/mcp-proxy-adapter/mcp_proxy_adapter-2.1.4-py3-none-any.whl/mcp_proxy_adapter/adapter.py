"""
Main adapter module for MCPProxy.

This module contains the MCPProxyAdapter class, which provides
integration of Command Registry with MCPProxy for working with AI model tools.
"""
import logging
import json
from typing import Dict, Any, List, Optional, Union, Callable, Protocol, Type
from fastapi import FastAPI, APIRouter, Request, Response, HTTPException, Depends
from pydantic import BaseModel, Field

try:
    # Import when package is installed
    from mcp_proxy_adapter.models import (
        JsonRpcRequest, 
        JsonRpcResponse, 
        CommandInfo,
        MCPProxyTool,
        MCPProxyConfig
    )
    from mcp_proxy_adapter.schema import SchemaOptimizer
except ImportError:
    # Import during local development
    try:
        from .models import (
            JsonRpcRequest, 
            JsonRpcResponse, 
            CommandInfo,
            MCPProxyTool,
            MCPProxyConfig
        )
        from .schema import SchemaOptimizer
    except ImportError:
        # Direct import for tests
        from src.models import (
            JsonRpcRequest, 
            JsonRpcResponse, 
            CommandInfo,
            MCPProxyTool,
            MCPProxyConfig
        )
        from src.schema import SchemaOptimizer

# Initialize logger with default settings
logger = logging.getLogger("mcp_proxy_adapter")

def configure_logger(parent_logger=None):
    """
    Configures the adapter logger with the ability to use a parent logger.
    
    Args:
        parent_logger: Parent project logger, if available
        
    Returns:
        logging.Logger: Configured adapter logger
    """
    global logger
    if parent_logger:
        logger = parent_logger.getChild('mcp_proxy_adapter')
    else:
        logger = logging.getLogger("mcp_proxy_adapter")
    return logger

class CommandRegistry(Protocol):
    """Protocol for CommandRegistry."""
    
    @property
    def dispatcher(self) -> Any:
        """Get the command dispatcher."""
        ...
    
    def get_commands_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all registered commands."""
        ...
    
    def add_generator(self, generator: Any) -> None:
        """Add an API generator."""
        ...

class OpenApiGenerator(Protocol):
    """Protocol for OpenAPI schema generator."""
    
    def generate_schema(self) -> Dict[str, Any]:
        """Generate OpenAPI schema."""
        ...
    
    def set_dispatcher(self, dispatcher: Any) -> None:
        """Set the command dispatcher."""
        ...

class MCPProxyAdapter:
    """
    Adapter for integrating Command Registry with MCPProxy.
    
    This adapter creates a hybrid API that supports both REST and JSON-RPC
    requests, and optimizes it for use with MCPProxy.
    """
    
    def __init__(
        self, 
        registry: CommandRegistry,
        cmd_endpoint: str = "/cmd",  # Added ability to specify cmd_endpoint
        include_schema: bool = True,
        optimize_schema: bool = True,
        tool_name_prefix: str = "mcp_"
    ):
        """
        Initializes the adapter for MCPProxy.
        
        Args:
            registry: CommandRegistry instance
            cmd_endpoint: Path for universal JSON-RPC endpoint
            include_schema: Whether to include endpoint for getting OpenAPI schema
            optimize_schema: Whether to optimize schema for AI models
            tool_name_prefix: Prefix for tool names
        """
        self.registry = registry
        self.cmd_endpoint = cmd_endpoint  # Use the provided parameter
        self.include_schema = include_schema
        self.optimize_schema = optimize_schema
        self.tool_name_prefix = tool_name_prefix
        self.router = APIRouter()
        
        # Schema optimizer
        self.schema_optimizer = SchemaOptimizer()
        
        # Route configuration
        self._generate_router()
        
        # OpenAPI generator setup, if provided
        try:
            # Import here to avoid requiring the dependency if not used
            from command_registry.generators.openapi_generator import OpenApiGenerator
            self.openapi_generator = OpenApiGenerator(
                title="Command Registry API",
                description="API for executing commands through MCPProxy",
                version="1.0.0"
            )
            self.registry.add_generator(self.openapi_generator)
        except ImportError:
            logger.info("OpenApiGenerator not found, schema generation will be limited")
            self.openapi_generator = None
    
    def _validate_param_types(self, command: str, params: Dict[str, Any]) -> List[str]:
        """
        Validates parameter types and returns validation errors.
        
        Args:
            command: Command name
            params: Command parameters
            
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        command_info = self.registry.dispatcher.get_command_info(command)
        
        if not command_info or "params" not in command_info:
            return errors
        
        for param_name, param_info in command_info["params"].items():
            if param_name not in params:
                continue
                
            param_value = params[param_name]
            param_type = param_info.get("type", "string")
            
            # Check basic types
            if param_type == "string" and not isinstance(param_value, str):
                errors.append(f"Parameter '{param_name}' must be a string")
            elif param_type == "integer" and not isinstance(param_value, int):
                errors.append(f"Parameter '{param_name}' must be an integer")
            elif param_type == "number" and not isinstance(param_value, (int, float)):
                errors.append(f"Parameter '{param_name}' must be a number")
            elif param_type == "boolean" and not isinstance(param_value, bool):
                errors.append(f"Parameter '{param_name}' must be a boolean")
            elif param_type == "array" and not isinstance(param_value, list):
                errors.append(f"Parameter '{param_name}' must be an array")
            elif param_type == "object" and not isinstance(param_value, dict):
                errors.append(f"Parameter '{param_name}' must be an object")
        
        return errors

    def _generate_router(self) -> None:
        """Generates FastAPI routes for the adapter."""
        # Universal endpoint for executing commands via JSON-RPC
        @self.router.post(self.cmd_endpoint, response_model=JsonRpcResponse)
        async def execute_command(request: JsonRpcRequest):
            """Executes a command via JSON-RPC protocol."""
            try:
                # Check if command exists
                if request.method not in self.registry.dispatcher.get_valid_commands():
                    logger.warning(f"Attempt to call non-existent command: {request.method}")
                    return JsonRpcResponse(
                        jsonrpc="2.0",
                        error={
                            "code": -32601,
                            "message": f"Command '{request.method}' not found"
                        },
                        id=request.id
                    )
                
                # Check for required parameters
                command_info = self.registry.dispatcher.get_command_info(request.method)
                if command_info and "params" in command_info:
                    missing_params = []
                    for param_name, param_info in command_info["params"].items():
                        if param_info.get("required", False) and param_name not in request.params:
                            missing_params.append(param_name)
                    
                    if missing_params:
                        logger.warning(f"Missing required parameters for command {request.method}: {missing_params}")
                        return JsonRpcResponse(
                            jsonrpc="2.0",
                            error={
                                "code": -32602,
                                "message": f"Missing required parameters: {', '.join(missing_params)}"
                            },
                            id=request.id
                        )
                
                # Check parameter types
                type_errors = self._validate_param_types(request.method, request.params)
                if type_errors:
                    logger.warning(f"Parameter type errors for command {request.method}: {type_errors}")
                    return JsonRpcResponse(
                        jsonrpc="2.0",
                        error={
                            "code": -32602,
                            "message": f"Invalid parameter types: {', '.join(type_errors)}"
                        },
                        id=request.id
                    )
                
                # Execute the command
                logger.debug(f"Executing command {request.method} with parameters {request.params}")
                try:
                    result = self.registry.dispatcher.execute(
                        request.method, 
                        **request.params
                    )
                    
                    # Return the result
                    return JsonRpcResponse(
                        jsonrpc="2.0",
                        result=result,
                        id=request.id
                    )
                except TypeError as e:
                    # Type error in arguments or unknown argument
                    logger.error(f"Error in command arguments {request.method}: {str(e)}")
                    return JsonRpcResponse(
                        jsonrpc="2.0",
                        error={
                            "code": -32602,
                            "message": f"Invalid parameters: {str(e)}"
                        },
                        id=request.id
                    )
                except Exception as e:
                    # Other errors during command execution
                    logger.exception(f"Error executing command {request.method}: {str(e)}")
                    return JsonRpcResponse(
                        jsonrpc="2.0",
                        error={
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        },
                        id=request.id
                    )
            except Exception as e:
                # Handle unexpected errors
                logger.exception(f"Unexpected error processing request: {str(e)}")
                return JsonRpcResponse(
                    jsonrpc="2.0",
                    error={
                        "code": -32603,
                        "message": f"Internal server error: {str(e)}"
                    },
                    id=request.id if hasattr(request, 'id') else None
                )
        
        # Add endpoint for getting OpenAPI schema
        if self.include_schema:
            @self.router.get("/openapi.json")
            async def get_openapi_schema():
                """Returns optimized OpenAPI schema."""
                if self.openapi_generator:
                    schema = self.openapi_generator.generate_schema()
                else:
                    schema = self._generate_basic_schema()
                
                # Optimize schema for MCP Proxy
                if self.optimize_schema:
                    schema = self.schema_optimizer.optimize(
                        schema, 
                        self.cmd_endpoint,
                        self.registry.get_commands_info()
                    )
                
                return schema
    
    def _generate_basic_schema(self) -> Dict[str, Any]:
        """
        Generates a basic OpenAPI schema when OpenApiGenerator is not found.
        
        Returns:
            Dict[str, Any]: Basic OpenAPI schema
        """
        schema = {
            "openapi": "3.0.2",
            "info": {
                "title": "Command Registry API",
                "description": "API for executing commands through MCPProxy",
                "version": "1.0.0"
            },
            "paths": {
                self.cmd_endpoint: {
                    "post": {
                        "summary": "Execute command via JSON-RPC",
                        "description": "Universal endpoint for executing commands",
                        "operationId": "execute_command",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/JsonRpcRequest"
                                    }
                                }
                            },
                            "required": True
                        },
                        "responses": {
                            "200": {
                                "description": "Command executed successfully",
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
                "schemas": {
                    "JsonRpcRequest": {
                        "type": "object",
                        "properties": {
                            "jsonrpc": {
                                "type": "string",
                                "description": "JSON-RPC version",
                                "default": "2.0"
                            },
                            "method": {
                                "type": "string",
                                "description": "Method name for execution"
                            },
                            "params": {
                                "type": "object",
                                "description": "Method parameters",
                                "additionalProperties": True
                            },
                            "id": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "integer"},
                                    {"type": "null"}
                                ],
                                "description": "Request identifier"
                            }
                        },
                        "required": ["jsonrpc", "method"]
                    },
                    "JsonRpcResponse": {
                        "type": "object",
                        "properties": {
                            "jsonrpc": {
                                "type": "string",
                                "description": "JSON-RPC version",
                                "default": "2.0"
                            },
                            "result": {
                                "description": "Command execution result",
                                "nullable": True
                            },
                            "error": {
                                "type": "object",
                                "description": "Command execution error information",
                                "nullable": True,
                                "properties": {
                                    "code": {
                                        "type": "integer",
                                        "description": "Error code"
                                    },
                                    "message": {
                                        "type": "string",
                                        "description": "Error message"
                                    },
                                    "data": {
                                        "description": "Additional error data",
                                        "nullable": True
                                    }
                                }
                            },
                            "id": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "integer"},
                                    {"type": "null"}
                                ],
                                "description": "Request identifier"
                            }
                        },
                        "required": ["jsonrpc"]
                    }
                }
            }
        }
        
        return schema
    
    def _register_mcp_cmd_endpoint(self, app: FastAPI) -> None:
        """
        Registers /cmd endpoint compatible with MCP Proxy format.
        
        Args:
            app: FastAPI application instance
        """
        @app.post("/cmd")
        async def mcp_cmd_endpoint(request: Request):
            """Executes a command in MCP Proxy format or JSON-RPC."""
            try:
                # Get data from request
                request_data = await request.json()
                
                # Detailed logging of the entire request
                logger.info(f"RECEIVED REQUEST TO /cmd: {json.dumps(request_data)}")
                
                # Check request format
                if "command" in request_data:
                    # MCP Proxy format: {"command": "...", "params": {...}}
                    command = request_data["command"]
                    params = request_data.get("params", {})
                    
                    logger.debug(f"Received request to /cmd in MCP Proxy format: command={command}, params={params}")
                elif "method" in request_data:
                    # JSON-RPC format: {"jsonrpc": "2.0", "method": "...", "params": {...}, "id": ...}
                    command = request_data["method"]
                    params = request_data.get("params", {})
                    
                    logger.debug(f"Received request to /cmd in JSON-RPC format: method={command}, params={params}")
                elif "params" in request_data:
                    # Implied command format: {"params": {...}}
                    params = request_data["params"]
                    
                    # Check if params contains command, use it as command name
                    if "command" in params:
                        command = params.pop("command")  # Use command from params and remove it from params
                        logger.info(f"Extracting command from params.command field: {command}")
                    # Check if params contains field that can be used as command name
                    elif "query" in params:
                        # Use query as command name or subcommand
                        query_value = params["query"]
                        logger.info(f"Extracting command from query field: {query_value}")
                        
                        # If query contains "/", split into parts
                        if isinstance(query_value, str) and "/" in query_value:
                            command_parts = query_value.split("/")
                            command = command_parts[0]  # First part - command name
                            
                            # Add remaining part back to params as subcommand
                            params["subcommand"] = "/".join(command_parts[1:])
                        else:
                            command = "execute"  # Use fixed command
                            # Leave query in params as is
                    else:
                        # Use default command
                        command = "execute"
                    
                    logger.info(f"Processing request with implied command: using command={command}, params={params}")
                else:
                    # Unknown format - return error in response body
                    logger.warning(f"Received request with incorrect format: {json.dumps(request_data)}")
                    return {
                        "error": {
                            "code": 422,
                            "message": "Missing required fields",
                            "details": "Request requires 'command', 'method' or 'params' field"
                        }
                    }
                
                # Check if command exists
                if command not in self.registry.dispatcher.get_valid_commands():
                    logger.warning(f"Attempt to call non-existent command: {command}")
                    return {
                        "error": {
                            "code": 404,
                            "message": f"Unknown command: {command}",
                            "details": f"Command '{command}' not found in registry. Available commands: {', '.join(self.registry.dispatcher.get_valid_commands())}"
                        }
                    }
                
                # Check for required parameters
                command_info = self.registry.dispatcher.get_command_info(command)
                if command_info and "params" in command_info:
                    missing_params = []
                    for param_name, param_info in command_info["params"].items():
                        if param_info.get("required", False) and param_name not in params:
                            missing_params.append(param_name)
                    
                    if missing_params:
                        logger.warning(f"Missing required parameters for command {command}: {missing_params}")
                        return {
                            "error": {
                                "code": 400,
                                "message": f"Missing required parameters: {', '.join(missing_params)}",
                                "details": f"Command '{command}' requires following parameters: {', '.join(missing_params)}"
                            }
                        }
                
                # Check parameter types
                type_errors = self._validate_param_types(command, params)
                if type_errors:
                    logger.warning(f"Parameter type errors for command {command}: {type_errors}")
                    return {
                        "error": {
                            "code": 400,
                            "message": f"Invalid parameter types: {', '.join(type_errors)}",
                            "details": "Check parameter types and try again"
                        }
                    }
                
                # Execute the command
                try:
                    result = self.registry.dispatcher.execute(command, **params)
                    
                    # Return result in MCP Proxy format
                    return {"result": result}
                    
                except Exception as e:
                    logger.error(f"Error executing command {command}: {str(e)}")
                    return {
                        "error": {
                            "code": 500,
                            "message": str(e),
                            "details": f"Error executing command '{command}': {str(e)}"
                        }
                    }
            
            except json.JSONDecodeError:
                # JSON parsing error
                logger.error("JSON parsing error from request")
                return {
                    "error": {
                        "code": 400,
                        "message": "Invalid JSON format",
                        "details": "Request contains incorrect JSON. Check request syntax."
                    }
                }
            except Exception as e:
                logger.error(f"Error processing request to /cmd: {str(e)}")
                return {
                    "error": {
                        "code": 500,
                        "message": "Internal server error",
                        "details": str(e)
                    }
                }

    def register_endpoints(self, app: FastAPI) -> None:
        """
        Registers adapter endpoints in FastAPI application.
        
        Args:
            app: FastAPI application instance
        """
        # IMPORTANT: first register /cmd endpoint for MCP Proxy compatibility
        self._register_mcp_cmd_endpoint(app)
        
        # Then integrate main JSON-RPC router into application
        app.include_router(self.router)
        
        # Add endpoint for getting list of commands
        @app.get("/api/commands")
        def get_commands():
            """Returns list of available commands with their descriptions."""
            commands_info = self.registry.get_commands_info()
            return {
                "commands": commands_info
            }
    
    def generate_mcp_proxy_config(self) -> MCPProxyConfig:
        """
        Generates MCP Proxy configuration based on registered commands.
        
        Returns:
            MCPProxyConfig: MCP Proxy configuration
        """
        tools = []
        routes = []
        
        # Get command information
        commands_info = self.registry.get_commands_info()
        
        # Create tools for each command
        for cmd_name, cmd_info in commands_info.items():
            # Create parameters schema for command
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            # Add parameter properties
            for param_name, param_info in cmd_info.get("params", {}).items():
                # Parameter property
                param_property = {
                    "type": param_info.get("type", "string"),
                    "description": param_info.get("description", "")
                }
                
                # Add additional properties if they exist
                if "default" in param_info:
                    param_property["default"] = param_info["default"]
                
                if "enum" in param_info:
                    param_property["enum"] = param_info["enum"]
                
                # Add property to schema
                parameters["properties"][param_name] = param_property
                
                # If parameter is required, add to required list
                if param_info.get("required", False):
                    parameters["required"].append(param_name)
            
            # Create tool
            tool = MCPProxyTool(
                name=f"{self.tool_name_prefix}{cmd_name}",
                description=cmd_info.get("description", ""),
                parameters=parameters
            )
            
            tools.append(tool)
            
            # Add route for tool
            route = {
                "tool_name": tool.name,
                "endpoint": f"{self.cmd_endpoint}",
                "method": "post",
                "json_rpc": {
                    "method": cmd_name
                }
            }
            
            routes.append(route)
        
        # Create MCP Proxy configuration
        config = MCPProxyConfig(
            version="1.0",
            tools=tools,
            routes=routes
        )
        
        return config
    
    def save_config_to_file(self, filename: str) -> None:
        """
        Saves MCP Proxy configuration to file.
        
        Args:
            filename: File name for saving
        """
        config = self.generate_mcp_proxy_config()
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f, ensure_ascii=False, indent=2)
        
        logger.info(f"MCP Proxy configuration saved to file {filename}")
    
    @classmethod
    def from_registry(cls, registry, **kwargs):
        """
        Creates adapter instance from existing command registry.
        
        Args:
            registry: Command registry instance
            **kwargs: Additional parameters for constructor
            
        Returns:
            MCPProxyAdapter: Configured adapter
        """
        return cls(registry, **kwargs) 
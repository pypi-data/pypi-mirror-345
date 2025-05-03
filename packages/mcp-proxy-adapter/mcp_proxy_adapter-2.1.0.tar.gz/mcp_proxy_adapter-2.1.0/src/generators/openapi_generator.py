"""
OpenAPI schema generator for API documentation based on registered commands.
"""
from typing import Any, Dict, List, Optional, Callable
import inspect
from pydantic import BaseModel, create_model

class OpenApiGenerator:
    """
    OpenAPI schema generator for API documentation based on registered commands.
    
    Creates OpenAPI schema describing all registered commands and their parameters
    for use in automatic API documentation.
    """
    
    def __init__(self, dispatcher: Any, title: str = "Vector Store API", 
                 version: str = "1.0.0", description: str = "Vector Store API Documentation"):
        """
        Initialize OpenAPI schema generator.
        
        Args:
            dispatcher: Command dispatcher providing access to registered commands
            title: API title
            version: API version
            description: API description
        """
        self.dispatcher = dispatcher
        self.title = title
        self.version = version
        self.description = description
    
    def generate_schema(self) -> Dict[str, Any]:
        """
        Generates complete OpenAPI schema for all registered commands.
        
        Returns:
            Dict[str, Any]: OpenAPI schema as dictionary
        """
        # Base OpenAPI schema structure
        schema = {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description
            },
            "paths": {},
            "components": {
                "schemas": {}
            }
        }
        
        # Get all registered commands
        commands = self.dispatcher.get_registered_commands()
        
        # Generate schemas for each command
        for command_name, command_data in commands.items():
            handler_func = command_data['handler']
            metadata = command_data.get('metadata', {})
            
            # Add path for endpoint
            path = f"/{command_name}"
            method = "post"  # By default all commands are handled via POST
            
            # Get request schema
            request_schema = self._generate_request_schema(command_name, handler_func)
            
            # Add response schema
            response_schema = self._generate_response_schema(command_name, handler_func, metadata)
            
            # Add path to schema
            schema["paths"][path] = {
                method: {
                    "summary": metadata.get('summary', f"Execute {command_name} command"),
                    "description": metadata.get('description', ""),
                    "operationId": f"{command_name}",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": request_schema
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful operation",
                            "content": {
                                "application/json": {
                                    "schema": response_schema
                                }
                            }
                        },
                        "500": {
                            "description": "Internal server error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {
                                                "type": "boolean",
                                                "example": False
                                            },
                                            "error": {
                                                "type": "string"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        
        # Add /help endpoint
        schema["paths"]["/help"] = {
            "get": {
                "summary": "Get API help",
                "description": "Get list of all available commands and API endpoints",
                "operationId": "getHelp",
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "success": {
                                            "type": "boolean",
                                            "example": True
                                        },
                                        "registered_commands": {
                                            "type": "object",
                                            "additionalProperties": {
                                                "type": "object",
                                                "properties": {
                                                    "endpoint": {
                                                        "type": "string"
                                                    },
                                                    "description": {
                                                        "type": "string"
                                                    },
                                                    "parameters": {
                                                        "type": "object"
                                                    }
                                                }
                                            }
                                        },
                                        "endpoints": {
                                            "type": "array",
                                            "items": {
                                                "type": "string"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return schema
    
    def _generate_request_schema(self, command_name: str, handler_func: Callable) -> Dict[str, Any]:
        """
        Generates request schema for specified command.
        
        Args:
            command_name: Command name
            handler_func: Command handler function
            
        Returns:
            Dict[str, Any]: Request schema in OpenAPI format
        """
        # Get function signature
        sig = inspect.signature(handler_func)
        
        # Create request schema
        properties = {}
        required = []
        
        for name, param in sig.parameters.items():
            # Skip self parameter
            if name == 'self':
                continue
                
            # Get parameter type
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else Any
            
            # Determine type for OpenAPI
            if param_type == str:
                prop_type = {"type": "string"}
            elif param_type == int:
                prop_type = {"type": "integer"}
            elif param_type == float:
                prop_type = {"type": "number"}
            elif param_type == bool:
                prop_type = {"type": "boolean"}
            elif param_type == list or param_type == List:
                prop_type = {"type": "array", "items": {"type": "string"}}
            elif param_type == dict or param_type == Dict:
                prop_type = {"type": "object"}
            else:
                prop_type = {"type": "object"}
            
            # Add property to schema
            properties[name] = prop_type
            
            # If parameter is required, add it to required list
            if param.default == inspect.Parameter.empty:
                required.append(name)
        
        schema = {
            "type": "object",
            "properties": properties
        }
        
        if required:
            schema["required"] = required
            
        return schema
    
    def _generate_response_schema(self, command_name: str, handler_func: Callable, 
                                 metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates response schema for specified command.
        
        Args:
            command_name: Command name
            handler_func: Command handler function
            metadata: Command metadata
            
        Returns:
            Dict[str, Any]: Response schema in OpenAPI format
        """
        # Base response structure
        return {
            "type": "object",
            "properties": {
                "success": {
                    "type": "boolean",
                    "example": True
                },
                "result": {
                    "type": "object",
                    "description": metadata.get("returns", "Command result")
                }
            }
        } 
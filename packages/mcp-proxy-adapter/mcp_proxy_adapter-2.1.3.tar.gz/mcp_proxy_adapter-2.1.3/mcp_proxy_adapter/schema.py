"""
Module for optimizing OpenAPI schema for MCP Proxy.
"""
from typing import Dict, Any, List, Optional

class SchemaOptimizer:
    """
    OpenAPI schema optimizer for use with MCP Proxy.
    
    This class transforms a standard OpenAPI schema into a format
    more suitable for use with MCP Proxy and AI models.
    """
    
    def optimize(
        self, 
        schema: Dict[str, Any], 
        cmd_endpoint: str,
        commands_info: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimizes OpenAPI schema for MCP Proxy.
        
        Args:
            schema: Original OpenAPI schema
            cmd_endpoint: Path for universal JSON-RPC endpoint
            commands_info: Information about registered commands
            
        Returns:
            Dict[str, Any]: Optimized schema
        """
        # Create a new schema in a format compatible with the proxy
        optimized = {
            "openapi": "3.0.2",
            "info": {
                "title": "Command Registry API",
                "description": "API for executing commands through MCPProxy",
                "version": "1.0.0"
            },
            "paths": {
                cmd_endpoint: {
                    "post": {
                        "summary": "Execute command",
                        "description": "Universal endpoint for executing various commands",
                        "operationId": "execute_command",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/CommandRequest"
                                    },
                                    "examples": {}
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
                                            "$ref": "#/components/schemas/CommandResponse"
                                        }
                                    }
                                }
                            },
                            "400": {
                                "description": "Error in request or during command execution",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "detail": {
                                                    "type": "string",
                                                    "description": "Error description"
                                                }
                                            }
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
                    "CommandRequest": {
                        "title": "CommandRequest",
                        "description": "Command execution request",
                        "type": "object",
                        "required": ["command"],
                        "properties": {
                            "command": {
                                "title": "Command",
                                "description": "Command to execute",
                                "type": "string",
                                "enum": list(commands_info.keys())
                            },
                            "params": {
                                "title": "Parameters",
                                "description": "Command parameters, depend on command type",
                                "oneOf": []
                            }
                        }
                    },
                    "CommandResponse": {
                        "title": "CommandResponse",
                        "description": "Command execution response",
                        "type": "object",
                        "required": ["result"],
                        "properties": {
                            "result": {
                                "title": "Result",
                                "description": "Command execution result"
                            }
                        }
                    }
                },
                "examples": {}
            }
        }
        
        # Add parameter schemas and examples for each command
        for cmd_name, cmd_info in commands_info.items():
            param_schema_name = f"{cmd_name.capitalize()}Params"
            params = cmd_info.get("params", {})
            has_params = bool(params)

            # Define parameter schema (даже если params пустой, схема будет пустым объектом)
            param_schema = {
                "title": param_schema_name,
                "description": f"Parameters for command {cmd_name}",
                "type": "object",
                "properties": {},
            }
            required_params = []
            example_params = {}

            for param_name, param_info in params.items():
                param_property = {
                    "title": param_name.capitalize(),
                    "type": param_info.get("type", "string"),
                    "description": param_info.get("description", "")
                }
                if "default" in param_info:
                    param_property["default"] = param_info["default"]
                if "enum" in param_info:
                    param_property["enum"] = param_info["enum"]
                param_schema["properties"][param_name] = param_property
                if param_info.get("required", False):
                    required_params.append(param_name)
                if "example" in param_info:
                    example_params[param_name] = param_info["example"]
                elif "default" in param_info:
                    example_params[param_name] = param_info["default"]
                elif param_info.get("type") == "string":
                    example_params[param_name] = "example_value"
                elif param_info.get("type") == "integer":
                    example_params[param_name] = 1
                elif param_info.get("type") == "boolean":
                    example_params[param_name] = False

            if required_params:
                param_schema["required"] = required_params

            # Добавляем схему параметров всегда, даже если она пустая
            optimized["components"]["schemas"][param_schema_name] = param_schema

            # Добавляем $ref на схему параметров в oneOf всегда
            optimized["components"]["schemas"]["CommandRequest"]["properties"]["params"]["oneOf"].append({
                "$ref": f"#/components/schemas/{param_schema_name}"
            })

            # Пример использования команды
            example_id = f"{cmd_name}_example"
            example = {
                "summary": f"Example of using command {cmd_name}",
                "value": {
                    "command": cmd_name
                }
            }
            if has_params:
                example["value"]["params"] = example_params
            optimized["components"]["examples"][example_id] = example
            optimized["paths"][cmd_endpoint]["post"]["requestBody"]["content"]["application/json"]["examples"][example_id] = {
                "$ref": f"#/components/examples/{example_id}"
            }

        # Для команд без параметров добавляем type: null в oneOf
        optimized_oneof = optimized["components"]["schemas"]["CommandRequest"]["properties"]["params"]["oneOf"]
        optimized_oneof.append({"type": "null"})

        # Add tool descriptions to schema for AI models
        self._add_tool_descriptions(optimized, commands_info)
        return optimized
    
    def _add_tool_descriptions(
        self, 
        schema: Dict[str, Any],
        commands_info: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Adds AI tool descriptions to the schema.
        
        This method enhances the OpenAPI schema with special descriptions
        for better integration with AI models and MCPProxy.
        
        Args:
            schema: OpenAPI schema to enhance
            commands_info: Information about registered commands
        """
        # Add AI tool descriptions to x-mcp-tools
        schema["x-mcp-tools"] = []
        
        for cmd_name, cmd_info in commands_info.items():
            # Create tool description
            tool = {
                "name": f"mcp_{cmd_name}",  # Add mcp_ prefix to command name
                "description": cmd_info.get("description", "") or cmd_info.get("summary", ""),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
            
            # Add parameters
            for param_name, param_info in cmd_info.get("params", {}).items():
                # Convert parameter to JSON Schema format
                param_schema = {}
                
                # Parameter type
                param_schema["type"] = param_info.get("type", "string")
                
                # Description
                if "description" in param_info:
                    param_schema["description"] = param_info["description"]
                
                # Default value
                if "default" in param_info:
                    param_schema["default"] = param_info["default"]
                
                # Possible values
                if "enum" in param_info:
                    param_schema["enum"] = param_info["enum"]
                
                # Add parameter to schema
                tool["parameters"]["properties"][param_name] = param_schema
                
                # If parameter is required, add to required list
                if param_info.get("required", False):
                    tool["parameters"]["required"].append(param_name)
            
            # Add tool to list
            schema["x-mcp-tools"].append(tool) 
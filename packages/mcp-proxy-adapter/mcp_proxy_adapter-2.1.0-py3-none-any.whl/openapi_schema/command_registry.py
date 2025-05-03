"""
Command registry for automatic OpenAPI schema generation.
Describes all available API commands, their parameters and response formats.
"""
from typing import Dict, Any, List, Optional, Type, Union, get_type_hints
import inspect
import docstring_parser
from pydantic import BaseModel, Field, create_model

class CommandParameter:
    """Description of a command parameter"""
    def __init__(self, name: str, type_hint: Type, default=None, description: str = None, required: bool = False):
        self.name = name
        self.type_hint = type_hint
        self.default = default
        self.description = description
        self.required = required
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts parameter to dictionary for JSON Schema"""
        result = {
            "name": self.name,
            "type": self._get_type_name(),
            "description": self.description or f"Parameter {self.name}",
            "required": self.required
        }
        
        if self.default is not None and self.default is not inspect.Parameter.empty:
            result["default"] = self.default
            
        return result
    
    def _get_type_name(self) -> str:
        """Gets type name for JSON Schema"""
        if self.type_hint == str:
            return "string"
        elif self.type_hint == int:
            return "integer"
        elif self.type_hint == float:
            return "number"
        elif self.type_hint == bool:
            return "boolean"
        elif self.type_hint == list or self.type_hint == List:
            return "array"
        elif self.type_hint == dict or self.type_hint == Dict:
            return "object"
        else:
            return "object"


class CommandInfo:
    """Information about a command"""
    def __init__(self, name: str, handler_func, description: str = None, summary: str = None):
        self.name = name
        self.handler_func = handler_func
        self.description = description or ""
        self.summary = summary or name.replace("_", " ").capitalize()
        self.parameters: List[CommandParameter] = []
        self._parse_parameters()
    
    def _parse_parameters(self):
        """Extracts parameter information from function signature"""
        sig = inspect.signature(self.handler_func)
        type_hints = get_type_hints(self.handler_func)
        docstring = docstring_parser.parse(self.handler_func.__doc__ or "")
        
        # Create dictionary for finding parameter descriptions in docstring
        param_descriptions = {param.arg_name: param.description for param in docstring.params}
        
        for name, param in sig.parameters.items():
            # Ignore self parameter for class methods
            if name == 'self':
                continue
                
            # Determine parameter type
            param_type = type_hints.get(name, Any)
            
            # Determine if parameter is required
            required = param.default == inspect.Parameter.empty
            
            # Add parameter
            self.parameters.append(CommandParameter(
                name=name,
                type_hint=param_type,
                default=None if param.default == inspect.Parameter.empty else param.default,
                description=param_descriptions.get(name),
                required=required
            ))
    
    def to_dict(self) -> Dict[str, Any]:
        """Converts command information to dictionary for OpenAPI schema"""
        return {
            "name": self.name,
            "summary": self.summary,
            "description": self.description,
            "parameters": [param.to_dict() for param in self.parameters]
        }


class CommandRegistry:
    """API command registry"""
    def __init__(self):
        self.commands: Dict[str, CommandInfo] = {}
    
    def register(self, name: str, handler_func = None, description: str = None, summary: str = None):
        """
        Registers a command in the registry.
        Can be used as a decorator.
        
        Args:
            name: Command name
            handler_func: Command handler function
            description: Command description
            summary: Brief command summary
        """
        def decorator(func):
            self.commands[name] = CommandInfo(
                name=name,
                handler_func=func,
                description=description or func.__doc__,
                summary=summary
            )
            return func
        
        if handler_func is not None:
            return decorator(handler_func)
        return decorator
    
    def get_command(self, name: str) -> Optional[CommandInfo]:
        """Gets information about a command by its name"""
        return self.commands.get(name)
    
    def get_all_commands(self) -> List[CommandInfo]:
        """Gets list of all registered commands"""
        return list(self.commands.values())
    
    def generate_openapi_components(self) -> Dict[str, Any]:
        """
        Generates OpenAPI schema components based on registered commands.
        
        Returns:
            Dict[str, Any]: OpenAPI schema components
        """
        components = {
            "schemas": {}
        }
        
        # Add common schemas for CommandRequest and JsonRpcResponse
        components["schemas"]["CommandRequest"] = {
            "type": "object",
            "required": ["command", "jsonrpc"],
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
                    "enum": list(self.commands.keys())
                },
                "params": {
                    "title": "Params",
                    "description": "Command parameters",
                    "oneOf": []
                }
            }
        }
        
        components["schemas"]["JsonRpcResponse"] = {
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
        
        # Create schemas for each command's parameters
        for command_name, command_info in self.commands.items():
            param_schema_name = f"{command_name.title().replace('_', '')}Params"
            
            # Create command parameter schema
            param_schema = {
                "type": "object",
                "title": param_schema_name,
                "description": f"Parameters for command {command_name}",
                "properties": {},
                "required": []
            }
            
            # Add properties for each parameter
            for param in command_info.parameters:
                param_type = param._get_type_name()
                param_schema["properties"][param.name] = {
                    "type": param_type,
                    "description": param.description or f"Parameter {param.name}"
                }
                
                if param.default is not None and param.default is not inspect.Parameter.empty:
                    param_schema["properties"][param.name]["default"] = param.default
                
                if param.required:
                    param_schema["required"].append(param.name)
            
            # Add parameter schema to components
            components["schemas"][param_schema_name] = param_schema
            
            # Add reference to parameter schema in oneOf list of CommandRequest
            components["schemas"]["CommandRequest"]["properties"]["params"]["oneOf"].append({
                "$ref": f"#/components/schemas/{param_schema_name}"
            })
        
        # Add null as possible value for parameters
        components["schemas"]["CommandRequest"]["properties"]["params"]["oneOf"].append({
            "type": "null"
        })
        
        return components
    
    def generate_examples(self) -> Dict[str, Any]:
        """
        Generates command usage examples for OpenAPI schema.
        
        Returns:
            Dict[str, Any]: Command usage examples
        """
        examples = {}
        
        for command_name, command_info in self.commands.items():
            # Create base request example
            example = {
                "summary": command_info.summary,
                "value": {
                    "jsonrpc": "2.0",
                    "command": command_name,
                    "params": {},
                    "id": command_name
                }
            }
            
            # Fill example with default parameters or examples
            for param in command_info.parameters:
                if param.default is not None and param.default is not inspect.Parameter.empty:
                    example["value"]["params"][param.name] = param.default
                elif param.type_hint == str:
                    example["value"]["params"][param.name] = f"example_{param.name}"
                elif param.type_hint == int:
                    example["value"]["params"][param.name] = 1
                elif param.type_hint == float:
                    example["value"]["params"][param.name] = 1.0
                elif param.type_hint == bool:
                    example["value"]["params"][param.name] = True
                elif param.type_hint == list or param.type_hint == List:
                    example["value"]["params"][param.name] = []
                elif param.type_hint == dict or param.type_hint == Dict:
                    example["value"]["params"][param.name] = {}
            
            # Add example to examples dictionary
            examples[f"{command_name}_example"] = example
            
        return examples


# Create global command registry instance
registry = CommandRegistry() 
# -*- coding: utf-8 -*-
"""
Test utilities for MCP Proxy Adapter: mock dispatcher, registry, and OpenAPI generator.
Can be used in examples and tests.
"""

def success_command(value: int = 1) -> dict:
    return {"result": value * 2}

def error_command() -> None:
    raise ValueError("Test error")

def param_command(required_param: str, optional_param: int = 0) -> dict:
    return {"required": required_param, "optional": optional_param}

def complex_param_command(array_param: list, object_param: dict, bool_param: bool = True) -> dict:
    return {
        "array_length": len(array_param),
        "object_keys": list(object_param.keys()),
        "bool_value": bool_param
    }

def type_error_command(param: int) -> dict:
    return {"param": param + 1}

class MockDispatcher:
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
                "params": {"value": {"type": "integer", "description": "Input value", "required": False, "default": 1}}
            },
            "error": {"description": "Command with error", "params": {}},
            "param": {
                "description": "Command with parameters",
                "params": {
                    "required_param": {"type": "string", "description": "Required parameter", "required": True},
                    "optional_param": {"type": "integer", "description": "Optional parameter", "required": False, "default": 0}
                }
            },
            "execute": {
                "description": "Universal command for executing other commands",
                "params": {"query": {"type": "string", "description": "Command or query to execute", "required": False}}
            },
            "complex_param": {
                "description": "Command with complex parameters",
                "params": {
                    "array_param": {"type": "array", "description": "Array of values", "required": True},
                    "object_param": {"type": "object", "description": "Object", "required": True},
                    "bool_param": {"type": "boolean", "description": "Boolean value", "required": False, "default": True}
                }
            },
            "type_error": {
                "description": "Command that will raise TypeError",
                "params": {"param": {"type": "integer", "description": "Integer parameter", "required": True}}
            }
        }

    def execute_from_params(self, **params):
        if "query" in params and params["query"] in self.commands:
            command = params.pop("query")
            return self.execute(command, **params)
        return {"available_commands": self.get_valid_commands(), "received_params": params}

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

class MockRegistry:
    def __init__(self, use_openapi_generator=False):
        self.dispatcher = MockDispatcher()
        self.generators = []
        self.use_openapi_generator = use_openapi_generator

    def get_commands_info(self):
        return self.dispatcher.get_commands_info()

    def add_generator(self, generator):
        self.generators.append(generator)
        if hasattr(generator, 'set_dispatcher'):
            generator.set_dispatcher(self.dispatcher)

class MockOpenApiGenerator:
    def __init__(self, **kwargs):
        self.dispatcher = None
        self.kwargs = kwargs

    def set_dispatcher(self, dispatcher):
        self.dispatcher = dispatcher

    def generate_schema(self):
        return {
            "openapi": "3.0.0",
            "info": {"title": "Mock API", "version": "1.0.0"},
            "paths": {}
        } 
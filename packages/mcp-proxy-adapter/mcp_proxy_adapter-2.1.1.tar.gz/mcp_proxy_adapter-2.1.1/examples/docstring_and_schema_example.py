"""
Docstring and Schema Example for MCPProxyAdapter

- How to write docstrings for commands
- How docstrings are used in OpenAPI/schema
- Best practices for documenting parameters and return values

Run:
    python examples/docstring_and_schema_example.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from mcp_proxy_adapter.adapter import MCPProxyAdapter

class MyRegistry:
    def __init__(self):
        self.dispatcher = self
        self.commands = {"sum": self.sum_numbers}
        self.commands_info = {
            "sum": {
                "description": self.sum_numbers.__doc__,
                "params": {
                    "a": {"type": "integer", "description": "First number", "required": True},
                    "b": {"type": "integer", "description": "Second number", "required": True}
                }
            }
        }
    def get_valid_commands(self):
        return list(self.commands.keys())
    def get_command_info(self, command):
        return self.commands_info.get(command)
    def get_commands_info(self):
        return self.commands_info
    def execute(self, command, **params):
        if command == "sum":
            return self.sum_numbers(**params)
        raise KeyError(f"Unknown command: {command}")
    def add_generator(self, generator):
        pass
    def sum_numbers(self, a: int, b: int) -> int:
        """
        Returns the sum of two numbers.
        
        Args:
            a (int): First number
            b (int): Second number
        
        Returns:
            int: The sum of a and b
        """
        return a + b

if __name__ == "__main__":
    registry = MyRegistry()
    adapter = MCPProxyAdapter(registry)
    # Print OpenAPI schema (simulated)
    schema = adapter.generate_mcp_proxy_config()
    print("=== Tool description from docstring ===")
    print(schema.tools[0].description) 
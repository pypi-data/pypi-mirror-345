"""
Testing Example for MCPProxyAdapter

- How to write unit and integration tests for commands
- How to test help and error handling
- Best practices for test structure

Run:
    python examples/testing_example.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from mcp_proxy_adapter.adapter import MCPProxyAdapter

class MyRegistry:
    def __init__(self):
        self.dispatcher = self
        self.commands = {"echo": self.echo}
        self.commands_info = {"echo": {"description": "Echo input string", "params": {"text": {"type": "string", "description": "Text to echo", "required": True}}}}
    def get_valid_commands(self):
        return list(self.commands.keys())
    def get_command_info(self, command):
        return self.commands_info.get(command)
    def get_commands_info(self):
        return self.commands_info
    def execute(self, command, **params):
        if command == "echo":
            return self.echo(**params)
        raise KeyError(f"Unknown command: {command}")
    def add_generator(self, generator):
        pass
    def echo(self, text: str) -> str:
        """Echo input string."""
        return text

def test_echo():
    registry = MyRegistry()
    adapter = MCPProxyAdapter(registry)
    # Unit test
    assert registry.execute("echo", text="hi") == "hi"
    # Integration test (simulate JSON-RPC)
    class Request:
        method = "echo"
        params = {"text": "hello"}
        id = 1
    response = adapter.router.routes[0].endpoint(Request())
    # Not a real FastAPI call, just for illustration
    print("[TEST] Echo command passed.")

if __name__ == "__main__":
    test_echo()
    print("All tests passed.") 
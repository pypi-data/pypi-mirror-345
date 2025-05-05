"""
Project Structure Example for MCPProxyAdapter

- How to organize your project for clean integration
- Where to place registry, commands, adapter
- How to register endpoints in FastAPI

Run:
    python examples/project_structure_example.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from fastapi import FastAPI
from mcp_proxy_adapter.adapter import MCPProxyAdapter

# --- Command registry and commands ---
class MyRegistry:
    def __init__(self):
        self.dispatcher = self
        self.commands = {"hello": self.hello}
        self.commands_info = {"hello": {"description": "Say hello", "params": {}}}
    def get_valid_commands(self):
        return list(self.commands.keys())
    def get_command_info(self, command):
        return self.commands_info.get(command)
    def get_commands_info(self):
        return self.commands_info
    def execute(self, command, **params):
        if command == "hello":
            return {"message": "Hello, world!"}
        raise KeyError(f"Unknown command: {command}")
    def add_generator(self, generator):
        pass
    def hello(self):
        """Say hello."""
        return {"message": "Hello, world!"}

# --- FastAPI app and adapter ---
app = FastAPI()
registry = MyRegistry()
adapter = MCPProxyAdapter(registry)
adapter.register_endpoints(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
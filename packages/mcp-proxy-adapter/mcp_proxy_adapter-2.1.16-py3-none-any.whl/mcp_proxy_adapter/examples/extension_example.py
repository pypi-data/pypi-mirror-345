"""
Extension Example for MCPProxyAdapter

- How to add custom commands
- How to extend help logic
- How to customize error handling

Run:
    python examples/extension_example.py
"""
import os
import sys
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from mcp_proxy_adapter.adapter import MCPProxyAdapter

class MyRegistry:
    def __init__(self):
        self.dispatcher = self
        self.commands = {"ping": self.ping, "help": self.help_command}
        self.commands_info = {
            "ping": {"description": "Ping command (returns pong)", "params": {}},
            "help": {"description": "Show help for commands", "params": {"cmdname": {"type": "string", "description": "Command name", "required": False}}}
        }
    def get_valid_commands(self):
        return list(self.commands.keys())
    def get_command_info(self, command):
        return self.commands_info.get(command)
    def get_commands_info(self):
        return self.commands_info
    def execute(self, *args, **params):
        if args:
            command = args[0]
            params = {k: v for k, v in params.items()}
        else:
            command = params.pop("cmdname", None)
        if command == "ping":
            return self.ping()
        if command == "help":
            return self.help_command(**params)
        raise KeyError(f"Unknown command: {command}")
    def add_generator(self, generator):
        pass
    def ping(self):
        """Ping command."""
        return {"result": "pong"}
    def help_command(self, cmdname: str = None):
        """Custom help logic: returns info for command or all commands."""
        if not cmdname:
            return {"commands": list(self.commands_info.keys())}
        if cmdname in self.commands_info:
            return {"command": cmdname, "info": self.commands_info[cmdname]}
        return {"error": f"Command '{cmdname}' not found"}

if __name__ == "__main__":
    registry = MyRegistry()
    adapter = MCPProxyAdapter(registry)
    # Call sync handler
    result_sync = registry.execute("ping")
    print(result_sync)  # Ping

    # Call help (all)
    result_help_all = registry.execute("help")
    print("Help (all)", result_help_all)

    # Call help (ping)
    result_help_ping = registry.execute("help", cmdname="ping")
    print("Help (ping)", result_help_ping)

    # Call help (notfound)
    result_help_notfound = registry.execute("help", cmdname="notfound")
    print("Help (notfound)", result_help_notfound) 
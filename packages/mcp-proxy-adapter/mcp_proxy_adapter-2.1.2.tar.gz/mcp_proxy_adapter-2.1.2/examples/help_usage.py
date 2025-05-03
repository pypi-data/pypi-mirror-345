"""
Example: Using 'help' command with MCPProxyAdapter

This script demonstrates how to:
- Call the 'help' command (if present in the project)
- Call 'help' with a parameter (for a specific command)
- Handle errors and fallback to adapter help
- Best practices for integrating and extending help

Run:
    python examples/help_usage.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from typing import Any, Dict

# Assume MCPProxyAdapter and MockRegistry are available from src and tests
from mcp_proxy_adapter.adapter import MCPProxyAdapter
from tests.test_mcp_proxy_adapter import MockRegistry

# --- Setup registry and adapter ---
registry = MockRegistry()
adapter = MCPProxyAdapter(registry)

# --- Best practice: always check if 'help' is in commands ---
def call_help(command: str = None) -> Dict[str, Any]:
    """Call help command with or without parameter."""
    dispatcher = registry.dispatcher
    if "help" in dispatcher.get_valid_commands():
        if command:
            try:
                return dispatcher.help_command(command=command)
            except Exception as e:
                print(f"Project help failed: {e}. Fallback to adapter help.")
                return adapter_help(command)
        else:
            return dispatcher.help_command()
    else:
        return adapter_help(command)

def adapter_help(command: str = None) -> Dict[str, Any]:
    """Fallback: call adapter's help (simulate)."""
    dispatcher = registry.dispatcher
    if not command:
        return {"source": "adapter", "commands": dispatcher.get_valid_commands()}
    if command in dispatcher.get_valid_commands():
        return {"source": "adapter", "command": command, "info": {"description": "Adapter help for command"}}
    return {"source": "adapter", "error": f"Command '{command}' not found (adapter)", "available_commands": dispatcher.get_valid_commands()}

if __name__ == "__main__":
    print("=== Project help (no param) ===")
    print(call_help())
    print("\n=== Project help (existing command) ===")
    print(call_help("success"))
    print("\n=== Project help (nonexistent command, triggers fallback) ===")
    print(call_help("not_a_command"))
    print("\n=== Adapter help (no project help present) ===")
    # Simulate registry without help
    registry_no_help = MockRegistry()
    if "help" in registry_no_help.dispatcher.commands:
        del registry_no_help.dispatcher.commands["help"]
    adapter_no_help = MCPProxyAdapter(registry_no_help)
    print(adapter_help("success")) 
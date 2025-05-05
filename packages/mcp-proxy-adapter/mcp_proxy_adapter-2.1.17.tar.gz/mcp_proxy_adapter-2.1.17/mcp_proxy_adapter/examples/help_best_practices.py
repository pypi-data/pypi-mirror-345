"""
Best Practices: Integrating and Testing 'help' Command in MCPProxyAdapter

This example demonstrates:
- How to robustly integrate a project-level 'help' command
- How to extend help with custom logic
- How to test help scenarios (including fallback and error cases)
- How to avoid common mistakes

Run:
    python examples/help_best_practices.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from typing import Any, Dict
from mcp_proxy_adapter.adapter import MCPProxyAdapter
from mcp_proxy_adapter.testing_utils import MockRegistry

# --- Setup registry and adapter ---
registry = MockRegistry()
adapter = MCPProxyAdapter(registry)

def robust_help(cmdname: str = None) -> Dict[str, Any]:
    """
    Best practice: always check for project help, handle errors, fallback to adapter help.
    """
    dispatcher = registry.dispatcher
    if "help" in dispatcher.get_valid_commands():
        try:
            if cmdname:
                return dispatcher.help_command(cmdname=cmdname)
            return dispatcher.help_command()
        except Exception as e:
            # Log error, fallback to adapter help
            print(f"[WARN] Project help failed: {e}. Fallback to adapter help.")
            return fallback_adapter_help(cmdname)
    else:
        return fallback_adapter_help(cmdname)

def fallback_adapter_help(cmdname: str = None) -> Dict[str, Any]:
    """
    Fallback: call adapter's help (simulate REST/JSON-RPC call).
    """
    dispatcher = registry.dispatcher
    if not cmdname:
        return {"source": "adapter", "commands": dispatcher.get_valid_commands()}
    if cmdname in dispatcher.get_valid_commands():
        return {"source": "adapter", "command": cmdname, "info": {"description": "Adapter help for command"}}
    return {"source": "adapter", "error": f"Command '{cmdname}' not found (adapter)", "available_commands": dispatcher.get_valid_commands()}

# --- Example test cases ---
def test_help():
    """Test all help scenarios."""
    print("[TEST] Project help (no param):", robust_help())
    print("[TEST] Project help (existing command):", robust_help("success"))
    print("[TEST] Project help (nonexistent command, triggers fallback):", robust_help("not_a_command"))
    # Simulate registry without help
    registry_no_help = MockRegistry()
    if "help" in registry_no_help.dispatcher.commands:
        del registry_no_help.dispatcher.commands["help"]
    global registry
    registry = registry_no_help
    print("[TEST] Adapter help (no project help present):", robust_help("success"))

if __name__ == "__main__":
    test_help() 
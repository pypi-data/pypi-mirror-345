#!/usr/bin/env python
"""
Entry point for the command registry CLI interface.

This module allows running commands from the command line
using the command dispatcher.

Usage:
    python -m command_registry.cli [command] [args...]
"""

import os
import sys
import importlib.util
from typing import Optional

from command_registry.cli.command_runner import CommandRunner
from command_registry.dispatchers.base_dispatcher import BaseDispatcher
from command_registry.dispatchers.command_dispatcher import CommandDispatcher


def find_dispatcher() -> BaseDispatcher:
    """
    Finds and creates command dispatcher.
    
    Search order:
    1. Checks DISPATCHER_MODULE environment variable
    2. Looks for app.py in current directory
    3. Creates new CommandDispatcher
    
    Returns:
        BaseDispatcher: Command dispatcher
    """
    # Check environment variable
    dispatcher_module = os.environ.get("DISPATCHER_MODULE")
    if dispatcher_module:
        try:
            module_path, attr_name = dispatcher_module.rsplit(":", 1)
            module = importlib.import_module(module_path)
            return getattr(module, attr_name)
        except (ValueError, ImportError, AttributeError) as e:
            print(f"Failed to load dispatcher from {dispatcher_module}: {e}", 
                  file=sys.stderr)
    
    # Check app.py file
    app_path = os.path.join(os.getcwd(), "app.py")
    if os.path.exists(app_path):
        try:
            spec = importlib.util.spec_from_file_location("app", app_path)
            if spec and spec.loader:
                app = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(app)
                
                # Look for dispatcher in module
                dispatcher = getattr(app, "dispatcher", None)
                if dispatcher and isinstance(dispatcher, BaseDispatcher):
                    return dispatcher
        except Exception as e:
            print(f"Failed to load dispatcher from app.py: {e}", 
                  file=sys.stderr)
    
    # Create new dispatcher if not found
    return CommandDispatcher()


def main() -> None:
    """
    Main function for running CLI interface.
    """
    # Get dispatcher
    dispatcher = find_dispatcher()
    
    # Create and run CommandRunner
    runner = CommandRunner(dispatcher)
    runner.run(sys.argv[1:])


if __name__ == "__main__":
    main() 
"""
Command line utility for executing commands.

Provides a command line interface for the command dispatcher,
allowing execution of registered commands and getting help information.
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Sequence

from command_registry.dispatchers.base_dispatcher import BaseDispatcher


class CommandRunner:
    """
    Command line utility for executing commands.
    
    Converts command line arguments into dispatcher command calls.
    Provides ability to get help information about commands.
    """
    
    def __init__(self, dispatcher: BaseDispatcher):
        """
        Initializes CommandRunner.
        
        Args:
            dispatcher: Command dispatcher for executing commands
        """
        self.dispatcher = dispatcher
    
    def build_parser(self) -> argparse.ArgumentParser:
        """
        Creates argument parser based on registered commands.
        
        Returns:
            Command line argument parser
        """
        parser = argparse.ArgumentParser(
            description="Execute commands from command registry",
            add_help=False,  # Disable standard help
        )
        
        # Add main arguments
        parser.add_argument(
            "command", 
            help="Command name to execute or 'help' to get list of commands",
            nargs="?",
            default="help",
        )
        
        parser.add_argument(
            "--help", "-h", 
            action="store_true",
            help="Show help for specified command",
            dest="show_help",
        )
        
        parser.add_argument(
            "--json", 
            action="store_true",
            help="Output result in JSON format",
        )
        
        return parser
    
    def _handle_help_command(self, args: Optional[List[str]] = None) -> None:
        """
        Outputs help information about available commands.
        
        Args:
            args: List of arguments, if first argument is command name,
                 outputs help for that command
        """
        if args and len(args) > 0 and args[0] != "help":
            # Help for specific command
            command_name = args[0]
            if command_name not in self.dispatcher.get_valid_commands():
                print(f"Unknown command: {command_name}", file=sys.stderr)
                return
            
            info = self.dispatcher.get_command_info(command_name)
            
            print(f"\nCommand: {command_name}\n")
            
            if info.get("description"):
                print(f"Description: {info['description']}\n")
            
            if "parameters" in info and info["parameters"]:
                print("Parameters:")
                for name, param_info in info["parameters"].items():
                    param_type = param_info.get("type", "any")
                    required = param_info.get("required", False)
                    description = param_info.get("description", "")
                    
                    req_str = " (required)" if required else ""
                    print(f"  {name} ({param_type}){req_str}")
                    if description:
                        print(f"    {description}")
                print()
            
            if "returns" in info and info["returns"]:
                print(f"Returns: {info['returns']}")
            
            print("\nUsage:")
            params_str = " ".join(
                f"--{name}=<value>" for name in info.get("parameters", {})
            )
            print(f"  python -m command_registry.cli {command_name} {params_str}")
        else:
            # General help
            commands = self.dispatcher.get_commands_info()
            
            print("\nAvailable commands:\n")
            for name, info in commands.items():
                description = info.get("description", "No description")
                # Show only first line of description for brevity
                short_desc = description.split("\n")[0]
                print(f"  {name:<20} {short_desc}")
            
            print("\nTo get detailed information about a command use:")
            print("  python -m command_registry.cli help <command>")
            print("  python -m command_registry.cli <command> --help")
    
    def run(self, args: Sequence[str]) -> None:
        """
        Runs command based on provided arguments.
        
        Args:
            args: Command line arguments (without program name)
        """
        parser = self.build_parser()
        
        # Parse arguments
        parsed_args, remaining = parser.parse_known_args(args)
        
        # Handle help command or --help flag
        if parsed_args.command == "help" or parsed_args.show_help:
            if parsed_args.command == "help":
                self._handle_help_command(remaining)
            else:
                self._handle_help_command([parsed_args.command])
            return
        
        # Check command existence
        if parsed_args.command not in self.dispatcher.get_valid_commands():
            print(f"Unknown command: {parsed_args.command}", file=sys.stderr)
            print("Use 'help' to get list of available commands", file=sys.stderr)
            sys.exit(1)
        
        # Convert remaining arguments to command parameters
        command_params = {}
        command_info = self.dispatcher.get_command_info(parsed_args.command)
        expected_params = command_info.get("parameters", {})
        
        # Parse parameters from remaining arguments
        i = 0
        while i < len(remaining):
            arg = remaining[i]
            
            # Support --param=value format
            if arg.startswith("--") and "=" in arg:
                param_name, value = arg[2:].split("=", 1)
                command_params[param_name] = self._parse_value(value)
                i += 1
            # Support --param value format
            elif arg.startswith("--"):
                param_name = arg[2:]
                if i + 1 < len(remaining) and not remaining[i + 1].startswith("--"):
                    command_params[param_name] = self._parse_value(remaining[i + 1])
                    i += 2
                else:
                    # Boolean flag
                    command_params[param_name] = True
                    i += 1
            else:
                print(f"Unknown argument: {arg}", file=sys.stderr)
                i += 1
        
        # Check required parameters
        for param_name, param_info in expected_params.items():
            if param_info.get("required", False) and param_name not in command_params:
                print(f"Missing required parameter: {param_name}", file=sys.stderr)
                sys.exit(1)
        
        try:
            # Execute command
            result = self.dispatcher.execute(parsed_args.command, **command_params)
            
            # Output result
            if parsed_args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif result is not None:
                print(result)
        except Exception as e:
            print(f"Error executing command: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _parse_value(self, value_str: str) -> Any:
        """
        Parses string value into corresponding type.
        
        Args:
            value_str: String representation of value
            
        Returns:
            Parsed value of corresponding type
        """
        # Boolean values
        if value_str.lower() in ("true", "yes", "y", "1"):
            return True
        if value_str.lower() in ("false", "no", "n", "0"):
            return False
        
        # Numbers
        try:
            if "." in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        # JSON
        if (value_str.startswith("{") and value_str.endswith("}")) or \
           (value_str.startswith("[") and value_str.endswith("]")):
            try:
                return json.loads(value_str)
            except json.JSONDecodeError:
                pass
        
        # Default - string
        return value_str 
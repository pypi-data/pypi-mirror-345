"""
Implementation of a JSON-RPC based command dispatcher.
"""
from typing import Dict, Any, Callable, List, Optional, Union
import inspect
import logging
import traceback
from .base_dispatcher import BaseDispatcher

logger = logging.getLogger("command_registry")

class CommandError(Exception):
    """Base class for command errors"""
    pass

class CommandNotFoundError(CommandError):
    """Error raised when attempting to execute a non-existent command"""
    pass

class CommandExecutionError(CommandError):
    """Error raised during command execution"""
    pass

class JsonRpcDispatcher(BaseDispatcher):
    """
    JSON-RPC based command dispatcher.
    
    Implements the BaseDispatcher interface for handling commands in JSON-RPC 2.0 format.
    Supports registration, execution, and retrieval of command information.
    """
    
    def __init__(self):
        """Initializes a new dispatcher instance"""
        self._handlers = {}
        self._metadata = {}
        
        # Register the built-in help command
        self.register_handler(
            command="help",
            handler=self._help_command,
            description="Returns information about available commands",
            summary="Command help",
            params={
                "command": {
                    "type": "string",
                    "description": "Command name for detailed information",
                    "required": False
                }
            }
        )
    
    def register_handler(
        self, 
        command: str, 
        handler: Callable, 
        description: str = "", 
        summary: str = "", 
        params: Dict[str, Any] = None
    ) -> None:
        """
        Registers a command handler.
        
        Args:
            command: Command name
            handler: Command handler function
            description: Command description
            summary: Brief command summary
            params: Command parameters description
        """
        if not params:
            params = {}
            
        # Save the handler
        self._handlers[command] = handler
        
        # Save metadata
        self._metadata[command] = {
            "description": description,
            "summary": summary or command.replace("_", " ").title(),
            "params": params
        }
        
        logger.debug(f"Registered command: {command}")
    
    def execute(self, command: str, **kwargs) -> Any:
        """
        Executes a command with the specified parameters.
        
        Args:
            command: Command name
            **kwargs: Command parameters
            
        Returns:
            Any: Command execution result
            
        Raises:
            CommandNotFoundError: If command is not found
            CommandExecutionError: On command execution error
        """
        # Check if command exists
        if command not in self._handlers:
            raise CommandNotFoundError(f"Command '{command}' not found")
        
        handler = self._handlers[command]
        
        try:
            # Get function signature
            sig = inspect.signature(handler)
            
            # If function accepts params dictionary, pass all parameters in it
            if len(sig.parameters) == 1 and list(sig.parameters.keys())[0] == 'params':
                return handler(params=kwargs)
            
            # Otherwise pass parameters as named arguments
            return handler(**kwargs)
        except Exception as e:
            # Log the error
            logger.error(f"Error executing command '{command}': {str(e)}")
            logger.debug(traceback.format_exc())
            
            # Re-raise the exception
            raise CommandExecutionError(f"Error executing command '{command}': {str(e)}")
    
    def get_valid_commands(self) -> List[str]:
        """
        Returns a list of all registered command names.
        
        Returns:
            List[str]: List of command names
        """
        return list(self._handlers.keys())
    
    def get_command_info(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Returns information about a command.
        
        Args:
            command: Command name
            
        Returns:
            Optional[Dict[str, Any]]: Command information or None if command not found
        """
        if command not in self._metadata:
            return None
        
        return self._metadata[command]
    
    def get_commands_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns information about all registered commands.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary {command_name: information}
        """
        return self._metadata.copy()
    
    def _help_command(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Built-in help command for getting command information.
        
        Args:
            params: Command parameters
                command: Command name for detailed information
                
        Returns:
            Dict[str, Any]: Command help information
        """
        if not params:
            params = {}
            
        # If specific command is specified, return information only about it
        if "command" in params and params["command"]:
            command = params["command"]
            if command not in self._metadata:
                return {
                    "error": f"Command '{command}' not found",
                    "available_commands": list(self._metadata.keys())
                }
            
            return {
                "command": command,
                "info": self._metadata[command]
            }
        
        # Otherwise return brief information about all commands
        commands_info = {}
        for cmd, info in self._metadata.items():
            commands_info[cmd] = {
                "summary": info["summary"],
                "description": info["description"],
                "params_count": len(info["params"])
            }
        
        return {
            "commands": commands_info,
            "total": len(commands_info),
            "note": "Use the 'command' parameter to get detailed information about a specific command"
        } 
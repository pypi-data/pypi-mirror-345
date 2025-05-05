"""
Implementation of a JSON-RPC based command dispatcher.

CHANGELOG:
- 2024-06-13: execute() now always returns awaitable. If handler is sync and for any reason result is not awaitable, it is wrapped in an async function and awaited. This guarantees await-safety for all handler types and fixes 'object ... can't be used in await expression' errors in all environments.
"""
from typing import Dict, Any, Callable, List, Optional, Union
import inspect
import logging
import traceback
from .base_dispatcher import BaseDispatcher
import asyncio

logger = logging.getLogger("command_registry")

print('[DEBUG] LOADED json_rpc_dispatcher.py')

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

    Best practice:
    ----------------
    Register handlers explicitly using register_handler (no decorators!).
    Both sync and async handlers are supported.

    Example:
        import asyncio
        from mcp_proxy_adapter.dispatchers.json_rpc_dispatcher import JsonRpcDispatcher

        def sync_handler(x):
            return x + 1

        async def async_handler(x):
            await asyncio.sleep(0.1)
            return x * 2

        dispatcher = JsonRpcDispatcher()
        dispatcher.register_handler('sync', sync_handler, description='Sync handler')
        dispatcher.register_handler('async', async_handler, description='Async handler')

        # Call sync handler
        result_sync = asyncio.run(dispatcher.execute('sync', x=10))
        print(result_sync)  # 11

        # Call async handler
        result_async = asyncio.run(dispatcher.execute('async', x=10))
        print(result_async)  # 20
    """
    
    def __init__(self):
        """Initializes a new dispatcher instance"""
        self._handlers = {}
        self._metadata = {}
        
        # Register the built-in help command
        self.register_handler(
            command="help",
            handler=self._help_command,
            description=(
                "Returns information about available commands.\n"
                "Best practice: Register handlers explicitly using register_handler (no decorators).\n"
                "Example: dispatcher.register_handler('mycmd', my_handler, description='...')"
            ),
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
    
    async def _call_handler_always_awaitable(self, handler, kwargs):
        loop = asyncio.get_running_loop()
        sig = inspect.signature(handler)
        params = sig.parameters
        try:
            if inspect.iscoroutinefunction(handler):
                if len(params) == 1 and 'params' in params:
                    result = handler(params=kwargs)
                else:
                    result = handler(**kwargs)
            else:
                if len(params) == 1 and 'params' in params:
                    result = loop.run_in_executor(None, lambda: handler(params=kwargs))
                else:
                    result = loop.run_in_executor(None, lambda: handler(**kwargs))
            if inspect.isawaitable(result):
                return await result
            else:
                async def _return_sync():
                    return result
                return await _return_sync()
        except Exception as e:
            raise e

    async def execute(self, command: str, **kwargs) -> Any:
        # Check if command exists
        if command not in self._handlers:
            raise CommandNotFoundError(f"Command '{command}' not found")
        handler = self._handlers[command]
        try:
            result = await self._call_handler_always_awaitable(handler, kwargs)
            return result
        except Exception as e:
            logger.error(f"Error executing command '{command}': {str(e)}")
            logger.debug(traceback.format_exc())
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
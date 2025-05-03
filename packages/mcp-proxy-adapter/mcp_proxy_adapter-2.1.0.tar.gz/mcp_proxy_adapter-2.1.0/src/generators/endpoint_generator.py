"""
REST API endpoint generator based on registered commands.
"""
from typing import Any, Callable, Dict, List, Optional
import inspect
import asyncio
from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel, create_model

class EndpointGenerator:
    """
    REST API endpoint generator based on registered commands.
    
    Creates dynamic FastAPI endpoints by automatically generating
    request and response models based on signatures and docstrings
    of registered handler functions.
    """
    
    def __init__(self, router: APIRouter, dispatcher: Any):
        """
        Initialize endpoint generator.
        
        Args:
            router: FastAPI router for registering endpoints
            dispatcher: Command dispatcher providing access to registered commands
        """
        self.router = router
        self.dispatcher = dispatcher
        self.registered_endpoints = []
    
    def generate_endpoint(self, command_name: str, handler_func: Callable, metadata: Dict[str, Any]) -> None:
        """
        Generates REST API endpoint for specified command.
        
        Args:
            command_name: Command name
            handler_func: Command handler function
            metadata: Command metadata from docstring
        """
        # Get function signature
        sig = inspect.signature(handler_func)
        
        # Create request model based on function parameters
        param_fields = {}
        for name, param in sig.parameters.items():
            # Skip self parameter
            if name == 'self':
                continue
                
            # Get parameter type and default value
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else Any
            default_value = ... if param.default == inspect.Parameter.empty else param.default
            
            # Add field to model
            param_fields[name] = (param_type, default_value)
        
        # Create request model
        request_model = create_model(
            f"{command_name.capitalize()}Request",
            **param_fields
        )
        
        # Create endpoint
        endpoint_path = f"/{command_name}"
        
        # Define endpoint handler
        async def endpoint_handler(request_data: request_model):
            # Call command through dispatcher
            try:
                # Get parameters from model
                params = request_data.__dict__ if hasattr(request_data, "__dict__") else {}
                
                # Call dispatcher's execute method
                result = self.dispatcher.execute(command_name, **params)
                
                # If result is coroutine, await its completion
                if inspect.iscoroutine(result):
                    result = await result
                
                return {"success": True, "result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Add documentation from metadata
        if 'description' in metadata:
            endpoint_handler.__doc__ = metadata['description']
        
        # Register endpoint
        self.router.post(endpoint_path, response_model=None)(endpoint_handler)
        self.registered_endpoints.append(endpoint_path)
    
    def generate_all_endpoints(self) -> List[str]:
        """
        Generates endpoints for all registered commands.
        
        Returns:
            List[str]: List of created endpoints
        """
        # Create endpoints for all commands
        commands_info = self.dispatcher.get_commands_info()
        
        for command_name, command_info in commands_info.items():
            # Get command handler
            handler = self.dispatcher._handlers[command_name] if hasattr(self.dispatcher, "_handlers") else None
            
            # If handler couldn't be obtained, skip command
            if not handler:
                continue
                
            self.generate_endpoint(
                command_name, 
                handler, 
                command_info
            )
        
        # Create help endpoint
        self.generate_help_endpoint()
        
        return self.registered_endpoints
    
    def generate_help_endpoint(self) -> None:
        """
        Creates special /help endpoint that returns information
        about all available commands and their endpoints.
        """
        async def help_handler(command: Optional[str] = None):
            if command:
                # If specific command is specified, return information about it
                command_info = self.dispatcher.get_command_info(command)
                if not command_info:
                    return {
                        "success": False,
                        "error": f"Command '{command}' not found",
                        "available_commands": self.dispatcher.get_valid_commands()
                    }
                
                # Add endpoint URL
                endpoint_path = f"/{command}"
                
                return {
                    "success": True,
                    "command": command,
                    "info": command_info,
                    "endpoint": endpoint_path
                }
            
            # Otherwise return information about all commands
            commands_info = {}
            for cmd in self.dispatcher.get_valid_commands():
                info = self.dispatcher.get_command_info(cmd)
                if not info:
                    continue
                    
                endpoint_path = f"/{cmd}"
                commands_info[cmd] = {
                    "summary": info.get("summary", ""),
                    "description": info.get("description", ""),
                    "endpoint": endpoint_path,
                    "params_count": len(info.get("params", {}))
                }
            
            return {
                "success": True,
                "commands": commands_info,
                "total": len(commands_info),
                "endpoints": self.registered_endpoints,
                "note": "Use 'command' parameter to get detailed information about a specific command"
            }
        
        help_handler.__doc__ = "Get list of all available commands and API endpoints"
        self.router.get("/help", response_model=None)(help_handler)
        self.registered_endpoints.append("/help") 
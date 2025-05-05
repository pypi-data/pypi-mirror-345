"""
Base command dispatcher class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, Optional

class BaseDispatcher(ABC):
    """
    Abstract base class for command dispatchers.
    
    Defines the interface that all command dispatchers must implement.
    Dispatchers are responsible for registering and executing commands.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_valid_commands(self) -> List[str]:
        """
        Returns a list of all registered command names.
        
        Returns:
            List[str]: List of command names
        """
        pass
    
    @abstractmethod
    def get_command_info(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Returns information about a command.
        
        Args:
            command: Command name
            
        Returns:
            Optional[Dict[str, Any]]: Command information or None if command not found
        """
        pass
    
    @abstractmethod
    def get_commands_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns information about all registered commands.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary {command_name: information}
        """
        pass 
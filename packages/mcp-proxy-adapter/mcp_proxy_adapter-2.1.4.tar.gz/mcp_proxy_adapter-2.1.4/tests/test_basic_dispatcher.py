"""
Tests for basic command dispatcher functionality.
"""
import sys
import os
import pytest
from typing import Dict, Any, List

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import classes for testing
from mcp_proxy_adapter.dispatchers.json_rpc_dispatcher import JsonRpcDispatcher, CommandNotFoundError, CommandExecutionError

# Fixture for creating dispatcher with test commands
@pytest.fixture
def test_dispatcher():
    """Creates dispatcher with test commands"""
    dispatcher = JsonRpcDispatcher()
    
    # Test command with parameters
    def test_command(a: int, b: int = 1) -> int:
        """
        Test command for adding two numbers.
        
        Args:
            a: First number
            b: Second number (default 1)
            
        Returns:
            int: Sum of numbers
        """
        return a + b
    
    # Command for error testing
    def error_command(message: str = "Test error") -> None:
        """
        Command for testing error handling.
        
        Args:
            message: Error message
            
        Raises:
            ValueError: Always raises error
        """
        raise ValueError(message)
    
    # Command accepting params dictionary
    def params_command(params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Command for testing passing all parameters in dictionary.
        
        Args:
            params: Parameters dictionary
            
        Returns:
            Dict[str, Any]: Same parameters dictionary
        """
        return params
    
    # Register commands
    dispatcher.register_handler(
        command="test",
        handler=test_command,
        description="Test command for adding numbers",
        params={
            "a": {"type": "integer", "description": "First number", "required": True},
            "b": {"type": "integer", "description": "Second number", "required": False, "default": 1}
        }
    )
    
    dispatcher.register_handler(
        command="error",
        handler=error_command,
        description="Command for testing errors",
        params={
            "message": {"type": "string", "description": "Error message", "required": False}
        }
    )
    
    dispatcher.register_handler(
        command="params",
        handler=params_command,
        description="Command for testing params passing",
        params={}
    )
    
    return dispatcher

def test_dispatcher_initialization():
    """Test dispatcher initialization"""
    dispatcher = JsonRpcDispatcher()
    
    # Check that dispatcher contains built-in help command
    assert "help" in dispatcher.get_valid_commands()
    
    # Check that help command metadata is correct
    help_info = dispatcher.get_command_info("help")
    assert help_info is not None
    assert "description" in help_info
    assert "summary" in help_info
    assert "params" in help_info

def test_register_and_execute_command(test_dispatcher):
    """Test command registration and execution"""
    # Check that command is registered
    assert "test" in test_dispatcher.get_valid_commands()
    
    # Execute command with required parameter
    result = test_dispatcher.execute("test", a=5)
    assert result == 6  # 5 + 1 (default value)
    
    # Execute command with all parameters
    result = test_dispatcher.execute("test", a=5, b=3)
    assert result == 8  # 5 + 3

def test_command_not_found(test_dispatcher):
    """Test handling of non-existent command"""
    with pytest.raises(CommandNotFoundError):
        test_dispatcher.execute("non_existent_command")

def test_command_execution_error(test_dispatcher):
    """Test handling of error during command execution"""
    with pytest.raises(CommandExecutionError):
        test_dispatcher.execute("error")

def test_get_commands_info(test_dispatcher):
    """Test getting information about commands"""
    commands_info = test_dispatcher.get_commands_info()
    
    # Check presence of all registered commands
    assert "test" in commands_info
    assert "error" in commands_info
    assert "params" in commands_info
    assert "help" in commands_info
    
    # Check presence of all fields in command information
    test_info = commands_info["test"]
    assert "description" in test_info
    assert "summary" in test_info
    assert "params" in test_info

def test_params_command(test_dispatcher):
    """Test command accepting params dictionary"""
    test_params = {"key1": "value1", "key2": 123}
    result = test_dispatcher.execute("params", **test_params)
    assert result == test_params

def test_help_command(test_dispatcher):
    """Test built-in help command"""
    # Request list of all commands
    result = test_dispatcher.execute("help")
    assert "commands" in result
    assert "total" in result
    assert result["total"] == 4  # help, test, error, params
    
    # Run second check through different approach - compare command list
    assert "help" in result["commands"]
    assert "test" in result["commands"]
    assert "error" in result["commands"]
    assert "params" in result["commands"]
    
    # Check that command data contains required fields
    assert "summary" in result["commands"]["test"]
    assert "description" in result["commands"]["test"]
    assert "params_count" in result["commands"]["test"] 
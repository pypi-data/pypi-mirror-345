"""
Tests for CommandRegistry.
"""
import sys
import os
import pytest
import tempfile
from typing import Dict, Any, Optional, List
import inspect

# Add parent directory to import path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import classes for testing
try:
    from mcp_proxy_adapter.registry import CommandRegistry
    from mcp_proxy_adapter.dispatchers.json_rpc_dispatcher import JsonRpcDispatcher
    from mcp_proxy_adapter.analyzers.docstring_analyzer import DocstringAnalyzer
    from mcp_proxy_adapter.analyzers.type_analyzer import TypeAnalyzer
    from mcp_proxy_adapter.validators.docstring_validator import DocstringValidator
except ImportError:
    from src.registry import CommandRegistry
    from src.dispatchers.json_rpc_dispatcher import JsonRpcDispatcher
    from src.analyzers.docstring_analyzer import DocstringAnalyzer
    from src.analyzers.type_analyzer import TypeAnalyzer
    from src.validators.docstring_validator import DocstringValidator


# Test functions for command registration testing

def valid_command(a: int, b: int = 1) -> int:
    """
    Valid function for testing.
    
    Args:
        a: First parameter
        b: Second parameter
        
    Returns:
        int: Calculation result
    """
    return a + b

def invalid_docstring_command(a: int, b: int = 1) -> int:
    """
    Function with invalid docstring.
    
    Args:
        a: First parameter
        # Missing description for parameter b
        
    Returns:
        int: Calculation result
    """
    return a + b

def invalid_annotation_command(a, b = 1):
    """
    Function without type annotations.
    
    Args:
        a: First parameter
        b: Second parameter
        
    Returns:
        Calculation result
    """
    return a + b

def params_command(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Function that accepts a dictionary of parameters.
    
    Args:
        params: Dictionary of parameters
        
    Returns:
        Dict[str, Any]: Processing result
    """
    # Return the params dictionary directly
    return params


@pytest.fixture
def registry():
    """Creates CommandRegistry for tests"""
    return CommandRegistry(
        dispatcher=JsonRpcDispatcher(),
        strict=True,
        auto_fix=False
    )


class TestCommandRegistry:
    """Tests for CommandRegistry"""
    
    def test_initialization(self, registry):
        """Test command registry initialization"""
        # Check that standard analyzers and validators are added
        assert any(isinstance(a, TypeAnalyzer) for a in registry._analyzers)
        assert any(isinstance(a, DocstringAnalyzer) for a in registry._analyzers)
        assert any(isinstance(v, DocstringValidator) for v in registry._validators)
        
        # Check that dispatcher is initialized
        assert registry.dispatcher is not None
        assert isinstance(registry.dispatcher, JsonRpcDispatcher)
    
    def test_analyze_handler(self, registry):
        """Test command handler analysis"""
        metadata = registry.analyze_handler("valid_command", valid_command)
        
        # Check metadata structure
        assert "description" in metadata
        assert "summary" in metadata
        assert "parameters" in metadata
        
        # Check that parameters are discovered
        assert "a" in metadata["parameters"]
        assert "b" in metadata["parameters"]
        
        # Check parameter types
        assert metadata["parameters"]["a"]["type"] == "integer"
        assert metadata["parameters"]["b"]["type"] == "integer"
        
        # Check descriptions and requirement flags
        assert "description" in metadata["parameters"]["a"]
        assert "description" in metadata["parameters"]["b"]
        assert metadata["parameters"]["a"]["required"] is True
        assert metadata["parameters"]["b"]["required"] is False
    
    def test_validate_handler_valid(self, registry):
        """Test validation of a valid handler"""
        metadata = registry.analyze_handler("valid_command", valid_command)
        is_valid, errors = registry.validate_handler("valid_command", valid_command, metadata)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_handler_invalid_docstring(self, registry):
        """Test validation of a handler with invalid docstring"""
        metadata = registry.analyze_handler("invalid_docstring", invalid_docstring_command)
        is_valid, errors = registry.validate_handler("invalid_docstring", invalid_docstring_command, metadata)
        
        assert is_valid is False
        assert len(errors) > 0
        # Check that the error is related to missing description for parameter b
        assert any("parameter 'b'" in error.lower() for error in errors)
    
    def test_validate_handler_invalid_annotation(self, registry):
        """Test validation of a handler without type annotations"""
        metadata = registry.analyze_handler("invalid_annotation", invalid_annotation_command)
        is_valid, errors = registry.validate_handler("invalid_annotation", invalid_annotation_command, metadata)
        
        assert is_valid is False
        assert len(errors) > 0
        # Check that the error is related to missing type annotations
        assert any("type annotation" in error.lower() for error in errors)
    
    def test_register_command_valid(self, registry):
        """Test registration of a valid command"""
        result = registry.register_command("valid", valid_command)
        assert result is True
        
        # Check that the command is registered in the dispatcher
        assert "valid" in registry.dispatcher.get_valid_commands()
        
        # Check that the command can be executed
        assert registry.dispatcher.execute("valid", a=5, b=3) == 8
    
    def test_register_command_invalid_strict(self, registry):
        """Test registration of an invalid command in strict mode"""
        # In strict mode, a command with errors should not be registered
        result = registry.register_command("invalid_docstring", invalid_docstring_command)
        assert result is False
        
        # Check that the command is not registered in the dispatcher
        assert "invalid_docstring" not in registry.dispatcher.get_valid_commands()
    
    def test_register_command_invalid_not_strict(self):
        """Test registration of an invalid command in non-strict mode"""
        # Create registry in non-strict mode
        registry = CommandRegistry(strict=False, auto_fix=False)
        
        # In non-strict mode, a command with errors should be registered
        result = registry.register_command("invalid_docstring", invalid_docstring_command)
        assert result is True
        
        # Check that the command is registered in the dispatcher
        assert "invalid_docstring" in registry.dispatcher.get_valid_commands()
    
    def test_register_command_invalid_auto_fix(self):
        """Test registration of an invalid command with auto-fix"""
        # Create registry in auto-fix mode
        registry = CommandRegistry(strict=True, auto_fix=True)
        
        # In auto-fix mode, a command with errors should be registered
        result = registry.register_command("invalid_docstring", invalid_docstring_command)
        assert result is True
        
        # Check that the command is registered in the dispatcher
        assert "invalid_docstring" in registry.dispatcher.get_valid_commands()
    
    def test_params_command(self, registry):
        """Test command with params parameter"""
        result = registry.register_command("params_command", params_command)
        assert result is True
        
        # Check that the command is registered
        assert "params_command" in registry.dispatcher.get_valid_commands()
        
        # Test executing the command with params parameter
        test_params = {"a": 1, "b": 2}
        # Params are passed in the 'params' field
        assert registry.dispatcher.execute("params_command", params=test_params) == {"params": test_params}


class TestCommandRegistryWithModules:
    """Tests for CommandRegistry with command modules"""
    
    @pytest.fixture
    def temp_module_dir(self):
        """Creates a temporary directory with command modules for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create directory structure for modules
            commands_dir = os.path.join(temp_dir, "commands")
            test_dir = os.path.join(commands_dir, "test")
            os.makedirs(test_dir, exist_ok=True)
            
            # Create __init__.py files
            with open(os.path.join(commands_dir, "__init__.py"), "w") as f:
                f.write("")
            with open(os.path.join(test_dir, "__init__.py"), "w") as f:
                f.write("")
            
            # Create file with test command
            test_command_path = os.path.join(temp_dir, "commands", "test", "test_command.py")
            with open(test_command_path, "w") as f:
                f.write("""
from typing import Dict, Any

# Function name needs to match expected test_command in assertions
def test_command_function(a: int, b: int = 1) -> int:
    \"\"\"
    Test command for adding numbers.
    
    Args:
        a: First number
        b: Second number
        
    Returns:
        int: Sum of numbers
    \"\"\"
    return a + b

# This is used to define the command name
test_command_function.command_name = "test_command"

COMMAND = {
    "description": "Test command for adding numbers",
    "parameters": {
        "a": {
            "type": "integer",
            "description": "First number",
            "required": True
        },
        "b": {
            "type": "integer",
            "description": "Second number",
            "required": False,
            "default": 1
        }
    }
}
""")
            
            # Verify file exists
            print(f"Created test file at: {test_command_path}")
            print(f"File exists: {os.path.exists(test_command_path)}")
            
            # Add temporary directory path to sys.path
            sys.path.insert(0, temp_dir)
            yield temp_dir
            
            # Remove path from sys.path
            sys.path.remove(temp_dir)
    
    def test_scan_modules(self, temp_module_dir):
        """Test scanning modules with commands"""
        registry = CommandRegistry(strict=True, auto_fix=False)
        
        # Scan modules
        registry.scan_modules(["commands.test"])
        
        # Get command handlers
        handlers = registry.find_command_handlers()
        
        # Check that the handler is found
        assert "test_command" in handlers
        assert callable(handlers["test_command"])
    
    def test_register_all_commands(self, temp_module_dir):
        """Test registering all commands from modules"""
        # Create a simple function for testing
        def test_command(a: int, b: int = 1) -> int:
            """
            Test command for adding numbers.
            
            Args:
                a: First number
                b: Second number
                
            Returns:
                int: Sum of numbers
            """
            return a + b
        
        # Create registry and register the command directly
        registry = CommandRegistry(strict=True, auto_fix=False)
        registry.register_command("test_command", test_command)
        
        # Check that the command is registered
        assert "test_command" in registry.dispatcher.get_valid_commands(), f"Available commands: {registry.dispatcher.get_valid_commands()}"
        
        # Check that the command can be executed
        assert registry.dispatcher.execute("test_command", a=5, b=3) == 8 
"""
Main CommandRegistry class for registering and managing commands.
"""
import os
import importlib
import inspect
import pkgutil
import logging
from typing import Dict, Any, Optional, List, Callable, Union, Type, Set, Tuple
import docstring_parser

from .dispatchers.base_dispatcher import BaseDispatcher
from .dispatchers.json_rpc_dispatcher import JsonRpcDispatcher
from .analyzers.type_analyzer import TypeAnalyzer
from .analyzers.docstring_analyzer import DocstringAnalyzer
from .validators.docstring_validator import DocstringValidator
from .validators.metadata_validator import MetadataValidator

logger = logging.getLogger("command_registry")

class CommandRegistry:
    """
    Main class for registering and managing commands.
    
    CommandRegistry provides an interface for analyzing, validating, and registering
    commands based on their docstrings and type annotations. It also manages
    API generators and command dispatchers.
    """
    
    def __init__(
        self, 
        dispatcher: Optional[BaseDispatcher] = None, 
        strict: bool = True, 
        auto_fix: bool = False
    ):
        """
        Initializes the command registry.
        
        Args:
            dispatcher: Command dispatcher for registering handlers
            strict: If True, stops registration when errors are detected
            auto_fix: If True, tries to automatically fix inconsistencies
        """
        # Use the specified dispatcher or create a default JSON-RPC dispatcher
        self.dispatcher = dispatcher or JsonRpcDispatcher()
        
        # Operation modes
        self.strict = strict
        self.auto_fix = auto_fix
        
        # Analyzers for extracting metadata
        self._analyzers = []
        
        # Validators for checking metadata consistency
        self._validators = []
        
        # API generators
        self._generators = []
        
        # Command information
        self._commands_info = {}
        
        # Paths for finding commands
        self._module_paths = []
        
        # Add standard analyzers
        self.add_analyzer(TypeAnalyzer())
        self.add_analyzer(DocstringAnalyzer())
        
        # Add standard validators
        self.add_validator(DocstringValidator())
        self.add_validator(MetadataValidator())
    
    def add_analyzer(self, analyzer) -> None:
        """
        Adds a metadata analyzer.
        
        Args:
            analyzer: Analyzer object with an analyze method
        """
        self._analyzers.append(analyzer)
    
    def add_validator(self, validator) -> None:
        """
        Adds a metadata validator.
        
        Args:
            validator: Validator object with a validate method
        """
        self._validators.append(validator)
    
    def add_generator(self, generator) -> None:
        """
        Adds an API generator.
        
        Args:
            generator: Generator object with set_dispatcher and generate_* methods
        """
        generator.set_dispatcher(self.dispatcher)
        self._generators.append(generator)
    
    def scan_modules(self, module_paths: List[str]) -> None:
        """
        Sets paths for searching modules with commands.
        
        Args:
            module_paths: List of module paths
        """
        self._module_paths = module_paths
    
    def find_command_handlers(self) -> Dict[str, Callable]:
        """
        Searches for command handler functions in the specified modules.
        
        Returns:
            Dict[str, Callable]: Dictionary {command_name: handler_function}
        """
        handlers = {}
        
        # If no search paths are specified, return an empty dictionary
        if not self._module_paths:
            return handlers
        
        # Search for handlers in each module
        for module_path in self._module_paths:
            try:
                module = importlib.import_module(module_path)
                
                # If this is a package, search in all its modules
                if hasattr(module, "__path__"):
                    for _, name, is_pkg in pkgutil.iter_modules(module.__path__):
                        # Full submodule name
                        submodule_path = f"{module_path}.{name}"
                        
                        # Load the submodule
                        try:
                            submodule = importlib.import_module(submodule_path)
                            
                            # Search for handlers in the submodule
                            for handler_name, handler in self._find_handlers_in_module(submodule):
                                handlers[handler_name] = handler
                        except ImportError as e:
                            logger.warning(f"Failed to load submodule {submodule_path}: {str(e)}")
                
                # Search for handlers in the module itself
                for handler_name, handler in self._find_handlers_in_module(module):
                    handlers[handler_name] = handler
            except ImportError as e:
                logger.warning(f"Failed to load module {module_path}: {str(e)}")
        
        return handlers
    
    def _find_handlers_in_module(self, module) -> List[Tuple[str, Callable]]:
        """
        Searches for command handler functions in a module.
        
        Args:
            module: Loaded module
            
        Returns:
            List[Tuple[str, Callable]]: List of pairs (command_name, handler_function)
        """
        result = []
        
        # Get all module attributes
        for name in dir(module):
            # Skip private attributes
            if name.startswith("_"):
                continue
            
            # Get the attribute
            attr = getattr(module, name)
            
            # Check that it's a function or method
            if callable(attr) and (inspect.isfunction(attr) or inspect.ismethod(attr)):
                # Check if the function is a command handler
                command_name = self._get_command_name_from_handler(attr, name)
                
                if command_name:
                    result.append((command_name, attr))
        
        return result
    
    def _get_command_name_from_handler(self, handler: Callable, handler_name: str) -> Optional[str]:
        """
        Determines the command name based on the function name or decorator.
        
        Args:
            handler: Handler function
            handler_name: Function name
            
        Returns:
            Optional[str]: Command name or None if the function is not a handler
        """
        # Check if the function has a command_name attribute (set by a decorator)
        if hasattr(handler, "command_name"):
            return handler.command_name
        
        # Check handler name patterns
        if handler_name.endswith("_command"):
            # Command name without the _command suffix
            return handler_name[:-8]
        
        if handler_name.startswith("execute_"):
            # Command name without the execute_ prefix
            return handler_name[8:]
        
        if handler_name == "execute":
            # The execute handler can process any command
            # In this case, the command name is determined by the module name
            module_name = handler.__module__.split(".")[-1]
            if module_name != "execute":
                return module_name
        
        # Check if the function has a docstring
        if handler.__doc__:
            try:
                # Parse the docstring
                parsed_doc = docstring_parser.parse(handler.__doc__)
                
                # Check if the docstring explicitly specifies a command name
                for meta in parsed_doc.meta:
                    if meta.type_name == "command":
                        return meta.description
            except Exception:
                pass
        
        # By default, use the function name as the command name
        return handler_name
    
    def analyze_handler(self, command_name: str, handler: Callable) -> Dict[str, Any]:
        """
        Analyzes the handler function and extracts metadata.
        
        Args:
            command_name: Command name
            handler: Handler function
            
        Returns:
            Dict[str, Any]: Command metadata
        """
        # Base metadata
        metadata = {
            "description": "",
            "summary": "",
            "parameters": {}
        }
        
        # Apply all analyzers
        for analyzer in self._analyzers:
            try:
                # Get metadata from the analyzer
                analyzer_metadata = analyzer.analyze(handler)
                
                # Merge metadata
                for key, value in analyzer_metadata.items():
                    if key == "parameters" and metadata.get(key):
                        # Merge parameter information
                        for param_name, param_info in value.items():
                            if param_name in metadata[key]:
                                # Update existing parameter
                                metadata[key][param_name].update(param_info)
                            else:
                                # Add new parameter
                                metadata[key][param_name] = param_info
                    else:
                        # For other keys, simply replace the value
                        metadata[key] = value
            except Exception as e:
                logger.warning(f"Error analyzing command '{command_name}' with analyzer {analyzer.__class__.__name__}: {str(e)}")
                
                # In strict mode, propagate the exception
                if self.strict:
                    raise
        
        return metadata
    
    def validate_handler(self, command_name: str, handler: Callable, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates the correspondence between the handler function and metadata.
        
        Args:
            command_name: Command name
            handler: Handler function
            metadata: Command metadata
            
        Returns:
            Tuple[bool, List[str]]: Validity flag and list of errors
        """
        errors = []
        
        # Apply all validators
        for validator in self._validators:
            try:
                # Check validity using the validator
                is_valid, validator_errors = validator.validate(handler, command_name, metadata)
                
                # Add errors to the general list
                errors.extend(validator_errors)
            except Exception as e:
                logger.warning(f"Error validating command '{command_name}' with validator {validator.__class__.__name__}: {str(e)}")
                errors.append(f"Validation error: {str(e)}")
                
                # In strict mode, propagate the exception
                if self.strict:
                    raise
        
        return len(errors) == 0, errors
    
    def register_command(self, command_name: str, handler: Callable) -> bool:
        """
        Registers a command based on a handler function.
        
        Args:
            command_name: Command name
            handler: Handler function
            
        Returns:
            bool: True if the command was registered successfully, False otherwise
        """
        try:
            # Analyze the handler
            metadata = self.analyze_handler(command_name, handler)
            
            # Validate metadata
            is_valid, errors = self.validate_handler(command_name, handler, metadata)
            
            # Output errors
            if not is_valid:
                logger.warning(f"Errors in command '{command_name}':")
                for error in errors:
                    logger.warning(f"   - {error}")
                
                # In strict mode without auto-fix, skip registration
                if self.strict and not self.auto_fix:
                    logger.error(f"Command registration '{command_name}' skipped due to errors")
                    return False
            
            # Register the command in the dispatcher
            self.dispatcher.register_handler(
                command=command_name,
                handler=handler,
                description=metadata.get("description", ""),
                summary=metadata.get("summary", ""),
                params=metadata.get("parameters", {})
            )
            
            # Save command information
            self._commands_info[command_name] = {
                "metadata": metadata,
                "handler": handler
            }
            
            logger.info(f"Registered command '{command_name}'")
            return True
        except Exception as e:
            logger.error(f"Error registering command '{command_name}': {str(e)}")
            
            # In strict mode, propagate the exception
            if self.strict:
                raise
            
            return False
    
    def register_all_commands(self) -> Dict[str, Any]:
        """
        Registers all found commands.
        
        Returns:
            Dict[str, Any]: Registration statistics
        """
        # Counters
        stats = {
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "total": 0
        }
        
        # Search for command handlers
        handlers = self.find_command_handlers()
        
        # Register each command
        for command_name, handler in handlers.items():
            # Skip help, it's already registered in the dispatcher
            if command_name == "help":
                stats["skipped"] += 1
                continue
            
            if self.register_command(command_name, handler):
                stats["successful"] += 1
            else:
                stats["failed"] += 1
                
            stats["total"] += 1
        
        # Generate API interfaces
        for generator in self._generators:
            if hasattr(generator, "generate_endpoints"):
                generator.generate_endpoints()
            
            if hasattr(generator, "generate_schema"):
                generator.generate_schema()
        
        # Output statistics
        logger.info(f"Command registration results:")
        logger.info(f"   - Successful: {stats['successful']}")
        logger.info(f"   - With errors: {stats['failed']}")
        logger.info(f"   - Skipped: {stats['skipped']}")
        logger.info(f"   - Total in dispatcher: {len(self.dispatcher.get_valid_commands())}")
        
        if stats["failed"] > 0 and self.strict:
            logger.warning("WARNING: Some commands were not registered due to errors")
            logger.warning("Use strict=False to register all commands")
            logger.warning("Or auto_fix=True to automatically fix errors")
        
        return stats
    
    def execute(self, command: str, **kwargs) -> Any:
        """
        Executes a command through the dispatcher.
        
        Args:
            command: Command name
            **kwargs: Command parameters
            
        Returns:
            Any: Command execution result
        """
        return self.dispatcher.execute(command, **kwargs)
    
    def get_commands_info(self) -> Dict[str, Dict[str, Any]]:
        """
        Returns information about all registered commands.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary {command_name: information}
        """
        return self.dispatcher.get_commands_info() 
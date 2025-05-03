"""
Validator for checking command metadata against function signatures.
"""
import inspect
from typing import Dict, Any, Optional, Callable, List, Tuple

class MetadataValidator:
    """
    Validator for checking handler function metadata.
    
    This class verifies that command metadata matches function signatures,
    and all parameters are correctly described.
    """
    
    def validate(self, handler: Callable, command_name: str, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Checks if metadata matches function's formal parameters.
        
        Args:
            handler: Command handler function
            command_name: Command name
            metadata: Command metadata
            
        Returns:
            Tuple[bool, List[str]]: Validity flag and list of errors
        """
        errors = []
        
        # Check presence of main fields in metadata
        if not metadata.get('description'):
            errors.append(f"Missing description for command '{command_name}'")
            
        # Get function's formal parameters
        sig = inspect.signature(handler)
        formal_params = list(sig.parameters.keys())
        
        # Skip self parameter for methods
        if formal_params and formal_params[0] == 'self':
            formal_params = formal_params[1:]
            
        # Check presence of parameters in metadata
        if 'parameters' not in metadata or not isinstance(metadata['parameters'], dict):
            errors.append(f"Parameters are missing or incorrectly defined in metadata for command '{command_name}'")
            return False, errors
            
        meta_params = metadata['parameters']
        
        # Check that all formal parameters are in metadata
        for param in formal_params:
            # Skip special parameters
            if param in ('params', 'kwargs'):
                continue
                
            if param not in meta_params:
                errors.append(f"Parameter '{param}' is not described in metadata for command '{command_name}'")
                continue
                
            param_info = meta_params[param]
            
            # Check presence of required fields for parameter
            if not isinstance(param_info, dict):
                errors.append(f"Incorrect format for parameter '{param}' description in metadata for command '{command_name}'")
                continue
                
            if 'type' not in param_info:
                errors.append(f"Type is not specified for parameter '{param}' in metadata for command '{command_name}'")
                
            if 'description' not in param_info:
                errors.append(f"Description is not specified for parameter '{param}' in metadata for command '{command_name}'")
        
        # Check that there are no extra parameters in metadata
        for param in meta_params:
            if param not in formal_params and param not in ('params', 'kwargs'):
                errors.append(f"Extra parameter '{param}' in metadata for command '{command_name}'")
        
        return len(errors) == 0, errors 
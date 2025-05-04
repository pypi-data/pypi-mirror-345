"""
Validator for checking the correspondence between docstrings and function signatures.
"""
import inspect
from typing import Dict, Any, Optional, Callable, List, Tuple, get_type_hints
import docstring_parser

class DocstringValidator:
    """
    Validator for checking the correspondence between docstrings and handler functions.
    
    This class verifies that function docstrings match their signatures,
    contain all necessary sections, and describe all parameters.
    """
    
    def validate(self, handler: Callable, command_name: str, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates the function's docstring against its formal parameters.
        
        Args:
            handler: Command handler function
            command_name: Command name
            metadata: Command metadata
            
        Returns:
            Tuple[bool, List[str]]: Validity flag and list of errors
        """
        errors = []
        
        # Get formal parameters of the function
        sig = inspect.signature(handler)
        formal_params = list(sig.parameters.keys())
        
        # Skip self parameter for methods
        if formal_params and formal_params[0] == 'self':
            formal_params = formal_params[1:]
            
        # Parse docstring
        docstring = handler.__doc__ or ""
        parsed_doc = docstring_parser.parse(docstring)
        
        # Check for function description
        if not parsed_doc.short_description and not parsed_doc.long_description:
            errors.append(f"Missing function description")
        
        # Get parameters from docstring
        doc_params = {param.arg_name: param for param in parsed_doc.params}
        
        # Check that all formal parameters are described in the docstring
        for param in formal_params:
            # Skip special parameters
            if param in ('params', 'kwargs'):
                continue
                
            if param not in doc_params:
                errors.append(f"Parameter '{param}' is not described in the function docstring")
        
        # Check for returns in docstring
        if not parsed_doc.returns and not any(t.type_name == 'Returns' for t in parsed_doc.meta):
            errors.append(f"Missing return value description in the function docstring")
        
        # Check for type annotations
        try:
            type_hints = get_type_hints(handler)
            for param in formal_params:
                # Skip special parameters
                if param in ('params', 'kwargs'):
                    continue
                    
                if param not in type_hints:
                    errors.append(f"Missing type annotation for parameter '{param}' in function {command_name}")
        except Exception as e:
            errors.append(f"Error getting type hints: {str(e)}")
        
        return len(errors) == 0, errors 
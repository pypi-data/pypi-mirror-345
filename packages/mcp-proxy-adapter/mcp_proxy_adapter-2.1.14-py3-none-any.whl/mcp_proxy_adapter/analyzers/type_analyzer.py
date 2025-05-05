"""
Type analyzer for extracting information from function type annotations.
"""
import inspect
from typing import Dict, Any, List, Optional, Callable, Union, get_origin, get_args, get_type_hints

class TypeAnalyzer:
    """
    Type analyzer for extracting information from function type annotations.
    
    This class is responsible for analyzing type annotations of command handler functions
    and converting them to JSON Schema/OpenAPI type format.
    """
    
    def __init__(self):
        # Mapping Python types to OpenAPI types
        self.type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            Any: "object",
            None: "null",
        }
    
    def analyze(self, handler: Callable) -> Dict[str, Any]:
        """
        Analyzes function type annotations and returns metadata.
        
        Args:
            handler: Handler function to analyze
            
        Returns:
            Dict[str, Any]: Metadata about parameter types and return value
        """
        result = {
            "parameters": {},
            "returns": None
        }
        
        # Get function signature
        sig = inspect.signature(handler)
        
        # Get type annotations
        type_hints = self._get_type_hints(handler)
        
        # Analyze parameters
        for param_name, param in sig.parameters.items():
            # Skip self for methods
            if param_name == 'self':
                continue
                
            # If parameter is named params, assume it's a dictionary of all parameters
            if param_name == 'params':
                continue
                
            # Determine if parameter is required
            required = param.default == inspect.Parameter.empty
            
            # Determine parameter type
            param_type = "object"  # Default type
            
            if param_name in type_hints:
                param_type = self._map_type_to_openapi(type_hints[param_name])
                
            # Create parameter metadata
            param_metadata = {
                "type": param_type,
                "required": required
            }
            
            # Add default value if exists
            if param.default != inspect.Parameter.empty:
                # Some default values cannot be serialized to JSON
                # So we convert them to string representation for such cases
                if param.default is None or isinstance(param.default, (str, int, float, bool, list, dict)):
                    param_metadata["default"] = param.default
            
            # Add parameter to metadata
            result["parameters"][param_name] = param_metadata
        
        # Analyze return value
        if 'return' in type_hints:
            result["returns"] = self._map_type_to_openapi(type_hints['return'])
        
        return result
    
    def _get_type_hints(self, handler: Callable) -> Dict[str, Any]:
        """
        Gets type annotations of a function.
        
        Args:
            handler: Handler function
            
        Returns:
            Dict[str, Any]: Type annotations
        """
        try:
            return get_type_hints(handler)
        except Exception:
            # If failed to get annotations via get_type_hints,
            # extract them manually from __annotations__
            return getattr(handler, "__annotations__", {})
    
    def _map_type_to_openapi(self, type_hint: Any) -> Union[str, Dict[str, Any]]:
        """
        Converts Python type to OpenAPI type.
        
        Args:
            type_hint: Python type
            
        Returns:
            Union[str, Dict[str, Any]]: OpenAPI type string representation or schema
        """
        # Check for None
        if type_hint is None:
            return "null"
        
        # Handle primitive types
        if type_hint in self.type_map:
            return self.type_map[type_hint]
        
        # Check for generic types
        origin = get_origin(type_hint)
        if origin is not None:
            # Handle List[X], Dict[X, Y], etc.
            if origin in (list, List):
                args = get_args(type_hint)
                if args:
                    item_type = self._map_type_to_openapi(args[0])
                    return {
                        "type": "array",
                        "items": item_type if isinstance(item_type, dict) else {"type": item_type}
                    }
                return "array"
            elif origin in (dict, Dict):
                # For dict we just return object, as OpenAPI
                # doesn't have a direct equivalent for Dict[X, Y]
                return "object"
            elif origin is Union:
                # For Union we take the first type that is not None
                args = get_args(type_hint)
                for arg in args:
                    if arg is not type(None):
                        return self._map_type_to_openapi(arg)
                return "object"
        
        # Default to object
        return "object" 
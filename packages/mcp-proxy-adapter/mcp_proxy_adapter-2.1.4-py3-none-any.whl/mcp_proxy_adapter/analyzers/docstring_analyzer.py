"""
Docstring analyzer for extracting information from function documentation.
"""
import inspect
from typing import Dict, Any, Optional, Callable, List, Tuple
import docstring_parser

class DocstringAnalyzer:
    """
    Docstring analyzer for extracting metadata from function documentation.
    
    This class is responsible for analyzing command handler function docstrings
    and extracting function descriptions, parameters, and return values.
    """
    
    def analyze(self, handler: Callable) -> Dict[str, Any]:
        """
        Analyzes function docstring and returns metadata.
        
        Args:
            handler: Handler function to analyze
            
        Returns:
            Dict[str, Any]: Metadata extracted from docstring
        """
        result = {
            "description": "",
            "summary": "",
            "parameters": {},
            "returns": {
                "description": ""
            }
        }
        
        # Get function signature
        sig = inspect.signature(handler)
        
        # Get docstring
        docstring = handler.__doc__ or ""
        
        # Parse docstring
        try:
            parsed_doc = docstring_parser.parse(docstring)
            
            # Extract general function description
            if parsed_doc.short_description:
                result["summary"] = parsed_doc.short_description
                result["description"] = parsed_doc.short_description
                
            if parsed_doc.long_description:
                # If both short and long descriptions exist, combine them
                if result["description"]:
                    result["description"] = f"{result['description']}\n\n{parsed_doc.long_description}"
                else:
                    result["description"] = parsed_doc.long_description
            
            # Extract parameter information
            for param in parsed_doc.params:
                param_name = param.arg_name
                param_desc = param.description or f"Parameter {param_name}"
                param_type = None
                
                # If parameter type is specified in docstring, use it
                if param.type_name:
                    param_type = self._parse_type_from_docstring(param.type_name)
                
                # Add parameter to metadata
                if param_name not in result["parameters"]:
                    result["parameters"][param_name] = {}
                    
                result["parameters"][param_name]["description"] = param_desc
                
                if param_type:
                    result["parameters"][param_name]["type"] = param_type
            
            # Extract return value information
            if parsed_doc.returns:
                result["returns"]["description"] = parsed_doc.returns.description or "Return value"
                
                if parsed_doc.returns.type_name:
                    result["returns"]["type"] = self._parse_type_from_docstring(parsed_doc.returns.type_name)
        
        except Exception as e:
            # In case of parsing error, use docstring as is
            if docstring:
                result["description"] = docstring.strip()
        
        # Fill parameter information from signature if not found in docstring
        for param_name, param in sig.parameters.items():
            # Skip self for methods
            if param_name == 'self':
                continue
                
            # If parameter not yet added to metadata, add it
            if param_name not in result["parameters"]:
                result["parameters"][param_name] = {
                    "description": f"Parameter {param_name}"
                }
            
            # Determine if parameter is required
            required = param.default == inspect.Parameter.empty
            result["parameters"][param_name]["required"] = required
            
            # Add default value if exists
            if param.default != inspect.Parameter.empty:
                # Some default values cannot be serialized to JSON
                # So we check if the value can be serialized
                if param.default is None or isinstance(param.default, (str, int, float, bool, list, dict)):
                    result["parameters"][param_name]["default"] = param.default
        
        return result
    
    def validate(self, handler: Callable) -> Tuple[bool, List[str]]:
        """
        Validates that function docstring matches its formal parameters.
        
        Args:
            handler: Command handler function
            
        Returns:
            Tuple[bool, List[str]]: Validity flag and list of errors
        """
        errors = []
        
        # Get function formal parameters
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
        
        # Check that all formal parameters are described in docstring
        for param in formal_params:
            if param not in doc_params and param != 'params':  # 'params' is special case, can be dictionary of all parameters
                errors.append(f"Parameter '{param}' not described in function docstring")
        
        # Check for returns in docstring
        if not parsed_doc.returns and not any(t.type_name == 'Returns' for t in parsed_doc.meta):
            errors.append(f"Missing return value description in function docstring")
        
        return len(errors) == 0, errors
    
    def _parse_type_from_docstring(self, type_str: str) -> str:
        """
        Parses type from string representation in docstring.
        
        Args:
            type_str: String representation of type
            
        Returns:
            str: Type in OpenAPI format
        """
        # Simple mapping of string types to OpenAPI types
        type_map = {
            "str": "string",
            "string": "string",
            "int": "integer",
            "integer": "integer",
            "float": "number",
            "number": "number",
            "bool": "boolean",
            "boolean": "boolean",
            "list": "array",
            "array": "array",
            "dict": "object",
            "object": "object",
            "none": "null",
            "null": "null",
        }
        
        # Convert to lowercase and remove spaces
        cleaned_type = type_str.lower().strip()
        
        # Check for simple types
        if cleaned_type in type_map:
            return type_map[cleaned_type]
        
        # Check for List[X]
        if cleaned_type.startswith("list[") or cleaned_type.startswith("array["):
            return "array"
        
        # Check for Dict[X, Y]
        if cleaned_type.startswith("dict[") or cleaned_type.startswith("object["):
            return "object"
        
        # Default to object
        return "object" 
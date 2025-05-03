"""
Combined OpenAPI schema for REST and RPC API.
Provides the get_openapi_schema function that returns the complete OpenAPI schema.
"""
from typing import Dict, Any

from .rest_schema import get_rest_schema
from .rpc_generator import generate_rpc_schema

__all__ = ["get_openapi_schema"]


def get_openapi_schema() -> Dict[str, Any]:
    """
    Gets the complete OpenAPI schema that includes both REST and RPC interfaces.
    
    Returns:
        Dict[str, Any]: Complete OpenAPI schema
    """
    # Get the base REST schema
    openapi_schema = get_rest_schema()
    
    # Generate RPC schema based on REST schema
    rpc_schema = generate_rpc_schema(openapi_schema)
    
    # Add /cmd endpoint from RPC schema to the general schema
    openapi_schema["paths"].update(rpc_schema["paths"])
    
    # Merge schema components
    for component_type, components in rpc_schema["components"].items():
        if component_type not in openapi_schema["components"]:
            openapi_schema["components"][component_type] = {}
        for component_name, component in components.items():
            # Avoid component duplication
            if component_name not in openapi_schema["components"][component_type]:
                openapi_schema["components"][component_type][component_name] = component
    
    return openapi_schema 
"""
Data models for MCP Proxy Adapter.
"""
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

class JsonRpcRequest(BaseModel):
    """Base model for JSON-RPC requests."""
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    method: str = Field(..., description="Method name to call")
    params: Dict[str, Any] = Field({}, description="Method parameters")
    id: Optional[Union[str, int]] = Field(None, description="Request identifier")

class JsonRpcResponse(BaseModel):
    """Base model for JSON-RPC responses."""
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    result: Optional[Any] = Field(None, description="Method execution result")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information")
    id: Optional[Union[str, int]] = Field(None, description="Request identifier")
    
class CommandInfo(BaseModel):
    """Command information model."""
    name: str = Field(..., description="Command name")
    description: str = Field("", description="Command description")
    summary: Optional[str] = Field(None, description="Brief description")
    parameters: Dict[str, Dict[str, Any]] = Field({}, description="Command parameters")
    returns: Optional[Dict[str, Any]] = Field(None, description="Return value information")

class CommandParameter(BaseModel):
    """Command parameter model."""
    type: str = Field(..., description="Parameter type")
    description: str = Field("", description="Parameter description")
    required: bool = Field(False, description="Whether the parameter is required")
    default: Optional[Any] = Field(None, description="Default value")
    enum: Optional[List[Any]] = Field(None, description="Possible values for enumeration")

class MCPProxyTool(BaseModel):
    """Tool model for MCPProxy."""
    name: str = Field(..., description="Tool name") 
    description: str = Field("", description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters schema")

class MCPProxyConfig(BaseModel):
    """Configuration model for MCPProxy."""
    version: str = Field("1.0", description="Configuration version")
    tools: List[MCPProxyTool] = Field([], description="List of tools")
    routes: List[Dict[str, Any]] = Field([], description="Routes configuration") 
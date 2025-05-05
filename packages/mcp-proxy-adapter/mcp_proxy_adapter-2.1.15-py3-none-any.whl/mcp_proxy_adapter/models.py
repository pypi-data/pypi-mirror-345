"""
Data models for MCP Proxy Adapter.
"""
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

class JsonRpcRequest(BaseModel):
    """Base model for JSON-RPC requests."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    method: str = Field(..., description="Method name to call")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method parameters")
    id: Optional[Union[str, int]] = Field(default=None, description="Request identifier")

class JsonRpcResponse(BaseModel):
    """Base model for JSON-RPC responses."""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    result: Optional[Any] = Field(default=None, description="Method execution result")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information")
    id: Optional[Union[str, int]] = Field(default=None, description="Request identifier")
    
class CommandInfo(BaseModel):
    """Command information model."""
    name: str = Field(..., description="Command name")
    description: str = Field(default="", description="Command description")
    summary: Optional[str] = Field(default=None, description="Brief description")
    parameters: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Command parameters")
    returns: Optional[Dict[str, Any]] = Field(default=None, description="Return value information")

class CommandParameter(BaseModel):
    """Command parameter model."""
    type: str = Field(..., description="Parameter type")
    description: str = Field(default="", description="Parameter description")
    required: bool = Field(default=False, description="Whether the parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value")
    enum: Optional[List[Any]] = Field(default=None, description="Possible values for enumeration")

class MCPProxyTool(BaseModel):
    """Tool model for MCPProxy."""
    name: str = Field(..., description="Tool name") 
    description: str = Field(default="", description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters schema")

class MCPProxyConfig(BaseModel):
    """Configuration model for MCPProxy."""
    version: str = Field(default="1.0", description="Configuration version")
    tools: List[MCPProxyTool] = Field(default_factory=list, description="List of tools")
    routes: List[Dict[str, Any]] = Field(default_factory=list, description="Routes configuration") 
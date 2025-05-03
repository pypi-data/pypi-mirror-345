"""
MCP Proxy Adapter
=================

Adapter for integrating Command Registry with MCP Proxy to use commands as tools
for AI models.
"""

# Package version
__version__ = '1.0.0'

# Public API
from .adapter import MCPProxyAdapter, configure_logger
from .models import MCPProxyConfig, MCPProxyTool, CommandInfo, CommandParameter

__all__ = ['MCPProxyAdapter', 'configure_logger', 'MCPProxyConfig', 'MCPProxyTool', 
           'CommandInfo', 'CommandParameter'] 
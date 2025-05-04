"""
LlamaIndex integration for MCP Server tools.
"""
from typing import List, Dict, Any, Optional, Callable, Union
import functools

from shivonai.core.mcp_client import MCPClient
from shivonai.utils.helpers import create_tool_description


def llamaindex_toolkit(auth_token: str, base_url: str = "https://mcp-server.shivonai.com") -> Dict[str, Any]:
    """Create LlamaIndex tools from MCP Server.
    
    Args:
        auth_token: Authentication token for MCP Server
        base_url: URL of the MCP server
        
    Returns:
        Dictionary of LlamaIndex tool functions
    """
    try:
        # Import from llama_index.core for newer versions
        try:
            from llama_index.core.tools import FunctionTool
        except ImportError:
            # Fallback for older versions
            from llama_index.tools import FunctionTool
    except ImportError:
        raise ImportError(
            "Could not import llama_index. "
            "Please install it with `pip install llama-index`."
        )

    client = MCPClient(base_url)
    client.authenticate(auth_token)
    available_tools = client.list_tools()
    
    llamaindex_tools = {}
    
    for tool_info in available_tools:
        # Create a function that will handle the tool
        def make_tool_func(name, description, parameters):
            def tool_func(**kwargs):
                return client.call_tool(name, kwargs)
            
            # Update function metadata for better integration with LlamaIndex
            tool_func.__name__ = name
            
            # Create full description with parameters
            full_description = create_tool_description(name, description, parameters)
            tool_func.__doc__ = full_description
            
            return tool_func
        
        # Create the tool function
        func = make_tool_func(
            tool_info["name"],
            tool_info.get("description", ""),
            tool_info.get("parameters", [])
        )
        
        # Create the full description including parameters
        full_description = create_tool_description(
            tool_info["name"],
            tool_info.get("description", ""),
            tool_info.get("parameters", [])
        )
        
        # Create the LlamaIndex FunctionTool
        llamaindex_tool = FunctionTool.from_defaults(
            name=tool_info["name"],
            description=full_description,
            fn=func,
        )
        
        llamaindex_tools[tool_info["name"]] = llamaindex_tool
    
    return llamaindex_tools
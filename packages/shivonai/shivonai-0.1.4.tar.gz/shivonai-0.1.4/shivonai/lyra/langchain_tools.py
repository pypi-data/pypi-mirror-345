"""
LangChain integration for MCP Server tools.
"""
from typing import List, Dict, Any, Optional
from langchain.tools import Tool, StructuredTool
from pydantic import create_model, Field, BaseModel
import json
from shivonai.core.mcp_client import MCPClient
from shivonai.utils.helpers import parse_tool_parameters, create_tool_description

def create_tool_description(name: str, description: str, parameters: List[Dict[str, Any]]) -> str:
    """Create a detailed description for a tool including its parameters."""
    param_desc = ""
    if parameters:
        param_desc = "\nParameters:\n"
        for param in parameters:
            param_desc += f"- {param['name']}: {param.get('description', 'No description')}"
            if param.get('required', False):
                param_desc += " (Required)"
            param_desc += "\n"
    
    return f"{description}{param_desc}"

def create_args_schema(parameters: List[Dict[str, Any]]):
    """Create a Pydantic model for tool arguments."""
    fields = {}
    for param in parameters:
        param_name = param["name"]
        required = param.get("required", False)
        description = param.get("description", "")
        
        # Default to string type, but you can expand this logic
        # to handle different parameter types
        if required:
            fields[param_name] = (str, Field(..., description=description))
        else:
            fields[param_name] = (str, Field(None, description=description))
    
    return create_model("ArgsSchema", **fields)


def langchain_toolkit(auth_token: str, base_url: str = "https://mcp-server.shivonai.com") -> List[Tool]:
    """Create LangChain tools from MCP Server.
    
    This function creates LangChain tools from available tools in MCP Server,
    using StructuredTool for multi-parameter tools to avoid the "Too many arguments" error.
    
    Args:
        auth_token: Authentication token for MCP Server
        base_url: URL of the MCP server
        
    Returns:
        List of LangChain tools
    """
    client = MCPClient(base_url)
    client.authenticate(auth_token)
    available_tools = client.list_tools()
    
    langchain_tools = []
    
    for tool_info in available_tools:
        name = tool_info["name"]
        description = tool_info.get("description", "")
        parameters = tool_info.get("parameters", [])
        
        if len(parameters) == 0:
            # For tools with no parameters, create a function that ignores inputs
            def create_no_param_func(tool_name, client_instance):
                def no_param_func(*args, **kwargs):
                    """Function that ignores inputs and calls the tool with empty params."""
                    # Ignore any arguments and just call the tool with empty params
                    return client_instance.call_tool(tool_name, {})
                return no_param_func
            
            tool_func = create_no_param_func(name, client)
            
            langchain_tool = Tool(
                name=name,
                description=create_tool_description(name, description, parameters),
                func=tool_func
            )
            
        elif len(parameters) == 1:
            # For tools with exactly 1 parameter, create a special handler
            param = parameters[0]
            param_name = param["name"]
            
            def create_single_param_func(tool_name, client_instance, param_key):
                def single_param_func(tool_input):
                    """Function that handles a single parameter tool."""
                    # Handle different ways the parameter might be provided
                    if isinstance(tool_input, dict):
                        # If it's a dict, check if it has the expected parameter name
                        if param_key in tool_input:
                            # Use the value of the expected parameter
                            return client_instance.call_tool(tool_name, {param_key: tool_input[param_key]})
                        elif len(tool_input) == 1:
                            # If there's only one value in the dict, use that regardless of key
                            # This handles cases where agent uses "__arg1" or other unexpected keys
                            value = next(iter(tool_input.values()))
                            return client_instance.call_tool(tool_name, {param_key: value})
                        else:
                            # If multiple values, just pass the whole dict
                            return client_instance.call_tool(tool_name, tool_input)
                    else:
                        # If it's not a dict, use it directly as the parameter value
                        return client_instance.call_tool(tool_name, {param_key: tool_input})
                
                return single_param_func
            
            # Create the tool with the single parameter handler
            tool_func = create_single_param_func(name, client, param_name)
            
            langchain_tool = Tool(
                name=name,
                description=create_tool_description(name, description, parameters),
                func=tool_func
            )
            
        else:
            # For tools with multiple parameters, create a Pydantic model and use StructuredTool
            # First, create a proper Pydantic model for the tool's parameters
            fields = {}
            for param in parameters:
                param_name = param["name"]
                param_desc = param.get("description", "")
                param_required = param.get("required", False)
                
                if param_required:
                    fields[param_name] = (str, Field(..., description=param_desc))
                else:
                    fields[param_name] = (str, Field(None, description=param_desc))
            
            # Create the model dynamically
            model_name = f"{name}Schema"
            args_schema = create_model(model_name, **fields)
            
            # Create a function that will handle multiple parameters
            def create_multi_param_func(tool_name, client_instance):
                def multi_param_func(**kwargs):
                    """Function that takes multiple parameters and passes them to the tool."""
                    return client_instance.call_tool(tool_name, kwargs)
                return multi_param_func
            
            multi_param_func = create_multi_param_func(name, client)
            
            # Create a StructuredTool with the schema
            langchain_tool = StructuredTool(
                name=name,
                description=create_tool_description(name, description, parameters),
                func=multi_param_func,
                args_schema=args_schema
            )
        
        langchain_tools.append(langchain_tool)
    
    return langchain_tools
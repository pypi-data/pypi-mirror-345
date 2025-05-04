"""
CrewAI integration for MCP Server tools.
"""
from typing import List, Dict, Any, Optional, Type, Union, Annotated
from pydantic import BaseModel, Field

from shivonai.core.mcp_client import MCPClient
from shivonai.utils.helpers import parse_tool_parameters, create_tool_description


def crew_toolkit(auth_token: str, base_url: str = "https://mcp-server.shivonai.com") -> List[Any]:
    """Create CrewAI tools from MCP Server.
    
    Args:
        auth_token: Authentication token for MCP Server
        base_url: URL of the MCP server
        
    Returns:
        List of CrewAI tools
    """
    try:
        from crewai.tools import BaseTool
    except ImportError:
        raise ImportError(
            "Could not import crewai. "
            "Please install it with `pip install crewai`."
        )

    client = MCPClient(base_url)
    client.authenticate(auth_token)
    available_tools = client.list_tools()
    
    crew_tools = []
    
    # Create a tool class for each available MCP tool
    for tool_info in available_tools:
        tool_name = tool_info["name"]
        tool_description = tool_info.get("description", "")
        tool_parameters = tool_info.get("parameters", [])
        
        # Create the full description with parameters
        full_description = create_tool_description(
            tool_name,
            tool_description,
            tool_parameters
        )
        
        # Create input schema class if there are parameters
        input_schema = None
        if tool_parameters:
            # Create dynamic input schema class
            input_schema_attrs = {
                "__doc__": f"Input schema for {tool_name} tool.",
                "__annotations__": {}  # This is important for Pydantic
            }
            
            # Add fields for each parameter with type annotations
            for param in tool_parameters:
                param_name = param["name"]
                param_desc = param.get("description", "")
                required = param.get("required", False)
                
                # Add type annotation to __annotations__ dict
                input_schema_attrs["__annotations__"][param_name] = str
                
                # Define Field with or without default value based on required flag
                if required:
                    input_schema_attrs[param_name] = Field(..., description=param_desc)
                else:
                    input_schema_attrs[param_name] = Field(None, description=param_desc)
            
            # Create the dynamic input schema class
            input_schema = type(
                f"{tool_name.capitalize()}ToolInput",
                (BaseModel,),
                input_schema_attrs
            )
        
        # Define the _run method
        def create_run_method(name=tool_name):
            if input_schema:
                # For tools with input schema
                def _run(self, **kwargs):
                    return client.call_tool(name, kwargs)
            else:
                # For tools without input schema
                def _run(self, input_str=""):
                    args = parse_tool_parameters(input_str)
                    return client.call_tool(name, args)
            
            return _run
        
        # Create a custom tool class that inherits from BaseTool
        class CustomToolClass(BaseTool):
            name: str = tool_name
            description: str = full_description
            
            # Add args_schema if we have an input schema
            if input_schema:
                args_schema: Type[BaseModel] = input_schema
            
            # Add the _run method
            _run = create_run_method()
            
        # Instantiate the tool
        tool_instance = CustomToolClass()
        crew_tools.append(tool_instance)
    
    return crew_tools
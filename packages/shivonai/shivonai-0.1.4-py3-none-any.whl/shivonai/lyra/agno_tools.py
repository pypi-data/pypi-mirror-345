"""
Agno integration for MCP Server tools.
"""
from typing import List, Dict, Any, Optional, Callable, Union
import functools
import inspect
import json

from shivonai.core.mcp_client import MCPClient
from shivonai.utils.helpers import create_tool_description


def convert_parameters_to_schema(parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Convert MCP tool parameters to JSON Schema format.
    
    This converts the MCP parameter format to a format compatible with JSON Schema
    that both OpenAI and Claude can understand.
    
    Args:
        parameters: List of parameter definitions from MCP
        
    Returns:
        JSON Schema object
    """
    properties = {}
    required = []
    
    for param in parameters:
        name = param.get("name", "")
        description = param.get("description", "")
        param_type = param.get("type", "string")
        required_flag = param.get("required", False)
        
        # Map MCP parameter types to JSON Schema types
        if param_type == "integer":
            json_type = "integer"
        elif param_type == "number":
            json_type = "number"
        elif param_type == "boolean":
            json_type = "boolean"
        elif param_type == "array":
            json_type = "array"
            # For arrays, we'd need to define items schema, defaulting to strings
            properties[name] = {
                "type": json_type,
                "description": description,
                "items": {"type": "string"}
            }
            continue
        else:  # Default to string
            json_type = "string"
        
        # Add property definition
        properties[name] = {
            "type": json_type,
            "description": description
        }
        
        # Add to required list if needed
        if required_flag:
            required.append(name)
    
    # Create the full schema
    schema = {
        "type": "object",
        "properties": properties
    }
    
    # Only add required field if there are required parameters
    if required:
        schema["required"] = required
    
    return schema


def agno_toolkit(auth_token: str, base_url: str = "https://mcp-server.shivonai.com") -> Dict[str, Callable]:
    """Create Agno tools from MCP Server.
    
    Args:
        auth_token: Authentication token for MCP Server
        base_url: URL of the MCP server
        
    Returns:
        Dictionary of Agno tool functions
    """
    try:
        # Import required Agno modules
        from agno.agent import Agent
    except ImportError:
        raise ImportError(
            "Could not import agno. "
            "Please install it with `pip install agno`."
        )

    client = MCPClient(base_url)
    client.authenticate(auth_token)
    available_tools = client.list_tools()
    
    # Dictionary to store our created tools
    agno_tools = {}
    
    # Create functions for each MCP tool
    for tool_info in available_tools:
        tool_name = tool_info["name"]
        tool_description = tool_info.get("description", "")
        tool_parameters = tool_info.get("parameters", [])
        
        # Convert parameters to JSON Schema for tool definition
        schema = convert_parameters_to_schema(tool_parameters)
        
        # Create the function that will handle the tool call
        def make_tool_func(name, description, parameters, schema):
            def tool_func(**kwargs):
                # Call the MCP tool and get the response
                response = client.call_tool(name, kwargs)
                
                # Convert the response to a string if it's a list or dictionary
                # This is important for compatibility with Agno and model expectations
                if isinstance(response, (list, dict)):
                    return json.dumps(response, indent=2)
                return response
            
            # Create full description with parameters for the docstring
            full_description = create_tool_description(name, description, parameters)
            tool_func.__doc__ = full_description
            tool_func.__name__ = name
            
            # Add JSON schema as an attribute for models that need it (like Claude)
            tool_func.schema = schema
            
            return tool_func
        
        # Create the function for this specific tool
        func = make_tool_func(tool_name, tool_description, tool_parameters, schema)
        
        # Store the function in our dictionary
        agno_tools[tool_name] = func
    
    return agno_tools


def create_agno_agent_with_mcp_tools(
    auth_token: str, 
    base_url: str = "https://mcp-server.shivonai.com",
    model: Any = None,
    instructions: Union[str, List[str]] = None,
    description: str = None,
    show_tool_calls: bool = True,
    markdown: bool = True
) -> Any:
    """Create an Agno agent with MCP tools.
    
    Args:
        auth_token: Authentication token for MCP Server
        base_url: URL of the MCP server
        model: The LLM model to use with the agent
        instructions: Instructions for the agent
        description: Description of the agent
        show_tool_calls: Whether to show tool calls in the agent's response
        markdown: Whether to render responses as markdown
        
    Returns:
        An Agno agent with MCP tools
    """
    try:
        from agno.agent import Agent
    except ImportError:
        raise ImportError("Could not import agno. Please install it with `pip install agno`.")
    
    # Get MCP tools as functions
    tools_dict = agno_toolkit(auth_token, base_url)
    tools = list(tools_dict.values())
    
    # Print available tools for debugging
    tool_names = [tool.__name__ for tool in tools]
    print(f"Available MCP tools for Agno: {tool_names}")
    
    # Check if we're using Claude model to add schema information
    is_claude_model = False
    if model is not None:
        model_id = getattr(model, "id", "")
        is_claude_model = "claude" in model_id.lower() or "anthropic" in str(model.__class__).lower()
    
    # Add schema information for Claude models
    if is_claude_model:
        # We need to configure the tools for Claude
        # Use the approach according to Agno's implementation for Claude
        from agno.models.aws import Claude
        if isinstance(model, Claude):
            # For Bedrock Claude, set tool schemas
            tool_schemas = []
            for tool in tools:
                tool_schemas.append({
                    "name": tool.__name__,
                    "description": tool.__doc__,
                    "input_schema": tool.schema
                })
            # Set the tools on the Claude model
            model.tool_schemas = tool_schemas
    
    # Create an Agno agent with the tools
    agent = Agent(
        model=model,
        instructions=instructions,
        description=description,
        tools=tools,
        show_tool_calls=show_tool_calls,
        markdown=markdown
    )
    
    return agent


# Function to get the available tools
def get_available_mcp_tools(auth_token: str, base_url: str = "https://mcp-server.shivonai.com") -> List[str]:
    """Get a list of available MCP tool names.
    
    Args:
        auth_token: Authentication token for MCP Server
        base_url: URL of the MCP server
        
    Returns:
        List of tool names
    """
    tools_dict = agno_toolkit(auth_token, base_url)
    return list(tools_dict.keys())
"""
Helper functions for ShivonAI package.
"""
import json
from typing import Dict, Any, List, Optional


def parse_tool_parameters(arg_string: str) -> Dict[str, Any]:
    """Parse tool parameters from a string.
    
    Args:
        arg_string: String representation of tool parameters
        
    Returns:
        Dictionary of tool parameters
    """
    if not arg_string or not arg_string.strip():
        return {}
    
    try:
        # Try to parse as JSON
        return json.loads(arg_string)
    except json.JSONDecodeError:
        # If not valid JSON, parse as key=value pairs
        args = {}
        pairs = arg_string.split(',')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                args[key.strip()] = value.strip()
        return args


def format_parameter_description(parameters: List[Dict[str, Any]]) -> str:
    """Format parameter description for tools.
    
    Args:
        parameters: List of parameter definitions
        
    Returns:
        Formatted parameter description
    """
    if not parameters:
        return ""
    
    param_desc = "\nParameters:\n"
    for param in parameters:
        required = "Required" if param.get("required", False) else "Optional"
        param_type = param.get("type", "any")
        description = param.get("description", "")
        param_desc += f"- {param['name']} ({param_type}): {description} [{required}]\n"
    
    return param_desc


def create_tool_description(name: str, description: str, parameters: List[Dict[str, Any]]) -> str:
    """Create a full tool description including parameters.
    
    Args:
        name: Tool name
        description: Tool description
        parameters: List of parameter definitions
        
    Returns:
        Full tool description
    """
    return f"{description}{format_parameter_description(parameters)}"
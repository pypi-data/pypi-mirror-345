"""
MCP Client for connecting with MCP Server.
"""
import requests
from typing import Dict, List, Any, Optional

class MCPClient:
    """Client to connect with MCP Server."""
    
    def __init__(self, base_url: str = "https://mcp-server.shivonai.com"):
        """Initialize MCP Client.
        
        Args:
            base_url: URL of the MCP server
        """
        self.base_url = base_url
        self.token = None
        self.available_tools = []
    
    def authenticate(self, token: str) -> Dict[str, Any]:
        """Authenticate with the MCP server using a token.
        
        Args:
            token: Authentication token
            
        Returns:
            Server information
        """
        self.token = token
        response = requests.post(
            f"{self.base_url}/initialize",
            json={"auth_token": token}
        )
        response.raise_for_status()
        data = response.json()
        return data["server_info"]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of tools available with current authentication.
        
        Returns:
            List of available tools
        """
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/tools/list",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        self.available_tools = data["tools"]
        return self.available_tools
    
    def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server.
        
        Args:
            tool_name: Name of the tool to call
            parameters: Parameters to pass to the tool
            
        Returns:
            Result of the tool call
        """
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/tools/call",
            headers=headers,
            json={"name": tool_name, "parameters": parameters}
        )
        response.raise_for_status()
        data = response.json()
        return data["result"]
import unittest
from unittest.mock import patch, MagicMock
from shivonai.core.mcp_client import MCPClient


class TestMCPClient(unittest.TestCase):
    """Test cases for MCPClient class."""
    
    def setUp(self):
        """Set up test environment."""
        self.client = MCPClient(base_url="https://mcp-server.shivonai.com")
        self.test_token = "test-token"
    
    @patch('requests.post')
    def test_authenticate(self, mock_post):
        """Test authenticate method."""
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"server_info": {"name": "Test Server", "version": "1.0"}}
        mock_post.return_value = mock_response
        
        # Call the method
        result = self.client.authenticate(self.test_token)
        
        # Assert
        mock_post.assert_called_once_with(
            "https://mcp-server.shivonai.com/initialize",
            json={"auth_token": self.test_token}
        )
        self.assertEqual(result, {"name": "Test Server", "version": "1.0"})
        self.assertEqual(self.client.token, self.test_token)
    
    @patch('requests.get')
    def test_list_tools(self, mock_get):
        """Test list_tools method."""
        # Set token
        self.client.token = self.test_token
        
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "tools": [
                {"name": "tool1", "description": "Test Tool 1"},
                {"name": "tool2", "description": "Test Tool 2"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Call the method
        result = self.client.list_tools()
        
        # Assert
        mock_get.assert_called_once_with(
            "https://mcp-server.shivonai.com/tools/list",
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "tool1")
        self.assertEqual(result[1]["name"], "tool2")
    
    def test_list_tools_not_authenticated(self):
        """Test list_tools method when not authenticated."""
        with self.assertRaises(ValueError) as context:
            self.client.list_tools()
        
        self.assertTrue("Not authenticated. Call authenticate() first." in str(context.exception))
    
    @patch('requests.post')
    def test_call_tool(self, mock_post):
        """Test call_tool method."""
        # Set token
        self.client.token = self.test_token
        
        # Configure mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "Tool executed successfully"}
        mock_post.return_value = mock_response
        
        # Call the method
        result = self.client.call_tool("test_tool", {"param1": "value1"})
        
        # Assert
        mock_post.assert_called_once_with(
            "https://mcp-server.shivonai.com/tools/call",
            headers={"Authorization": f"Bearer {self.test_token}"},
            json={"name": "test_tool", "parameters": {"param1": "value1"}}
        )
        self.assertEqual(result, "Tool executed successfully")
    
    def test_call_tool_not_authenticated(self):
        """Test call_tool method when not authenticated."""
        with self.assertRaises(ValueError) as context:
            self.client.call_tool("test_tool", {"param1": "value1"})
        
        self.assertTrue("Not authenticated. Call authenticate() first." in str(context.exception))


if __name__ == '__main__':
    unittest.main()
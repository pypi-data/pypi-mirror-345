# shivonai/__init__.py
"""
ShivonAI Package - Tools for connecting AI agents with MCP server
"""
from shivonai.core.mcp_client import MCPClient

__version__ = "0.1.4"

# shivonai/core/__init__.py
"""
Core components for ShivonAI package.
"""
from shivonai.core.mcp_client import MCPClient

# shivonai/lyra/__init__.py
"""
Lyra module for integration with different AI agent frameworks.
"""
from shivonai.lyra.langchain_tools import langchain_toolkit
from shivonai.lyra.llamaindex_tools import llamaindex_toolkit
from shivonai.lyra.crew_tools import crew_toolkit
from shivonai.lyra.agno_tools import agno_toolkit

# shivonai/utils/__init__.py
"""
Utility functions for ShivonAI package.
"""
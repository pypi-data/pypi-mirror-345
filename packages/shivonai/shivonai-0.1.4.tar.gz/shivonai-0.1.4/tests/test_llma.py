
# tested on openai models and bedrock claude models
# work with both types of models models. 

# ## Openai usage
# import os

# from llama_index.llms.openai import OpenAI
# from llama_index.core.agent import ReActAgent
# from shivonai.lyra import llamaindex_toolkit

# # Set up OpenAI API key - you'll need this to use OpenAI models with LlamaIndex
# os.environ["OPENAI_API_KEY"] = "openai_api_key"

# # Your MCP server authentication details
# MCP_AUTH_TOKEN = "shivonai_auth_token"


# def main():
#     """Test LlamaIndex integration with ShivonAI."""
#     print("Testing LlamaIndex integration with ShivonAI...")
    
#     # Get LlamaIndex tools from your MCP server
#     tools = llamaindex_toolkit(MCP_AUTH_TOKEN)
#     print(f"Found {len(tools)} MCP tools for LlamaIndex:")
    
#     for name, tool in tools.items():
#         print(f"  - {name}: {tool.metadata.description[:60]}...")
    
#     # Create a LlamaIndex agent with these tools
#     llm = OpenAI(model="gpt-4")
    
#     # Convert tools dictionary to a list
#     tool_list = list(tools.values())
    
#     # Create the ReAct agent
#     agent = ReActAgent.from_tools(
#         tools=tool_list,
#         llm=llm,
#         verbose=True
#     )
    
#     # Test the agent with a simple query that should use one of your tools
#     # Replace this with a query that's relevant to your tools
#     query = "what listings I have?"
    
#     print("\nTesting agent with query:", query)
#     response = agent.chat(query)
    
#     print("\nAgent response:")
#     print(response)

# if __name__ == "__main__":
#     main()


# bedrock use
"""
Test script for LlamaIndex integration with ShivonAI package.
This demonstrates how to use the llamaindex_toolkit to create and use tools with AWS Bedrock's Claude model.
"""
import os
import boto3
from llama_index.llms.bedrock import Bedrock
from llama_index.core.agent import ReActAgent
from shivonai.lyra import llamaindex_toolkit

# Your MCP server authentication details
MCP_AUTH_TOKEN = "shivonai_auth_token"
  # Change this to your server URL

def main():
    """Test LlamaIndex integration with ShivonAI using AWS Bedrock's Claude model."""
    print("Testing LlamaIndex integration with ShivonAI using Bedrock's Claude Sonnet...")
    
    # Get LlamaIndex tools from your MCP server
    tools = llamaindex_toolkit(MCP_AUTH_TOKEN)
    print(f"Found {len(tools)} MCP tools for LlamaIndex:")
    
    for name, tool in tools.items():
        print(f"  - {name}: {tool.metadata.description[:60]}...")
    
    # Create the Bedrock LLM with Claude Sonnet model
    llm = Bedrock(
        model="anthropic.claude-3-sonnet-20240229-v1:0",  # Claude 3 Sonnet model ID
        # Authentication options - choose one:
        # Option 1: Using AWS profile
        # Option 2: Using AWS credentials
        aws_access_key_id="bedrock_access_key",
        aws_secret_access_key="bedrock_secrate_access_key",
        # aws_session_token="YOUR_SESSION_TOKEN",  # if using temporary credentials
        region_name="bedrock_region",  # Change to your AWS region
        
        # Required for newer Claude models
        context_size=200000,  # Set appropriate context size for Claude 3 Sonnet
        
        # Optional parameters
        temperature=0.7,
        max_tokens=2000
    )
    
    # Convert tools dictionary to a list
    tool_list = list(tools.values())
    
    # Create the ReAct agent
    agent = ReActAgent.from_tools(
        tools=tool_list,
        llm=llm,
        verbose=True
    )
    
    # Test the agent with a simple query that should use one of your tools
    # Replace this with a query that's relevant to your tools
    query = "what listings I have?"
    
    print("\nTesting agent with query:", query)
    response = agent.chat(query)
    
    print("\nAgent response:")
    print(response)

if __name__ == "__main__":
    main()
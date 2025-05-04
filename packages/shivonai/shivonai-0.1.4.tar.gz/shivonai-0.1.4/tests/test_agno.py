# tested on openai models and bedrock claude models
# do not work with bedrock claude models. 

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from shivonai.lyra import agno_toolkit
import os
from agno.models.aws import Claude

# Replace with your actual MCP server details
auth_token = "Shivonai_auth_token"
 # Your MCP server URL


os.environ["OPENAI_API_KEY"] = "oepnai_api_key"
os.environ["AWS_ACCESS_KEY_ID"] = "bedrock_access_key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "bedrock_secrate_access_key"
os.environ["AWS_REGION "] = "bedrock_region"


# Get Agno tools
tools = agno_toolkit(auth_token)
print(tools)
# Print available tools
# print(tools.__name__)

print(f"Available MCP tools: {list(tools.keys())}")
print(tools.values())

# Create an Agno agent with tools
agent = Agent(
    model=OpenAIChat(id="gpt-3.5-turbo"),
    # model = Claude(id="anthropic.claude-3-5-sonnet-20240620-v1:0"),
    tools=list(tools.values()),
    markdown=True,
    show_tool_calls=True
)

# Try the agent with a simple task
try:
    agent.print_response("what listing are there?", stream=True)
except Exception as e:
    print(f"Error: {e}")
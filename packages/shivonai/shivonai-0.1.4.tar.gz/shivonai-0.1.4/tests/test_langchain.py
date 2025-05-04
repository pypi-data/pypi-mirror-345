# tested on openai models and bedrock claude models
# work with both types of models models. 

# #openai use

# from langchain_openai import ChatOpenAI
# from langchain.agents import initialize_agent, AgentType
# from shivonai.lyra import langchain_toolkit

# # Replace with your actual MCP server details
# auth_token = "shivonai_auth_token"

# # Get LangChain tools
# tools = langchain_toolkit(auth_token)

# # Print available tools
# print(f"Available tools: {[tool.name for tool in tools]}")

# # Initialize LangChain agent with tools
# llm = ChatOpenAI(
#             temperature=0,
#             model_name="gpt-4-turbo",
#             openai_api_key="openai-api-key"
#         )



# agent = initialize_agent(
#     tools=tools,
#     llm=llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True
# )

# # Try running the agent with a simple task
# try:
#     result = agent.run("what listing I have?")
#     print(f"Result: {result}")
# except Exception as e:
#     print(f"Error: {e}")


# bedrock use
from langchain_aws import ChatBedrock
from langchain.agents import initialize_agent, AgentType
from shivonai.lyra import langchain_toolkit
import os

os.environ["AWS_ACCESS_KEY_ID"] = "bedrock_access_key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "bedrock_secrate_access_key"


# Replace with your actual MCP server details
auth_token = "Shivonai_auth_token"

# Get LangChain tools
tools = langchain_toolkit(auth_token)

# Print available tools
print(f"Available tools: {[tool.name for tool in tools]}")

# Initialize LangChain agent with Claude Sonnet via AWS Bedrock
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",  # Claude Sonnet model ID
    region_name="bedrock_region",  # Replace with your AWS region
    temperature=0
)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Try running the agent with a simple task
try:
    result = agent.run("what listing I have?")
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
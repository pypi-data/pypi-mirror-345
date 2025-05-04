# tested on openai models and bedrock claude models
# work with both types of models models. 


# openai use
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI  # or any other LLM you prefer
from shivonai.lyra import crew_toolkit
import os


os.environ["OPENAI_API_KEY"] = "oepnai_api_key"


llm = ChatOpenAI(temperature=0.7, model="gpt-4")

# Get CrewAI tools
tools = crew_toolkit("shivonai_auth_token")

# Print available tools
print(f"Available tools: {[tool.name for tool in tools]}")

# Create an agent with these tools
agent = Agent(
    role="Data Analyst",
    goal="Analyze data using custom tools",
    backstory="You're an expert data analyst with access to custom tools",
    tools=tools,
    llm=llm  # Provide the LLM here
)

# Create a task - note the expected_output field
task = Task(
    description="what listings I have?",
    expected_output="A detailed report with key insights and recommendations",
    agent=agent
)

crew = Crew(
    agents=[agent],
    tasks=[task]
)

result = crew.kickoff()
print(result)






# #bedrock claude model use
# from crewai import Agent, Task, Crew, LLM
# from shivonai.lyra import crew_toolkit
# import os
# import boto3

# # Set up AWS credentials
# os.environ["AWS_ACCESS_KEY_ID"] = "bedrock_access_key"
# os.environ["AWS_SECRET_ACCESS_KEY"] = "bedrock_secrate_access_key"
# os.environ["AWS_REGION "] = "bedrock_region"


# # Create the CrewAI LLM instance with the bedrock prefix
# bedrock_llm = LLM(model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0")

# # Get CrewAI tools
# tools = crew_toolkit("shivonai_auth_token")

# # Create an agent with these tools
# agent = Agent(
#     role="Data Analyst",
#     goal="Analyze data using custom tools",
#     backstory="You're an expert data analyst with access to custom tools",
#     tools=tools,
#     llm=bedrock_llm  # Using the Bedrock LLM
# )

# # Create a task
# task = Task(
#     description="what listings I have?",
#     expected_output="A detailed report with key insights and recommendations",
#     agent=agent
# )

# crew = Crew(
#     agents=[agent],
#     tasks=[task]
# )

# result = crew.kickoff()
# print(result)
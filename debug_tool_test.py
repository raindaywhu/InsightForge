"""
Debug test for CrewAI with tools
"""

import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Crew, Task, Process, LLM
from crewai.tools import tool

# Create LLM
llm = LLM(
    model='openai/glm-5',
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_API_BASE')
)

# Create a simple tool
@tool('Test Tool')
def test_tool(query: str) -> str:
    '''A test tool that returns a message'''
    return f'Tool received: {query}'

# Create agent with tool
agent = Agent(
    role='Test Agent',
    goal='Test tool usage',
    backstory='A test agent with tools',
    llm=llm,
    tools=[test_tool],
    verbose=True
)

# Create task that should use tool
task = Task(
    description='Use the test tool to check the query "hello world" and then say goodbye',
    expected_output='Tool result and a goodbye message',
    agent=agent
)

# Create crew
crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=True
)

print('Starting crew with tools...')
result = crew.kickoff()
print('Result:', str(result))
"""
Debug test for CrewAI with knowledge sources
"""

import os
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, Crew, Task, Process, LLM
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

# Create LLM
llm = LLM(
    model='openai/glm-5',
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_API_BASE')
)

# Create knowledge source
knowledge_content = """
# Test Knowledge

## Topic: AI Agents
AI Agents are autonomous systems that can perform tasks.

## Key Points
1. They can use tools
2. They can reason and plan
3. They can learn from feedback
"""

print("Creating knowledge source...")
ks = StringKnowledgeSource(content=knowledge_content)
print("Knowledge source created")

# Create agent
agent = Agent(
    role='Knowledge Agent',
    goal='Answer questions using knowledge',
    backstory='An agent with access to a knowledge base',
    llm=llm,
    verbose=True
)

# Create task
task = Task(
    description='What are AI Agents? Use the knowledge base to answer.',
    expected_output='A brief explanation of AI Agents',
    agent=agent
)

# Create crew with knowledge
crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    knowledge_sources=[ks],
    verbose=True
)

print('Starting crew with knowledge...')
start = time.time()
result = crew.kickoff()
elapsed = time.time() - start
print(f'Result (took {elapsed:.1f}s):', str(result))
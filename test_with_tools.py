"""
测试带 Tools 的 Agent
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(Path(__file__).parent / ".env")

# 设置 ChromaDB 环境变量
os.environ["CHROMA_OPENAI_API_KEY"] = os.getenv("EMBEDDING_API_KEY", os.getenv("OPENAI_API_KEY", ""))
os.environ["CHROMA_OPENAI_API_BASE"] = os.getenv("EMBEDDING_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
os.environ["CHROMA_OPENAI_EMBEDDING_MODEL"] = os.getenv("DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v3")

print("=" * 60)
print("测试带 Tools 的 Agent")
print("=" * 60)

from crewai import Agent, Task, Crew, Process, LLM

# 创建 LLM
llm = LLM(
    model=f"openai/{os.getenv('OPENAI_MODEL_NAME', 'glm-5')}",
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_API_BASE')
)

# 加载搜索工具
print("\n[1] 加载搜索工具...")
try:
    from src.tech_report_agent.tools import get_search_tools
    tools = get_search_tools()
    print(f"  ✅ 加载了 {len(tools)} 个工具")
except Exception as e:
    print(f"  ❌ 加载失败: {e}")
    tools = []

# 创建带 tools 的 Agent
print("\n[2] 创建带 tools 的 Agent...")
agent = Agent(
    role="技术分析师",
    goal="分析技术主题",
    backstory="你是一个专业的技术分析师",
    llm=llm,
    tools=tools,
    verbose=True
)
print("  ✅ Agent 创建成功")

# 创建 Task
print("\n[3] 创建 Task...")
task = Task(
    description="简单分析 AI Agent 技术趋势，用2-3句话总结",
    expected_output="2-3句话的总结",
    agent=agent
)
print("  ✅ Task 创建成功")

# 执行 Crew
print("\n[4] 执行 Crew...")
crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=True
)

try:
    result = crew.kickoff()
    print(f"\n  Result: {result}")
    print("  ✅ Crew 执行成功！")
except Exception as e:
    print(f"  ❌ Crew 执行失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
"""
单独测试 design_task
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
print("测试 design_task")
print("=" * 60)

from src.tech_report_agent.crew import TechReportCrew
from crewai import Crew, Process, Task, LLM

# 创建 LLM
llm = LLM(
    model=f"openai/{os.getenv('OPENAI_MODEL_NAME', 'glm-5')}",
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_API_BASE')
)

# 创建设计 Agent
print("\n[1] 创建设计 Agent...")
from crewai import Agent

designer = Agent(
    role="演示设计师",
    goal="将技术报告转化为专业PPT",
    backstory="你是一位资深的演示设计专家",
    llm=llm,
    verbose=True,
    memory=False
)
print("  ✅ Agent 创建成功")

# 简单测试任务
print("\n[2] 创建简单设计任务...")
simple_design_task = Task(
    description="""
    将以下报告摘要转化为一个简单的 PPT 结构（JSON格式，5页以内）：
    
    报告主题：AI Agent 技术趋势
    
    主要发现：
    1. AI Agent 正从技术验证向商业落地过渡
    2. 企业级应用是最佳切入点
    3. 可靠性和成本是主要瓶颈
    
    输出 JSON 格式：
    {
      "metadata": {"title": "标题", "author": "InsightForge", "date": "日期"},
      "slides": [{"slide_number": 1, "type": "title", "title": "标题", "content": ["副标题"]}]
    }
    """,
    expected_output="JSON 格式的 PPT 结构",
    agent=designer
)
print("  ✅ Task 创建成功")

# 执行
print("\n[3] 执行设计任务...")
crew = Crew(
    agents=[designer],
    tasks=[simple_design_task],
    process=Process.sequential,
    verbose=True
)

try:
    result = crew.kickoff()
    print(f"\n✅ 执行成功！")
    print(f"Result: {result}")
except Exception as e:
    print(f"\n❌ 执行失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
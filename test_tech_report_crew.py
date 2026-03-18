"""
测试 TechReportCrew 实际配置
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
print("测试 TechReportCrew")
print("=" * 60)

from crewai import Crew, Process, Task

# 创建 Crew
print("\n[1] 创建 TechReportCrew...")
try:
    from src.tech_report_agent.crew import TechReportCrew
    crew_instance = TechReportCrew()
    print("  ✅ TechReportCrew 创建成功")
    print(f"  Knowledge sources: {len(crew_instance.knowledge_sources)}")
except Exception as e:
    print(f"  ❌ 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 获取 Agent
print("\n[2] 获取 Agents...")
try:
    analyst = crew_instance.technical_analyst()
    print(f"  technical_analyst: {analyst.role}")
    print(f"  memory: {analyst.memory}")
except Exception as e:
    print(f"  ❌ 获取 Agent 失败: {e}")
    import traceback
    traceback.print_exc()

# 获取 Task
print("\n[3] 获取 Tasks...")
try:
    analyze = crew_instance.analyze_task()
    print(f"  analyze_task: {analyze.description[:50]}...")
except Exception as e:
    print(f"  ❌ 获取 Task 失败: {e}")
    import traceback
    traceback.print_exc()

# 创建简单测试
print("\n[4] 执行简化测试 (只用 analyst, 简单任务)...")
simple_task = Task(
    description="用一句话总结 AI Agent 技术趋势",
    expected_output="一句话总结",
    agent=analyst
)

test_crew = Crew(
    agents=[analyst],
    tasks=[simple_task],
    process=Process.sequential,
    verbose=True
)

try:
    result = test_crew.kickoff()
    print(f"\n  Result: {result}")
    print("  ✅ 测试成功！")
except Exception as e:
    print(f"  ❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
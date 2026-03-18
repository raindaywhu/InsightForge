"""
测试完整的 TechReportCrew 流程
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
print("测试完整 TechReportCrew 流程")
print("=" * 60)

from src.tech_report_agent.crew import TechReportCrew
from crewai import Crew, Process

print("\n[1] 创建 TechReportCrew...")
crew_instance = TechReportCrew()
print("  ✅ 创建成功")

print("\n[2] 组装 Crew (两个 Agent, 两个 Task)...")
crew = crew_instance.crew()
print(f"  Agents: {len(crew.agents)}")
print(f"  Tasks: {len(crew.tasks)}")

for i, task in enumerate(crew.tasks):
    print(f"  Task {i+1}: {task.description[:50]}...")

print("\n[3] 执行 Crew...")
print("  这可能需要几分钟...")

try:
    result = crew.kickoff(inputs={"topic": "AI Agent 技术趋势", "language": "zh"})
    print(f"\n  ✅ Crew 执行成功！")
    print(f"  Result length: {len(str(result))} chars")
    print(f"  Preview: {str(result)[:200]}...")
except Exception as e:
    print(f"\n  ❌ Crew 执行失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
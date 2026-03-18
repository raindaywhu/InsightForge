"""
最小化 Agent 测试 - 排查 E2E 失败问题
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
print("最小化 Agent 测试")
print("=" * 60)

# 测试 1: LLM 连接
print("\n[1] 测试 LLM 连接...")
from crewai import LLM

model = os.getenv('OPENAI_MODEL_NAME', 'glm-5')
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('OPENAI_API_BASE')

print(f"  Model: {model}")
print(f"  API Base: {base_url}")

llm = LLM(
    model=f"openai/{model}",
    api_key=api_key,
    base_url=base_url
)

response = llm.call("回复一个字：好")
print(f"  Response: {response}")
print("  ✅ LLM 连接正常")

# 测试 2: 创建简单 Agent
print("\n[2] 测试创建 Agent...")
from crewai import Agent, Task, Crew, Process

agent = Agent(
    role="测试助手",
    goal="回复简单问题",
    backstory="你是一个测试助手",
    llm=llm,
    verbose=True
)
print("  ✅ Agent 创建成功")

# 测试 3: 创建简单 Task
print("\n[3] 测试创建 Task...")
task = Task(
    description="回复：测试成功",
    expected_output="一句话回复",
    agent=agent
)
print("  ✅ Task 创建成功")

# 测试 4: 执行 Crew
print("\n[4] 测试执行 Crew...")
crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=True
)

try:
    result = crew.kickoff()
    print(f"  Result: {result}")
    print("  ✅ Crew 执行成功！")
except Exception as e:
    print(f"  ❌ Crew 执行失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
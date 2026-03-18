"""
InsightForge 诊断测试
"""

import sys
import os
from pathlib import Path

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# Windows 兼容
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("InsightForge 诊断测试")
print("=" * 60)

# 1. 检查环境变量
print("\n[1] 环境变量检查:")
print(f"  OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY', 'NOT SET')[:20]}...")
print(f"  OPENAI_API_BASE: {os.getenv('OPENAI_API_BASE', 'NOT SET')}")
print(f"  OPENAI_MODEL_NAME: {os.getenv('OPENAI_MODEL_NAME', 'NOT SET')}")

# 2. 测试 LLM 连接
print("\n[2] 测试 LLM 连接...")
try:
    from crewai import LLM
    llm = LLM(
        model=f"openai/{os.getenv('OPENAI_MODEL_NAME', 'glm-5')}",
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_API_BASE')
    )
    print("  LLM 实例创建成功")
except Exception as e:
    print(f"  ❌ LLM 创建失败: {e}")
    sys.exit(1)

# 3. 测试简单调用
print("\n[3] 测试 LLM 调用...")
try:
    from openai import OpenAI
    client = OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_API_BASE')
    )
    response = client.chat.completions.create(
        model=os.getenv('OPENAI_MODEL_NAME', 'glm-5'),
        messages=[{"role": "user", "content": "你好，请回复'测试成功'"}],
        max_tokens=50
    )
    print(f"  ✅ LLM 响应: {response.choices[0].message.content}")
except Exception as e:
    print(f"  ❌ LLM 调用失败: {e}")
    sys.exit(1)

# 4. 测试知识库加载
print("\n[4] 测试知识库加载...")
try:
    from src.tech_report_agent.crew import TechReportCrew
    crew = TechReportCrew()
    print(f"  ✅ 知识源数量: {len(crew.knowledge_sources)}")
except Exception as e:
    print(f"  ❌ 知识库加载失败: {e}")
    sys.exit(1)

# 5. 测试 Agent 创建
print("\n[5] 测试 Agent 创建...")
try:
    agent = crew.technical_analyst()
    print(f"  ✅ Agent 创建成功: {agent.role}")
except Exception as e:
    print(f"  ❌ Agent 创建失败: {e}")
    sys.exit(1)

# 6. 测试 Crew 执行 (简化)
print("\n[6] 测试 Crew 执行...")
try:
    test_crew = crew.crew()
    print(f"  ✅ Crew 创建成功")
    print(f"  - Agents: {len(test_crew.agents)}")
    print(f"  - Tasks: {len(test_crew.tasks)}")
except Exception as e:
    print(f"  ❌ Crew 创建失败: {e}")
    sys.exit(1)

# 7. 测试实际执行
print("\n[7] 测试实际执行 (可能需要 30-60 秒)...")
try:
    inputs = {
        "topic": "Python 编程语言优势",
        "language": "zh"
    }
    result = test_crew.kickoff(inputs=inputs)
    print(f"  ✅ 执行成功!")
    print(f"  结果长度: {len(str(result))} 字符")
except Exception as e:
    print(f"  ❌ 执行失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ 所有诊断测试通过！")
print("=" * 60)
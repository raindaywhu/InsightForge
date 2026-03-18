"""
测试 CrewAI Knowledge 实际使用（不依赖 Embedding API）
"""

import os
import sys
from pathlib import Path

# 加载 .env
from dotenv import load_dotenv
load_dotenv()

# 设置 UTF-8 编码
os.environ["PYTHONUTF8"] = "1"

def test_crewai_knowledge_without_embedding():
    """
    测试 CrewAI Knowledge 是否可以在没有 embedding 的情况下工作
    
    CrewAI Knowledge 可能有以下模式：
    1. 需要 embedding 进行向量检索
    2. 纯文本匹配（不需要 embedding）
    """
    try:
        from crewai import Agent, Crew, Task, Process, LLM
        from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
        
        print("[TEST] CrewAI Knowledge without Embedding")
        
        # 创建 LLM
        llm = LLM(
            model="openai/glm-5",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        
        # 创建知识源（不使用 storage，避免 embedding）
        knowledge_content = """
        SWOT分析方法论：
        - 优势(Strengths)：内部积极因素，如技术优势、品牌价值
        - 劣势(Weaknesses)：内部消极因素，如资源不足、经验缺乏
        - 机会(Opportunities)：外部积极因素，如市场增长、政策支持
        - 威胁(Threats)：外部消极因素，如竞争加剧、技术替代
        
        使用原则：
        1. 客观分析，避免主观臆断
        2. 数据支撑，每个观点要有依据
        3. 动态更新，定期重新评估
        """
        
        # 尝试创建 StringKnowledgeSource（不带 storage）
        print("  创建知识源（无 storage）...")
        ks = StringKnowledgeSource(content=knowledge_content)
        print(f"  知识源创建成功: {type(ks)}")
        
        # 创建 Agent 并添加知识
        print("  创建 Agent...")
        agent = Agent(
            role="分析师",
            goal="使用SWOT方法进行分析",
            backstory="你是一位熟练的分析师",
            llm=llm,
            knowledge_sources=[ks],  # 添加知识源
            verbose=True
        )
        print(f"  Agent 创建成功")
        
        # 创建简单任务
        print("  创建 Task...")
        task = Task(
            description="简要说明SWOT分析的四个维度",
            expected_output="简短说明",
            agent=agent  # 添加 agent
        )
        
        # 创建 Crew
        print("  创建 Crew...")
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        print("\n  开始执行 Crew...")
        result = crew.kickoff()
        
        print(f"\n[SUCCESS] Crew 执行成功!")
        print(f"结果: {result}")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crewai_with_embedder_none():
    """
    测试 CrewAI Knowledge 使用 embedder=None
    """
    try:
        from crewai import Agent, Crew, Task, Process, LLM
        from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
        
        print("\n[TEST] CrewAI Knowledge with embedder=None")
        
        llm = LLM(
            model="openai/glm-5",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        
        knowledge_content = "SWOT分析包括优势、劣势、机会、威胁四个维度。"
        
        ks = StringKnowledgeSource(content=knowledge_content)
        
        agent = Agent(
            role="分析师",
            goal="进行分析",
            backstory="专业分析师",
            llm=llm,
            knowledge_sources=[ks],
            embedder=None,  # 尝试禁用 embedder
            verbose=True
        )
        
        task = Task(
            description="什么是SWOT？",
            expected_output="简短回答"
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        print("  执行 Crew...")
        result = crew.kickoff()
        
        print(f"[SUCCESS] 执行成功: {result}")
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("CrewAI Knowledge 实际使用测试")
    print("=" * 60)
    
    # 测试 1: 无 embedding 模式
    result1 = test_crewai_knowledge_without_embedding()
    
    # 测试 2: embedder=None
    # result2 = test_crewai_with_embedder_none()
    
    print("\n" + "=" * 60)
    if result1:
        print("CrewAI Knowledge 可以在不使用 Embedding 的情况下工作!")
        print("建议：启用 RAG 代码，让它使用内置的知识检索机制")
    else:
        print("CrewAI Knowledge 需要有效的 Embedding API")
        print("解决方案：")
        print("  1. 获取 DashScope API Key (推荐)")
        print("  2. 使用 Prompt 注入方案")
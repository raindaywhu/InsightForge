"""
测试 DashScope Embedding API 兼容性
"""

import os
import sys
from pathlib import Path

# 加载 .env
from dotenv import load_dotenv
load_dotenv()

# 测试 Coding API Embedding
def test_coding_embedding():
    """测试 Coding API Embedding"""
    import requests
    import json
    
    # Coding API 配置
    api_key = os.getenv("OPENAI_API_KEY")  # Coding API Key
    api_base = os.getenv("OPENAI_API_BASE", "https://coding.dashscope.aliyuncs.com/v1")
    
    print(f"[TEST] Coding API Embedding")
    print(f"  API Base: {api_base}")
    print(f"  API Key: {api_key[:20]}...")
    
    url = f"{api_base}/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 尝试不同的模型名称
    models_to_try = ["text-embedding-v3", "text-embedding-v2", "embedding-v1"]
    
    for model in models_to_try:
        print(f"\n  尝试模型: {model}")
        data = {
            "model": model,
            "input": "测试文本"
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get("data", [{}])[0].get("embedding", [])
                print(f"  [SUCCESS] 模型 {model} 可用!")
                print(f"    向量维度: {len(embedding)}")
                return True, model
            else:
                print(f"  [FAILED] 状态码: {response.status_code}")
                error_info = response.json().get("error", {})
                print(f"    错误: {error_info.get('message', response.text[:100])}")
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    return False, None


def test_crewai_knowledge_with_coding():
    """测试 CrewAI Knowledge + Coding API"""
    try:
        from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
        from crewai.knowledge.storage.knowledge_storage import KnowledgeStorage
        
        print(f"\n[TEST] CrewAI Knowledge + Coding API")
        
        # 使用 Coding API 配置
        embedder_config = {
            "provider": "openai",
            "config": {
                "model_name": "text-embedding-v3",  # 会自动重试其他模型
                "api_key": os.getenv("OPENAI_API_KEY"),
                "api_base": os.getenv("OPENAI_API_BASE")
            }
        }
        
        print(f"  Embedder config: provider=openai, api_base={os.getenv('OPENAI_API_BASE')}")
        
        # 创建 KnowledgeStorage
        storage = KnowledgeStorage(embedder=embedder_config)
        
        # 创建 StringKnowledgeSource
        ks = StringKnowledgeSource(
            content="SWOT分析是一种战略分析工具，用于评估优势、劣势、机会和威胁。",
            storage=storage
        )
        
        print(f"[SUCCESS] CrewAI Knowledge 初始化成功!")
        return True
        
    except Exception as e:
        print(f"[ERROR] CrewAI Knowledge 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_crewai_knowledge_with_dashscope():
    """测试 CrewAI Knowledge + DashScope API（使用正确的 Key）"""
    try:
        from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
        from crewai.knowledge.storage.knowledge_storage import KnowledgeStorage
        
        print(f"\n[TEST] CrewAI Knowledge + DashScope API")
        
        # DashScope 需要单独的 API Key
        # 这里我们暂时使用 Coding API 来测试
        dashscope_api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if not dashscope_api_key or dashscope_api_key.startswith("sk-sp"):
            print("[WARN] DASHSCOPE_API_KEY 可能是 Coding API Key，跳过测试")
            return None
        
        embedder_config = {
            "provider": "openai",
            "config": {
                "model_name": "text-embedding-v3",
                "api_key": dashscope_api_key,
                "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1"
            }
        }
        
        storage = KnowledgeStorage(embedder=embedder_config)
        ks = StringKnowledgeSource(
            content="测试内容",
            storage=storage
        )
        
        print(f"[SUCCESS] DashScope Embedding 成功!")
        return True
        
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Embedding API 兼容性测试")
    print("=" * 60)
    
    # 测试 Coding API Embedding
    result1, working_model = test_coding_embedding()
    
    # 测试 CrewAI Knowledge
    result2 = test_crewai_knowledge_with_coding()
    
    # 测试 DashScope API（如果有正确的 Key）
    # result3 = test_crewai_knowledge_with_dashscope()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    print(f"  Coding API Embedding: {'成功 - 模型: ' + working_model if result1 else '失败'}")
    print(f"  CrewAI Knowledge:     {'成功' if result2 else '失败'}")
    
    if result1:
        print(f"\n建议: 使用 Coding API 的 {working_model} 模型进行 Embedding")
    else:
        print(f"\n需要: 获取 DashScope API Key (不是 Coding API Key)")
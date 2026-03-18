"""测试 DashScope Embedding API"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# 设置 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

api_key = os.getenv("EMBEDDING_API_KEY")
api_base = os.getenv("EMBEDDING_API_BASE")

print("=" * 60)
print("测试 DashScope Embedding API")
print("=" * 60)
print(f"API Base: {api_base}")
print(f"API Key: {api_key[:10]}...{api_key[-6:]}")
print()

# 测试 text-embedding-v3
url = f"{api_base}/embeddings"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
data = {
    "model": "text-embedding-v3",
    "input": "测试文本"
}

print("[TEST] text-embedding-v3...")
response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    result = response.json()
    embedding = result.get("data", [{}])[0].get("embedding", [])
    print(f"  [OK] 成功! 向量维度: {len(embedding)}")
    print(f"  前5维: {embedding[:5]}")
else:
    print(f"  [FAIL] 失败: {response.status_code}")
    print(f"  错误: {response.text}")

print()
print("=" * 60)
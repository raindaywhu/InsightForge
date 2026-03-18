"""
InsightForge 搜索工具
集成 Tavily API 进行实时数据检索
"""

import os
from typing import Optional, List, Dict, Any
from crewai.tools import tool

# Tavily 搜索工具
@tool("Web Search Tool")
def web_search(query: str, max_results: int = 5) -> str:
    """
    搜索网络获取实时信息
    
    Args:
        query: 搜索查询
        max_results: 最大结果数
        
    Returns:
        搜索结果摘要
    """
    try:
        from tavily import TavilyClient
        
        # 获取 API Key
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            # 没有 API Key 时优雅降级 - 返回提示但不报错
            return "[提示] 未配置 TAVILY_API_KEY，跳过网络搜索。将基于知识库进行分析。"
        
        # 执行搜索
        client = TavilyClient(api_key=api_key)
        response = client.search(query=query, max_results=max_results)
        
        # 格式化结果
        results = []
        for i, result in enumerate(response.get("results", []), 1):
            title = result.get("title", "无标题")
            url = result.get("url", "")
            content = result.get("content", "")[:500]  # 限制长度
            results.append(f"{i}. **{title}**\n   URL: {url}\n   摘要: {content}...")
        
        return "\n\n".join(results) if results else "未找到相关结果"
        
    except ImportError:
        return "错误: 请安装 tavily-python: pip install tavily-python"
    except Exception as e:
        return f"搜索错误: {str(e)}"


# 创建搜索工具实例
def get_search_tools():
    """获取搜索工具列表"""
    return [web_search]


# 测试函数
def test_search():
    """测试搜索功能"""
    print("测试 Web 搜索...")
    result = web_search.run("OpenAI Sora 最新进展 2024")
    print(result)


if __name__ == "__main__":
    test_search()
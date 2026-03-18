"""
InsightForge 搜索工具集
支持 Web 搜索、arXiv 论文检索、网页抓取
"""

import os
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
from crewai.tools import tool


# ============== Web 搜索工具 ==============

@tool("Web Search Tool")
def web_search(query: str, max_results: int = 5, days_ago: int = None) -> str:
    """
    搜索网络获取实时信息
    
    Args:
        query: 搜索查询
        max_results: 最大结果数 (默认5)
        days_ago: 只返回最近N天的结果 (可选)
        
    Returns:
        搜索结果摘要，包含标题、URL、发布日期
    """
    try:
        from tavily import TavilyClient
        
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            # 没有 API Key 时优雅降级 - 返回提示但不报错
            return "[提示] 未配置 TAVILY_API_KEY，跳过网络搜索。将基于知识库进行分析。"
        
        client = TavilyClient(api_key=api_key)
        
        # 构建搜索参数
        search_params = {
            "query": query,
            "max_results": max_results,
            "include_raw_content": False,
            "include_dates": True
        }
        
        # 时间过滤
        if days_ago:
            search_params["days_ago"] = days_ago
        
        response = client.search(**search_params)
        
        # 格式化结果
        results = []
        for i, result in enumerate(response.get("results", []), 1):
            title = result.get("title", "无标题")
            url = result.get("url", "")
            content = result.get("content", "")[:500]
            published_date = result.get("published_date", "未知日期")
            
            # 标注时效性
            date_str = f"📅 {published_date}" if published_date != "未知日期" else ""
            
            results.append(
                f"### [{i}] {title}\n"
                f"{date_str}\n"
                f"🔗 URL: {url}\n"
                f"📝 摘要: {content}...\n"
            )
        
        if not results:
            return "未找到相关结果"
        
        return "\n".join(results)
        
    except ImportError:
        return "错误: 请安装 tavily-python: pip install tavily-python"
    except Exception as e:
        return f"搜索错误: {str(e)}"


# ============== arXiv 论文搜索工具 ==============

@tool("arXiv Search Tool")
def arxiv_search(query: str, max_results: int = 5, category: str = None) -> str:
    """
    搜索 arXiv 学术论文
    
    Args:
        query: 搜索关键词 (支持标题、摘要、作者)
        max_results: 最大结果数 (默认5)
        category: 论文类别 (如 cs.AI, cs.LG, cs.CL)
        
    Returns:
        论文列表，包含标题、作者、arXiv ID、摘要
    """
    try:
        import arxiv
        
        # 构建搜索查询
        search_query = query
        if category:
            search_query = f"cat:{category} AND {query}"
        
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        results = []
        for i, paper in enumerate(search.results(), 1):
            title = paper.title
            authors = ", ".join([a.name for a in paper.authors[:3]])
            if len(paper.authors) > 3:
                authors += " et al."
            
            arxiv_id = paper.entry_id.split("/")[-1]
            summary = paper.summary.replace("\n", " ")[:400]
            published = paper.published.strftime("%Y-%m-%d")
            pdf_url = paper.pdf_url
            
            results.append(
                f"### [{i}] {title}\n"
                f"📄 arXiv: {arxiv_id}\n"
                f"👥 作者: {authors}\n"
                f"📅 发布: {published}\n"
                f"📝 摘要: {summary}...\n"
                f"🔗 PDF: {pdf_url}\n"
            )
        
        if not results:
            return "未找到相关论文"
        
        return "\n".join(results)
        
    except ImportError:
        return "错误: 请安装 arxiv: pip install arxiv"
    except Exception as e:
        return f"arXiv 搜索错误: {str(e)}"


@tool("arXiv Paper Detail")
def arxiv_paper_detail(arxiv_id: str) -> str:
    """
    获取 arXiv 论文详细信息
    
    Args:
        arxiv_id: arXiv 论文 ID (如 2403.12345 或 2024.12345)
        
    Returns:
        论文详细信息，包含完整摘要、引用格式
    """
    try:
        import arxiv
        
        # 标准化 ID 格式
        arxiv_id = arxiv_id.replace("arXiv:", "").strip()
        
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(search.results(), None)
        
        if not paper:
            return f"未找到论文: {arxiv_id}"
        
        title = paper.title
        authors = ", ".join([a.name for a in paper.authors])
        summary = paper.summary
        published = paper.published.strftime("%Y-%m-%d")
        updated = paper.updated.strftime("%Y-%m-%d")
        pdf_url = paper.pdf_url
        abs_url = paper.entry_id
        categories = ", ".join(paper.categories)
        
        # 生成引用格式
        year = paper.published.year
        first_author = paper.authors[0].name.split()[-1]
        citation = f"[{first_author} et al., {year}, arXiv:{arxiv_id}]"
        
        return (
            f"# {title}\n\n"
            f"**arXiv ID**: {arxiv_id}\n"
            f"**作者**: {authors}\n"
            f"**发布日期**: {published}\n"
            f"**更新日期**: {updated}\n"
            f"**分类**: {categories}\n\n"
            f"## 摘要\n{summary}\n\n"
            f"## 链接\n"
            f"- 📄 PDF: {pdf_url}\n"
            f"- 🌐 Abstract: {abs_url}\n\n"
            f"## 引用格式\n"
            f"```\n{citation}\n```\n"
        )
        
    except ImportError:
        return "错误: 请安装 arxiv: pip install arxiv"
    except Exception as e:
        return f"获取论文详情错误: {str(e)}"


# ============== 网页抓取工具 ==============

@tool("Web Fetch Tool")
def web_fetch(url: str, max_length: int = 5000) -> str:
    """
    抓取网页内容
    
    Args:
        url: 网页 URL
        max_length: 返回内容最大长度 (默认5000字符)
        
    Returns:
        网页正文内容
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # 移除脚本和样式
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # 提取正文
        text = soup.get_text(separator="\n")
        
        # 清理空白
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        content = "\n".join(lines)
        
        # 截断
        if len(content) > max_length:
            content = content[:max_length] + "\n... [内容已截断]"
        
        return f"来源: {url}\n访问时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n{content}"
        
    except ImportError:
        return "错误: 请安装 requests 和 beautifulsoup4: pip install requests beautifulsoup4"
    except Exception as e:
        return f"抓取错误: {str(e)}"


# ============== 时间验证工具 ==============

@tool("Check Data Freshness")
def check_data_freshness(date_str: str, max_days: int = 90) -> str:
    """
    检查数据时效性
    
    Args:
        date_str: 日期字符串 (如 2024-03-15 或 March 15, 2024)
        max_days: 最大允许天数 (默认90天)
        
    Returns:
        时效性评估结果
    """
    try:
        from dateutil import parser
        
        # 解析日期
        date = parser.parse(date_str)
        now = datetime.now()
        
        # 计算天数差
        days_diff = (now - date).days
        
        # 评估
        if days_diff <= 7:
            status = "🟢 最新 (1周内)"
        elif days_diff <= 30:
            status = "🟢 较新 (1月内)"
        elif days_diff <= 90:
            status = "🟡 可用 (3月内)"
        elif days_diff <= 180:
            status = "🟠 偏旧 (6月内)"
        else:
            status = "🔴 过时 (超过6月)"
        
        return (
            f"数据日期: {date.strftime('%Y-%m-%d')}\n"
            f"距今: {days_diff} 天\n"
            f"状态: {status}\n"
            f"符合标准: {'✅ 是' if days_diff <= max_days else '❌ 否'}\n"
        )
        
    except ImportError:
        return "错误: 请安装 python-dateutil: pip install python-dateutil"
    except Exception as e:
        return f"日期解析错误: {str(e)}"


# ============== 引用格式化工具 ==============

@tool("Format Citation")
def format_citation(source_type: str, data: str) -> str:
    """
    格式化引用
    
    Args:
        source_type: 来源类型 (arxiv/web/report/news)
        data: 来源数据 (arXiv ID 或 URL)
        
    Returns:
        标准化引用格式
    """
    now = datetime.now().strftime("%Y-%m-%d")
    
    if source_type == "arxiv":
        return f"[arXiv:{data}] - 访问日期: {now}"
    
    elif source_type == "web":
        return f"[来源]({data}) - 访问日期: {now}"
    
    elif source_type == "report":
        return f"[报告, {data}] - 访问日期: {now}"
    
    elif source_type == "news":
        return f"[新闻报道, {data}] - 访问日期: {now}"
    
    else:
        return f"[{data}] - 访问日期: {now}"


# ============== 工具集合 ==============

def get_search_tools():
    """获取所有搜索工具"""
    return [
        web_search,
        arxiv_search,
        arxiv_paper_detail,
        web_fetch,
        check_data_freshness,
        format_citation
    ]


def get_basic_tools():
    """获取基础工具 (仅搜索)"""
    return [web_search, arxiv_search]


# ============== 测试 ==============

def test_tools():
    """测试所有工具"""
    print("=" * 50)
    print("测试 Web 搜索...")
    print("=" * 50)
    result = web_search.run("OpenAI Sora 最新进展 2026")
    print(result[:1000])
    
    print("\n" + "=" * 50)
    print("测试 arXiv 搜索...")
    print("=" * 50)
    result = arxiv_search.run("speculative decoding LLM")
    print(result[:1000])
    
    print("\n" + "=" * 50)
    print("测试工具数量:", len(get_search_tools()))


if __name__ == "__main__":
    test_tools()
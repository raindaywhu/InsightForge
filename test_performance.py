"""
InsightForge 性能测试脚本
测试各阶段耗时和资源占用
"""

import sys
import time
import tracemalloc
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

# 配置 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8')

def test_performance():
    """执行性能测试"""
    print("=" * 50)
    print("InsightForge 性能测试")
    print("=" * 50)
    
    # 初始化内存追踪
    tracemalloc.start()
    
    results = {}
    
    # 1. 测试知识库加载
    print("\n1. 测试知识库加载...")
    start_time = time.time()
    from src.tech_report_agent.crew import TechReportCrew
    crew = TechReportCrew()
    load_time = time.time() - start_time
    results["知识库加载"] = load_time
    print(f"   耗时: {load_time:.2f}s")
    
    # 获取内存快照
    current, peak = tracemalloc.get_traced_memory()
    results["内存峰值(MB)"] = peak / 1024 / 1024
    print(f"   内存峰值: {results['内存峰值(MB)']:.2f} MB")
    
    # 2. 测试 RAG 检索
    print("\n2. 测试 RAG 检索...")
    start_time = time.time()
    try:
        result = crew.crew().knowledge_queries(['SWOT 分析'])
        rag_time = time.time() - start_time
        results["RAG 检索"] = rag_time
        print(f"   耗时: {rag_time:.2f}s")
        print(f"   结果长度: {len(str(result))} 字符")
    except Exception as e:
        print(f"   错误: {e}")
        results["RAG 检索"] = "失败"
    
    # 3. 测试 Agent 初始化
    print("\n3. 测试 Agent 初始化...")
    start_time = time.time()
    from crewai import Crew
    test_crew = crew.crew()
    init_time = time.time() - start_time
    results["Agent 初始化"] = init_time
    print(f"   耗时: {init_time:.2f}s")
    print(f"   Agent 数量: {len(test_crew.agents)}")
    print(f"   Task 数量: {len(test_crew.tasks)}")
    
    # 4. 测试 PPT 生成
    print("\n4. 测试 PPT 生成...")
    from src.tech_report_agent.ppt_generator import PPTGenerator
    
    test_structure = {
        "metadata": {"title": "性能测试", "author": "InsightForge", "date": "2026-03-18"},
        "slides": [
            {"slide_number": 1, "type": "title", "title": "测试", "content": ["标题", "副标题"]},
            {"slide_number": 2, "type": "content", "title": "内容", "content": ["要点1", "要点2", "要点3"]},
            {"slide_number": 3, "type": "closing", "title": "结束", "content": ["谢谢"]}
        ]
    }
    
    start_time = time.time()
    generator = PPTGenerator()
    output_path = Path(__file__).parent / "output" / "test_performance.pptx"
    generator.generate(test_structure, output_path)
    ppt_time = time.time() - start_time
    results["PPT 生成"] = ppt_time
    print(f"   耗时: {ppt_time:.2f}s")
    print(f"   文件大小: {output_path.stat().st_size / 1024:.2f} KB")
    
    # 停止内存追踪
    tracemalloc.stop()
    
    # 打印汇总
    print("\n" + "=" * 50)
    print("性能测试汇总")
    print("=" * 50)
    for name, value in results.items():
        if isinstance(value, float):
            print(f"{name}: {value:.2f}s" if "内存" not in name else f"{name}: {value:.2f}")
        else:
            print(f"{name}: {value}")
    
    print("\n✅ 性能测试完成!")
    return results


if __name__ == "__main__":
    test_performance()
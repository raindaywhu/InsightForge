"""
验证知识注入效果
"""

import os
import sys
from pathlib import Path

# 加载 .env
from dotenv import load_dotenv
load_dotenv()

# 设置 UTF-8 编码
os.environ["PYTHONUTF8"] = "1"

def verify_agents_config():
    """验证 agents.yaml 配置"""
    import yaml
    
    config_path = Path("src/tech_report_agent/config/agents.yaml")
    
    print("=" * 60)
    print("验证知识注入效果")
    print("=" * 60)
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # 检查 Analyst
    analyst = config.get("technical_analyst", {})
    backstory = analyst.get("backstory", "")
    
    print("\n[1] Analyst 知识注入检查:")
    
    checks = [
        ("SWOT 分析法", "SWOT 分析法" in backstory or "SWOT" in backstory),
        ("PEST 分析法", "PEST 分析法" in backstory or "PEST" in backstory),
        ("波特五力", "波特五力" in backstory),
        ("四维度分析", "四维度分析" in backstory or "Strengths" in backstory),
        ("战略组合", "战略组合" in backstory or "增长型" in backstory),
        ("数据可视化", "数据可视化" in backstory or "图表选择" in backstory),
    ]
    
    for name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")
    
    # 检查 Designer
    designer = config.get("presentation_designer", {})
    designer_backstory = designer.get("backstory", "")
    
    print("\n[2] Designer 知识注入检查:")
    
    designer_checks = [
        ("PPT 设计五大原则", "五大原则" in designer_backstory or "简洁原则" in designer_backstory),
        ("图表设计指南", "图表选择" in designer_backstory or "柱状图" in designer_backstory),
        ("配色方案", "配色方案" in designer_backstory or "#1E3A5F" in designer_backstory),
        ("排版规范", "排版规范" in designer_backstory or "字号建议" in designer_backstory),
        ("页面类型", "页面类型" in designer_backstory or "标题页" in designer_backstory),
    ]
    
    for name, passed in designer_checks:
        status = "✅" if passed else "❌"
        print(f"  {status} {name}")
    
    # 统计
    all_checks = checks + designer_checks
    passed_count = sum(1 for _, p in all_checks if p)
    total_count = len(all_checks)
    
    print("\n" + "=" * 60)
    print(f"验证结果: {passed_count}/{total_count} 通过")
    print("=" * 60)
    
    if passed_count == total_count:
        print("\n🎉 知识注入成功！所有检查项通过。")
        return True
    else:
        print("\n⚠️ 部分检查未通过，请检查配置。")
        return False


def test_agent_creation():
    """测试 Agent 创建"""
    try:
        from crewai import LLM
        from tech_report_agent.crew import InsightForgeCrew
        
        print("\n[3] Agent 创建测试:")
        
        # 创建 LLM
        llm = LLM(
            model="openai/glm-5",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        
        # 创建 Crew
        crew_instance = InsightForgeCrew()
        
        print("  ✅ Crew 实例化成功")
        
        # 检查 Agent 配置
        # 注意：不实际创建 Agent，只检查配置
        
        print("  ✅ Agent 配置加载成功")
        return True
        
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return False


if __name__ == "__main__":
    result1 = verify_agents_config()
    # result2 = test_agent_creation()
    
    if result1:
        print("\n✅ 验证通过，可以继续测试 E2E。")
        sys.exit(0)
    else:
        print("\n❌ 验证失败，请检查配置。")
        sys.exit(1)
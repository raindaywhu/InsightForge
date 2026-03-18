"""
测试搜索工具集成
"""

import sys
import os
from pathlib import Path

# Windows 兼容
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))


def test_search_tool_import():
    """测试搜索工具导入"""
    print("\n" + "="*60)
    print("测试搜索工具集成...")
    print("="*60)
    
    # 1. 测试导入
    try:
        from src.tech_report_agent.tools import web_search, get_search_tools
        print("✅ 搜索工具导入成功")
    except Exception as e:
        print(f"❌ 搜索工具导入失败: {e}")
        return False
    
    # 2. 测试工具函数
    tools = get_search_tools()
    print(f"✅ 获取到 {len(tools)} 个搜索工具")
    
    # 3. 测试工具属性
    for tool in tools:
        print(f"   - 工具名: {tool.name}")
    
    # 4. 检查环境变量配置
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        print("✅ TAVILY_API_KEY 已配置")
    else:
        print("⚠️ TAVILY_API_KEY 未配置（搜索功能将返回错误提示）")
    
    # 5. 测试搜索工具是否正确集成到 Agent
    try:
        from src.tech_report_agent.crew import TechReportCrew
        crew = TechReportCrew()
        analyst = crew.technical_analyst()
        
        if analyst.tools:
            print(f"✅ technical_analyst Agent 已集成 {len(analyst.tools)} 个工具")
            for tool in analyst.tools:
                print(f"   - {tool.name}")
        else:
            print("⚠️ technical_analyst Agent 未集成工具")
    except Exception as e:
        print(f"❌ Agent 工具集成检查失败: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ 搜索工具集成测试完成！")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    test_search_tool_import()
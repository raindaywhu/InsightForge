"""测试 CrewAI Knowledge 加载"""
import os
import sys
sys.path.insert(0, "C:/Users/raind/projects/InsightForge/src")

os.environ["PYTHONUTF8"] = "1"

from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("测试 CrewAI Knowledge 加载")
print("=" * 60)

try:
    from tech_report_agent.crew import TechReportCrew
    
    print("\n[TEST] 创建 TechReportCrew 实例...")
    crew = TechReportCrew()
    
    print("\n[RESULT] 知识库加载状态:")
    if hasattr(crew, 'knowledge_sources'):
        print(f"  - knowledge_sources: {len(crew.knowledge_sources)} 个文件")
    if hasattr(crew, 'knowledge_by_category'):
        print(f"  - analyst: {len(crew.knowledge_by_category.get('analyst', []))} 个")
        print(f"  - designer: {len(crew.knowledge_by_category.get('designer', []))} 个")
    
    print("\n[OK] Knowledge 加载成功!")
    
except Exception as e:
    import traceback
    print(f"\n[FAIL] 错误: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
"""
测试多语言输出
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.tech_report_agent.crew import TechReportCrew

def test_chinese():
    """测试中文输出"""
    print("\n" + "="*60)
    print("测试中文输出...")
    print("="*60)
    
    crew = TechReportCrew()
    inputs = {
        "topic": "OpenAI 在 AI Agent 领域的竞争力",
        "language": "zh"
    }
    
    try:
        result = crew.crew().kickoff(inputs=inputs)
        print("\n✅ 中文测试完成")
        print(f"输出长度: {len(str(result))} 字符")
        return True
    except Exception as e:
        print(f"\n❌ 中文测试失败: {e}")
        return False


def test_english():
    """测试英文输出"""
    print("\n" + "="*60)
    print("Testing English Output...")
    print("="*60)
    
    crew = TechReportCrew()
    inputs = {
        "topic": "OpenAI competitiveness in AI Agent space",
        "language": "en"
    }
    
    try:
        result = crew.crew().kickoff(inputs=inputs)
        print("\n✅ English test completed")
        print(f"Output length: {len(str(result))} characters")
        return True
    except Exception as e:
        print(f"\n❌ English test failed: {e}")
        return False


if __name__ == "__main__":
    # 测试中文
    zh_ok = test_chinese()
    
    # 测试英文
    en_ok = test_english()
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"中文输出: {'✅ 通过' if zh_ok else '❌ 失败'}")
    print(f"英文输出: {'✅ 通过' if en_ok else '❌ 失败'}")
    print("="*60 + "\n")
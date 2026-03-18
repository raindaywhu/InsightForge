"""
InsightForge v1.0 端到端测试
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# Windows 兼容
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

from src.tech_report_agent.crew import TechReportCrew
from src.tech_report_agent.ppt_generator import PPTGenerator


def test_full_pipeline():
    """完整流程测试"""
    # 使用默认测试主题
    topic = "AI Agent 技术趋势 2024"
    language = "zh"
    
    print("\n" + "="*60)
    print(f"InsightForge v1.0 端到端测试")
    print(f"主题: {topic}")
    print(f"语言: {language}")
    print("="*60 + "\n")
    
    start_time = time.time()
    
    # 1. 创建输出目录
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = topic.replace(" ", "_")[:30]
    
    # 2. 运行 Agent Crew
    print("🔄 Step 1: 运行 Agent 分析...")
    crew = TechReportCrew()
    inputs = {
        "topic": topic,
        "language": language
    }
    
    try:
        result = crew.crew().kickoff(inputs=inputs)
        report_content = str(result)
        print(f"✅ 分析完成，报告长度: {len(report_content)} 字符")
    except Exception as e:
        print(f"❌ Agent 分析失败: {e}")
        return False
    
    # 3. 保存 Markdown 报告
    print("\n🔄 Step 2: 保存 Markdown 报告...")
    report_path = output_dir / f"report_{timestamp}_{safe_topic}.md"
    report_path.write_text(report_content, encoding="utf-8")
    print(f"✅ 报告已保存: {report_path}")
    
    # 4. 生成 PPT 结构
    print("\n🔄 Step 3: 生成 PPT 结构...")
    ppt_gen = PPTGenerator()
    
    # 从报告提取 PPT 结构
    ppt_structure = ppt_gen.generate_structure(report_content, topic)
    print(f"✅ PPT 结构生成完成，共 {len(ppt_structure.get('slides', []))} 页")
    
    # 保存 JSON 结构
    json_path = output_dir / f"ppt_structure_{timestamp}_{safe_topic}.json"
    import json
    json_path.write_text(json.dumps(ppt_structure, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 结构已保存: {json_path}")
    
    # 5. 生成 PPTX 文件
    print("\n🔄 Step 4: 生成 PPTX 文件...")
    pptx_path = output_dir / f"presentation_{timestamp}_{safe_topic}.pptx"
    
    try:
        ppt_gen.generate_pptx(ppt_structure, str(pptx_path))
        print(f"✅ PPTX 已生成: {pptx_path}")
    except Exception as e:
        print(f"❌ PPTX 生成失败: {e}")
        return False
    
    # 6. 总结
    elapsed = time.time() - start_time
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
    print(f"⏱️ 总耗时: {elapsed:.2f} 秒")
    print(f"📄 报告: {report_path}")
    print(f"📊 结构: {json_path}")
    print(f"📽️ PPT: {pptx_path}")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    success = test_full_pipeline()
    sys.exit(0 if success else 1)
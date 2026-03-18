"""
InsightForge v1.0 端到端测试
"""

import sys
import os
import time
import json
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


def extract_json_from_text(text: str) -> dict:
    """从文本中提取 JSON 结构"""
    import re
    
    # 尝试直接解析
    try:
        return json.loads(text)
    except:
        pass
    
    # 尝试提取 JSON 代码块
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    matches = re.findall(json_pattern, text)
    
    for match in matches:
        try:
            return json.loads(match)
        except:
            continue
    
    # 尝试找到最外层的 JSON 对象
    brace_pattern = r'\{[\s\S]*\}'
    match = re.search(brace_pattern, text)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    
    raise ValueError("无法从输出中提取有效的 JSON 结构")


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
    print("🔄 Step 1: 运行 Agent Crew...")
    crew = TechReportCrew()
    inputs = {
        "topic": topic,
        "language": language
    }
    
    try:
        result = crew.crew().kickoff(inputs=inputs)
        print("✅ Crew 执行完成")
    except Exception as e:
        print(f"❌ Crew 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. 提取任务输出
    print("\n🔄 Step 2: 提取任务输出...")
    report_content = None
    ppt_json = None
    
    if hasattr(result, 'tasks_output'):
        for task_output in result.tasks_output:
            task_name = task_output.name if hasattr(task_output, 'name') else str(task_output)
            content = task_output.raw if hasattr(task_output, 'raw') else str(task_output)
            
            if 'analyze' in task_name.lower():
                report_content = content
                print(f"✅ 获取分析报告: {len(content)} 字符")
            elif 'design' in task_name.lower():
                try:
                    ppt_json = extract_json_from_text(content)
                    print(f"✅ 获取 PPT 结构: {len(ppt_json.get('slides', []))} 页")
                except Exception as e:
                    print(f"⚠️ PPT 结构解析失败: {e}")
                    ppt_json = None
    
    # 如果没有从 tasks_output 获取到，尝试从最终结果获取
    if not report_content and hasattr(result, 'raw'):
        report_content = result.raw
        print(f"✅ 从 raw 获取报告: {len(report_content)} 字符")
    
    if not report_content:
        print("❌ 未能获取报告内容")
        return False
    
    # 4. 保存 Markdown 报告
    print("\n🔄 Step 3: 保存 Markdown 报告...")
    report_path = output_dir / f"report_{timestamp}_{safe_topic}.md"
    report_path.write_text(report_content, encoding="utf-8")
    print(f"✅ 报告已保存: {report_path}")
    
    # 5. 如果有 PPT JSON，生成 PPT
    if ppt_json:
        print("\n🔄 Step 4: 生成 PPT...")
        
        # 保存 JSON 结构
        json_path = output_dir / f"ppt_structure_{timestamp}_{safe_topic}.json"
        json_path.write_text(json.dumps(ppt_json, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"✅ 结构已保存: {json_path}")
        
        # 生成 PPTX 文件
        pptx_path = output_dir / f"presentation_{timestamp}_{safe_topic}.pptx"
        
        try:
            ppt_gen = PPTGenerator()
            ppt_gen.generate(ppt_json, str(pptx_path))
            print(f"✅ PPTX 已生成: {pptx_path}")
        except Exception as e:
            print(f"❌ PPTX 生成失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n⚠️ 未获取到有效的 PPT JSON 结构，跳过 PPT 生成")
    
    # 6. 总结
    elapsed = time.time() - start_time
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)
    print(f"⏱️ 总耗时: {elapsed:.2f} 秒")
    print(f"📄 报告: {report_path}")
    if ppt_json:
        print(f"📊 结构: {json_path}")
        print(f"📽️ PPT: {pptx_path}")
    print("="*60 + "\n")
    
    return True


if __name__ == "__main__":
    success = test_full_pipeline()
    sys.exit(0 if success else 1)
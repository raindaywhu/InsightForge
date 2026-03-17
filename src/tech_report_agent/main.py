"""
InsightForge 主入口模块

提供命令行接口，执行报告生成流程。
"""

import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .crew import TechReportCrew
from .ppt_generator import generate_ppt


# 确保 UTF-8 输出（Windows 兼容）
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def get_output_dir() -> Path:
    """获取输出目录"""
    output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def print_progress(step: str, message: str):
    """打印进度信息"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {step} {message}")


def save_report(report_content: str, output_dir: Path, topic: str, suffix: str = "") -> Path:
    """保存 Markdown 报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 清理主题名称，用于文件名
    safe_topic = "".join(c if c.isalnum() or c in " _-" else "" for c in topic)
    safe_topic = safe_topic[:50].strip().replace(" ", "_")
    
    filename = f"report_{timestamp}_{safe_topic}{suffix}.md"
    filepath = output_dir / "reports" / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    filepath.write_text(report_content, encoding="utf-8")
    return filepath


def save_ppt_structure(json_content: str, output_dir: Path, topic: str, theme: str = "tech_blue") -> tuple[Path, Path | None]:
    """保存 PPT 结构 JSON 并生成 PPT 文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = "".join(c if c.isalnum() or c in " _-" else "" for c in topic)
    safe_topic = safe_topic[:50].strip().replace(" ", "_")
    
    filename = f"ppt_structure_{timestamp}_{safe_topic}.json"
    filepath = output_dir / "presentations" / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # 尝试格式化 JSON
    ppt_data = None
    try:
        ppt_data = json.loads(json_content)
        filepath.write_text(json.dumps(ppt_data, indent=2, ensure_ascii=False), encoding="utf-8")
    except:
        filepath.write_text(json_content, encoding="utf-8")
    
    # 生成 PPT 文件
    pptx_path = None
    if ppt_data:
        try:
            pptx_filename = f"presentation_{timestamp}_{safe_topic}.pptx"
            pptx_path = output_dir / "presentations" / pptx_filename
            generate_ppt(ppt_data, pptx_path, theme=theme)
        except Exception as e:
            print(f"[WARN] Failed to generate PPT: {e}")
            pptx_path = None
    
    return filepath, pptx_path


def run(topic: str, verbose: bool = True, output_dir: Optional[str] = None, theme: str = "tech_blue") -> dict:
    """
    执行技术报告生成流程
    
    Args:
        topic: 分析主题
        verbose: 是否输出详细日志
        output_dir: 输出目录路径
        theme: PPT 主题 (tech_blue, business_gray, minimal_white, nature_green)
        
    Returns:
        包含输出文件路径的字典
    """
    print("\n" + "="*60)
    print("  InsightForge - AI Report Generator")
    print("="*60)
    print_progress("START", f"Topic: {topic}")
    
    # 设置输出目录
    if output_dir:
        os.environ["OUTPUT_DIR"] = output_dir
    
    # 初始化 Crew
    print_progress("INIT", "Initializing agents and tasks...")
    crew = TechReportCrew()
    
    # 执行
    print_progress("RUN", "Running analysis crew...")
    inputs = {"topic": topic}
    
    try:
        result = crew.crew().kickoff(inputs=inputs)
    except Exception as e:
        print_progress("ERROR", f"Failed: {e}")
        raise
    
    # 保存输出
    out_dir = get_output_dir()
    outputs = {}
    
    # 保存所有任务的输出
    if hasattr(result, 'tasks_output'):
        print_progress("SAVE", "Saving outputs...")
        for i, task_output in enumerate(result.tasks_output):
            task_name = task_output.name if hasattr(task_output, 'name') else f"task_{i}"
            content = task_output.raw if hasattr(task_output, 'raw') else str(task_output)
            
            if 'analyze' in task_name.lower():
                # 保存 Markdown 报告
                report_path = save_report(content, out_dir, topic)
                outputs["report"] = str(report_path)
                print_progress("SAVED", f"Report: {report_path}")
            elif 'design' in task_name.lower():
                # 保存 PPT 结构并生成 PPT
                ppt_path, pptx_path = save_ppt_structure(content, out_dir, topic, theme=theme)
                outputs["ppt_structure"] = str(ppt_path)
                print_progress("SAVED", f"PPT Structure: {ppt_path}")
                if pptx_path:
                    outputs["pptx"] = str(pptx_path)
                    print_progress("SAVED", f"PPT File: {pptx_path}")
            else:
                # 其他任务输出
                other_path = save_report(content, out_dir, topic, suffix=f"_{task_name}")
                outputs[task_name] = str(other_path)
                print_progress("SAVED", f"{task_name}: {other_path}")
    elif hasattr(result, "raw"):
        # 单任务输出
        report_path = save_report(result.raw, out_dir, topic)
        outputs["report"] = str(report_path)
        print_progress("DONE", f"Report saved: {report_path}")
    
    print("\n" + "="*60)
    print("  Generation Complete!")
    print("="*60 + "\n")
    
    return outputs


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="InsightForge - AI-powered Technical Report Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  insightforge run "Analyze OpenAI competitiveness in AI Agent space"
  insightforge run "2024 LLM Development Trends" -o ./output
  
  # Chinese topics also supported
  insightforge run "分析 OpenAI 在 AI Agent 领域的竞争力"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # run 命令
    run_parser = subparsers.add_parser("run", help="Generate technical report")
    run_parser.add_argument("topic", help="Analysis topic")
    run_parser.add_argument("--output", "-o", help="Output directory", default="output")
    run_parser.add_argument("--theme", "-t", 
                            choices=["tech_blue", "business_gray", "minimal_white", "nature_green"],
                            default="tech_blue",
                            help="PPT theme (default: tech_blue)")
    run_parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    if args.command == "run":
        run(topic=args.topic, verbose=not args.quiet, output_dir=args.output, theme=args.theme)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
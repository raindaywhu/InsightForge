"""
InsightForge 主入口模块

提供命令行接口，执行报告生成流程。
"""

import os
import argparse
from datetime import datetime
from pathlib import Path

from .crew import TechReportCrew


def get_output_dir() -> Path:
    """获取输出目录"""
    output_dir = Path(os.getenv("OUTPUT_DIR", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_report(report_content: str, output_dir: Path, topic: str) -> Path:
    """保存 Markdown 报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # 清理主题名称，用于文件名
    safe_topic = "".join(c if c.isalnum() or c in " _-" else "" for c in topic)
    safe_topic = safe_topic[:50].strip().replace(" ", "_")
    
    filename = f"report_{timestamp}_{safe_topic}.md"
    filepath = output_dir / "reports" / filename
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    filepath.write_text(report_content, encoding="utf-8")
    return filepath


def run(topic: str, verbose: bool = True) -> dict:
    """
    执行技术报告生成流程
    
    Args:
        topic: 分析主题
        verbose: 是否输出详细日志
        
    Returns:
        包含输出文件路径的字典
    """
    print(f"\n🚀 InsightForge 启动")
    print(f"📋 分析主题: {topic}\n")
    
    # 初始化 Crew
    crew = TechReportCrew()
    
    # 执行
    inputs = {"topic": topic}
    result = crew.crew().kickoff(inputs=inputs)
    
    # 保存输出
    output_dir = get_output_dir()
    
    outputs = {}
    
    # 保存报告
    if hasattr(result, "raw"):
        report_path = save_report(result.raw, output_dir, topic)
        outputs["report"] = str(report_path)
        print(f"\n✅ 报告已保存: {report_path}")
    
    print(f"\n🎉 完成!")
    return outputs


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="InsightForge - AI驱动的技术报告生成系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  insightforge run "分析 OpenAI 在 AI Agent 领域的竞争力"
  insightforge run "2024年大语言模型发展趋势分析" --output ./my_output
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # run 命令
    run_parser = subparsers.add_parser("run", help="生成技术报告")
    run_parser.add_argument("topic", help="分析主题")
    run_parser.add_argument("--output", "-o", help="输出目录", default="output")
    run_parser.add_argument("--quiet", "-q", action="store_true", help="静默模式")
    
    args = parser.parse_args()
    
    if args.command == "run":
        if args.output:
            os.environ["OUTPUT_DIR"] = args.output
        run(topic=args.topic, verbose=not args.quiet)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
"""
Tech Report Agent - 主入口
技术报告生成系统
"""

import os
import sys
from datetime import datetime

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tech_report_agent.crew import TechReportCrew


def run(topic: str):
    """
    运行技术报告生成
    
    Args:
        topic: 报告主题
    """
    print(f"\n{'='*60}")
    print(f"📊 技术报告生成系统")
    print(f"📝 主题: {topic}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)

    # 初始化 Crew
    crew_instance = TechReportCrew()
    crew = crew_instance.crew()

    # 执行任务
    inputs = {
        'topic': topic
    }

    try:
        result = crew.kickoff(inputs=inputs)
        
        # 保存报告
        report_path = os.path.join(output_dir, f'report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(str(result))
        
        print(f"\n{'='*60}")
        print(f"✅ 报告生成完成!")
        print(f"📄 报告路径: {report_path}")
        print(f"{'='*60}\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        raise


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='技术报告生成系统')
    parser.add_argument('topic', help='报告主题')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    run(args.topic)


if __name__ == '__main__':
    main()
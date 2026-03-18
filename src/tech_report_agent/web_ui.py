"""
InsightForge Web UI
Gradio 界面实现
"""

import gradio as gr
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 配置 UTF-8
import locale
if locale.getpreferredencoding() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from src.tech_report_agent.crew import TechReportCrew
from src.tech_report_agent.ppt_generator import PPTGenerator

# 主题配置
THEMES = {
    "科技蓝": "tech_blue",
    "商务灰": "business_gray", 
    "简约白": "minimal_white",
    "自然绿": "nature_green"
}

def generate_report(topic: str, theme: str, progress=gr.Progress()):
    """
    生成报告和 PPT
    
    Args:
        topic: 分析主题
        theme: PPT 主题
        progress: Gradio 进度条
    
    Yields:
        tuple: (report_content, ppt_path, status)
    """
    try:
        # 初始化
        progress(0, desc="初始化...")
        
        if not topic or not topic.strip():
            yield "", None, "❌ 请输入分析主题"
            return
        
        # 创建输出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = topic.replace(" ", "_").replace("/", "_")[:30]
        output_dir = Path(__file__).parent.parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # 初始化 Crew
        progress(0.1, desc="加载知识库...")
        crew = TechReportCrew()
        
        # 执行分析
        progress(0.2, desc="正在分析主题...")
        
        # 运行 Crew
        result = crew.crew().kickoff(inputs={"topic": topic})
        
        progress(0.6, desc="生成报告...")
        
        # 获取报告内容
        report_content = str(result)
        
        # 保存报告
        report_path = output_dir / f"report_{timestamp}_{safe_topic}.md"
        report_path.write_text(report_content, encoding='utf-8')
        
        progress(0.7, desc="生成 PPT...")
        
        # 尝试生成 PPT
        ppt_path = None
        try:
            # 从输出中提取 PPT 结构
            # 这里简化处理，实际需要从 agent 输出解析
            ppt_generator = PPTGenerator()
            ppt_path = output_dir / f"presentation_{timestamp}_{safe_topic}.pptx"
            
            # 使用简单的 PPT 结构
            simple_structure = {
                "metadata": {
                    "title": topic,
                    "author": "InsightForge",
                    "date": datetime.now().strftime("%Y-%m-%d")
                },
                "slides": [
                    {"slide_number": 1, "type": "title", "title": topic, "content": ["技术分析报告", "InsightForge 生成"]},
                    {"slide_number": 2, "type": "content", "title": "分析概要", "content": ["基于 SWOT/PEST 框架分析", "深度洞察与专业建议"]},
                    {"slide_number": 3, "type": "closing", "title": "谢谢", "content": ["InsightForge", "锻造洞察，智绘未来"]}
                ]
            }
            
            ppt_generator.generate(simple_structure, ppt_path, theme=THEMES.get(theme, "tech_blue"))
            
        except Exception as e:
            print(f"PPT 生成警告: {e}")
            ppt_path = None
        
        progress(1.0, desc="完成!")
        
        # 返回结果
        status = f"✅ 完成! 报告已保存到: {report_path.name}"
        if ppt_path:
            status += f"\n📊 PPT 已保存到: {ppt_path.name}"
        
        yield report_content, str(ppt_path) if ppt_path else None, status
        
    except Exception as e:
        yield "", None, f"❌ 错误: {str(e)}"


def create_ui():
    """创建 Gradio 界面"""
    
    with gr.Blocks(title="InsightForge") as demo:
        
        # 标题
        gr.Markdown(
            """
            # 🔥 InsightForge
            ### 锻造洞察，智绘未来
            
            AI 驱动的技术报告生成系统，支持深度分析和专业 PPT 生成。
            """,
            elem_classes=["main-title"]
        )
        
        # 主要内容区
        with gr.Row():
            # 左侧输入区
            with gr.Column(scale=1):
                topic_input = gr.Textbox(
                    label="分析主题",
                    placeholder="例如：OpenAI 在 AI Agent 领域的竞争力分析",
                    lines=3,
                    info="输入你想分析的主题，系统将自动选择合适的分析框架"
                )
                
                theme_dropdown = gr.Dropdown(
                    choices=list(THEMES.keys()),
                    value="科技蓝",
                    label="PPT 主题",
                    info="选择 PPT 的配色风格"
                )
                
                generate_btn = gr.Button(
                    "🚀 开始生成",
                    variant="primary",
                    size="lg"
                )
                
                status_output = gr.Textbox(
                    label="状态",
                    lines=2,
                    interactive=False,
                    elem_classes=["status-box"]
                )
            
            # 右侧输出区
            with gr.Column(scale=2):
                with gr.Tab("📄 报告预览"):
                    report_output = gr.Markdown(
                        label="生成报告",
                        value="报告将在这里显示..."
                    )
                
                with gr.Tab("📊 PPT 下载"):
                    ppt_output = gr.File(
                        label="PPT 文件",
                        file_types=[".pptx"]
                    )
        
        # 示例
        gr.Markdown("### 📝 示例主题")
        gr.Examples(
            examples=[
                ["OpenAI 在 AI Agent 领域的竞争力分析"],
                ["中国新能源汽车市场 SWOT 分析"],
                ["大模型技术发展趋势 PEST 分析"],
                ["苹果公司 AI 战略分析"],
            ],
            inputs=topic_input,
            label=""
        )
        
        # 底部信息
        gr.Markdown(
            """
            ---
            💡 **提示**: 
            - 分析时间约 2-5 分钟，取决于主题复杂度
            - 支持的分析框架：SWOT、PEST、波特五力等
            - 输出包含 Markdown 报告和 PPT 文件
            """
        )
        
        # 事件绑定
        generate_btn.click(
            fn=generate_report,
            inputs=[topic_input, theme_dropdown],
            outputs=[report_output, ppt_output, status_output]
        )
    
    return demo


def main():
    """启动 Web UI"""
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
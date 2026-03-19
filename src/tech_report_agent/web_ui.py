"""
InsightForge Web UI
Gradio 界面实现 - 支持项目管理与团队协作
"""

import gradio as gr
import sys
import os
from pathlib import Path
from datetime import datetime
import json

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# 配置 UTF-8
import locale
if locale.getpreferredencoding() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from src.tech_report_agent.crew import TechReportCrew
from src.tech_report_agent.ppt_generator import PPTGenerator
from src.tech_report_agent.project_manager import get_project_manager

# 主题配置
THEMES = {
    "科技蓝": "tech_blue",
    "商务灰": "business_gray", 
    "简约白": "minimal_white",
    "自然绿": "nature_green",
    "珊瑚夕阳": "coral_sunset",
    "深海蓝": "ocean_depth"
}

# 模板配置
TEMPLATES = {
    "技术趋势": "technical",
    "竞品分析": "competitive",
    "行业研究": "industry",
    "技术评估": "evaluation"
}

# 当前用户（模拟）
CURRENT_USER = "default"

def generate_report(project_id: str, topic: str, template: str, theme: str, progress=gr.Progress()):
    """
    生成报告和 PPT（支持项目保存）
    
    Args:
        project_id: 项目ID（可选）
        topic: 分析主题
        template: 报告模板
        theme: PPT 主题
        progress: Gradio 进度条
    
    Yields:
        tuple: (report_content, ppt_path, status, new_project_id)
    """
    try:
        progress(0, desc="初始化...")
        
        if not topic or not topic.strip():
            yield "", None, "❌ 请输入分析主题", None
            return
        
        # 获取项目管理器
        pm = get_project_manager()
        
        # 创建或获取项目
        if not project_id:
            project = pm.create_project(
                name=topic[:30],
                topic=topic,
                owner=CURRENT_USER,
                template=TEMPLATES.get(template, "technical")
            )
            project_id = project["id"]
        else:
            project = pm.get_project(project_id)
            if not project:
                yield "", None, "❌ 项目不存在", None
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
        
        # 保存报告到项目
        pm.save_report(project_id, report_content)
        
        # 保存报告文件
        report_path = output_dir / f"report_{timestamp}_{safe_topic}.md"
        report_path.write_text(report_content, encoding='utf-8')
        
        progress(0.7, desc="生成 PPT...")
        
        # 尝试生成 PPT
        ppt_path = None
        try:
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
        status = f"✅ 完成! 报告已保存到: {report_path.name}\n📁 项目ID: {project_id}"
        if ppt_path:
            status += f"\n📊 PPT 已保存到: {ppt_path.name}"
        
        yield report_content, str(ppt_path) if ppt_path else None, status, project_id
        
    except Exception as e:
        yield "", None, f"❌ 错误: {str(e)}", None


def list_projects():
    """列出当前用户的项目"""
    pm = get_project_manager()
    projects = pm.list_projects(owner=CURRENT_USER)
    
    if not projects:
        return "暂无项目"
    
    lines = []
    for p in projects[:10]:  # 最多显示 10 个
        status_emoji = "✅" if p.get("status") == "completed" else "📝"
        lines.append(f"{status_emoji} **{p['name']}** (ID: `{p['id']}`)")
        lines.append(f"   - 主题: {p.get('topic', 'N/A')}")
        lines.append(f"   - 更新: {p.get('updated_at', 'N/A')[:10]}")
        lines.append("")
    
    return "\n".join(lines)


def load_project(project_id: str):
    """加载项目"""
    if not project_id or not project_id.strip():
        return "", "", "请输入项目ID"
    
    pm = get_project_manager()
    project = pm.get_project(project_id.strip())
    
    if not project:
        return "", "", f"❌ 项目 {project_id} 不存在"
    
    report = pm.load_report(project_id) or ""
    
    return (
        project.get("topic", ""),
        report,
        f"✅ 已加载项目: {project.get('name')} (ID: {project_id})"
    )


def delete_project(project_id: str):
    """删除项目"""
    if not project_id or not project_id.strip():
        return "请输入项目ID"
    
    pm = get_project_manager()
    success = pm.delete_project(project_id.strip())
    
    if success:
        return f"✅ 项目 {project_id} 已删除"
    else:
        return f"❌ 删除失败，项目 {project_id} 不存在"


def export_project(project_id: str):
    """导出项目"""
    if not project_id or not project_id.strip():
        return None, "请输入项目ID"
    
    pm = get_project_manager()
    export_data = pm.export_project(project_id.strip())
    
    if not export_data:
        return None, f"❌ 项目 {project_id} 不存在"
    
    # 保存为 JSON 文件
    export_path = Path(__file__).parent.parent.parent / "output" / f"export_{project_id}.json"
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    return str(export_path), f"✅ 已导出到: {export_path.name}"


def create_ui():
    """创建 Gradio 界面"""
    
    with gr.Blocks(title="InsightForge", theme=gr.themes.Soft()) as demo:
        
        # 状态存储
        current_project_id = gr.State(value=None)
        
        # 标题
        gr.Markdown(
            """
            # 🔥 InsightForge
            ### 锻造洞察，智绘未来
            
            AI 驱动的技术报告生成系统，支持深度分析和专业 PPT 生成。
            """,
            elem_classes=["main-title"]
        )
        
        # 使用 Tab 组织功能
        with gr.Tabs():
            # Tab 1: 生成报告
            with gr.TabItem("📝 生成报告"):
                with gr.Row():
                    # 左侧输入区
                    with gr.Column(scale=1):
                        topic_input = gr.Textbox(
                            label="分析主题",
                            placeholder="例如：OpenAI 在 AI Agent 领域的竞争力分析",
                            lines=3,
                            info="输入你想分析的主题，系统将自动选择合适的分析框架"
                        )
                        
                        template_dropdown = gr.Dropdown(
                            choices=list(TEMPLATES.keys()),
                            value="技术趋势",
                            label="报告模板",
                            info="选择报告类型"
                        )
                        
                        theme_dropdown = gr.Dropdown(
                            choices=list(THEMES.keys()),
                            value="科技蓝",
                            label="PPT 主题",
                            info="选择演示文稿视觉风格"
                        )
                        
                        generate_btn = gr.Button(
                            "🚀 开始分析",
                            variant="primary",
                            size="lg"
                        )
                    
                    # 右侧输出区
                    with gr.Column(scale=2):
                        status_output = gr.Textbox(
                            label="状态",
                            lines=2,
                            interactive=False
                        )
                        
                        report_output = gr.Textbox(
                            label="分析报告",
                            lines=15,
                            max_lines=30,
                            interactive=False,
                            show_copy_button=True
                        )
                        
                        ppt_output = gr.File(
                            label="PPT 文件",
                            file_count="single"
                        )
            
            # Tab 2: 项目管理
            with gr.TabItem("📁 项目管理"):
                gr.Markdown("### 我的项目")
                
                project_list = gr.Textbox(
                    label="项目列表",
                    lines=10,
                    interactive=False,
                    value=list_projects()
                )
                
                refresh_btn = gr.Button("🔄 刷新列表")
                refresh_btn.click(fn=list_projects, outputs=project_list)
                
                gr.Markdown("---")
                gr.Markdown("### 项目操作")
                
                with gr.Row():
                    project_id_input = gr.Textbox(
                        label="项目ID",
                        placeholder="输入项目ID进行操作"
                    )
                
                with gr.Row():
                    load_btn = gr.Button("📂 加载项目")
                    export_btn = gr.Button("📤 导出项目")
                    delete_btn = gr.Button("🗑️ 删除项目", variant="stop")
                
                project_status = gr.Textbox(label="操作结果", interactive=False)
                export_file = gr.File(label="导出文件")
                
                # 事件绑定
                load_btn.click(
                    fn=load_project,
                    inputs=[project_id_input],
                    outputs=[topic_input, report_output, project_status]
                )
                
                export_btn.click(
                    fn=export_project,
                    inputs=[project_id_input],
                    outputs=[export_file, project_status]
                )
                
                delete_btn.click(
                    fn=delete_project,
                    inputs=[project_id_input],
                    outputs=[project_status]
                )
        
        # 示例
        gr.Examples(
            examples=[
                ["GPT-5 技术发展预测"],
                ["中国新能源汽车市场 SWOT 分析"],
                ["大模型技术发展趋势 PEST 分析"],
                ["苹果公司 AI 战略分析"],
            ],
            inputs=topic_input,
            label="示例主题"
        )
        
        # 底部信息
        gr.Markdown(
            """
            ---
            💡 **提示**: 
            - 分析时间约 2-5 分钟，取决于主题复杂度
            - 支持的分析框架：SWOT、PEST、波特五力等
            - 输出包含 Markdown 报告和 PPT 文件
            - 所有项目自动保存，可在"项目管理"中查看
            """
        )
        
        # 事件绑定
        generate_btn.click(
            fn=generate_report,
            inputs=[current_project_id, topic_input, template_dropdown, theme_dropdown],
            outputs=[report_output, ppt_output, status_output, current_project_id]
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
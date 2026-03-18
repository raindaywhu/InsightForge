"""
InsightForge 集成测试

测试内容：
- Agent 协作测试
- RAG 检索测试
"""

import sys
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 设置测试环境变量（必须在导入前）
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
os.environ["CHROMA_OPENAI_API_KEY"] = os.getenv("CHROMA_OPENAI_API_KEY", "test-key")
os.environ["CHROMA_OPENAI_API_BASE"] = os.getenv("CHROMA_OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestAgentCollaboration:
    """测试 Agent 协作"""
    
    @pytest.mark.slow
    def test_analyze_task_alone(self):
        """单独测试 analyze_task"""
        from tech_report_agent.crew import TechReportCrew
        
        crew = TechReportCrew()
        
        # 只运行 analyze_task
        result = crew.crew().agents[0].execute_task(
            crew.crew().tasks[0],
            context={}
        )
        
        # 验证输出
        assert result is not None
        assert len(result) > 100  # 应有实质内容
    
    @pytest.mark.slow
    def test_design_task_alone(self):
        """单独测试 design_task（使用简化输入）"""
        from tech_report_agent.crew import TechReportCrew
        
        # 准备简化输入
        simplified_report = """
# AI Agent 技术分析

## 执行摘要
- 发现1: 技术快速发展
- 发现2: 市场需求增长

## 分析
### SWOT
- 优势: 技术领先
- 劣势: 成本高
- 机会: 市场大
- 威胁: 竞争激烈

## 结论
AI Agent 技术前景广阔。
"""
        
        crew = TechReportCrew()
        
        # 运行 design_task（需要 context）
        # 注意：这个测试需要 mock 或者简化
        
    @pytest.mark.slow
    def test_full_crew_flow_short_topic(self):
        """完整 Crew 流程（简短主题）"""
        from tech_report_agent.main import run
        
        # 使用简短主题
        result = run(topic="AI", verbose=False, output_dir="test_output")
        
        # 验证输出
        assert result is not None
        assert "report_path" in result or "ppt_structure" in result


class TestRAGRetrieval:
    """测试 RAG 检索"""
    
    @pytest.mark.skip(reason="需要 API Key 和网络连接")
    def test_knowledge_base_loading(self):
        """测试知识库加载"""
        from tech_report_agent.crew import TechReportCrew
        
        crew = TechReportCrew()
        
        # 检查知识库是否正确初始化
        # 实际检查取决于 CrewAI 的实现
        
    def test_framework_retrieval(self):
        """测试分析框架检索"""
        # 模拟查询 "竞争分析"
        # 预期检索到 SWOT、波特五力
        
    def test_ppt_skill_retrieval(self):
        """测试 PPT 技能检索"""
        # 模拟查询 "图表设计"
        # 预期检索到图表设计指南


class TestKnowledgeBase:
    """测试知识库"""
    
    def test_knowledge_files_loaded(self):
        """验证知识文件被加载"""
        knowledge_dir = Path(__file__).parent.parent / "knowledge"
        
        # 统计知识文件
        md_files = list(knowledge_dir.rglob("*.md"))
        assert len(md_files) >= 8, f"Expected at least 8 knowledge files, got {len(md_files)}"
    
    def test_knowledge_content_quality(self):
        """验证知识内容质量"""
        knowledge_dir = Path(__file__).parent.parent / "knowledge"
        
        # 检查每个知识文件
        for md_file in knowledge_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            
            # 应有实质内容
            assert len(content) > 100, f"Knowledge file too short: {md_file.name}"
            
            # 应有标题
            assert "#" in content, f"Knowledge file missing headers: {md_file.name}"


# 标记慢测试
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"])
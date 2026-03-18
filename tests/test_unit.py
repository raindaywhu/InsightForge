"""
InsightForge 单元测试

测试内容：
- main.py: 参数解析、文件命名、UTF-8 编码
- ppt_generator.py: JSON 解析、幻灯片类型、图表生成、主题配色
- crew.py: Agent 初始化、知识库加载、Embedder 配置
"""

import sys
import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# 设置测试环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"


class TestMainSaveReport:
    """测试 main.py 的 save_report 函数"""
    
    def test_ascii_filename_from_chinese_topic(self):
        """中文主题应生成 ASCII 文件名"""
        from tech_report_agent.main import save_report
        
        output_dir = Path("test_output")
        topic = "AI Agent 技术 2024"
        
        filepath = save_report("# Test", output_dir, topic)
        
        # 文件名应为 ASCII
        assert all(c.isascii() for c in filepath.name), f"文件名包含非 ASCII 字符: {filepath.name}"
        
        # 清理
        filepath.unlink(missing_ok=True)
    
    def test_ascii_filename_from_special_chars(self):
        """特殊字符主题应生成干净的文件名"""
        from tech_report_agent.main import save_report
        
        output_dir = Path("test_output")
        topic = "AI@Agent#2024!测试"
        
        filepath = save_report("# Test", output_dir, topic)
        
        # 文件名应为 ASCII
        assert all(c.isascii() for c in filepath.name)
        
        # 清理
        filepath.unlink(missing_ok=True)
    
    def test_empty_topic_uses_timestamp(self):
        """空主题应使用时间戳作为文件名"""
        from tech_report_agent.main import save_report
        
        output_dir = Path("test_output")
        topic = "测试测试测试"  # 全中文会被过滤为空
        
        filepath = save_report("# Test", output_dir, topic)
        
        # 文件名应包含时间戳格式
        assert "report_" in filepath.name
        
        # 清理
        filepath.unlink(missing_ok=True)
    
    def test_report_content_utf8(self):
        """报告内容应为 UTF-8 编码"""
        from tech_report_agent.main import save_report
        
        output_dir = Path("test_output")
        topic = "Test Topic"
        content = "# 测试报告\n\n中文内容测试 🚀"
        
        filepath = save_report(content, output_dir, topic)
        
        # 读取并验证 UTF-8
        read_content = filepath.read_text(encoding="utf-8")
        assert "中文内容测试" in read_content
        assert "🚀" in read_content
        
        # 清理
        filepath.unlink(missing_ok=True)


class TestMainSavePPTStructure:
    """测试 main.py 的 save_ppt_structure 函数"""
    
    def test_valid_json_output(self):
        """PPT 结构应为有效 JSON"""
        from tech_report_agent.main import save_ppt_structure
        
        output_dir = Path("test_output")
        topic = "Test Topic"
        ppt_data = {
            "metadata": {"title": "Test", "author": "InsightForge"},
            "slides": [{"slide_number": 1, "type": "title", "title": "Test"}]
        }
        
        filepath, pptx_path = save_ppt_structure(json.dumps(ppt_data), output_dir, topic)
        
        # JSON 文件应可解析
        with open(filepath, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        assert loaded["metadata"]["title"] == "Test"
        
        # 清理
        filepath.unlink(missing_ok=True)
        if pptx_path:
            pptx_path.unlink(missing_ok=True)
    
    def test_ascii_filename_for_ppt(self):
        """PPT 文件名应为 ASCII"""
        from tech_report_agent.main import save_ppt_structure
        
        output_dir = Path("test_output")
        topic = "AI Agent 技术"
        ppt_data = {"metadata": {}, "slides": []}
        
        filepath, _ = save_ppt_structure(json.dumps(ppt_data), output_dir, topic)
        
        # 文件名应为 ASCII
        assert all(c.isascii() for c in filepath.name)
        
        # 清理
        filepath.unlink(missing_ok=True)


class TestPPTGenerator:
    """测试 ppt_generator.py"""
    
    def test_all_slide_types(self):
        """测试所有幻灯片类型"""
        from tech_report_agent.ppt_generator import generate_ppt
        
        ppt_data = {
            "metadata": {"title": "Test", "author": "Test"},
            "slides": [
                {"slide_number": 1, "type": "title", "title": "Title"},
                {"slide_number": 2, "type": "agenda", "title": "Agenda", "content": ["Item 1"]},
                {"slide_number": 3, "type": "content", "title": "Content", "content": ["Point 1"]},
                {"slide_number": 4, "type": "key_findings", "title": "Findings", "content": ["Finding 1"]},
                {"slide_number": 5, "type": "methodology", "title": "Method", "content": ["Step 1"]},
                {"slide_number": 6, "type": "analysis", "title": "Analysis", "content": ["Analysis 1"]},
                {"slide_number": 7, "type": "chart", "title": "Chart", "content": {"chart_type": "column", "title": "Chart", "data": {"labels": ["A"], "values": [1]}}},
                {"slide_number": 8, "type": "swot", "title": "SWOT", "content": {"strengths": ["S1"], "weaknesses": ["W1"], "opportunities": ["O1"], "threats": ["T1"]}},
                {"slide_number": 9, "type": "conclusion", "title": "Conclusion", "content": ["C1"]},
                {"slide_number": 10, "type": "recommendations", "title": "Recs", "content": ["R1"]},
                {"slide_number": 11, "type": "closing", "title": "Thanks", "content": ["Thank you"]},
            ]
        }
        
        output_path = Path("test_output/test_all_types.pptx")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        generate_ppt(ppt_data, output_path)
        
        # 文件应存在
        assert output_path.exists()
        
        # 清理
        output_path.unlink(missing_ok=True)
    
    def test_chart_generation(self):
        """测试图表生成"""
        from tech_report_agent.ppt_generator import generate_ppt
        
        chart_types = ["column", "bar", "line", "pie"]
        
        for chart_type in chart_types:
            ppt_data = {
                "metadata": {"title": "Test"},
                "slides": [{
                    "slide_number": 1,
                    "type": "chart",
                    "title": f"{chart_type} Chart",
                    "content": {
                        "chart_type": chart_type,
                        "title": "Test Chart",
                        "data": {"labels": ["A", "B", "C"], "values": [10, 20, 30]}
                    }
                }]
            }
            
            output_path = Path(f"test_output/test_chart_{chart_type}.pptx")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            generate_ppt(ppt_data, output_path)
            assert output_path.exists(), f"{chart_type} chart generation failed"
            
            output_path.unlink(missing_ok=True)
    
    def test_theme_colors(self):
        """测试主题配色"""
        from tech_report_agent.ppt_generator import generate_ppt
        
        themes = ["tech_blue", "warm_orange", "nature_green"]
        
        ppt_data = {
            "metadata": {"title": "Test"},
            "slides": [{"slide_number": 1, "type": "title", "title": "Test"}]
        }
        
        for theme in themes:
            output_path = Path(f"test_output/test_theme_{theme}.pptx")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            generate_ppt(ppt_data, output_path, theme=theme)
            assert output_path.exists(), f"Theme {theme} generation failed"
            
            output_path.unlink(missing_ok=True)


class TestCrew:
    """测试 crew.py"""
    
    def test_knowledge_files_exist(self):
        """测试知识库文件存在"""
        knowledge_dir = Path(__file__).parent.parent / "knowledge"
        
        # 检查主要知识文件
        expected_files = [
            "academic_analysis/SWOT分析.md",
            "academic_analysis/PEST分析.md",
            "academic_analysis/波特五力分析.md",
            "ppt_skills/PPT设计原则.md",
            "report_templates/技术报告模板.md",
        ]
        
        for file_path in expected_files:
            full_path = knowledge_dir / file_path
            assert full_path.exists(), f"知识文件不存在: {file_path}"
    
    def test_config_files_exist(self):
        """测试配置文件存在"""
        config_dir = Path(__file__).parent.parent / "src" / "tech_report_agent" / "config"
        
        assert (config_dir / "agents.yaml").exists()
        assert (config_dir / "tasks.yaml").exists()


class TestTools:
    """测试工具函数"""
    
    def test_web_search_graceful_degradation(self):
        """测试 web_search 优雅降级（无 API Key）"""
        # 模拟无 API Key 环境
        original_key = os.environ.pop("TAVILY_API_KEY", None)
        
        try:
            from tech_report_agent.tools.search import web_search
            
            # 在无 API Key 时应返回提示信息
            result = web_search.run("test query")
            assert "未配置 TAVILY_API_KEY" in result or "错误" not in result
            
        finally:
            if original_key:
                os.environ["TAVILY_API_KEY"] = original_key
    
    def test_tools_exist(self):
        """测试所有工具函数存在"""
        from tech_report_agent.tools.search import (
            web_search,
            arxiv_search,
            arxiv_paper_detail,
            web_fetch,
            check_data_freshness,
            format_citation,
            get_search_tools
        )
        
        tools = get_search_tools()
        assert len(tools) == 6, f"Expected 6 tools, got {len(tools)}"


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
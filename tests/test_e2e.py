"""
InsightForge E2E 测试

测试内容：
- 核心流程测试
- 边界测试
- 多语言测试
"""

import sys
import os
import json
import time
import pytest
from pathlib import Path

# 设置测试环境变量
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
os.environ["CHROMA_OPENAI_API_KEY"] = os.getenv("CHROMA_OPENAI_API_KEY", "test-key")
os.environ["CHROMA_OPENAI_API_BASE"] = os.getenv("CHROMA_OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")

# 添加源码路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestE2EBasic:
    """基础 E2E 测试"""
    
    @pytest.mark.e2e
    def test_chinese_topic_full_flow(self):
        """中文主题完整流程"""
        from tech_report_agent.main import run
        
        result = run(
            topic="AI Agent 技术",
            verbose=False,
            output_dir="test_output",
            theme="tech_blue",
            language="zh"
        )
        
        # 验证结果
        assert result is not None
        assert "report_path" in result
        assert "ppt_path" in result
        
        # 验证文件存在
        if result.get("report_path"):
            assert Path(result["report_path"]).exists()
        
        if result.get("ppt_path"):
            assert Path(result["ppt_path"]).exists()
    
    @pytest.mark.e2e
    def test_english_topic_full_flow(self):
        """英文主题完整流程"""
        from tech_report_agent.main import run
        
        result = run(
            topic="AI Agent Technology",
            verbose=False,
            output_dir="test_output",
            theme="tech_blue",
            language="en"
        )
        
        assert result is not None


class TestE2EBoundary:
    """边界测试"""
    
    @pytest.mark.e2e
    def test_short_topic(self):
        """简短主题"""
        from tech_report_agent.main import run
        
        result = run(topic="AI", verbose=False, output_dir="test_output")
        assert result is not None
    
    @pytest.mark.e2e
    def test_long_topic(self):
        """长主题"""
        from tech_report_agent.main import run
        
        long_topic = "人工智能技术在企业数字化转型中的应用与挑战分析研究"
        result = run(topic=long_topic, verbose=False, output_dir="test_output")
        assert result is not None
    
    @pytest.mark.e2e
    def test_special_characters_topic(self):
        """特殊字符主题"""
        from tech_report_agent.main import run
        
        special_topic = "AI@Agent#2024!"
        result = run(topic=special_topic, verbose=False, output_dir="test_output")
        assert result is not None


class TestE2EMultiLanguage:
    """多语言测试"""
    
    @pytest.mark.e2e
    def test_chinese_output(self):
        """中文输出"""
        from tech_report_agent.main import run
        
        result = run(
            topic="AI Agent",
            language="zh",
            verbose=False,
            output_dir="test_output"
        )
        
        # 验证报告内容是中文
        if result.get("report_path"):
            content = Path(result["report_path"]).read_text(encoding="utf-8")
            # 应包含中文内容
            assert any('\u4e00' <= c <= '\u9fff' for c in content)
    
    @pytest.mark.e2e
    def test_english_output(self):
        """英文输出"""
        from tech_report_agent.main import run
        
        result = run(
            topic="AI Agent",
            language="en",
            verbose=False,
            output_dir="test_output"
        )
        
        assert result is not None


class TestE2EThemes:
    """主题配色测试"""
    
    @pytest.mark.e2e
    def test_tech_blue_theme(self):
        """tech_blue 主题"""
        from tech_report_agent.main import run
        
        result = run(
            topic="AI Agent",
            theme="tech_blue",
            verbose=False,
            output_dir="test_output"
        )
        assert result is not None
    
    @pytest.mark.e2e
    def test_warm_orange_theme(self):
        """warm_orange 主题"""
        from tech_report_agent.main import run
        
        result = run(
            topic="AI Agent",
            theme="warm_orange",
            verbose=False,
            output_dir="test_output"
        )
        assert result is not None
    
    @pytest.mark.e2e
    def test_nature_green_theme(self):
        """nature_green 主题"""
        from tech_report_agent.main import run
        
        result = run(
            topic="AI Agent",
            theme="nature_green",
            verbose=False,
            output_dir="test_output"
        )
        assert result is not None


class TestE2EPerformance:
    """性能测试"""
    
    @pytest.mark.e2e
    def test_e2e_time(self):
        """端到端时间测试 (< 5分钟)"""
        from tech_report_agent.main import run
        
        start = time.time()
        result = run(topic="AI", verbose=False, output_dir="test_output")
        elapsed = time.time() - start
        
        assert elapsed < 300, f"E2E time {elapsed:.1f}s exceeds 5 minutes"
        print(f"\nE2E time: {elapsed:.1f}s")


# 标记配置
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end (deselect with '-m \"not e2e\"')"
    )


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not e2e"])
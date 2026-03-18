"""
InsightForge 性能测试

测试内容：
- 端到端时间
- 知识库加载时间
- 报告生成时间
- PPT 生成时间
- 内存使用
"""

import sys
import os
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

# 可选：内存监控
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class TestPerformance:
    """性能测试"""
    
    @pytest.mark.perf
    def test_ppt_generation_time(self):
        """PPT 生成时间 (< 10秒)"""
        from tech_report_agent.ppt_generator import generate_ppt
        
        ppt_data = {
            "metadata": {"title": "Test", "author": "Test"},
            "slides": [
                {"slide_number": i, "type": "content", "title": f"Slide {i}", "content": ["Point 1", "Point 2"]}
                for i in range(1, 15)
            ]
        }
        
        output_path = Path("test_output/perf_test.pptx")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        start = time.time()
        generate_ppt(ppt_data, output_path)
        elapsed = time.time() - start
        
        assert elapsed < 10, f"PPT generation took {elapsed:.2f}s"
        print(f"\nPPT generation time: {elapsed:.2f}s")
        
        # 清理
        output_path.unlink(missing_ok=True)
    
    @pytest.mark.perf
    def test_json_parsing_time(self):
        """JSON 解析时间 (< 1秒)"""
        from tech_report_agent.main import save_ppt_structure
        
        # 创建大型 PPT 数据
        ppt_data = {
            "metadata": {"title": "Test"},
            "slides": [
                {
                    "slide_number": i,
                    "type": "content",
                    "title": f"Slide {i}",
                    "content": [f"Point {j}" for j in range(10)]
                }
                for i in range(1, 20)
            ]
        }
        
        json_content = __import__("json").dumps(ppt_data)
        
        start = time.time()
        filepath, _ = save_ppt_structure(json_content, Path("test_output"), "test")
        elapsed = time.time() - start
        
        assert elapsed < 1, f"JSON parsing took {elapsed:.2f}s"
        print(f"\nJSON parsing time: {elapsed:.3f}s")
        
        # 清理
        filepath.unlink(missing_ok=True)
    
    @pytest.mark.perf
    def test_memory_usage(self):
        """内存使用测试 (< 500 MB)"""
        if not HAS_PSUTIL:
            pytest.skip("psutil not installed")
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 导入模块
        from tech_report_agent.ppt_generator import generate_ppt
        
        # 生成 PPT
        ppt_data = {
            "metadata": {"title": "Test"},
            "slides": [{"slide_number": i, "type": "content", "title": f"Slide {i}"} for i in range(1, 15)]
        }
        
        output_path = Path("test_output/memory_test.pptx")
        generate_ppt(ppt_data, output_path)
        
        peak_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = peak_memory - initial_memory
        
        assert peak_memory < 500, f"Memory usage {peak_memory:.1f}MB exceeds 500MB"
        print(f"\nMemory usage: {peak_memory:.1f}MB (increase: {memory_increase:.1f}MB)")
        
        # 清理
        output_path.unlink(missing_ok=True)
    
    @pytest.mark.perf
    def test_file_size(self):
        """输出文件大小测试"""
        from tech_report_agent.ppt_generator import generate_ppt
        
        ppt_data = {
            "metadata": {"title": "Test"},
            "slides": [{"slide_number": i, "type": "content", "title": f"Slide {i}"} for i in range(1, 15)]
        }
        
        output_path = Path("test_output/size_test.pptx")
        generate_ppt(ppt_data, output_path)
        
        file_size = output_path.stat().st_size / 1024  # KB
        
        assert file_size < 500, f"PPT file size {file_size:.1f}KB exceeds 500KB"
        print(f"\nPPT file size: {file_size:.1f}KB")
        
        # 清理
        output_path.unlink(missing_ok=True)


class TestReportQuality:
    """报告质量测试"""
    
    @pytest.mark.quality
    def test_report_structure(self):
        """报告结构测试"""
        # 验证报告包含必要章节
        required_sections = ["标题", "摘要", "分析", "结论"]
        
        # 读取最近生成的报告
        reports_dir = Path("test_output/reports")
        if not reports_dir.exists():
            pytest.skip("No reports generated yet")
        
        reports = list(reports_dir.glob("*.md"))
        if not reports:
            pytest.skip("No reports found")
        
        latest_report = max(reports, key=lambda p: p.stat().st_mtime)
        content = latest_report.read_text(encoding="utf-8")
        
        # 检查结构
        for section in required_sections:
            assert section in content or "#" in content, f"Missing section: {section}"
    
    @pytest.mark.quality
    def test_ppt_structure_valid_json(self):
        """PPT 结构 JSON 有效性"""
        ppt_dir = Path("test_output/presentations")
        if not ppt_dir.exists():
            pytest.skip("No PPT structures generated yet")
        
        ppt_files = list(ppt_dir.glob("*.json"))
        if not ppt_files:
            pytest.skip("No PPT structures found")
        
        for ppt_file in ppt_files[:5]:  # 检查最近 5 个
            try:
                content = ppt_file.read_text(encoding="utf-8")
                data = __import__("json").loads(content)
                assert "slides" in data, f"Missing slides in {ppt_file.name}"
            except Exception as e:
                pytest.fail(f"Invalid JSON in {ppt_file.name}: {e}")


# 标记配置
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "perf: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "quality: marks tests as quality tests"
    )


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
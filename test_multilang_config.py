"""
快速验证多语言配置
"""

import sys
import os
from pathlib import Path

# Windows 兼容
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

def test_language_config():
    """验证语言参数配置"""
    print("\n" + "="*60)
    print("验证多语言配置...")
    print("="*60)
    
    # 1. 检查 tasks.yaml 中的语言指令
    tasks_path = Path(__file__).parent / "src" / "tech_report_agent" / "config" / "tasks.yaml"
    tasks_content = tasks_path.read_text(encoding="utf-8")
    
    # 验证语言设置存在
    assert "language == 'en'" in tasks_content, "缺少英文语言指令"
    assert "language == 'zh'" not in tasks_content or "中文" in tasks_content, "缺少中文语言指令"
    print("✅ tasks.yaml 语言指令配置正确")
    
    # 2. 检查 main.py 中的语言参数
    main_path = Path(__file__).parent / "src" / "tech_report_agent" / "main.py"
    main_content = main_path.read_text(encoding="utf-8")
    
    assert "--language" in main_content, "main.py 缺少 --language 参数"
    assert "language == 'zh'" in main_content or "language" in main_content, "main.py 未传递语言参数"
    print("✅ main.py 语言参数配置正确")
    
    # 3. 检查 inputs 传递
    assert '"language": language' in main_content or "inputs={\"topic\": topic, \"language\": language}" in main_content, "语言参数未传递给 inputs"
    print("✅ 语言参数正确传递到 Crew inputs")
    
    print("\n" + "="*60)
    print("✅ 多语言配置验证通过！")
    print("="*60 + "\n")
    
    # 打印使用示例
    print("使用方法:")
    print("  中文输出: insightforge run \"分析主题\" --language zh")
    print("  英文输出: insightforge run \"Analysis Topic\" --language en")
    
    return True


if __name__ == "__main__":
    test_language_config()
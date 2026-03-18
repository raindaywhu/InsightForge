#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""详细 E2E 测试，捕获所有日志"""

import sys
import os
import json
import logging

# 设置 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.chdir(r'C:\Users\raind\projects\InsightForge')

from dotenv import load_dotenv
load_dotenv()

# 启用详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

print('=' * 60)
print('详细 E2E 测试')
print('=' * 60)

# 检查环境
print('\n[1] 环境检查:')
print(f'  OPENAI_API_KEY: {"已设置" if os.getenv("OPENAI_API_KEY") else "未设置"}')
print(f'  OPENAI_API_BASE: {os.getenv("OPENAI_API_BASE", "未设置")}')
print(f'  OPENAI_MODEL_NAME: {os.getenv("OPENAI_MODEL_NAME", "qwen-plus")}')

# 导入和初始化
print('\n[2] 初始化 Crew...')
try:
    from tech_report_agent.crew import TechReportCrew
    
    crew_instance = TechReportCrew()
    crew = crew_instance.crew()
    
    print(f'  ✓ Agents: {len(crew.agents)}')
    for a in crew.agents:
        print(f'    - {a.role}')
    
    print(f'  ✓ Tasks: {len(crew.tasks)}')
    for t in crew.tasks:
        print(f'    - {t.name}')
    
except Exception as e:
    print(f'  ✗ 初始化失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 执行测试
print('\n[3] 执行 Crew (topic="测试")...')
print('-' * 60)

try:
    result = crew.kickoff(inputs={'topic': '测试', 'language': 'zh'})
    print('-' * 60)
    
    print('\n[4] 分析结果:')
    result_str = str(result)
    print(f'  结果长度: {len(result_str)} 字符')
    
    # 检查是否是 JSON
    result_str = result_str.strip()
    if result_str.startswith('{') or result_str.startswith('```'):
        print('  结果类型: JSON/PPT 结构')
        
        # 移除可能的 markdown 代码块
        if result_str.startswith('```'):
            lines = result_str.split('\n')
            result_str = '\n'.join(lines[1:-1])
        
        try:
            ppt_json = json.loads(result_str)
            print(f'  ✓ JSON 解析成功')
            print(f'  ✓ 幻灯片数量: {len(ppt_json.get("slides", []))}')
            
            # 保存结果
            output_file = 'test_output/e2e_result.json'
            os.makedirs('test_output', exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(ppt_json, f, ensure_ascii=False, indent=2)
            print(f'  ✓ 结果已保存: {output_file}')
        except json.JSONDecodeError as e:
            print(f'  ⚠ JSON 解析失败: {e}')
            print(f'  结果前200字符: {result_str[:200]}')
    else:
        print('  结果类型: Markdown 报告')
        
        # 保存报告
        output_file = 'test_output/e2e_report.md'
        os.makedirs('test_output', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result_str)
        print(f'  ✓ 报告已保存: {output_file}')
    
    print('\n' + '=' * 60)
    print('✅ E2E 测试成功完成!')
    print('=' * 60)
    
except Exception as e:
    print('-' * 60)
    print(f'\n❌ 执行失败: {e}')
    import traceback
    traceback.print_exc()
    
    print('\n[DEBUG] 尝试分析错误...')
    print(f'  错误类型: {type(e).__name__}')
    print(f'  错误消息: {str(e)}')
    
    sys.exit(1)
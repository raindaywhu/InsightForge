#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""E2E 调试脚本"""

import sys
import os

# 设置 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# 切换到项目目录
os.chdir(r'C:\Users\raind\projects\InsightForge')

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

print('=' * 60)
print('InsightForge E2E 调试')
print('=' * 60)

# 检查环境
print('\n[1] 环境变量检查:')
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('OPENAI_BASE_URL')
tavily_key = os.getenv('TAVILY_API_KEY')

print(f'  OPENAI_API_KEY: {"已设置 (" + api_key[:10] + "...)" if api_key else "未设置"}')
print(f'  OPENAI_BASE_URL: {base_url or "未设置"}')
print(f'  TAVILY_API_KEY: {"已设置" if tavily_key else "未设置"}')

# 导入模块
print('\n[2] 模块导入:')
try:
    from tech_report_agent.crew import TechReportCrew
    print('  ✓ TechReportCrew 导入成功')
except Exception as e:
    print(f'  ✗ 导入失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 初始化
print('\n[3] 初始化 Crew:')
try:
    crew_instance = TechReportCrew()
    crew = crew_instance.crew()
    print(f'  ✓ Crew 创建成功')
    print(f'    - Agents: {len(crew.agents)}')
    print(f'    - Tasks: {len(crew.tasks)}')
    
    # 列出 agents
    for i, agent in enumerate(crew.agents):
        print(f'      [{i+1}] {agent.role}')
    
    # 列出 tasks
    for i, task in enumerate(crew.tasks):
        print(f'      [{i+1}] {task.name}')
        
except Exception as e:
    print(f'  ✗ 初始化失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 执行测试
print('\n[4] 执行 Crew (简单测试):')
print('  Topic: "测试"')
print('  Language: zh')
print('-' * 60)

try:
    result = crew.kickoff(inputs={'topic': '测试', 'language': 'zh'})
    print('-' * 60)
    print('  ✓ Crew 执行成功')
    print(f'  结果长度: {len(str(result))} 字符')
    
    # 保存结果
    output_dir = 'test_output'
    os.makedirs(output_dir, exist_ok=True)
    
    result_file = os.path.join(output_dir, 'debug_result.md')
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(str(result))
    print(f'  结果已保存: {result_file}')
    
except Exception as e:
    print('-' * 60)
    print(f'  ✗ Crew 执行失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\n' + '=' * 60)
print('E2E 测试完成!')
print('=' * 60)
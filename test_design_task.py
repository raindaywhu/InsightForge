#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试 design_task 单独执行"""

import sys
import os
import json

# 设置 UTF-8 编码
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

os.chdir(r'C:\Users\raind\projects\InsightForge')

from dotenv import load_dotenv
load_dotenv()

print('=' * 60)
print('测试 design_task 单独执行')
print('=' * 60)

# 创建一个模拟的分析报告作为输入
test_report = """
# 测试技术分析报告

## 执行摘要

本报告针对"测试"主题进行深度分析，主要发现如下：
1. 测试行业正处于快速转型期
2. AI驱动的测试技术成为主流趋势
3. 测试人才结构面临重大调整

## 一、分析框架

本次分析采用PEST和SWOT分析框架。

## 二、详细分析

### 2.1 PEST分析
- 政治因素：数据安全法规趋严
- 经济因素：市场规模持续增长
- 社会因素：用户体验要求提升
- 技术因素：AI技术广泛应用

### 2.2 SWOT分析
- 优势：方法论成熟，工具生态丰富
- 劣势：人才结构失衡，测试数据管理薄弱
- 机会：AI赋能测试，测试左移实践
- 威胁：技术变革加速，技能过时风险

## 三、结论与建议

### 3.1 核心结论
1. 测试左移是质量效能提升的核心路径
2. AI将重塑测试方法论
3. 测试人才转型迫在眉睫

### 3.2 建议
- 短期：开展测试现状评估，启动自动化测试
- 中期：构建测试金字塔，集成CI/CD流水线
- 长期：建设质量工程体系，深度应用AI技术
"""

print('\n[1] 导入模块...')
try:
    from tech_report_agent.crew import TechReportCrew
    from tech_report_agent.agents import TechnicalAnalyst, PresentationDesigner
    from tech_report_agent.tasks import TechReportTasks
    print('  ✓ 导入成功')
except Exception as e:
    print(f'  ✗ 导入失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\n[2] 创建 Agent 和 Task...')
try:
    # 创建 designer agent
    designer = PresentationDesigner()
    agent = designer.create()
    print(f'  ✓ Agent 创建成功: {agent.role}')
    
    # 创建 task
    tasks = TechReportTasks()
    design_task = tasks.design_task(agent, test_report, 'zh')
    print(f'  ✓ Task 创建成功: {design_task.name}')
    
except Exception as e:
    print(f'  ✗ 创建失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\n[3] 执行 Task...')
try:
    from crewai import Crew
    
    crew = Crew(
        agents=[agent],
        tasks=[design_task],
        verbose=True
    )
    
    result = crew.kickoff()
    print('\n' + '=' * 60)
    print('执行结果:')
    print('=' * 60)
    print(result)
    
    # 尝试解析 JSON
    print('\n[4] 验证 JSON 格式...')
    try:
        result_str = str(result).strip()
        # 移除可能的 markdown 代码块标记
        if result_str.startswith('```'):
            result_str = result_str.split('\n', 1)[1]  # 移除第一行
        if result_str.endswith('```'):
            result_str = result_str.rsplit('\n', 1)[0]  # 移除最后一行
        
        ppt_json = json.loads(result_str)
        print(f'  ✓ JSON 解析成功')
        print(f'  ✓ 幻灯片数量: {len(ppt_json.get("slides", []))}')
        
        # 保存结果
        output_file = 'test_output/test_design_result.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ppt_json, f, ensure_ascii=False, indent=2)
        print(f'  ✓ 结果已保存: {output_file}')
        
    except json.JSONDecodeError as e:
        print(f'  ✗ JSON 解析失败: {e}')
        print(f'  结果前100字符: {result_str[:100]}')
    
except Exception as e:
    print(f'  ✗ 执行失败: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)

print('\n' + '=' * 60)
print('测试完成!')
print('=' * 60)
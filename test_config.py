#!/usr/bin/env python
"""Test Agent and Task configuration"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env first
load_dotenv(Path(__file__).parent / '.env')

print('=' * 50)
print('Agent & Task Configuration Test')
print('=' * 50)

sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from tech_report_agent.crew import TechReportCrew
    
    print('\n[INFO] Creating TechReportCrew...')
    crew_instance = TechReportCrew()
    
    # Test 1: Agent creation
    print('\n--- Test 1: Agent Configuration ---')
    analyst = crew_instance.technical_analyst()
    print(f'[OK] Agent: {analyst.role}')
    print(f'[OK] Goal: {analyst.goal[:50]}...')
    print(f'[OK] Backstory: {analyst.backstory[:50]}...')
    
    designer = crew_instance.presentation_designer()
    print(f'[OK] Agent: {designer.role}')
    print(f'[OK] Goal: {designer.goal[:50]}...')
    
    # Test 2: Task creation
    print('\n--- Test 2: Task Configuration ---')
    analyze = crew_instance.analyze_task()
    print(f'[OK] Task description: {analyze.description[:50]}...')
    print(f'[OK] Expected output: {analyze.expected_output[:50]}...')
    
    design = crew_instance.design_task()
    print(f'[OK] Task description: {design.description[:50]}...')
    
    # Test 3: Crew creation
    print('\n--- Test 3: Crew Assembly ---')
    crew = crew_instance.crew()
    print(f'[OK] Agents: {len(crew.agents)}')
    print(f'[OK] Tasks: {len(crew.tasks)}')
    print(f'[OK] Process: {crew.process}')
    print(f'[OK] Memory: {crew.memory}')
    print(f'[OK] Knowledge sources: {len(crew_instance.knowledge_sources)}')
    
    print('\n' + '=' * 50)
    print('[SUCCESS] All configuration tests passed!')
    print('=' * 50)
    
except Exception as e:
    print(f'[FAIL] Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
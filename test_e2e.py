#!/usr/bin/env python
"""End-to-end test: Generate a simple report"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env first
load_dotenv(Path(__file__).parent / '.env')

print('=' * 50)
print('End-to-End Test: Report Generation')
print('=' * 50)

sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from tech_report_agent.crew import TechReportCrew
    from tech_report_agent.main import TechReportCrew as MainCrew
    
    # Test with a simple topic
    topic = "AI Agent 技术发展趋势"
    
    print(f'\n[INFO] Testing with topic: {topic}')
    print('[INFO] This may take a few minutes...\n')
    
    # Create crew instance
    crew_instance = TechReportCrew()
    
    # Build the crew
    crew = crew_instance.crew()
    
    # Prepare inputs
    inputs = {
        'topic': topic
    }
    
    # Run the crew
    print('[INFO] Starting crew execution...')
    result = crew.kickoff(inputs=inputs)
    
    print('\n' + '=' * 50)
    print('[SUCCESS] Report generated!')
    print('=' * 50)
    
    # CrewOutput is an object, get the raw output
    if hasattr(result, 'raw'):
        print(f'\nResult preview:\n{result.raw[:500]}...')
    elif hasattr(result, 'result'):
        print(f'\nResult preview:\n{str(result.result)[:500]}...')
    else:
        print(f'\nResult: {result}')
    
except Exception as e:
    print(f'[FAIL] Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
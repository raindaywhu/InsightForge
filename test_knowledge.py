#!/usr/bin/env python
"""Test complete knowledge loading with vector storage"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env first
load_dotenv(Path(__file__).parent / '.env')

# Verify environment variables
print('=' * 50)
print('Environment Check')
print('=' * 50)
api_key = os.getenv('OPENAI_API_KEY')
api_base = os.getenv('OPENAI_API_BASE')
print(f'OPENAI_API_KEY: {api_key[:10]}...{api_key[-4:] if api_key else "NOT SET"}')
print(f'OPENAI_API_BASE: {api_base}')

# Test complete crew initialization
print('\n' + '=' * 50)
print('Testing Crew Initialization with Knowledge')
print('=' * 50)

sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from tech_report_agent.crew import TechReportCrew
    
    print('[INFO] Creating TechReportCrew instance...')
    crew = TechReportCrew()
    
    print(f'[OK] Knowledge sources loaded: {len(crew.knowledge_sources)} files')
    
    # Test agent creation
    analyst = crew.technical_analyst()
    print(f'[OK] Agent created: {analyst.role}')
    
    print('\n' + '=' * 50)
    print('[SUCCESS] Knowledge loading test passed!')
    print('=' * 50)
    
except Exception as e:
    print(f'[FAIL] Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
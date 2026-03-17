#!/usr/bin/env python
"""Verify InsightForge environment setup"""

import crewai
import chromadb
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

print('=' * 50)
print('InsightForge Environment Verification')
print('=' * 50)

# 1. Verify core libraries
print(f'\n[OK] crewai: {crewai.__version__}')
print(f'[OK] chromadb: {chromadb.__version__}')

# 2. Verify API Key
api_key = os.getenv('DASHSCOPE_API_KEY')
if api_key:
    print(f'[OK] DASHSCOPE_API_KEY: {api_key[:10]}...{api_key[-4:]}')
else:
    print('[FAIL] DASHSCOPE_API_KEY not found in .env')
    exit(1)

# 3. Test DashScope API connection
print('\nTesting DashScope API connection...')
try:
    client = OpenAI(
        api_key=api_key,
        base_url='https://dashscope.aliyuncs.com/compatible-mode/v1'
    )
    response = client.chat.completions.create(
        model='qwen-plus',  # DashScope supports qwen series
        messages=[{'role': 'user', 'content': 'Hello, respond with just OK'}],
        max_tokens=10
    )
    print(f'[OK] DashScope API response: {response.choices[0].message.content}')
except Exception as e:
    print(f'[FAIL] DashScope API error: {e}')
    exit(1)

print('\n' + '=' * 50)
print('[SUCCESS] All verifications passed!')
print('=' * 50)
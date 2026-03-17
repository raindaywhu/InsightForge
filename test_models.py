#!/usr/bin/env python
"""Test which models work with DashScope OpenAI compatible mode"""

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv('DASHSCOPE_API_KEY')
base_url = 'https://dashscope.aliyuncs.com/compatible-mode/v1'

client = OpenAI(api_key=api_key, base_url=base_url)

# Test models
models_to_test = [
    'qwen-turbo',
    'qwen-plus', 
    'qwen-max',
    'qwen2.5-72b-instruct',
    'qwen2.5-32b-instruct',
    'glm-4',
    'glm-4-plus',
]

print('Testing DashScope OpenAI compatible models:')
print('=' * 50)

for model in models_to_test:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': 'Say OK'}],
            max_tokens=10
        )
        print(f'[OK] {model}: {response.choices[0].message.content}')
    except Exception as e:
        error_msg = str(e)[:80]
        print(f'[FAIL] {model}: {error_msg}')

print('=' * 50)
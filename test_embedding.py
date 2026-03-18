"""
Test DashScope embedding API
"""

import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

print("Testing embedding API...")
try:
    response = client.embeddings.create(
        model="text-embedding-v3",
        input="Hello world"
    )
    print(f"Success! Embedding dimension: {len(response.data[0].embedding)}")
except Exception as e:
    print(f"Error: {e}")
#!/usr/bin/env python
"""Debug knowledge embedding issue"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env first
load_dotenv(Path(__file__).parent / '.env')

print('=' * 50)
print('Debug: Knowledge Embedding')
print('=' * 50)

# Check environment
api_key = os.getenv('OPENAI_API_KEY')
api_base = os.getenv('OPENAI_API_BASE')
print(f'OPENAI_API_KEY: {api_key[:10]}...{api_key[-4:] if api_key else "NOT SET"}')
print(f'OPENAI_API_BASE: {api_base}')

# Test embedding directly
print('\n--- Test Direct Embedding ---')
from openai import OpenAI

client = OpenAI(api_key=api_key, base_url=api_base)

try:
    response = client.embeddings.create(
        model='text-embedding-v3',
        input='Hello world'
    )
    print(f'[OK] Embedding dimension: {len(response.data[0].embedding)}')
except Exception as e:
    print(f'[FAIL] Embedding error: {e}')

# Test ChromaDB
print('\n--- Test ChromaDB ---')
try:
    import chromadb
    from chromadb.config import Settings
    
    # Use ephemeral mode (in-memory)
    client = chromadb.EphemeralClient()
    print(f'[OK] ChromaDB version: {chromadb.__version__}')
    print(f'[OK] Ephemeral client created')
    
    # Try to create a collection
    collection = client.create_collection(name='test')
    print(f'[OK] Collection created: {collection.name}')
    
except Exception as e:
    print(f'[FAIL] ChromaDB error: {e}')
    import traceback
    traceback.print_exc()

print('\n' + '=' * 50)
print('Debug complete')
print('=' * 50)
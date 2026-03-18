"""
Test knowledge base RAG functionality
"""
import os
import ssl
import urllib.request

# Check SSL context
print("=" * 60)
print("SSL Diagnosis")
print("=" * 60)

print(f"SSL version: {ssl.OPENSSL_VERSION}")
print(f"SSL default verify paths: {ssl.get_default_verify_paths()}")

# Test basic connectivity
print("\n" + "=" * 60)
print("Testing HTTPS connections")
print("=" * 60)

test_urls = [
    "https://dashscope.aliyuncs.com",
    "https://api.openai.com",
    "https://www.google.com",
]

for url in test_urls:
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ {url}: {response.status}")
    except Exception as e:
        print(f"❌ {url}: {e}")

# Test CrewAI knowledge source
print("\n" + "=" * 60)
print("Testing CrewAI Knowledge Source")
print("=" * 60)

try:
    from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
    
    test_content = "This is a test knowledge content for RAG."
    ks = StringKnowledgeSource(content=test_content)
    print(f"✅ StringKnowledgeSource created: {type(ks)}")
    print(f"   Content length: {len(test_content)}")
    
    # Try to access embeddings (this is where SSL error might occur)
    print("\n   Attempting to access embeddings...")
    # The knowledge source doesn't have direct access to embeddings
    # It's used by CrewAI internally
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")

# Test ChromaDB
print("\n" + "=" * 60)
print("Testing ChromaDB")
print("=" * 60)

try:
    import chromadb
    from chromadb.config import Settings
    
    # Create a local ephemeral client
    client = chromadb.EphemeralClient()
    print(f"✅ ChromaDB client created: {client}")
    
    # Create a test collection
    collection = client.get_or_create_collection("test_collection")
    print(f"✅ Collection created: {collection.name}")
    
    # Add a test document
    collection.add(
        documents=["This is a test document"],
        metadatas=[{"source": "test"}],
        ids=["test_1"]
    )
    print(f"✅ Document added")
    
    # Query
    results = collection.query(
        query_texts=["test"],
        n_results=1
    )
    print(f"✅ Query successful: {results}")
    
except Exception as e:
    print(f"❌ ChromaDB Error: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("Diagnosis Complete")
print("=" * 60)
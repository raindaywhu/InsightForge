"""Test ONNX embedder configuration"""
import sys
import os

# Fix GBK encoding issue
os.environ['PYTHONIOENCODING'] = 'utf-8'

sys.path.insert(0, r'C:\Users\raind\projects\InsightForge\src')

print("Testing ONNX embedder...")

try:
    from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
    from crewai.knowledge.storage.knowledge_storage import KnowledgeStorage
    
    # Create knowledge storage with ONNX embedder
    storage = KnowledgeStorage(embedder={'provider': 'onnx'})
    print("[OK] KnowledgeStorage created with ONNX embedder")
    
    # Create knowledge source
    test_content = """
    SWOT Analysis Framework
    
    SWOT is a strategic planning technique used to identify:
    - Strengths: Internal positive attributes
    - Weaknesses: Internal negative attributes  
    - Opportunities: External positive factors
    - Threats: External negative factors
    """
    
    ks = StringKnowledgeSource(
        content=test_content,
        storage=storage
    )
    print("[OK] StringKnowledgeSource created")
    
    # Test search
    print("\nTesting search...")
    results = ks.search("What is SWOT?")
    print(f"[OK] Search returned {len(results)} results")
    if results:
        print(f"First result: {results[0].get('content', 'N/A')[:100]}...")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
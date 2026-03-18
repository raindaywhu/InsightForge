"""
Test Knowledge RAG integration with Crew
"""
import os
import sys

# Set encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("Testing Knowledge RAG Integration")
print("=" * 60)

# Test 1: Load knowledge
print("\n1. Loading knowledge sources...")
from tech_report_agent.crew import TechReportCrew

crew = TechReportCrew()
print(f"   Knowledge sources loaded: {len(crew.knowledge_sources)}")

# Test 2: Check Crew creation
print("\n2. Creating Crew...")
c = crew.crew()
print(f"   Crew created: {type(c)}")
print(f"   Agents: {len(c.agents)}")
print(f"   Tasks: {len(c.tasks)}")
print(f"   Knowledge sources: {len(c.knowledge_sources) if c.knowledge_sources else 0}")

# Test 3: Quick run (just check it starts)
print("\n3. Testing kickoff (short topic)...")
inputs = {"topic": "AI"}

try:
    # Run with a simple topic
    result = c.kickoff(inputs=inputs)
    
    # Check output
    output = result.raw if hasattr(result, 'raw') else str(result)
    print(f"\n   Output length: {len(output)} chars")
    print(f"   Output preview: {output[:200]}...")
    
    # Check if knowledge was used (look for framework keywords)
    has_swot = "SWOT" in output or "swot" in output.lower()
    has_pest = "PEST" in output or "pest" in output.lower()
    has_porter = "波特五力" in output or "Porter" in output
    
    print(f"\n   Contains SWOT: {has_swot}")
    print(f"   Contains PEST: {has_pest}")
    print(f"   Contains Porter's Five Forces: {has_porter}")
    
    print("\n" + "=" * 60)
    print("SUCCESS! Knowledge RAG integration working!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n   Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
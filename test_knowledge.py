"""Test full knowledge integration"""
import sys
import os

# Fix GBK encoding issue
os.environ['PYTHONIOENCODING'] = 'utf-8'

sys.path.insert(0, r'C:\Users\raind\projects\InsightForge\src')

print("Testing knowledge integration...")

try:
    from tech_report_agent.crew import TechReportCrew
    
    # Create crew
    print("Creating TechReportCrew...")
    crew_instance = TechReportCrew()
    print(f"[OK] Knowledge sources loaded: {len(crew_instance.knowledge_sources)}")
    
    # Check crew configuration
    crew = crew_instance.crew()
    print(f"[OK] Crew created with {len(crew.agents)} agents and {len(crew.tasks)} tasks")
    
    # Check if knowledge is enabled
    print(f"Knowledge sources in crew: {crew.knowledge_sources}")
    print(f"Embedder config: {crew.embedder}")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
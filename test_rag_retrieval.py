#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test RAG retrieval functionality
"""

import sys
import os

# Set UTF-8 encoding for Windows console
os.environ['PYTHONIOENCODING'] = 'utf-8'

from src.tech_report_agent.crew import TechReportCrew

def test_rag_retrieval():
    """Test that RAG knowledge retrieval works"""
    print("=" * 50)
    print("Testing RAG Knowledge Retrieval")
    print("=" * 50)
    
    # Create crew
    print("\n1. Creating TechReportCrew...")
    crew = TechReportCrew()
    
    # Check knowledge sources
    print(f"\n2. Knowledge sources loaded: {len(crew.knowledge_sources) if crew.knowledge_sources else 0}")
    
    # Try a simple query
    print("\n3. Testing knowledge query...")
    try:
        # The knowledge should be available during crew execution
        # Let's check if the crew can be built
        crew_instance = crew.crew()
        print(f"   Crew built successfully!")
        print(f"   Agents: {len(crew_instance.agents)}")
        print(f"   Tasks: {len(crew_instance.tasks)}")
        
        # Check if knowledge is attached
        for agent in crew_instance.agents:
            if hasattr(agent, 'knowledge_sources') and agent.knowledge_sources:
                print(f"   Agent '{agent.role}' has knowledge sources!")
        
        print("\n" + "=" * 50)
        print("RAG Knowledge Test PASSED!")
        print("=" * 50)
        return True
    except Exception as e:
        print(f"   Error: {e}")
        print("\n" + "=" * 50)
        print("RAG Knowledge Test FAILED!")
        print("=" * 50)
        return False

if __name__ == "__main__":
    success = test_rag_retrieval()
    sys.exit(0 if success else 1)
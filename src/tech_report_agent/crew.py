"""
InsightForge Crew Definition

Defines Agent, Task and Crew, manages knowledge loading.

RAG Knowledge Architecture:
- technical_analyst: academic_analysis + report_templates (analysis frameworks)
- presentation_designer: ppt_skills (design principles, chart types, color guides)

Agent Collaboration (Hierarchical):
- report_manager: 协调分析师和设计师，评审质量，请求补充
- technical_analyst: 深度分析，输出报告
- presentation_designer: 设计 PPT，呈现洞察
"""

import os
from pathlib import Path
from typing import List, Dict, Any

from crewai import Agent, Crew, Task, Process, LLM
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.knowledge.storage.knowledge_storage import KnowledgeStorage

from crewai.project import CrewBase, agent, crew, task


# DashScope embedder configuration (OpenAI-compatible API)
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", os.getenv("OPENAI_API_KEY", ""))
EMBEDDING_API_BASE = os.getenv("EMBEDDING_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
EMBEDDING_MODEL = os.getenv("DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v3")

# Set environment variables for CrewAI's internal OpenAI client
os.environ["OPENAI_EMBEDDING_MODEL"] = EMBEDDING_MODEL
os.environ["OPENAI_EMBEDDING_API_KEY"] = EMBEDDING_API_KEY
os.environ["OPENAI_EMBEDDING_API_BASE"] = EMBEDDING_API_BASE

# ChromaDB uses CHROMA_ prefix for OpenAI embedding function
os.environ["CHROMA_OPENAI_API_KEY"] = EMBEDDING_API_KEY
os.environ["CHROMA_OPENAI_API_BASE"] = EMBEDDING_API_BASE
os.environ["CHROMA_OPENAI_EMBEDDING_MODEL"] = EMBEDDING_MODEL

DASHSCOPE_EMBEDDER_CONFIG = {
    "provider": "openai",
    "config": {
        "model_name": EMBEDDING_MODEL,
        "api_key": EMBEDDING_API_KEY,
        "api_base": EMBEDDING_API_BASE
    }
}


@CrewBase
class TechReportCrew:
    """
    Tech Report Generation Crew
    
    Three agents collaborate with dedicated knowledge sources:
    1. Report Manager - Coordinates workflow, reviews quality, requests revisions
    2. Technical Analyst - Uses analysis frameworks (SWOT, PEST, Porter's, etc.)
    3. Presentation Designer - Uses PPT design principles
    
    Collaboration Mode: Hierarchical Process
    - Manager assigns tasks and reviews output
    - Can request analyst to supplement information
    - Iterates until quality standard is met
    
    RAG Knowledge Categories:
    - academic_analysis/ → Technical Analyst (analysis frameworks)
    - report_templates/  → Technical Analyst (report structure)
    - ppt_skills/        → Presentation Designer (design principles)
    """
    
    agents_config: str = 'config/agents.yaml'
    tasks_config: str = 'config/tasks.yaml'
    
    def __init__(self):
        """Initialize: Configure LLM and Knowledge Storage"""
        # Knowledge storage with DashScope embeddings
        self.knowledge_storage = self._create_knowledge_storage()
        self.knowledge_by_category = self._load_knowledge_by_category()
        self.knowledge_sources = self._get_all_knowledge_sources()
        
        self.llm = self._create_llm()
    
    def _create_llm(self) -> LLM:
        """Create LLM instance with DashScope configuration"""
        model = os.getenv('OPENAI_MODEL_NAME', 'qwen-plus')
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_API_BASE', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        
        return LLM(
            model=f"openai/{model}",
            api_key=api_key,
            base_url=base_url
        )
    
    def _create_knowledge_storage(self) -> KnowledgeStorage:
        """Create KnowledgeStorage with DashScope embeddings."""
        return KnowledgeStorage(embedder=DASHSCOPE_EMBEDDER_CONFIG)
    
    def _load_knowledge_by_category(self) -> Dict[str, List[StringKnowledgeSource]]:
        """
        Load knowledge base by category for different agents.
        
        Categories:
        - 'analyst': academic_analysis/ + report_templates/ → Technical Analyst
        - 'designer': ppt_skills/ → Presentation Designer
        """
        knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
        
        categories = {
            'analyst': ['academic_analysis', 'report_templates'],  # 分析方法论 + 报告模板
            'designer': ['ppt_skills']  # PPT 设计技巧
        }
        
        result = {}
        
        for agent_type, subdirs in categories.items():
            sources = []
            for subdir in subdirs:
                subdir_path = knowledge_dir / subdir
                if subdir_path.exists():
                    for md_file in subdir_path.glob("*.md"):
                        try:
                            content = md_file.read_text(encoding="utf-8")
                            if content.strip():
                                ks = StringKnowledgeSource(
                                    content=content,
                                    storage=self.knowledge_storage
                                )
                                sources.append(ks)
                                print(f"[OK] {agent_type}: {subdir}/{md_file.name}")
                        except Exception as e:
                            print(f"[WARN] Failed to load {md_file}: {e}")
            result[agent_type] = sources
        
        # Print summary
        total = sum(len(v) for v in result.values())
        print(f"\n[INFO] Knowledge loaded: {total} files total")
        print(f"       - Analyst: {len(result.get('analyst', []))} files")
        print(f"       - Designer: {len(result.get('designer', []))} files\n")
        
        return result
    
    def _get_all_knowledge_sources(self) -> List[StringKnowledgeSource]:
        """Combine all knowledge sources for Crew-level config."""
        all_sources = []
        for sources in self.knowledge_by_category.values():
            all_sources.extend(sources)
        return all_sources
    
    @agent
    def report_manager(self) -> Agent:
        """
        Report Manager Agent
        
        Role: Coordinates analyst and designer, reviews quality, requests revisions
        
        Capabilities:
        - Task assignment and coordination
        - Quality review and feedback
        - Request analyst to supplement information
        - Final quality gate
        """
        return Agent(
            config=self.agents_config['report_manager'],
            llm=self.llm,
            verbose=True,
            memory=False,
            allow_delegation=True,  # Can delegate to analyst and designer
        )
    
    @agent
    def technical_analyst(self) -> Agent:
        """
        Technical Analyst Agent
        
        Knowledge: academic_analysis + report_templates
        - Analysis frameworks: SWOT, PEST, Porter's Five Forces, etc.
        - Report structure templates
        
        Tools: web_search, arxiv_search, web_fetch, etc.
        """
        tools = []
        try:
            from .tools import get_search_tools
            tools = get_search_tools()
            print(f"[INFO] Loaded {len(tools)} search tools")
        except Exception as e:
            print(f"[WARN] Failed to load search tools: {e}")
        
        return Agent(
            config=self.agents_config['technical_analyst'],
            llm=self.llm,
            tools=tools,
            verbose=True,
            memory=False,
            allow_delegation=False,
            # Agent-level knowledge: analysis frameworks + report templates
            knowledge_sources=self.knowledge_by_category.get('analyst', []),
            embedder=DASHSCOPE_EMBEDDER_CONFIG
        )
    
    @agent
    def presentation_designer(self) -> Agent:
        """
        Presentation Designer Agent
        
        Knowledge: ppt_skills
        - Design principles
        - Chart type selection
        - Color and layout guides
        """
        return Agent(
            config=self.agents_config['presentation_designer'],
            llm=self.llm,
            verbose=True,
            memory=False,
            allow_delegation=False,
            # Agent-level knowledge: PPT design skills
            knowledge_sources=self.knowledge_by_category.get('designer', []),
            embedder=DASHSCOPE_EMBEDDER_CONFIG
        )
    
    @task
    def analyze_task(self) -> Task:
        """分析任务: 输入主题 → 输出 Markdown 技术报告"""
        return Task(
            config=self.tasks_config['analyze_task']
        )
    
    @task
    def design_task(self) -> Task:
        """设计任务: 输入报告 → 输出 JSON PPT 结构"""
        return Task(
            config=self.tasks_config['design_task']
        )
    
    @crew
    def crew(self) -> Crew:
        """
        Assemble Crew with Hierarchical Process for better collaboration.
        
        Manager coordinates:
        1. Assigns analysis task to Technical Analyst
        2. Reviews report quality, requests revisions if needed
        3. Assigns design task to Presentation Designer
        4. Reviews PPT quality, ensures key info is preserved
        5. Final quality gate before delivery
        
        Each agent has dedicated knowledge sources:
        - Technical Analyst: analysis frameworks + report templates
        - Presentation Designer: PPT design skills
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,  # Manager coordinates collaboration
            manager_llm=self.llm,  # Manager uses same LLM
            verbose=True,
            memory=False,  # Disabled for DashScope compatibility
            # Crew-level knowledge
            knowledge_sources=self.knowledge_sources if self.knowledge_sources else None,
            embedder=DASHSCOPE_EMBEDDER_CONFIG
        )
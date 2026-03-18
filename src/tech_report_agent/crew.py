"""
InsightForge Crew Definition

Defines Agent, Task and Crew, manages knowledge loading.
"""

import os
from pathlib import Path
from typing import List

from crewai import Agent, Crew, Task, Process, LLM
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.knowledge.storage.knowledge_storage import KnowledgeStorage

from crewai.project import CrewBase, agent, crew, task


# DashScope embedder configuration (OpenAI-compatible API)
# Load from environment variables - use separate embedding config
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
    
    Two agents collaborate:
    1. Technical Analyst - Analyze and write reports
    2. Presentation Designer - Convert reports to PPT
    """
    
    agents_config: str = 'config/agents.yaml'
    tasks_config: str = 'config/tasks.yaml'
    
    def __init__(self):
        """Initialize: Load knowledge and configure LLM"""
        self.knowledge_storage = self._create_knowledge_storage()
        self.knowledge_sources = self._load_knowledge()
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
        """
        Create KnowledgeStorage with DashScope embeddings (OpenAI-compatible).
        """
        return KnowledgeStorage(embedder=DASHSCOPE_EMBEDDER_CONFIG)
    
    def _load_knowledge(self) -> List[StringKnowledgeSource]:
        """
        Load knowledge base from knowledge/ directory
        Uses custom KnowledgeStorage with ONNX embeddings.
        """
        knowledge_sources = []
        knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
        
        if not knowledge_dir.exists():
            print(f"[WARN] Knowledge directory not found: {knowledge_dir}")
            return knowledge_sources
        
        # Find all .md files
        md_files = list(knowledge_dir.rglob("*.md"))
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
                if content.strip():  # Skip empty files
                    # Create knowledge source with custom storage (ONNX embeddings)
                    ks = StringKnowledgeSource(
                        content=content,
                        storage=self.knowledge_storage
                    )
                    knowledge_sources.append(ks)
                    print(f"[OK] Loaded: {md_file.relative_to(knowledge_dir)}")
            except Exception as e:
                print(f"[WARN] Failed to load {md_file}: {e}")
        
        print(f"[INFO] Knowledge base loaded: {len(knowledge_sources)} files\n")
        return knowledge_sources
    
    @agent
    def technical_analyst(self) -> Agent:
        """
        Technical Analyst Agent
        
        Responsibilities:
        - Understand analysis topic
        - Select analysis framework (SWOT/PEST/Porter's Five Forces)
        - Execute deep analysis
        - Write technical report
        """
        # 尝试加载搜索工具
        tools = []
        try:
            from .tools import get_search_tools
            tools = get_search_tools()
            print("[INFO] Search tools loaded")
        except Exception as e:
            print(f"[WARN] Failed to load search tools: {e}")
        
        return Agent(
            config=self.agents_config['technical_analyst'],
            llm=self.llm,
            tools=tools,  # 添加搜索工具
            verbose=True,
            memory=False,  # Disabled for DashScope compatibility
            allow_delegation=False
        )
    
    @agent
    def presentation_designer(self) -> Agent:
        """
        Presentation Designer Agent
        
        Responsibilities:
        - Parse report structure
        - Design information architecture
        - Create slide structure
        - Provide chart suggestions
        """
        return Agent(
            config=self.agents_config['presentation_designer'],
            llm=self.llm,
            verbose=True,
            memory=False,  # Disabled for DashScope compatibility
            allow_delegation=False
        )
    
    @task
    def analyze_task(self) -> Task:
        """
        分析任务
        
        输入: topic (主题)
        输出: Markdown 技术报告
        """
        return Task(
            config=self.tasks_config['analyze_task']
        )
    
    @task
    def design_task(self) -> Task:
        """
        设计任务
        
        输入: Markdown 报告 (来自 analyze_task)
        输出: JSON 结构描述
        """
        return Task(
            config=self.tasks_config['design_task']
        )
    
    @crew
    def crew(self) -> Crew:
        """
        Assemble Crew
        
        Configuration:
        - Sequential execution
        - Memory disabled (DashScope compatibility)
        - Knowledge sources disabled (embedding API compatibility)
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Disabled for DashScope compatibility
            # Knowledge sources disabled - requires DashScope embedding API
            # which is not compatible with GLM-5 Coding API key
            # knowledge_sources=self.knowledge_sources if self.knowledge_sources else None,
            # embedder=DASHSCOPE_EMBEDDER_CONFIG
        )
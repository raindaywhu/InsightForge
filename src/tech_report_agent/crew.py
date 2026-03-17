"""
InsightForge Crew 定义模块

定义 Agent、Task 和 Crew，管理知识库加载。
"""

from pathlib import Path
from typing import List

from crewai import Agent, Crew, Task, Process
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

from crewai.project import CrewBase, agent, crew, task


@CrewBase
class TechReportCrew:
    """
    技术报告生成 Crew
    
    通过两个 Agent 协作：
    1. Technical Analyst - 深度分析并撰写报告
    2. Presentation Designer - 将报告转化为 PPT
    """
    
    agents_config: str = 'config/agents.yaml'
    tasks_config: str = 'config/tasks.yaml'
    
    def __init__(self):
        """初始化: 加载知识库"""
        self.knowledge_sources = self._load_knowledge()
    
    def _load_knowledge(self) -> List[StringKnowledgeSource]:
        """
        Load knowledge base from knowledge/ directory
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
                    ks = StringKnowledgeSource(content=content)
                    knowledge_sources.append(ks)
                    print(f"[OK] Loaded: {md_file.relative_to(knowledge_dir)}")
            except Exception as e:
                print(f"[WARN] Failed to load {md_file}: {e}")
        
        print(f"[INFO] Knowledge base loaded: {len(knowledge_sources)} files\n")
        return knowledge_sources
    
    @agent
    def technical_analyst(self) -> Agent:
        """
        技术分析师 Agent
        
        职责:
        - 理解分析主题
        - 选择分析框架 (SWOT/PEST/波特五力等)
        - 执行深度分析
        - 撰写技术报告
        """
        return Agent(
            config=self.agents_config['technical_analyst'],
            verbose=True,
            memory=True,
            allow_delegation=False
        )
    
    @agent
    def presentation_designer(self) -> Agent:
        """
        演示设计师 Agent
        
        职责:
        - 解析报告结构
        - 设计信息架构
        - 创建幻灯片结构
        - 提供图表建议
        """
        return Agent(
            config=self.agents_config['presentation_designer'],
            verbose=True,
            memory=True,
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
        组装 Crew
        
        配置:
        - 顺序执行模式
        - 启用记忆
        - 加载知识库
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            knowledge_sources=self.knowledge_sources
        )
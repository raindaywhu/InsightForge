"""
Tech Report Agent Crew
技术报告生成系统 - Crew 定义
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
import os


@CrewBase
class TechReportCrew:
    """技术报告生成 Crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # 加载知识库
        self.knowledge_sources = self._load_knowledge()

    def _load_knowledge(self):
        """加载知识库内容"""
        knowledge_dir = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', 'knowledge'
        )
        
        knowledge_sources = []
        
        # 加载所有知识库文件
        for root, dirs, files in os.walk(knowledge_dir):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 创建知识源
                    ks = StringKnowledgeSource(content=content)
                    knowledge_sources.append(ks)
        
        return knowledge_sources

    @agent
    def technical_analyst(self) -> Agent:
        """技术分析师 Agent"""
        return Agent(
            config=self.agents_config['technical_analyst'],
            verbose=True,
            memory=True
        )

    @agent
    def presentation_designer(self) -> Agent:
        """演示设计师 Agent"""
        return Agent(
            config=self.agents_config['presentation_designer'],
            verbose=True,
            memory=True
        )

    @task
    def analyze_task(self) -> Task:
        """分析任务"""
        return Task(
            config=self.tasks_config['analyze_task']
        )

    @task
    def design_task(self) -> Task:
        """PPT设计任务"""
        return Task(
            config=self.tasks_config['design_task']
        )

    @crew
    def crew(self) -> Crew:
        """创建 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            knowledge_sources=self.knowledge_sources
        )
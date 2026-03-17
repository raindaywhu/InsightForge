"""
InsightForge - AI驱动的技术报告生成系统

基于 CrewAI 框架，通过多 Agent 协作 + RAG 知识增强，
自动化产出高质量的技术报告和 PPT 演示。
"""

__version__ = "0.1.0"
__author__ = "万一"

from .crew import TechReportCrew

__all__ = ["TechReportCrew"]
@echo off
cd /d C:\Users\raind\projects\InsightForge
call C:\Users\raind\miniconda3\Scripts\activate.bat insightforge
python -m src.tech_report_agent.web_ui
pause
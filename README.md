# Tech Report Agent

基于 CrewAI 的技术报告生成系统，集成 RAG 知识库。

## 📁 项目结构

```
tech_report_agent/
├── src/tech_report_agent/
│   ├── config/
│   │   ├── agents.yaml      # Agent 配置
│   │   └── tasks.yaml       # Task 配置
│   ├── crew.py              # Crew 定义
│   ├── main.py              # 入口文件
│   └── __init__.py
├── knowledge/               # RAG 知识库
│   ├── academic_analysis/   # 学术分析技巧
│   │   ├── SWOT分析.md
│   │   ├── PEST分析.md
│   │   ├── 波特五力分析.md
│   │   └── 数据可视化.md
│   ├── ppt_skills/          # PPT 制作技巧
│   │   ├── PPT设计原则.md
│   │   ├── 配色指南.md
│   │   └── 图表设计.md
│   └── report_templates/    # 报告模板
│       └── 技术报告模板.md
├── output/                  # 输出目录（自动创建）
├── .env.example             # 环境变量示例
├── pyproject.toml           # 项目配置
└── README.md
```

## 🚀 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入 API Key
```

### 2. 安装依赖

```bash
# 使用 crewai conda 环境
conda activate crewai

# 或直接安装
pip install -e .
```

### 3. 运行

```bash
cd src/tech_report_agent
python main.py "AI Agent 发展现状与趋势分析"
```

## 🤖 Agent 角色

| Agent | 职责 | 输出 |
|-------|------|------|
| 技术分析师 | 深度分析、撰写报告 | Markdown 报告 |
| 演示设计师 | PPT 结构设计 | PPT 结构 JSON |

## 📚 知识库内容

### 学术分析技巧
- SWOT 分析框架
- PEST 分析框架
- 波特五力分析
- 数据可视化实践

### PPT 制作技巧
- 设计核心原则
- 配色指南
- 图表设计

### 报告模板
- 技术报告标准结构

## ⚙️ 配置

### 修改 LLM

编辑 `.env`:
```env
OPENAI_API_BASE=https://api.deepseek.com/v1
OPENAI_MODEL_NAME=deepseek-chat
OPENAI_API_KEY=your_key
```

### 添加知识库

在 `knowledge/` 目录下添加 `.md` 文件，系统会自动加载。

## 📝 扩展

### 添加新的分析框架

1. 在 `knowledge/academic_analysis/` 创建新的 `.md` 文件
2. 重新运行即可

### 添加新的 Agent

1. 编辑 `config/agents.yaml` 添加新 Agent
2. 编辑 `config/tasks.yaml` 添加对应 Task
3. 在 `crew.py` 中添加对应的 `@agent` 和 `@task` 方法

---

**Created by 万一** 🤖
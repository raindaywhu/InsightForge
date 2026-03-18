# InsightForge

> AI 驱动的技术报告生成系统

基于 CrewAI 多 Agent 协作 + RAG 知识增强，自动化产出高质量的技术报告和 PPT 演示。

---

## ✨ 特性

- 🤖 **多 Agent 协作**：技术分析师 + 演示设计师协同工作
- 📚 **RAG 知识增强**：内置分析框架（SWOT/PEST/波特五力）和 PPT 设计知识库
- 📝 **Markdown 报告**：输出结构化、专业的技术报告
- 🎨 **PPT 结构设计**：自动设计幻灯片结构和内容布局
- 🌐 **Web UI**：提供友好的 Web 界面
- 🔧 **易于扩展**：支持自定义 Agent、Task 和知识库

---

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/raindaywhu/InsightForge.git
cd InsightForge

# 创建虚拟环境
conda create -n insightforge python=3.11
conda activate insightforge

# 安装依赖
pip install -e .
```

### 2. 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，配置阿里云 DashScope API Key
# DASHSCOPE_API_KEY=sk-your-api-key-here
# EMBEDDING_API_KEY=sk-your-embedding-key-here
```

**注意**：本项目使用阿里云 DashScope API（GLM-5 模型），需要：
- `DASHSCOPE_API_KEY` - 用于 LLM 调用（Coding API）
- `EMBEDDING_API_KEY` - 用于 Embedding（DashScope 兼容 API）

### 3. 运行

**命令行方式**：
```bash
# 生成技术报告
insightforge run "分析 OpenAI 在 AI Agent 领域的竞争力"

# 指定输出目录
insightforge run "2024年大语言模型发展趋势分析" -o ./my_output
```

**Web UI 方式**：
```bash
# 启动 Web 界面
python -m src.tech_report_agent.web_ui

# 访问 http://localhost:7860
```

---

## 📖 文档

- [产品设计文档 (PRD)](docs/PRD.md)
- [技术设计文档](docs/TECH_DESIGN.md)

---

## 🏗️ 项目结构

```
InsightForge/
├── src/
│   └── tech_report_agent/
│       ├── config/
│       │   ├── agents.yaml      # Agent 配置
│       │   └── tasks.yaml       # Task 配置
│       ├── crew.py              # Crew 定义
│       ├── main.py              # 入口文件
│       └── __init__.py
│
├── knowledge/                   # 知识库
│   ├── academic_analysis/       # 分析方法论
│   │   ├── SWOT分析.md
│   │   ├── PEST分析.md
│   │   └── 波特五力分析.md
│   ├── ppt_skills/              # PPT 技能
│   │   ├── PPT设计原则.md
│   │   └── 图表设计.md
│   └── report_templates/        # 报告模板
│       └── 技术报告模板.md
│
├── output/                      # 输出目录
│   ├── reports/                 # 生成的报告
│   └── presentations/           # 生成的 PPT
│
├── docs/
│   ├── PRD.md                   # 产品设计文档
│   └── TECH_DESIGN.md           # 技术设计文档
│
├── .env.example                 # 环境变量模板
├── pyproject.toml               # 项目配置
└── README.md                    # 项目说明
```

---

## 🔧 工作流程

```
用户输入主题
     │
     ▼
┌─────────────────────────────────────┐
│  Agent 1: 技术分析师                 │
│  ┌───────────┐  ┌───────────┐      │
│  │ 理解主题  │→│ RAG检索   │      │
│  │           │  │ 分析框架  │      │
│  └───────────┘  └───────────┘      │
│         │                           │
│         ▼                           │
│  ┌───────────────────────────┐     │
│  │  LLM分析 → Markdown报告   │     │
│  └───────────────────────────┘     │
└─────────────────────────────────────┘
     │
     ▼ Markdown 报告
┌─────────────────────────────────────┐
│  Agent 2: 演示设计师                 │
│  ┌───────────┐  ┌───────────┐      │
│  │ 解析报告  │→│ RAG检索   │      │
│  │           │  │ PPT原则   │      │
│  └───────────┘  └───────────┘      │
│         │                           │
│         ▼                           │
│  ┌───────────────────────────┐     │
│  │  LLM设计 → PPT结构JSON    │     │
│  └───────────────────────────┘     │
└─────────────────────────────────────┘
     │
     ▼
输出: 报告.md + PPT.json
```

---

## 🧠 知识库

### 分析方法论

| 框架 | 用途 |
|------|------|
| SWOT 分析 | 评估优势、劣势、机会、威胁 |
| PEST 分析 | 分析政治、经济、社会、技术环境 |
| 波特五力 | 分析行业竞争格局 |

### PPT 设计知识

| 内容 | 说明 |
|------|------|
| PPT 设计原则 | 简洁、聚焦、一致性、可视化、对齐 |
| 图表设计 | 柱状图、折线图、饼图、散点图等选择指南 |

---

## 🔌 扩展开发

### 添加新的分析框架

在 `knowledge/academic_analysis/` 目录下创建新的 Markdown 文件：

```markdown
# [新框架名称]

## 概述
[框架介绍]

## 分析步骤
[步骤说明]

## 应用示例
[示例说明]
```

### 添加新的 Agent

1. 在 `src/tech_report_agent/config/agents.yaml` 添加配置
2. 在 `crew.py` 中添加 `@agent` 方法

---

## 📝 开发计划

- [ ] 支持 PDF/Word 报告导出
- [x] 集成 Web 搜索工具
- [ ] 添加数据可视化图表生成
- [x] Web UI 界面
- [ ] 支持更多 LLM 后端（Claude、DeepSeek等）

---

## 📄 License

MIT License

---

## 🙏 致谢

- [CrewAI](https://github.com/joaomdmoura/crewAI) - 多 Agent 框架
- [ChromaDB](https://github.com/chroma-core/chroma) - 向量数据库
- [Mem0](https://github.com/mem0ai/mem0) - 记忆管理
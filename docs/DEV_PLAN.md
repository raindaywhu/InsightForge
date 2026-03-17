# InsightForge 开发计划

> 版本：1.0  
> 创建日期：2026-03-17  
> 维护者：万一

---

## 开发阶段总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          InsightForge 开发路线图                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 0: 基础搭建 (1-2天)                                                  │
│  ├─ ✅ 项目结构初始化                                                       │
│  ├─ ✅ 设计文档编写                                                         │
│  └─ ✅ 知识库框架搭建                                                       │
│                                                                             │
│  Phase 1: MVP 核心功能 (3-5天) ⭐ 当前目标                                  │
│  ├─ 🔄 Agent 基础实现                                                       │
│  ├─ 🔄 RAG 知识检索                                                         │
│  └─ 🔄 Markdown 报告输出                                                    │
│                                                                             │
│  Phase 2: PPT 生成 (2-3天)                                                  │
│  ├─ ⏳ PPT 结构设计                                                         │
│  ├─ ⏳ python-pptx 集成                                                     │
│  └─ ⏳ .pptx 文件输出                                                       │
│                                                                             │
│  Phase 3: 增强功能 (3-4天)                                                  │
│  ├─ ⏳ 框架选择器                                                           │
│  ├─ ⏳ 更多知识库内容                                                       │
│  └─ ⏳ 质量检查模块                                                         │
│                                                                             │
│  Phase 4: 高级功能 (按需)                                                   │
│  ├─ ⏳ Web 搜索集成                                                         │
│  ├─ ⏳ Web UI 界面                                                          │
│  └─ ⏳ 多 LLM 后端支持                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: 基础搭建 ✅

**目标**：完成项目骨架和设计文档

**状态**：已完成

| 任务 | 状态 | 产出 |
|------|------|------|
| 项目结构初始化 | ✅ | 目录结构、.gitignore |
| PRD 编写 | ✅ | docs/PRD.md |
| 技术设计文档 | ✅ | docs/TECH_DESIGN.md |
| 知识库框架 | ✅ | knowledge/*.md |
| Agent 配置文件 | ✅ | config/agents.yaml, tasks.yaml |
| 项目配置 | ✅ | pyproject.toml, README.md |

---

## Phase 1: MVP 核心功能 🔄

**目标**：实现最小可用产品，能够生成 Markdown 报告

**时间**：3-5 天

### 1.1 环境配置 (0.5天)

| 任务 | 详情 | 验收标准 |
|------|------|---------|
| Conda 环境创建 | 创建 insightforge 环境，Python 3.11 | `conda env list` 显示环境 |
| 依赖安装 | 安装 crewai, chromadb, mem0ai 等 | `pip list` 显示所有依赖 |
| 环境变量配置 | 创建 .env，配置 OPENAI_API_KEY | 运行无报错 |

**命令**：
```bash
conda create -n insightforge python=3.11 -y
conda activate insightforge
pip install -e .
```

---

### 1.2 Crew 核心实现 (1-2天)

#### 1.2.1 知识库加载器

**文件**：`src/tech_report_agent/crew.py`

**任务**：
- [ ] 实现 `_load_knowledge()` 方法
- [ ] 遍历 knowledge/ 目录读取所有 .md 文件
- [ ] 创建 StringKnowledgeSource 实例
- [ ] 测试知识库加载

**代码框架**：
```python
def _load_knowledge(self) -> List[StringKnowledgeSource]:
    """加载知识库文件"""
    knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
    sources = []
    
    for md_file in knowledge_dir.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        source = StringKnowledgeSource(content=content)
        sources.append(source)
    
    return sources
```

**验收标准**：
- 启动时能成功加载所有知识文件
- ChromaDB 中能看到向量数据

---

#### 1.2.2 Agent 实现

**文件**：`src/tech_report_agent/crew.py`

**任务**：
- [ ] 实现 `technical_analyst` Agent
- [ ] 实现 `presentation_designer` Agent
- [ ] 配置 Agent 的 role, goal, backstory
- [ ] 启用 memory 功能

**验收标准**：
- Agent 能正确读取配置
- Agent 具有记忆能力

---

#### 1.2.3 Task 实现

**文件**：`src/tech_report_agent/crew.py`

**任务**：
- [ ] 实现 `analyze_task` - 分析任务
- [ ] 实现 `design_task` - 设计任务
- [ ] 配置任务依赖关系

**验收标准**：
- Task 能正确接收输入
- Task 能产出预期输出

---

#### 1.2.4 Crew 组装

**文件**：`src/tech_report_agent/crew.py`

**任务**：
- [ ] 组装 Agent 和 Task
- [ ] 配置顺序执行流程
- [ ] 启用 Crew 级别记忆
- [ ] 配置知识源

**验收标准**：
- `crew.kickoff()` 能成功执行
- Agent 能调用 RAG 检索知识

---

### 1.3 CLI 入口实现 (0.5天)

**文件**：`src/tech_report_agent/main.py`

**任务**：
- [ ] 实现命令行参数解析
- [ ] 实现主流程：输入 → Crew 执行 → 输出保存
- [ ] 添加进度提示
- [ ] 输出文件命名（时间戳）

**命令格式**：
```bash
insightforge run "分析主题" [--output DIR]
```

**验收标准**：
- 能解析命令行参数
- 能输出 Markdown 报告到 output/reports/

---

### 1.4 测试与调试 (1天)

**任务**：
- [ ] 运行端到端测试
- [ ] 验证 RAG 检索效果
- [ ] 验证报告质量
- [ ] 修复发现的问题

**测试场景**：
```bash
# 测试1：简单主题
insightforge run "分析 OpenAI 的竞争优势"

# 测试2：技术主题
insightforge run "2024年大语言模型发展趋势"

# 测试3：行业分析
insightforge run "电动汽车行业竞争格局"
```

**验收标准**：
- 报告包含完整的章节结构
- 分析框架应用正确
- 内容逻辑清晰

---

### 1.5 Phase 1 验收清单

```
□ conda 环境正常
□ 依赖安装完整
□ 知识库加载成功
□ Agent 能正常工作
□ RAG 检索有效
□ 能生成 Markdown 报告
□ 报告质量可接受
□ 文档更新完整
```

---

## Phase 2: PPT 生成功能

**目标**：实现 PPT 结构设计和 .pptx 文件输出

**时间**：2-3 天

### 2.1 PPT 结构设计器 (1天)

**任务**：
- [ ] 设计 PPT 结构 JSON Schema
- [ ] 实现 `PresentationDesigner` Agent 输出格式
- [ ] 设计幻灯片类型（标题页、内容页、图表页等）

**JSON Schema 示例**：
```json
{
  "title": "报告标题",
  "slides": [
    {
      "type": "title",
      "title": "主标题",
      "subtitle": "副标题"
    },
    {
      "type": "content",
      "title": "章节标题",
      "bullets": ["要点1", "要点2", "要点3"]
    },
    {
      "type": "chart",
      "title": "数据图表",
      "chart_type": "bar",
      "data": {...}
    }
  ]
}
```

---

### 2.2 python-pptx 集成 (1天)

**任务**：
- [ ] 安装 python-pptx
- [ ] 实现 PPT 生成器类
- [ ] 实现各类型幻灯片模板
- [ ] 实现配色方案应用

**文件结构**：
```
src/tech_report_agent/
├── tools/
│   ├── __init__.py
│   └── ppt_generator.py    # PPT 生成工具
```

---

### 2.3 输出集成 (0.5天)

**任务**：
- [ ] 集成到主流程
- [ ] 输出 .pptx 文件
- [ ] 添加文件命名规则

---

### 2.4 Phase 2 验收清单

```
□ 能生成 PPT 结构 JSON
□ JSON 格式符合 Schema
□ 能生成 .pptx 文件
□ PPT 结构合理
□ PPT 可正常打开
```

---

## Phase 3: 增强功能

**目标**：提升用户体验和输出质量

**时间**：3-4 天

### 3.1 框架选择器 (1天)

**任务**：
- [ ] 实现自动框架匹配
- [ ] 支持手动指定框架
- [ ] 支持多框架组合

**命令扩展**：
```bash
insightforge run "主题" --framework swot
insightforge run "主题" --framework swot,pest
```

---

### 3.2 知识库扩展 (1天)

**任务**：
- [ ] 添加更多分析框架（价值链、BCG矩阵等）
- [ ] 添加更多报告模板
- [ ] 完善配色指南

---

### 3.3 质量检查模块 (1天)

**任务**：
- [ ] 实现输出完整性检查
- [ ] 实现格式规范性检查
- [ ] 自动修复常见问题

---

### 3.4 Phase 3 验收清单

```
□ 框架选择功能正常
□ 多框架组合可用
□ 知识库内容丰富
□ 质量检查有效
□ 报告质量提升
```

---

## Phase 4: 高级功能（按需）

**目标**：扩展系统能力

### 4.1 Web 搜索集成

- [ ] 集成 Tavily/Exa 搜索 API
- [ ] 实现实时数据检索
- [ ] 数据来源标注

### 4.2 Web UI

- [ ] 使用 Streamlit/Gradio 构建
- [ ] 支持在线预览
- [ ] 支持下载导出

### 4.3 多 LLM 后端

- [ ] 支持 Claude
- [ ] 支持 DeepSeek
- [ ] 支持本地模型（Ollama）

---

## 开发规范

### Git 提交规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
refactor: 代码重构
test: 测试相关
chore: 构建/工具相关
```

### 分支策略

```
main        # 主分支，稳定版本
develop     # 开发分支
feature/*   # 功能分支
hotfix/*    # 紧急修复
```

### 代码规范

- 使用 Black 格式化
- 使用 Ruff 检查
- 类型注解完整
- 文档字符串规范

---

## 风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|---------|
| API 调用成本高 | 中 | 高 | 使用 gpt-4o-mini，添加缓存 |
| RAG 检索不准 | 中 | 中 | 优化知识库内容，调整检索参数 |
| Agent 输出不稳定 | 中 | 高 | 添加输出校验，重试机制 |
| 依赖版本冲突 | 低 | 中 | 锁定版本，使用 conda |

---

## 下一步行动

### 本周目标（Phase 1）

1. **环境配置**（0.5天）
   ```bash
   conda create -n insightforge python=3.11
   conda activate insightforge
   pip install -e .
   ```

2. **Crew 实现**（1-2天）
   - 完善知识库加载
   - 实现 Agent 和 Task
   - 测试 RAG 检索

3. **CLI 入口**（0.5天）
   - 命令行解析
   - 输出保存

4. **端到端测试**（1天）
   - 运行完整流程
   - 验证输出质量

---

> 文档版本：1.0  
> 最后更新：2026-03-17
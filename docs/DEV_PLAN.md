# InsightForge 开发计划 v2

> 版本：2.0  
> 更新日期：2026-03-18  
> 维护者：万一

---

## 开发阶段总览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          InsightForge 开发路线图                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 0: 基础搭建 ✅ 已完成                                                │
│                                                                             │
│  Phase 1: MVP 核心功能 (5-7天) ⭐ 当前目标                                  │
│  ├─ 1.1 环境配置 (0.5天)                                                   │
│  ├─ 1.2 知识库加载器 (0.5天)                                               │
│  ├─ 1.3 Agent Prompt 设计 (1.5天) ⭐⭐⭐ 核心任务                           │
│  ├─ 1.4 Agent/Task 代码实现 (1天)                                          │
│  ├─ 1.5 Crew 组装与集成 (0.5天)                                            │
│  ├─ 1.6 CLI 入口 (0.5天)                                                   │
│  └─ 1.7 测试与调优 (1天)                                                   │
│                                                                             │
│  Phase 2: PPT 生成 (2-3天)                                                  │
│  Phase 3: 增强功能 (3-4天)                                                  │
│  Phase 4: 高级功能 (按需)                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: 基础搭建 ✅

**状态**：已完成

| 任务 | 状态 | 产出 |
|------|------|------|
| 项目结构初始化 | ✅ | 目录结构、.gitignore |
| PRD 编写 | ✅ | docs/PRD.md |
| 技术设计文档 | ✅ | docs/TECH_DESIGN.md |
| 知识库框架 | ✅ | knowledge/*.md |
| Agent 配置骨架 | ✅ | config/agents.yaml, tasks.yaml |
| 项目配置 | ✅ | pyproject.toml, README.md |

---

## Phase 1: MVP 核心功能 🔄

**目标**：实现最小可用产品，能够生成 Markdown 报告

**总时间**：5-7 天

---

### 1.1 环境配置 (0.5天)

#### 子任务拆解

| # | 子任务 | 具体操作 | 验收标准 |
|---|--------|---------|---------|
| 1.1.1 | 创建 conda 环境 | `conda create -n insightforge python=3.11 -y` | `conda env list` 显示环境 |
| 1.1.2 | 安装核心依赖 | `pip install crewai chromadb mem0ai` | 无报错 |
| 1.1.3 | 安装项目 | `pip install -e .` | `pip show tech-report-agent` |
| 1.1.4 | 配置环境变量 | 复制 `.env.example` 为 `.env`，填入 DASHSCOPE_API_KEY | 文件存在，值正确 |
| 1.1.5 | 验证安装 | 运行简单测试脚本 | 无报错 |

**验收脚本**：
```python
# test_env.py
import crewai
import chromadb
import os
from openai import OpenAI

print(f"crewai: {crewai.__version__}")
print(f"chromadb: {chromadb.__version__}")

# 测试 DashScope API 连接
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
response = client.chat.completions.create(
    model="glm-4",
    messages=[{"role": "user", "content": "Hello"}],
    max_tokens=10
)
print(f"DashScope API: {response.choices[0].message.content}")
```

---

### 1.2 知识库加载器 (0.5天)

#### 子任务拆解

| # | 子任务 | 具体操作 | 验收标准 |
|---|--------|---------|---------|
| 1.2.1 | 实现 `_load_knowledge()` 方法 | 遍历 knowledge/ 目录，读取 .md 文件 | 代码完成 |
| 1.2.2 | 创建 StringKnowledgeSource | 每个文件创建一个实例 | 实例列表正确 |
| 1.2.3 | 测试加载功能 | 打印加载的文件名和内容长度 | 显示正确 |
| 1.2.4 | 验证向量存储 | 检查 ChromaDB 数据 | 向量数据存在 |

**代码实现**：
```python
# src/tech_report_agent/crew.py

from pathlib import Path
from typing import List
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

def _load_knowledge(self) -> List[StringKnowledgeSource]:
    """
    加载知识库文件
    
    Returns:
        List[StringKnowledgeSource]: 知识源列表
    """
    knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
    sources = []
    
    for md_file in knowledge_dir.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        source = StringKnowledgeSource(
            content=content,
            metadata={"source": str(md_file.relative_to(knowledge_dir))}
        )
        sources.append(source)
        print(f"[Knowledge] Loaded: {md_file.name} ({len(content)} chars)")
    
    return sources
```

**测试脚本**：
```python
# test_knowledge.py
from pathlib import Path
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

knowledge_dir = Path("knowledge")
for md_file in knowledge_dir.rglob("*.md"):
    content = md_file.read_text(encoding="utf-8")
    print(f"File: {md_file.name}")
    print(f"  Length: {len(content)} chars")
    print(f"  Preview: {content[:100]}...")
    print()
```

---

### 1.3 Agent Prompt 设计 (1.5天) ⭐⭐⭐ 核心任务

> **这是最关键的开发任务！**
> Prompt 质量直接决定输出质量。
> 需要迭代优化，不是一次性完成。

#### 子任务拆解

| # | 子任务 | 具体操作 | 预估时间 |
|---|--------|---------|---------|
| 1.3.1 | Technical Analyst - Role 设计 | 定义角色身份、专业背景 | 0.5h |
| 1.3.2 | Technical Analyst - Goal 设计 | 定义目标、成功标准 | 0.5h |
| 1.3.3 | Technical Analyst - Backstory 设计 | 定义背景故事、能力特点 | 1h |
| 1.3.4 | Analyze Task - Description 设计 | 定义任务步骤、要求 | 1h |
| 1.3.5 | Analyze Task - Expected Output 设计 | 定义输出格式、质量标准 | 0.5h |
| 1.3.6 | Prompt 测试与迭代 | 运行测试，优化 prompt | 3-4h |
| 1.3.7 | 文档化 Prompt 设计决策 | 记录设计理由、迭代历史 | 0.5h |

---

#### 1.3.1 Technical Analyst - Role 设计

**设计目标**：定义清晰的角色身份，让 LLM 知道"我是谁"

**设计原则**：
- 具体化：使用具体的职位名称
- 专业性：体现专业能力
- 独特性：与其他 Agent 区分

**迭代过程**：

| 版本 | Role 描述 | 问题 | 改进 |
|------|----------|------|------|
| v1 | 技术分析师 | 太泛泛 | |
| v2 | 资深技术分析师，专注于行业研究和竞争分析 | 更具体 | 加入"资深" |
| v3 | **资深技术分析师**，拥有10年行业研究经验，擅长运用学术分析框架（SWOT、PEST、波特五力）进行深度研究 | 最终版本 | 加入具体能力 |

**最终设计**：
```yaml
technical_analyst:
  role: >
    资深技术分析师，拥有10年行业研究经验，擅长运用学术分析框架（SWOT、PEST、波特五力）进行深度研究
```

---

#### 1.3.2 Technical Analyst - Goal 设计

**设计目标**：定义 Agent 的目标和成功标准

**设计原则**：
- 结果导向：描述期望的输出
- 可衡量：有明确的质量标准
- 行动性：引导 Agent 行动

**迭代过程**：

| 版本 | Goal 描述 | 问题 | 改进 |
|------|----------|------|------|
| v1 | 分析主题，输出报告 | 太简单 | |
| v2 | 深度研究分析主题，输出高质量技术报告 | 更好 | 但不够具体 |
| v3 | **深度研究分析主题，运用学术分析方法论，输出结构严谨、论证有力、洞察独到的技术报告** | 最终版本 | 加入具体要求 |

**最终设计**：
```yaml
  goal: >
    深度研究分析主题，运用学术分析方法论，输出结构严谨、论证有力、洞察独到的技术报告
```

---

#### 1.3.3 Technical Analyst - Backstory 设计

**设计目标**：定义背景故事，塑造 Agent "性格"

**设计原则**：
- 人格化：有个性特点
- 能力描述：具体技能
- 行为引导：隐含行为模式

**迭代过程**：

| 版本 | Backstory 描述 | 问题 |
|------|---------------|------|
| v1 | 你是技术分析师 | 太简单 |
| v2 | 你是一位资深的技术分析师，拥有丰富的学术研究经验。你擅长运用各种分析框架 | 更好 |
| v3 | 完整版本（见下方） | 最终 |

**最终设计**：
```yaml
  backstory: >
    你是一位资深的技术分析师，拥有10年的行业研究和竞争分析经验。
    
    你的核心能力：
    - 精通各类学术分析框架（SWOT、PEST、波特五力、价值链分析等）
    - 擅长从海量信息中提炼关键洞察
    - 能够构建逻辑严密的分析框架
    - 善于用数据支撑观点
    
    你的工作风格：
    - 严谨：每个结论都有依据
    - 深入：不满足于表面现象
    - 清晰：表达简洁有力
    - 客观：避免主观臆断
    
    你撰写的报告总是：
    - 结构清晰，逻辑自洽
    - 数据支撑充分
    - 观点独到，洞察深刻
    - 可操作性强
```

---

#### 1.3.4 Analyze Task - Description 设计

**设计目标**：定义具体任务步骤

**设计原则**：
- 步骤化：清晰的执行步骤
- 约束性：明确的要求和限制
- 引导性：引导 Agent 正确执行

**最终设计**：
```yaml
analyze_task:
  description: >
    针对"{topic}"主题进行深度分析研究。
    
    ## 执行步骤
    
    ### Step 1: 理解主题 (5分钟思考)
    - 明确分析的核心问题是什么
    - 确定分析范围和边界
    - 识别关键利益相关者
    
    ### Step 2: 选择分析框架
    - 从知识库中检索相关的分析框架
    - 根据主题特点选择最合适的框架
    - 可以组合多个框架
    
    推荐框架选择：
    - 竞争分析 → SWOT + 波特五力
    - 宏观环境 → PEST
    - 价值分析 → 价值链
    - 组合分析 → BCG矩阵
    
    ### Step 3: 执行深度分析
    - 按照选定的框架展开分析
    - 每个维度都要有充分论证
    - 用数据和案例支撑观点
    - 识别关键洞察和发现
    
    ### Step 4: 撰写报告
    按照以下结构撰写：
    
    1. **执行摘要** (200-300字)
       - 核心结论
       - 关键发现
       - 主要建议
    
    2. **主题背景** (300-500字)
       - 分析对象介绍
       - 分析背景和目的
       - 分析框架说明
    
    3. **核心分析** (2000-3000字)
       - 按框架展开各维度分析
       - 每个维度要有数据/案例支撑
       - 提炼关键洞察
    
    4. **结论与建议** (500-800字)
       - 核心结论总结
       - 可行性建议
       - 后续研究方向
    
    ## 输出要求
    
    - 使用 Markdown 格式
    - 合理使用标题层级（#, ##, ###）
    - 重要观点使用加粗
    - 数据使用列表或表格呈现
    - 总字数控制在 3000-5000 字
```

---

#### 1.3.5 Analyze Task - Expected Output 设计

**设计目标**：定义期望的输出格式

```yaml
  expected_output: >
    一份完整的 Markdown 格式技术报告，包含：
    
    - 执行摘要
    - 主题背景
    - 核心分析（使用至少一个分析框架）
    - 结论与建议
    
    质量标准：
    - 结构完整，逻辑清晰
    - 分析框架应用正确
    - 观点有数据/案例支撑
    - 语言专业，表达流畅
```

---

#### 1.3.6 Prompt 测试与迭代

**测试方法**：

```python
# test_prompt.py
from tech_report_agent.crew import TechReportCrew

crew = TechReportCrew()

# 测试用例
test_cases = [
    "分析 OpenAI 在 AI Agent 领域的竞争力",
    "2024年大语言模型发展趋势",
    "电动汽车行业竞争格局分析"
]

for topic in test_cases:
    print(f"\n{'='*60}")
    print(f"测试主题: {topic}")
    print('='*60)
    
    result = crew.crew().kickoff(inputs={'topic': topic})
    
    # 评估输出
    output = result.raw
    print(f"输出长度: {len(output)} 字符")
    print(f"包含执行摘要: {'执行摘要' in output}")
    print(f"包含分析框架: {'SWOT' in output or '波特五力' in output or 'PEST' in output}")
    print(f"包含结论: {'结论' in output or '建议' in output}")
```

**迭代记录**：

| 迭代 | 问题 | 改进 | 效果 |
|------|------|------|------|
| v1 | 输出太短 | 增加"总字数控制"要求 | 长度增加 |
| v2 | 没用分析框架 | 增加"框架选择"步骤 | 框架使用正确 |
| v3 | 结构混乱 | 增加详细的章节结构 | 结构清晰 |
| v4 | 缺少数据支撑 | 增加"数据/案例支撑"要求 | 论证更有力 |

---

#### 1.3.7 文档化 Prompt 设计

**创建文件**：`docs/PROMPT_DESIGN.md`

记录内容：
- 每个 prompt 的设计理由
- 迭代历史和改进效果
- 最佳实践总结

---

### 1.4 Agent/Task 代码实现 (1天)

#### 子任务拆解

| # | 子任务 | 具体操作 | 验收标准 |
|---|--------|---------|---------|
| 1.4.1 | 实现 technical_analyst Agent | 在 crew.py 中创建 Agent 方法 | Agent 可实例化 |
| 1.4.2 | 实现 analyze_task | 创建 Task 方法 | Task 可实例化 |
| 1.4.3 | 配置 memory | 启用 Mem0 记忆 | 记忆功能正常 |
| 1.4.4 | 配置知识源 | 连接知识库 | RAG 检索正常 |
| 1.4.5 | 单元测试 | 测试 Agent 和 Task | 测试通过 |

**代码实现**：

```python
# src/tech_report_agent/crew.py

from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from typing import List
from pathlib import Path
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

@CrewBase
class TechReportCrew:
    """技术报告生成 Crew"""
    
    agents_config: str = 'config/agents.yaml'
    tasks_config: str = 'config/tasks.yaml'
    
    def __init__(self):
        """初始化：加载知识库"""
        self.knowledge_sources = self._load_knowledge()
    
    def _load_knowledge(self) -> List[StringKnowledgeSource]:
        """加载知识库文件"""
        knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
        sources = []
        
        for md_file in knowledge_dir.rglob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            source = StringKnowledgeSource(
                content=content,
                metadata={"source": str(md_file.relative_to(knowledge_dir))}
            )
            sources.append(source)
        
        return sources
    
    @agent
    def technical_analyst(self) -> Agent:
        """技术分析师 Agent"""
        return Agent(
            config=self.agents_config['technical_analyst'],
            verbose=True,
            memory=True,
            allow_delegation=False
        )
    
    @task
    def analyze_task(self) -> Task:
        """分析任务"""
        return Task(
            config=self.tasks_config['analyze_task'],
            output_file='output/report.md'
        )
    
    @crew
    def crew(self) -> Crew:
        """组装 Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            knowledge_sources=self.knowledge_sources
        )
```

---

### 1.5 Crew 组装与集成 (0.5天)

#### 子任务拆解

| # | 子任务 | 具体操作 | 验收标准 |
|---|--------|---------|---------|
| 1.5.1 | 配置执行流程 | 设置 sequential 流程 | 流程正确 |
| 1.5.2 | 配置记忆后端 | 启用 Crew 级别记忆 | Mem0 正常工作 |
| 1.5.3 | 配置知识源 | 传入 knowledge_sources | RAG 正常 |
| 1.5.4 | 集成测试 | 运行完整流程 | 能生成报告 |

---

### 1.6 CLI 入口 (0.5天)

#### 子任务拆解

| # | 子任务 | 具体操作 | 验收标准 |
|---|--------|---------|---------|
| 1.6.1 | 命令行参数解析 | 使用 argparse/click | 解析正确 |
| 1.6.2 | 主流程实现 | 调用 Crew 执行 | 流程完整 |
| 1.6.3 | 输出保存 | 保存到文件 | 文件正确 |
| 1.6.4 | 进度提示 | 打印执行进度 | 提示清晰 |

**代码实现**：

```python
# src/tech_report_agent/main.py

import argparse
from datetime import datetime
from pathlib import Path
from .crew import TechReportCrew

def main():
    parser = argparse.ArgumentParser(description='InsightForge - 技术报告生成器')
    parser.add_argument('topic', help='分析主题')
    parser.add_argument('--output', '-o', default='output', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'report_{timestamp}.md'
    
    print(f"[InsightForge] 开始分析: {args.topic}")
    print(f"[InsightForge] 输出文件: {output_file}")
    
    # 执行分析
    crew = TechReportCrew()
    result = crew.crew().kickoff(inputs={'topic': args.topic})
    
    # 保存结果
    output_file.write_text(result.raw, encoding='utf-8')
    
    print(f"[InsightForge] 完成! 报告已保存到: {output_file}")

if __name__ == '__main__':
    main()
```

---

### 1.7 测试与调优 (1天)

#### 子任务拆解

| # | 子任务 | 具体操作 | 验收标准 |
|---|--------|---------|---------|
| 1.7.1 | 端到端测试 | 运行完整流程 | 无报错 |
| 1.7.2 | RAG 检索测试 | 验证知识库检索 | 检索有效 |
| 1.7.3 | 输出质量评估 | 评估报告质量 | 达到标准 |
| 1.7.4 | Prompt 优化 | 根据结果调整 | 质量提升 |
| 1.7.5 | 性能测试 | 测试执行时间 | 可接受 |

#### 质量评估标准

```
□ 报告结构完整
  □ 包含执行摘要
  □ 包含主题背景
  □ 包含核心分析
  □ 包含结论建议

□ 分析框架应用正确
  □ 使用了至少一个分析框架
  □ 框架应用方式正确
  □ 各维度分析充分

□ 内容质量
  □ 逻辑清晰
  □ 论证有力
  □ 语言流畅
  □ 字数达标 (3000-5000字)

□ 格式规范
  □ Markdown 格式正确
  □ 标题层级合理
  □ 重点突出
```

---

## Phase 1 验收清单

```
□ 1.1 环境配置
  □ conda 环境正常
  □ 依赖安装完整
  □ API Key 配置正确

□ 1.2 知识库加载器
  □ 能加载所有知识文件
  □ 向量存储正常

□ 1.3 Agent Prompt 设计 ⭐
  □ Role 设计完成
  □ Goal 设计完成
  □ Backstory 设计完成
  □ Task Description 设计完成
  □ Expected Output 设计完成
  □ 测试迭代完成

□ 1.4 Agent/Task 实现
  □ Agent 可实例化
  □ Task 可实例化
  □ Memory 正常

□ 1.5 Crew 组装
  □ 执行流程正确
  □ RAG 检索有效

□ 1.6 CLI 入口
  □ 命令行解析正常
  □ 输出保存正确

□ 1.7 测试与调优
  □ 端到端测试通过
  □ 输出质量达标
```

---

## 任务依赖关系

```
1.1 环境配置
    ↓
1.2 知识库加载器
    ↓
1.3 Agent Prompt 设计 ←─── 核心任务，需要迭代
    ↓
1.4 Agent/Task 实现
    ↓
1.5 Crew 组装
    ↓
1.6 CLI 入口
    ↓
1.7 测试与调优 ──→ 可能需要回到 1.3 优化 Prompt
```

---

## 开发时间估算

| 任务 | 最短 | 最长 | 说明 |
|------|------|------|------|
| 1.1 环境配置 | 0.25天 | 0.5天 | 取决于网络和依赖冲突 |
| 1.2 知识库加载器 | 0.25天 | 0.5天 | 代码简单，主要是调试 |
| 1.3 Prompt 设计 | 1天 | 2天 | **核心任务，需要迭代** |
| 1.4 Agent/Task 实现 | 0.5天 | 1天 | 代码实现 |
| 1.5 Crew 组装 | 0.25天 | 0.5天 | 配置为主 |
| 1.6 CLI 入口 | 0.25天 | 0.5天 | 代码简单 |
| 1.7 测试与调优 | 0.5天 | 1天 | 可能需要多次迭代 |
| **总计** | **3天** | **6天** | |

---

## 下一步行动

### 立即开始

```bash
# 1. 创建环境
conda create -n insightforge python=3.11 -y
conda activate insightforge

# 2. 安装依赖
cd C:\Users\raind\projects\InsightForge
pip install -e .

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY

# 4. 测试环境
python -c "import crewai; print(crewai.__version__)"
```

### Prompt 设计任务

从 1.3.1 开始，按照子任务列表逐项完成 Prompt 设计。

---

> 文档版本：2.0  
> 最后更新：2026-03-18
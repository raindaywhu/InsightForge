# InsightForge 测试方案

> 版本：1.0  
> 日期：2026-03-19  
> 作者：万一

---

## 1. 测试策略

### 1.1 测试金字塔

```
                    ┌─────────┐
                    │  E2E    │  ← 端到端测试（用户流程）
                    │  测试   │
                  ┌─┴─────────┴─┐
                  │  集成测试   │  ← Agent 协作、RAG 检索
                  └─────────────┘
                ┌───────────────────┐
                │     单元测试       │  ← 函数、工具、工具类
                └───────────────────┘
```

### 1.2 测试覆盖目标

| 测试类型 | 覆盖率目标 | 优先级 |
|---------|-----------|--------|
| 单元测试 | > 80% | P0 |
| 集成测试 | > 70% | P0 |
| E2E 测试 | 核心流程 100% | P0 |
| 性能测试 | 关键指标 | P1 |
| 输出质量测试 | 抽样评估 | P1 |

---

## 2. 单元测试

### 2.1 核心模块测试

| 模块 | 测试内容 | 预期结果 |
|------|---------|---------|
| **main.py** | 参数解析 | 正确解析 --topic, --output, --theme, --language |
| | 文件命名 | 中文主题 → ASCII 文件名 |
| | UTF-8 编码 | 控制台输出无乱码 |
| **ppt_generator.py** | JSON 解析 | 有效 JSON → PPT 对象 |
| | 幻灯片类型 | 支持所有定义的类型 |
| | 图表生成 | 正确生成柱状图、饼图、折线图 |
| | 主题配色 | tech_blue/warm_orange/nature_green |
| **crew.py** | Agent 初始化 | 两个 Agent 正确创建 |
| | Task 定义 | analyze_task + design_task |
| | 知识库加载 | 8 个知识文件加载成功 |
| | Embedder 配置 | DashScope API 正确配置 |

### 2.2 工具测试

| 工具 | 测试内容 | 预期结果 |
|------|---------|---------|
| **web_search** | API Key 缺失 | 优雅降级，返回提示信息 |
| | 正常搜索 | 返回搜索结果 |
| **format_citation** | arXiv 格式 | 正确引用格式 |
| **check_data_freshness** | 日期检查 | 正确计算天数差 |

### 2.3 测试用例

```python
# test_unit.py

class TestMain:
    def test_save_report_ascii_filename(self):
        """中文主题应生成 ASCII 文件名"""
        # 输入: "AI Agent 技术"
        # 预期: 文件名不含中文字符
        
    def test_save_ppt_structure_valid_json(self):
        """PPT 结构应为有效 JSON"""
        
    def test_utf8_encoding_windows(self):
        """Windows 控制台 UTF-8 编码"""
        
class TestPPTGenerator:
    def test_all_slide_types(self):
        """测试所有幻灯片类型"""
        # title, agenda, content, key_findings, methodology,
        # analysis, diagram, chart, swot, conclusion, 
        # recommendations, closing
        
    def test_chart_generation(self):
        """图表生成测试"""
        # column, bar, line, pie
        
    def test_theme_colors(self):
        """主题配色测试"""
        
class TestCrew:
    def test_agent_initialization(self):
        """Agent 初始化"""
        
    def test_knowledge_loading(self):
        """知识库加载"""
        
    def test_embedder_config(self):
        """Embedder 配置"""
```

---

## 3. 集成测试

### 3.1 Agent 协作测试

| 测试场景 | 输入 | 预期输出 |
|---------|------|---------|
| **analyze_task 单独执行** | 主题 "AI Agent" | Markdown 报告 |
| **design_task 单独执行** | 简化报告 | PPT JSON 结构 |
| **完整 Crew 流程** | 主题 "AI Agent" | 报告 + PPT |

### 3.2 RAG 检索测试

| 测试场景 | 查询 | 预期检索结果 |
|---------|------|-------------|
| 分析框架检索 | "竞争分析" | SWOT、波特五力 |
| PPT 技能检索 | "图表设计" | 图表设计指南 |
| 模板检索 | "报告格式" | 技术报告模板 |

### 3.3 测试用例

```python
# test_integration.py

class TestAgentCollaboration:
    def test_analyze_task_alone(self):
        """单独测试 analyze_task"""
        
    def test_design_task_alone(self):
        """单独测试 design_task（使用简化输入）"""
        
    def test_full_crew_flow(self):
        """完整 Crew 流程"""
        
class TestRAGRetrieval:
    def test_framework_retrieval(self):
        """分析框架检索"""
        
    def test_ppt_skill_retrieval(self):
        """PPT 技能检索"""
        
    def test_template_retrieval(self):
        """模板检索"""
```

---

## 4. E2E 测试

### 4.1 核心流程测试

| 测试场景 | 输入 | 验证点 |
|---------|------|--------|
| **中文主题完整流程** | "AI Agent 技术趋势" | 1. 报告生成成功 2. PPT 生成成功 3. 文件名无乱码 |
| **英文主题完整流程** | "AI Agent Technology Trends" | 1. 英文报告 2. 英文 PPT |
| **简短主题** | "AI" | 流程完成 |
| **长主题** | "人工智能技术在企业数字化转型中的应用与挑战分析" | 流程完成 |

### 4.2 边界测试

| 测试场景 | 输入 | 预期行为 |
|---------|------|---------|
| 空主题 | "" | 错误提示 |
| 特殊字符主题 | "AI@Agent#2024!" | 过滤特殊字符 |
| 超长主题 | 200 字符 | 截断处理 |

### 4.3 多语言测试

| 语言 | 参数 | 预期输出 |
|------|------|---------|
| 中文 | --language zh | 中文报告和 PPT |
| 英文 | --language en | 英文报告和 PPT |

### 4.4 测试用例

```python
# test_e2e.py

class TestE2E:
    def test_chinese_topic_full_flow(self):
        """中文主题完整流程"""
        
    def test_english_topic_full_flow(self):
        """英文主题完整流程"""
        
    def test_short_topic(self):
        """简短主题"""
        
    def test_long_topic(self):
        """长主题"""
        
    def test_empty_topic(self):
        """空主题（应报错）"""
        
    def test_special_characters_topic(self):
        """特殊字符主题"""
        
    def test_multilang_chinese(self):
        """中文输出"""
        
    def test_multilang_english(self):
        """英文输出"""
```

---

## 5. 性能测试

### 5.1 性能指标

| 指标 | 目标 | 当前值 | 状态 |
|------|------|--------|------|
| **端到端时间** | < 5 分钟 | ~90 秒 | ✅ |
| **知识库加载** | < 10 秒 | 28 秒 | ⚠️ 待优化 |
| **报告生成** | < 60 秒 | ~30 秒 | ✅ |
| **PPT 生成** | < 10 秒 | < 1 秒 | ✅ |
| **内存峰值** | < 500 MB | 148 MB | ✅ |

### 5.2 测试方法

```python
# test_performance.py

class TestPerformance:
    def test_e2e_time(self):
        """端到端时间测试"""
        start = time.time()
        # 执行完整流程
        elapsed = time.time() - start
        assert elapsed < 300  # 5 分钟
        
    def test_knowledge_loading_time(self):
        """知识库加载时间"""
        
    def test_report_generation_time(self):
        """报告生成时间"""
        
    def test_ppt_generation_time(self):
        """PPT 生成时间"""
        
    def test_memory_usage(self):
        """内存使用测试"""
```

---

## 6. 输出质量测试

### 6.1 报告质量评估

| 维度 | 评估标准 | 评分方式 |
|------|---------|---------|
| **完整性** | 包含标题、摘要、分析、结论 | 自动检查 |
| **结构化** | 章节清晰、层次分明 | 自动检查 |
| **长度控制** | 2000 字以内 | 自动统计 |
| **方法论应用** | 使用 PRD 定义的分析框架 | 人工评估 |
| **专业性** | 语言准确、逻辑清晰 | 人工评估 |

### 6.2 PPT 质量评估

| 维度 | 评估标准 | 评分方式 |
|------|---------|---------|
| **JSON 有效性** | 可被解析 | 自动检查 |
| **幻灯片数量** | 10-15 页 | 自动统计 |
| **类型覆盖** | 包含 title, agenda, content, conclusion | 自动检查 |
| **内容精简** | 每页 3-5 要点 | 自动统计 |
| **设计一致性** | 风格统一 | 人工评估 |

### 6.3 测试用例

```python
# test_quality.py

class TestReportQuality:
    def test_report_completeness(self):
        """报告完整性"""
        
    def test_report_structure(self):
        """报告结构化"""
        
    def test_report_length(self):
        """报告长度控制"""
        
class TestPPTQuality:
    def test_json_validity(self):
        """JSON 有效性"""
        
    def test_slide_count(self):
        """幻灯片数量"""
        
    def test_slide_type_coverage(self):
        """类型覆盖"""
        
    def test_content_conciseness(self):
        """内容精简度"""
```

---

## 7. 测试执行计划

### 7.1 Phase 1：单元测试（0.5 天）

- [ ] main.py 测试
- [ ] ppt_generator.py 测试
- [ ] crew.py 测试
- [ ] 工具测试

### 7.2 Phase 2：集成测试（0.5 天）

- [ ] Agent 协作测试
- [ ] RAG 检索测试

### 7.3 Phase 3：E2E 测试（0.5 天）

- [ ] 核心流程测试
- [ ] 边界测试
- [ ] 多语言测试

### 7.4 Phase 4：性能与质量测试（0.5 天）

- [ ] 性能指标测试
- [ ] 输出质量评估

---

## 8. 测试环境

### 8.1 环境配置

```bash
# Python 环境
conda activate insightforge

# 环境变量
DASHSCOPE_API_KEY=xxx
DASHSCOPE_MODEL_NAME=glm-5
```

### 8.2 测试命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/test_unit.py -v

# 运行集成测试
pytest tests/test_integration.py -v

# 运行 E2E 测试
pytest tests/test_e2e.py -v

# 运行性能测试
pytest tests/test_performance.py -v

# 测试覆盖率
pytest --cov=src tests/
```

---

## 9. 测试报告模板

### 9.1 每日测试报告

```markdown
# 测试报告 - YYYY-MM-DD

## 执行摘要
- 通过: X
- 失败: Y
- 跳过: Z

## 失败详情
| 测试用例 | 错误信息 | 状态 |
|---------|---------|------|
| xxx | xxx | 待修复 |

## 性能指标
| 指标 | 当前值 | 目标 |
|------|--------|------|
| E2E 时间 | XXs | <300s |

## 下一步
- [ ] 修复 xxx
- [ ] 优化 xxx
```

---

> 文档版本：1.0  
> 最后更新：2026-03-19
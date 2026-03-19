# 安全最佳实践

## 🚨 敏感信息保护

### 禁止硬编码的内容

| 类型 | 示例 | 替代方案 |
|------|------|---------|
| API Keys | `sk-xxx`, `api_key = "xxx"` | 环境变量 `os.getenv()` |
| 密码 | `password = "xxx"` | 环境变量 |
| Token | `token = "xxx"` | 环境变量 |
| 私钥 | `private_key = "xxx"` | 文件 + .gitignore |

### 正确做法

```python
# ✅ 正确：从环境变量加载
import os
api_key = os.getenv("OPENAI_API_KEY")

# ❌ 错误：硬编码
api_key = "sk-xxxxxxxxxxxxxxxx"
```

## 📁 文件保护

### 必须在 .gitignore 中

```
.env
*.pem
*.key
credentials.json
secrets.yaml
```

### 可以提交

```
.env.example      # 配置模板（无实际值）
*.md              # 文档
```

## 🔒 Git Hooks

### pre-commit 检测

项目已配置 pre-commit hook，会自动扫描：
- OpenAI-style API keys (`sk-xxx`)
- Coding API keys (`sk-sp-xxx`)
- `api_key = "..."` 模式
- `password = "..."` 模式
- `secret = "..."` 模式

### 安装

```bash
# 方法 1: 使用 pre-commit (推荐)
pip install pre-commit
pre-commit install

# 方法 2: 直接使用 (已配置)
# .git/hooks/pre-commit 已就绪
```

### 手动扫描

```bash
# 扫描所有文件
grep -rnE "sk-[a-zA-Z0-9]{20,}" --include="*.py" .

# 或使用 detect-secrets
pip install detect-secrets
detect-secrets scan > .secrets.baseline
```

## 🛡️ 事件响应

### 如果不小心提交了敏感信息

1. **立即撤销** - 在控制台删除/重置 API Key
2. **清理历史** - 使用 `git filter-branch` 清除
3. **强制推送** - 更新远程仓库
4. **通知团队** - 如有协作者，通知他们 rebase

### 清理命令参考

```bash
# 备份
git branch backup-before-cleanup

# 清理
git filter-branch --force --tree-filter \
  'find . -type f -exec sed -i "s/YOUR_SECRET/REDACTED/g" {} \;' \
  HEAD

# 清理旧 refs
rm -rf .git/refs/original
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 强制推送
git push origin --force --all
```

## ✅ 检查清单

提交前确认：

- [ ] `.env` 未被跟踪 (`git status` 不显示 `.env`)
- [ ] 代码中无硬编码密钥
- [ ] pre-commit hook 已安装
- [ ] `.env.example` 已更新（如有新配置项）

---

> 最后更新：2026-03-19
> 维护者：万一
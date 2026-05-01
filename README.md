# AI 代码审查 Agent

基于 GPT-4 的智能代码审查系统，自动化发现代码问题、提供改进建议、生成 PR 描述。

## 功能特性

- 🐛 自动检测代码 bug 和逻辑错误
- ✅ 检查代码风格和最佳实践
- 🔒 发现安全漏洞和性能问题
- 📝 自动生成 PR 描述
- 🤖 GitHub PR 集成
- 📊 代码质量评分

## 安装

```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

## 使用

### 命令行使用

```python
from code_review_agent import CodeReviewAgent

agent = CodeReviewAgent()
result = agent.full_review("./your-repo")
print(f"总体评分：{result['overall_score']}")
```

### GitHub PR 集成

```python
from github_integration import GitHubIntegration

integration = GitHubIntegration()
integration.review_pr("your-username/your-repo", 123)
```

## 项目结构

```
├── code_review_agent.py    # 核心审查 Agent
├── github_integration.py   # GitHub 集成
├── requirements.txt        # 依赖
└── .env.example           # 环境变量示例
```

# harness-learning 学习仓库

用于学习 **Harness 工程**相关内容：收集关注的学习资料与开源项目，统一管理、按来源分类归档。

## 目录结构

| 目录 | 用途 |
|------|------|
| `00-inbox/` | **临时目录**。新移入的资料先放这里，待确定意图后移入下方分类目录 |
| `01-projects/` | **开源项目**。每个项目一个子目录，目录名 = 项目名（如 `deepseek-harness-hub/`） |
| `02-docs/` | **学习资料**。文档、教程、视频、笔记等单篇资料，按主题建子目录整理 |
| `README.md` | 本索引：目录说明 + 使用流程 + 项目登记表 |

## 使用流程

1. 新资料（项目/文档）复制进 `00-inbox/`
2. 查看资料、确定学习意图后：
   - 开源项目 → 移动到 `01-projects/<项目名>/`
   - 单篇资料 → 移动到 `02-docs/<主题>/`
3. 在下方「项目登记表」中登记一行（名称、来源、意图、状态）
4. 提交 Git：`git add .` 然后 `git commit`

## 项目登记表

| 项目/资料 | 来源 | 意图（为什么学） | 状态 |
|-----------|------|------------------|------|
| ai-agent-handbook-main | GitHub | AI Agent 实践手册，学习 Agent 工程 | 学习中 |
| codex-cli-docs | OpenAI 官方文档（learn.chatgpt.com） | Codex CLI 官方产品文档离线资料集（31 页中文译文 + 英文存档） | 学习中 |
| Fission-AI-OpenSpec | GitHub（Fission-AI/OpenSpec） | OpenSpec 官方文档集：写代码前先与 AI 对齐计划的规范驱动工作流 | 待整理 |
| mattpocock-skills | GitHub（mattpocock） | Matt Pocock 的 Agent skills 集合（engineering/productivity），参考技能设计与提示词写法 | 待整理 |

> 每移入一个新项目，在表中追加一行；状态建议用：待整理 / 学习中 / 已掌握 / 弃用。

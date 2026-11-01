# harness-learning 学习仓库

用于学习 **Harness 工程**相关内容：收集关注的学习资料与开源项目，统一管理、按内容性质分类归档。

## 目录结构

| 目录 | 用途 |
|------|------|
| `00-inbox/` | **临时目录**。新移入的资料先放这里，待确定意图后移入下方分类目录 |
| `01-projects/` | **需要研究的软件项目（源码）**。每个项目一个子目录，目录名 = 项目名（如 `codex-main/`、`pi-main/`） |
| `02-docs/` | **harness 产品 / Agent skill / Agent 使用相关文档**。原始内容或二次整理（可读性优化后）的文档，按主题建子目录 |
| `03-bin/` | 工具安装包等二进制文件 |
| `README.md` | 本索引：目录说明 + 使用流程 + 登记表 |

## 使用流程

1. 新资料（项目/文档）复制进 `00-inbox/`
2. 查看资料、确定学习意图后，先判断资料性质：
   - **需要研究的软件项目（源码类，如 harness 项目）** → 移动到 `01-projects/<项目名>/`
   - **文档、手册、skill 集合、产品/工具使用资料** → 移动到 `02-docs/<主题>/`，可保留原始内容并逐步二次整理
3. 在下方对应登记表中登记一行（名称、来源、意图、状态）
4. 提交 Git：`git add .` 然后 `git commit`

## 登记表

### 01-projects（研究的软件项目）

| 项目 | 来源 | 意图（为什么学） | 状态 |
|-----------|------|------------------|------|
| codex-main | GitHub（openai/codex） | Codex CLI 官方源码，学习 Agent harness 的 CLI、Rust 核心、SDK 与工具执行架构 | 待整理 |
| pi-main | GitHub（pi.dev / @earendil-works/pi-coding-agent） | Pi：极简可扩展的 Agent harness，学习 Agent 工程、extensions/skills/packages 扩展机制 | 待整理 |

### 02-docs（文档 / 手册 / skill 集合）

| 资料 | 来源 | 意图（为什么学） | 状态 |
|-----------|------|------------------|------|
| codex-cli-docs | OpenAI 官方文档（learn.chatgpt.com）+ 中文整理站（codex-docs.com） | Codex 系列资料主体域：CLI（31 页中文译文 + 英文存档）+ App Server / SDK（3 页中文存档），内部按 codex-cli / code-app-server / codex-sdk 分大类 | 学习中 |
| ai-agent-handbook-main | GitHub | AI Agent 实践手册，学习 Agent 工程 | 学习中 |
| Fission-AI-OpenSpec | GitHub（Fission-AI/OpenSpec） | OpenSpec 官方文档集：写代码前先与 AI 对齐计划的规范驱动工作流 | 待整理 |
| mattpocock-skills | GitHub（mattpocock） | Matt Pocock 的 Agent skills 集合（engineering/productivity），参考技能设计与提示词写法 | 待整理 |
| pi-coding-agent-docs | pi-main（packages/coding-agent/docs，v1.4.0） | Pi 官方文档二次整理（仿 codex-cli-docs）：00 说明 + 01 索引 + 10 个中文主题页（总览/模型/配置/会话/终端/扩展/MCP/SDK/安全/CLI）+ source 英文存档（42 篇 + docs.json + 4 图） | 学习中 |

> 每移入一个新项目/资料，在对应表中追加一行；状态建议用：待整理 / 学习中 / 已掌握 / 弃用。

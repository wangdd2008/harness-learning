# OpenSpec 文档

欢迎。这里是 OpenSpec 的一切内容所在。

OpenSpec 帮助你和你的 AI 编程助手**在编写任何代码之前就构建什么达成一致。**你描述变更，AI 起草一份简短的规格说明和任务清单，你们双方查看同一份计划，然后工作才开始。不再会出现中途发现 AI 构建错误的情况。

如果你只能读两篇文档，那就读这两篇：

1. [开始使用](getting-started.md)：安装、初始化并完成你的第一次变更。
2. [命令如何工作](how-commands-work.md)：你在哪里输入 `/opsx:propose`（提示：在你的 AI 聊天中，而不是终端里）。这几乎让每个人都困惑过一次。

第二篇比你想象的更重要。OpenSpec 有两个部分：一个在终端中运行的命令行工具，以及你给 AI 助手的斜杠命令。知道哪个是哪个可以避免你最常见的困惑时刻。

> **最先养成的最佳习惯：当你不确定要构建什么时，从 `/opsx:explore` 开始。**它是一个无风险的思考伙伴，可以阅读你的代码、权衡选项，并在编写任何代码之前将一个模糊的想法打磨成具体的计划。[先探索](explore.md)指南阐述了这一点。

## 选择你的路径

**我是新手。**从[开始使用](getting-started.md)开始，然后浏览一下[核心概念速览](overview.md)。当某些内容让你感到困惑时，[常见问题](faq.md)和[术语表](glossary.md)就在附近。

**我有一个问题，但还没有计划。**这是最常见的情况，它有一个专门的答案：[先探索](explore.md)。使用 `/opsx:explore` 在与 AI 思考之前不要承诺任何事情。

**我有一个大型现有代码库。**你不需要记录所有内容。[在现有项目中使用 OpenSpec](existing-projects.md)展示了如何在真实的、遗留的代码中开始，而不需要全盘翻新。

**我只想让一切工作。**[安装](installation.md)，运行 `openspec init`，然后阅读[命令如何工作](how-commands-work.md)，这样你的第一个斜杠命令就能正确运行。或者将设置交给你的助手，使用[AI 辅助安装提示](installation.md#install-with-your-ai-assistant)。

**我喜欢通过示例学习。**[示例与配方](examples.md)页面从头到尾展示了真实的变更：一个小功能、一个 bug 修复、一次重构、一次探索。

**AI 刚刚起草了一个计划——现在怎么办？**阅读它。[审查变更](reviewing-changes.md)展示了在两分钟内捕捉错误方向的方法，而[编写好的规格说明](writing-specs.md)则涵盖了值得批准的计划应该包含什么内容。

**我在团队中工作。**[OpenSpec 在团队中](team-workflow.md)展示了变更如何映射到分支和拉取请求，以及队友如何在代码之前审查计划。

**我从旧工作流迁移而来。**[迁移指南](migration-guide.md)解释了发生了什么变化以及原因，并保证你现有的工作是安全的。

**我想让它适应我们团队的工作流程。**[自定义](customization.md)涵盖了项目配置、自定义模式和共享上下文。

**有些问题。**[故障排除](troubleshooting.md)收集了人们实际遇到的故障及其修复方法。

## 完整地图

### 从这里开始

| 文档 | 它提供什么 |
|------|-----------|
| [开始使用](getting-started.md) | 安装、初始化并从头到尾运行你的第一次变更 |
| [先探索](explore.md) | 使用 `/opsx:explore` 在承诺之前思考一个想法 |
| [命令如何工作](how-commands-work.md) | 斜杠命令在哪里运行、"交互模式"是什么意思、终端与聊天 |
| [核心概念速览](overview.md) | 一页纸上的完整心智模型：规格说明、变更、差异、归档 |
| [安装](installation.md) | npm、pnpm、yarn、bun、Nix、交给 AI 助手处理的安装提示，以及如何验证安装成功 |

### 日常使用

| 文档 | 它提供什么 |
|------|-----------|
| [工作流](workflows.md) | 常见模式以及何时使用每个命令 |
| [示例与配方](examples.md) | 真实变更的完整示例，可复制粘贴 |
| [编写好的规格说明](writing-specs.md) | 强大的需求和场景是什么样的，以及如何调整变更大小 |
| [审查变更](reviewing-changes.md) | 在编写任何代码之前对起草的计划进行两分钟的审查 |
| [OpenSpec 在团队中](team-workflow.md) | 变更如何适应分支、拉取请求和审查 |
| [在现有项目中使用 OpenSpec](existing-projects.md) | 在大型遗留代码库中采用 OpenSpec |
| [编辑和迭代变更](editing-changes.md) | 更新产物、回退、协调手动编辑 |
| [命令](commands.md) | 每个 `/opsx:*` 斜杠命令的参考 |
| [CLI](cli.md) | 每个 `openspec` 终端命令的参考 |

### 深入理解

| 文档 | 它提供什么 |
|------|-----------|
| [概念](concepts.md) | 规格说明、变更、产物、模式、归档的长篇解释 |
| [OPSX 工作流](opsx.md) | 为什么工作流是流动的而不是分阶段的，以及架构深入解析 |
| [术语表](glossary.md) | 每个术语在一个地方定义 |

### 让它成为你的

| 文档 | 它提供什么 |
|------|-----------|
| [自定义](customization.md) | 项目配置、自定义模式、共享上下文 |
| [多语言](multi-language.md) | 生成英语以外的语言的产物 |
| [支持的工具](supported-tools.md) | OpenSpec 集成的 30+ AI 工具，以及文件存放位置 |
| [社区展示](community.md) | 用 OpenSpec 构建和为 OpenSpec 构建的项目和资源 |

### 当你需要帮助时

| 文档 | 它提供什么 |
|------|-----------|
| [常见问题](faq.md) | 人们最常问的问题的快速答案 |
| [故障排除](troubleshooting.md) | 具体故障的具体修复 |
| [迁移指南](migration-guide.md) | 从旧工作流迁移到 OPSX |

### 跨仓库协调（测试版）

| 文档 | 它提供什么 |
|------|-----------|
| [存储：用户指南](stores-beta/user-guide.md) | 当工作跨越仓库或团队时，在自己的仓库中进行计划 |
| [代理合约](agent-contract.md) | 代理驱动的机器可读 CLI 接口 |

## 三十秒版本

```text
1. 安装        npm install -g @fission-ai/openspec@latest
2. 初始化      cd your-project && openspec init
3. 探索        （在你的 AI 聊天中）/opsx:explore           ← 可选，但好习惯
4. 提议        （在你的 AI 聊天中）/opsx:propose add-dark-mode
5. 构建        （在你的 AI 聊天中）/opsx:apply
6. 归档        （在你的 AI 聊天中）/opsx:archive
```

步骤 1 和 2 在你的终端中执行。其余的在你的 AI 助手的聊天中执行。这个划分是值得一提的事情，[命令如何工作](how-commands-work.md)详细解释了原因。步骤 3 是可选的，但在不确定时从 `/opsx:explore` 开始是最值得养成的习惯。

## 其他获取帮助的方式

- **Discord：** [discord.gg/YctCnvvshC](https://discord.gg/YctCnvvshC) 用于提问、想法和帮助。
- **GitHub Issues：** [github.com/Fission-AI/OpenSpec/issues](https://github.com/Fission-AI/OpenSpec/issues) 用于 bug 和功能请求。
- **`openspec feedback "your message"`** 从你的终端直接发送反馈（它会打开一个 GitHub issue）。

在这些文档中发现了错误、过时或令人困惑的内容？那是一个 bug。提交一个 issue 或 PR。文档改进是你可以做出的最有价值的贡献之一。

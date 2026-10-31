# 常见问题

人们最常问的问题的快速答案。如果你的问题实际上是"某个东西坏了"，[故障排除](troubleshooting.md) 是更好的页面。如果你想了解术语定义，参见 [词汇表](glossary.md)。

## 基础

### 什么是 OpenSpec，一句话？

一个轻量级层，让你和你的 AI 编码助手在写任何代码之前就达成一致，以书面形式。

### 为什么我想要那个？

因为 AI 助手即使在错误时也很自信。当需求只存在于聊天线程中时，AI 会用猜测填补空白，而你在代码存在后才发现。OpenSpec 将协议提前到错误修复还很便宜的时候。参见 [核心概念一览](overview.md) 了解完整案例。

### 我必须在所有事情上都使用它吗？

不。在协议重要的非平凡工作中使用它。对于一个字符的拼写错误，仪式可能不值得，这没问题。

### 我可以在大型现有代码库上使用它，还是只适用于新项目？

现有代码库是主要场景。OpenSpec 是 brownfield-first：你不需要 upfront 记录整个应用。你只为每个变更触及的部分编写 specs，你的 specs 会随时间在你实际做的工作周围自然填充。有一个专用指南：[在现有项目中使用 OpenSpec](existing-projects.md)。

### 它是否与特定 AI 工具绑定？

不。OpenSpec 可与 30+ 助手配合使用，包括 Claude Code、Cursor、Devin Desktop、GitHub Copilot、Gemini CLI、Codex 等。完整列表和每个工具的详细信息在 [支持的工具](supported-tools.md) 中。

## 运行命令

### 我在哪里输入 `/opsx:propose`？

在你的 AI 助手的聊天中，不是在你的终端中。这是最常见的混淆点，所以它有自己的页面：[命令如何工作](how-commands-work.md)。简而言之：`openspec ...` 在终端中运行，`/opsx:...` 在聊天中运行。

### 如何"启动交互模式"？

没有单独的模式需要启动。你像往常一样打开 AI 助手，然后在聊天中输入斜杠命令。斜杠命令就是你"进入" OpenSpec 的方式。（唯一真正交互的终端功能是 `openspec view`，一个用于浏览 specs 和变更的仪表板。）完整解释在 [命令如何工作](how-commands-work.md) 中。

### 我输入了斜杠命令但什么都没发生。为什么？

最有可能的是，你在终端中而不是 AI 聊天中输入了它，或者你使用了工具不注册的拼写，或者命令尚未安装。如果文件缺失 — 或者你从未设置工具 — 运行 `openspec init`；`openspec update` 只刷新已存在的文件。然后重启你的助手并使用"入门"下列出的形式 — 参见 [如何调用](supported-tools.md#how-to-invoke)。[故障排除](troubleshooting.md#commands-dont-show-up) 有完整检查清单。

### 为什么一个工具中是 `/opsx:propose` 的语法，在另一个工具中是 `/opsx-propose`？

每个 AI 工具对自定义命令的处理方式略有不同，OpenSpec 会按照工具加载文件的方式拼写。名为 `opsx-propose.md` 的命令文件输入为 `/opsx-propose`；放在 `commands/opsx/` 下的文件输入为 `/opsx:propose`。使用技能而非命令的工具使用技能名称 — Codex 需要 `$openspec-propose`，Kimi Code `/skill:openspec-propose`。`openspec init` 的"入门"提示已经为你选定的工具打印了正确的形式；完整表格在 [如何调用](supported-tools.md#how-to-invoke) 中。

### 技能和命令之间有什么区别？

两者都是 OpenSpec 写入的文件，以便你的助手运行工作流。技能（`.../skills/openspec-*/SKILL.md`）是较新的跨工具标准；命令（`.../commands/opsx-*`）是较旧的特定工具斜杠文件。你不需要选择。你只需输入斜杠命令，OpenSpec 就会安装你的工具使用的那种。

## 工作流

### 如果我不确定要构建什么，应该从哪里开始？

从 `/opsx:explore` 开始。它是一个无风险的思考伙伴，读取你的代码库，列出选项，并在写任何代码之前将模糊的问题转化为具体的计划。它在默认配置文件中，所以随时可用。当计划清晰时，它会移交给 `/opsx:propose`。这是最好的习惯，因为它阻止了热心的 AI 自信地构建错误的东西。参见 [探索优先](explore.md)。

### 最简单的流程是什么？

```text
/opsx:explore (可选)   then   /opsx:propose <你想要什么>   then   /opsx:apply   then   /opsx:archive
```

Explore 思考清楚，propose 起草计划，apply 构建它，archive 归档。当你已经确切知道想要什么时跳过 explore。

### `/opsx:propose` 和 `/opsx:new` 有什么区别？

`/opsx:propose` 是默认的一步命令：它创建变更并一次性起草所有规划产物。`/opsx:new` 是扩展命令集的一部分，只搭建一个空变更，让你用 `/opsx:continue`（或一次性用 `/opsx:ff`）逐个创建产物。除非你想要逐步控制，否则使用 propose。参见 [命令](commands.md)。

### 什么是 `core` 和扩展配置文件？

配置文件决定安装哪些斜杠命令。**Core**（默认）给你 `propose`、`explore`、`apply`、`update`、`sync`、`archive`。扩展集增加了 `new`、`continue`、`ff`、`verify`、`bulk-archive` 和 `onboard` 以进行更细粒度的控制。用 `openspec config profile` 切换，然后应用 `openspec update`。

### 我需要运行 `/opsx:sync` 吗？

通常不需要。Sync 将变更的 delta specs 合并到你的主 specs 中，而 `/opsx:archive` 会帮你做这个。只在想要在归档前手动合并 specs 时运行 sync，例如在一个长期运行的变更上。参见 [命令](commands.md#opsxsync)。

### 开始之后如何编辑 proposal、spec 或 task？

直接编辑文件。每个产物都是 `openspec/changes/<name>/` 中的纯 Markdown，没有锁定的阶段或特殊编辑模式。手动更改它，或让 AI 修订它（"update the design to use a queue"），然后继续。AI 总是根据当前文件内容工作。完整指南：[编辑与迭代变更](editing-changes.md)。

### 实施部分之后可以回去修改计划吗？

是的，随时都可以。工作流是流动的，所以审查和编辑不是你被锁在外面的阶段。编辑产物，然后继续。如果你想要一个结构化的检查来确认代码仍然符合计划，运行 `/opsx:verify`。参见 [编辑与迭代变更](editing-changes.md#how-do-i-go-back-to-review-after-implementing)。

### 我手动编辑了代码。如何与 OpenSpec 协调？

在归档前让它们同步，因为归档会使你的 specs 成为记录真相。如果代码现在正确，更新 delta spec 以匹配你交付的行为；如果 spec 正确，继续构建直到代码一致。`/opsx:verify` 会暴露不匹配。参见 [编辑与迭代变更](editing-changes.md#i-edited-the-code-by-hand-how-do-i-reconcile-that-with-openspec)。

### 何时应该更新现有变更 vs 开始新的？

当是同一项工作的精炼时更新；当意图根本改变或范围爆炸到完全不同的工作时重新开始。有一个决策流程图和示例在 [工作流：何时更新 vs 重新开始](workflows.md#when-to-update-vs-start-fresh) 中。

### 如果我的会话超出上下文，或需求在实施期间改变怎么办？

这就是 specs 证明自己的地方。因为计划存在于文件中（不仅仅是聊天历史中），你可以清除上下文，开始一个新的 AI 会话，然后用 `/opsx:apply` 继续；它会读取产物并从第一个未勾选的任务恢复。如果需求改变，编辑产物以匹配新的现实并继续。在开始实施之前保持上下文窗口干净也会产生更好的结果。

### 我应该将 `openspec/` 文件夹提交到 git 吗？

是的。你的 specs、活跃变更和归档是你项目历史的一部分。像任何其他源文件一样提交它们。

## Specs 和变更

### Spec 和 Design 有什么区别？

Spec 描述可观察的行为：系统做什么、其输入、输出和错误条件。Design 描述你将如何构建它：技术方法、架构决策、文件变更。如果实现可以在不改变外部可见行为的情况下改变，它属于 design，而不是 spec。参见 [概念](concepts.md#what-a-spec-is-and-is-not) 深入了解。

### 什么是 delta spec？

只描述正在变化的内容的 spec，使用 `ADDED`、`MODIFIED` 和 `REMOVED` 章节，而不是重述整个 spec。这是 OpenSpec 干净地处理现有系统编辑的方式。参见 [概念：Delta Specs](concepts.md#delta-specs)。

### 归档的变更去了哪里？

到 `openspec/changes/archive/YYYY-MM-DD-<name>/`，所有变更产物都保留。变更移出你的活跃列表。显式声明 `retire_capabilities: true` 的变更也可以删除一个能力移除其最终需求时的主能力 spec。

## 配置和自定义

### 如何告诉 AI 我的技术栈？

把它放在 `openspec/config.yaml` 的 `context:` 下。该文本被注入到每个规划请求中，所以 AI 总是知道你的栈和约定。参见 [自定义配置](customization.md#project-configuration)。

### 我可以生成英语以外的 specs 吗？

是的。将语言指令添加到配置的 `context:` 中。[多语言](multi-language.md) 有几个语言的复制粘贴片段。

### 我可以改变工作流本身吗？

是的，使用自定义模式。模式定义存在哪些产物以及它们如何相互依赖。用 `openspec schema fork spec-driven my-workflow` 复刻默认值，然后编辑。参见 [自定义配置](customization.md#custom-schemas)。

## 模型、隐私和升级

### 我应该使用哪个 AI 模型？

OpenSpec 最适合与高推理模型配合使用。README 推荐 Codex 5.5 和 Opus 4.7 等模型用于规划和实施。在开始实施之前保持上下文窗口干净。

### OpenSpec 收集数据吗？

它收集匿名使用统计：只有命令名称和版本。没有参数、路径、内容或个人数据，而且它在 CI 中自动关闭。使用 `export OPENSPEC_TELEMETRY=0` 或 `export DO_NOT_TRACK=1` 选择退出。

### 如何升级？

两步。升级包（`npm install -g @fission-ai/openspec@latest`），然后在每个项目中运行 `openspec update` 以刷新生成的技能和命令。

### 如何卸载 OpenSpec？

没有卸载命令，因为它只是一个全局包加上项目中的文件。移除包（`npm uninstall -g @fission-ai/openspec`），并可选删除 `openspec/` 目录和生成的工具文件。分步说明，包括什么可以安全保留，在 [安装：卸载](installation.md#uninstalling) 中。

## 获取帮助

### 我在哪里提问或报告 bug？

- **Discord：** [discord.gg/YctCnvvshC](https://discord.gg/YctCnvvshC)
- **GitHub Issues：** [github.com/Fission-AI/OpenSpec/issues](https://github.com/Fission-AI/OpenSpec/issues)
- **从你的终端：** `openspec feedback "your message"` 为你打开一个 GitHub issue。

### 这些文档是错的或令人困惑的。我该怎么办？

告诉我们，或修复它。文档 PR 是受欢迎和重视的。开个 issue 或发送 pull request。

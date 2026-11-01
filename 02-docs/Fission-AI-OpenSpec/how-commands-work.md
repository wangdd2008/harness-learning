# 命令如何工作

**要知道的一件事：OpenSpec 有两种命令，它们在两个不同的地方运行。**

- `openspec ...` 命令在你的**终端**中运行。（示例：`openspec init`。）
- `/opsx:...` 命令在你的**AI 助手的聊天**中运行。（示例：`/opsx:propose`。）

如果你曾经在终端中输入 `/opsx:propose` 然后什么也没发生，这就是原因。你在对 OpenSpec 的错误一半说话。斜杠命令不是终端命令。它们是你给 AI 编程助手的指令，在你会输入"添加一个登录表单"的同一个聊天框中。

那个单一的区别是新用户最常见的绊脚石，所以我们把它说清楚。

## 两个部分

OpenSpec 是一个项目戴着两顶帽子。

**CLI（终端一半）。**一个名为 `openspec` 的程序，你从 shell 安装和运行。它设置你的项目，列出和验证变更，显示仪表板，并归档完成的工作。你在 iTerm、VS Code 终端、PowerShell、任何你运行 `git` 或 `npm` 的地方输入这些。

```bash
openspec init        # 在此项目中设置 OpenSpec
openspec list        # 查看活跃变更
openspec view        # 打开交互式仪表板
```

**斜杠命令（聊天一半）。**`/opsx:propose` 和 `/opsx:apply` 等短命令，你在 AI 助手中输入。这些告诉 AI 遵循 OpenSpec 工作流：起草提案，编写规格说明，从任务列表构建，完成后归档。你在 Claude Code、Cursor、Devin Desktop、Copilot 或任何你使用的助手中输入这些。

```text
/opsx:propose add-dark-mode    （在你的 AI 聊天中输入）
/opsx:apply                    （在你的 AI 聊天中输入）
/opsx:archive                  （在你的 AI 聊天中输入）
```

这是一个图中的心智模型：

```text
        你的终端                           你的 AI 助手的聊天
   ┌──────────────────────┐               ┌──────────────────────────────┐
   │  $ openspec init     │   安装      │  /opsx:propose add-dark-mode  │
   │  $ openspec list     │  ────────►  │  /opsx:apply                  │
   │  $ openspec view     │   命令      │  /opsx:archive                │
   └──────────────────────┘   和技能    └──────────────────────────────┘
        在这里运行 openspec                   在这里运行 /opsx:*
```

注意箭头。在你的终端中运行 `openspec init` 是*安装*斜杠命令到你的 AI 工具中。终端一半设置聊天一半。之后，日常驱动主要在聊天中进行。

## "如何启动交互模式？"

**没有单独的交互模式需要启动。**这个问题经常出现，所以它值得一个直白的答案。

你不进入特殊的 OpenSpec 模式。你只需像往常一样打开你的 AI 编程助手，然后在聊天中输入斜杠命令。斜杠命令*就是*你"进入" OpenSpec 的方式。你的助手识别它，加载匹配的 OpenSpec 技能，然后开始遵循工作流。

所以真正的说明是：

1. 在你的项目中打开你的 AI 编程助手（Claude Code、Cursor、Devin Desktop 等）。
2. 在它的聊天中输入 `/opsx:propose`，与你输入任何其他请求的地方相同。
3. 观察自动完成：如果 OpenSpec 已安装，当你输入斜杠时，你会看到 `/opsx:propose`、`/opsx:apply` 等出现。

就是这样。没有模式要切换，没有守护进程要启动，没有单独的窗口。

真正交互式的东西存在于终端中：`openspec view`。它打开一个用于浏览你的规格说明和变更的仪表板。但那是查看器，不是你提议和构建的东西。构建通过聊天中的斜杠命令进行。

## 为什么存在这种划分

这值得理解，因为它解释了为什么 OpenSpec 能与 30 多种不同的 AI 工具一起工作。

CLI 是**引擎**。它知道规则：变更文件夹看起来如何，哪些产物依赖于哪些，如何将差异规格说明合并到你的真相来源。它在任何地方都是一样的。

斜杠命令是**方向盘**，每个 AI 工具都有稍微不同的一个。Claude Code 称它们为命令。Cursor 和 Devin Desktop 有自己的格式。有些工具称它们为技能。当你运行 `openspec init` 时，OpenSpec 为每个你选择的工具生成正确类型的文件，所以无论你喜欢哪个助手，相同的 `/opsx:propose` 意图都能工作。

这种设计的优势在于：你一次学会工作流，然后跨工具携带。权衡在于：命令的确切语法在不同工具之间可能略有不同，这是下一节。

## 按工具划分的斜杠命令语法

意图在任何地方都是相同的。拼写遵循你的工具加载的文件。

| 你的工具的命令文件 | 你如何输入 | 示例工具 |
|--------------------------|-----------------|---------------|
| `.../commands/opsx/<id>.*` | `/opsx:propose` | Claude Code、Gemini CLI、Crush |
| `.../opsx-<id>.*` | `/opsx-propose` | Cursor、GitHub Copilot (IDE)、Devin Desktop、Trae、Oh My Pi |
| `.amazonq/prompts/opsx-<id>.md` | `@opsx-propose` | Amazon Q Developer |
| none — 仅技能 | `/openspec-propose` | CodeArts、ForgeCode、Hermes、Mistral Vibe、Zed Agent、共享 `.agents` |
| none — Kimi Code | `/skill:openspec-propose` | Kimi Code |
| none — Codex CLI | `$openspec-propose` | Codex |

Devin 是唯一跨越两行的工具。Devin Desktop 读取 `.devin/workflows/`，所以 `/opsx-propose` 在那里工作；[Devin Local 不行](https://docs.devin.ai/desktop/devin-local)，所以在该代理上使用 `/openspec-propose` 技能。OpenSpec 写入 `.devin/skills/` 的技能在两者上都工作，这就是为什么它们通过技能名称相互引用。

每个工具都在[如何调用](supported-tools.md#how-to-invoke)中列出——该表是权威的。两行根本不是斜杠命令：Amazon Q 将其文件加载到使用 `@` 调用的提示库中，最后三行使用*技能*名称，它不是命令 id（`/opsx:apply` 是 `openspec-apply-change` 技能）。

如有疑问，请阅读 `openspec init` 打印的"开始使用"行：它已经使用了你的工具注册的形式。输入斜杠并观察自动完成也适用于那些显示斜杠命令的工具。

## 命令如何到达那里：技能和命令

当你运行 `openspec init`（或 `openspec update`）时，OpenSpec 会向你的项目中写入小文件，以便你的 AI 工具可以找到工作流。根据你的工具和设置，这些是**技能**、**命令**或两者。

- **技能**存在于 `.claude/skills/openspec-*/SKILL.md` 等地方。它们是新兴的跨工具标准：你的助手自动检测的指令文件夹。
- **命令**存在于 `.cursor/commands/opsx-<id>.md` 或 `.claude/commands/opsx/<id>.md` 等地方——布局是工具的，它决定你如何输入命令。它们是较旧的每个工具斜杠命令文件。Codex 不会获得生成的命令文件；使用 `.agents/skills/openspec-*`。

你不必关心你的工具使用哪个。你只需输入斜杠命令，它就会工作。但知道这些文件的存在有助于在出现问题时：如果你的命令消失，通常意味着这些文件缺失或过时，`openspec update` 会重新生成它们。

请参阅[支持的工具](supported-tools.md)了解每个工具的确切路径，以及[迁移指南](migration-guide.md)了解技能如何取代旧的仅命令方法。

## 确认已安装

快速检查，从最快到最慢：

1. **在你的 AI 聊天中输入斜杠。**开始输入 `/opsx` 并观察自动完成建议。如果它们出现，你就准备好了。在仅技能的工具（Codex、Kimi Code、CodeArts、ForgeCode、Hermes、Mistral Vibe、Zed Agent 或共享的 `.agents` 目标）上，`/opsx` 即使在健康的安装下也不会完成——请尝试上面的表格中的技能名称。
2. **查找文件。**对于 Claude Code，检查 `.claude/skills/` 是否包含 `openspec-*` 文件夹。其他工具使用它们自己的目录（[支持的工具](supported-tools.md)列出它们）。
3. **重新运行设置。**从你的项目根目录运行 `openspec update`。这会重新生成你配置的工具的技能和命令文件。
4. **重启你的助手。**许多工具在启动时扫描技能和命令，所以一个新窗口可能是缺失的步骤。

## 我有哪些命令？

默认情况下，OpenSpec 安装**核心**斜杠命令集：

- `/opsx:explore`：在与 AI 承诺变更之前先思考一个想法（当你不确定时的很好的第一步）
- `/opsx:propose`：创建一个变更并一次性起草其所有规划产物
- `/opsx:apply`：通过处理其任务列表来构建变更
- `/opsx:update`：修订变更的规划产物并保持它们的一致性
- `/opsx:sync`：将变更的规格更新合并到你的主规格说明中（通常是自动的）
- `/opsx:archive`：完成变更并将其归档

一个好的默认节奏是：当你弄清楚要做什么时`explore`，然后`propose`、`apply`、`archive`。[先探索](explore.md)指南解释了为什么这个开头步骤会得到回报。

还有一个**扩展**集，供想要更精细控制的人使用（`/opsx:new`、` /opsx:continue`、`/opsx:ff`、`/opsx:verify`、`/opsx:bulk-archive`、`/opsx:onboard`）。你可以通过 `openspec config profile` 打开它，然后通过 `openspec update` 应用。

刚接触所有这些？`/opsx:onboard`（在扩展集中）带你完成一个完整的变更，在你的代码库上，叙述每个步骤。这是最友好的介绍方式。

有关每个命令的详细说明，请参阅[命令](commands.md)。有关何时使用哪个，请参阅[工作流](workflows.md)。

## 干净的第一次运行

综合起来，这是整个序列，每个步骤都标明了发生地点。

```text
终端   $ npm install -g @fission-ai/openspec@latest
终端   $ cd your-project
终端   $ openspec init
              （将斜杠命令安装到你的 AI 工具中）

AI 聊天  /opsx:explore
              （可选：先与 AI 一起思考这个想法）

AI 聊天  /opsx:propose add-dark-mode
              （AI 起草 proposal、specs、design、tasks）

AI 聊天  /opsx:apply
              （AI 构建它，勾选任务）

AI 聊天  /opsx:archive
              （变更合并到你的规格说明中并归档）
```

两个终端步骤来设置。然后你生活在聊天中。这就是节奏。

## 相关

- [开始使用](getting-started.md)：完整的第一次变更演练
- [命令](commands.md)：每个斜杠命令的详细说明
- [CLI](cli.md)：每个终端命令的详细说明
- [支持的工具](supported-tools.md)：每个工具的语法和文件位置
- [常见问题](faq.md)：更多快速答案
- [故障排除](troubleshooting.md)：当命令不显示时的修复

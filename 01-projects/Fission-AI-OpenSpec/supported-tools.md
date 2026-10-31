# 支持的工具

OpenSpec 可与多种 AI 编码助手配合使用。当你运行 `openspec init` 时，OpenSpec 会根据你的活动配置文件/工作流选择和交付模式来配置选定的工具。

## 如何工作

对于每个选定的工具，OpenSpec 可以安装：

1. **技能**（如果交付包含技能）：`.../skills/openspec-*/SKILL.md`
2. **命令**（如果交付包含命令）：特定工具的 `opsx-*` 命令文件

Codex 仅使用技能：OpenSpec 为 Codex 安装 `.agents/skills/openspec-*/SKILL.md`，即使交付设置为 `commands`，并且它不会生成 Codex 自定义提示文件。旧版 `.codex/skills` 路径下的现有 OpenSpec 管理技能在替换写入后进行协调；自定义和不同的文件会被保留。

默认情况下，OpenSpec 使用 `core` 配置文件，其中包含：
- `propose`
- `explore`
- `apply`
- `update`
- `sync`
- `archive`

你可以通过 `openspec config profile` 启用扩展工作流（`new`、`continue`、`ff`、`verify`、`bulk-archive`、`onboard`），然后运行 `openspec update`。

## 如何调用

这些文档使用 `/opsx:propose` 作为规范名称，但每个工具会以它加载 OpenSpec 文件的方式拼写它。
在下面找到你的工具的命令路径，然后在这里匹配它的形式。

| OpenSpec 写入的命令文件 | 你输入 | 工具 |
|------------------------------|----------|-------|
| `.../commands/opsx/<id>.*` — `opsx/` 文件夹命名它 | `/opsx:<id>` | Claude Code, CodeBuddy, Crush, Gemini CLI, Lingma, Qoder, ZCode |
| `.../opsx-<id>.*` — 文件名就是命令 | `/opsx-<id>` | 所有其他生成命令文件的工具，除了 Amazon Q 和 Devin |
| `.devin/workflows/opsx-<id>.md` — 仅被 Devin 的两个代理之一读取 | `/opsx-<id>` on Devin Desktop, `/openspec-<skill>` on Devin Local | Devin Desktop\*\*\*\* |
| `.amazonq/prompts/opsx-<id>.md` — 一个提示，不是命令 | `@opsx-<id>` | Amazon Q Developer |
| none — 仅技能 | `/openspec-<skill>` | CodeArts, ForgeCode, Hermes, MiniMax Code, Mistral Vibe, Zed Agent, shared `.agents` |
| none — Kimi Code | `/skill:openspec-<skill>` | Kimi Code |
| none — Codex CLI | `$openspec-<skill>` | Codex ([`/openspec-<skill>` 不被识别](https://github.com/openai/codex/issues/11817)) |

所以在 Cursor 中 `/opsx:propose` 是 `/opsx-propose`，在 Amazon Q 中是 `@opsx-propose`，在 Codex 中是 `$openspec-propose`。

有两件事独立变化，因此行不会合并：

- **名称。** 第 1–2 行仅在文件如何命名命令上不同，
  `opsx-<id>` / `opsx:<id>` 词干对于每个生成命令文件的工具都是相同的。
- **包装器。** Amazon Q 将其文件加载到用
  `@` 调用的提示库中。仅使用技能的工具根本不生成命令文件，所以它们的
  最后三行使用 *技能* 名称 — 列在
  [生成的技能名称](#generated-skill-names) 下 — 它们不一对一映射到
  命令 id（`/opsx:apply` 是 `openspec-apply-change` 技能）。

上面的命令路径模式故意是中性扩展名（`.*`）：扩展名是工具的（Gemini CLI 用 `.toml`，Continue 用 `.prompt`，Kiro 和 GitHub Copilot 用 `.prompt.md`），一些工具在选择器中显示带有扩展名的名称。匹配目录形状，而不是扩展名。

OpenSpec 生成的文件和设置后打印的"入门"提示已经为你选定的工具使用了正确的形式 — 所以最快的答案是阅读该提示。

## 工具目录参考

| 工具 (ID) | 技能路径模式 | 命令路径模式 |
|-----------|---------------------|----------------------|
| Amazon Q Developer (`amazon-q`) | `.amazonq/skills/openspec-*/SKILL.md` | `.amazonq/prompts/opsx-<id>.md` |
| Antigravity (`antigravity`) | `.agent/skills/openspec-*/SKILL.md` | `.agent/workflows/opsx-<id>.md` |
| Auggie (`auggie`) | `.augment/skills/openspec-*/SKILL.md` | `.augment/commands/opsx-<id>.md` |
| IBM Bob Shell (`bob`) | `.bob/skills/openspec-*/SKILL.md` | `.bob/commands/opsx-<id>.md` |
| Claude Code (`claude`) | `.claude/skills/openspec-*/SKILL.md` | `.claude/commands/opsx/<id>.md` |
| Cline (`cline`) | `.cline/skills/openspec-*/SKILL.md` | `.clinerules/workflows/opsx-<id>.md` |
| Command Code (`command-code`) | `.commandcode/skills/openspec-*/SKILL.md` | `.commandcode/commands/opsx-<id>.md` |
| CodeArts (`codeartsagent`) | `.codeartsdoer/skills/openspec-*/SKILL.md` | 不生成（无命令适配器；使用基于技能的 `/openspec-*` 调用） |
| CodeBuddy (`codebuddy`) | `.codebuddy/skills/openspec-*/SKILL.md` | `.codebuddy/commands/opsx/<id>.md` |
| Codex (`codex`) | `.agents/skills/openspec-*/SKILL.md` | 不生成（仅技能；使用 `$openspec-*`） |
| Devin Desktop, 前身为 Windsurf (`devin`) | `.devin/skills/openspec-*/SKILL.md` | `.devin/workflows/opsx-<id>.md`\*\*\*\* |
| ForgeCode (`forgecode`) | `.forge/skills/openspec-*/SKILL.md` | 不生成（无命令适配器；使用基于技能的 `/openspec-*` 调用） |
| Continue (`continue`) | `.continue/skills/openspec-*/SKILL.md` | `.continue/prompts/opsx-<id>.prompt` |
| CoStrict (`costrict`) | `.cospec/skills/openspec-*/SKILL.md` | `.cospec/openspec/commands/opsx-<id>.md` |
| Crush (`crush`) | `.crush/skills/openspec-*/SKILL.md` | `.crush/commands/opsx/<id>.md` |
| Cursor (`cursor`) | `.cursor/skills/openspec-*/SKILL.md` | `.cursor/commands/opsx-<id>.md` |
| Factory Droid (`factory`) | `.factory/skills/openspec-*/SKILL.md` | `.factory/commands/opsx-<id>.md` |
| Gemini CLI (`gemini`) | `.gemini/skills/openspec-*/SKILL.md` | `.gemini/commands/opsx/<id>.toml` |
| GitHub Copilot (`github-copilot`) | `.github/skills/openspec-*/SKILL.md` | `.github/prompts/opsx-<id>.prompt.md`\*\* |
| Hermes Agent (`hermes`) | `.hermes/skills/openspec-*/SKILL.md`\*\*\* | 不生成（无命令适配器；使用基于技能的 `/openspec-*` 调用） |
| iFlow (`iflow`) | `.iflow/skills/openspec-*/SKILL.md` | `.iflow/commands/opsx-<id>.md` |
| Junie (`junie`) | `.junie/skills/openspec-*/SKILL.md` | `.junie/commands/opsx-<id>.md` |
| Kilo Code (`kilocode`) | `.kilocode/skills/openspec-*/SKILL.md` | `.kilo/command/opsx-<id>.md` |
| Kimi Code (`kimi`) | `.kimi-code/skills/openspec-*/SKILL.md` | 不生成（无命令适配器；使用基于技能的 `/skill:openspec-*` 调用） |
| Kiro (`kiro`) | `.kiro/skills/openspec-*/SKILL.md` | `.kiro/prompts/opsx-<id>.prompt.md` |
| Lingma (`lingma`) | `.lingma/skills/openspec-*/SKILL.md` | `.lingma/commands/opsx/<id>.md` |
| MiniMax Code (`minimax-code`) | `~/.minimax/skills/openspec-*/SKILL.md` | 不生成（无命令适配器；使用 MiniMax Code 技能） |
| Mistral Vibe (`vibe`) | `.vibe/skills/openspec-*/SKILL.md` | 不生成（无命令适配器；使用基于技能的 `/openspec-*` 调用） |
| Oh My Pi (`oh-my-pi`) | `.omp/skills/openspec-*/SKILL.md` | `.omp/commands/opsx-<id>.md` |
| OpenCode (`opencode`) | `.opencode/skills/openspec-*/SKILL.md` | `.opencode/commands/opsx-<id>.md` |
| Pi (`pi`) | `.pi/skills/openspec-*/SKILL.md` | `.pi/prompts/opsx-<id>.md` |
| SourceCraft Code Assistant for VS Code (`codeassistant`) | `.codeassistant/skills/openspec-*/SKILL.md` | `.codeassistant/commands/opsx-<id>.md` |
| Qoder (`qoder`) | `.qoder/skills/openspec-*/SKILL.md` | `.qoder/commands/opsx/<id>.md` |
| Qwen Code (`qwen`) | `.qwen/skills/openspec-*/SKILL.md` | `.qwen/commands/opsx-<id>.md` |
| [Rovo Dev CLI](https://support.atlassian.com/rovo/docs/use-rovo-dev-cli/) (`rovodev`) | `.rovodev/skills/openspec-*/SKILL.md` | 不生成。Rovo 没有斜杠命令表面 — 它自动匹配技能或通过提示匹配（例如 "use the openspec-propose skill"）；`/skills` 只管理它们。生成的内容引用技能名称，从不作为 `/openspec-*` 命令。 |
| [Zoo Code](https://github.com/Zoo-Code-Org/Zoo-Code) (`roocode`) | `.roo/skills/openspec-*/SKILL.md` | `.roo/commands/opsx-<id>.md` |
| Trae (`trae`) | `.trae/skills/openspec-*/SKILL.md` | `.trae/commands/opsx-<id>.md` |
| [Zed Agent](https://zed.dev/docs/ai/skills) (`zed`) | `.agents/skills/openspec-*/SKILL.md` | 不生成（仅技能；使用 `/openspec-*` 或 `@openspec-*`） |
| ZCode (`zcode`) | `.zcode/skills/openspec-*/SKILL.md` | `.zcode/commands/opsx/<id>.md` |
| Shared `.agents` skills (`agents`) | `.agents/skills/openspec-*/SKILL.md` | 不生成（无命令适配器；使用基于技能的 `/openspec-*` 调用） |

\*\* GitHub Copilot 提示文件在 IDE 扩展（VS Code、JetBrains、Visual Studio）中被识别为自定义斜杠命令。Copilot CLI 目前不直接消费 `.github/prompts/*.prompt.md`。选择 `github-copilot` 还可以设置 GitHub 托管的 **云端编码代理** — 参见下面的 [GitHub Copilot 云端编码代理](#github-copilot-cloud-coding-agent)。

\*\*\* Hermes 默认从 `~/.hermes/skills/` 加载技能。要使用项目本地 OpenSpec 技能，将项目 `.hermes/skills/` 目录添加到 `~/.hermes/config.yaml` 中的 `skills.external_dirs`；Hermes 随后会暴露用户可见的斜杠调用，如 `/openspec-propose`。

\*\*\*\* Windsurf 在 2026 年 6 月 2 日 [更名为 Devin Desktop](https://docs.devin.ai/desktop/devin-desktop-faq)，其配置目录也随之一并移动：`.devin/` 是首选的读写位置，`.windsurf/` 是旧版的只读回退。OpenSpec 遵循重命名 — 工具 id 是 `devin`，`--tools windsurf` 仍然解析到它，因此现有设置脚本继续工作。项目中仍保留 OpenSpec 文件在 `.windsurf/` 的，下一次 `openspec update` 时会提供移动选项；拒绝则保持原位，你自己写的文件永远不会被触碰。工作流通过文件名调用，因此 `.devin/workflows/opsx-apply.md` 是 `/opsx-apply`。[Devin Local 代理不支持工作流](https://docs.devin.ai/desktop/devin-local) — 仅支持技能，且它根本不读取 `.windsurf/` — 所以每当 OpenSpec 写入 Devin 技能时，它保留技能内容，入门提示保留在 `/openspec-*` 技能调用上，这在两个代理上都有效。在仅命令交付时不会写入技能，两者都回退到 `/opsx-*`。

SourceCraft Code Assistant 支持针对其 VS Code 扩展。其[自定义命令](https://sourcecraft.dev/portal/docs/en/code-assistant/operations/agent/slash-commands)和[技能](https://sourcecraft.dev/portal/docs/ru/code-assistant/operations/agent/skills)仅在 VS Code 中可用。此集成不配置 SourceCraft Web 或 JetBrains。

在仅技能交付时，请 Code Assistant 使用 `openspec-propose` 技能。技能通过请求匹配激活；OpenSpec 不会为此工具生成 `/openspec-*` 命令。

MiniMax Code 是全局仅技能集成。OpenSpec 只写入
`~/.minimax/skills/` 下的 `openspec-*` 目录；它不会创建
repo-local `.minimax` 或 `.mavis` 目录。仅命令交付会保留
现有的全局 MiniMax Code 技能，因此一个项目的交付设置
不能删除另一个项目使用的技能。

### GitHub Copilot 云端编码代理

GitHub 的 [Copilot 编码代理](https://docs.github.com/en/copilot/using-github-copilot/coding-agent) 在 GitHub Actions 环境中运行在 GitHub 上 — 与你的编辑器中的 Copilot 分开。OpenSpec 可以通过生成两个文件来设置它，以使用 OpenSpec CLI：

- `.github/workflows/copilot-setup-steps.yml` — 在代理环境中安装 `@fission-ai/openspec`
- `.github/agents/openspec.agent.md` — 告诉代理如何驱动 OpenSpec

因为这会向你的仓库写入一个 GitHub Actions 工作流，所以它是 **选择加入** 的：

| 方式 | 行为 |
|-----|----------|
| `openspec init`（交互式） | 询问是否设置云端文件。默认是 **否**。 |
| `openspec init --copilot-cloud` | 不提示直接设置（用于脚本/CI）。 |
| `openspec init --no-copilot-cloud` | 不提示直接跳过，并移除任何以前生成的文件。 |
| `openspec update` | 从不提示。仅在你选择加入（或项目已有它们）时刷新文件。如果你选择退出，它会移除 OpenSpec 管理的云端文件。 |

你的选择保存在 `openspec/config.yaml` 中作为 `githubCopilot.cloudAgent: true|false`，因此非交互式更新会遵守它。OpenSpec 只写入或移除其内容生成的文件 — 如果你自定义了 `copilot-setup-steps.yml` 或 `openspec.agent.md`，或者已经有了自己的，它们会保持不动，`init`/`update` 会告诉你。

### 何时选择共享的 `.agents` 目标

`agents` 是厂商中立的选项：它将技能写入 `.agents/skills/`，
许多代理工具读取的共享根目录，而不是特定工具的目录。

| 情况 | 选择 |
|-----------|------|
| 你的工具在上面有自己的行 | 它自己的 ID — 你获得该工具的集成，包括斜杠命令（如果支持） |
| 一个仓库上有多个代理，都读取 `.agents/skills` | `agents` — 一个技能树而不是每个工具一个 |
| 你的工具尚未列出但读取 `.agents/skills` | `agents` |

与特定工具 ID 一起选择它是可以的；每个通常写入自己的
根目录。Codex 和 Zed Agent 是例外，因为它们使用相同的规范
`.agents` 根目录。如果 Codex 与 Zed 或 `agents` 一起选择，OpenSpec 保留一个
Codex 主导的树。其交接命名 `$openspec-*` 用于 Codex，命名
`/openspec-*` 用于其他代理，因此 `--tools all` 和现有的多代理
设置无需两个写入者覆盖相同的文件即可继续工作。
OpenSpec 也在项目拥有 `.agents/skills/` 目录后自动提供它 — 仅仅一个 `.agents/` 是不够的，因为工具使用该根目录存放规则
和子代理定义。注意 `.agents` 不是 `.agent`：单数
目录属于 Antigravity。

有两件事要知道：

- **仅技能。** 没有命令适配器存在，因此不会写入 `opsx-*` 命令文件；在包含命令的交付模式下，`openspec init` 会在 `Commands skipped for: … (no adapter)` 下列出 `agents`。
  通过技能名称调用工作流 —
  大多数读取 `.agents/skills` 的助手将其拼写为 `/openspec-propose`，即 OpenSpec 设置提示打印的形式。目标是厂商中立的，因此如果它使用另一种形式，请检查你的助手的文档。
- **不会创建或编辑 `AGENTS.md`。** 目标是 `.agents/` 目录。
  如果你的根目录 `AGENTS.md` 仍保留旧版
  OpenSpec 标记块，`openspec update` 会移除它们 — 参见 [迁移指南](migration-guide.md)。

Zed 支持针对内置 Zed Agent。Zed 外部代理和终端线程使用它们自己的集成。Agent 技能需要
[Zed v1.4.2](https://github.com/zed-industries/zed/releases/tag/v1.4.2) 或更新版本。
在未信任的工作区中，项目本地技能不可用，直到你
[授予信任](https://zed.dev/docs/worktree-trust)。

因为 `.agents/skills/` 由 Codex、Zed Agent 和厂商中立目标共享，
值得了解 OpenSpec 对其声称的内容：
它只为你选定工作流的 `openspec-*` 技能目录写入、刷新和移除，
以及一个 `.openspec-target` 标记，记录是 Codex、
Zed Agent 还是厂商中立目标渲染了该共享树。该目录中的其他内容
保持不动。将 `openspec-*` 名称和标记视为 OpenSpec 的 —
下次 `openspec update` 时其中的编辑会被替换，与
其他每个工具相同。

对于标记前项目，OpenSpec 从管理技能引用推断所有权：
`$openspec-*` 表示 Codex，`/openspec-*` 表示厂商中立目标。一个通用
规范树与旧版 `.codex/skills` 一起被视为
较旧的双目标安装，并被合并到兼容的共享树中。

`openspec update` 也遵守此所有权。如果项目将 `.agents` 作为
厂商中立目标，且仅检测到来自分散提示文件的 Codex 安装残留，
更新会保留已建立的 `agents` 树而不是用 Codex 语法重写，
并保留那些旧版提示文件而不是删除它们。要将共享树移交给 Codex，
显式运行 `openspec init --tools codex`。

## 非交互式设置

对于 CI/CD 或脚本化设置，使用 `--tools`（和可选的 `--profile`）：

```bash
# 配置特定工具
openspec init --tools claude,cursor

# 配置所有支持的工具
openspec init --tools all

# 跳过工具配置
openspec init --tools none

# 覆盖此 init 运行的配置文件
openspec init --profile core
```

**可用的工具 ID (`--tools`)** — `windsurf` 也被接受，作为 `devin` 的别名：`amazon-q`、`antigravity`、`auggie`、`bob`、`claude`、`cline`、`command-code`、`codeartsagent`、`codex`、`devin`、`forgecode`、`codebuddy`、`continue`、`costrict`、`crush`、`cursor`、`factory`、`gemini`、`github-copilot`、`hermes`、`iflow`、`junie`、`kilocode`、`kimi`、`kiro`、`lingma`、`minimax-code`、`vibe`、`oh-my-pi`、`opencode`、`pi`、`qoder`、`qwen`、`roocode`、`codeassistant`、`trae`、`zed`、`zcode`、`agents`

## 工作流相关安装

OpenSpec 根据选定的工作流安装工作流产物：

- **Core 配置文件（默认）：** `propose`、`explore`、`apply`、`update`、`sync`、`archive`
- **自定义选择：** 所有工作流 ID 的任何子集：
  `propose`、`explore`、`new`、`continue`、`apply`、`update`、`ff`、`sync`、`archive`、`bulk-archive`、`verify`、`onboard`

换句话说，技能/命令数量取决于配置文件和交付方式，而不是固定的。

## 生成的技能名称

当由配置文件/工作流配置选择时，OpenSpec 生成以下技能：

- `openspec-propose`
- `openspec-explore`
- `openspec-new-change`
- `openspec-continue-change`
- `openspec-apply-change`
- `openspec-update-change`
- `openspec-ff-change`
- `openspec-sync-specs`
- `openspec-archive-change`
- `openspec-bulk-archive-change`
- `openspec-verify-change`
- `openspec-onboard`

命令行为请参见 [命令](commands.md)，`init`/`update` 选项请参见 [CLI](cli.md)。

## 相关

- [CLI 参考](cli.md) — 终端命令
- [命令](commands.md) — 斜杠命令和技能
- [入门指南](getting-started.md) — 首次设置

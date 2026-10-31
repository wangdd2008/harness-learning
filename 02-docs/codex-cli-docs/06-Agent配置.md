# Agent 配置

本页汇总 Codex CLI 中与 Agent 行为定制相关的四个核心主题：通过 `AGENTS.md` 文件注入持久化指令、使用子代理（subagents）并行处理复杂任务、调整模型速度模式（Fast / Ultrafast），以及通过规则文件精细控制沙箱外命令的执行权限。这些配置共同决定了 Codex 在不同项目和任务中的工作方式与安全边界。

## AGENTS.md

原文存档：[source/agents-md.md](source/agents-md.md)

Codex 在执行任何工作之前会先读取 `AGENTS.md` 文件。通过在全局指导之上叠加项目级覆盖规则，可以在每次打开仓库时都以一致的期望启动任务。

### Codex 如何发现指导文件

Codex 在启动时（每次运行一次；在 TUI 中通常每个启动会话一次）构建指令链。发现顺序如下：

1. **全局范围**：在 Codex 主目录（默认为 `~/.codex`，除非设置了 `CODEX_HOME`）中，Codex 优先读取 `AGENTS.override.md`；如果不存在则读取 `AGENTS.md`。此层级只使用第一个非空文件。
2. **项目范围**：从项目根目录（通常是 Git 根）开始，Codex 逐层向下遍历到当前工作目录。如果找不到项目根，则只检查当前目录。在路径上的每个目录中，依次检查 `AGENTS.override.md`、`AGENTS.md`，以及 `project_doc_fallback_filenames` 中配置的任何备用文件名。每个目录最多包含一个文件。
3. **合并顺序**：Codex 从根目录向下拼接文件，以空行分隔。靠近当前目录的文件会覆盖先前的指导，因为它们在合并后的 prompt 中出现得更晚。

Codex 会跳过空文件，并在合并总大小达到 `project_doc_max_bytes`（默认为 32 KiB）定义的上限后停止添加。参见 [05-配置-高级与参考.md](05-配置-高级与参考.md) 中的项目指令发现部分。达到上限时可以调大限制或把指令拆分到嵌套目录中。

### 创建全局指导

在 Codex 主目录中创建持久化默认值，使每个仓库都继承你的工作约定。

1. 确保目录存在：

```bash
mkdir -p ~/.codex
```

2. 创建 `~/.codex/AGENTS.md`，写入可复用的偏好：

```md
# ~/.codex/AGENTS.md

## Working agreements

- Always run `npm test` after modifying JavaScript files.
- Prefer `pnpm` when installing dependencies.
- Ask for confirmation before adding new production dependencies.
```

3. 在任意位置运行 Codex 以确认文件已加载：

```bash
codex --ask-for-approval never "Summarize the current instructions."
```

预期行为：Codex 在提出工作方案之前会引用 `~/.codex/AGENTS.md` 中的条目。

如果需要临时全局覆盖而不删除基础文件，使用 `~/.codex/AGENTS.override.md`。移除该覆盖文件即可恢复共享指导。

### 分层项目指令

仓库级文件让 Codex 了解项目规范，同时仍然继承全局默认值。

1. 在仓库根目录添加一个 `AGENTS.md`，涵盖基本设置：

```md
# AGENTS.md

## Repository expectations

- Run `npm run lint` before opening a pull request.
- Document public utilities in `docs/` when you change behavior.
```

2. 当特定团队需要不同规则时，在嵌套目录中添加覆盖。例如，在 `services/payments/` 目录内创建 `AGENTS.override.md`：

```md
# services/payments/AGENTS.override.md

## Payments service rules

- Use `make test-payments` instead of `npm test`.
- Never rotate API keys without notifying the security channel.
```

3. 从 payments 目录启动 Codex：

```bash
codex --cd services/payments --ask-for-approval never "List the instruction sources you loaded."
```

预期行为：Codex 先报告全局文件，其次是仓库根的 `AGENTS.md`，最后是 payments 覆盖文件。

Codex 一旦到达当前目录就停止搜索，因此应将覆盖文件放在离专项工作尽可能近的位置。

### 添加代码审查规则

对于 GitHub 中的 Codex 代码审查，在距离被审查代码最近的 `AGENTS.md` 中添加 `## Code Review Rules` 小节。仓库级检查放在根目录，服务级检查放在嵌套文件中。

```md
## Code Review Rules

### Experiment cohorts

- Do not filter treatment comparisons on post-exposure behavior, including conversion or retention.
  Safe path: build cohorts from assignment or exposure; report conversion as an outcome.
```

保持规则简洁，说明需要标记的行为以及任何安全路径或例外，格式化和 lint 检查留给 CI 处理。

### 自定义备用文件名

如果你的仓库已经使用了不同的文件名（例如 `TEAM_GUIDE.md`），将其添加到备用列表中，Codex 就会将其视为指令文件。

1. 编辑 Codex 配置：

```toml
# ~/.codex/config.toml
project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]
project_doc_max_bytes = 65536
```

2. 重启 Codex 或运行新命令以加载更新后的配置。

现在 Codex 在每个目录中按以下顺序检查：`AGENTS.override.md`、`AGENTS.md`、`TEAM_GUIDE.md`、`.agents.md`。不在此列表中的文件名不会被用于指令发现。更大的字节上限允许在截断前合并更多指导内容。

设置 `CODEX_HOME` 环境变量可以使用不同的配置文件，例如项目专属的自动化用户：

```bash
CODEX_HOME=$(pwd)/.codex codex exec "List active instruction sources"
```

预期行为：输出列出相对于自定义 `.codex` 目录的文件。

### 验证设置

- 在仓库根目录运行 `codex --ask-for-approval never "Summarize the current instructions."`。Codex 应按优先级顺序回显全局和项目文件中的指导。
- 使用 `codex --cd subdir --ask-for-approval never "Show which instruction files are active."` 确认嵌套覆盖替代了更广泛的规则。
- 要审计 Codex 加载了哪些指令文件，可通过 `codex -c log_dir=./.codex-log` 启用纯文本 TUI 日志，然后查看 `./.codex-log/codex-tui.log`；如果启用了会话日志，也可以检查最新的 `session-*.jsonl` 文件。
- 如果指令看起来过期，在目标目录重启 Codex。Codex 每次运行时都会重建指令链（以及每个 TUI 会话开始时），不需要手动清理缓存。

### 排查发现问题

- **什么都没加载**：确认你在预期的仓库中，且 `codex status` 报告的工作区根目录是你期望的。确保指令文件包含内容；Codex 会忽略空文件。
- **出现了错误的指导**：在目录树更高处或 Codex 主目录下查找 `AGENTS.override.md`。重命名或移除覆盖文件以回退到常规文件。
- **Codex 忽略备用名称**：确认你在 `project_doc_fallback_filenames` 中列出的名称没有拼写错误，然后重启 Codex 使配置生效。
- **指令被截断**：调大 `project_doc_max_bytes` 或将大文件拆分到嵌套目录中，以保持关键指导完整。
- **配置文件混淆**：在启动 Codex 之前运行 `echo $CODEX_HOME`。非默认值会将 Codex 指向与你编辑的目录不同的主目录。

## 子代理

原文存档：[source/subagents.md](source/subagents.md)

ChatGPT Work 和 Codex 可以通过并行启动专门的子代理并在单个回复中收集结果来运行子代理工作流。这对于高度并行的复杂任务特别有帮助，例如代码库探索或实现多步骤功能计划。

在本地 Codex 客户端中，你还可以为不同任务定义具有不同模型配置和指令的自定义代理。

### 可用性

当前 Codex 版本默认启用子代理工作流。子代理活动会显示在 ChatGPT 桌面应用、Codex CLI 和 IDE 扩展中。

由于每个子代理都执行自己的模型和工具工作，子代理工作流比可比的单代理运行消耗更多的 token。

在交互式 CLI 会话中，要求 Codex 使用子代理。Codex 也可以遵循适用的 `AGENTS.md` 或技能指令中的委托请求。使用 `/subagents` 在代理线程运行时查看和切换。主线程将子代理结果收集到最终回复中。

### 子代理工作流的优势

即使有大上下文窗口，模型也有极限。如果你用大量嘈杂的中间输出（探索笔记、测试日志、堆栈跟踪、命令输出）淹没主聊天（你在此定义需求、约束和决策的地方），会话随着时间推移会变得不太可靠。

这通常被描述为：

- **上下文污染**：有用信息被嘈杂的中间输出淹没。
- **上下文腐烂**：随着聊天中充斥着不太相关的细节，性能下降。

子代理工作流通过将嘈杂工作移出主线程来解决这些问题：

- 让**主代理**专注于需求、决策和最终输出。
- 并行运行专门的**子代理**进行探索、测试或日志分析。
- 子代理只返回**摘要**，而非原始中间输出。

当工作可以独立并行运行时，它们还可以节省时间；通过将大型任务拆分为有界片段，使更大形状的任务更易于处理。例如，Codex 可以将数百万 token 文档的分析拆分为更小的问题，并将提炼后的要点返回给主线程。

作为起点，将并行代理用于读密集型任务，如探索、测试、分类和总结。对于并行写密集型工作流要更加小心，因为多个代理同时编辑代码可能产生冲突并增加协调开销。

### 核心术语

Codex 在子代理工作流中使用以下几个相关术语：

- **子代理工作流**：Codex 运行并行代理并组合其结果的工作流。
- **子代理**：Codex 为处理特定任务而启动的委托代理。
- **代理线程**：子代理执行工作的线程。支持的客户端允许你打开这些线程以查看进度或结果。

### 触发子代理工作流

直接要求子代理或并行代理工作。Codex 也可以在适用的项目或技能指令要求时进行委托。

实际操作中，手动触发意味着使用直接指令，例如"启动两个代理"、"并行委托这项工作"或"每个要点使用一个代理"。子代理工作流比可比的单代理运行消耗更多 token，因为每个子代理都执行自己的模型和工具工作。

一个好的子代理 prompt 应说明如何划分工作、Codex 是否应等待所有代理完成后再继续，以及应返回什么摘要或输出。

```text
Review this branch with parallel subagents. Spawn one subagent for security risks, one for test gaps, and one for maintainability. Wait for all three, then summarize the findings by category with file references.
```

### 选择模型和推理强度

不同的代理需要不同的模型和推理设置。

如果你没有配置子代理模型或 `model_reasoning_effort`，子代理会继承父代理的模型和推理强度。如果显式启动请求或 `[agents]` 默认值选择了某个模型但没有明确的推理强度，子代理使用该模型的默认推理强度。为了在每个任务中平衡智能、速度和价格，可以在 prompt 中请求特定模型或推理强度，在 `config.toml` 中配置 `[agents]` 默认值，或在自定义代理文件中直接设置 `model` 和 `model_reasoning_effort`。

例如，使用 `gpt-6-luna` 进行快速扫描，或使用更高强度的 `gpt-6.1-sol` 配置处理更复杂的推理。

#### 模型选择

- **`gpt-6.1-sol`**：对要求高的代理从这里开始。用于模糊、多步骤的工作，需要在更大的上下文中进行规划、工具使用、验证和跟进。
- **`gpt-6-luna`**：用于快速、范围狭窄的代理，处理清晰、可重复或高容量的工作。

#### 推理强度（`model_reasoning_effort`）

对于 GPT-6.1 Sol，使用你的客户端和所选模型支持的推理强度。对于显式模型设置，GPT-6 Luna 从 `high` 开始，GPT-6 Astra 从 `low` 开始。根据任务使用所选模型支持的级别进行调整。

- **`ultra`**：当所选模型支持时，用于最深层推理。
- **`max`** 和 **`xhigh`**：当所选模型支持这些级别时，用于特别要求高的推理。
- **`high`**：当代理需要追踪复杂逻辑、检查假设或处理边缘情况时使用（例如审查者或安全专注的代理）。
- **`medium`**：平衡速度和深度。
- **`low`**：当任务简单且速度最重要时使用。

更高的推理强度会增加响应时间和 token 用量，但可以提高复杂工作的质量。参见 [05-配置-高级与参考.md](05-配置-高级与参考.md) 中的配置参考部分。

### 编排和线程控制

ChatGPT 或 Codex 处理跨代理的编排，包括启动新的子代理、路由后续指令、等待结果和关闭代理线程。

当许多代理运行时，Codex 会等待所有请求的结果可用，然后返回合并后的响应。

要实际体验，可以在你的项目上尝试以下 prompt：

```text
I would like to review the following points on the current PR (this branch vs main). Spawn one agent per point, wait for all of them, and summarize the result for each point.
1. Security issue
2. Code quality
3. Bugs
4. Race
5. Test flakiness
6. Maintainability of the code
```

### 管理子代理

- 在 CLI 中使用 `/subagents` 在活动代理线程之间切换并查看正在进行的线程。
- 直接要求 Codex 引导正在运行的子代理、停止它或关闭已完成的代理线程。

### 审批和沙箱控制

在交互式 CLI 会话中，即使你正在查看主线程，审批请求也可能从非活动代理线程弹出。审批覆盖层显示源线程标签，你可以按 `o` 在批准、拒绝或回答请求之前打开该线程。

在非交互式流程中，或者当运行无法弹出新审批时，需要新审批的操作会失败，Codex 将错误呈现回父工作流。

子代理继承父轮次的当前沙箱和审批设置，包括通过 `/permissions` 或 `--yolo` 所做的更改。自定义代理文件不能替换这些设置。

### 自定义代理

Codex 自带内置代理：

- `default`：通用后备代理。
- `worker`：专注于执行的代理，用于实现和修复。
- `explorer`：读密集型代码库探索代理。

要定义自己的自定义代理，在 `~/.codex/agents/` 下添加独立的 TOML 文件（个人代理）或在 `.codex/agents/` 下（项目范围代理）。

每个文件定义一个自定义代理。自定义代理可以更改模型设置和指令或禁用支持的功能。它们继承父代理的权限、提供者和 MCP 服务器；自定义代理文件不能覆盖这些设置。

每个独立的自定义代理文件必须定义：

- `name`
- `description`
- `developer_instructions`

如果自定义代理文件设置了 `model` 或 `model_reasoning_effort`，文件中的值优先。在应用文件之前，Codex 按以下顺序解析每个设置：显式启动值、对应的 `[agents]` 默认值、父代理的值。如果显式启动请求或 `[agents]` 默认值选择了模型但都没有提供推理强度，Codex 使用该模型的默认强度。只设置 `model` 的自定义代理文件会保留此先前解析的强度。如果所选模型不支持该强度或你想要不同的强度，请在文件中也设置 `model_reasoning_effort`。技能从父代理继承，自定义代理可以通过 `skills.config` 禁用单个技能。

#### 全局设置

全局子代理设置仍然位于 `config.toml` 中的 `[agents]` 下。

| 字段 | 类型 | 必填 | 用途 |
| --- | --- | :---: | --- |
| `agents.enabled` | boolean | 否 | 启用或禁用多代理工具。 |
| `agents.max_concurrent_threads_per_session` | number | 否 | 限制并发打开的已启动代理线程数，不包括主线程。 |
| `agents.default_subagent_model` | string | 否 | 设置已启动代理的默认模型。 |
| `agents.default_subagent_reasoning_effort` | string | 否 | 设置已启动代理的默认推理强度。 |
| `agents.interrupt_message` | boolean | 否 | 当代理轮次被中断时记录一条模型可见的消息。 |

**注意：**

- `agents.enabled` 默认为 `true`。设置为 `false` 可禁用多代理工具。
- 当你不设置 `agents.max_concurrent_threads_per_session` 时，Codex 会选择默认值。现有配置可以继续使用 `agents.max_threads` 作为旧别名。
- 显式启动值会覆盖 `agents.default_subagent_model` 和 `agents.default_subagent_reasoning_effort`。
- `agents.interrupt_message` 默认为 `true`。设置为 `false` 可从代理上下文中省略模型可见的中断消息。
- 如果自定义代理名称与内置代理（如 `explorer`）匹配，你的自定义代理优先。

#### 自定义代理文件模式

| 字段 | 类型 | 必填 | 用途 |
| --- | --- | :---: | --- |
| `name` | string | 是 | Codex 在启动或引用此代理时使用的代理名称。 |
| `description` | string | 是 | 面向用户的指导，说明 Codex 何时应使用此代理。 |
| `developer_instructions` | string | 是 | 定义代理行为的核心指令。 |

使用 `model`、`model_reasoning_effort`、`model_reasoning_summary` 和 `model_verbosity` 自定义模型行为。参见配置参考了解其接受值。

要减少自定义代理的功能，将支持的功能键设置为 `false`：`features.shell_tool`、`features.apps`、`features.plugins`、`features.memories` 或 `features.request_permissions_tool`。通过 `skills.config` 禁用单个技能，或通过 `skills.bundled.enabled = false` 禁用捆绑技能。设置 `skills.include_instructions = false` 可省略自动技能指令块。托管要求仍然适用。

其他会话设置，包括 `sandbox_mode`、`approval_policy`、`model_provider` 和 `mcp_servers`，放在自定义代理文件中时不会覆盖父配置。服务层级也遵循根会话的偏好。在父会话中配置 MCP 服务器，以便代理可以使用它们。

Codex 通过 `name` 字段识别自定义代理。将文件名与代理名称匹配是最简单的约定，但 `name` 字段才是事实来源。

#### 自定义代理示例

最好的自定义代理是范围狭窄且有明确主张的。为每个代理分配清晰的任务、与任务匹配的工具表面，以及防止其漂移到相邻工作的指令。

示例使用 GPT-6.1 Sol（当你的已登录账户或工作区有权限时）。如果不可用，选择你可以使用的模型。

**示例 1：PR 审查**

此模式将审查拆分到三个专注的自定义代理中：

- `pr_explorer` 映射代码库并收集证据。
- `reviewer` 查找正确性、安全和测试风险。
- `docs_researcher` 通过专用 MCP 服务器检查框架或 API 文档。

项目配置（`.codex/config.toml`）：

```toml
[agents]
max_concurrent_threads_per_session = 8

[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
```

`.codex/agents/pr-explorer.toml`：

```toml
name = "pr_explorer"
description = "Read-only codebase explorer for gathering evidence before changes are proposed."
model = "gpt-6-luna"
model_reasoning_effort = "high"
developer_instructions = """
Stay in exploration mode.
Do not edit files.
Trace the real execution path, cite files and symbols, and avoid proposing fixes unless the parent agent asks for them.
Prefer fast search and targeted file reads over broad scans.
"""
```

`.codex/agents/reviewer.toml`：

```toml
name = "reviewer"
description = "PR reviewer focused on correctness, security, and missing tests."
model = "gpt-6.1-sol"
model_reasoning_effort = "medium"
developer_instructions = """
Review code like an owner.
Do not edit files.
Prioritize correctness, security, behavior regressions, and missing test coverage.
Lead with concrete findings, include reproduction steps when possible, and avoid style-only comments unless they hide a real bug.
"""
```

`.codex/agents/docs-researcher.toml`：

```toml
name = "docs_researcher"
description = "Documentation specialist that uses the docs MCP server to verify APIs and framework behavior."
model = "gpt-6-luna"
model_reasoning_effort = "high"
developer_instructions = """
Use the docs MCP server to confirm APIs, options, and version-specific behavior.
Return concise answers with links or exact references when available.
Do not make code changes.
"""
```

此设置适用于以下 prompt：

```text
Review this branch against main. Have pr_explorer map the affected code paths, reviewer find real risks, and docs_researcher verify the framework APIs that the patch relies on.
```

**示例 2：前端集成调试**

此模式适用于 UI 回归、不稳定的浏览器流程或跨越应用代码与运行产品的集成错误。

项目配置（`.codex/config.toml`）：

```toml
[agents]
max_concurrent_threads_per_session = 6

[mcp_servers.chrome_devtools]
url = "http://localhost:3000/mcp"
startup_timeout_sec = 20
```

`.codex/agents/code-mapper.toml`：

```toml
name = "code_mapper"
description = "Read-only codebase explorer for locating the relevant frontend and backend code paths."
model = "gpt-6-luna"
model_reasoning_effort = "high"
developer_instructions = """
Map the code that owns the failing UI flow.
Do not edit files.
Identify entry points, state transitions, and likely files before the worker starts editing.
"""
```

`.codex/agents/browser-debugger.toml`：

```toml
name = "browser_debugger"
description = "UI debugger that uses browser tooling to reproduce issues and capture evidence."
model = "gpt-6.1-sol"
model_reasoning_effort = "medium"
developer_instructions = """
Reproduce the issue in the browser, capture exact steps, and report what the UI actually does.
Use browser tooling for screenshots, console output, and network evidence.
Do not edit application code.
"""
```

`.codex/agents/ui-fixer.toml`：

```toml
name = "ui_fixer"
description = "Implementation-focused agent for small, targeted fixes after the issue is understood."
model = "gpt-6-luna"
model_reasoning_effort = "high"
developer_instructions = """
Own the fix once the issue is reproduced.
Make the smallest defensible change, keep unrelated files untouched, and validate only the behavior you changed.
"""

[[skills.config]]
path = "/Users/me/.agents/skills/docs-editor/SKILL.md"
enabled = false
```

此设置适用于以下 prompt：

```text
Investigate why the settings modal fails to save. Have browser_debugger reproduce it, code_mapper trace the responsible code path, and ui_fixer implement the smallest fix once the failure mode is clear.
```

## 速度

原文存档：[source/speed.md](source/speed.md)

你可以在 Codex 中提高模型速度，代价是更高的用量。

### Fast 模式

Fast 模式为支持的模型加速，包括 GPT-6.1 Sol、GPT-6.1 Terra、GPT-6 Astra、GPT-6 Sol 和 GPT-6 Luna（在可用时）。对于 GPT-5.6，速度提升为 1.5 倍。

在 CLI 中使用 `/fast` 切换 Fast 模式。使用 `/statusline` 在页脚中显示它。你还可以在 `config.toml` 中通过 `service_tier = "fast"` 加上 `[features].fast_mode = true` 来持久化默认值。Fast 模式在你使用 ChatGPT 登录时可在 ChatGPT 桌面应用、Codex CLI 和 IDE 扩展中使用。

对于支持的模型，Fast 模式以 Standard 速率的 2.5 倍使用订阅包含额度。购买的积分和企业按需用量按 Standard 速率的 2 倍计费。

### Ultrafast 模式

Ultrafast 支持 GPT-6 Astra 和 GPT-6.1 Sol。

GPT-6 Astra Ultrafast 在 Codex 中生成 token 的速度比 Standard 模式下的 GPT-6 Astra 快 8 倍。

Ultrafast 在 Pro $500 以及符合条件的企业和教育版套餐中可用于 Codex 和 ChatGPT Work。在 Pro $500 上，Ultrafast 先使用你包含的用量额度，然后在该额度用完后使用可用积分。

Ultrafast 模式对购买的积分和企业按需用量按 Standard 速率的 6 倍计费。Ultrafast 以 Standard 速率的 8 倍使用订阅包含额度。

对于企业工作区，Ultrafast 默认关闭。工作区所有者可以通过工作区权限为选定用户或整个工作区启用访问。现有的按用户支出控制适用于符合条件的 Ultrafast 用量。

### 可用性和计费细节

**ChatGPT Work 和 Codex 共享用量。** 两者使用相同的定价、积分和用量限制。

GPT-5.5 将于 2026 年 10 月 14 日中午 PDT（19:00 UTC）从使用 ChatGPT 登录的 Codex 中退役。OpenAI API 和使用 API key 认证的 Codex 会话不受影响。

#### Ultrafast 套餐和工作区要求

- 符合条件的企业工作区使用积分制或 USD 用量制协议。用量根据工作区的协议计费。
- 符合条件的教育版套餐使用积分。依赖速率限制而非用量计费的旧版企业套餐不受支持。

其他自助套餐在发布时无法使用 Ultrafast，即使购买了积分。

GPT-6.1 Sol Ultrafast 支持美国和欧洲（EEA + 瑞士）的推理驻留。GPT-6 Astra Ultrafast 仅支持美国的推理驻留。

#### API 计费

使用 API key 时，Codex 改用 API token 定价，ChatGPT 积分倍率不适用。

## 规则

原文存档：[source/rules.md](source/rules.md)

使用规则来控制 Codex 可以在沙箱外运行哪些命令。

规则是实验性的，可能会发生变化。

### 创建规则文件

对于使用 Work Cloud 的本地计算机访问，在 Agent Security 中通过 `rules` TOML 字段配置支持的托管命令规则。这些规则适用于本地执行器；Work Cloud 容器使用现有的 Work Cloud 策略。

这些本地 `.rules` 指令适用于 Codex；不要假设使用 Work Cloud 的本地计算机会读取本地规则文件。参见托管配置和配置参考了解托管 Work 要求。

1. 在活动配置层旁边的 `rules/` 文件夹下创建一个 `.rules` 文件（例如 `~/.codex/rules/default.rules`）。
2. 添加一条规则。此示例在允许 `gh pr view` 在沙箱外运行之前会提示确认。

```python
# Prompt before running commands with the prefix `gh pr view` outside the sandbox.
prefix_rule(
    # The prefix to match.
    pattern = ["gh", "pr", "view"],

    # The action to take when Codex requests to run a matching command.
    decision = "prompt",

    # Optional rationale for why this rule exists.
    justification = "Viewing PRs is allowed with approval",

    # `match` and `not_match` are optional "inline unit tests" where you can
    # provide examples of commands that should (or should not) match this rule.
    match = [
        "gh pr view 7888",
        "gh pr view --repo openai/codex",
        "gh pr view 7888 --json title,body,comments",
    ],
    not_match = [
        # Does not match because the `pattern` must be an exact prefix.
        "gh pr --repo openai/codex view 7888",
    ],
)
```

3. 重启 Codex。

Codex 启动时扫描每个活动配置层下的 `rules/`，包括团队配置位置和 `~/.codex/rules/` 处的用户层。项目本地规则位于 `<repo>/.codex/rules/` 下，仅在项目 `.codex/` 层受信任时加载。

当你在 TUI 中将命令添加到允许列表时，Codex 会写入 `~/.codex/rules/default.rules` 处的用户层，以便未来运行可以跳过提示。

启用 Smart approvals 后（默认），Codex 可能在升级请求期间为你建议一个 `prefix_rule`。在接受之前仔细审查建议的前缀。

管理员还可以从 `requirements.toml` 中强制执行限制性的 `prefix_rule` 条目。

### 理解规则字段

`prefix_rule()` 支持以下字段：

- `pattern` **（必填）**：定义要匹配的命令前缀的非空列表。每个元素可以是：
  - 字面字符串（例如 `"pr"`）。
  - 字面量的并集（例如 `["view", "list"]`），用于在该参数位置匹配多个选项。
- `decision` **（默认为 `"allow"`）**：规则匹配时采取的操作。当多个规则匹配时，Codex 应用最严格的决策（`forbidden` > `prompt` > `allow`）。
  - `allow`：在沙箱外运行命令而不提示。
  - `prompt`：每次匹配调用前提示。
  - `forbidden`：不提示直接阻止请求。
- `justification` **（可选）**：规则的非空、人类可读理由。Codex 可能会在审批提示或拒绝消息中显示它。使用 `forbidden` 时，在 justification 中包含推荐的替代方案（例如 `"Use \`rg\` instead of \`grep\`."`）。
- `match` 和 `not_match` **（默认为 `[]`）**：Codex 加载规则时验证的示例。使用这些在规则生效前捕捉错误。

当 Codex 考虑运行命令时，它将命令的参数列表与 `pattern` 进行比较。在内部，Codex 将命令视为参数列表（就像 `execvp(3)` 接收到的那样）。

### Shell 包装器和复合命令

有些工具将多个 shell 命令包装到单个调用中，例如：

```text
["bash", "-lc", "git add . && rm -rf /"]
```

因为这种命令可以在一个字符串中隐藏多个操作，Codex 对 `bash -lc`、`bash -c` 及其 `zsh` / `sh` 等价物做特殊处理。

#### 当 Codex 可以安全拆分脚本时

如果 shell 脚本是仅由以下内容组成的线性命令链：

- 普通单词（无变量展开、无 `VAR=...`、无 `$FOO`、无 `*` 等）
- 由安全操作符（`&&`、`||`、`;` 或 `|`）连接

那么 Codex 会解析它（使用 tree-sitter）并在应用规则之前将其拆分为单独的命令。

上面的脚本被视为两个独立的命令：

- `["git", "add", "."]`
- `["rm", "-rf", "/"]`

然后 Codex 根据你的规则评估每个命令，最严格的结果胜出。

即使你允许 `pattern=["git", "add"]`，Codex 也不会自动允许 `git add . && rm -rf /`，因为它会单独评估 `rm -rf /`。

这防止了危险命令被混入安全命令中。

#### 当 Codex 不拆分脚本时

如果脚本使用更高级的 shell 功能，例如：

- 重定向（`>`、`>>`、`<`）
- 替换（`$(...)`、反引号包裹的命令）
- 环境变量（`FOO=bar`）
- 通配符模式（`*`、`?`）
- 控制流（`if`、`for`、带赋值的 `&&` 等）

那么 Codex 不会尝试解释或拆分它。

在这些情况下，整个调用被视为：

```text
["bash", "-lc", "<full script>"]
```

你的规则应用于这个**单个**调用。

通过这种处理，你在安全可行时获得逐命令评估的安全性，在不可行时获得保守行为。

### 测试规则文件

使用 `codex execpolicy check` 测试你的规则如何应用于命令：

```shell
codex execpolicy check --pretty \
  --rules ~/.codex/rules/default.rules \
  -- gh pr view 7888 --json title,body,comments
```

该命令输出 JSON，显示最严格的决策和任何匹配的规则，包括来自匹配规则的任何 `justification` 值。使用多个 `--rules` 标志来组合文件，并添加 `--pretty` 来格式化输出。

### 理解规则语言

`.rules` 文件格式使用 `Starlark`。它的语法类似于 Python，但设计为安全运行：规则引擎可以在没有副作用的情况下运行它（例如触碰文件系统）。

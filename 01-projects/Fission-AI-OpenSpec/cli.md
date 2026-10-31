# CLI 参考

OpenSpec CLI (`openspec`) 提供用于项目设置、验证、状态检查和管理终端命令。这些命令补充了在[命令](commands.md)中记录的 AI 斜杠命令（如 `/opsx:propose`）。

## 摘要

| 类别 | 命令 | 目的 |
|----------|----------|---------|
| **设置** | `init`, `update` | 在项目中初始化和更新 OpenSpec |
| **存储（独立 OpenSpec 仓库）** | `store setup`, `store register`, `store unregister`, `store remove`, `store list`, `store doctor` | 管理存储 — 你已注册的独立 OpenSpec 仓库 |
| **健康** | `doctor` | 报告解析后的根目录的健康关系 |
| **工作上下文** | `context` | 组装工作集（根 + 引用的存储） |
| **个人工作集** | `workset create`, `workset list`, `workset open`, `workset remove` | 在你的工具中保持和打开个人、本地工作视图 |
| **浏览** | `list`, `view`, `show` | 探索变更和规格说明 |
| **验证** | `validate` | 检查变更和规格说明中的问题 |
| **生命周期** | `archive` | 完成已完成的变更 |
| **工作流** | `new change`, `status`, `instructions`, `templates`, `schemas` | 产物驱动的工作流支持 |
| **模式** | `schema init`, `schema fork`, `schema validate`, `schema which` | 创建和管理自定义工作流 |
| **配置** | `config` | 查看和修改设置 |
| **工具** | `feedback`, `completion` | 反馈和 shell 集成 |

---

## 人类 vs 代理命令

大多数 CLI 命令设计用于终端中的**人类使用**。某些命令还通过 JSON 输出支持**代理/脚本使用**。

### 仅人类命令

这些命令是交互式的，设计用于终端使用：

| 命令 | 目的 |
|---------|---------|
| `openspec init` | 初始化项目（交互式提示） |
| `openspec view` | 交互式仪表板 |
| `openspec workset open <name>` | 打开已保存的工作集（编辑器窗口或终端代理会话） |
| `openspec config edit` | 在编辑器中打开配置 |
| `openspec feedback` | 通过 GitHub 提交反馈 |
| `openspec completion install` | 安装 shell 补全 |

### 代理兼容命令

这些命令支持 `--json` 输出，供 AI 代理和脚本编程使用：

| 命令 | 人类使用 | 代理使用 |
|---------|-----------|-----------|
| `openspec list` | 浏览变更/规格说明 | `--json` 用于结构化数据 |
| `openspec show <item>` | 读取内容 | `--json` 用于解析 |
| `openspec validate` | 检查问题 | `--all --json` 用于批量验证 |
| `openspec status` | 查看产物进度 | `--json` 用于结构化状态 |
| `openspec instructions` | 获取下一步 | `--json` 用于代理指令 |
| `openspec templates` | 查找模板路径 | `--json` 用于路径解析 |
| `openspec schemas` | 列出可用模式 | `--json` 用于模式发现；`--store <id>` 选择已注册的根目录 |
| `openspec store setup <id>` | 创建并注册本地存储 | `--json` 带有显式输入，用于结构化设置输出 |
| `openspec store register <path>` | 注册现有存储 | `--json` 用于结构化注册输出 |
| `openspec store unregister <id>` | 忘记本地存储注册 | `--json` 用于结构化清理输出 |
| `openspec store remove <id>` | 删除已注册的本地存储文件夹 | `--yes --json` 用于非交互式删除 |
| `openspec store list` | 浏览已注册的存储 | `--json` 用于结构化注册 |
| `openspec store doctor` | 检查本地存储设置 | `--json` 用于结构化诊断 |
| `openspec new change <id>` | 创建仓库本地变更脚手架 | `--json`，加上 `--store <id>` 使用已注册的存储作为 OpenSpec 根目录 |
| `openspec workset create [name]` | 组合个人工作视图 | `--member <path> --json` 用于非交互式组合 |
| `openspec workset list` | 浏览已保存的工作集 | `--json` 用于结构化视图 |
| `openspec workset remove <name>` | 删除已保存的视图 | `--yes --json` 用于非交互式删除 |

---

## 全局选项

这些选项适用于所有命令：

| 选项 | 描述 |
|--------|-------------|
| `--version`, `-V` | 显示版本号 |
| `--no-color` | 禁用彩色输出 |
| `--help`, `-h` | 显示命令帮助 |

---

## 设置命令

### `openspec init`

在你的项目中初始化 OpenSpec。创建文件夹结构并配置 AI 工具集成。

默认行为使用全局配置默认值：配置文件 `core`，交付 `both`，工作流 `propose, explore, apply, update, sync, archive`。

```
openspec init [path] [options]
```

使用 `--language <language>` 向新项目的 `openspec/config.yaml` 添加语言指令。对于现有项目，编辑配置的 `context` 字段，以便 OpenSpec 永远不会覆盖项目特定的指导。

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `path` | 否 | 目标目录（默认：当前目录） |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--tools <list>` | 非交互式配置 AI 工具。使用 `all`、`none` 或逗号分隔的列表 |
| `--language <language>` | 创建新配置时用此语言编写产物 |
| `--force` | 无需提示自动清理旧版文件 |
| `--profile <profile>` | 覆盖此 init 运行的全局配置文件（`core` 或 `custom`） |
| `--no-animation` | 显示静态欢迎屏幕，而不是动画 |
| `--copilot-cloud` | 无需提示设置 GitHub Copilot [云编码代理文件](supported-tools.md#github-copilot-cloud-coding-agent) |
| `--no-copilot-cloud` | 无需提示跳过 GitHub Copilot 云编码代理文件 |

`--profile custom` 使用全局配置中当前选定的工作流（`openspec config profile`）。

当设置 `OPENSPEC_NO_ANIMATION` 环境变量时（任何值，包括空值），当 `NO_COLOR` 设置为非空值时，或当启用操作系统减少运动偏好设置时（macOS 减少运动、GNOME 动画禁用），欢迎动画也会被跳过。

**支持的工具 ID (`--tools`)** — `windsurf` 也接受，作为 `devin` 的别名：`amazon-q`、`antigravity`、`auggie`、`bob`、`claude`、`cline`、`command-code`、`codeartsagent`、`codex`、`devin`、`forgecode`、`codebuddy`、`continue`、`costrict`、`crush`、`cursor`、`factory`、`gemini`、`github-copilot`、`hermes`、`iflow`、`junie`、`kilocode`、`kimi`、`kiro`、`lingma`、`minimax-code`、`vibe`、`oh-my-pi`、`opencode`、`pi`、`codeassistant`、`qoder`、`qwen`、`rovodev`、`roocode`、`trae`、`zed`、`zcode`、`agents`

> 此列表镜像 `src/core/config.ts` 中的 `AI_TOOLS`。请参阅[支持的工具](supported-tools.md)了解每个工具的技能和命令路径。

**示例：**

```bash
# 交互式初始化
openspec init

# 在特定目录中初始化
openspec init ./my-project

# 非交互式：为 Claude 和 Cursor 配置
openspec init --tools claude,cursor

# 非交互式：配置全局 MiniMax Code 技能
openspec init --tools minimax-code

# 为所有支持的工具配置
openspec init --tools all

# 覆盖此运行的配置文件
openspec init --profile core

# 跳过提示并自动清理旧版文件
openspec init --force
```

**它创建了什么：**

```
openspec/
├── specs/              # 你的规格说明（真相的来源）
├── changes/            # 提议的变更
└── config.yaml         # 项目配置

.claude/skills/         # Claude Code 技能（如果选择了 claude）
.cursor/skills/         # Cursor 技能（如果选择了 cursor）
.cursor/commands/       # Cursor OPSX 命令（如果交付包括命令）
.agents/skills/         # AGENTS.md 兼容工具的共享技能（如果选择了 agents）
... (其他工具配置)
```

---

### `openspec update`

升级 CLI 后更新 OpenSpec 指令文件。使用当前全局配置文件、选定的工作流和交付模式重新生成 AI 工具配置文件。

```
openspec update [path] [options]
```

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `path` | 否 | 目标目录（默认：当前目录） |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--force` | 即使文件是最新的，也强制更新 |

**示例：**

```bash
# npm 升级后更新指令文件
npm install -g @fission-ai/openspec@latest
openspec update
```

先升级包。指令文件由已安装的 CLI 生成，因此对旧安装运行 `openspec update` 会报告所有内容都是最新的，而不会添加较新版本发布的工作流。

为了使其可见，`openspec update` 会询问 npm 注册表是否已发布更新的 CLI。当你的版本落后时，它会提供升级：

```text
A newer OpenSpec CLI is available (v1.6.0 → v1.7.0).
  Running from: /usr/local/lib/node_modules/@fission-ai/openspec
? Upgrade to v1.7.0 now? (Y/n)
```

回答 yes 会运行 `npm install -g @fission-ai/openspec@latest`，然后使用新 CLI 重新运行更新，以便新工作流落在同一命令中。它通过询问已安装的二进制文件其版本来确认升级，而不是信任 npm 的退出代码，因此如果你的 `PATH` 上较早的另一个安装仍在应答，它会告诉你，而不是声称成功。回答 no 会打印命令并使用你现有的 CLI 进行更新。Ctrl-C 停止命令。

仅在交互式终端中显示该提示，且仅当 npm 拥有该安装时 — `npm install -g` 实际修复的情况。其他所有情况都会获得与其安装方式匹配的命令：

| OpenSpec 安装方式 | 你得到什么 |
|---------------------------|--------------|
| 全局 npm 安装 | 提示，并在交互式终端中为你运行升级；管道输出会获得打印的命令 |
| 全局 pnpm、bun、yarn 或 volta 安装 | 该管理器自己的命令：`pnpm add -g …@latest`、`bun add -g …@latest`、`yarn global add …@latest` 或 `volta install …@latest` |
| 项目的依赖项 | 更新依赖项的说明，因为其包管理器拥有 lockfile |
| `npx` / `dlx` 缓存 | `npx @fission-ai/openspec@latest update` — 该命令就是更新，所以没有第二步 |
| git 克隆 | 什么也没有 — 你的版本就是分支所说的 |

每当打印任何内容时，它都会命名运行 CLI 加载自的目录 — 当你升级后但旧的 shim 仍然拥有你的 `PATH` 时要检查的内容。

它在 npm 导出时询问 `npm_config_registry` 中的注册表，否则询问 `https://registry.npmjs.org`。不读取 `.npmrc`：让文件内容选择出站请求的去向是一个值得避免的流程，而且项目的 `.npmrc` 随仓库一起传播。在私有镜像上，导出 `npm_config_registry` — 或设置 `OPENSPEC_NO_UPDATE_CHECK` 以完全跳过检查。当 `CI` 设置为任何非显式 off 值（`false`、`0`、`no`、`off` 或空值）、在 `NODE_ENV=test` 下，以及设置 `OPENSPEC_NO_UPDATE_CHECK`（任何值）、`DO_NOT_TRACK=1` 或 `OPENSPEC_TELEMETRY=0` 时，检查被跳过。它在更新之前运行，最多可以延迟 1.5 秒 — 即使网络静默丢包，它也会在此之后放弃，并在注册表不可达时保持安静。

**如何判断"最新"：**技能文件记录生成它们的版本，因此 OpenSpec 将其与已安装的 CLI 进行比较。命令文件没有版本标记，因此对于有命令但没有技能的工具（交付 `commands`），OpenSpec 将文件内容与其现在生成的内容进行比较 — 对这些文件的编辑被视为漂移并被覆盖。使用交付 `skills` 或 `both` 时，仅检查记录的版本，因此版本仍然匹配的手动编辑文件保持不动；使用 `--force` 重写。无论哪种方式，生成的文件都是 OpenSpec 拥有的 — 将你的指令保留在其他地方。

---

## 存储（独立 OpenSpec 仓库）

> **测试版。** 存储和基于它们构建的功能（引用、工作上下文、工作集）是新的；命令名称、标志、文件格式和 JSON 输出可能在版本之间更改形状。有关问题优先的演练，请参阅[存储指南](stores-beta/user-guide.md)。

存储是你已在此计算机上注册的独立 OpenSpec 仓库 — 例如规划仓库或合约仓库。注册存储允许普通命令（`list`、`show`、`status`、`validate`、`new change`、`archive`、...）通过传递 `--store <id>` 从任何地方在其中执行。

### `openspec store setup`

创建并注册本地存储。在终端中没有参数时，OpenSpec 会引导用户完成设置。代理和脚本应传递显式输入并使用 `--json`。

```bash
openspec store setup [id] [options]
```

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--path <path>` | 存储应所在的文件夹（例如 `~/openspec/<id>`） |
| `--remote <url>` | 在新存储的 `store.yaml` 中记录规范的远程地址 |
| `--init-git` | 初始化一个带有初始提交的 Git 仓库（默认） |
| `--no-init-git` | 跳过每个 Git 操作：不初始化，没有初始提交 |
| `--json` | 输出 JSON |

非交互式运行（`--json`、脚本、代理）必须同时传递存储 id 和 `--path`。在交互式终端中，设置会提示输入位置，并在可见的、用户拥有的位置提供可编辑的建议（例如 `~/openspec/<id>`）；它从不默认为 OpenSpec 的管理数据目录。

示例：

```bash
openspec store setup
openspec store setup team-context
openspec store setup team-context --path ~/openspec/team-context --no-init-git
openspec store setup team-context --path ~/openspec/team-context --no-init-git --json
```

### `openspec store register`

注册现有的本地存储文件夹。在存储测试版期间，根目录可以在任何变更存在、规格说明已应用或变更已归档之前注册；在这种情况下，`openspec/changes/`、`openspec/specs/` 和 `openspec/changes/archive/` 可能在正常命令创建它们之前不存在。
声明 `store: <id>` 的仅配置仓库仍然指向另一个存储，除非移除该指针，否则不会注册为存储根目录。

```bash
openspec store register [path] [options]
```

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--id <id>` | 存储 id；默认为存储元数据或文件夹名称 |
| `--yes` | 确认为健康的 OpenSpec 根目录创建存储身份元数据 |
| `--json` | 输出 JSON |

### `openspec store unregister`

忘记本地存储注册而不删除文件。

```bash
openspec store unregister <id> [--json]
```

在存储被移动、克隆到其他地方或不应再由此计算机上的 OpenSpec 显示时使用。

### `openspec store remove`

忘记本地存储注册并删除其本地文件夹。

```bash
openspec store remove <id> [--yes] [--json]
```

`remove` 在交互式终端中删除之前显示确切的文件夹。代理、脚本和 JSON 调用者必须传递 `--yes` 以确认删除。OpenSpec 拒绝删除不包含匹配存储元数据的文件夹。

### `openspec store list`

列出本地注册的存储。

```bash
openspec store list [--json]
openspec store ls [--json]
```

### `openspec store doctor`

检查本地存储注册、元数据和 Git 存在。

```bash
openspec store doctor [id] [--json]
```

Doctor 仅用于诊断；它报告缺失的根目录、元数据不匹配和无效的本地注册表状态，而不修改存储。

### 从项目引用存储

项目仓库可以在其 `openspec/config.yaml` 中声明其工作依赖哪些存储：

```yaml
schema: spec-driven
references:
  - team-context
```

从那时起，`openspec instructions` 在该仓库中的输出（每个产物和 `apply` 表面，JSON 和人类模式）携带每个引用存储的规格说明索引 — 规格说明 id、来自每个规格说明目的部分的一行摘要，以及获取命令（`openspec show <spec-id> --type spec --store <id>`）。索引从每次运行时的注册检出生成；规格说明内容永远不会复制到输出中。

引用是只读上下文。它们永远不会改变命令的作用位置：工作保留在仓库自己的根目录中，写入引用存储仍然是显式的 `--store` 操作。无法解析的引用（例如，此计算机上未注册的存储）在索引中降级为警告，并带有确切的修复方法，指令仍然生成。`openspec doctor` 在一个地方报告引用健康。

### 记录存储克隆自何处

存储可以在其已提交的身份文件中记录其规范的克隆来源，因此入职永远不会在"注册存储"处死胡同：

```bash
openspec store setup team-context --path ~/openspec/team-context \
  --remote git@github.com:acme/team-context.git
```

远程地址落在初始提交内的 `.openspec-store/store.yaml` 中，因此每个克隆天生就知道它。对于现有存储，手动编辑 `store.yaml` 并提交。`store doctor` 显示记录的远程地址（以及检出观察到的 Git 来源）；setup/register 共享指导命名它；register 在本地注册表中记录检出来源。

引用声明也可以携带克隆来源，因此尚未拥有存储的队友会获得一个完整、可粘贴的修复（`git clone <remote> <path> && openspec store register <path> --id <id>`）：

```yaml
references:
  - { id: team-context, remote: "git@github.com:acme/team-context.git" }
```

记录远程不是同步：OpenSpec 永远不会自行克隆、拉取或推送。

### 声明默认存储

规划完全外部化的仓库 — 没有本地 `openspec/specs/` 或 `openspec/changes/` — 可以一次声明其存储，而不是在每个命令上传递 `--store`：

```yaml
# openspec/config.yaml（openspec/ 下的唯一文件）
store: team-context
```

然后普通命令自动解析到声明的存储；根目录横幅和 JSON `root` 块报告 `source: "declared"` 和存储 id，打印的提示仍然携带 `--store <id>`。声明是后备，永远不会覆盖：显式的 `--store` 始终获胜，带有真实规划文件夹的目录会忽略该指针（带有警告）。要将指针仓库转换为本地 OpenSpec 根目录，请移除 `store:` 行并运行 `openspec init` — init 在声明存在时拒绝搭建。

机器级变体一次覆盖每个仓库：`openspec config set defaultStore <id>`（请参阅配置）。仅在 `--store`、本地根目录和项目指针都未能解析后才会查阅；根目录横幅和 JSON `root` 块然后报告 `source: "global_default"`。

## Doctor（关系健康）

一个只读问题，一个地方：OpenSpec 根目录是否健康，它引用的存储是否在此计算机上可用？

```bash
openspec doctor [--store <id>] [--json]
```

报告将根目录健康、存储元数据健康（包括记录远程和检出来源分叉时的说明，以及存储检出落后于其最后获取的上游跟踪引用时的说明）和引用健康（指令显示相同的诊断，以及未解析引用的克隆修复）分开。任何严重程度的健康发现都以 0 退出 — 代理读取 `status` 数组；只有命令失败（无根目录、未知存储）以 1 退出。Doctor 永远不会克隆、同步或修复。要获取组装集本身而不是其健康状况，请使用 `openspec context`。

## 工作上下文（组装集）

与此工作相关的所有内容，通过 OpenSpec 声明，在一个工作集中：OpenSpec 根目录和它引用的存储。

```bash
openspec context [--store <id>] [--json] [--code-workspace <path> [--force]]
```

JSON 简报可供代理使用（每个可用的引用存储携带其获取方法；未解析的成员携带相同的修复指令和 doctor 显示）。`--code-workspace` 另外写入一个 VS Code 工作区文件，包含根目录加上可用的引用存储（`ref:<id>` 文件夹）— 这是此命令执行的唯一写入，如果文件存在，没有 `--force` 则拒绝执行。不可用的成员会被报告，不会猜测。

"工作上下文"是组装集；`openspec/config.yaml` 中的 `context:` 字段是注入指令的项目背景 — 两个不同的东西。`openspec doctor` 回答该集是否健康；`openspec context` 回答该集是什么。

## 个人工作集

> **测试版。** 工作集是新的测试版表面的一部分；命令、标志和文件格式可能在版本之间更改形状。有关演练，请参阅[存储指南](stores-beta/user-guide.md#worksets-reopen-the-folders-you-work-on-together)。

工作集是你个人、命名的一起工作的文件夹视图 — 一个规划根目录加上你选择的任何其他内容 — 保留在你的机器上并按名称在你的工具中重新打开。它纯粹是本地的：永远不会提交，永远不会共享，永远不会从声明中派生，移除一个永远不会接触成员文件夹。

```bash
openspec workset create [name] [--member <path> | --member <name>=<path>]... [--tool <id>] [--json]
openspec workset list [--json]
openspec workset open <name> [--tool <id>]
openspec workset remove <name> [--yes] [--json]
```

`create` 运行一个简短的引导流程（或非交互式地接受 `--member` 标志；第一个成员是主要的 — 会话从那里开始）。`open` 启动选定的工具：编辑器（VS Code、Cursor）打开包含每个成员的窗口并返回；CLI 代理（Claude Code、codex）接管此终端作为会话，附加每个成员，不预填提示，直到退出时结束。打开时缺失的文件夹会被跳过并附带说明；其余的打开。保存的工具偏好可以通过 `--tool` 按打开覆盖。

支持新工具是配置，不是代码。每个工具都是两种启动样式之一 — `workspace-file`（使用生成的 `.code-workspace` 启动）或 `attach-dirs`（每个成员一个附加标志）— 而全局 `config.json` 中的 `openers` 键（使用 `openspec config edit` 打开）按字段添加工具或调整内置工具：

```json
{
  "openers": {
    "zed": { "style": "workspace-file" },
    "claude": { "attach_flag": "--dir" }
  }
}
```

所有工作集状态都位于全局数据目录的 `worksets/` 文件夹下（保存的视图加上生成的 `<name>.code-workspace` 文件，每次打开时重新生成）；删除该文件夹会移除每个痕迹。

---

## 浏览命令

### `openspec list`

列出项目中的变更或规格说明。

```
openspec list [options]
```

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--specs` | 列出规格说明而不是变更 |
| `--changes` | 列出变更（默认） |
| `--sort <order>` | 按 `recent`（默认）或 `name` 排序 |
| `--json` | 输出为 JSON |

**示例：**

```bash
# 列出所有活跃变更
openspec list

# 列出所有规格说明
openspec list --specs

# 脚本 JSON 输出
openspec list --json
```

**输出（文本）：**

```
Changes:
  add-dark-mode     No tasks      just now
```

---

### `openspec view`

显示用于探索规格说明和变更的交互式仪表板。

```
openspec view
```

打开基于终端的界面，用于浏览项目的规格说明和变更。

---

### `openspec show`

显示变更或规格说明的详细信息。

```
openspec show [item-name] [options]
```

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `item-name` | 否 | 变更或规格说明的名称（如果省略则提示） |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--type <type>` | 指定类型：`change` 或 `spec`（如果不明确则自动检测） |
| `--json` | 输出为 JSON |
| `--no-interactive` | 禁用提示 |

**变更特定选项：**

| 选项 | 描述 |
|--------|-------------|
| `--deltas-only` | 仅显示差异规格说明（JSON 模式） |

**规格说明特定选项：**

| 选项 | 描述 |
|--------|-------------|
| `--requirements` | 仅显示需求，排除场景（JSON 模式） |
| `--no-scenarios` | 排除场景内容（JSON 模式） |
| `-r, --requirement <id>` | 按基于 1 的索引显示特定需求（JSON 模式） |

**示例：**

```bash
# 交互式选择
openspec show

# 显示特定变更
openspec show add-dark-mode

# 显示特定规格说明
openspec show auth --type spec

# 用于解析的 JSON 输出
openspec show add-dark-mode --json
```

---

## 验证命令

### `openspec validate`

验证变更和规格说明的结构问题，并检查变更的修改需求与它们将替换的主规格说明。

```
openspec validate [item-name] [options]
```

除非其 `.openspec.yaml` 声明 `skip_specs: true`（对于纯重构、工具或文档工作 — 请参阅[配方 5](examples.md#recipe-5-a-refactor-with-no-behavior-change)），否则具有零规格差异的变更验证失败。

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `item-name` | 否 | 要验证的特定项目（如果省略则提示） |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--all` | 验证所有变更和规格说明 |
| `--changes` | 验证所有变更 |
| `--specs` | 验证所有规格说明 |
| `--archived` | 验证归档的变更是否所有任务都已完成（用于预提交 lint） |
| `--type <type>` | 当名称不明确时指定类型：`change` 或 `spec` |
| `--strict` | 启用严格验证模式 |
| `--json` | 输出为 JSON |
| `--concurrency <n>` | 最大并行验证数（默认：6，或 `OPENSPEC_CONCURRENCY` 环境变量） |
| `--no-interactive` | 禁用提示 |

`--archived` 是它自己的范围：它不验证规格差异（在归档时已经应用），它验证 `changes/archive/` 下的每个变更的所有 `tasks.md` 复选框是否都已勾选，如果任何未勾选则以非零退出。这捕捉了归档时未完成工作的变更 — 在预提交钩子中很方便。

**示例：**

```bash
# 交互式验证
openspec validate

# 验证特定变更
openspec validate add-dark-mode

# 验证所有变更
openspec validate --changes

# 使用 JSON 输出验证所有内容（用于 CI/脚本）
openspec validate --all --json

# 增加并行性的严格验证
openspec validate --all --strict --concurrency 12

# 如果任何归档变更仍有未勾选的任务，则失败
openspec validate --archived
```

**输出（文本）：**

```
Validating add-dark-mode...
  ✓ proposal.md valid
  ✓ specs/ui/spec.md valid
  ⚠ design.md: missing "Technical Approach" section

1 warning found
```

**输出（JSON）：**

```json
{
  "version": "1.0.0",
  "results": {
    "changes": [
      {
        "name": "add-dark-mode",
        "valid": true,
        "warnings": ["design.md: missing 'Technical Approach' section"]
      }
    ]
  },
  "summary": {
    "total": 1,
    "valid": 1,
    "invalid": 0
  }
}
```

---

## 生命周期命令

### `openspec archive`

归档已完成的变更并将差异规格说明合并到主规格说明中。

```
openspec archive [change-name] [options]
```

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-name` | 否 | 要归档的变更（如果省略则提示；当没有任何东西可以回答提示时为必需） |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `-y, --yes` | 跳过确认提示。当没有任何东西可以回答它们时 — AI 代理、CI 作业或任何关闭 stdin 的运行时为必需 |
| `--skip-specs` | 跳过一次归档运行的规格更新。永久没有规格差异的变更应在其 `.openspec.yaml` 中声明 `skip_specs: true` — 它无需标志即可归档 |
| `--no-validate` | 跳过验证（需要确认）。同时禁用能力退役 — 没有验证器裁决，没有任何东西被退役 |

**示例：**

```bash
# 交互式归档（询问哪个变更，然后确认）
openspec archive

# 归档特定变更
openspec archive add-dark-mode

# 无提示归档（代理、CI、脚本）
openspec archive add-dark-mode --yes

# 归档不影响规格的工具变更
openspec archive update-ci-config --skip-specs
```

**退役能力：**将退役标记添加到变更元数据：

```yaml
# openspec/changes/retire-legacy/.openspec.yaml
schema: spec-driven
retire_capabilities: true
```

然后正常归档变更：

```bash
openspec archive retire-legacy --yes
```

当变更移除能力的最后一个需求时，OpenSpec 删除其活动的 `spec.md`。同一变更中的其他能力差异仍然会更新它们的主规格说明。没有标记，归档会在更改任何文件之前停止并告诉你添加它。

**它做什么：**

1. 验证变更（除非 `--no-validate`）
2. 提示确认（除非 `--yes`）
3. 在更改任何主规格说明之前声明归档目的地
4. 验证并将活动的差异规格说明合并到 `openspec/specs/` 中 — 变更移除其最后一个需求的能力会被退役，其规格文件会被删除，但仅当变更的 `.openspec.yaml` 在其 `schema:` 旁边声明 `retire_capabilities: true` 时
5. 将变更文件夹移动到 `openspec/changes/archive/YYYY-MM-DD-<name>/`
6. 如果在完成归档之前规格突变或最终移动失败，恢复规格说明并将变更保留或返回到其活动路径
7. 如果已验证的后备副本完成但暂存源清理失败，则保留完整的归档和提交的规格状态以供恢复

**没有终端时：**AI 代理、CI 作业或任何关闭 stdin 的运行时无法回答步骤 2，因此归档会在接触任何东西之前停止，以 1 退出，并命名要重跑的命令 — `openspec archive <name> --yes`，携带你传递的任何其他标志。预先传递 `--yes`（和变更名称）以跳过往返。

---

## 工作流命令

这些命令支持产物驱动的 OPSX 工作流。它们对人类检查进度和代理确定下一步都很有用。

### `openspec new change`

在解析的 OpenSpec 根目录中创建变更目录和可选的签入元数据。

```bash
openspec new change <name> [options]
```

变更名称必须使用小写短横线命名：小写字母、数字和单个短横线。它们不能包含空格、下划线、大写字母、连续短横线或前导/尾随短横线。允许前导数字，因此你可以为排序或分层变更添加前缀，例如 `100-add-feature` 或 `00001-add-auth`。

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--description <text>` | 要添加到 `README.md` 的描述 |
| `--goal <text>` | 可选的目标元数据，与变更一起存储 |
| `--schema <name>` | 要使用的工作流模式 |
| `--store <id>` | 要用作 OpenSpec 根目录的存储 id（存储是你已注册的独立 OpenSpec 仓库） |
| `--json` | 输出 JSON |

示例：

```bash
openspec new change add-billing-api
openspec new change add-billing-api --store team-context --json
```

### `openspec status`

显示变更的产物完成状态。

```
openspec status [options]
```

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--change <id>` | 变更名称（如果省略则提示） |
| `--schema <name>` | 模式覆盖（从变更的配置自动检测） |
| `--json` | 输出为 JSON |

**示例：**

```bash
# 交互式状态检查
openspec status

# 特定变更的状态
openspec status --change add-dark-mode

# 代理使用的 JSON
openspec status --change add-dark-mode --json
```

**输出（文本）：**

```
Change: add-dark-mode
Schema: spec-driven
Progress: 2/4 artifacts complete

[x] proposal
[x] specs
[ ] design
[-] tasks (blocked by: design)
```

声明 `skip_specs: true` 的变更显示其 specs 阶段为 `[~] specs (skipped: change declares skip_specs)` 并将其从进度计数中排除。

**输出（JSON）：**

```json
{
  "changeName": "add-dark-mode",
  "schemaName": "spec-driven",
  "isPlanningComplete": false,
  "isComplete": false,
  "applyRequires": ["tasks"],
  "artifacts": [
    {"id": "proposal", "outputPath": "proposal.md", "status": "done", "requires": []},
    {"id": "specs", "outputPath": "specs/**/*.md", "status": "done", "requires": ["proposal"]},
    {"id": "design", "outputPath": "design.md", "status": "ready", "requires": ["proposal"]},
    {"id": "tasks", "outputPath": "tasks.md", "status": "blocked", "requires": ["specs", "design"], "missingDeps": ["design"]}
  ]
}
```

`isPlanningComplete` 报告每个未跳过的规划产物是否存在；跳过的产物在未创建的情况下计为已满足。它不报告实现任务是否完成。`isComplete` 保留为具有相同值的兼容性别名。

产物按依赖顺序列出 — 依赖项永远不会出现在需要它的东西之后 — 并且同时变得准备好的产物（spec-driven 的 `specs` 和 `design` 都只需要 `proposal`）保持模式声明它们的顺序，而不是字母顺序。因此第一个 `ready` 条目是要写入的下一个产物。

---

### `openspec instructions`

获取创建产物或应用任务的丰富指令。由 AI 代理使用以了解接下来要创建什么。

```
openspec instructions [artifact] [options]
```

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `artifact` | 否 | 产物 ID，或工作流输入表面：`apply` 或 `archive` |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--change <id>` | 变更名称（非交互式模式下必需） |
| `--schema <name>` | 模式覆盖 |
| `--json` | 输出为 JSON |

**特殊情况：**使用 `apply` 获取任务实现指令。使用 `archive` 获取有效变更的当前只读归档输入（`context` 和 `operationGuidance`）；它不归档或突变任何东西。

**示例：**

```bash
# 获取下一个产物的指令
openspec instructions --change add-dark-mode

# 获取特定产物指令
openspec instructions design --change add-dark-mode

# 获取 apply/实现指令
openspec instructions apply --change add-dark-mode

# 不归档获取当前归档操作输入
openspec instructions archive --change add-dark-mode --json

# 代理使用的 JSON
openspec instructions design --change add-dark-mode --json
```

**输出包括：**

- 产物的模板内容
- 来自配置的项目上下文
- 来自依赖产物的内容
- 来自配置的每个产物规则
- `apply`/`archive` 的当前项目上下文和匹配的操作指导

操作输入从每次调用时的解析仓库或选定存储中读取。项目上下文是必需的提示级输入：代理读取它并应用相关的项目事实、约定和约束。操作指导是可选的附加建议：代理考虑每个条目并仅遵循适用于内置工作流且兼容的条目。两个字段都保持与显式用户选择、CLI 控制状态、内置指令和产物规则分开。冲突的上下文会被报告；冲突或不适当的指导不会被遵循，并解释原因。这些是生成代理的行为契约，不是可执行的 CLI 检查。`instructions archive` 仅返回选定的变更、可选输入和根元数据；它不包括静态归档工作流。

对于通过 `skip_specs: true` 跳过的产物，输出仅为警告（JSON 添加 `skipped`/`warning` 字段）— 产物不得创建。

---

### `openspec templates`

显示模式中所有产物的解析模板路径。

```
openspec templates [options]
```

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--schema <name>` | 要检查的模式（默认：`spec-driven`） |
| `--json` | 输出为 JSON |

**示例：**

```bash
# 显示默认模式的模板路径
openspec templates

# 显示自定义模式的模板
openspec templates --schema my-workflow

# 编程使用的 JSON
openspec templates --json
```

**输出（文本）：**

```
Schema: spec-driven

Templates:
  proposal  → ~/.openspec/schemas/spec-driven/templates/proposal.md
  specs     → ~/.openspec/schemas/spec-driven/templates/specs.md
  design    → ~/.openspec/schemas/spec-driven/templates/design.md
  tasks     → ~/.openspec/schemas/spec-driven/templates/tasks.md
```

---

### `openspec schemas`

列出可用的工作流模式及其描述和产物流。

```
openspec schemas [options]
```

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--json` | 输出为 JSON |
| `--store <id>` | 使用已注册的存储作为 OpenSpec 根目录 |

**示例：**

```bash
openspec schemas
```

**输出：**

```
Available schemas:

  spec-driven (package)
    The default spec-driven development workflow
    Flow: proposal → specs → design → tasks

  my-custom (project)
    Custom workflow for this project
    Flow: research → proposal → tasks
```

---

## 模式命令

用于创建和管理自定义工作流模式的命令。

### `openspec schema init`

创建新的项目本地模式。

```
openspec schema init <name> [options]
```

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `name` | 是 | 模式名称（短横线命名） |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--description <text>` | 模式描述 |
| `--artifacts <list>` | 逗号分隔的产物 ID（默认：`proposal,specs,design,tasks`） |
| `--default` | 设置为项目默认模式 |
| `--no-default` | 不提示设置为默认 |
| `--force` | 覆盖现有模式 |
| `--json` | 输出为 JSON |

**示例：**

```bash
# 交互式模式创建
openspec schema init research-first

# 非交互式特定产物
openspec schema init rapid \
  --description "Rapid iteration workflow" \
  --artifacts "proposal,tasks" \
  --default
```

**它创建了什么：**

```
openspec/schemas/<name>/
├── schema.yaml           # 模式定义
└── templates/
    ├── proposal.md       # 每个产物的模板
    ├── specs.md
    ├── design.md
    └── tasks.md
```

---

### `openspec schema fork`

将现有模式复制到你的项目中进行自定义。

```
openspec schema fork <source> [name] [options]
```

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `source` | 是 | 要复制的模式 |
| `name` | 否 | 新模式名称（默认：`<source>-custom`） |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--force` | 覆盖现有目标 |
| `--json` | 输出为 JSON |

**示例：**

```bash
# 分叉内置的 spec-driven 模式
openspec schema fork spec-driven my-workflow
```

---

### `openspec schema validate`

验证模式的结构和模板。

```
openspec schema validate [name] [options]
```

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `name` | 否 | 要验证的模式（如果省略则验证所有） |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--verbose` | 显示详细的验证步骤 |
| `--json` | 输出为 JSON |

**示例：**

```bash
# 验证特定模式
openspec schema validate my-workflow

# 验证所有模式
openspec schema validate
```

---

### `openspec schema which`

显示模式解析自何处（用于调试优先级）。

```
openspec schema which [name] [options]
```

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `name` | 否 | 模式名称 |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--all` | 列出所有模式及其来源 |
| `--json` | 输出为 JSON |

**示例：**

```bash
# 检查模式来自哪里
openspec schema which spec-driven
```

**输出：**

```
spec-driven resolves from: package
  Source: /usr/local/lib/node_modules/@fission-ai/openspec/schemas/spec-driven
```

**模式优先级：**

1. 项目：`openspec/schemas/<name>/`
2. 用户：`~/.local/share/openspec/schemas/<name>/`
3. 包：内置模式

---

## 配置命令

### `openspec config`

查看和修改全局 OpenSpec 配置。

```
openspec config <subcommand> [options]
```

**子命令：**

| 子命令 | 描述 |
|------------|-------------|
| `path` | 显示配置文件位置 |
| `list` | 显示所有当前设置 |
| `get <key>` | 获取特定值 |
| `set <key> <value>` | 设置值 |
| `unset <key>` | 移除键 |
| `reset` | 重置为默认值 |
| `edit` | 在 `$EDITOR` 中打开 |
| `profile [preset]` | 交互式或通过预设配置工作流配置文件 |

**示例：**

```bash
# 显示配置文件路径
openspec config path

# 列出所有设置
openspec config list

# 获取特定值
openspec config get telemetry.enabled

# 设置值（禁用匿名使用遥测）
openspec config set telemetry.enabled false

# 显式设置字符串值
openspec config set user.name "My Name" --string

# 移除自定义设置
openspec config unset user.name

# 设置机器级默认存储（当没有 --store、
# 本地根目录或项目存储：指针解析时的后备根目录）
openspec config set defaultStore team-plans

# 重置所有配置
openspec config reset --all --yes

# 在编辑器中编辑配置
openspec config edit

# 使用基于操作的向导配置配置文件
openspec config profile

# 快速预设：将工作流切换到 core（保持交付模式）
openspec config profile core
```

**遥测退出：**`telemetry.enabled` 在未设置时默认为开启（退出模式）。设置为 `false` 以禁用匿名使用统计和 `openspec update` 版本检查。环境变量优先于配置：`OPENSPEC_TELEMETRY=0`、`DO_NOT_TRACK=1`，以及真实的 `CI` 值（例如 `true`/`1`/`yes`）始终禁用遥测，无论配置值如何。

`openspec config profile` 从当前状态摘要开始，然后让你选择：
- 更改交付 + 工作流
- 仅更改交付
- 仅更改工作流
- 保持当前设置（退出）

如果保持当前设置，则不会写入任何更改，也不会显示更新提示。如果没有配置更改，但当前项目文件与全局配置文件/交付不同步，OpenSpec 将显示警告并建议 `openspec update`。
按 `Ctrl+C` 也会干净地取消流程（没有堆栈跟踪）并以代码 `130` 退出。
在工作流清单中，`[x]` 表示该工作流已在全局配置中选择。要将这些选择应用到项目文件，请运行 `openspec update`（或在项目内提示时选择 `Apply changes to this project now?`）。

**交互式示例：**

```bash
# 仅交付更新
openspec config profile
# 选择：仅更改交付
# 选择交付：仅技能

# 仅工作流更新
openspec config profile
# 选择：仅更改工作流
# 在清单中切换工作流，然后确认
```

---

## 工具命令

### `openspec feedback`

提交关于 OpenSpec 的反馈。创建一个 GitHub issue。

```
openspec feedback <message> [options]
```

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `message` | 是 | 反馈摘要；长文本在 issue 标题中缩短并保留在正文中 |

**选项：**

| 选项 | 描述 |
|--------|-------------|
| `--body <text>` | 摘要之后包含的其他详细信息 |

**要求：**必须安装并验证 GitHub CLI (`gh`)。

**示例：**

```bash
openspec feedback "Add support for custom artifact types" \
  --body "I'd like to define my own artifact types beyond the built-in ones."
```

---

### `openspec completion`

管理 OpenSpec CLI 的 shell 补全。

```
openspec completion <subcommand> [shell]
```

**子命令：**

| 子命令 | 描述 |
|------------|-------------|
| `generate [shell]` | 将补全脚本输出到 stdout |
| `install [shell]` | 为你的 shell 安装补全 |
| `uninstall [shell]` | 移除已安装的补全 |

**支持的 shell：**`bash`、`zsh`、`fish`、`powershell`

**示例：**

```bash
# 安装补全（自动检测 shell）
openspec completion install

# 为特定 shell 安装
openspec completion install zsh

# 为手动安装生成脚本（bash）
openspec completion generate bash > ~/.bash_completion.d/openspec

# 卸载
openspec completion uninstall
```

**Windows (PowerShell)：**为当前 PowerShell 主机安装补全：

```powershell
$env:PROFILE = $PROFILE
openspec completion install powershell
. $PROFILE
```

`$env:PROFILE` 告诉 OpenSpec 要在此会话中配置哪个配置文件。安装程序创建缺失的配置文件目录并添加加载 `OpenSpecCompletion.ps1` 的管理块。重新加载配置文件会立即启用补全。

要从当前主机卸载，请运行：

```powershell
$env:PROFILE = $PROFILE
openspec completion uninstall powershell
```

卸载后重启 PowerShell 以清除当前会话中的补全。

补全是可选加入的。CLI 在交互式终端中第一次运行命令时在 stderr 上提及一次，之后不再提及 — 如果你已经安装了补全，它也会保持安静。设置 `OPENSPEC_NO_COMPLETIONS=1` 以完全抑制该提示。

---

## 退出代码

| 代码 | 含义 |
|------|---------|
| `0` | 成功 |
| `1` | 错误（验证失败、缺失文件等） |

---

## 环境变量

| 变量 | 描述 |
|----------|-------------|
| `OPENSPEC_TELEMETRY` | 设置为 `0` 以禁用遥测和 `openspec update` 版本检查（覆盖全局配置中的 `telemetry.enabled`） |
| `DO_NOT_TRACK` | 设置为 `1` 以禁用遥测和 `openspec update` 版本检查（标准 DNT 信号；覆盖配置） |
| `OPENSPEC_CONCURRENCY` | 批量验证的默认并发数（默认：6） |
| `EDITOR` 或 `VISUAL` | `openspec config edit` 的编辑器 |
| `NO_COLOR` | 设置时禁用彩色输出 |
| `OPENSPEC_NO_ANIMATION` | 设置时禁用 `openspec init` 欢迎动画 |
| `OPENSPEC_NO_COMPLETIONS` | 设置为 `1` 以抑制关于 shell 补全的一次性提示 |
| `OPENSPEC_NO_UPDATE_CHECK` | 设置时禁用 `openspec update` 检查更新的已发布 CLI（任何值，包括空值）。当设置 `CI` 时也会跳过（除非 `false`/`0`/`no`/`off`）或 `NODE_ENV=test` |
| `npm_config_registry` | `openspec update` 版本检查询问的注册表。必须是 `http(s)` URL，否则回退到 `https://registry.npmjs.org`。不读取 `.npmrc` 文件 |

---

## 相关文档

- [命令](commands.md) — AI 斜杠命令（`/opsx:propose`、`/opsx:apply` 等）
- [工作流](workflows.md) — 常见模式以及何时使用每个命令
- [自定义](customization.md) — 创建自定义模式和模板
- [开始使用](getting-started.md) — 首次设置指南

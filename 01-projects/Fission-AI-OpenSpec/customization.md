# 自定义配置

OpenSpec 提供三个级别的自定义：

| 级别 | 作用 | 适用场景 |
|-------|--------------|----------|
| **项目配置** | 设置默认值，注入上下文/规则 | 大多数团队 |
| **自定义模式** | 定义你自己的工作流产物 | 拥有独特流程的团队 |
| **全局覆盖** | 在所有项目中共享模式 | 高级用户 |

---

## 项目配置

`openspec/config.yaml` 文件是为你的团队自定义 OpenSpec 最简单的方式。它可以让你：

- **设置默认模式** — 每条命令都不需要 `--schema`
- **注入项目上下文** — AI 能看到你的技术栈、约定等
- **添加每个产物的规则** — 特定产物的自定义规则
- **添加每个操作的指导** — 针对 apply 和 archive 操作的建议偏好
- **记住集成选择** — 例如 [GitHub Copilot 云端编码代理](supported-tools.md#github-copilot-cloud-coding-agent) 的 opt-in

### 快速设置

```bash
openspec init
```

这会交互式地引导你创建配置。或者手动创建一个：

```yaml
# openspec/config.yaml
schema: spec-driven

context: |
  技术栈: TypeScript, React, Node.js, PostgreSQL
  API 风格: RESTful, 文档在 docs/api.md
  测试: Jest + React Testing Library
  所有公共 API 都必须保持向后兼容

rules:
  proposal:
    - 包含回滚计划
    - 确定受影响的团队
  specs:
    - 使用 Given/When/Then 格式
    - 优先引用现有模式，不要重复发明

operations:
  apply:
    guidance:
      - 先运行聚焦测试，再运行完整测试套件
  archive:
    guidance:
      - 保持完成摘要简洁

# 由 `openspec init` 在你选择（或拒绝）GitHub Copilot
# 云端编码代理时设置；控制 `init`/`update` 是否生成其文件
githubCopilot:
  cloudAgent: false
```

### 工作原理

**默认模式：**

```bash
# 没有配置时
openspec new change my-feature --schema spec-driven

# 有配置时 — 模式自动生效
openspec new change my-feature
```

**上下文和规则注入：**

当生成任何产物时，你的上下文和规则会被注入到 AI 提示中：

```xml
<context>
技术栈: TypeScript, React, Node.js, PostgreSQL
...
</context>

<rules>
- 包含回滚计划
- 确定受影响的团队
</rules>

<template>
[模式的内置模板]
</template>
```

- **上下文** 出现在所有产物中
- **规则** 只出现在匹配的产物中

**操作指导：**

`operations.apply.guidance` 和 `operations.archive.guidance` 是可选的建议指令数组，用于指导代理如何执行这些操作。它们与 `rules` 是分开的：操作指导不限制产物内容，而产物规则也不会被重新标记为操作指导。

Apply 和 archive 在运行时获取这些输入：

```bash
openspec instructions apply --change my-feature --json
openspec instructions archive --change my-feature --json
```

两者都会返回当前项目的 `context` 和匹配的 `operationGuidance`，作为单独的可选字段。每次调用都会从解析的根目录读取最新快照。当选择 `--store <id>` 时，变更、上下文和指导都来自该存储，而不是当前仓库。

archive 指令命令是只读的：它不会检查或合并差异规格说明，不会写入主规格说明，不会移动变更，也不会运行静态 archive 工作流。

项目上下文是必需的提示级输入。生成的工作流会读取它，并应用相关的项目事实、约定和约束。操作指导是可选的附加建议：工作流会考虑每条条目，并遵循那些适用且与内置工作流兼容的条目。

两个字段都保持独立于 CLI 控制的状态、解析的路径、内置步骤、显式用户选择和产物规则。工作流会报告上下文冲突，同时保留控制值。它不会遵循不适用或冲突的指导，并会解释原因。两个字段都不是可强制执行的检查，工作流不会将它们的文本复制到实现文件、规格说明、变更产物或摘要中，除非用户单独请求该内容。

**Archive 和 spec-sync 输入安全：**

Archive、bulk archive 和独立的 sync 使用 `openspec status --json` 中的 `artifactPaths.specs.existingOutputPaths` 作为唯一的 delta-spec 来源。没有 `specs` 产物的模式，或者具体输出列表为空的变更，没有可同步的内容；其他产物不会用于推断 delta specs。

在语义合并写入主规格说明之前，工作流会消费当前 `openspec instructions specs --change <name> --json` 的输出。返回的 `specs` 规则仅约束该合并产生的主规格说明。单次 archive 将该快照传递给内联 sync，独立 sync 直接获取它，bulk archive 在第一次写入规格说明之前获取所有必需的快照。非零或无效的 JSON archive/specs 指令响应是查找失败，而不是空输入：工作流会在受影响的写入或变更移动之前停止（对于 bulk archive，在任何批处理写入或移动之前）。

此配置不会更改 archive 执行阶段、用户提示、文件系统操作、语义合并所有权、直接的 `openspec archive` 命令，或产物 `rules` 的结构和输出。

### 模式解析顺序

当 OpenSpec 需要模式时，它会按以下顺序检查：

1. CLI 标志：`--schema <name>`
2. 变更元数据（变更文件夹中的 `.openspec.yaml`）
3. 项目配置（`openspec/config.yaml`）
4. 默认值（`spec-driven`）

---

## 自定义模式

当项目配置不够用时，你可以创建自己的模式，拥有完全自定义的工作流。自定义模式存放在项目的 `openspec/schemas/` 目录中，并与你的代码一起版本控制。

```text
your-project/
├── openspec/
│   ├── config.yaml        # 项目配置
│   ├── schemas/           # 自定义模式存放处
│   │   └── my-workflow/
│   │       ├── schema.yaml
│   │       └── templates/
│   └── changes/           # 你的变更
└── src/
```

### 复刻现有模式

最快的自定义方式是复刻一个内置模式：

```bash
openspec schema fork spec-driven my-workflow
```

这会将整个 `spec-driven` 模式复制到 `openspec/schemas/my-workflow/`，你可以在那里自由编辑。

**你会得到：**

```text
openspec/schemas/my-workflow/
├── schema.yaml           # 工作流定义
└── templates/
    ├── proposal.md       # proposal 产物模板
    ├── spec.md           # specs 模板
    ├── design.md         # design 模板
    └── tasks.md          # tasks 模板
```

现在编辑 `schema.yaml` 来改变工作流，或编辑模板来改变 AI 生成的内容。

### 从头创建模式

对于完全全新的工作流：

```bash
# 交互式
openspec schema init research-first

# 非交互式
openspec schema init rapid \
  --description "快速迭代工作流" \
  --artifacts "proposal,tasks" \
  --default
```

### 模式结构

模式定义了工作流中的产物及其依赖关系：

```yaml
# openspec/schemas/my-workflow/schema.yaml
name: my-workflow
version: 1
description: 我团队的自定义工作流

artifacts:
  - id: proposal
    generates: proposal.md
    description: 初始提案文档
    template: proposal.md
    instruction: |
      创建一个解释为什么需要这个变更的提案。
      聚焦问题，而非解决方案。
    requires: []

  - id: design
    generates: design.md
    description: 技术设计
    template: design.md
    instruction: |
      创建一份解释如何实现的技术设计文档。
    requires:
      - proposal    # 必须先有 proposal 才能创建 design

  - id: tasks
    generates: tasks.md
    description: 实现检查清单
    template: tasks.md
    requires:
      - design

apply:
  requires: [tasks]
  tracks: tasks.md
```

**关键字段：**

| 字段 | 用途 |
|-------|---------|
| `id` | 唯一标识符，用于命令和规则 |
| `generates` | 输出文件名（支持 `specs/**/*.md` 等 glob 模式） |
| `template` | `templates/` 目录中的模板文件 |
| `instruction` | 创建该产物时的 AI 指令 |
| `requires` | 依赖关系 — 哪些产物必须先存在 |

按你希望写入的顺序列出产物。`requires` 决定什么可以创建；`artifacts:` 列表的顺序决定当多个产物同时就绪时，哪个先创建。

### 模板

模板是指导 AI 的 Markdown 文件。在创建产物时，它们会被注入到提示中。

```markdown
<!-- templates/proposal.md -->
## Why

<!-- 解释此变更的动机。它解决了什么问题？ -->

## What Changes

<!-- 描述将要发生什么变化。对新能力或修改要具体。 -->

## Impact

<!-- 受影响的代码、API、依赖项、系统 -->
```

模板可以包含：
- AI 应填写的章节标题
- 给 AI 的 HTML 注释指导
- 展示预期结构的示例格式

### 验证你的模式

在使用自定义模式之前，先验证它：

```bash
openspec schema validate my-workflow
```

这会检查：
- `schema.yaml` 语法正确
- 所有引用的模板都存在
- 没有循环依赖
- 产物 ID 有效

### 使用你的自定义模式

创建完成后，使用方式如下：

```bash
# 在命令中指定
openspec new change feature --schema my-workflow

# 或在 config.yaml 中设为默认
schema: my-workflow
```

### 调试模式解析

不确定使用的是哪个模式？检查一下：

```bash
# 查看特定模式从哪解析
openspec schema which my-workflow

# 列出所有可用模式
openspec schema which --all
```

输出显示它来自你的项目、用户目录还是软件包：

```text
Schema: my-workflow
Source: project
Path: /path/to/project/openspec/schemas/my-workflow
```

---

> **注意：** OpenSpec 也支持用户级别的模式，存放在 `~/.local/share/openspec/schemas/`，用于跨项目共享，但推荐使用项目级模式，因为它们与代码一起版本控制。

---

## 示例

### 快速迭代工作流

最小化的快速迭代工作流：

```yaml
# openspec/schemas/rapid/schema.yaml
name: rapid
version: 1
description: 最小开销的快速迭代

artifacts:
  - id: proposal
    generates: proposal.md
    description: 快速提案
    template: proposal.md
    instruction: |
      为此变更创建一个简短的提案。
      聚焦是什么和为什么，跳过详细规格说明。
    requires: []

  - id: tasks
    generates: tasks.md
    description: 实现检查清单
    template: tasks.md
    requires: [proposal]

apply:
  requires: [tasks]
  tracks: tasks.md
```

### 添加审查产物

复刻默认模式并添加审查步骤：

```bash
openspec schema fork spec-driven with-review
```

然后编辑 `schema.yaml` 添加：

```yaml
  - id: review
    generates: review.md
    description: 实现前审查检查清单
    template: review.md
    instruction: |
      基于设计创建审查检查清单。
      包含安全性、性能和测试考量。
    requires:
      - design

  - id: tasks
    # ... 现有 tasks 配置 ...
    requires:
      - specs
      - design
      - review    # 现在 tasks 也需要 review
```

---

## 社区模式

OpenSpec 也支持通过独立仓库分发的社区维护模式。这些提供了将 OpenSpec 与其他工具或系统集成的有见地的工作流，类似于 [github/spec-kit 的社区扩展目录](https://github.com/github/spec-kit/tree/main/extensions) 对 spec-kit 的做法。

社区模式不会被打包到 OpenSpec 核心中 — 它们有自己的仓库和发布节奏。要使用，将模式包复制到你项目的 `openspec/schemas/<schema-name>/` 目录中（每个仓库的 README 都有安装说明）。

| 模式 | 维护者 | 仓库 | 描述 |
|--------|-----------|-----------|-------------|
| `intent-driven` | @harikrishnan83 | [intent-driven-dev/openspec-schemas](https://github.com/intent-driven-dev/openspec-schemas/tree/main/openspec/schemas/intent-driven) | 在实施前捕获变更意图、可观察行为、技术设计和持久的架构决策。添加变更本地的 ADR 审查清单，并将符合资格的长期决策写为不可变的、可替代的 ADR。 |
| `superpowers-bridge` | @JiangWay | [JiangWay/openspec-schemas](https://github.com/JiangWay/openspec-schemas/tree/main/superpowers-bridge) | 将 OpenSpec 的产物治理与 [obra/superpowers](https://github.com/obra/superpowers) 执行技能（头脑风暴、编写计划、通过子代理进行 TDD、代码审查、收尾）集成。添加了一个以证据为先的 `retrospective` 产物，填补了 Superpowers 原生不覆盖的空白。 |
| `nanopm` | @nmrtn | [nmrtn/nanopm](https://github.com/nmrtn/nanopm/tree/main/openspec-schema) | PM 优先工作流。在实施之前运行 [nanopm](https://github.com/nmrtn/nanopm) 的规划管道（审计 → 策略 → 路线图 → PRD）。将产品规划桥接到 OpenSpec 的 spec-driven 工程工作流。产物从 `.nanopm/` 读取（如果存在）— proposal 从审计获取，design 从策略获取，tasks 从 PRD 分解获取。 |
| `e2e-runbooks` | @Lukk17 | [Lukk17/openspec-schemas](https://github.com/Lukk17/openspec-schemas/tree/master/openspec/schemas/e2e-runbooks) | 能力级端到端测试运行手册。每个能力都有一个不可变的规格说明、一个不可变的任务模板，以及每次执行一个带时间戳的运行记录。断言仅限可观察行为（HTTP 状态、响应体、持久化状态 — 绝不包括日志子串）；每次运行记录开始/结束 UTC 时间、持续时间和最佳估计的 LLM token 消耗。 |
| `anvil` | @jikkujoyce | [jikkujoyce/openspec-schemas](https://github.com/jikkujoyce/openspec-schemas/tree/main/schemas/anvil) | 带有 TDD 纪律和对抗性审查步骤的 spec-driven 工作流。流程：`proposal` → `specs` → `design` → `review` → `test-plan` → `tasks` → `apply` → `verify`。`review` 由一个新上下文、只读审查者（当有一个可用时为第二个模型）撰写，并发出一条 `VERDICT:` 行，告诉代理要控制 `test-plan`、`tasks` 和 `apply`；OpenSpec 只检查产物是否存在，所以请使用你自己的 CI 或钩子来强制执行该控制。`test-plan` 将每个规格场景映射到一个命名测试，并作为 `verify` 审计的红/绿台账。 |

> 想贡献一个社区模式？开一个 issue 并附上你的仓库链接，或提交 PR 添加一行到上表中。

---

## 另请参阅

- [CLI 参考：模式命令](cli.md#schema-commands) — 完整命令文档

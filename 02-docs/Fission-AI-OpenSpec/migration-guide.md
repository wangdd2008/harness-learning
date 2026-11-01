# 迁移到 OPSX

本指南帮助你从旧版 OpenSpec 工作流迁移到 OPSX。迁移过程设计得非常平滑——你的现有工作会被保留，而新系统提供了更大的灵活性。

## 发生了什么变化？

OPSX 用流畅的、基于行动的方式取代了旧的阶段锁定工作流。以下是关键变化：

| 方面 | 旧版 | OPSX |
|--------|--------|------|
| **命令** | `/openspec:proposal`, `/openspec:apply`, `/openspec:archive` | 默认: `/opsx:propose`, `/opsx:explore`, `/opsx:apply`, `/opsx:update`, `/opsx:sync`, `/opsx:archive` (扩展工作流命令可选) |
| **工作流** | 一次性创建所有产物 | 增量创建或一次性创建——由你选择 |
| **回退** | 尴尬的阶段门 | 自然的——随时更新任何产物 |
| **自定义** | 固定结构 | 基于模式，完全可定制 |
| **配置** | `CLAUDE.md` 带标记 + `project.md` | 干净的 `openspec/config.yaml` 配置 |

**理念变化：** 工作不是线性的。OPSX 不再假装它是线性的。

---

## 开始之前

### 你的现有工作是安全的

迁移过程以保留为设计理念：

- **`openspec/changes/` 中的活跃变更** — 完全保留。你可以继续使用 OPSX 命令处理它们。
- **已归档的变更** — 保持不变。你的历史记录完整保留。
- **`openspec/specs/` 中的主规格** — 保持不变。这些是你的事实来源。
- **你在 CLAUDE.md、AGENTS.md 等中的内容** — 保留。只有 OpenSpec 标记块被移除；你写的内容全部保留。

### 什么会被移除

只有被替换的 OpenSpec 管理文件：

| 内容 | 原因 |
|------|-----|
| 旧版斜杠命令目录/文件 | 被新的技能系统替代 |
| `openspec/AGENTS.md` | 过工作流触发器 |
| `CLAUDE.md`、`AGENTS.md` 等中的 OpenSpec 标记 | 不再需要 |

**各工具的旧版命令位置**（示例——你的工具可能不同）：

- Claude Code: `.claude/commands/openspec/`
- Cursor: `.cursor/commands/openspec-*.md`
- Devin Desktop, 前身为 Windsurf: `.windsurf/workflows/openspec-*.md`
- Cline: `.clinerules/workflows/openspec-*.md`
- Roo: `.roo/commands/openspec-*.md`
- GitHub Copilot: `.github/prompts/openspec-*.prompt.md`（仅限 IDE 扩展；Copilot CLI 不支持）
- Codex: OpenSpec 现在使用规范的 `.agents/skills/openspec-*` 路径。OpenSpec 管理的 `SKILL.md` 文件在旧 `.codex/skills` 路径下的，仅在存在替换文件后进行协调；自定义文件和发散副本保留在原处。如果未标记的 `.agents` 树已包含 OpenSpec 技能，OpenSpec 会保留其现有的 Codex（`$openspec-*`）或通用（`/openspec-*`）渲染，而非从旧目录猜测。使用 `openspec init` 显式选择 `codex` 以切换所有权。旧版提示清理仍仅针对 OpenSpec 允许列表中的文件名，位于 `$CODEX_HOME/prompts` 或 `~/.codex/prompts`。
- 以及其他（Augment、Continue、Amazon Q 等）

迁移会检测你已配置的工具并清理它们的旧版文件。

移除列表可能看起来很长，但这些都是 OpenSpec 最初创建的文件。你自己的内容永远不会被删除。

### 需要你注意的事项

有一个文件需要手动迁移：

**`openspec/project.md`** — 这个文件不会自动删除，因为它可能包含你写的项目上下文。你需要：

1. 审查其内容
2. 将有用上下文移到 `openspec/config.yaml`（见下方指导）
3. 准备好后删除该文件

**我们为什么做这个更改：**

旧的 `project.md` 是被动的——Agent 可能会读，可能不会读，可能会忘记读过什么。我们发现可靠性不一致。

新的 `config.yaml` 上下文**主动注入到每个 OpenSpec 规划请求中**。这意味着你的项目约定、技术栈和规则在 AI 创建产物时始终存在。可靠性更高。

**权衡：**

因为上下文注入到每个请求中，你需要保持简洁。专注于真正重要的内容：
- 技术栈和关键约定
- AI 需要知道的非显而易见的约束
- 以前经常被忽略的规范

不必担心做到完美。我们仍在试验什么最有效，并且会随着实验不断改进上下文注入的方式。

---

## 运行迁移

`openspec init` 和 `openspec update` 都会检测旧版文件并引导你完成相同的清理过程。根据你的情况选择合适的方式：

- 新安装默认使用 `core` 配置（`propose`、`explore`、`apply`、`update`、`sync`、`archive`）。
- 迁移后的安装通过写入 `custom` 配置来保留你之前安装的工作流。

### 使用 `openspec init`

如果你想添加新工具或重新配置已设置的工具，请运行：

```bash
openspec init
```

init 命令检测旧版文件并引导你完成清理：

```
升级到新版 OpenSpec

OpenSpec 现在使用 Agent 技能，这是跨编码
Agent 的新兴标准。这简化了你的设置，同时保持一切
像以前一样工作。

要移除的文件
无需保留的用户内容：
  • .claude/commands/openspec/
  • openspec/AGENTS.md

要更新的文件
OpenSpec 标记将被移除，你的内容被保留：
  • CLAUDE.md
  • AGENTS.md

需要你注意
  • openspec/project.md
    我们不会删除这个文件。它可能包含有用的项目上下文。

    新的 openspec/config.yaml 有一个 "context:" 部分用于规划
    上下文。这包含在每个 OpenSpec 请求中，比旧的
    project.md 方法更可靠。

    审查 project.md，将任何有用内容移到 config.yaml 的 context
    部分，然后准备好后删除该文件。

? 升级并清理旧版文件？ (Y/n)
```

**当你确认后会发生什么：**

1. 旧版斜杠命令目录被移除
2. OpenSpec 标记从 `CLAUDE.md`、`AGENTS.md` 等中剥离（你的内容保留）
3. `openspec/AGENTS.md` 被删除
4. 新技能安装在 `.claude/skills/` 中
5. `openspec/config.yaml` 被创建，带有默认模式

### 使用 `openspec update`

如果你只想迁移并将现有工具刷新到最新版本：

```bash
openspec update
```

update 命令同样检测并清理旧版产物，然后刷新生成的技能/命令以匹配你当前的配置和交付设置。

### 非交互式 / CI 环境

对于脚本化迁移：

```bash
openspec init --force --tools claude
```

`--force` 标志跳过提示并自动接受清理。

这包括对 OpenSpec 管理的 Codex 提示文件在全局 Codex 提示目录中的清理。清理仅针对 OpenSpec 允许列表中的旧版 Codex 提示文件名，仅在替换的 `.agents/skills/openspec-*` 技能存在后移除它们，并保留所有其他文件。

---

## 将 project.md 迁移到 config.yaml

旧的 `openspec/project.md` 是用于项目上下文的自由格式 markdown 文件。新的 `openspec/config.yaml` 是结构化的——并且关键的是——**注入到每个规划请求中**，因此你的约定在 AI 工作时始终存在。

### 之前 (project.md)

```markdown
# 项目上下文

这是一个使用 React 和 Node.js 的 TypeScript 单体仓库。
我们使用 Jest 进行测试并遵循严格的 ESLint 规则。
我们的 API 是 RESTful 的，文档记录在 docs/api.md 中。

## 约定

- 所有公共 API 必须保持向后兼容
- 新功能应包含测试
- 对规格说明使用 Given/When/Then 格式
```

### 之后 (config.yaml)

```yaml
schema: spec-driven

context: |
  技术栈: TypeScript, React, Node.js
  测试: Jest with React Testing Library
  API: RESTful, documented in docs/api.md
  我们保持所有公共 API 的向后兼容

rules:
  proposal:
    - 对有风险的变化包含回滚计划
  specs:
    - 对场景使用 Given/When/Then 格式
    - 在发明新模式之前参考现有模式
  design:
    - 对复杂流程包含序列图
```

### 关键区别

| project.md | config.yaml |
|------------|-------------|
| 自由格式 markdown | 结构化 YAML |
| 一大段文本 | 分开的上下文和按产物规则 |
| 不清楚何时使用 | 上下文出现在所有产物中；规则仅出现在匹配产物中 |
| 无模式选择 | 显式 `schema:` 字段设置默认工作流 |

### 保留什么，舍弃什么

迁移时要有选择性。问自己："AI 在*每个*规划请求中都需要这个吗？"

**`context:` 的好候选**
- 技术栈（语言、框架、数据库）
- 关键架构模式（单体仓库、微服务等）
- 非显而易见的约束（"我们不能使用库 X，因为……"）
- 经常被忽略的关键约定

**改为移到 `rules:`**
- 产物特定的格式（"在规格说明中使用 Given/When/Then"）
- 审查标准（"提案必须包含回滚计划"）
- 这些只出现在匹配产物中，保持其他请求更轻量

**完全省略**
- AI 已经知道的一般最佳实践
- 可以总结的冗长解释
- 不影响当前工作的历史背景

### 迁移步骤

1. **创建 config.yaml**（如果 init 未创建）：
   ```yaml
   schema: spec-driven
   ```

2. **添加你的上下文**（要简洁——这会进入每个请求）：
   ```yaml
   context: |
     你的项目背景放在这里。
     专注于 AI 真正需要知道的内容。
   ```

3. **添加按产物规则**（可选）：
   ```yaml
   rules:
     proposal:
       - 你的提案特定指导
     specs:
       - 你的规格编写规则
   ```

4. **删除 project.md**，在你移完所有有用内容后。

**不要想太多。** 从基础开始，然后迭代。如果你注意到 AI 遗漏了重要内容，就加上去。如果上下文感觉臃肿，就精简它。这是一个活文档。

### 需要帮助？使用这个提示

如果你不确定如何提炼你的 project.md，请向你的 AI 助手询问：

```
我正在从 OpenSpec 旧的 project.md 迁移到新的 config.yaml 格式。

这是我当前的 project.md：
[粘贴你的 project.md 内容]

请帮我创建一个 config.yaml，包含：
1. 一个简洁的 `context:` 部分（这会注入到每个规划请求中，所以保持精简——专注于技术栈、关键约束和经常被忽略的约定）
2. 如果有内容是产物特定的，则添加 `rules:`（例如，"使用 Given/When/Then" 属于规格规则，不是全局上下文）

省略任何 AI 模型已经知道的通用内容。对简洁性要无情。
```

AI 会帮助你识别什么是必需的，什么可以精简。

---

## 新命令

命令可用性取决于配置：

**默认 (`core` 配置):**

| 命令 | 用途 |
|---------|---------|
| `/opsx:propose` | 一步创建变更并生成规划产物 |
| `/opsx:explore` | 无结构地思考想法 |
| `/opsx:apply` | 从 tasks.md 实现任务 |
| `/opsx:update` | 修订变更的规划产物并保持它们一致 |
| `/opsx:sync` | 将 delta 规格合并到主规格 |
| `/opsx:archive` | 最终完成并归档变更 |

**扩展工作流 (自定义选择):**

| 命令 | 用途 |
|---------|---------|
| `/opsx:new` | 开始一个新的变更脚手架 |
| `/opsx:continue` | 创建下一个产物（一次一个） |
| `/opsx:ff` | 快进——一次性创建规划产物 |
| `/opsx:verify` | 验证实现与规格是否匹配 |
| `/opsx:bulk-archive` | 一次性归档多个变更 |
| `/opsx:onboard` | 引导式端到端入门工作流 |

使用 `openspec config profile` 启用扩展命令，然后运行 `openspec update`。

### 从旧版映射命令

| 旧版 | OPSX 等效 |
|--------|-----------------|
| `/openspec:proposal` | `/opsx:propose` (默认) 或 `/opsx:new` 然后 `/opsx:ff` (扩展) |
| `/openspec:apply` | `/opsx:apply` |
| `/openspec:archive` | `/opsx:archive` |

### 新能力

这些能力是扩展工作流命令集的一部分。

**细粒度产物创建：**
```
/opsx:continue
```
根据依赖关系一次创建一个产物。当你想审查每一步时使用此命令。

**探索模式：**
```
/opsx:explore
```
在承诺变更之前与合作伙伴一起思考想法。

---

## 理解新架构

### 从阶段锁定到流畅

旧版工作流强制线性推进：

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   规划阶段   │ ───► │   实现阶段   │ ───► │   归档阶段   │
└──────────────┘      └──────────────┘      └──────────────┘

如果你在实现阶段意识到设计错了？
太糟糕了。阶段门不容易让你回去。
```

OPSX 使用行动，而非阶段：

```
         ┌───────────────────────────────────────────────┐
         │            行动 (而非阶段)                      │
         │                                               │
         │     new ◄──► continue ◄──► apply ◄──► archive │
         │      │          │           │             │   │
         │      └──────────┴───────────┴─────────────┘   │
         │                    任意顺序                    │
         └───────────────────────────────────────────────┘
```

### 依赖关系图

产物形成一个有向图。依赖关系是促成因素，不是门：

```
                        proposal
                       (根节点)
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
           specs                       design
        (requires:                  (requires:
         proposal)                   proposal)
              │                           │
              └─────────────┬─────────────┘
                            │
                            ▼
                         tasks
                     (requires:
                     specs, design)
```

当你运行 `/opsx:continue` 时，它检查什么已就绪并提供下一个产物。你也可以按任意顺序创建多个就绪产物。

### 技能 vs 命令

旧版系统使用工具特定的命令文件：

```
.claude/commands/openspec/
├── proposal.md
├── apply.md
└── archive.md
```

OPSX 使用新兴的**技能**标准：

```
.claude/skills/
├── openspec-explore/SKILL.md
├── openspec-new-change/SKILL.md
├── openspec-continue-change/SKILL.md
├── openspec-apply-change/SKILL.md
└── ...
```

技能在多个 AI 编码工具中被识别，并提供更丰富的元数据。

Codex 在 OPSX 中仅支持技能。OpenSpec 不再生成 Codex 自定义提示文件；请使用生成的 `.agents/skills/openspec-*` 目录。

---

## 继续现有变更

你进行中的变更与 OPSX 命令无缝工作。

**有来自旧版工作流的活跃变更？**

```
/opsx:apply add-my-feature
```

OPSX 读取现有产物并从你离开的地方继续。

**想为现有变更添加更多产物？**

```
/opsx:continue add-my-feature
```

根据已存在的内容显示可以创建什么。

**需要查看状态？**

```bash
openspec status --change add-my-feature
```

---

## 新配置系统

### config.yaml 结构

```yaml
# 必需: 新变更的默认模式
schema: spec-driven

# 可选: 项目上下文 (最大 50KB)
# 注入到所有产物指令中
context: |
  你的项目背景、技术栈、
  约定和约束。

# 可选: 按产物规则
# 仅注入到匹配产物中
rules:
  proposal:
    - 包含回滚计划
  specs:
    - 使用 Given/When/Then 格式
  design:
    - 记录回退策略
  tasks:
    - 拆分为最多 2 小时的块
```

### 模式解析

在确定使用哪个模式时，OPSX 按以下顺序检查：

1. **CLI 标志**: `--schema <name>` (最高优先级)
2. **变更元数据**: 变更目录中的 `.openspec.yaml`
3. **项目配置**: `openspec/config.yaml`
4. **默认值**: `spec-driven`

### 可用模式

| 模式 | 产物 | 最适合 |
|--------|-----------|----------|
| `spec-driven` | proposal → specs → design → tasks | 大多数项目 |

列出所有可用模式：

```bash
openspec schemas
```

### 自定义模式

创建你自己的工作流：

```bash
openspec schema init my-workflow
```

或复刻现有模式：

```bash
openspec schema fork spec-driven my-workflow
```

详情见 [自定义](customization.md)。

---

## 故障排除

### "在非交互模式下检测到旧版文件"

你在 CI 或非交互环境中运行。请使用：

```bash
openspec init --force
```

### 迁移后命令未出现

重启你的 IDE。技能在启动时检测。

### "规则中的产物 ID 未知"

检查你的 `rules:` 键是否匹配模式的产物 ID：

- **spec-driven**: `proposal`, `specs`, `design`, `tasks`

运行以下命令查看有效的产物 ID：

```bash
openspec schemas --json
```

### 配置未应用

1. 确保文件位于 `openspec/config.yaml`（不是 `.yml`）
2. 验证 YAML 语法
3. 配置更改立即生效——无需重启

### project.md 未迁移

系统有意保留 `project.md`，因为它可能包含你的自定义内容。手动审查它，将有用部分移到 `config.yaml`，然后删除它。

### 想看看会清理什么？

运行 init 并拒绝清理提示——你会看到完整的检测摘要，而不会进行任何更改。

---

## 快速参考

### 迁移后的文件

```
project/
├── openspec/
│   ├── specs/                    # 不变
│   ├── changes/                  # 不变
│   │   └── archive/              # 不变
│   └── config.yaml               # 新增: 项目配置
├── .claude/
│   └── skills/                   # 新增: OPSX 技能
│       ├── openspec-propose/     # 默认 core 配置
│       ├── openspec-explore/
│       ├── openspec-apply-change/
│       ├── openspec-update-change/
│       ├── openspec-sync-specs/
│       ├── openspec-archive-change/
│       └── ...                   # 扩展配置添加 new/continue/ff 等
├── CLAUDE.md                     # OpenSpec 标记已移除，你的内容保留
└── AGENTS.md                     # OpenSpec 标记已移除，你的内容保留
```

### 已移除的内容

- `.claude/commands/openspec/` — 被 `.claude/skills/` 替代
- `openspec/AGENTS.md` — 已过时
- `openspec/project.md` — 迁移到 `config.yaml`，然后删除
- `CLAUDE.md`、`AGENTS.md` 等中的 OpenSpec 标记块

### 命令速查表

```text
/opsx:propose      快速开始 (默认 core 配置)
/opsx:apply        实现任务
/opsx:archive      完成并归档

# 扩展工作流 (如果启用):
/opsx:new          搭建变更
/opsx:continue     创建下一个产物
/opsx:ff           创建规划产物
```

---

## 获取帮助

- **Discord**: [discord.gg/YctCnvvshC](https://discord.gg/YctCnvvshC)
- **GitHub Issues**: [github.com/Fission-AI/OpenSpec/issues](https://github.com/Fission-AI/OpenSpec/issues)
- **文档**: [docs/opsx.md](opsx.md) 获取完整的 OPSX 参考

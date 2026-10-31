# 命令

这是 OpenSpec 斜杠命令的参考。这些命令在你的 AI 编程助手的聊天界面中调用（例如，Claude Code、Cursor、Devin Desktop）。

有关工作流模式以及何时使用每个命令，请参阅[工作流](workflows.md)。有关 CLI 命令，请参阅[CLI](cli.md)。

这些页面使用 `/opsx:<command>` 作为规范名称。某些工具的拼写方式不同 — Cursor 和 GitHub Copilot 注册 `/opsx-propose`，Codex 使用 `$openspec-propose` — 因此请检查[如何调用](supported-tools.md#how-to-invoke)以了解你的工具。OpenSpec 生成的文件已经使用了正确的形式。

## 快速参考

### 默认快速路径（`core` 配置文件）

| 命令 | 目的 |
|---------|---------|
| `/opsx:propose` | 创建变更并一步生成规划产物 |
| `/opsx:explore` | 在承诺变更之前思考想法 |
| `/opsx:apply` | 从变更中实现任务 |
| `/opsx:update` | 修订变更的规划产物并保持它们一致 |
| `/opsx:sync` | 将差异规格说明合并到主规格说明中 |
| `/opsx:archive` | 归档已完成的变更 |

### 扩展工作流命令（自定义工作流选择）

| 命令 | 目的 |
|---------|---------|
| `/opsx:new` | 开始新的变更脚手架 |
| `/opsx:continue` | 基于依赖关系创建下一个产物 |
| `/opsx:ff` | 快进：一次创建所有规划产物 |
| `/opsx:verify` | 验证实现是否匹配产物 |
| `/opsx:bulk-archive` | 一次归档多个变更 |
| `/opsx:onboard` | 引导你完成完整工作流的交互式教程 |

默认全局配置文件是 `core`。要启用扩展工作流命令，请运行 `openspec config profile`，选择工作流，然后在你的项目中运行 `openspec update`。

---

## 命令参考

### `/opsx:propose`

创建新变更并一步生成规划产物。这是 `core` 配置文件中的默认起始命令。

**语法：**
```text
/opsx:propose [change-name-or-description]
```

**参数：**
| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-name-or-description` | 否 | 短横线命名或纯语言变更描述 |

**它做什么：**
- 创建 `openspec/changes/<change-name>/`
- 生成实现之前所需的产物（对于 `spec-driven`：proposal、specs、design、tasks）
- 在变更准备好 `/opsx:apply` 时停止

**示例：**
```text
你：/opsx:propose add-dark-mode

AI： 创建了 openspec/changes/add-dark-mode/
     ✓ proposal.md
     ✓ specs/ui/spec.md
     ✓ design.md
     ✓ tasks.md
     准备好实现。运行 /opsx:apply。
```

**提示：**
- 用于最快的端到端路径
- 如果你想要逐步产物控制，请启用扩展工作流并使用 `/opsx:new` + `/opsx:continue`

---

### `/opsx:explore`

> **不确定时从这里开始。**探索是一个无风险的思考伙伴：它阅读你的代码库，比较选项，并在编写任何代码之前将模糊的想法变成具体的计划。它随默认配置文件一起提供。有关完整案例和更多示例，请参阅[先探索](explore.md)指南。

思考想法，调查问题，并在承诺变更之前澄清需求。

**语法：**
```
/opsx:explore [topic]
```

**参数：**
| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `topic` | 否 | 你想要探索或调查的内容 |

**它做什么：**
- 打开不需要结构的探索性对话
- 调查代码库以回答问题
- 比较选项和方法
- 创建可视化图表以澄清思路
- 在你要求时捕获探索，或在你同意时提供：搭建变更并使用 `openspec new change` 写入你命名的规划产物，或更新现有变更的产物
- 当见解结晶时可以过渡到 `/opsx:propose`（默认）或 `/opsx:new`（扩展工作流）

**示例：**
```text
你：/opsx:explore

AI： 你想要探索什么？

你：我们应该如何处理移动应用的认证？

AI： 让我调查你当前的认证设置...
     [分析代码库]

     我看到你正在为 Web 应用使用基于会话的认证。
     对于移动应用，我们有三个主要选项：

     1. JWT 令牌（无状态，离线工作）
     2. OAuth2（如果你需要第三方登录）
     3. 扩展当前会话（更简单，但需要连接）

     你的 API 已经配置了 CORS。你对哪个方向感兴趣？

你：我们选择 JWT。

AI： 这是一个值得保留的决定。要我启动一个名为
     add-jwt-auth 的变更吗？只是变更文件夹，其他什么也没有。

你：好。

AI： 已启动 openspec/changes/add-jwt-auth/。说一声，我就从
     我们刚才讨论的内容中写出 proposal、specs 和 tasks。
```

**提示：**
- 当需求不清楚或你需要调查时使用
- 它从不编写代码，也不会在你要求时编写其他内容，除非你同意
- 适合在决定前比较多种方法
- 可以阅读和搜索代码库

---

### `/opsx:new`

开始新的变更脚手架。创建变更文件夹并等待你使用 `/opsx:continue` 或 `/opsx:ff` 生成产物。

此命令是扩展工作流集的一部分（不包含在默认的 `core` 配置文件中）。

**语法：**
```
/opsx:new [change-name] [--schema <schema-name>]
```

**参数：**
| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-name` | 否 | 变更文件夹的名称（如果未提供则提示） |
| `--schema` | 否 | 要使用的工作流模式（默认：来自配置或 `spec-driven`） |

**它做什么：**
- 创建 `openspec/changes/<change-name>/` 目录
- 在变更文件夹中创建 `.openspec.yaml` 元数据文件
- 显示准备好创建的第一个产物模板
- 如果未提供，则提示变更名称和模式

**它创建了什么：**
```
openspec/changes/<change-name>/
└── .openspec.yaml    # 变更元数据（模式、创建日期）
```

**示例：**
```
你：/opsx:new add-dark-mode

AI： 创建了 openspec/changes/add-dark-mode/
     模式：spec-driven

     准备好创建：proposal
     使用 /opsx:continue 创建它，或 /opsx:ff 创建所有产物。
```

**提示：**
- 使用描述性名称：`add-feature`、`fix-bug`、`refactor-module`
- 避免通用名称如 `update`、`changes`、`wip`
- 模式也可以在项目配置（`openspec/config.yaml`）中设置

---

### `/opsx:continue`

在依赖链中创建下一个产物。一次创建一个产物以实现增量进展。

**语法：**
```
/opsx:continue [change-name]
```

**参数：**
| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-name` | 否 | 要继续的变更（如果未提供则从上下文推断） |

**它做什么：**
- 查询产物依赖图
- 显示哪些产物已准备好 vs 被阻塞
- 创建第一个准备好的产物
- 读取依赖文件以获取上下文
- 显示创建后什么变得可用

**示例：**
```
你：/opsx:continue

AI： 变更：add-dark-mode

     产物状态：
     ✓ proposal    （完成）
     ◆ specs       （准备好）
     ◆ design      （准备好）
     ○ tasks       （阻塞 - 需要：specs、design）

     正在创建 specs...

     [读取 proposal.md，基于需求创建 specs]

     ✓ 创建了 openspec/changes/add-dark-mode/specs/ui/spec.md

     现在可用：design
     运行 /opsx:continue 创建下一个产物。
```

**提示：**
- 当你想要在继续之前审查每个产物时使用
- 适合你想要控制的复杂变更
- 多个产物可能同时变得准备好
- 你可以在继续之前编辑已创建的产物

---

### `/opsx:ff`

快速前进通过产物创建。一次创建所有规划产物。

**语法：**
```
/opsx:ff [change-name]
```

**参数：**
| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-name` | 否 | 要快进的变更（如果未提供则从上下文推断） |

**它做什么：**
- 按依赖顺序创建所有产物
- 通过待办事项列表跟踪进度
- 当所有 `apply-required` 产物完成时停止
- 在创建下一个产物之前读取每个依赖项

**示例：**
```
你：/opsx:ff add-dark-mode

AI： 正在快进 add-dark-mode...

     ✓ 创建 proposal.md
     ✓ 创建 specs/ui/spec.md
     ✓ 创建 design.md
     ✓ 创建 tasks.md

     所有规划产物完成！
     准备好实现。运行 /opsx:apply 开始。
```

**提示：**
- 当你对要构建的内容有清晰认识时使用
- 比 `/opsx:continue` 更快，适用于简单的变更
- 你仍然可以在事后编辑产物
- 适合中小型功能

---

### `/opsx:apply`

从变更中实现任务。处理任务列表，编写代码并勾选项目。

**语法：**
```
/opsx:apply [change-name]
```

**参数：**
| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-name` | 否 | 要实现的变更（如果未提供则从上下文推断） |

**它做什么：**
- 读取 `tasks.md` 并识别未完成的任务
- 逐个处理任务
- 编写代码、创建文件、按需运行测试
- 用复选框 `[x]` 标记完成的任务

**示例：**
```
你：/opsx:apply

AI： 正在实现 add-dark-mode...

     读取 tasks.md：
     - [ ] 1.1 创建 ThemeContext
     - [ ] 1.2 添加 CSS 自定义属性
     - [ ] 1.3 实现 localStorage 持久化

     正在处理 1.1：创建 ThemeContext...
     [创建 src/context/ThemeContext.tsx]

     ✓ 1.1 完成

     正在处理 1.2：添加 CSS 自定义属性...
     [更新 src/styles/globals.css]

     ✓ 1.2 完成
     ...
```

**提示：**
- 如果中断，可以从头继续
- 通过指定变更名称用于并行变更
- 完成状态在 `tasks.md` 复选框中跟踪

---

### `/opsx:update`

修订变更的现有规划产物并保持它们彼此之间的一致性。仅规划产物 — 它从不编辑代码。

**语法：**

```text
/opsx:update [change-name]
```

**参数：**

| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-name` | 否 | 要更新的变更（如果未提供则从上下文推断） |

**它做什么：**

- 通过 `openspec status --change <name> --json` 读取变更的产物
- 应用你请求的修订，如果你没有命名则在产物中审查矛盾
- 在任何方向协调其他现有产物（设计编辑可能会波及到提案）
- 在写入之前逐个产物确认每次编辑
- 最后推荐下一步：`/opsx:continue`（未开始的产物）、`/opsx:apply`（将修订后的计划带入代码）或 `/opsx:archive`（全部完成）

**缺失文件：**

- 对于至少有一个现有文件的 glob 产物（如 `specs/**/*.md`），如果存在，update 可以建议缺失的配套文件。它使用模式的指令并要求你在创建之前确认具体路径。
- 还没有文件的产物仍保留给 `/opsx:continue`。故意跳过的产物保持不动。
- 新文件必须保留在变更目录内。如果文件在创建之前出现在确认的路径上，update 会停止而不是覆盖它。

**示例：**

```text
你：/opsx:update add-dark-mode - 我们现在将主题存储在 cookie 中，而不是 localStorage

AI： 正在读取 add-dark-mode 产物...

     design 在两个地方引用了 localStorage；tasks 1.3 涉及
     localStorage 持久化；proposal 没有提到存储。

     提议的修订：
     1. design.md - 将 localStorage 决定替换为 cookie 存储
     2. tasks.md - 将任务 1.3 重新表述为 cookie 持久化

     应用修订 1？（design.md）
```

**提示：**

- 它不会启动没有现有文件的产物。启用 `/opsx:continue`，或使用 `openspec status` 和 `openspec instructions`（如果该可选工作流未安装）。
- 如果变更已经实现，请跟进 `/opsx:apply` 以使代码匹配修订后的计划
- 如果你的修订变更了变更的*意图*，请改用新变更从头开始（请参阅[何时更新 vs 重新开始](opsx.md#when-to-update-vs-start-fresh)）

---

### `/opsx:verify`

验证实现是否匹配变更产物。检查完整性、正确性和一致性。

**语法：**
```
/opsx:verify [change-name]
```

**参数：**
| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-name` | 否 | 要验证的变更（如果未提供则从上下文推断） |

**它做什么：**
- 检查实现质量的三个维度
- 搜索代码库中的实现证据
- 将问题分类为 CRITICAL、WARNING 或 SUGGESTION
- 不阻塞归档，但会浮现问题

**验证维度：**

| 维度 | 它验证什么 |
|-----------|-------------------|
| **完整性** | 所有任务完成，所有需求实现，场景覆盖 |
| **正确性** | 实现匹配规格说明意图，边缘情况处理 |
| **一致性** | 设计决策反映在代码中，模式一致 |

**示例：**
```
你：/opsx:verify

AI： 正在验证 add-dark-mode...

     完整性
     ✓ tasks.md 中的 8 个任务已全部勾选
     ✓ specs 中的所有需求都有对应的代码
     ⚠ 场景"系统偏好检测"没有测试覆盖

     正确性
     ✓ 实现匹配规格说明意图
     ✓ 场景中的边缘情况已处理
     ✓ 错误状态匹配规格说明定义

     一致性
     ✓ 设计决策反映在代码结构中
     ✓ 命名约定与 design.md 一致
     ⚠ 设计提到"CSS 变量"但实现使用 Tailwind 类

     摘要
     ─────────────────────────────
     关键问题：0
     警告：2
     准备好归档：是（有警告）

     建议：
     1. 为系统偏好检测添加测试
     2. 更新 design.md 以反映 Tailwind 用法，或重构为使用 CSS 变量
```

**提示：**
- 在归档之前运行以尽早发现不匹配
- 警告不阻塞归档，但指示潜在问题
- 适合在提交之前审查 AI 的工作
- 可以揭示产物和实现之间的差异

---

### `/opsx:sync`

**可选命令。**将变更的差异规格说明合并到主规格说明中。归档会在需要时提示同步，因此你通常不需要手动运行它。

**语法：**
```
/opsx:sync [change-name]
```

**参数：**
| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-name` | 否 | 要同步的变更（如果未提供则从上下文推断） |

**它做什么：**
- 从变更文件夹读取差异规格说明
- 解析 新增/修改/移除/重命名 章节
- 将变更合并到主 `openspec/specs/` 目录
- 保留差异中未提及的现有内容
- 不归档变更（保持活跃）

**示例：**
```
你：/opsx:sync

AI： 正在同步 add-dark-mode 差异规格说明...

     读取：openspec/changes/add-dark-mode/specs/ui/spec.md
     目标：openspec/specs/ui/spec.md

     要应用的变更：
     ✓ 新增：主题选择需求（2 个场景）
     ✓ 新增：无障碍需求（1 个场景）

     合并中...
     ✓ openspec/specs/ui/spec.md 已更新

     变更保持活跃。准备好时运行 /opsx:archive 完成。
```

**何时手动使用：**

| 场景 | 使用同步？ |
|----------|-----------|
| 长期运行的变更，想在归档之前将规格说明保留在主规格说明中 | 是 |
| 多个并行变更需要更新的基础规格说明 | 是 |
| 想要预览/单独审查合并 | 是 |
| 快速变更，直接归档 | 否（归档会处理它） |

**提示：**
- 同步是智能的，不是复制粘贴
- 可以向现有需求添加场景而不会重复
- 同步后变更保持活跃（未归档）
- 大多数用户永远不需要直接调用它 — 归档会在需要时提示

---

### `/opsx:archive`

归档已完成的变更。完成变更并将其移动到归档文件夹。

**语法：**
```
/opsx:archive [change-name]
```

**参数：**
| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-name` | 否 | 要归档的变更（如果未提供则从上下文推断） |

**它做什么：**
- 检查产物完成状态
- 检查任务完成（如果不完整则警告）
- 如果尚未同步，则提供同步差异规格说明
- 将变更文件夹移动到 `openspec/changes/archive/YYYY-MM-DD-<name>/`
- 保留所有产物以供审计

**示例：**
```
你：/opsx:archive

AI： 正在归档 add-dark-mode...

     产物状态：
     ✓ proposal.md 存在
     ✓ specs/ 存在
     ✓ design.md 存在
     ✓ tasks.md 存在（8/8 任务完成）

     差异规格说明：尚未同步
     → 现在同步？（推荐）

你：是

AI：  ✓ 规格同步到 openspec/specs/ui/spec.md
     ✓ 移动到 openspec/changes/archive/2025-01-24-add-dark-mode/

     变更归档成功。
```

**提示：**
- 归档不会阻塞不完整的任务，但会警告
- 差异规格说明可以在归档期间或之前同步
- 归档的变更保留以供历史查看
- 先使用 `/opsx:verify` 以发现问题

---

### `/opsx:bulk-archive`

一次归档多个已完成的变更。处理变更之间的规格说明冲突。

**语法：**
```
/opsx:bulk-archive [change-names...]
```

**参数：**
| 参数 | 必需 | 描述 |
|----------|----------|-------------|
| `change-names` | 否 | 要归档的特定变更（如果未提供则提示选择） |

**它做什么：**
- 列出所有已完成的变更
- 归档前验证每个变更
- 检测变更之间的规格说明冲突
- 通过检查实际实现来解决冲突
- 按时间顺序归档

**示例：**
```
你：/opsx:bulk-archive

AI： 发现 3 个已完成的变更：
     - add-dark-mode（8/8 任务完成）
     - fix-login-bug（3/3 任务完成）
     - update-footer（2/2 任务完成）

     检查规格说明冲突...
     ⚠ add-dark-mode 和 update-footer 都触及 specs/ui/

     检查代码库以解决...
     两个变更都已实现。将按时间顺序合并：
     1. add-dark-mode（1 月 20 日创建）
     2. update-footer（1 月 22 日创建）

     归档所有 3 个变更？

你：是

AI：  ✓ 归档 add-dark-mode
     ✓ 归档 fix-login-bug
     ✓ 归档 update-footer
     规格说明合并：add-dark-mode → update-footer
```

**提示：**
- 适合并行工作流
- 冲突解决是代理式的（检查代码库）
- 变更按创建顺序归档
- 在覆盖规格内容之前提示

---

### `/opsx:onboard`

引导你完成完整 OpenSpec 工作流。使用你的实际代码库的交互式教程。

**语法：**
```
/opsx:onboard
```

**它做什么：**
- 引导你完成完整的工作流循环并附带叙述
- 扫描你的代码库以寻找真正的改进机会
- 创建具有真实产物的实际变更
- 实现实际工作（小的、安全的变更）
- 归档已完成的变更
- 解释每一步

**阶段：**
1. 欢迎和代码库分析
2. 寻找改进机会
3. 创建变更（`/opsx:new`）
4. 编写提案
5. 创建规格说明
6. 编写设计
7. 创建任务
8. 实现任务（`/opsx:apply`）
9. 验证实现
10. 归档变更
11. 摘要和下一步

**示例：**
```
你：/opsx:onboard

AI： 欢迎来到 OpenSpec！

     我将引导你使用你的实际代码库完成完整的工作流。
     我们会找到一些小的改进，为它创建适当的变更，
     实现它，并归档它。

     让我扫描你的代码库以寻找机会...

     [分析代码库]

     我发现了一些我们可以处理的事情：
     1. 为联系表单添加输入验证
     2. 改进认证流程中的错误消息
     3. 为异步按钮添加加载状态

     你对哪个感兴趣？（或建议其他内容）
```

**提示：**
- 最适合学习工作流的新用户
- 使用真实代码，而非玩具示例
- 创建你可以保留或丢弃的真实变更
- 完成需要 15-30 分钟

---

## 按 AI 工具划分的命令语法

不同的 AI 工具使用稍微不同的命令语法。使用与你的工具匹配的格式：

| 你的工具的命令文件 | 语法示例 | 示例工具 |
|--------------------------|----------------|---------------|
| `.../commands/opsx/<id>.*` | `/opsx:propose`, `/opsx:apply` | Claude Code、Gemini CLI、Crush |
| `.../opsx-<id>.*` | `/opsx-propose`, `/opsx-apply` | Cursor、Devin Desktop、Copilot (IDE)、Trae、Oh My Pi |
| none — 仅技能 | `/openspec-propose`, `/openspec-apply-change` | CodeArts、ForgeCode、Hermes、MiniMax Code、Mistral Vibe、Zed Agent、共享 `.agents` |
| none — Kimi Code | `/skill:openspec-propose` | Kimi Code |
| none — Codex CLI | `$openspec-propose` | Codex |

> **Devin Desktop vs Devin Local：**`.devin/workflows/opsx-*.md` 文件给
> Devin Desktop 提供 `/opsx-propose`。Devin Local 没有工作流 — 请使用
> OpenSpec 写入 `.devin/skills/` 的技能，例如 `/openspec-propose`，在
> 两个代理上都有效。

意图在所有工具中都是相同的，但集成方式可能因工具而异。[如何调用](supported-tools.md#how-to-invoke)列出了每个受支持的工具；此表仅显示每种形式的示例。

> **注意：**GitHub Copilot 命令（`.github/prompts/*.prompt.md`）仅在 IDE 扩展（VS Code、JetBrains、Visual Studio）中可用。GitHub Copilot CLI 目前不支持自定义提示文件 — 有关详细信息和变通方法，请参阅[支持的工具](supported-tools.md)。

---

## 旧版命令

这些命令使用较旧的"一次性"工作流。它们仍然有效，但推荐使用 OPSX 命令。

| 命令 | 它做什么 |
|---------|--------------|
| `/openspec:proposal` | 一次创建所有产物（proposal、specs、design、tasks） |
| `/openspec:apply` | 实现变更 |
| `/openspec:archive` | 归档变更 |

**何时使用旧版命令：**
- 使用旧工作流的现有项目
- 不需要增量产物创建的简单变更
- 偏好全有或全无方法

**迁移到 OPSX：**
旧版变更可以继续使用 OPSX 命令。产物结构兼容。

---

## 故障排除

### "找不到变更"

命令无法识别要处理的变更。

**解决方案：**
- 显式指定变更名称：`/opsx:apply add-dark-mode`
- 检查变更文件夹是否存在：`openspec list`
- 验证你在正确的项目目录中

### "没有产物准备好"

所有产物要么完成，要么被缺失的依赖项阻塞。

**解决方案：**
- 运行 `openspec status --change <name>` 查看什么在阻塞
- 检查所需的产物是否存在
- 首先创建缺失的依赖产物

### "找不到模式"

指定的模式不存在。

**解决方案：**
- 列出可用模式：`openspec schemas`
- 检查模式名称拼写
- 如果是自定义模式，请创建它：`openspec schema init <name>`

### 命令未被识别

AI 工具无法识别 OpenSpec 命令。

**解决方案：**
- 确保 OpenSpec 已初始化：`openspec init`
- 重新生成技能：`openspec update`
- 检查 `.claude/skills/` 目录是否存在（对于 Claude Code）
- 重启你的 AI 工具以获取新技能

### 产物未正确生成

AI 创建不完整或不正确的产物。

**解决方案：**
- 在 `openspec/config.yaml` 中添加项目上下文
- 为特定指导添加每个产物的规则
- 在变更描述中提供更多详细信息
- 使用 `/opsx:continue` 而不是 `/opsx:ff` 以获得更的控制

---

## 下一步

- [工作流](workflows.md) — 常见模式以及何时使用每个命令
- [CLI](cli.md) — 用于管理和验证的终端命令
- [自定义](customization.md) — 创建自定义模式和工作流

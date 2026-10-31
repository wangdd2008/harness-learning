## 作用

`to-tickets` 获取一个计划、一个 [spec](https://www.aihero.dev/ai-coding-dictionary/spec)，或你所在的对话，并将其分解成 issue tracker 上的一组 **[tickets](https://www.aihero.dev/ai-coding-dictionary/ticket)**。每个 ticket 声明其 **blocking edges**：在它开始之前必须完成的其他 tickets。

每个 ticket 都是一个 **tracer bullet**：一条狭窄但完整的路径，贯穿变更的每一层（schema、API、UI、测试），一旦落地就可以单独演示。这就是该技能与显而易见的拆分工作方式的区别，后者是一次切割一层并在最后集成。它还将每个 ticket 的大小调整为适合单个新鲜的 [context window](https://www.aihero.dev/ai-coding-dictionary/context-window)，因为一个从未见过你 spec 的 [session](https://www.aihero.dev/ai-coding-dictionary/session) 会捡起 ticket。

## 何时使用

你通过输入 `/to-tickets` 来调用它。[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 不会自动触发它。

| 你的状态 | 运行什么 |
| --- | --- |
| 你有 spec issue，构建跨越多个 session | `/to-tickets`，或 `/to-tickets #<spec_issue>` |
| 计划只在对话中，从未写出来 | `/to-tickets` 直接读取线程，无需 spec |
| 整个变更 fits 一个 context window | [implement](https://aihero.dev/skills-implement)，跳过 tickets |
| 什么都没决定 | [grill-with-docs](https://aihero.dev/skills-grill-with-docs)，然后 [to-spec](https://aihero.dev/skills-to-spec) |
| [wayfinder](https://aihero.dev/skills-wayfinder) 地图已清除 | [to-spec](https://aihero.dev/skills-to-spec) 首先，以压缩地图，然后 `/to-tickets` |

`to-tickets` 产生的 tickets 按构造就是 agent-ready 的。不要对它们运行 [triage](https://aihero.dev/skills-triage)。Triage 是针对从别人那里传来的工作。

## 前置条件

`to-tickets` 发布到 tracker 中，因此 [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) 必须为此 repo 配置一个 tracker，以及分类标签词汇。两种都可以：像 GitHub 或 Linear 这样的真实 tracker，或者 `.scratch/` 下的本地 markdown 文件，后者无需额外设置即可工作。

## Tracer bullets，不是 layers

**水平** slice 运送变更的一层。在所有层都落地之前什么都不工作，而且每个 ticket 的验收标准必须触及另一个 ticket 拥有的工作。**垂直** slice（tracer bullet）一次运送一条贯穿所有层的薄路径，因此它可以单独验证并拥有它评分的所有内容。

这是人们最常违反的规则。一个团队运行了一个按层切分的 26-ticket 堆栈（corpus、producer、aggregator、selector），每个关闭的 ticket 大约有二十个 agent 运行，其中约四分之三是返工。他们自己的 post-mortem 将每个失败类别都追溯到水平切片而不是实现。

在发布任何内容之前会发生两件事。`to-tickets` 寻找 prefactoring（原则"让变更容易，然后做容易的变更"）并将该工作排在前面。然后它以编号列表的形式呈现分解结果，并对你进行测验：粒度是否正确、blocking edges 是否真实、是否有任何应该合并或拆分的东西。在你批准之前，没有任何东西到达 tracker，而那个测验就是你提出异议的地方。

## Blocking edges

Edges 是 artifacts 的重点。它们以两种方式工作，取决于 tracker：

| Tracker | Edge 存在哪里 | 你如何操作它们 |
| --- | --- | --- |
| 本地 markdown | `.scratch/<feature>/issues/<NN>-<slug>.md` 下每个 ticket 一个文件中的文本，按 blockers-first 编号 | 从上到下，手动 |
| 真实 tracker（GitHub、Linear） | 原生 blocking links，或者 tracker 有的 sub-issues | 任何 blockers 都完成的 ticket 在 **frontier** 上，可以被抓取 |

Edges 无论如何都存在于 ticket 中。Tracker 只决定是否有东西可以并行作用于它们。`to-tickets` 产生 artifact；运行它（一次一个 session，或一批）是你的工作，不是该技能的。

## 大范围重构例外

有一种形状打破了 tracer-bullet 规则。**大范围重构**是单一的机械变更（重命名列、重新类型共享符号），其 **blast radius** 覆盖整个代码库。一次编辑会破坏数千个调用点，因此没有垂直 slice 能绿色落地。

`to-tickets` 将其序列化为 **expand–contract**：

- **Expand**：在旧形式旁边添加新形式，因此不会破坏任何东西。
- **Migrate**：按 blast radius 大小分批移动调用点（按包、按目录），每个批次一个 ticket，每个都被 expand 阻塞。CI 保持绿色，因为旧形式仍然存在。
- **Contract**：一旦没有调用者剩余，删除旧形式，在一个被每个 migrate 批次阻塞的 ticket 中。

即使批次无法单独保持绿色，它们也共享一个集成分支，并且都被一个最终的 integrate-and-verify ticket 阻塞。CI 只需要在该 ticket 上是绿色的。

## 常见问题

**它为三行变更产出了十二个 tickets。**

过度分解是该技能报告最多的问题，很多用户都看到了。[model](https://www.aihero.dev/ai-coding-dictionary/model) 默认为原子单位，失去了使它们有意义的 grouping。测验步骤就是你修复的地方。要求它合并 tickets，它会合并的。还有一个下限。如果整个变更 fits 一个 context window，你根本不需要这个技能。直接去找 [implement](https://aihero.dev/skills-implement)。

**Tickets 按层出来：所有 schema 在一个，所有 API 在另一个。**

这是 vertical-slice 规则所针对的失败，而且该技能有时仍会产生它。在测验步骤中通过为每个 ticket 问一个问题来发现它：完成后我可以演示什么？没有答案的 ticket 就是水平 slice。有些人为此在每个 ticket 上添加一条 "demo path"，并报告说这促使 model 走向垂直切片。

**在 GitHub 上，tickets 没有创建为 spec issue 的 sub-issues。**

这在多次运行和多个 model 中都有报告，[最完整地见于 issue #554](https://github.com/mattpocock/skills/issues/554)。已修复：`to-tickets` 现在将每个 ticket 设为其源 issue 的 sub-issue，GitHub tracker 模板给出了命令（`gh issue create --parent <n>`，`gh` 2.94+）。重新运行 [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) 以刷新较旧的 `docs/agents/issue-tracker.md`。

**"Blocked by" 被写进了 issue 正文而不是真正的 blocking link。**

这是同一类问题，[报告于 issue #513](https://github.com/mattpocock/skills/issues/513)，其中 agent 甚至声明 GitHub 没有原生的 blocking 关系。它有：`gh issue create --blocked-by 12,15`。因为该技能先发布 blockers，它们的编号在创建时总是可用的。正文文本是为没有原生 edge 的 tracker 提供的后备，而不是默认值。现在当 edges 是原生的时候，ticket 模板会省略 `## Blocked by`。

**本地 tickets 放在哪里？v1.1 的说明说根目录的 `tickets.md`。**

是的，那是个 bug。单个共享文件还会在并行 agents 写入时导致 race condition。本地模式现在将每个 ticket 写入 `.scratch/<feature-slug>/issues/<NN>-<slug>.md`，按依赖顺序排列，与本地 tracker 模板已描述的布局一致。`NN` 前缀是真实的 ticket ID，因此 `/implement 03` 可以工作，而无需重新输入长标题。

**它尝试读取我的 spec 时一直截断。**

一个非常大的 spec 可能超出 tracker issue 能干净返回的大小。没有本地副本可回退，因此 agent 花费 [tool calls](https://www.aihero.dev/ai-coding-dictionary/tool-call) 反复获取块，永远到不了尽头。不要在 `/to-spec` 和 `/to-tickets` 之间 [clear](https://www.aihero.dev/ai-coding-dictionary/clearing) 或 [compact](https://www.aihero.dev/ai-coding-dictionary/compaction)。在同一个 context window 中运行它们，agent 就永远不需要重新获取 spec。

**验收标准什么都没评分：有些在工作完成前就通过了。**

模板要求标准但没有说它们是否能失败，所以这会发生。三种形状反复出现：在基础 commit 已经真实的标准、只有另一个 ticket 中的工作才能满足的标准、以及重述请求而不是从 artifact 推导的标准。垂直切片可以防止大部分，因为交付新行为的 slice 按构造在基础 commit 上失败。手动检查仍然值得。对于每个标准，命名一个能显示它为假的观察，并确认它在实现者开始的 commit 上是失败的。

**Tickets 发布了。我该如何实际运行它们？**

该技能在 artifact 处停止，没有自动调度模式。调度是手动的：查看 board，统计没有 open blockers 的 tickets，并打开相应数量的 agent sessions。给每个 ticket 一个新鲜的 context，并在它们之间 clear。[implement](https://aihero.dev/skills-implement) 在完成时不会可靠地关闭或勾选 ticket，无论是在 GitHub 还是本地 markdown 上，所以你自己更新 ticket 的状态。

## 正常工作的标志

- 每个 ticket 都有 "完成后我可以演示什么？" 的答案，而且答案是行为，不是层。
- 列表在发布前返回给你，编号并带有每个 ticket 的 "Blocked by" 行。
- 顶部的 ticket 没有 blockers，可以立即开始。
- Ticket 正文中没有任何东西是文件路径或行号，除了原型产生的片段。
- 每个 ticket 读起来像是一个 fresh session 可以在没有你到房间的情况下完成的。
- Prefactoring，如果有的话，排在前面而不是混入 feature tickets。

## 它在何处适用

`to-tickets` 是主构建链中的一个步骤：

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

上游是 [to-spec](https://aihero.dev/skills-to-spec)，它交给它一个已确定的 spec 来切片。将两者保持在同一个 context window 中，中间没有 clear。下游是 [implement](https://aihero.dev/skills-implement)，它每次构建一个 fresh session 的 ticket，驱动 [tdd](https://aihero.dev/skills-tdd) 进行测试，并以 [code-review](https://aihero.dev/skills-code-review) 结束。[implement-spec](https://aihero.dev/skills-implement-spec) 是另一条路径。它读取相同的 blocking edges 作为任务图，并在集成分支上并行构建每个就绪的 ticket。当你不确定哪个技能或流程适用时，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你指引。

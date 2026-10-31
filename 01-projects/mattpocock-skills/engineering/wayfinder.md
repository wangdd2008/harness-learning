## 作用

`wayfinder` 处理对于单个 agent [session](https://www.aihero.dev/ai-coding-dictionary/session) 来说太大的工作。这是一个你能说出**目的地**但还看不到路线的想法。Wayfinder 将其绘制为你的 issue tracker 上共享的**地图**，由**决策 tickets**组成，然后逐个解决 tickets，直到路线清晰。

它规划而不构建。每个 ticket 问一个问题，答案是决策，而不是构建的一个切片。地图在没有任何东西需要在有人构建之前决定时完成。这条规则将 wayfinder ticket 与普通实现 [ticket](https://www.aihero.dev/ai-coding-dictionary/ticket) 区分开来，也是 agents 最常违反的规则。当地图清除时，wayfinder 移交并不再进入代码。

## 何时使用

你通过输入 `/wayfinder` 来调用它；[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 不会自动触发它。

它是该系列中最重的工作流，因此触发条件很窄。工作必须大于一个 agent session 能容纳的，而且到目的地的路线必须不清楚。按 session 数分割：`/grill-with-docs` 用于单 session 规划，`/wayfinder` 用于多 session 规划。

| 你面前有什么 | 运行什么 |
| --- | --- |
| 一个你能在一个 session 内确定的 well-scoped feature | [grill-me](https://aihero.dev/skills-grill-me)，或当有一个代码库时使用 [grill-with-docs](https://aihero.dev/skills-grill-with-docs) |
| 一个 greenfield 项目，或跨越多个 session 的构建，路线仍不清楚 | `/wayfinder` |
| 已经决定的对话线程 | [to-spec](https://aihero.dev/skills-to-spec)：跳过地图 |
| 已清除的 wayfinder 地图 | [to-spec](https://aihero.dev/skills-to-spec)，然后 [to-tickets](https://aihero.dev/skills-to-tickets) 和 [implement](https://aihero.dev/skills-implement) |
| 已经变得太大的现有 session | 说 "hand off to `/wayfinder`"（[handoff](https://aihero.dev/skills-handoff) 也会桥接到地图） |

Greenfield 不是必需的。人们经常在遗留和半构建的代码库上使用 wayfinder，而且在那里可能更有用，因为大部分迷雾是"这里已经有什么是真的"而不是"我们应该做什么"。

## 前置条件

地图及其 tickets 存在于 repo 的 issue tracker 上，因此 wayfinder 需要 [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) 的 tracker 设置。该步骤写入一个"Wayfinding operations"部分。该部分描述如何在 GitHub、GitLab 或本地 markdown 上表达地图、其子 tickets、blocking edges 和 frontier 查询。Wayfinder 通过你 `CLAUDE.md` / `AGENTS.md` 中的指针找到该文档，不是固定路径。如果没有配置 tracker，它会回退到本地 markdown 文件。

Tracker 确实做真正的工作。它的原生 blocking links 在 tracker 自己的 UI 中显示 frontier。在没有原生依赖链接的 tracker（例如自托管 Gitea）上，wayfinder 从地图文本中推断 blockers。这有效，但你必须更密切地监督它。

## 地图、迷雾和前沿

**地图**是一个标记为 `wayfinder:map` 的单一 issue，其 tickets 是它的子 issues。它是一个**索引，不是存储**。决策存在于唯一的地方，它的 ticket，而地图只提供一行摘要和一个链接。一个 session 以低分辨率加载地图，并在需要时打开单个 tickets。这让地图不断增长，而无需每个 session 加载它的整个历史。

地图有四个部分：

- **Destination。** 这个地图的终点看起来什么样。你首先命名它，在任何 ticket 存在之前，因为目的地固定了你衡量每个 ticket 的范围。
- **Decisions so far。** 每个关闭的 ticket 一行，每个都链接到详细信息所在的位置。
- **Not yet specified。** 这是**战争迷雾**：你能看到即将到来的决策，但还无法精确表述。雾与 ticket 的测试是，你现在能否精确地陈述问题，而不是你是否能回答它。当你解决一个 ticket 时，它前面的雾会清除，任何你现在能指定的东西都会升级为新 ticket。
- **Out of scope。** 目的地之外的工作。雾只向*目的地*聚集，所以 out-of-scope 工作保持关闭，永不升级。

**前沿**是开放的、未被阻塞的、未被认领的 tickets 集合（已知世界的边缘）。一个 session 通过将自己分配给它来认领 ticket，然后再做任何工作。受让人*就是*认领，所以并发 sessions 会跳过该 ticket。Sessions 按名称引用 tickets，从不使用裸 `#42`，因为一墙 issue 号码在阅读时很难懂。

## 四种决策 ticket 类型

每个 ticket 携带一个 `wayfinder:<type>` 标签。每个 ticket 要么是 **[HITL](https://www.aihero.dev/ai-coding-dictionary/human-in-the-loop)**（与人类一起工作，人类为自己发言）要么是 **[AFK](https://www.aihero.dev/ai-coding-dictionary/afk)**（仅由 agent 驱动）。HITL ticket 只能通过实时交流解决。回答自己的 [grilling](https://www.aihero.dev/ai-coding-dictionary/grilling) 问题的 agent 已经破坏了它。

| 类型 | 模式 | 何时使用 | 由谁解决 |
| --- | --- | --- | --- |
| `grilling` | HITL | 默认。问题可以通过讨论解决。 | [grilling](https://aihero.dev/skills-grilling) 加 [domain-modeling](https://aihero.dev/skills-domain-modeling)，在 fresh session 中 |
| `prototype` | HITL | "这应该长什么样"或"它应该如何行为"：讨论无法解决的问题。 | [prototype](https://aihero.dev/skills-prototype)，带有从 ticket 到构建的 artifact 的链接 |
| `research` | AFK | 阻止决策的事实位于工作目录之外。 | 一个 [research](https://aihero.dev/skills-research) [subagent](https://www.aihero.dev/ai-coding-dictionary/subagent)，在你绘制地图时启动，并在 `research/<name>` 分支上并行运行 |
| `task` | 任一 | 无需决定，但手动工作阻碍决策，例如配置访问、注册服务，或移动数据以便你能看到其形状。 | Agent 在可能时单独完成，否则为人类提供精确的清单 |

`task` 是唯一一种*做*而不是决定的类型。它属于地图只是因为它解除决策的阻碍，从不因为它交付目的地的一部分。这种类型在实践中出错最多。Agents 将其理解为实现步骤，并在地图内部开始编写产品代码。

Research 是唯一一个*一个 session 一个 ticket*规则的例外。

## 常见问题

**这与 `/grill-with-docs` 有何不同？我应该从哪个开始？**

Session 数，不是项目大小。`/grill-with-docs` 是单 session 规划；wayfinder 是多 session 规划。如果你能在一次对话中容纳整个东西，grilling 更便宜更好，而 wayfinder 在这种情况下更慢更密集。社区速记是，wayfinder 只有工作无法放入单个 session 时才有意义。这是目前问得最多的 wayfinder 问题。人们不断问它，因为技能描述没有告诉你自己的任务在那条线上处于什么位置。你必须自己判断 session 数。

**当它要求"destination"时，它指的是这个 session 的结束还是一切的结束？**

整个地图的结束，不只是第一个 session。这个问题读起来有歧义，但 wayfinder 按定义是多 session 工具，因此 session 范围的答案永远没有意义。典型的目的地是要移交的 [spec](https://www.aihero.dev/ai-coding-dictionary/spec)、要在规划开始前锁定的决策、概念验证，或数据迁移等就地变更。

**地图已清除。Wayfinder 不是已经写了 spec 并制作了 tickets 吗？为什么我还需要 `/to-spec` 和 `/to-tickets`？**

不。Wayfinder 的 tickets 是决策 tickets，到地图关闭时它们都已关闭。剩下的是一张满是链接决策的地图，这不是构建计划。[to-spec](https://aihero.dev/skills-to-spec) 将这些链接决策压缩成一个文档（`/to-spec #<map_issue>`），[to-tickets](https://aihero.dev/skills-to-tickets) 将该 spec 切割成 tracer-bullet 实现 tickets。如果你直接把地图循环到 [implement](https://aihero.dev/skills-implement)，你就跳过了压缩并丢失了链接的详细信息。只有当工作量很小的时候才直接实现。有些人运行更短的流程并报告说它有效。额外的两个步骤给你一个显式的 spec，评审者或同事可以阅读，当你不是独自工作时这更重要。

**我的 agent 在 wayfinder session 中间开始编写生产代码。**

这是该技能报告最多的失败，而且该技能中确实存在一个真正的空白导致了它。你可以在地图的 **Notes** 中覆盖 wayfinder 的"plan, don't do"默认。但 agent 编写 Notes，因此约束及其豁免权位于受约束 agent 拥有的文件中。一位用户 watched an agent 在地图的 Notes 中写入"this map carries execution"。在后来的 sessions 中，agent 将该行读作许可并在实时服务器上构建。该技能没有硬性的"我是默认"停止。直到它出现之前，阅读任何你没有自己绘制的地图的 Notes，在单独的 sessions 中保持实现，并将任何看起来像构建切片的 `wayfinder:task` 视为错误分类。

**我绘制了 27 个 tickets，当我到达第十三个时，其余的不再有意义。**

这个问题逐字来自用户报告，其他人报告了相同的结果。默认情况下，wayfinder 进行全面规划。当后面的 tickets 建立在早期 tickets  invalidated 的假设上时，地图落入批评者指责该技能的 waterfall 陷阱。两件事有帮助。首先，将地图范围限制为有界的目的地，而不是整个产品。用户报告说，范围限定为一个已定义 epic 的地图比一个 sprawling "implement V1" 表现更好。目标是发布小增量，而不是计划非常大的东西。其次，积极 [prototype](https://www.aihero.dev/ai-coding-dictionary/prototyping)。路线保持最新，因为便宜的具体 artifacts 在实现依赖它们之前暴露了不确定性。Wayfinder 是"prototypemaxxing"，不是"planmaxxing"。

**我可以同时处理多个 tickets 吗？**

Frontier 向你显示可以取哪些 tickets，而 blocking edges 使并行工作在理论上安全。在实践中，一次一个 ticket 是更安全的默认值。如果你同时处理两个 grilling tickets，一个 session 可以问你刚刚在另一个中回答过的问题，因为 sessions 不共享 [context](https://www.aihero.dev/ai-coding-dictionary/context)。Prototype tickets 也有一个已知的空白。一位用户报告 agent 构建了三个 UI 变体，自己选了一个，并关闭了 ticket。那个选择是你的，而技能还没有足够清楚地说明这一点。如果你确实要并行运行 tickets，请先自己审查依赖图。

**我必须使用 GitHub Issues 吗？**

不。任何 issue tracker 都有效。GitHub 有最好的支持，因为它的原生 sub-issues 和 blocking relationships 使 frontier 无需打开地图即可见。人们也使用 GitLab、Linear、Jira 和本地 markdown。有两个注意事项。在没有原生 blocking 的 tracker 上，wayfinder 从文本中推断依赖图，你必须手动纠正它。本地 markdown 将 artifacts 放入你的 repo，这不推荐，因为 repo 中存储的东西往往会意外持久化。开源维护者遇到相反的问题（公共 trackers 中充斥着 agent 生成的规划 tickets），因此经常选择本地 markdown。

** grilling 令人筋疲力尽。每个问题都是三段长。**

这是关于 wayfinder 最尖锐的开放投诉，而且还没有人修复它。一位用户这样分解：冗长本身导致决策疲劳，而且长度隐藏了*为什么* agent 会问这个问题，所以你在地图增长时失去了从决策到决策的链条。冗长看起来更像是当前 [models](https://www.aihero.dev/ai-coding-dictionary/model) 的属性，而不是技能本身。用户尝试两种缓解措施：较低的 [reasoning effort](https://www.aihero.dev/ai-coding-dictionary/effort)，以及你全局的 `CLAUDE.md` 中的纯语言指令。无论如何都要在这里努力思考。Wayfinder 要求你进行大量思考，这主要是它的目的，而不是缺陷。

**一个我已经关闭的决策被证明是错误的。我是否编辑旧 ticket 还是制作一个新的？**

没有官方指导，而且 agent 的默认做法没有帮助。它倾向于围绕坏决策进行设计而不是挑战它，所以你必须自己引导它。有效的方法是直接告诉 wayfinder 什么发生了变化。然后它会更新地图，修订受影响的 tickets，并在已关闭的 tickets 上评论。你可以从地图中间的范围变化中恢复。但如果你*设计*了一张要改变的地图，那就是范围错误的信号。

**`decision-mapping` 去哪儿了？**

就是这个技能。v1.1 将它重命名为 `wayfinder`，你调用它为 `/wayfinder"。"Decision map" 是行话，而且它也不准确，因为四种 ticket 类型中只有一种是决策本身。新名称给了技能一个一致的词汇（destination、fog of war、frontier、the map），而不是在上面发明的术语。单位保留了"decision"这个词：wayfinder ticket 是**决策 ticket**，这样人们就不会将其理解为实现 ticket。

## 正常工作的标志

- 在任何 ticket 存在之前，目的地已被写下并商定。
- 每个开放的 ticket 读起来像一个问题。任何读起来像"build the X"的 ticket 要么是错误分类的，要么属于地图下游。
- 你可以查看你的 tracker 并看到哪些 tickets 可以取，而无需打开地图，因为原生 blocking 显示了 frontier。
- 一个 session 解决一个 ticket，将答案作为解决评论发布，关闭它，并在地图的 *Decisions so far* 中添加一行。然后它停止。
- **Not yet specified** 随着时间的推移而缩小。当雾升级为 ticket 时，它离开该部分，不会同时出现在两个地方。
- 当开口的 breadth-first grill 根本找不到雾时，技能停止并告诉你工作量小到可以跳过地图。
- 完成地图的 session 指向 spec，而不是 pull request。

## 它在何处适用

`wayfinder` 是一个**情境化上匝道**，不是默认起点。大多数工作仍然从 grill-led idea → ship 链开始。当你有一个 session 装不下的想法时使用它。它在 [to-spec](https://aihero.dev/skills-to-spec) 处重新加入该链，因为清除的地图移交而不构建。

大部分工作发生在 wayfinder 调度的其他技能中。[grilling](https://www.aihero.dev/skills-grilling) 和 [domain-modeling](https://aihero.dev/skills-domain-modeling) 解决默认 ticket 类型，[prototype](https://aihero.dev/skills-prototype) 解决讨论无法解决的 tickets，[research](https://aihero.dev/skills-research) 作为 subagent 运行，因此它的阅读不会进入你的 session。[handoff](https://aihero.dev/skills-handoff) 在内外移动工作：从变得太大的对话进入地图，以及当 side quest 在 session 中间出现时从地图出去。对于其他任何事情，[ask-matt](https://aihero.dev/skills-ask-matt) 会在整个集合中为你指引。

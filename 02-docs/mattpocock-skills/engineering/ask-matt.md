## 作用

`ask-matt` 是本仓库中技能的路由器。你描述自己当前的情况（一个无法开始的想法、一堆传入的 bug 报告、一个运行时间过长的[会话](https://www.aihero.dev/ai-coding-dictionary/session)），它会指出适合的技能或技能序列，以及该序列中需要人工决策的位置。

它推荐后就停止。不会追问、不会写[规格说明](https://www.aihero.dev/ai-coding-dictionary/spec)、不会打开文件或启动它刚刚命名的技能；你得到的是下一步应该输入的内容，然后你自己输入。它也是一个手写的技能地图，而不是对你已安装技能的扫描，因此它不会路由到你自己的技能或其他作者的。

## 何时使用

你通过输入 `/ask-matt` 来调用；代理不会自动调用它。

| 你的情况 | 路由器返回的内容 |
| --- | --- |
| 有一个想法，但不知道从何开始 | 主流程的起点，以及构建是否小到可以跳过规格说明 |
| 来自其他人的 bug 和请求 | [分类](https://aihero.dev/skills-triage)入口，以及为什么你自己生成的[工单](https://www.aihero.dev/ai-coding-dictionary/ticket)不属于此处 |
| 两个看起来可互换的技能 | 它们之间的界限，通常是一个具体的测试而非品味问题。[grill-me](https://aihero.dev/skills-grill-me) 或 [grill-with-docs](https://aihero.dev/skills-grill-with-docs) 取决于你是否在工作目录中；[grill-with-docs](https://aihero.dev/skills-grill-with-docs) 或 [wayfinder](https://aihero.dev/skills-wayfinder) 取决于工作是否适合一个会话 |
| 一个漫长的会话以及关于[上下文](https://www.aihero.dev/ai-coding-dictionary/context)的决策 | 在阶段边界五个选项的有序树 |
| 一个你已经选择的技能 | 没什么有用的。直接调用该技能。 |

## 前置条件

路由器命名技能；它不安装它们。它指向的所有内容都必须已安装才能执行推荐，而且它只知道本仓库中已提升的技能。

依赖于追踪器的路由（分类、`to-spec`、`to-tickets`、`implement`）假设 [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) 已在仓库中配置了问题追踪器。即使在此之前，路由器也会推荐它们。

## 流程，不是技能

该技能的先导词是**流程**，一条*穿过*技能的路径，而不是单个技能。当你描述自己的情况时，路由器将你放在流程中的某一步。这与"这是匹配你关键词的技能"不同。有五种类型的路由，技能本身完整描述了它们：

- **主流程**，从想法到交付。审问、规格说明、工单、实现（一次一个，或与 [implement-spec](https://aihero.dev/skills-implement-spec) 并行处理整个任务图）、审查，然后[回顾](https://aihero.dev/skills-retro)，将构建中学到的东西反馈到代理的环境中。它有两个分支。一个是原型绕道，当一个问题需要可运行的代码来解决时。另一个是规格说明与工单的分割，只有当构建跨越多个会话时才值得其成本。
- **入口匝道**，适用于生成工作然后合并到主流程的情况：传入的 bug 报告、某些损坏的内容，或者一个过于模糊且太大而无法在一个会话中完成的工作。
- **代码库健康**，维护而非功能工作。[improve-codebase-architecture](https://aihero.dev/skills-improve-codebase-architecture) 调查代码以寻找深化机会，每个发现都会作为一个想法重新进入主流程。
- **独立技能**，它们位于每个流程之外，单独使用：原型、问卷、研究运行。
- **底层词汇层**，当问题出在词汇而非流程时，其他技能引用的两个参考资料。

## 阶段边界

该技能的另一个关键概念是**阶段边界**。阶段是会话内的一整块工作（[审问](https://www.aihero.dev/ai-coding-dictionary/grilling)、实现、QA），它们之间的边界是唯一适合问"这个上下文怎么处理？"的地方。阶段中间没有可决策的：继续，或将剩余部分分成[子代理](https://www.aihero.dev/ai-coding-dictionary/subagent)。

| 选项 | 何时选择 |
| --- | --- |
| **继续** | 下一阶段需要这一阶段的完整内容，或者你还有[智能区域](https://www.aihero.dev/ai-coding-dictionary/smart-zone)剩余。这是唯一保持会话作为[原始来源](https://www.aihero.dev/ai-coding-dictionary/primary-source)的操作，因此先排除它 |
| **`/clear`** | 背后的所有内容都是一次性的。最便宜的选项，但如果你错了就无法撤销 |
| **[handoff](https://aihero.dev/skills-handoff)** | 某些东西必须传递：一个新的[工具链](https://www.aihero.dev/ai-coding-dictionary/harness)、一个新目录、一位同事、一个阶段中期分叉的副任务 |
| **子代理** | 任务范围足够明确，可以在你[离开键盘](https://www.aihero.dev/ai-coding-dictionary/afk)时运行 |
| **`/compact`** | 以上都不是。它是默认值，树经常在此结束 |

人们经常搞错其中两个选项，这就是为什么路由器给出顺序而不仅仅是列表。`/handoff` 看起来像是在上下文窗口之间移动的通用方式，但它不是。它给你的只是可移植性。`/compact` 是树中的最后一个选项，而不是第一个，因为上面四个选项中的每一个都更便宜或更精确。

## 常见问题

**不是应该有一个按正确顺序排列的技能列表吗？**

人们一直在 README 中要求一个。这个技能就是那个列表。静态表格会显示 `wayfinder → to-spec → to-tickets → implement → code-review → retro`，并且对大多数情况来说都是错的。重要的部分是分支：是否有代码库、构建是否跨越会话、能否通过交谈解决这个问题。代价是路由器是手动维护的，因此它落后于仓库。`/grilling` 在路由器命名它之前就已经上线了。

**它告诉我有一半的技能没有安装。**

这是一个已知 bug，且尚未修复。路由器路由的大多数技能都设置了 `disable-model-execution: true`，这意味着工具链会将它们从注入代理上下文的技能列表中排除。代理将该列表视为穷尽的，并报告它们缺失。在一个报告的会话中，它声明整个规格说明与工单流程不存在，并重新路由到原始的 `/grilling` 和 `/tdd`。插件的 27 个技能中有 16 个带有此标志，因此这是常见情况而非边缘情况。它们已安装。直接输入斜杠命令，或检查 `.claude-plugin/plugin.json`，它是关于存在什么的权威。

**它描述了一个技能的行为，但该技能不这样做。**

这也是一个真实的 bug，也尚未修复。路由器从它自己对每个技能的一行摘要中回答，而不是从技能本身。一份详细报告在一个会话中追踪了三个实例，包括仅根据摘要"将线程变成规格说明"建议跳过[to-spec](https://aihero.dev/skills-to-spec)。路由器从未打开 `to-spec/SKILL.md`。在每种情况下，它只有在用户反对后才进行验证，从未主动验证。在那里跳过 `to-spec` 消耗了一个真实的接缝检查，并且出来的工单低估了工作量。当路由器陈述关于另一个技能的内容且你将据此行动时，要求它先打开该 `SKILL.md`。同样适用于地图未涵盖的问题，例如是否使用[计划模式](https://www.aihero.dev/ai-coding-dictionary/agent-mode)：该答案是[模型](https://www.aihero.dev/ai-coding-dictionary/model)的推断，而不是这里写的内容。

**为什么它是散文而不是编号清单？**

这是一个合理的抱怨。一个开放的问题认为大多数路由是确定性的，叙述使其难以扫描。没有什么能阻止你要求压缩形式："直接给我序列"就能得到序列。散文承载的是条件部分：分支、预期的人工决策、步骤之间在哪里清除或压缩。平面清单恰好丢弃了这些内容。

**它能路由到我自己的技能，或其他作者的技能吗？**

不能。三个独立的提案要求一个能读取你的本地 `skills/` 目录并从已安装的内容中推荐的路由器。`ask-matt` 不是那个。它是一组技能的手动地图，对你自己编写或从其他地方安装的技能一无所知。

**它告诉我要编辑一个 SKILL.md。**

这个建议通常是对的，但编辑很少持久。有人询问如何让[implement](https://aihero.dev/skills-implement)关闭工单，被告知要在技能中添加一行，并立刻看到了问题所在。`npx skills update` 会覆盖该文件，且插件安装是只读的。将持久行为放在你自己的 `CLAUDE.md` 或 `AGENTS.md` 中，或在调用时说明。你在提示中做出的更改会在更新后保留。人们以这种方式将流程指向 Linear 而不是 GitHub，或询问哪些开放票证可以并行运行。

**它命名了一个我没有的技能，或遗漏了我有的一个。**

在假设它消失之前，先检查变更日志以了解是否有重命名。`writing-great-skills` 变成了 [writing-for-agents](https://aihero.dev/skills-writing-for-agents) 且没有别名，`to-prd` 变成了 [to-spec](https://aihero.dev/skills-to-spec)，`pathfinder` 变成了 [wayfinder](https://aihero.dev/skills-wayfinder)。有四个技能被直接退休，合并到了吸收它们的技能中：`ubiquitous-language`、`design-an-interface`、`qa` 和 `request-refactor-plan`。如果它遗漏了某个你拥有的技能，那就是路由器自身的滞后，如上所述。

## 正常工作的标志

- 它最后指出应该输入什么并停止，而不是自己开始工作。
- 它返回的路由提到了在哪里清除或压缩上下文，以及在哪里预期你进行审查，而不仅仅是一个技能名称列表。
- 当两个技能接近时，它会说哪一个以及为什么另一个对你来说是错的。
- 它关于另一个技能行为的任何声明都会在追踪中显示为它正在阅读该技能的 `SKILL.md`。
- 你在它返回的内容中认出了自己的情况，而不是最接近的通用场景。

## 它在何处适用

`ask-matt` 是一个**独立路由器**，位于整个集合之上。它从来不是链中的一个步骤。它指向每个链，其他文档页面链接回它，因此它们都不必重绘图表。从你最常降落在[grill-with-docs](https://aihero.dev/skills-grill-with-docs)，即主流程的起点，或[triage](https://aihero.dev/skills-triage)，即到达工作而非你启动的工作的入口匝道。

它是关于所描述技能的[二手来源](https://www.aihero.dev/ai-coding-dictionary/secondary-source)。当路由器与 `SKILL.md` 不一致时，`SKILL.md` 是对的。

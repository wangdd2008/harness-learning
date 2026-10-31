## 作用

`to-spec` 将你刚刚进行的对话转化为一份 **[spec](https://www.aihero.dev/ai-coding-dictionary/spec)**，并以单个 issue 的形式发布到你的 issue tracker 中。

它不会采访你。当你选择它时，决策已经做出了。因此它综合已知信息（来自线程、代码库、你的 `GLOSSARY.md` 和 ADR），不会开始新一轮提问。Spec 记录你已经做出的决策。它不是做新决策的地方。

## 何时使用

你通过输入 `/to-spec` 来调用它；[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 不会自动触发它。

在构建太大，无法在一个 agent [session](https://www.aihero.dev/ai-coding-dictionary/session) 中完成，必须拆分成多个时选择它。这就是整个触发条件：

| 你的状态 | 运行什么 |
| --- | --- |
| 你什么都还没决定 | 先用 [grill-with-docs](https://aihero.dev/skills-grill-with-docs) |
| 已决定，工作 fits 一个 [context window](https://www.aihero.dev/ai-coding-dictionary/context-window) | [implement](https://aihero.dev/skills-implement)：跳过 spec |
| 已决定，工作跨越多个 session | `/to-spec`，然后 [to-tickets](https://aihero.dev/skills-to-tickets) |
| [wayfinder](https://aihero.dev/skills-wayfinder) 地图已清除 | `/to-spec #<map_issue>` |

## 前置条件

`to-spec` 将 spec 发布为 issue，因此 [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) 必须首先为此 repo 配置 tracker 和分类标签词汇。两种 tracker 都可以：像 GitHub 这样的真实 tracker，或者 `.scratch/` 下的本地 markdown 文件，后者无需额外设置即可工作。

## Spec 是一份决策记录

Spec 存在的原因是 context window 会结束。你在 [grilling](https://www.aihero.dev/ai-coding-dictionary/grilling) 过程中确定了很多事情：解决方案的形状、你争论过的选择、以及你故意拒绝的东西。所有这些都在一个你即将清空的对话中。Spec 保留了它。

因此 spec 不验证或决定任何事情。它记录你决定的，用你自己的项目词汇，这样一个新的 session 就可以接手工作，无需你再次解释。如果 spec 声明了你从未说过的东西，那就是一个缺陷。

## Seam 先于散文

在写任何东西之前，`to-spec` 先勾勒 feature 将被测试的 **seam**，并与您确认。它优先使用现有的 seam 而不是新的，并选择尽可能高的 seam。变更的理想 seam 数量是一。

其他技能稍后使用这些商定的 seam。[tdd](https://aihero.dev/skills-tdd) 只在你提前商定的 seam 上工作。[code-review](https://aihero.dev/skills-code-review) 根据 spec 审查 diff，所以没有人同意的 seam 会显示为审查发现。这两个连接都通过本文档。这就是为什么你应该在这里认真对待 seam 对话，而不是把它留给实现阶段。

## 常见问题

**`/to-prd` 去哪儿了？**

就是这个技能，在 v1.1 中重命名。"Spec" 现在是整个过程中使用的唯一术语，旧的 `to-prd` slug 不再工作，所以请在新名称下重新安装。旧词汇被 *spec* 和 *tickets* 这对词取代。Spec 是目的地和固定它的决策。[tickets](https://www.aihero.dev/ai-coding-dictionary/ticket) 是到达那里的步骤。如果你改变方向，删除未完成的 tickets 并保留 spec。

**为什么 spec 得到 `ready-for-agent` 标签？我不想让 agent 基于它实现。**

该标签的意思是"无需进一步分类"：文档足够完整，agent 可以从中工作。它标记的是输入，而不是工单。但轮询 `ready-for-agent` 的 AFK agent 看不出这个区别。它们会尝试在一次运行中构建整个 spec，而不是选取 ticket slice。这是该技能报告最多的问题。在改变之前，在你的 AFK agent 的提示中显式排除父 spec，或者在 `/to-tickets` 运行后移除该标签。

**为什么不直接从 grilling 到 `/to-tickets` 跳过 spec？**

通常你应该这样做。Spec 只有在多 session 工作中才值得这一步。它的价值在于 tickets 是一次性的，而 spec 不是。每个 ticket 都是为一个新鲜的 context window 设计的，然后被删除或关闭，而 spec 始终是记录它们背后推理的唯一地方。在单 session 变更中，这什么都给不了你，而且你要支付额外的合成步骤，其中 [model](https://www.aihero.dev/ai-coding-dictionary/model) 可能会漂移。从 grilling 到 `/implement`。

**我刚完成一个 wayfinder 地图。我该喂它什么？**

给它主地图 issue，`/to-spec #<map_issue>`，而不是单个决策 tickets。[wayfinder](https://aihero.dev/skills-wayfinder) 产生分布在地图上的决策，而不是可交付成果。`to-spec` 将它们压缩成一个可以构建的文档。如果你直接把地图循环到 `/implement`，你就失去了那一步。

**Spec 是给我审查的，还是只给 agent 的？**

主要是给 agent 的，而且它读起来也这样：完整、密集、充满引用。阅读 seam 和 out-of-scope 部分。在这两个地方，错误的决策现在最容易被发现，而后期发现的代价最高。人们确实抱怨阅读整个东西，而且没有摘要模式。但如果 spec 让你惊讶，那 grilling 太浅了；不是 spec 太长。

**一旦 tickets 开始，我是否保持 spec 冻结，还是让 agent 重写它？**

没有什么能让它保持同步。在实践中，它是你在那一刻所知的快照，第一次实现教你一些东西时它就过时了。在工作完成后将其视为一次性的。你的 `GLOSSARY.md` 和 ADR 是设计用来持久的。如果你在实现过程中学到了应该持久的东西，把它放在那里，而不是编辑 spec。

**我的工作是一次重构或模块边界，不是 feature。模板适用吗？**

不太适用，这是一个已知的限制。模板严重依赖用户故事，而用户故事不适合架构工作。你最终会为真正关于接口和不变量的决策编写没有人要求的故事。改用 implementation-decisions 和 testing-decisions 部分。通过 [grill-with-docs](https://aihero.dev/skills-grill-with-docs) 将持久的架构决策记录为 ADR，而不是在 spec 中。

**它会检查 tracker 中的相关工作，或引用它遵循的 ADR 吗？**

两者都不会。它读取并遵循它所触及区域的 ADR，但不会链接它们。它也不会在写入前搜索 tracker 中的重叠 issues，因此 spec 可能重复某人已经提交的工作，而且没有任何警告。如果该区域很忙，请先自己搜索 tracker。

**`/to-tickets` 无法读取我的 spec：它一直截断。**

Tracker issue 可能不会完整返回一个非常大的 spec，而且没有本地副本可用。要解决这个问题，请不要在 `/to-spec` 和 `/to-tickets` 之间 [clear](https://www.aihero.dev/ai-coding-dictionary/clearing) 或 [compact](https://www.aihero.dev/ai-coding-dictionary/compaction)。在同一个窗口中运行它们，这样 `/to-tickets` 就永远不需要再次获取 spec。

## 正常工作的标志

- 它开始写作而不是问你新一轮问题。
- 它在写作前向你展示 seam，并尽可能少地提议。
- 它使用你项目的名词，而不是通用的产品管理套话。
- 你记得每一个决策。它没有为了填充部分而编造任何东西。
- Out-of-scope 部分列出了真实的东西。你拒绝的东西通常是页面上最有用的部分。

## 它在何处适用

`to-spec` 是主构建链中的一个步骤，但只在其多 session 分支上：

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

上游，[grill-with-docs](https://aihero.dev/skills-grill-with-docs) 做出该技能只记录的决策，已完成的 [wayfinder](https://aihero.dev/skills-wayfinder) 地图在此处加入链。下游，[to-tickets](https://aihero.dev/skills-to-tickets) 将 spec 切割成 tracer-bullet tickets 供 [implement](https://aihero.dev/skills-implement) 构建。当你不确定哪个技能或流程适用时，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你指引。

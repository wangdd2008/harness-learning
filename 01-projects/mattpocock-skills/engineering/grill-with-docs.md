## 作用

`grill-with-docs` 通过访谈来了解你对某个计划或设计的理解，直到你和 [agent](https://www.aihero.dev/ai-coding-dictionary/agent) 对它有了一致的理解，并在访谈过程中将词汇和艰难的决策写入你的仓库。它与 [grill-me](https://aihero.dev/skills-grill-me) 运行的是同一套访谈流程（一轮问题，等待，下一轮），只是指向了一个代码库。

它是**有状态的**（[stateful](https://www.aihero.dev/ai-coding-dictionary/stateful)）。其他所有 grilling 技能都会将 [session](https://www.aihero.dev/ai-coding-dictionary/session) 留在你的脑子里；而这个技能会将文件留在磁盘上。当一个术语被确定下来时，技能会立即将其写入 `GLOSSARY.md`，而不是在最后批量写入。当一个决策通过了三个 gate 时，技能会将其作为 ADR 写入。这就是全部的区别，也是人们在使用这个技能时遇到的大多数麻烦的根源。这些产物是真实仓库中的真实文件，所以它们可能在你期望的时候缺失，也可能在不止一个人写入的时候发生漂移。

## 何时使用

你通过输入 `/grill-with-docs` 来调用它，agent 不会自动使用它。

在变更开始时、仓库中、计划尚不清晰且事物的名称尚未确定时，就使用它。它是单 session 的工具。你需要哪个 grilling 技能取决于你面前有什么：

| 你有什么 | 使用 |
| --- | --- |
| 你根本没有在工作目录中工作 | [grill-me](https://aihero.dev/skills-grill-me) |
| 一个仓库，以及可以在一个 session 中确定的变更 | `grill-with-docs` |
| 一个 session 装不下的工作（全新构建、大型功能） | [wayfinder](https://aihero.dev/skills-wayfinder) |
| 一个完全没有领域文档的仓库，且没有特定的功能需求 | `grill-with-docs`，指向仓库本身而非某个变更 |
| 一个被他人脑中知识阻塞的决策 | [to-questionnaire](https://aihero.dev/skills-to-questionnaire) |

wayfinder 的分割取决于 session 数量：`/grill-with-docs` 用于单 session 规划，`/wayfinder` 用于多 session 规划。

## 前置条件

这个技能会写入你的仓库，所以你需要在一个安全的地方运行。已确定的术语会写入根目录的 `GLOSSARY.md`，或者如果根目录的 `GLOSSARY-MAP.md` 标记了仓库为多上下文，则写入相关上下文的 `GLOSSARY.md`。决策会写入 `docs/adr/`。技能只会在需要时创建这些文件。在第一个术语或决策确定之前，什么都不存在，所以你不需要提前设置。

它还需要另外两个技能，因为它自己的 `SKILL.md` 只有一行，是委托给它们的。[grilling](https://aihero.dev/skills-grilling) 提供访谈，[domain-modeling](https://aihero.dev/skills-domain-modeling) 提供写入。单独安装 `grill-with-docs` 会得到一个无法工作的技能。

## 记录轨迹

一次 session 会产生三样东西，它们的重要性并不相等。

| 什么被确定了 | 它落在哪里 |
| --- | --- |
| 术语：项目自己对某个事物的称呼 | `GLOSSARY.md`，内联，确定的那一刻 |
| 一个难以逆转、没有上下文会让人惊讶、且涉及真实权衡的决策 | `docs/adr/` 下的 ADR |
| 你决定的其他所有事情 | 对话中， nowhere else |

第三行是最容易让人困惑的。`GLOSSARY.md` 只是一个词汇表。它不包含实现细节、没有 [spec](https://www.aihero.dev/ai-coding-dictionary/spec)，也没有草稿笔记。ADR 需要同时满足三个条件，所以大多数决策都不符合，大多数 session 都不会产生 ADR。一个 session 产生了一个更清晰的词汇表和零个 ADR，是设计如此，但这意味着你们达成的大多数共识只存在于你们达成它的 [context window](https://www.aihero.dev/ai-coding-dictionary/context-window) 中。与其 [clearing](https://www.aihero.dev/ai-coding-dictionary/clearing)，不如将同一次对话交给 [to-spec](https://aihero.dev/skills-to-spec)。

词汇表是主要产出。这个技能构建领域语言：项目自己的词汇，一次确定，所以你、agent 和你的同事不需要再次确定。不是每个人都同意这能改善 agent 的表现。最有力的反对意见是，一个术语和它的普通英文解释从 [model](https://www.aihero.dev/ai-coding-dictionary/model) 那里得到的结果是一样的，词汇表主要是缩短共享它的人之间的沟通。按照这种观点，词汇表仍然有价值，但价值归于人类。

## 常见问题

**我应该用这个还是 `/wayfinder`？**
范围决定。任何可以在一个 session 中确定的事情都用这个；当工作太大，装不进一个 session 时，使用 [wayfinder](https://aihero.dev/skills-wayfinder)。wayfinder 更慢、更密集，在一个范围明确的功能上使用它是常见的错误。它不能替代这个技能，它可以为这个技能中适合的部分启动 grilling session。

**它运行了，但没有出现 `GLOSSARY.md` 和 ADR。**
有两个已知原因。第一个是没有任何东西符合条件。ADR 需要同时满足三个 gate，而一次关于没有新词汇的变更的 session 就没有东西可写。第二个是真正的 bug。当技能在另一个编排层内部运行时（spec-driven-development 包装器、多 agent 框架、一个将它作为别人 pipeline 中的步骤调用的规则），用户报告文件写入部分静默地没有发生，而访谈仍然运行。这个 bug 已记录但尚未修复。如果你处于那种设置中，在信任 session 的输出之前，检查工作目录。

**它一次性问了所有问题，没有建议，也没有提到 `GLOSSARY.md`。**
这是技能没有加载它的两个依赖项。因为 `SKILL.md` 是一行委托，一个没有加载 [grilling](https://aihero.dev/skills-grilling) 和 [domain-modeling](https://www.aihero.dev/skills-domain-modeling) 的 agent 会猜测 grilling 的含义，你会得到所有问题一次性抛出，没有结构。部分加载更混乱。`grilling` 加载了，`domain-modeling` 没有，你会得到一个好的访谈但没有记录。发生的频率取决于 model 和 [effort](https://www.aihero.dev/ai-coding-dictionary/effort) 级别，这是这个技能报告最多的问题。如果你怀疑，直接问 agent 它加载了哪些技能。

**我其他的决策都去哪了？**
只存在于对话中。这是关于这个技能最严重的公开抱怨。词汇表不是 spec，大多数答案都赚不到 ADR，也没有记录将每个确定的答案与 spec、ticket 和测试关联起来。后续步骤会将精确的答案（排序保证、负面需求、数字默认值）软化成更弱的散文，结果可能看起来完整，但缺少了你决定的东西。目前，保留 session 并直接将其输入 [to-spec](https://aihero.dev/skills-to-spec)。然后对照你自己的答案重新阅读 spec，而不是假设它捕捉到了它们。

**我可以指向一个完全没有文档的现有仓库吗？**
可以。这是一个完全没有 ADR、没有领域语言、没有设计原则的仓库的正确技能：调用它并说"帮我记录我的仓库"。用户经常将其与 [improve-codebase-architecture](https://aihero.dev/skills-improve-codebase-architecture) 配对使用，以构建或修复 `GLOSSARY.md`。准备好引导它。它会读取代码并询问你关于它发现的东西，你决定代码中已有的哪些词是正确的。

**session 结束时我该做什么？**
技能的结束消息通常是开放式的，这是一个已知问题。在主流程中，答案是 [to-spec](https://aihero.dev/skills-to-spec)，在同一个对话中。如果变更小到可以直接构建，直接跳到 [implement](https://aihero.dev/skills-implement)。

**为什么叫这个名字？**
没有人对这个名字满意。有一个公开建议将其重命名为 `grill-domain-model`，这更准确地描述了行为。但没有任何进展。如果重命名真的落地，文档页面会随之移动，URL 也会改变。

## 正常工作的标志

- `GLOSSARY.md` 在 session 过程中逐个术语地变化，而不是在最后一次性出现。
- 词汇表读起来是纯词汇（你自己的词汇，定义紧凑），不包含实现细节或类似 spec 的散文。
- 代码库能回答的问题，由代码库回答，而不是问你。
- 你很少或没有 ADR，而且你得到的 ADR 是你不愿意再争论一次的决策。
- 它会因为你现有的词汇表以不同方式定义而挑战你使用的词。

## 它在何处适用

`grill-with-docs` 是主构建链的起点：

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

它在任何东西被写成 spec 之前。它产生共享理解和确定的词汇，[to-spec](https://aihero.dev/skills-to-spec) 随后综合这些而不需要再次访谈你。它的近邻是 [grill-me](https://aihero.dev/skills-grill-me)（同样的访谈，没有仓库和文件）和 [domain-modeling](https://www.aihero.dev/skills-domain-modeling)（它驱动的词汇表和 ADR 规范）；两者都使用 [grilling](https://aihero.dev/skills-grilling) 原语进行访谈。在它上游，[wayfinder](https://aihero.dev/skills-wayfinder) 规划太大而放不进一个 session 的工作，并可以将地图的一部分交回给它。当你不确定哪个技能或流程适合时，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你路由。

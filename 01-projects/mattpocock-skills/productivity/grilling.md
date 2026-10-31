## 作用

`grilling` 是在任何人根据计划、决策或想法行动之前对其进行压力测试的 interview loop。它将主题映射为**设计树**：每个决策分支出依赖于它的决策，并逐分支采访你，直到没有假设保持未陈述。

它不是一次问一个 question，也不是一次性问所有 question。每个**轮次**询问完整的**前沿**：所有先决条件已确定的决策，仅此而已。如果两个问题中一个依赖于另一个，它们永远不会共享一轮；依赖于尚未回答的答案的问题属于后面的轮次。你的答案确定了决策，前沿向外移动，下一轮询问被解除阻挡的内容。十三个问题通常在大约三轮中落地，而不是十三轮。

## 何时使用

输入 `/grilling`，或者当任务适合时 [agent](https://www.aihero.dev/ai-coding-dictionary/agent) 会自动触发。它是 grilling 族中唯一 model-invoked 的 [skill](https://www.aihero.dev/ai-coding-dictionary/skill)，因此你很少输入它。通常你输入的技能会为你运行它。

直接输入 `/grilling` 会让你得到纯 interview，别无其他。当你想要的不止这些时：

| 你有什么 | 选择 |
| --- | --- |
| 你不在工作目录中 | [grill-me](https://aihero.dev/skills-grill-me)：相同的 [session](https://www.aihero.dev/ai-coding-dictionary/session)，在一个 agent 永远不会自行触发的名称下 |
| 你在工作目录中 | [grill-with-docs](https://aihero.dev/skills-grill-with-docs)：相同的 session，并且它边走边写 `GLOSSARY.md` 和 ADR |
| 一个 session 装不下的工作量 | [wayfinder](https://www.aihero.dev/skills-wayfinder)：它绘制地图并在决策 tickets 内运行 grilling |
| 讨论无法解决的一个问题：它应该长什么样或感觉如何 | [prototype](https://www.aihero.dev/skills-prototype)：构建一次性版本，然后回来 |
| 你自己的技能需要一个 interview | 从它调用 `/grilling`，而不是写另一个 interview |

## 轮次、前沿和谁决定

该技能建立在三个理念之上。

**设计树**是主题的模型：决策上挂着决策。**前沿**是先决条件都已确定的所有决策集合：agent 目前唯一能问的 questions。一个**轮次**是完整的前沿，全部问完，全部答完。

在轮次内部，每个 question 都有固定格式：编号并 titled 在 `❓` 后面，然后是正文，然后是 agent 单独一行放在 `➡️` 上的推荐答案。这种格式让你可以按编号回答一轮（"1 yes, 2 the second option, 3 no, here's why"），而不是引用 questions 回来。这种格式有一个已知问题。推荐有时会反对 question 的措辞，所以同意推荐意味着对 question 回答"no"。当这种情况发生时，回答推荐并说明。

设计的另一半是事实与决策的分离。事实是该技能自己的工作。当前沿 question 需要 [environment](https://www.aihero.dev/ai-coding-dictionary/environment) 可以解决的东西时，agent 派遣 [sub-agent](https://www.aihero.dev/ai-coding-dictionary/subagent) 去查明，而不是问你。轮次不等待该 research；只有依赖于它的 questions 才等待。决策是你的，agent 必须等待它们。运行 `grilling` 的 agent 回答自己的决策已经破坏了该技能。当前沿为空时 session 结束。然后 agent 等待你确认共享理解，然后再根据你同意的内容采取行动。

前沿有一个限制。Agent 通过判断来选择它；它不是从图中计算出来的。所以它可以把两个 question 放在一轮中，后来发现一个答案应该已经改变了另一个。唯一的 guard 是告诉它。这在下一轮中重新打开受影响的分支。

## 什么在这里，什么在 wrappers 中

本页涵盖机制。Wrapper 技能的页面回答人们最常问的问题。

| Question | 在哪里回答 |
| --- | --- |
| 树、前沿、轮次、question 格式、事实 vs 决策 | 这里 |
| Session 应该运行多久、你无法通过讨论回答的 question 怎么办、如何避免点头 | [grill-me](https://aihero.dev/skills-grill-me) |
| 什么写入 `GLOSSARY.md`、什么成为 ADR | [grill-with-docs](https://aihero.dev/skills-grill-with-docs) |

## 常见问题

**我可以一次回到一个 question 吗？**

可以，而且很大一部分用户这样做。将这个添加到你的全局 `CLAUDE.md`：

```
When grilling, ask one question at a time.
```

不是每个人都喜欢基于轮的默认值。阅读缓慢的人、使用第二语言的人，或使用顺序格式帮助他们集中注意力的用户报告说，一次一个 question 对他们更有效。退出是受支持的设置，不是变通方法。

**`/batch-grill-me` 去哪儿了？**

进入这个技能。基于轮的 questioning 曾短暂地作为一个单独的技能发布，然后移入 `grilling` 本身，因此所有建立在原语之上的东西（`grill-me`、`grill-with-docs`、`triage`、`wayfinder`）都一次性得到了它。没有 `batch-grill-me` 可安装，也没有单独的顺序技能；上面的 `CLAUDE.md` 行是回到一次一个的方法。

**一次问完整轮一定 lose 了我早期答案会引发的问题。不是吗？**

这是关于轮次最常见的反对意见，而前沿回答了它。一轮只包含不依赖于彼此的 questions，所以一轮中的任何答案都不能使同一轮中的另一个 question 无效。你的答案仍然改变后面出现的内容，因为 agent 从零开始计算每个下一轮。你确实会 lose 一些东西，但比"所有 questions 一次性"暗示的要少。见上面的前沿限制。

**它用尽了 questions 并开始构建。**

确认门就是为此存在的。该技能在你确认共享理解时才完成，而不是在前沿为空时。较弱和更快的 [models](https://www.aihero.dev/ai-coding-dictionary/model) 仍然会跳过门。用户报告这在低 effort 或非前沿 model 上最常见，它们将"interview until shared understanding"折叠成几个问题和一个 outline。如果你的这样做，可靠的修复是你自己的 `AGENTS.md` 或 `CLAUDE.md` 中的一行，告诉 agent 没有许可不要实现。

**它回答了自己的 questions 而不是问我。**

那是一个 bug，也是该技能文本将事实与决策分开的原因。它最常发生在另一个技能运行 `grilling` 来解决 ticket 时，agent 将该任务作为继续前进的许可。同样的约束也是为什么没有异步模式的原因。人们要求一个读取 GitHub issue 并发布一个综合决策 memo 的变体，那是一种不同的技能，因为没有人回答的 grilling session 产生的是 agent 的意见而不是你的。

**我可以限制 question 数量吗？**

不行，而且上限是故意超出范围的。有些计划需要三个 questions，有些需要五十个；固定的 ceiling 要么截断困难的情况，要么在容易的情况下感觉武断。预期的控制是简单语言。告诉它结束，或者停下来接受计划目前的状态。如果 session 运行得非常长，原因通常是范围太大了；拆分工作并 grill 各个部分。

**我单独安装了 `grill-me` 但什么都没发生。**

`grill-me` 是一个只有一行的技能，其整个主体是"运行一个 `/grilling` session"，因此它也需要安装这个技能。`grill-with-docs` 也是如此，它还需要 [domain-modeling](https://aihero.dev/skills-domain-modeling)。安装整个套装可以避免问题；选择性安装意味着也要安装原语。

**`grill-with-docs` 运行了，但它从未加载 `grilling`。**

这是一个真实的 bug，仍未修复，用户在 [harnesses](https://www.aihero.dev/ai-coding-dictionary/harness) 和 model 中都报告了它。一个命名另一个 skill 的 skill 不会可靠地导致该 skill 加载，而 `grill-with-docs` 命名了两个。标志是一个 session 问所有东西，没有推荐。这意味着 model 正在即兴发挥 interview 而不是运行这个。直接问 agent 是否加载了 `grilling` 和 `domain-modeling` 通常会恢复它。

## 正常工作的标志

- 一轮以编号列表的形式到达，每个 question 及其推荐分别放在 `➡️` 行上，你可以按编号回答整轮。
- 一轮中没有任何东西需要先回答同一轮中的另一个 question。
- 后面的轮次询问第一轮无法询问的东西。
- 它去查找事实（读取文件、派遣 sub-agent），而不是问你一些它可以找到的东西。
- 在后台运行的 research 不会停滞轮次；只有依赖于它的 questions 才等待。
- 它在最后停下来，要求你确认共享理解，而不是开始工作。
- Question 数量保持高，而轮次数量保持低。

## 它在何处适用

`grilling` 是一个**原语**，不是你调度的步骤：interview 技术的单一事实来源，保存在一个地方，因此每个需要 interview 的技能都会去找它，而不是发明一个。[grill-me](https://aihero.dev/skills-grill-me) 和 [grill-with-docs](https://aihero.dev/skills-grill-with-docs) 是它的两个用户调用的前门，而 `grill-with-docs` 是主构建链开始的地方，在 [to-spec](https://aihero.dev/skills-to-spec) 之前。[wayfinder](https://aihero.dev/skills-wayfinder) 运行它来解决决策 tickets，[triage](https://aihero.dev/skills-triage) 来将模糊的报告 grill 成可工作的，而 [improve-codebase-architecture](https://aihero.dev/skills-improve-codebase-architecture) 在你选择了要深化的候选后遍历树。当你不确定哪个入口点适用时，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你指引。

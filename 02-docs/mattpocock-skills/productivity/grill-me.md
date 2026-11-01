## 作用

`grill-me` 获取一个**松散的想法**，并采访你，直到你能承诺它。你不需要一个制定好的计划来开始，因为 [session](https://www.aihero.dev/ai-coding-dictionary/session) 的存在就是为了生成一个。它以**轮次**提问。每一轮都是完整的**前沿**：即所有先决条件已确定的question。因此它从不问你一个依赖于它尚未听到的答案的question。

它是 **[stateless](https://www.aihero.dev/ai-coding-dictionary/stateless)** 的。它不写文件，也不留下工作空间。唯一的结果是你脑海中更清晰的想法版本。

## 何时使用

你通过输入 `/grill-me` 来调用它；[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 不会自动触发它。在**全新的对话**中启动它，而不是在你已经让 agent 写好计划的基础上。

一旦你有一个值得认真对待的想法（一个功能、一个产品方向、一个业务决策、一篇文章），并且远在你弄清楚它涉及什么之前，就选择它。模糊不是等待的理由，因为 session 的存在就是为了消除它。如果你已经能精确地指定这个东西，你就不需要 grill 它了。

你想要三个 grilling 技能中的哪一个取决于你面前有什么：

- **任何东西，任何地方。** 使用 `grill-me`。它不需要 repo，也不写文件，主题不一定是代码。
- **需要对齐的代码库。** 使用 [grill-with-docs](https://aihero.dev/skills-grill-with-docs)。它是相同的 interview，但 [stateful](https://www.aihero.dev/ai-coding-dictionary/stateful)：它读取你的代码，并将学到的东西保存在 `GLOSSARY.md` 和 ADR 中。
- **太大，无法放入一个 session。** 使用 [wayfinder](https://aihero.dev/skills-wayfinder)。它将工作量绘制为地图，并在其中运行 grilling sessions。

关闭 [plan mode](https://www.aihero.dev/ai-coding-dictionary/agent-mode)。Plan mode 让 agent 急于生成计划，而你想让它继续提问。

## 这是对话，不是 interview

技能提问，但**你**拥有范围。人们经常忽略这一点。这是将想法转化为决策的 session 与产生自信废话的 session 之间的区别。

失败模式是**被动性**：对四十个问题回答"同意，同意，同意"，然后带着 agent 写的、你点头同意的计划出来。它感觉有成效，因为它很长。但你什么都没决定，结果看起来比实际更确定。

主动意味着掌舵。反驳一个不够详细的问题。说范围在漂移。回答"我不知道"并认真地说。这个技能帮助工程师，而不是取代工程师。结果的质量取决于你的回答质量，而不是问题数量。

相反的错误也是真实的，但更少见：在 interview 中待得太久，永远到不了代码。

## 可 grill 和不可 grill

有些问题可以通过讨论回答。有些不能，再多的 grilling 也无法让你到达那里。

"One long form or three pages?" 和 "how should this interaction feel?" 是**不可 grill 的**。在回答之前，你需要一些东西来 react。当你遇到一个时，停止 grilling。用 [prototype](https://aihero.dev/skills-prototype) 构建一次性的版本，看看它，然后回来用一句话回答。

当你尝试通过讨论一个不可 grill 的问题时，session 会变得太长。Agent 不断重新措辞，你不断猜测，范围随着不确定性增长。

## 正常工作的标志

- 你不同意某件事。没有你的反驳的 session 是你不需要的 session。
- Questions 在几轮中出现，而不是一次一个很长时间，而且后面的轮次明显建立在你之前说的基础上。
- 你最终到达了你没想到的地方，因为一个 question 展示了一个你一直在做但没注意到的决策。
- 最后，你可以向不在场的人辩护每个选择。

## 常见问题

**我应该期望多少个 question，我怎么知道它什么时候结束？**

数轮次，而不是 questions。四十六个问题分布在四轮中是一个普通的 session。它在前沿为空时结束：它访问了每个分支，没有什么作为未陈述的假设留下。

**它问了我两百个问题。出了什么问题？**

通常范围太大了。要求 agent 先把工作分成更小的部分，然后 grill 每个部分。非常长的 session 也会漂移到 **[dumb zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)**，其中 [context window](https://www.aihero.dev/ai-coding-dictionary/context-window) 足够满，questions 变得更糟。

**我可以一次回到一个 question 吗？**

可以。将这个添加到你的全局 `CLAUDE.md`：

```
When grilling, ask one question at a time.
```

**如果我 genuinely 不知道答案怎么办？**

说出来。"I don't know" 是一个真实的答案，你无法回答的 question 通常是 prototype 而不是猜测的信号。

**我在写 spec 之前是否启动一个新的 session？**

不。Session 的价值在于你刚刚建立的 [context](https://www.aihero.dev/ai-coding-dictionary/context)。直接将同一对话交给 [to-spec](https://aihero.dev/skills-to-spec)。

**Model 重要吗？**

比大多数技能更重要。Grilling 依赖于 [model](https://www.aihero.dev/ai-coding-dictionary/model) 对系统如何断裂的了解，所以使用你最好的那个。实现主要遵循 context，所以更便宜的 model 在那里没问题。

## 它在何处适用

`grill-me` 是一个**独立的、你可以在任何地方对任何东西运行的工具**。因为它是 stateless 的，所以它是可移植的。它不需要 repo、工作空间或设置，也不假设想法是关于软件的。人们用它来做业务决策、写作和接下来做什么：任何他们无法自己清晰思考的事情。

可移植性是与 [grill-with-docs](https://aihero.dev/skills-grill-with-docs) 的唯一区别。该技能运行相同的 interview，但读取代码库进行对齐，并将学到的东西记录为 `GLOSSARY.md` 和 ADR。两者都使用底层的 [grilling](https://www.aihero.dev/skills-grilling) 技能。`grill-me` 是用户调用的入口点，不保留状态。

如果你 grill 的东西确实是软件，你可以将同一对话交给 [to-spec](https://aihero.dev/skills-to-spec)，然后继续进入构建流程（一个选项，而不是该技能的重点）。当你不确定哪个流程适用时，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你指引。

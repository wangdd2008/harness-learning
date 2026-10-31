## 作用

你输入 `wait-what` 当你不理解一条消息时。[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 然后 re-pitches 它刚才说的话。它添加你缺失的 context，用 plain English 写作，并使用你项目的 `GLOSSARY.md` 中的词汇。

该技能只有三行。这是设计，不是未完成的草稿。对抗冗长的技能通常会失败，因为它们变得太长。一个四百行的简洁技能仍然让 [model](https://www.aihero.dev/ai-coding-dictionary/model) 冗长，因为 model 复制技能的长度，而不是它的请求。这个技能有一个精确的 leading word，别无其他。

## 何时使用

你通过输入 `/wait-what` 来调用它。Agent 不会自动触发它，而且它不应该。只有你知道你什么时候跟不上了。

当你注意到你在 skimming 时立即使用它。例如，agent 开始使用它发明的术语，在一个句子中放入五个缩写，或解释一个你从未见过的前提的决策。它修复你已经处于的 conversation。要阻止术语出现，使用 [grill-with-docs](https://aihero.dev/skills-grill-with-docs)，它在前面建立共享语言。

## 名字就是机制

Leading word 是 **wait**。"Be concise" 是关于 agent 输出的指令，model 通过删减单词来遵守它，让你进一步 lose。**Wait** 是关于 *你* 的状态。它说你在这里 stopped understanding。听到 "be brief" 的 agent 写剪辑的片段。听到 "wait, you lost me" 的 agent 退后并解释。

这个区别就是整个技能。每个流行的冗长修复都命名 *output*：`/tldr`、`/no-fluff`、`/talk-normal`。Model 过度纠正为剪辑的片段，它们更短，但一点也不更清楚。命名 *listener* 要求两半同时出现：更少的单词 **和** 你缺失的 context。

该技能说 re-pitch **that**，不是 "that last message"。失去你的通常比一段更大，因此 agent 决定回溯多远。

## 它插入你已经拥有的语言

正文重用你全局 `CLAUDE.md` 和你项目的 `GLOSSARY.md` 中已有的 leading words。ASD-STE100 Simplified Technical English 设定 register。Ubiquitous language 提供 nouns。该技能、`CLAUDE.md` 和 `GLOSSARY.md` 使用相同的 [tokens](https://www.aihero.dev/ai-coding-dictionary/token)，因此调用它不是一个新的指令。它提醒 agent 它已经同意的一个。

如果你没有 `GLOSSARY.md`（也没有指向 `GLOSSARY-MAP.md` 的上下文），该技能仍然工作。你只 lose 领域词汇部分。

## 正常工作的标志

- Re-pitch 是**更短更清楚**，不是更短更生硬。
- 它添加你缺失的前提，而不是只删除单词。
- Project nouns 替代发明的术语。你 `GLOSSARY.md` 中的术语回来了。
- 你可以连续使用两次，而且它不会退化为简洁。

## 它在何处适用

你可以在任何 point、任何 conversation、任何其他技能内部使用 `wait-what`。它事后修复一条消息。真正的修复是提前同意的共享语言，那就是 [grill-with-docs](https://aihero.dev/skills-grill-with-docs)：一个 [grilling](https://www.aihero.dev/skills-grilling) session，它运行 [domain-modeling](https://aihero.dev/skills-domain-modeling)，因此它把你俩使用的词记录在你的 `GLOSSARY.md` 中。如果你不确定哪个技能适合当前时刻，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你指引。

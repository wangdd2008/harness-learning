## 作用

`writing-for-agents` 是编写 agent-facing documents 的参考：一个技能、一个 `AGENTS.md` 或 `CLAUDE.md`、一个 [spec](https://www.aihero.dev/ai-coding-dictionary/spec)、一个 runtime prompt、一个 README、任何 [agent](https://www.aihero.dev/ai-coding-dictionary/agent) 读取的文档。格式不同，但写作没有。相同的杠杆使每个都可预测，因此 agent 在每个 run 上遵循相同的 *process*（不一定遵循相同的 output）。

它的默认修复是删除，而不是解释。要求 agent 为另一个 agent 写 instructions，它会花大部分词解释 [model](https://www.aihero.dev/ai-coding-dictionary/model) 已经知道的东西。每一行都是**no-op**：它花费 [context](https://www.aihero.dev/ai-coding-dictionary/context) 但改变 no behaviour。这个参考帮助你找到它们，因此它在你已有的文档上与在空白文件上一样有用。

它被称为 `writing-great-skills` 直到 v1.1。新名字适合它一直以来的样子。几乎 none of it 是特定于 skills 的。Skill-only 的 mechanics（frontmatter、model- 对比 user-invoked 选择、router skills）存在于一个链接的 `SKILL-MECHANICS.md` 中，你只在面前的文档是 skill 时才阅读它。

## 何时使用

输入 `/writing-for-agents`，或者当你创建或编辑 skill，或修改 `AGENTS.md` 或 `CLAUDE.md` 时，agent 会自动触发它。

手动抓取它用于 agent 读取的所有其他东西：你的 docs、specs 和 [tickets](https://www.aihero.dev/ai-coding-dictionary/ticket)、系统和 [AFK](https://www.aihero.dev/ai-coding-dictionary/afk) prompts。测试是一个问题：agent 读取这个吗？Agent 如何获取文档不重要：pointer 命名它、人类粘贴它，或它在 repo 中。要找出代码库包含什么，使用 [grill-with-docs](https://aihero.dev/skills-grill-with-docs)。这个参考控制文档如何阅读，而不是它知道什么。

## 两个负载

核心思想是每个文档和 pointer 花费的两个 budgets：

- **Context load**：always-loaded 材料对 agent window 的成本：一个 `AGENTS.md` 行、skill description、任何每 [turn](https://www.aihero.dev/ai-coding-dictionary/turn) 都坐在 context 中的东西，无论它是否触发。
- **Cognitive load**：你记住哪些文档存在以及何时抓取它们的成本。你是索引。不要试图最小化这个成本，因为它是 human agency 的代价。

一旦你以这两个负载思考，大多数创作决策（拆分还是不拆分、inline 还是 disclose、point 还是 push）就成为在不同地方进行的相同 trade。

## 杠杆

- **[Context pointers](https://www.aihero.dev/ai-coding-dictionary/context-pointer)**：保留在 context 中的引用，命名 out-of-context 材料并编码何时抓取它。Skill description 和命名 doc 的 `AGENTS.md` 行是同一件事。Pointer 的 *wording*，而不是它的 target，决定 agent 遵循它的可靠程度。
- **Information hierarchy**：从 in-file step 到 in-file reference 到 pointer 后面的 disclosed reference 的梯子。**[Progressive disclosure](https://www.aihero.dev/ai-coding-dictionary/progressive-disclosure)** 是将材料向下移动，使顶部易于阅读。
- **Completion criteria**：每个步骤的 done-condition 有多清晰和要求，以及该需求引起的 **legwork**。它们是对 **premature completion** 的防御。
- **Leading words**：model pretraining 中已有的紧凑概念（*tight*、*red*、*tracer bullet*），agent 在运行文档时思考的东西。它在两个地方工作。在正文中它引导 execution，在 pointer 中它触发 invocation。
- **Pruning**：单一 truth source、相关性，以及逐句 applied 的 no-op test，对抗 **duplication**、**sediment** 和 **sprawl**。

## 常见问题

**`/writing-great-skills` 去哪儿了？**

就是这个技能，在 v1.1 中重命名。用户早在重命名之前就把它指向 `AGENTS.md`、docs、specs、tickets 和 runtime prompts。Structure、leading words 和 pruning 适用于 agent 读取的任何文本。没有 alias。在新名字下重新安装。

**"Writing for agents"：所以 agent 做写作？**

反过来。你是作者；agent 是读者。这就是它难的原因。你写的东西是给已经读了一切的 reader 的，因此解释是浪费，precision 是整个工作。

**我不能要求 agent 为我写吗？**

可以，而且它会生成 verbose 的东西。单独留着的 model 解释它已经知道的东西，而且它不会自行应用 no-op test 或抓取 leading word。使用该参考 review 草稿。它的大部分价值来自那个 review pass。

**我要求 agent 修剪一个文档，它剪掉了功能。**

被告诉 "streamline" 的 agent 为 length 优化，因为 length 是它能看到的。No-op test 检查 behaviour，而不是 style：删除该行，问 agent 的 behaviour 是否改变。当一句话 fail 时，删除整句话而不是从中删减单词，并通过运行文档而不是争论来解决关于它的分歧。

**我怎么知道它完成了？**

当它工作时，你不再能找到 duplication、sediment 或 no-ops。没有自动 eval。你通过手动运行文档并使用 failure-mode vocabulary 诊断问题来检查。当文档 misbehaves 时，相同的 vocabulary 帮助你修复它：首先命名 failure mode，然后修复它。

**这应该放在 `CLAUDE.md` 还是其他地方？**

问你愿意支付哪个 load。`CLAUDE.md` 无条件加载到每个 [session](https://www.aihero.dev/ai-coding-dictionary/session) 中。Pointer 后面的材料只花费 pointer 自己的行，直到它触发。任何在十个 session 中的一个适用的东西，在其他九个 session 中花费 context load。

**我需要为每个新 model 重写我的文档吗？**

大部分不需要，而且 over-fitting 到一个 model 会导致它自己有问题。为新 model 更新通常只是另一个 no-op pass，而不是重写。

**我的 skill 只在它构建的确切任务上工作。**

常见的方法（做一次工作，然后让 agent 把它写成一个 skill）与那一次 run 太贴合，examples 出来太具体。保留 run 作为证据，然后有意泛化：剥离属于那个 repo 和那些文件的东西，为任务类别写作。

**英语不是我的第一语言。我 lose 了 leading-word 优势吗？**

不。找到将最多 behaviour 打包到最少 [tokens](https://www.aihero.dev/ai-coding-dictionary/token) 中的词是该参考为你做的工作。

## 正常工作的标志

- 文档随着改进而变短，而且你会惊讶于剩下多么少。
- 你可以指向一个 leading word，并看到它在不止一个地方改变 agent 的 behaviour。
- Nothing 被陈述两次，以任何形式。Duplication 是文档从未被测试的最可靠迹象。
- 只有一个 branch 需要的 reference 坐在 pointer 后面，而不是主文件中。

## 它在何处适用

这是一个随时可用的独立参考。它适用于整个集合，而不是一个技能。这里的每个技能都是用这个技能写的，它也涵盖其他技能产生的文档（`GLOSSARY.md` 及其 ADR、spec、ticket），一旦 agent 必须读取它们。它的一个直接调用者是 [retro](https://aihero.dev/skills-retro)，它在提议任何 steering file 或 skill 之前加载它。当你不确定哪个技能或流程适合任务时，[ask-matt](https://aihero.dev/skills-ask-matt) 会在整个集合中为你指引。

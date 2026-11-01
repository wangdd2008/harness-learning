## 作用

`to-questionnaire` 将你自己无法决定的决策转化为一份**questionnaire**：一个 Markdown 文档，你把它交给拥有你所缺东西的那个人，让他们异步填写，或你们两个在会议中一起过。

它 grilling 你的是**send**，而不是 subject。关于主题的 interview 毫无意义，因为不知道主题正是你要写给其他人的原因。因此它问你两件你总是能回答的事情（这是给谁看的，以及你需要从他们那里得到什么），并将文档中的每个问题都瞄准两者之间的**gap**。

## 何时使用

你通过输入 `/to-questionnaire` 来调用它；[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 不会自动触发它。

当一个决策被阻碍于你脑海中只有一个人拥有的知识时选择它：客户、领域专家、拥有业务规则的 exec、你不坐在一个团队里的同事。你想要哪个技能取决于答案在哪里：

| 答案在… | 选择 |
| --- | --- |
| 你自己的脑海中，未磨练 | [grill-me](https://aihero.dev/skills-grill-me) |
| 代码库中 | [grill-with-docs](https://aihero.dev/skills-grill-with-docs) |
| 别人的脑海中 | `to-questionnaire` |
| 还没有人的脑海中，question 需要一些东西来 react | [prototype](https://aihero.dev/skills-prototype) |

常见的情况是 [grilling](https://www.aihero.dev/ai-coding-dictionary/grilling) session 停滞了，因为有些 raised 的 questions 不是你能回答的。在同一次对话中运行 `/to-questionnaire` 把那些 questions 带到线下，然后把答案带回来继续。

## Send，不是 subject

Interview 是两个 exchange，然后停止。

- **给谁看？** 他们的角色、他们的专业知识、他们与你的关系。这设定了语气以及文档需要携带多少 context。外部客户需要 orienting；队友不需要。
- **你需要从他们那里得到什么？** 你无法独自解决的 concrete decisions 或 facts。这成为完成文档的 checklist。你命名的每个项目都会得到一个针对它的问题。

之后的一切都是起草。该技能将文件写入当前目录的 `to-questionnaire-<slug>.md`。没有 setup，没有 workspace，也没有什么要配置的。

## 文档

该文档是一个**发现 questionnaire**，因为你缺乏 context，而 recipient 拥有它。这设定了它的形状：

- 一行目的，命名依赖它的决策，以及一个简短的 context 部分，面向不知道你任何背景的 recipient。
- Questions 按**最重要优先**排序，并在 themed headings 下分组，因为异步意味着你可能只得到一次 pass。
- 每个 question 一个 idea，绝不 compound，下面有一个 answer stub，以及一个 *why this matters* 行，只有在 question 可能被误读的地方。
- 明确允许回答 "I don't know"，因为 flagged 的不确定性是有用的，而自信的猜测一旦被读作事实则不是。
- 一个关闭的 catch-all：还有什么我们没有问到的，我们应该知道？

该文档故意不是两件事。它不是**branching** 的。Questions 是一个扁平的、分组的列表，不是一棵树，如果你回答了 A 就跳过 D 节。它也不是**multi-recipient** 的。一次运行产生一个文档给一个人。

## 常见问题

**它读取我的 grilling session 并从中提取 questions 吗？**

不是作为它自己的步骤。该技能没有 ingest phase。它询问 send，然后起草。使它能在 grilling session 后工作的是，你在**同一次对话**中运行它，因此 [session](https://www.aihero.dev/ai-coding-dictionary/session) 已经在 [context](https://www.aihero.dev/ai-coding-dictionary/context) 中，起草可以从中汲取。如果你在 fresh session 中启动它，它对 grilling 一无所知，你在回答 "what do you need back?" 时自己提供主题。

**缺失的答案并不都在同一个人那里。它们可以按 recipient 拆分吗？**

不行。第一步要求 *the* recipient，单数，而且该技能将整个文档的语气对准他们。如果三个人拥有答案的三个部分，运行三次，每次一个人。人们要求一个按学科或角色路由 questions 的文档，但没有发布。

**Questions 是依赖的吗：它是否基于早期答案跳过 sections？**

不。Dependent-question 设计被探索过，但没有发布。输出是一个静态文档：themed groups，most-important-first，每个 question 都 alive。对此的反对意见是公平的。[model](https://www.aihero.dev/ai-coding-dictionary/model) 在真实答案之前计划超过两三个 questions 时计划得很糟糕，而 branching 文档必须在每个答案之前计划所有 questions。

**如果 recipient 也不知道呢？**

文档告诉他们说出来。它明确要求 "I don't know" 和部分答案。Flagged 的不确定性比猜测更有价值，因为模糊的答案和自信的错误答案一旦回到你的 context 中，看起来完全相同。

**它发送到任何地方吗（Slack、issue tracker、email）？**

不。它在当前目录中写入一个 Markdown 文件并告诉你路径。Delivery 是你的：粘贴到 [ticket](https://www.aihero.dev/ai-coding-dictionary/ticket)、放入 Slack thread、附加到 email，或在共享屏幕上打开并现场过。人们已经手动完成了所有四项。

**这不就是 `/grill-me` 的 batch mode 吗？**

不。`grill-me` 已经在**轮次**中提问。它一次询问整个前沿的 open questions，然后从你的答案中重新计算它，所以它已经满足了"一次性给我所有 questions"的需求。`to-questionnaire` 在另一个轴上不同。它是关于答案在谁的脑海中，而不是 questions 如何交付。自己更快地回答问题，使用 `grill-me`。从别人那里获取答案，使用这个。

**我不能没有 skill 就要求 agent 做这个吗？**

可以，而且很多人在这之前就做了：`OPEN_QUESTIONS.md` 文件、发送给客户的 spreadsheets、每个未回答问题的 "needs more info" ticket。该技能给你买两件东西：interview 永远不会漂移到 subject 上，而且文档以一个非技术的 recipient 可以填写的形状出来。如果你已经有有效的 house format，你不需要这个。

## 正常工作的标志

- 它询问 recipient 和你需要什么，然后停止询问。如果它询问 subject 本身，该技能就错了。
- 你命名为"我需要什么"的每个项目都可以追溯到文件中的一个 question。
- Questions 读起来像是针对 *recipient* 所知的，而不是你自己的 open questions 逐字复制。
- 你可以把它交给没有参与对话的人，他们会知道为什么收到它以及何时回复。
- 回来的答案是新 grilling round 的可用输入，而不是一套新的 questions。

## 它在何处适用

`to-questionnaire` 是一个随时可用的独立工具。你在自己的知识结束而下一步是问另一个人时使用它，而不是运行另一个技能。这最常发生在流程中间，当规划停滞在不是你能决定的东西上时。

它的邻居是 [grill-me](https://aihero.dev/skills-grill-me)，两者在答案在哪里方面不同。Grilling 从你那里获取答案；questionnaire 从别人那里获取。把回来的东西喂到另一个 grilling round，或者如果工作正走向构建，喂到 [grill-with-docs](https://aihero.dev/skills-grill-with-docs) 或 [to-spec](https://aihero.dev/skills-to-spec)。当你不确定哪个技能适合当前时刻时，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你指引。

## 作用

`teach` 将你运行它的目录变成一个 standing teaching workspace，并在许多 [sessions](https://www.aihero.dev/ai-coding-dictionary/session) 中教你一个主题，以简短的自包含 HTML lessons 形式。

它不从 [model](https://www.aihero.dev/ai-coding-dictionary/model) 已经知道的东西中教学。它将 [parametric knowledge](https://www.aihero.dev/ai-coding-dictionary/parametric-knowledge) 视为不可信。在教学之前，它会找到高可信资源，将它们记录在 `RESOURCES.md` 中，并在每个 lesson 中引用它们。它也是 [stateful](https://www.aihero.dev/ai-coding-dictionary/stateful) 的。任务、资源、lessons 和你学到的东西的记录都以文件的形式存在于目录中，因此下一个 session 从这些文件继续，而不是从上一次对话的剩余部分。

## 何时使用

你通过输入 `/teach` 来调用它；[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 不会自动触发它。

当学习就是项目时选择它：一种语言、一个框架、你刚刚加入的代码库、瑜伽、shaders、一个认证。它不是用于顺带的解释。

| 你想要什么 | 选择什么 |
| --- | --- |
| 在几周内学习一个主题，sessions 累积 | `teach` |
| 在你已经处于的 session 中解释一个概念 | 直接在那个 session 中问 |
| Agent 的最后一条消息重新表述，因为它没有落地 | [wait-what](https://aihero.dev/skills-wait-what) |
| 磨练你已经拥有的思维，而不是获取新材料 | [grill-me](https://aihero.dev/skills-grill-me) |
| 后台 agent 读取 [一级来源](https://www.aihero.dev/ai-coding-dictionary/primary-source) 并给你留下一个引用的文档 | [research](https://aihero.dev/skills-research) |
| 在学习 grilling 过程中学到的东西，而不 derailing [grilling](https://www.aihero.dev/ai-coding-dictionary/grilling) | [handoff](https://aihero.dev/skills-handoff) 到一个 teaching workspace，然后在那里 `teach` |

## 前置条件

`teach` 构建一个目录而不是生成一个文件，而且该技能假设每个 workspace 一个任务，所以在某个你愿意让渡给单个主题的地方运行它。把它放在你正在工作的项目之外。单独的 repo 是最好的家，比全局的 `~/.learnings/` 文件夹或工作项目本身更好。专用 repo 还允许你提交 lessons，这就是团队共享它们的方式。

在那个目录中累积的内容：

| 路径 | 它保存什么 |
| --- | --- |
| `MISSION.md` | 你为什么学习这个。每个其他文件都依赖它。如果缺失，`teach` 做的第一件事就是 interview 你，直到它不再缺失 |
| `RESOURCES.md` | 它从中教学的来源，分为 Knowledge 和 Wisdom（社区） |
| `lessons/*.html` | 编号的 lessons：教学的主要单位 |
| `reference/*.html` | 压缩的 cheat-sheets、算法、glossary：你返回查阅的文档 |
| `learning-records/*.md` | ADR-style 的 notes，关于你已经 demonstrably 学到的东西，用于决定下一步教什么 |
| `assets/*` | 可复用组件，从一个共享样式表开始，因此 lessons 看起来像一门课程 |
| `NOTES.md` | 你声明的教学偏好 |

关于该列表的两点说明。Glossary 适合大多数主题，但该技能运送一个 `GLOSSARY-FORMAT.md`，`SKILL.md` 不再链接到它，所以你只有在你要求时才能得到一个（[issue #559](https://github.com/mattpocock/skills/issues/559)）。所有这些都落在你在 `/teach` 中运行的目录中。

## Storage strength，不是 fluency

要思考的词是 **storage strength**：长期记忆，与 **fluency** 相对，即你正在阅读时感觉像掌握的即时回忆，一周后消失。`teach` 通过 desirable difficulty 建立前者：retrieval practice、spacing、interleaving。知识首先到来。在这个阶段 difficulty 对你不利，因为它消耗你需要理解的工作记忆。然后 `teach` 通过一个紧密的反馈循环 drill 技能，在这个阶段 difficulty 是工具。

两件事决定你学什么。**任务**（你想要这个的具体现实原因）是每一个 lesson 的基础。没有它，lessons 变得抽象，没有什么决定下一步该来什么。从任务和学习记录中，`teach` 在你**proximal development zone**内挑选下一个 lesson：足够难以需要努力，但不要太超前，以至于你无法学习。

Storage strength 也是为什么该技能反驳而不是同意。需要 **wisdom**（现实判断）的问题会得到一个尝试性答案，然后一个指向你可以测试它的社区的指针。该技能不会让你跳过测验。一位用户报告说"thanks a lot"，然后被告知 drill 还没有完成。

## Lessons、references 和 components

一个 **lesson** 是一个自包含的 HTML 文件，短到可以在一个 sitting 内完成，与任务绑定，给出一个有形的胜利。它引用其来源，推荐一个一级来源供你自己阅读，并链接到 sibling lessons 和 reference documents。

你很少会回到一个 lesson，但你会回到 reference documents。因此 lesson 的短形式（语法表、算法、姿势序列、glossary）属于 `reference/`，而不是埋在引入它的 lesson 中。

Lessons 由 `assets/` 中的 **components** 构建：样式表、quiz widgets、simulators、diagram helpers。复用是默认的。Agent 在编写 lesson 之前读取 `assets/` 并从那里构建。它将任何新的、第二个 lesson 可以使用的东西写为 component，而不是 inline。共享样式表是每个 workspace 中的第一个 component，它使 lessons 看起来像一门课程而不是许多不相关的页面。

## 常见问题

**它把文件放在哪里？我的落在了 `~/.claude/skills`。**

在你运行 `/teach` 的目录中（[#377](https://github.com/mattpocock/skills/issues/377)）。

**我是留在同一个 session，还是每个 lesson 启动一个新的？**

三种方法都有效：留在同一个 session，在新的 session 中重新调用 `/teach`，或在同一个文件夹中打开新的 session。每个 lesson 是它自己的调用。课程状态存在于文件夹中，不在对话中。常见的做法是在 workspace 中打开一个 fresh session 并说 `/teach next lesson for <topic>`。

**我怎么知道它没有教我一些它编造的东西？**

仅凭该技能的保证是不知道的。你阅读一级来源。`teach` 不足够可靠，不能未经检查就信任，而且任何基于 LLM 的技能都不是。每个 lesson 中的 grounding（`RESOURCES.md`、引用、每个 lesson 推荐一个一级来源）使检查一个 lesson 变得便宜。它不会消除检查的需要。这个失败发生过：一位学习 2x2 Rubik's cube 的用户得到了编造的 move sequences，无法解决它。在那种情况下，检查 model、harness、effort setting 和来源。风险最高的是具有精确记号的程序性领域，最低的是输出可立即验证的地方，比如你可以运行的代码。

**正确的 quiz 答案总是第一个选项。**

多人在 Sonnet、Opus 和 GLM 上确认了这一点，而且仍未修复。`SKILL.md` 现在要求每个答案具有相同的单词数。这消除了一个不同的线索（正确答案曾经是唯一完全推理的），但对位置什么也没说。一位贡献者测试了位置层面的修复，正确答案在九次 lesson 中 33 次中有 33 次落在 slot A（[#335](https://github.com/mattpocock/skills/issues/335)）。因此真正的修复是 `assets/` 中的一个 shuffle answers 的 quiz component，而不是更好的措辞。在发布之前，忽略答案位置。你的 `assets/` 目录是你自己的，可以更改，因此你可以要求一个 shuffle render time 的 component 作为本地修复。

**它假设我已经知道一些东西，并使用了它从未定义的术语。**

这是最常见真实的投诉。没有评估步骤。`teach` 从任务和学习记录中推断你的水平，而且在 session one 中没有学习记录。一位在 wayfinder pipeline 中运行它的用户直白地说："It never did grilling to establish my starting point so it made lots of assumptions of what I already knew。"另一位用户报告了使用未定义术语的 lessons，以及关于他们硬件的 lesson，涵盖了硬件能做什么，但从未说它不能做什么。两件事有帮助：在第一条消息中声明你先前的知识和你的空白，并在 lesson 出错时大声纠正，因为纠正成为学习记录并引导下一个。一个显式的知识评估步骤是一个 standing feature request（[#725](https://github.com/mattpocock/skills/issues/725)），不是已发布的行为。

**它做 spaced repetition 吗，它知道什么时候停止教学吗？**

第一个不做，第二个不可靠。该技能围绕 spacing 和 interleaving 设计 lessons，但 nothing schedules review，而且也没有 Anki 或日历集成。用户经常要求两者。相关的空白是 exit criteria。正如一位用户所说，`teach` "is good at making the next lesson, but not as good at knowing when to stop and switch to review or real practice。"如果你想 review 或 drill 而不是新材料，请要求；该技能不会自行提出切换。

**它只对代码有用吗？**

不。报告的大部分使用都在 coding 之外：韩语、日语正式语体、钢琴、吉他、棋盘游戏设计、OpenSCAD、电影情节、Azure 和 CCNA 认证、大学考试，以及八岁和十岁孩子获得的关于逃生室和火蝾螈的可打印书籍。该技能中没有特定于编程的东西。任务、资源、proximal development zone 和 drill 在任何领域都以相同的方式工作。在代码中，用户报告说，在陌生的代码库或新团队的 stack 中定位自己比从头学习一种语言获得更多价值。

**我应该用哪个 model 运行它？**

没有 canonical 答案，而且报告的差异很大。用户报告说更高的 [reasoning effort](https://www.aihero.dev/ai-coding-dictionary/effort) 比 medium setting 产生更好的 lessons。一位用户通过 Copilot CLI 用 Codex 运行同一个技能，得到了一个 30 行的 HTML card，而 Claude Code 产生了一个完整的 lesson。它在 Claude Cowork 中未修改地运行，如果你的组织允许你在那里添加技能。如果 lessons 出来很薄，先改变 model、[harness](https://www.aihero.dev/ai-coding-dictionary/harness) 或 effort，然后再重写你的 prompt。

## 正常工作的标志

- 它在空目录中做的第一件事是 interview 你为什么要学习这个，而不是 produce a lesson。
- `RESOURCES.md` 在 lessons 之前填满，而且每个 lesson 都命名一个值得自己阅读的一级来源。
- Lesson 中的声明带有链接。没有引用的 lesson 是该技能从记忆中教学。
- 一个 lesson 花一个 sitting，让你能做一件以前做不到的事情。
- 在文件夹中打开 fresh session 并说 "next lesson" 会继续课程而不是重新开始。
- `learning-records/` 增长，lessons 停止重新教你已经 demonstrable 的东西。
- Lessons 看起来像一门课程：它们链接 `assets/` 中的样式表，而不是每个都携带自己的样式表。
- 需要判断的问题会让你指向论坛、subreddit 或班级，而不仅仅是一个答案。

## 它在何处适用

`teach` 是一个**随时可用的独立工具**。它不是构建链中的步骤，也不与 engineering flow 共享 artifacts；它在它自己的目录中工作，只要你学习这个主题。

它唯一真正的邻居是 [handoff](https://aihero.dev/skills-handoff)。它们一起回答"如果我在被 grilling 一些我不懂的东西时该怎么办？"不要停止 grilling 去学习。`/handoff` 到一个 teaching workspace，在那里用 `/teach` 学习，然后回去继续你离开的地方。附近的替代方案是 [research](https://aihero.dev/skills-research)，当你想要的是一个引用的文档而不是 lessons 和 retention。当你不确定哪个技能或流程适用时，[ask-matt](https://aihero.dev/skills-ask-matt) 会在整个集合中为你指引。

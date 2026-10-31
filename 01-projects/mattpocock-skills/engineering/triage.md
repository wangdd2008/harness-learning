## 作用

`triage` 处理你项目 tracker 上的 issues。它将每个 issue 通过一个小的 **分类角色** 状态机（一个类别角色和一个状态角色）移动。每个 issue 最终成为 agent-ready 简报、给报告者的具体问题，或带记录原因的关闭 issue。

它只用于**你没有创建的** issues。这意味着原始 bug 报告、传入的功能请求，或未经通知到达的外部 pull request：从外部进入 tracker 的工作，以报告者留下的任何形状。来自 [to-tickets](https://aihero.dev/skills-to-tickets) 的 [tickets](https://www.aihero.dev/ai-coding-dictionary/ticket) 已经是 agent-ready 的，所以如果你对它们运行 `triage`，你就是在浪费工作。规则很简单：`/triage` 只用于传入 issues，不用于你自己创建的 issues。

它也不同于手动标记，因为它推荐然后等待。它给你它的类别和状态判断及推理，加上它在代码库中发现的内容，并且在得到你的指示之前什么都不应用。

## 何时使用

你通过输入 `/triage` 然后用自然语言描述你想要什么来调用它。[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 不会自动触发它。示例："Show me anything that needs my attention"、"let's look at #42"、"move #42 to ready-for-agent"。

| 你有什么 | 去哪里 |
| --- | --- |
| 一个满是其他人原始报告的 tracker | `/triage` |
| 你自己的粗略想法，什么都没写下来 | [grill-with-docs](https://aihero.dev/skills-grill-with-docs) |
| 要转化为 [spec](https://www.aihero.dev/ai-coding-dictionary/spec) 的已确定对话 | [to-spec](https://aihero.dev/skills-to-spec) |
| 要拆分成 agent-ready tickets 的 spec | [to-tickets](https://aihero.dev/skills-to-tickets) |
| 需要根本原因确认的已确认 bug | [diagnosing-bugs](https://aihero.dev/skills-diagnosing-bugs) |

## 前置条件

`triage` 读取和写入你的 issue tracker，因此 [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) 必须首先配置该 tracker 及其标签词汇。下面的角色名称是**规范的**。你 tracker 中的标签字符串可能不同，setup 提供了映射。如果你的 tracker 已经精确使用规范名称，你无需映射，也无需设置。

Tracker 配置还决定外部 pull requests 是否算作请求面，以及谁算作外部。该标志默认关闭，setup 不再询问它。要将 PR 纳入范围，请在 `docs/agents/issue-tracker.md` 中打开它。

## 状态机

每个分类项目最终恰好有一个类别角色和一个状态角色。有两个类别：`bug`（某些东西坏了）和 `enhancement`（新功能或改进）。有五个状态：

| 状态 | 含义 |
| --- | --- |
| `needs-triage` | 你需要评估它。未标记的 issue 通常首先落在这里。 |
| `needs-info` | 等待报告者回复。他们回复后返回 `needs-triage`。 |
| `ready-for-agent` | 完全指定，附有 agent 简报。AFK agent 可以接手。 |
| `ready-for-human` | 相同的简报，加上为什么 agent 做不了：判断、外部访问、手动测试。 |
| `wontfix` | 关闭，原因已记录。 |

这就是全部词汇。每个项目恰好有一个状态角色的规则使查询保持简单。这些状态也是该 [skill](https://www.aihero.dev/ai-coding-dictionary/skill) 请求最多的区域。用户要求增加一个用于工作被另一个 issue 阻塞的状态、一个用于等待未来触发的 `deferred` 状态，以及一个终端的 `implemented` 状态。这些都没有发布。见下面的问题。

`wontfix` 有三种情况。区别很重要，因为只有其中一种会写入知识库：

| 你为什么关闭它 | 发生什么 |
| --- | --- |
| Already implemented | 一条评论指出功能已经存在。不会写入 `.out-of-scope/`，因为它是已构建的功能，不是被拒绝的功能，而且那里的文件会破坏 dedup 检查。 |
| Rejected bug | 礼貌解释，然后关闭。 |
| Rejected enhancement | `.out-of-scope/` 中的一个文件，从关闭评论中链接，然后关闭。 |

`.out-of-scope/` 为每个被拒绝的**概念**保存一个 markdown 文件，不是每个 issue。每个文件是一个简短的设计文档，不是数据库行。它说明了什么被拒绝、为什么，并列出了每个要求它的 issue。`triage` 在评估任何东西之前读取整个目录。它按概念匹配，不是按关键词，所以 "night theme" 匹配 `dark-mode.md`。当它找到匹配时，它向你展示旧决策并问你仍然同意它，而不是从头开始争论请求。

## 在简报之前验证

在任何 [grilling](https://www.aihero.dev/ai-coding-dictionary/grilling) 之前，`triage` 检查声明是否成立。对于 bug，它从报告者的步骤中复现。对于 PR，它 checkout 分支并运行相关测试。然后它报告三个结果之一：

- Confirmed，附带代码路径。
- Failed to reproduce。
- Not enough detail to try。这是最强的 `needs-info` 信号。

在同一遍中，它还针对代码库运行两个额外检查。**冗余**检查询问功能是否已实现，并按领域概念搜索，不是按报告者的措辞。**先前拒绝**检查询问 `.out-of-scope/` 是否已经说了不。两个检查都很便宜，而且任何一个命中都会产生 `wontfix`。

所有这些工作产生了一个好的 artifact：**agent 简报**。这是 `triage` 在 issue 移动到 `ready-for-agent` 时发布的结构化评论。`triage` 发布后，简报就是合同，原始报告只是上下文。简报是**耐久的**而不是精确的，因为 issue 可以在 `ready-for-agent` 中放置数周，而代码在此期间发生变化。因此简报命名类型、签名和行为契约，绝不命名文件路径或行号。确认的复现比猜测产生强得多的简报。

## PR 是附带代码的 issue

如果 tracker 将外部 pull requests 视为请求面，它们经历相同的状态机，具有相同的类别、状态和转换。状态适用于 diff。`ready-for-agent` 意味着附有简报，agent 应该对代码采取下一步。`ready-for-human` 意味着人可以合并它。PR 上的简报描述了对现有 diff 还剩下什么要做，不是如何从零开始构建东西。

发现只显示*外部* PR，因为协作者的进行中分支不是分类工作。该过滤器仅适用于发现。如果你显式命名 PR，`triage` 处理它，无论谁写的。

## 常见问题

**我运行了 `/to-spec` 和 `/to-tickets`，现在那些 tickets 坐在那里未分类。我是否需要对它们运行 `/triage`？**

不需要。它们已经是 agent-ready 的。`to-tickets` 在发布它们时应用 `ready-for-agent` 标签，因此 AFK runner 无需另一次通过就能捡起它们。遇到这个问题的用户运行了 spec 流程，看到输出上有 `needs-triage`，他们的 AFK runner 忽略了所有东西。`triage` 是从外部到达的工作的上匝道。Spec 流程是你自己启动的工作的车道。两者在 `ready-for-agent` 处相遇，而不是之前。

**既然有了 `to-spec` → `to-tickets` → `implement` 流程，`triage` 还相关吗？**

只有你传入工作时才相关。`triage` 比那个流程更古老，做不同的工作：它处理其他人提交的报告。如果你的 tracker 中的所有东西都来自于你自己的规划，你很少会使用它。如果你维护任何公共项目，或者你的团队向你提交 bug，那就是该工作开始的地方。主要用途是接受外部贡献者 issues 的开源 repos。

**Agent 尝试应用 `ready-for-agent` 时，`gh` 说标签不存在。**

这是一个已知的开放 bug（[#616](https://github.com/mattpocock/skills/issues/616)）。`setup-matt-pocock-skills` 将标签词汇写入 `docs/agents/triage-labels.md`，但不会在 tracker 中创建标签。自己用 `gh label create` 或 tracker 的 UI 创建五个状态标签和两个类别标签，一次就够了，错误就会停止。该 issue 链接到一个尚未合并的社区修复分支。

**五个状态不够。那 blocked、deferred 或 implemented 呢？**

这是该技能提交最多的空白。它以三种形式出现：

- 一个完全指定但等待另一个 issue 关闭的问题（[#139](https://github.com/mattpocock/skills/issues/139)）。报告者说 `ready-for-agent` 在那里"技术上正确"但具有误导性，所以 agent 捡起它并卡住。
- 未来有意进行但等待触发的工作，因此目前不可行（[#297](https://github.com/mattpocock/skills/issues/297)）。
- "已实现，等待验证"的终端状态。没有它，AFK runner 可以再次排队已完成的 tickets。

Blocked 情况被认为是真实的，但名称尚未确定（`blocked` 对比 `paused`）。这些都没有发布。作为变通方法，人们在类别旁边添加一个 repo-local 额外标签。状态槽随后持有准确的值，但该技能不知道额外标签。一个社区分支更进一步，添加了 `needs-slicing`、`tracking` 和 effort 标签。这有效，但它属于那个分支，不属于该技能。

**这与 `/diagnosing-bugs` 有何不同？**

这里的验证步骤故意很浅。它回答"这是真的吗，以及大致在哪里"，不会寻找根本原因。如果 bug 在几分钟内无法从报告者的步骤中复现，使用 `needs-info`，或者如果你想现在调查，使用 [diagnosing-bugs](https://aihero.dev/skills-diagnosing-bugs)。两个技能的文本目前都没有提到对方。一位用户报告了那个空白，而且它仍然是开放的。

**我可以指向整个 backlog 让它运行吗？**

你可以问，但要 watch 它读取什么。"Show what needs attention" 传递是一个便宜的列表，用于*选择*。你挑一个 issue，然后 `triage` 收集该 issue 的完整 [context](https://www.aihero.dev/ai-coding-dictionary/context)。如果你一次运行二十个 issues，agent 可以将该便宜列表作为唯一证据使用，而不告诉你。列表返回 issue 正文但不返回评论。一位用户恰好遇到了这种情况。三个 issues 已经有评论说"already fixed, recommend closing"，所有三个都获得了新的 agent 简报。对于批量通过，明确说明它必须读取每个 issue 的评论。

**它适用于 Linear，还是 GitHub Issues 以外的任何工具？**

是的。Tracker 是配置，不是硬编码的假设。人们通过 `linear` CLI 针对 Linear 运行它，GitLab，以及 `.scratch/` 下的纯 markdown 文件。常见的分割是 Linear 用于 issues 和规划，GitHub 用于代码和 PR。说"issue tracker" 的技能映射到 Linear，说"PR" 的映射到 GitHub。本地 markdown tracker 有一个开放的模板 bug：生成的文件可以在顶层和 agent 简报内部各包含一次验收标准（[#200](https://github.com/mattpocock/skills/issues/200)）。

## 正常工作的标志

- 它触及的每个项目最终恰好有一个类别角色和一个状态角色，从不为零，也从不冲突。
- 它给你推荐并附带推理，然后停止。它不会重新标记 issue 并继续。
- 在到达 `ready-for-agent` 之前，它复现了 bug，或 checkout 并运行了 PR。
- 它写的简报命名类型和行为，不包含文件路径和行号。
- 当六个月前你拒绝的请求再次出现时，它告诉你并引用旧原因，而不是再次分类。
- 它发布的每条评论都以 `> *This was generated by AI during triage.*` 开头。

## 它在何处适用

`triage` 是一个**上匝道**，不是主链中的步骤。主流从你拥有的想法开始（grill、spec、tickets、implement、review）。`triage` 是用于从别人那里传来的工作的并行车道。两条车道最终到达同一个地方：标记为 `ready-for-agent` 并附有简报的 issue。[implement](https://aihero.dev/skills-implement) 以与捡起 [to-tickets](https://aihero.dev/skills-to-tickets) 的 ticket 相同的方式捡起它。当请求需要更多细节才能 `triage` 简报时，`triage` 一起运行 [grilling](https://www.aihero.dev/skills-grilling) 和 [domain-modeling](https://aihero.dev/skills-domain-modeling)，一轮问题一轮问题地来，因此当你做决定时，它会把它们记录在 `GLOSSARY.md` 和 ADR 中。当你不确定你在哪个车道时，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你指引。

## 作用

`implement-spec` 接收一个 [spec](https://www.aihero.dev/ai-coding-dictionary/spec) 及其 [tickets](https://www.aihero.dev/ai-coding-dictionary/ticket)，一次性完成整个工作。编排 [agent](https://www.aihero.dev/ai-coding-dictionary/agent) 将每个 ticket 交给一个实现者 [subagent](https://www.aihero.dev/ai-coding-dictionary/subagent)，后者在自己的 git worktree 中工作，将每个完成的分支合并到一个**集成分支**上，对结果运行 [code-review](https://aihero.dev/skills-code-review)，然后关闭这些 tickets。

它将 tickets 视为**任务图**，而非列表。阻塞边决定了什么可以开始，所以在任何时刻，都存在一个**前沿**——所有阻塞者都已落地的 tickets——前沿上的每个 ticket 同时运行。这就是它与逐个处理 tickets 的区别。图的形状决定了节奏，而不是 tickets 在跟踪器上的顺序。

## 何时使用

你通过输入 `/implement-spec` 来调用它，agent 不会自动使用它。

| 你的情况 | 使用 |
| --- | --- |
| 一个 spec，已拆分成带有阻塞边的 tickets，你想一次性落地 | `/implement-spec` |
| 逐个处理，在自己的 [context window](https://www.aihero.dev/ai-coding-dictionary/context-window) 中，[clearing](https://www.aihero.dev/ai-coding-dictionary/clearing) 每个 ticket 之间 | [implement](https://aihero.dev/skills-implement) |
| 一个尚未拆分成 tickets 的 spec | 先用 [to-tickets](https://aihero.dev/skills-to-tickets) |
| 一个没什么图结构的小任务 | 直接使用 [implement](https://aihero.dev/skills-implement) |

## 前置条件

- **一个 issue tracker。** 技能从 tracker 读取 tickets，并在上面关闭它们，这是 [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) 配置的。如果没有配置，它会停下来告诉你先运行那个，而不是猜测。
- **带有阻塞边的 tickets**，由 [to-tickets](https://aihero.dev/skills-to-tickets) 写入。没有边的话，图就是平的，所有 ticket 同时开始。
- **一个 [harness](https://www.aihero.dev/ai-coding-dictionary/harness)**，可以在后台运行 subagents，并为每个提供一个 git worktree。这个技能的存在就是为了同时运行 tickets，所以在一个串行运行 subagents 的 harness 上，它只是更慢的 `implement`。

## 集成分支

所有工作都落在一个分支上。每个实现者：

1. 在开始之前确认它的 worktree 基于集成分支，
2. 使用 [tdd](https://aihero.dev/skills-tdd) 构建它的 ticket，一次一个红绿切片，
3. 在报告完成之前将集成分支的 tip 合并到自己的分支，所以落地时是快进。

tracker 决定是否要创建 pull request。如果你的 tracker 通过 PR 关闭工作，或者你要求一个，技能会在第一次合并后打开一个 draft PR，并在最后标记为 ready。否则，运行会在集成分支上停止，每个 ticket 都以你的 tracker 关闭工作的方式解决，这完全适用于本地 markdown tracker。

实现者通过 [context pointers](https://www.aihero.dev/ai-coding-dictionary/context-pointer)（spec、ticket、共享探索笔记、早期提交）与编排器通信，而不是粘贴摘要。这保持了每个 subagent 的 prompt 很小，为编排器的窗口留出了图的空间。

## 常见问题

**这和手动对每个 ticket 运行 `/implement` 有什么区别？**

这是这个技能要回答的核心问题。在它发布之前，人们一直在构建自己的版本，一位用户描述了需求：他们想要"subagents 实现 tickets"，而不是"当 spec 可能包含 5 个以上 tickets 时，逐个创建新 session 并告诉它们实现一个 ticket"。使用 `implement`，你是调度员：每个 ticket 一个 [session](https://www.aihero.dev/ai-coding-dictionary/session)，中间 clearing，自己跟踪哪些 tickets 已解除阻塞。`implement-spec` 将这项工作交给一个编排 session。代价是你不再阅读每个 ticket 的工作成果；你在最后审查集成分支。要开始一次运行，clear context 并输入 `/implement-spec`，附带一个指向 spec 的指针（issue 编号或文件路径）。对于没有真正图结构的小变更，跳过它，直接使用 `implement`。

**它需要 GitHub 吗？我想让它停在分支上。**

不，现在不需要了。一位喜欢内部版本的用户有完全相同的抱怨："它在最后创建一个 PR，这需要像 GitHub 这样的在线仓库。我希望它可以离线完成同样的工作，停在所有工作都合并的分支上。"现在运行会停在集成分支上。只有当配置的 tracker 通过 PR 关闭工作，或者你要求一个时，才会打开 PR，所以在本地 markdown tracker 上，运行会以每个 ticket 都已解决、工作合并到分支上结束。

**它的审查和修复循环运行了几个小时，或者一直在"修复"尚未构建的 tickets。**

这两种情况都发生在 `code-review` 在技能指定的一个点之外的任何地方运行时。它将代码与整个 spec 对比，所以只有在每个 ticket 都已落地后才有意义。如果它在运行中途运行，每个未构建的 ticket 都会读作失败。然后 agent 构建那个 ticket，触发另一次审查。最后，技能运行一次 `code-review` 并将每个发现发给一个修复 subagent，但它没有说明在修复后何时停止。一位用户报告了一个五 ticket 的功能，"审查和修复循环大约花了四个小时"。如果你看到第二次广泛审查开始，告诉它运行针对修复发现的聚焦检查并停止。预期第一次审查会发现真正的问题。运行的输出是 draft，审查完成它，而不是一个可以直接交付的东西。

**它像 implement 一样驱动 tdd 吗？**

现在是的，尽管一开始不是。运行内部版本的用户注意到"实现者 subagents 没有继承 /tdd 指令"，所以 red-green 在从单个 ticket 扩展到整个 spec 时就停止了。每个实现者现在使用 `tdd` 构建它的 ticket。仍然没有你 interactively 同意 seams 的步骤，就像 `implement` session 中那样，所以如果你想固定它们，在 spec 或 tickets 中命名 seams。

**两个并行运行的实现者在同一个文件上冲突，或者为同一个事物选择了不同的名称。**\n
Worktree 不能消除冲突；它们只是将冲突推迟到合并时。从 ticket 文本中写入的阻塞边是对每个 ticket 将触及哪些文件的猜测，两个在不同"代码库部分"的 tickets 仍然共享一个消息目录、一个配置注册表或一个类型。每个实现者只能看到自己的 ticket 和共享笔记，永远看不到另一个的工作进度，所以一位用户的 web 和 mobile tickets 将相同的字符串添加为 `blockedSince` 和 `blockedOn`。当两个前沿 tickets 触及一个共享文件时，要么在它们之间添加一个阻塞边，让它们一个接一个运行，要么让探索笔记固定每个 ticket 添加的确切名称。

**阻塞的 tickets 永远不会开始，即使它们的阻塞者已经合并。**

这是 GitHub 上的一个已知问题。tracker 的 blocked-by 计数只在一个阻塞者*关闭*时才下降，而 tickets 通常在 PR 合并时关闭，也就是运行结束时。tracker 是启动图的正确来源，但运行中是过时的。告诉编排器跟踪哪些 tickets 已合并到集成分支，并从中计算前沿。

**这会取代 Sandcastle 或 AFK 脚本吗？**

不会。人们会问，因为技能现在触及实现："Sandcastle 还有意义吗？你的技能现在似乎也能处理实现了。"`implement-spec` 将一个 agent 放在 harness session 内部的编排位置上，这不需要基础设施，让你可以观察和引导。对于真正 [AFK](https://www.aihero.dev/ai-coding-dictionary/afk) 的工作，确定性循环（[Sandcastle](https://github.com/mattpocock/sandcastle)、shell 脚本、CI job）更快、更便宜、更可靠，因为没有 agent 来做编排决策。

**一个 ticket 的关键测试在它的 worktree 中被跳过了，却报告了绿色。**

Worktree 只包含 git 跟踪的内容。读取 gitignored fixtures、本地数据库或凭据的测试可能会静默跳过。对于一个验证依赖于未跟踪材料的 ticket，告诉编排器在主 checkout 中运行它。

## 正常工作的标志

- 每当图允许时，多个实现者同时运行，而不是一个接一个。
- 一个 ticket 在其最后一个阻塞者落地集成分支时立即开始，而不是在整个运行结束时。
- 每个 ticket 的 trace 都显示 `tdd` 在运行，先有失败的测试，后有代码。
- 合并到集成分支是快进，而不是冲突解决。
- 运行以一个分支结束，每个 ticket 都已解决，只有当你的 tracker 需要时才创建 PR。

## 它在何处适用

`implement-spec` 是主链的构建步骤，是每个 ticket 运行一次 [implement](https://aihero.dev/skills-implement) 的并行替代：

```txt
grill-with-docs → to-spec → to-tickets → implement-spec → retro
```

它的邻居是 [to-tickets](https://aihero.dev/skills-to-tickets)，它声明了作为任务图读取的阻塞边；以及 [code-review](https://aihero.dev/skills-code-review)，它在关闭前在集成分支上运行。[ask-matt](https://aihero.dev/skills-ask-matt) 是整个集合的路由器，当你不确定自己在哪个流程中时。

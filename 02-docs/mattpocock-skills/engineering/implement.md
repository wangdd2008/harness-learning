## 作用

`implement` 构建已经决定好的工作。你指向一个 [ticket](https://www.aihero.dev/ai-coding-dictionary/ticket)、一个 [spec](https://www.aihero.dev/ai-coding-dictionary/spec)，或者你刚刚在对话中同意的计划，它会编写代码，在 seams 处驱动 [tdd](https://aihero.dev/skills-tdd)，边做边类型检查，最后运行 [code-review](https://aihero.dev/skills-code-review)，并提交到当前分支。

它从不重新打开计划。没有访谈，没有澄清回合，没有提出不同的方法。上游确定的一切都是输入，技能的全部工作就是将其转化为提交。这就是它与在一个全新的 [agent](https://www.aihero.dev/ai-coding-dictionary/agent) 面前输入"构建这个"的区别，后者经常在构建时重新设计工作。

## 何时使用

你通过输入 `/implement` 自己调用它，agent 不会自动使用它。它随 `disable-model-invocation: true` 一起发布，所以其他技能也不能调用它。无论 [ask-matt](https://aihero.dev/skills-ask-matt) 或 [to-tickets](https://aihero.dev/skills-to-tickets) 在哪里说"然后每个 ticket 用 `/implement`"。

工作目前在哪里决定了这是否是正确的技能：

| 工作是… | 使用 |
| --- | --- |
| tracker 上的一个 ticket | `/implement #42`，每个 [session](https://www.aihero.dev/ai-coding-dictionary/session) 一个 ticket，[clearing](https://www.aihero.dev/ai-coding-dictionary/clearing) tickets 之间 |
| 一个尚未拆分的 spec，构建跨越 sessions | 先用 [to-tickets](https://aihero.dev/skills-to-tickets)，然后每个 ticket 用 `/implement` |
| 一个 spec，构建很小 | 直接针对 spec 使用 `/implement` |
| 只在刚才的对话中，而且仍然很小 | 就在那里使用 `/implement`，在同一个窗口中 |
| 还没有写下来的东西 | [grill-with-docs](https://aihero.dev/skills-grill-with-docs)，如果没有代码库则用 [grill-me](https://aihero.dev/skills-grill-me) |
| 一个具体的行为，你想要测试优先，没有 spec | 直接使用 [tdd](https://aihero.dev/skills-tdd) |
| 已经构建好了，你想检查它 | 直接使用 [code-review](https://aihero.dev/skills-code-review) |

同 session 的情况值得单独提及，因为技能本身的第一行没有涵盖它。`SKILL.md` 说"spec 或 tickets"，这促使 [model](https://www.aihero.dev/ai-coding-dictionary/model) 寻找一个可能不存在的文件。如果计划只存在于对话中，调用时说明这一点。

## 前置条件

`implement` 提交到你所在的分支。它不会创建分支，也不会询问。在开始之前，检查你是否在正确的工作分支上。

如果 tickets 来自 [to-tickets](https://aihero.dev/skills-to-tickets)，[setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills) 配置了它们所在的 tracker。`code-review` 在关闭时读取相同的配置以找到原始 spec。

## 一次运行做什么

一次运行有五个步骤，按顺序：

1. 读取 ticket 或 spec 并确定 seams。
2. 在预先确定的 seams 处驱动 [tdd](https://aihero.dev/skills-tdd)，一次一个红绿切片。
3. 经常类型检查，运行单个测试文件。
4. 最后运行完整的测试套件一次。
5. 运行 [code-review](https://aihero.dev/skills-code-review)，然后提交到当前分支。

一次运行覆盖一个 ticket。[to-tickets](https://aihero.dev/skills-to-tickets) 产生的 tickets 是适合单个全新 [context window](https://www.aihero.dev/ai-coding-dictionary/context-window) 的追踪弹垂直切片，所以预期的节奏是：clear context，实现一个 ticket，提交，再次 clear。每个 ticket 都是独立的，所以你可以丢弃前一个 ticket 的 context。

## 预先确定的 seams

技能的核心思想是 **seam**，即你在不深入内部的情况下观察行为的公共边界。测试在 seams 处进行。当 seam 在代码存在之前就被确定时，测试会持续存在，你可以在不改变测试的情况下重写底层实现。

"预先确定"很重要，它也是技能最弱的地方。`implement` 内部没有任何东西来确定 seams。`tdd` 是那个询问的技能，它拒绝在未经确认的 seam 处编写测试。所以在实践中，协议要么在 spec 中上游发生，要么在运行的第一次交换中发生。如果 nowhere 发生，运行就变成了"直接写代码"，没有任何警告。在 spec 中命名 seams 可以阻止这种情况。

## 常见问题

**它完成了，但我的 ticket 仍然开着，验收标准仍未勾选。**

正确，而且这是预期的。`implement` 没有完成步骤。它在提交时结束，从不碰工作项。这在 GitHub Issues 和本地 markdown tracker 上都是一样的，所以这不是 tracker 集成问题。它也不处理 `code-review` 产生的结果，不勾选原始 issue 上的 `- [ ]` 框。自己关闭 ticket 并核对标准。这在依赖链中最重要，因为 `to-tickets` 将前沿定义为所有阻塞者都已关闭的 tickets。如果 nothing 被关闭，nothing 会显式解除阻塞。

**我可以一次指向所有 tickets，或者并行运行几个吗？**

不能用 `/implement`：一次调用，一个 ticket。对于整个 spec 一次运行，使用 [implement-spec](https://aihero.dev/skills-implement-spec)，它在前沿的每个 ticket 交给一个 [subagent](https://www.aihero.dev/ai-coding-dictionary/subagent)，在自己的 worktree 中，然后将结果合并到集成分支上。在一个 checkout 中并排运行多个 `/implement` session 比不受支持更糟。一份现场报告描述了一个 session 中的 `git commit --amend` 落到另一个 session 的提交上，stash 从 `refs/stash` 中消失，提交落在错误的分支上，一个下午三个 issue 中全部发生。sessions 共享一个工作目录、一个 index 和一个 HEAD。用户通过 git worktree 来解决这个问题，但 `refs/stash` 是跨 worktree 共享的，所以仅靠 worktree 无法解决 stash 的情况。

**它可以打开 pull request 而不是提交吗？**

没有内置支持。它直接提交到当前分支。有些人觉得这太急切了，因为代码在你验证它是否工作之前就落地了。没有配置标志，也没有 PR 模式。人们在调用时覆盖它（"提交到分支并打开 PR"），或者编辑技能的本地副本。当 agent 确实写 PR 时，[pr](https://aihero.dev/skills-pr) 塑造其正文。

**`code-review` 说看不到我的更改。**

`code-review` 审查的是 `git diff <fixed-point>...HEAD`，它排除了 staged 和工作区中的更改。`implement` 在提交之前运行它，所以除非已经存在临时提交，否则 diff 中没有什么可审查的。多人报告了这个问题，两边都没有修复。先提交，然后针对你从分支出来的点进行审查。

另外，有些人根本不希望审查在运行内部进行，因为 agent 审查自己刚刚写的代码时，会有利于自己的解决方案。在一个新 session 中针对固定点运行 [code-review](https://aihero.dev/skills-code-review) 是一个有效的替代方案。同样的偏见也是为什么该技能在单独的 sub-agents 中运行其两个轴。

**一个 ticket 烧了 150k tokens。我用错了吗？**

可能没有。更可能是 ticket 太大了。一次运行包括代码库探索、每个 seam 的红绿循环、完整套件和审查，所以一个非平凡的 ticket 超过 100k [tokens](https://www.aihero.dev/ai-coding-dictionary/token) 是正常的，而不是出问题的迹象。解决方案在上游。在 [to-tickets](https://aihero.dev/skills-to-tickets) 中调整 ticket 大小，使每个都适合一个全新的窗口。如果单个 ticket 一直超，拆分它，而不是提高 [effort](https://www.aihero.dev/ai-coding-dictionary/effort) 级别。

**`/implement #2` 在一个新 session 中工作在了完全不相关的东西上。**

agent 将 `#2` 解析为上下文中的另一个编号列表，比如 todo 文件或清单，而不是配置的 tracker。`implement` 现在从 issue tracker 获取传递的引用，并在开始前声明其标题，当引用模糊时询问。检查该标题是否与你想要的一致；传递 issue URL 或 `owner/repo#2` 可以彻底消除歧义。

## 正常工作的标志

- session 开头读取 ticket 或 spec 并复述它将要构建的内容，而不是问你该构建什么。
- 你可以在 trace 中看到实际的 `tdd` Skill tool call，而不仅仅是 diff 中出现的测试。
- typechecks 和单个测试文件在运行中反复运行，完整套件在最后运行一次。
- 运行在当前分支上到达提交，无需你提示继续。
- diff 是一个 ticket 的变更量：一个贯穿每个层的垂直切片，而不是几个 ticket 混在一起。

## 它在何处适用

`implement` 是主链的构建步骤：

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

它的邻居是 [to-tickets](https://aihero.dev/skills-to-tickets)，它产生它消费的 tickets 并声明决定它们顺序的阻塞边；[tdd](https://aihero.dev/skills-tdd)，它在每个 seam 处内部驱动；以及 [code-review](https://aihero.dev/skills-code-review)，它在提交前运行。它位于规划技能的下游并信任它们。它不重新验证交给它的内容的结构，所以一个结构糟糕的 map 或水平切片的 ticket 会按原样构建。

这就是 [wayfinder](https://aihero.dev/skills-wayfinder) 在 [to-spec](https://aihero.dev/skills-to-spec) 处合并到链上，而不是直接将地图循环到 `implement` 的原因。只有在工作结果很小的时候，才直接从地图到 `implement`。

[ask-matt](https://aihero.dev/skills-ask-matt) 是整个集合的路由器，当你不确定自己在哪个流程中时。

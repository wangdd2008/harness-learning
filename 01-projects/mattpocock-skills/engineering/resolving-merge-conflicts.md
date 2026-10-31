> **已归档。** 这个技能在 v1.3.0 中从插件中移除，不再维护。没有什么替代它：agent 在没有专用技能的情况下处理合并或变基冲突。该页面保留供参考。

## 作用

`resolving-merge-conflicts` 逐 hunk 处理正在进行的 git 合并或变基，然后运行项目的检查并完成操作。

它拒绝将冲突视为文本问题。在触及一个 hunk 之前，它追溯每一方到其 **[一级来源]**(https://www.aihero.dev/ai-coding-dictionary/primary-source)（提交消息、PR、原始 issue），所以它是在两种意图之间选择，而不是在两个文本块之间选择，并在它们兼容的地方保留两者。在它们不兼容的地方，它选择符合合并既定目标的一方，并命名权衡。它不会发明新的行为来隐藏冲突，也从不使用 `--abort`。它总是将合并带到完成的提交。

## 何时使用

输入 `/resolving-merge-conflicts`，或者当任务适合时 [agent](https://www.aihero.dev/ai-coding-dictionary/agent) 会自动使用它。

在 git 已经因无法自行解决的冲突而停止时使用它。它只针对你面前的冲突，而不是它两边的任何东西：

| 你的情况 | 技能 |
| --- | --- |
| 合并或变基中途，树中有冲突标记 | 这个 |
| 合并完成，某物现在行为异常，原因不明 | [diagnosing-bugs](https://aihero.dev/skills-diagnosing-bugs) |
| 规划如何切分工作以减少分支冲突 | 都不是：见下面的并行工作问题 |

## 一级来源胜过 `ours` 和 `theirs`

这个技能的存在是为了防止通过标志解决：`--ours`、`--theirs`，或手动删除看起来不那么重要的块，这样标记就消失了，构建就编译了。这种解决可以在语法上完美，但仍然会静默丢弃某人故意做的更改。

你无法保留你没有读过的意图。所以工作从历史（提交、PR、[tickets](https://www.aihero.dev/ai-coding-dictionary/ticket)）开始，然后才移到 diff。检查步骤的存在出于同样的原因。技能找到仓库自己的 [自动化检查](https://www.aihero.dev/ai-coding-dictionary/automated-check) 并在提交前运行它们，因为合并是 git 中最容易产生既满足两个分支又通不过任何一方测试的代码的地方。

## 常见问题

**Claude Code 自己就能很好地解决冲突。为什么需要这个技能？**

附加值在于"找到一级来源"和"运行反馈循环"步骤，否则你每次都必须手动提示。未受提示的 agent 通常会从 diff 本身产生一个合理的解决并停在那里。技能的价值在于它不会让 agent 跳过的两步：阅读每一方为什么存在，以及之后运行检查。这是一个好的 [model](https://www.aihero.dev/ai-coding-dictionary/model) 之上的小改进，这是设计如此。至少有一位读者预测这整个技能会随着 model 改进而变成 no-op。

**我应该让并行 agent 远离相同的文件，以避免冲突吗？**

大多数情况下不。在并行任务之间划分文件的成本比节省的要多，因为 agent 在合并冲突方面已经足够好，权衡并不像看起来那么严厉。值得遵守的一条纪律是先做大型重构。十个分支从一个重命名上分叉后，重命名落地的成本仍然很高。

关于并行 worktree 的用户报告有一个注意事项：当同级 [sessions](https://www.aihero.dev/ai-coding-dictionary/session) 在自己的树中构建一个 ticket 时，最佳合并方式是由写了变更的 session 来做，因为它已经知道意图。如果一个 agent 在最后解决所有人的冲突，它会丢失这个技能第二步必须重建的 [context](https://www.aihero.dev/ai-coding-dictionary/context)。

**为什么从不 `--abort`？**

中止会丢弃解决工作，让你下次尝试时回到同一个冲突， unchanged。这个技能是为合并将要发生的情况而写的。如果你已经决定它不应该发生，那是在调用之前做出的决定，而不是循环内部的分支。

## 正常工作的标志

- agent 在解决时引用提交消息、PR 或 issue，而不仅仅是 diff hunk。
- 每个 hunk 最终包含两边的行为，或有明确的注释说明什么被丢弃以及为什么。
- 结果中没有出现在任何一方上的东西。
- agent 在提交前找到类型检查、测试和格式化并运行它们 green，而不是在你注意到某些东西坏了之后。
- 你以干净树和操作完成结束，包括多提交变基中的每个剩余提交。

## 它在何处适用

一个随时可用的独立工具，不依赖任何其他技能：它在 git 停滞时开始，在树干净并提交时结束。它唯一的真正邻居是 [diagnosing-bugs](https://aihero.dev/skills-diagnosing-bugs)，在合并干净解决但合并代码行为异常时接管：那是一个诊断问题，而不是冲突问题。它在主想法到发布的流程之外，所以 [ask-matt](https://aihero.dev/skills-ask-matt) 是它前后运行的地图。

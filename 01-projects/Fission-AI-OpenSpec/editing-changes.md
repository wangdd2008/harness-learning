# 编辑与迭代变更

**变更中的每个产物都只是你可以随时编辑的 Markdown 文件。** 没有锁定的"规划阶段"，没有审批关卡，没有特殊的编辑模式要进入。想在开始构建后修改 proposal？打开 `proposal.md` 修改它。实现到一半发现设计是错的？修正 `design.md` 然后继续。这就是全部答案，而且这是有意设计的。

这一页适用于当你想"等等，我可以回去改那个吗？"的时刻。是的。以下是如何做，针对每种常见情况。

## 编辑任何东西的两种方式

你总是有这两种方式：

1. **直接编辑文件。** 产物是 `openspec/changes/<name>/` 中的纯 Markdown。在编辑器中打开 `proposal.md`、`design.md`、`tasks.md` 或 `specs/` 下的 delta spec 并修改它。不需要其他操作。

2. **让 AI 修改它。** 在聊天中，直接说出你的需求："Update the proposal to drop the caching idea and add a rate-limit section," 或 "the design should use a queue, not polling." AI 会为你编辑产物，使用变更的其余部分作为上下文。

用适合当时情况的方式。小的措辞调整？直接编辑文件。实质性的重新思考？让 AI 带着完整上下文来修改。

## "我已经开始了，怎么更新 proposal（或 specs）？"

直接更新它。同一个变更，精炼后的版本。

如果你使用的是扩展命令，自然的流程是：编辑产物，然后运行 `/opsx:continue` 从新状态继续，或者 `/opsx:apply` 继续按照更新后的计划实现。如果你使用的是默认的 `core` 命令，编辑产物然后运行 `/opsx:apply`；它会读取当前文件，所以它是根据产物现在的内容来构建的。

心理模型：产物是活跃的计划，而不是签字的合同。AI 总是根据它们的当前内容工作，所以编辑它们就是在引导工作。

```text
You: I want to change the approach in this change.

You: [编辑 design.md，或告诉 AI：]
     Update design.md to use a background job instead of a synchronous call.

AI:  Updated design.md. The task list still fits; want me to continue applying?

You: /opsx:apply
```

这回答了一个非常常见的问题：没有单独的"更新 proposal"命令，因为你不需要。文件就是真相的来源，编辑它（手动或通过 AI）就是更新。

## "实现后如何回去审查？"

你不需要"回去"，因为你从未离开过。工作流是流动的：审查、编辑和实现不是把你困住的顺序阶段。

具体来说，在一些 `/opsx:apply` 工作之后：

- 想重新检查计划？打开产物阅读它们，或在终端运行 `openspec show <change>` 以获得综合视图。
- 发现有需要改的地方？编辑产物（或让 AI 做），然后继续。
- 想要一个结构化的检查来确认代码是否符合计划？运行 `/opsx:verify`（扩展命令）。它会报告完整性、正确性和一致性，不会阻塞任何东西。参见 [工作流：验证](workflows.md#verify-check-your-work)。

没有什么"审查阶段"需要返回，因为审查是你随时都可以做的事情，包括实现之后。

## "我手动编辑了代码。如何与 OpenSpec 协调？"

这经常发生，而且没问题。你在编辑器里微调了一些东西，现在代码和产物不一致了。把它们同步回真实的状态：

- **代码现在是对的，spec 过时了。** 更新 delta spec（和相关的 tasks）来描述你实际交付的行为。在归档之前，spec 应该与事实相符，因为归档会将 spec 合并到你的真相来源中。
- **spec 是对的，代码漂移了。** 继续构建或修复，直到代码与 spec 相符。

一个快速发现不一致的方法是 `/opsx:verify`：它会读取你的产物和代码，并告诉你它们在哪里分叉。把它的输出当作待办清单来协调，协调完成后再归档。

原则：在归档时，你的 specs 成为记录的真相。所以在归档之前，让 specs 诚实地反映代码做什么。手动编辑是受欢迎的；只是不要让它们悄悄地把 spec 弄脱同步。

## 精炼你不满意的 proposal

如果生成的 proposal 没达到要求，你有三个好选择：

- **就地迭代。** 告诉 AI 哪里不对（"范围太广了，去掉 admin 功能"）然后让它修改。最便宜，通常也是对的。
- **先探索，再重新提出。** 如果问题出在思路本身不清楚，退回到 `/opsx:explore`，想清楚，然后让更清晰的 proposal 从中诞生。参见 [探索优先](explore.md)。
- **重新开始。** 如果意图已经根本改变了，一个新的变更可能比修补旧的更清晰。

最后一个选择有自己的决策指南，接下来是。

## 何时更新 vs 开始新的变更

简而言之：**当是同一项工作的精炼时更新；当意图根本改变或范围爆炸到完全不同的工作时重新开始。**

- 目标相同，方法更好？更新。
- 范围缩小（先交付 MVP，更多以后再说）？更新，然后归档，然后为第二阶段创建新变更。
- 问题本身改变了（"添加 dark mode"变成了"构建完整的主题系统"）？新变更。

完整的流程图和示例在 [工作流：何时更新 vs 重新开始](workflows.md#when-to-update-vs-start-fresh) 和 [OPSX：何时更新 vs 重新开始](opsx.md#when-to-update-vs-start-fresh) 中有更深入的讨论。

## 关于 tasks 的说明

`tasks.md` 是一个活跃的检查清单，不是冻结的计划。随着你实现，你可以添加新发现的任务、删除不必要的任务，或重新排序它们。AI 在 `/opsx:apply` 期间会在完成任务时勾选它们，如果你之后回来，它会从第一个未勾选的任务继续。在飞行中编辑列表是预料之中的。

## 下一步去哪

- [工作流](workflows.md) - 模式，以及更新 vs 新开始的决策指南
- [审查变更](reviewing-changes.md) - 在构建前对计划的快速两分钟检查
- [探索优先](explore.md) - 当想法需要重新思考时退回到这里
- [命令](commands.md) - `/opsx:continue`、`/opsx:apply` 和 `/opsx:verify` 的详细说明
- [概念：产物](concepts.md#artifacts) - 每个产物的作用

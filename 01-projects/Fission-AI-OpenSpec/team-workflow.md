# OpenSpec 在团队中

其他指南中的所有内容，无论你是独自工作还是二十人团队，工作方式都相同。在团队中发生变化的是边缘问题：specs 放在哪里、队友如何审查计划，以及这一切如何融入你们已有的 pull-request 流程？

简短回答：变更只是文件，OpenSpec 从不碰 git。所以它能融入你们已有的工作流，而不是取代它。这一页详细说明了那些行之有效的约定。

## 一条规则：OpenSpec 不碰 git

OpenSpec 读取和写入 `openspec/` 下的纯 Markdown。它从不 commit、branch、push 或 pull — 也从不会克隆或同步 [store](stores-beta/user-guide.md)。这意味着：

- **你把 `openspec/` 当作源代码一样提交。** Specs、活跃变更和归档是你们项目历史的一部分。（是的，提交整个文件夹 — 参见 [FAQ](faq.md#should-i-commit-the-openspec-folder-to-git)。）
- **变更是一个像代码一样版本控制的文件夹。** `openspec/changes/add-dark-mode/` 就是分支上的一个文件夹。
- **下面的一切都是约定，不是强制。** OpenSpec 不会强迫你这么做；它只是很干净地融入。

## 日常循环

行之有效的工作流是将变更映射到分支和 pull request：

```
git switch -c add-dark-mode        像往常一样开始分支
   │
/opsx:propose add-dark-mode        起草计划（proposal + specs + tasks）
   │
REVIEW THE PLAN                    在任何代码之前阅读 — 参见审查变更
   │
/opsx:apply                        构建它；产物和代码一起变化
   │
git commit && open a PR            PR 包含 spec delta AND 代码
   │
teammate reviews, merges
   │
/opsx:archive                      将 delta 折叠到 specs/，将变更移到 archive/
```

计划和代码在同一个分支中并排存在，所以你的队友可以一起审查两者，六个月后归档的 spec 仍然可以解释为什么代码是那个样子。

## 在 pull request 中审查 specs

这就是团队感受到回报的地方。当 PR 包含变更的 delta spec 时，审查者会得到原始 diff 永远无法提供的东西：**这个变更应该做什么的纯语言说明**，在他们阅读任何一行代码之前。

审查者的推荐审查顺序：

1. **阅读 `proposal.md`** — 这是正确的问题和范围吗？
2. **阅读 `specs/` 下的 delta** — "完成"被正确定义了吗？（这就是 [审查变更](reviewing-changes.md) 的两分钟审查，现在发生在 PR 中。）
3. **然后阅读代码 diff** — 它是否准确交付了那些需求？

审查者如果不同意 *方法*，可以在 proposal 上便宜地指出，而不是在 300 行代码中反复争论。把 delta spec 放在 PR 描述顶部附近，或指向审查者变更文件夹，让他们从那里开始。

## 何时归档

归档将变更的 deltas 折叠到你们的主 `openspec/specs/` 中，并将变更文件夹移到 `openspec/changes/archive/YYYY-MM-DD-<name>/`。因为 `specs/` 是 **共享的真相来源**，在团队中归档的时机很重要。两种可行的约定：

- **PR 合并后归档（推荐）。** 分支承载活跃变更；一旦合并到主分支，就在那里归档（通常是一个小的后续提交或计划清理）。这让共享的 `specs/` 只随实际交付的工作向前推进。
- **在 PR 内归档。** 对小型团队更简单：添加代码的同一个 PR 也同步和归档。代价是你的 `specs/` diff 和代码 diff 一起落地，这可能让 PR 更嘈杂。

选择一个并保持一致。无论哪种方式，`/opsx:archive` 都会检查任务是否完成，并在需要时提示先同步，所以不会意外合并半成品。

## 两个人，并行变更

因为变更是独立的文件夹，它们不会冲突：

- **不同的变更，不同的人 — 没问题。** `add-dark-mode` 和 `rate-limit-login` 是不同分支上的不同文件夹；它们直到都归档前不会互相接触。
- **一个变更，一个负责人。** 两个人编辑同一个变更文件夹就像两个人编辑同一个文件一样。让一个变更保持单一作者，或者拆分为两个变更（这是 [控制大小](writing-specs.md#right-size-the-change) 的另一个原因）。
- **唯一可能冲突的地方是 `specs/`。** 如果两个变更都修改了 *同一个* 需求，归档第二个时会在 `openspec/specs/…/spec.md` 中冲突 — 像任何合并冲突一样解决它，保留反映现实的需求。这很少见，而且它是一个功能：git 在告诉你两个变更对系统应该如何行为存在分歧。

## 当规划超出单个仓库时

以上所有都假设计划存在于代码仓库自身的 `openspec/` 文件夹中，这是正确的默认。当你们的规划真正跨越多个仓库或团队时 — 一个功能触及三个服务，或者需求由一个团队拥有而其他团队消费 — 这就是 beta 的 **stores** 功能的作用：规划获得自己的仓库，任何代码仓库都可以指向它。从 [Stores User Guide](stores-beta/user-guide.md) 开始。

## 下一步去哪

- [审查变更](reviewing-changes.md) — 现在在你的 PR 内部的审查流程。
- [编写好的规格说明](writing-specs.md) — 包括如何控制变更大小以适配一个分支。
- [Stores User Guide](stores-beta/user-guide.md) — 跨越仓库和团队的规划。

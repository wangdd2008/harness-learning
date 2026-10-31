# 示例与配方

真实的变更，从头到尾。每个配方展示了你会输入的命令和你会看到的反馈，这样你就可以将情况与模式匹配并复制它。这些使用默认的 **core** 命令（`propose`、`explore`、`apply`、`update`、`sync`、`archive`）；在需要扩展集的地方会注明。

在开始之前提醒一下：像 `/opsx:propose` 这样的斜杠命令在你的 **AI 助手聊天** 中输入，而 `openspec` 命令在你的 **终端** 中运行。如果你不熟悉，先阅读 [命令如何工作](how-commands-work.md)。下面的对话记录中，`You:` 和 `AI:` 代表聊天，以 `$` 开头的行是终端。

> **还不确定要构建什么？** 大多数配方在用 `/opsx:explore` 想清楚之后会更清晰。开始之前先看看 [探索优先](explore.md)。[配方 3](#配方-3-在承诺之前探索) 展示了它的实际应用。

## 配方 1：小功能，快速路径

**何时使用：** 你知道想要什么，而且是一个可控的工作片段。这是最常用的配方。

整个流程就三个命令。Propose、build、archive。

```text
You: /opsx:propose add-logout-button

AI:  已创建 openspec/changes/add-logout-button/
     ✓ proposal.md — 为什么和是什么
     ✓ specs/      — 新需求和场景
     ✓ design.md   — 技术方案
     ✓ tasks.md    — 实现检查清单
     准备实现。运行 /opsx:apply。
```

现在阅读计划。打开 proposal 和 delta spec。这是 OpenSpec 设计的时刻：在错误还只是一个段落时抓住它，而不是 400 行代码之后。如果有什么不对，直接编辑任何产物，然后继续。

```text
You: /opsx:apply

AI:  执行任务中...
     ✓ 1.1 在 header 中添加 logout 按钮
     ✓ 1.2 点击时清除 session
     ✓ 1.3 添加确认对话框
     所有任务完成！

You: /opsx:archive

AI:  正在归档 add-logout-button...
     ✓ 已合并 specs 到 openspec/specs/auth/spec.md
     ✓ 已移动到 openspec/changes/archive/2026-06-22-add-logout-button/
     完成。准备下一个变更。
```

就是这样。logout 行为现在是 specs 的一部分，变更已归档并保留了完整上下文。

## 配方 2：Bug 修复

**何时使用：** 有些东西坏了，你想将修复记录为对行为的蓄意变更，而不是一个神秘提交。

Bug 修复与功能完全一样。区别在于你如何构建 proposal：描述 *正确* 的行为，而不是仅仅"修复 bug"。

```text
You: /opsx:propose fix-login-redirect-loop

AI:  已创建变更。proposal 捕获了当前破损的行为和
     预期行为。delta spec 将重定向
     需求修改为现在精确且可测试。
     准备实现。
```

因为修复以 `MODIFIED` 需求的形式落地，并带有一个新场景，下一个人（或下一个 AI 会话）看到的不仅是你修复了它，还有"正确"意味着什么。然后像往常一样 `/opsx:apply` 和 `/opsx:archive`。

提示：对于修复来说，一个好的场景就是文字形式的回归测试。"GIVEN 一个已登出的用户，WHEN 他们提交有效凭证时，THEN 他们到达 dashboard 且不再被重定向。" 写下这个，实现就有了清晰的目标。

## 配方 3：在承诺之前探索

**何时使用：** 你有问题但还没有计划。你不确定要构建什么，或者哪种方法是对的。

从 `/opsx:explore` 开始。它是一个没有结构的思考伙伴。它从不写代码，也从不写其他内容，除非你要求它记录你决定的内容，或在它提供时同意。它读取你的代码库并帮助你决定。

```text
You: /opsx:explore

AI:  你想探索什么？

You: 页面加载感觉很慢，但不知道时间花在哪里。

AI:  让我看看...我找到了三个可能的罪魁祸首：
     1. 产品列表上大的未优化图片
     2. ProductList 中阻塞渲染的同步数据获取
     3. 上下文变化导致的重新渲染
     我们应该先解决哪个？

You: 数据获取那个。

You: /opsx:propose optimize-product-list-fetching

AI:  创建了变更，proposal 基于我们刚才的发现。
     准备实现。
```

探索在 *你花一个变更在它上面之前* 澄清了你的思路。当洞察结晶时，提出它，AI 会将上下文带入产物。

## 配方 4：同时处理两个变更

**何时使用：** 你正在做功能到一半，一个紧急修复插队了。

变更是独立的文件夹，所以并行工作不会冲突。开始修复，交付它，然后回到你离开功能的地方。

```text
You: 我正在做 add-dark-mode，但我现在需要修复一个登录 bug。

You: /opsx:propose fix-login-redirect

AI:  已创建 openspec/changes/fix-login-redirect/。准备实现。

You: /opsx:apply

AI:  已实现修复。所有任务完成。

You: /opsx:archive

AI:  ✓ 已归档 fix-login-redirect。

You: 回到 dark mode。

You: /opsx:apply add-dark-mode

AI:  继续 add-dark-mode...
     从任务 2.3 开始：更新 Header...
```

在 `/opsx:apply add-dark-mode` 中命名变更是指向特定变更的方式，当有多个活跃变更时。因为任务完成度追踪在 `tasks.md` 中，AI 确切知道你停在哪里。

当有多个变更完成时，扩展的 `/opsx:bulk-archive` 会将它们一起归档，并通过检查实际实现的内容来解决 spec 冲突。参见 [工作流](workflows.md#parallel-changes)。

## 配方 5：没有行为变更的重构

**何时使用：** 你正在重构代码，外部可见行为应保持不变。

这是有趣的情况，因为纯重构 *没有东西要添加到 specs*。行为契约不变；只有实现变了。所以工作存在于 design 和 tasks 中，而 spec delta 是空的或缺失的。

```text
You: /opsx:propose refactor-payment-module

AI:  已创建变更。proposal 说明了目标（拆分
     payment 模块，无行为变更）和 design 捕获了
     新结构。没有 spec 变更，因为行为相同。
     准备实现。
```

通过在变更的 `.openspec.yaml` 中显式设置 `skip_specs: true` 来声明空 delta：

```yaml
schema: spec-driven
skip_specs: true
```

没有这个标记，`openspec validate` 会拒绝零 delta 的变更（所以被遗忘的 specs 阶段仍会被捕获）；有了它，验证通过，`openspec status` 将 specs 阶段显示为显式跳过而非待处理。如果重构最终确实改变了行为，从 `.openspec.yaml` 中移除 `skip_specs` 并编写 delta specs — 验证将标记加上 spec 文件的过时标记视为冲突，所以陈旧的标记不会默默存在。

归档带标记的变更不需要额外的标志（没有 delta 要合并）。`--skip-specs` 标志告诉终端命令显式跳过 spec 步骤：

```bash
$ openspec archive refactor-payment-module --skip-specs
```

同样的标志对工具、CI 和仅文档变更很有用。原则：specs 描述行为，所以如果行为没变，spec 也不应该变。参见 [概念](concepts.md#what-a-spec-is-and-is-not)。

## 配方 6：逐步控制（扩展命令）

**何时使用：** 复杂或有风险的变更，你想在继续之前审查每个产物。

核心的 `/opsx:propose` 一次性起草所有内容。当你想一步一步来时，打开扩展命令：

```bash
$ openspec config profile      # 选择扩展工作流
$ openspec update              # 应用到这个项目
```

现在你可以增量地脚手架和构建：

```text
You: /opsx:new add-2fa

AI:  已创建 openspec/changes/add-2fa/。准备创建：proposal。

You: /opsx:continue

AI:  已创建 proposal.md。现在可用：specs, design。

You: /opsx:continue

AI:  已创建 specs/auth/spec.md。现在可用：design。
```

每个产物落地时审查它，自由编辑，满意后继续。当你想一次性起草剩余部分时，`/opsx:ff` 快速推进剩余的规划产物。归档前，`/opsx:verify` 检查实现是否与 specs 一致。参见 [工作流](workflows.md#opsxff-vs-opsxcontinue)。

## 配方 7：动手学习整个循环

**何时使用：** 你已安装 OpenSpec，想在你自己的代码上 *感受* 工作流，而不是一个玩具示例。

打开扩展命令（参见配方 6），然后：

```text
You: /opsx:onboard

AI:  欢迎来到 OpenSpec！我将带你完成一个完整的变更
     使用你的实际代码库。让我扫描一个小的、安全的
     改进，我们可以一起做...
```

`/opsx:onboard` 会找到一个真实的（小的）改进，为它创建一个变更，实现它，并归档它，解释每一步。需要 15 到 30 分钟，并留下一个你可以保留或丢弃的真实变更。这是最温和的学习方式。参见 [命令](commands.md#opsxonboard)。

## 从终端检查工作

任何时候，你都可以在终端中检查状态：

```bash
$ openspec list                      # 活跃变更
$ openspec show add-dark-mode        # 一个变更的详细信息
$ openspec validate add-dark-mode    # 检查结构
$ openspec view                      # 交互式仪表板
```

这些是阅读和检查工具。提出建议和构建仍通过聊天中的斜杠命令进行。完整详情参见 [CLI 参考](cli.md)。

## 下一步去哪

- [探索优先](explore.md)：当你不确定时的推荐起点
- [工作流](workflows.md)：上面的模式，以及何时使用每个的决策指南
- [命令](commands.md)：每个斜杠命令的详细说明
- [入门指南](getting-started.md)：规范的第一个变更指南
- [概念](concepts.md)：为什么各个部分以这种方式组合在一起

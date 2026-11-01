# 在现有项目中使用 OpenSpec

**你不需要在开始时记录整个代码库。你只为你将要变更的部分编写 specs。** 这是关于在现有项目中采用 OpenSpec 最重要的事情，也是为什么 OpenSpec 是 brownfield-first 的。

一个常见的担忧听起来像这样："我的应用有 80,000 行代码。我是否需要在使用 OpenSpec 之前为所有部分编写 specs？" 不需要。你会讨厌那样，我们也一样。OpenSpec 一次变更一个地增长你的 specs。你的第一个变更记录了它触及的部分，下一个变更记录了它的部分，几个月后你的 specs 会自然地在你实际做的工作周围填充起来。

本指南展示了如何在不煮沸海洋的情况下从第一天开始。

## 三十秒版本

```bash
$ cd your-existing-project
$ openspec init          # 添加 openspec/ 和你的 AI 工具的命令
```

然后，在你的 AI 聊天中：

```text
/opsx:explore            # 可选：让 AI 读取你将触及的区域
/opsx:propose <一个你实际需要的小变更>
/opsx:apply
/opsx:archive
```

你的 specs 现在精确描述了该变更触及的系统部分，其他什么都没说。这是正确的。你不用再担心另外 80,000 行代码了。

## 为什么 delta-first 是整个技巧

OpenSpec 变更以 **delta** 的形式编写：`ADDED`、`MODIFIED`、`REMOVED`。Delta 描述相对于当前行为的变化，而不是整个系统。

这正是 brownfield 工作所需要的。你很少从无到有地构建。你是在添加字段、修复重定向、收紧超时。Delta 让你精确地指定那一个变更，而无需先写一个 40 页的周围系统规格说明。

所以你的 `openspec/specs/` 目录开始时不是满的。它几乎为空并随着时间积累。每个归档的变更都会合并它的 delta。`auth/` 的 spec 只有在你做了几个 auth 变更之后才变得详尽，而这正是你希望它详尽的时候。

如果你想了解更深层次的机制，参见 [概念：Delta Specs](concepts.md#delta-specs)。

## 在真实代码库上的第一次变更

选择小而真实的东西。不是玩具，不是重写。一个你本周本来就要做的变更。小的第一次变更用低风险教你工作流。

**第 1 步：让 AI 读取相关区域。** 这是 `/opsx:explore` 在不熟悉或大型代码库上的价值所在。指向你将要触及的部分，让它在提出任何内容之前先了解系统。

```text
You: /opsx:explore

AI:  你想探索什么？

You: 我需要为我们的公共 API 添加限流，但我不确定
     请求目前如何通过中间件。

AI:  让我追踪一下...[读取 router、中间件栈和配置]
     请求命中 Express，通过 auth 中间件，然后到达你的
     controllers。目前没有限流层。最干净的
     插入点是 auth 之后的一个中间件。要确定范围吗？
```

注意 AI 现在理解了你的实际结构，所以它写的 proposal 会适合你的代码，而不是通用模板。在大型代码库上，这个单一习惯能避免最多的痛苦。参见 [探索优先](explore.md)。

**第 2 步：提出变更。** Proposal 和它的 delta spec 只捕捉这个变更。

```text
You: /opsx:propose add-api-rate-limiting
```

**第 3 步：构建和归档** 用 `/opsx:apply` 和 `/opsx:archive`，与任何变更一样。归档后，你为你的限流行为有了一个真正的 spec，诞生于一个你本来就需要的变更。

## 想要导游吗？使用 onboard

如果你想在自己的代码上看完整循环的发生并带有解说，扩展命令 `/opsx:onboard` 正好做这个：它扫描你的代码库寻找一个小的、安全的改进，然后带你经历提出、构建和归档的每一步。

先打开扩展命令：

```bash
$ openspec config profile      # 选择扩展工作流
$ openspec update              # 应用到这个项目
```

然后在聊天中：

```text
/opsx:onboard
```

这是最温和的引入方式，在真实项目上，它留下一个真正的（小的）变更，你可以保留或丢弃。参见 [命令](commands.md#opsxonboard)。

## "但我已经有需求文档了"

也许你有一个 PRD、SRS、正式 spec，甚至 TLA+ 模型。很好。你不会整体导入它们，也不会扔掉它们。

将现有文档视为 **探索的源材料**，而不是要转换的 specs。当你开始一个变更时，粘贴或指向 AI 到相关部分，让它从中塑造一个专注的 OpenSpec delta。Delta 以 OpenSpec 可测试的需求和场景形式捕捉你正在改变的行为。你的原始文档留在原处作为背景。

诚实的原因：OpenSpec specs 故意以行为为先并限定在变更范围内。一个 40 页的 PRD 是不同工作不同职责的产物。强制一次性批量转换往往会产生一个庞大的、没人信任的过时 spec。让 specs 从真实变更中增长能保持它们的准确性。

```text
You: /opsx:explore
You: 这是我们 PRD 中关于 checkout 的部分。我接下来
     要实现 "guest checkout" 需求。
     [粘贴相关需求]
AI:  [阅读它，提出澄清问题，然后帮助确定变更范围]
You: /opsx:propose add-guest-checkout
```

## 在大型代码库中组织 specs

Specs 存放在 `openspec/specs/` 下，按 **域** 分组：一个与你的团队思考系统方式相匹配的逻辑区域。你不需要 upfront 设计整个分类法。在第一个变更触及该区域时创建一个域文件夹。

常见的域划分方式：

- **按功能区域：** `auth/`、`payments/`、`search/`
- **按组件：** `api/`、`frontend/`、`workers/`
- **按限界上下文：** `ordering/`、`fulfillment/`、`inventory/`

选择让新人也能点头的划分方式。你可以稍后完善。参见 [概念：Specs](concepts.md#specs)。

## Monorepos 和跨仓库的工作

对于 monorepo，最简单的模型是在仓库根目录放一个 `openspec/` 文件夹，域映射到你的包或服务。这覆盖了大多数团队。

如果你的工作真正跨越 **多个仓库**（或几个你视为独立的包），OpenSpec 有一个 beta 的 **stores** 功能：规划存在于自己的独立仓库中，你的任何代码仓库都可以引用，所以计划不必居住在某个仓库的 `openspec/` 文件夹内。它是 beta 功能，所以将其命令和状态视为不断变化的。从 [Stores User Guide](stores-beta/user-guide.md) 开始了解心智模型和最小有用路径。

## 一些诚实的警告

- **抵制回填一切的冲动。** 为不打算更改的代码编写 specs 感觉很有成效，但通常不是。这些 specs 会变旧，因为没有什么强迫它们跟踪现实。让真实变更驱动你的 specs。
- **保持早期变更小而聚焦。** 你的前几个变更与学习和交付一样重要。紧凑的范围让循环快速、教训便宜。
- **将 `openspec/` 提交到 git。** 你的 specs 和归档属于版本控制，与它们描述的代码并列。
- **给 AI 上下文。** 在大型代码库上，如果约定很强，填写 `openspec/config.yaml` 的 `context:`，这样每个 proposal 都会尊重你的栈和模式。参见 [自定义配置](customization.md#project-configuration)。

## 下一步去哪

- [探索优先](explore.md) - 在更改代码之前理解代码的关键习惯
- [入门指南](getting-started.md) - 完整的第一次变更指南
- [编辑与迭代变更](editing-changes.md) - 随着学习调整变更
- [概念：Delta Specs](concepts.md#delta-specs) - 为什么 delta 让 brownfield 工作变得干净
- [自定义配置](customization.md) - 教 OpenSpec 你项目的约定

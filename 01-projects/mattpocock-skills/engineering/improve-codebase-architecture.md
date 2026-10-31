## 作用

`improve-codebase-architecture` 调查代码库中的**深化机会**。这些是一些可以从浅模块（接口几乎和它隐藏的东西一样复杂）变为深模块的地方。它会将它们写成一个自包含的 HTML 报告，然后对你选择的那个进行 [grilling](https://www.aihero.dev/ai-coding-dictionary/grilling)。

它永远不会修改代码。整个运行产生一次对话和一个你操作系统临时目录中的 HTML 文件。你稍后在单独的 [session](https://www.aihero.dev/ai-coding-dictionary/session) 中通过正常的构建流程进行重构。这使它成为一个调查工具，而不是重构工具，所以你可以在一个你还没有准备好触碰的代码库上运行它。

两个过滤器阻止报告变成通用的清理建议。首先，每个候选必须通过**删除测试**：如果你移除了这个模块，它的复杂性是会移到更小的接口后面，还是会扩散到调用者中？只有第一种情况才会得到卡片。其次，除非你指向特定区域，否则它会先读取最近的提交历史，并将扫描集中在经常变更的路径上。在没有人触碰的代码中的深化是一次永远收不回成本的重构。

## 何时使用

你通过输入 `/improve-codebase-architecture` 来调用它；[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 不会自动使用它。

它不是主构建循环中的步骤。你定期运行它来排队更多改善代码库的工作。人们在四种情况下使用它：

| 情况 | 如何使用 |
| --- | --- |
| 例行维护 | 每隔几天运行一次，或者当你有空闲时间时，这样结构不会在功能之间腐烂。 |
| 大型构建之前 | 指向 [spec](https://www.aihero.dev/ai-coding-dictionary/spec) 并问"如何让这个变更容易？"这是对它最有效的 prompt。 |
| 棕地审计 | 在一个大型、非结构化或 [vibe-coded](https://www.aihero.dev/ai-coding-dictionary/vibe-coding) 的仓库上运行，看看它的状况如何。 |
| 遗留测试工作 | 用它来在无法测试的代码上写测试之前找到缺失的 seams。 |

与兄弟技能的区别：

- 对于你已经选定的一个模块，使用 [codebase-design](https://aihero.dev/skills-codebase-design)。这个技能找到要处理的模块，`codebase-design` 是设计它的地方。
- 对于整个一个 session 装不下的工作，使用 [wayfinder](https://aihero.dev/skills-wayfinder)。
- 对于"这个特定的东西坏了"，使用 [diagnosing-bugs](https://aihero.dev/skills-diagnosing-bugs)。当真正的发现是没有好的 seam 来锁定 bug 时，它会把你送到这里。

## 前置条件

运行它没有任何前置条件。如果 `GLOSSARY.md` 或 `docs/adr/` 中的 ADR 存在，它会读取它们并使用你自己领域的名词。然后候选会显示为"深化订单录入模块"，而不是"重构 FooBarHandler"。

它会在两个地方写入。报告会写到 `<tmpdir>/architecture-review-<timestamp>.html`，在仓库外部。在 grilling 循环期间，它会在 `GLOSSARY.md` 中添加或细化术语，如果文件不存在则创建它。它还会提议将一个被拒绝的候选记录为 ADR，这样未来的运行就不会再建议它。

## 深度，以及寻找它的报告

技能建立在一种思想上：**深度**。深模块将大量行为放在一个小而稳定的接口后面。浅模块通过一个几乎和它下面的代码一样宽的接口暴露其实现。报告寻找三种浅的形式：

- 仅为了可测试性而提取的纯函数，而真正的 bug 在于调用者如何使用它们（没有 **locality**）。
- 跨越其 **seams** 泄漏的模块。
- 一个你不打开五个文件就无法理解的概念。

对于每一种，它提出修复它的深化方案。

每个候选是一张卡片，包含涉及的文件、摩擦、一个英文解决方案、以 **locality** 和 **leverage** 表示的收益、前后对比图，以及一个强度徽章。

| 徽章 | 对你的意义 |
| --- | --- |
| `Strong` | 删除测试明显通过，摩擦是真实的。认真对待这些。 |
| `Worth exploring` | 合理的深化，但收益取决于代码下一步的方向。 |
| `Speculative` | 为了完整性而包含。你可以忽略大部分。 |

报告以**首要推荐**结束，即它会先做的候选。然后技能停下来问你想要探索哪个候选。此时你还没有决定任何事情，也没有代码被修改。

## 选择候选后会发生什么

当你选择一个候选时，一个 [grilling](https://www.aihero.dev/skills-grilling) session 会在它上面开始。它涵盖约束、哪些东西放在 seam 后面、哪些测试能存活，以及深化后的接口应该是什么样子。那次 session 的输出是一个决策，而不是 diff。从那里开始，正常流程适用：将决策带入 [to-spec](https://aihero.dev/skills-to-spec)，然后 [to-tickets](https://aihero.dev/skills-to-tickets)，然后 [implement](https://aihero.dev/skills-implement)。

## 常见问题

**它花了一个小时围绕一个想法问我，而不是给我看选项。可以关掉吗？**

可以。在调用它时说"不要问我，只给我看报告"。这是关于这个技能最常见的抱怨。一位用户喜欢它"是获得改进分析的一个便捷方式"，但 grilling 循环被添加后，发现它"几乎无法使用"。设计意图是报告先出现，grilling 只在你选择的候选上开始。但较弱的 [models](https://www.aihero.dev/ai-coding-dictionary/model) 会直接跳到关于它第一个想法的访谈。结果因模型而异很大。这是一个开放问题，技能目前还没有文档化的无 grill 模式。

**报告打开为未样式的原始 HTML，没有图表。发生了什么？**

报告从 CDN 加载 Tailwind 和 Mermaid，所以打开时需要网络访问。如果某些东西阻止了这些脚本，页面会崩溃且没有错误。在报告的情况下，安全钩子需要 SRI 哈希。agent 添加了它们，但 CDN 向浏览器提供的字节与计算哈希的 `curl` 不同，所以浏览器阻止了脚本。离线或锁定环境有同样的问题。agent 看不到它，因为它从不渲染页面。作为变通方法，请求内联 CSS 和手绘 SVG 图而不是 CDN 设置。这是一个开放问题。

**它给了我十二个候选。我应该在同一个 session 中处理它们，还是启动一个新的？**

每个 session 处理一个。如果你在同一个对话中处理多个，[context window](https://www.aihero.dev/ai-coding-dictionary/context-window) 会同时充满报告、grilling、领域模型编辑和代码更改。报告只是一个临时文件，所以向前推进候选，而不是文件。选择一个，grilling 它，然后将决策带入 `/to-spec`。把其余的变成 [tickets](https://www.aihero.dev/ai-coding-dictionary/ticket)，以后可以单独处理。把选定的改进放进 spec 而不是直接进入实现。人们经常问这个问题，技能本身没有记录这个工作流。

**我应该怎么 prompt 它？**

用你接下来要构建的东西来 prompt。如果即将有一个大型构建，指向 spec 并问"如何让这个变容易？"没有 prompt 的运行会自己寻找热点。这对例行维护没问题，但方向使报告可操作。

**它在大型遗留代码库上工作吗？**

部分。它在缺乏一致结构的大型现有代码库上工作得很好，也是任何一次性结构设置后的推荐维护工具。但失控项目的用户报告说它"帮了一点，但仍然似乎无法胜任"。一位拥有八年遗留代码库的开发人员报告说模型绕圈子，尽管相同的技能在整洁的仓库上产生清晰的图。目前还没有专门的 `/refactor` 技能。如果代码库没有共享词汇，先运行 [grill-with-docs](https://aihero.dev/skills-grill-with-docs) 创建一个。这通常会使这个技能的输出好得多。

**这和 `/codebase-design` 有什么不同？**

`/codebase-design` 是参考，而不是 session 驱动器。它提供词汇（module、interface、depth、seam、adapter、leverage、locality），而这个技能使用它。如果你给一个新 agent `/codebase-design` 作为任务，它会以一种已知的方式失败。它没有自己的流程可循，所以 agent 会发明一个，再次探索代码，然后运行很长时间才问你任何问题。运行这个技能，让它使用那个。

**它会告诉我代码库没问题吗？**

很少，所以在你开始之前要知道这一点。技能的存在是为了输出发现，所以它倾向于产生候选而不是得出 nothing is wrong 的结论。使用强度徽章来纠正这一点。如果报告中的每个候选都是 `Speculative`，技能没有找到任何东西。

**它在 Codex 或其他 harness 中工作吗？**

部分。探索步骤直接命名了 Claude Code 的 `Agent` 工具的 `subagent_type=Explore`。没有该工具的 [harness](https://www.aihero.dev/ai-coding-dictionary/harness) 可能会跳过并行探索而不是使用自己的等效工具。技能仍然运行，但扫描不够彻底。有人提议了一个 harness 中立的 rewrite，但尚未合并。

**如何在 TypeScript 中实际实现深模块？**

技能没有提供好的答案。人们经常要求一个 `TYPESCRIPT.md`，包含具体的文件和模块布局。它不存在。技能告诉你深化属于哪里以及什么放在 seam 后面。你必须自己把它转化为包或目录结构。

## 正常工作的标志

- 候选命名你领域的概念，而不是虚构的类名："订单录入模块"，而不是"FooBarHandler"。
- 候选在你最近编辑的文件中，而不是仓库中没有人触碰的部分。
- 运行期间没有代码更改。唯一的新文件是你临时目录中的 HTML 报告。
- 它在报告后停下来问你想要哪个候选。它不会自己继续。
- 每张卡片以 locality 或 leverage 解释收益，并说哪些测试变得更简单，而不仅仅是"这更干净"。
- 当你因为一个持久的理由拒绝一个候选时，它提议记录一个 ADR，这样下一次运行就不会再建议它。

## 它在何处适用

`improve-codebase-architecture` 是**定期维护**。你每隔几天运行一次，在任何链之外，排队工作，而不是做它。它的邻居：

- [codebase-design](https://aihero.dev/skills-codebase-design) 拥有每个候选使用的深度和 seam 词汇。
- [grilling](https://aihero.dev/skills-grilling) 在你选择候选后走决策树。
- [domain-modeling](https://aihero.dev/skills-domain-modeling) 在你做决定时保持 `GLOSSARY.md` 和 ADR 最新。

它的输出是一个想法，回到主构建流程的 [grill-with-docs](https://aihero.dev/skills-grill-with-docs) 或 [to-spec](https://aihero.dev/skills-to-spec)。它在主流程末端的对应物是 [retro](https://aihero.dev/skills-retro)。这个技能改进 agent 工作的代码，而 `retro` 在构建后改进它周围的环境（检查、标准、引导文件）。对于哪种技能适合哪种情况，[ask-matt](https://aihero.dev/skills-ask-matt) 是整个集合的路由器。

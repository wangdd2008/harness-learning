## 作用

`tdd` 通过测试优先的方式构建功能或修复 bug：先写一个失败的测试，然后只写刚好让它通过的代码，接着处理下一个行为。它承载了使这个循环产生值得保留的测试的标准：什么是好的测试、测试放在哪里、mock 的用途，以及让测试套件毫无价值的三种反模式。

它不会在未经你同意的 seam 上写测试。在出现任何测试之前，它会先命名打算测试的公共边界，然后停下来等待你的确认。测试工作力是有限的，这一步把它花在关键路径上，而不是每个边界情况上。`tdd` 也是一份**参考**，而不是驱动器。它包含了循环的规则，而执行者（你或 [implement](https://aihero.dev/skills-implement)）负责运行应用这些规则的 [session](https://www.aihero.dev/ai-coding-dictionary/session)。

## 何时使用

输入 `/tdd`，或者当任务适合时 [agent](https://www.aihero.dev/ai-coding-dictionary/agent) 会自动触发：以测试优先的方式构建功能或修复 bug，或者当你说 "red-green-refactor" 时。

在存在具体行为需要构建、有输入和可观察输出，并且你希望测试能在重构后存活时选择它。

| 你的情况 | 选择 |
| --- | --- |
| 具有明确定义输入和输出的行为（业务逻辑、请求/响应契约、转换、验证） | `tdd` |
| 行为尚未确定 | [to-spec](https://aihero.dev/skills-to-spec)，它也会在写任何代码前商定测试 seam |
| 问题实际上是接口的形状，而不是测试 | [codebase-design](https://aihero.dev/skills-codebase-design) |
| 你有 [spec](https://www.aihero.dev/ai-coding-dictionary/spec) 或 [tickets](https://www.aihero.dev/ai-coding-dictionary/ticket) 并且希望为你运行整个构建 | [implement](https://aihero.dev/skills-implement)，它会按 ticket 驱动 `tdd` |
| 配置、接线、胶水、类型注解、直接的 CRUD 委托 | 没有一个完全适合；见下面的开放空白 |

最后一行是一个真正的空白。该技能决定了 seam 放在哪里，但没有任何东西决定一个变更是否值得这个循环。如果你在没有任何独立真相来源可断言的变更上运行它，你会得到一个重复实现的测试。这就是该技能警告的循环论证反模式，从另一端达到了。这是 [issue #746](https://github.com/mattpocock/skills/issues/746)，目前仍是开放的。在它关闭之前，你自己做出判断，或者把这个规则写进你的 `CLAUDE.md`。

## 前置条件

需要安装 [codebase-design](https://aihero.dev/skills-codebase-design)。`tdd` 过去自带深度模块和接口设计说明；v1.0 删除了它们，转而使用共享技能，现在 `tdd` 使用其接口设计词汇。没有其他要求；该技能是 [stateless](https://www.aihero.dev/ai-coding-dictionary/stateless) 的，不写入自己的文件。

## 循环，以及它运行的 seam

该技能建立在三个术语之上。

**Red-green。** 先写失败的测试，然后只写刚好让它通过的代码。不要为下一个测试写代码。没有重构阶段。该技能在 2026 年 6 月删除了它，因为 agent 几乎从不执行这一步，而且审查和实现作为独立的 session 效果更好。重构属于 [code-review](https://aihero.dev/skills-code-review)。

**Vertical slice。** 在一个 seam 上写一个测试，然后写最小实现，然后重复。第一个循环是一个**tracer bullet**，证明端到端的单一路径。相反的是水平切片：先写所有测试，再写所有代码。批量写的测试验证的是*想象的*行为。它们检查的是事物的形状而不是用户实际做了什么，而且它们在理解实现之前就锁定了测试结构。

**Pre-agreed seam。** Seam 是你观察行为的公共边界，而不深入内部。这条规则没有例外。不要在未经确认的 seam 上写测试。在完整链中，seam 在更早的 [to-spec](https://aihero.dev/skills-to-spec) 阶段就已商定："`/tdd` 被告知只在预先商定的测试 seam 上工作，`/code-review` 检查只使用了商定的 seam。" 单独调用时，`tdd` 会直接问你。

它旨在防止的三种反模式：

| 反模式 | 迹象 |
| --- | --- |
| 实现耦合 | 重命名内部函数时测试失败，尽管行为没有改变。模拟了内部协作者、断言了调用次数、用数据库查询来验证而不是接口。 |
| 循环论证 | 预期值是用代码计算出来的方式计算的，所以测试按构造通过。预期值必须来自其他地方：已知的字面量、计算示例、spec。 |
| 水平切片 | 一批测试在任何实现之前就位。 |

Mock 仅用于系统边界：外部 API、时间、随机性，有时文件系统或数据库。永远不要 mock 你自己的模块。

## 常见问题

**为什么不重构？描述说的是 "red-green-refactor"。**

因为重构步骤被删除了，而描述没有。删除是故意的。Agent 几乎从不执行这一步，而且把实现和审查放在独立的 session 中效果更好。结果是否还算严格意义上的 TDD 不如循环是否产生更好的代码重要。触发词与正文的不匹配已作为 [issue #589](https://github.com/mattpocock/skills/issues/589) 提交，目前仍是开放的，所以 "red-green-refactor" 仍然可以作为触发该技能的短语使用。你得到的是 red-green，重构在 [code-review](https://aihero.dev/skills-code-review) 中。

**它让我选择测试 seam，我完全不知道该选哪个。**

这是该技能报告最多的摩擦（[issue #607](https://github.com/mattpocock/skills/issues/607)）。提示只按名称列出候选 seam，对每个 seam 能捕获什么或遗漏什么没有任何说明，所以你在标签之间选择。目前还没有修复方案。实际的变通方法是在回答前让 agent 说明权衡：组件级 seam 遗漏了什么而集成 seam 能捕获，以及慢多少。这也是为什么链在 `to-spec` 中提前商定 seam 的原因，那时你看到的是整个功能而不是一个提示。

**它先写了实现再写测试，尽管技能说 red 优先。**

这会发生。一位用户追问 [model](https://www.aihero.dev/ai-coding-dictionary/model) 后得到了一个异常诚实的回答："我知道技能说 '一次一个测试，看着它因正确的原因失败'。我读过。我只是默认了我的正常习惯。"该技能接受这一点。没有任何指令能让 agent 100% 遵守，更严格的措辞会限制 agent 的创造力而收益甚微。即使 agent 没有严格遵守，这个循环仍然值得运行，因为总体结果仍然更好。如果某个特定 slice 的严格遵守很重要，那就 watch 运行而不是相信技能会强制执行。

**它应该先写浏览器或端到端测试吗？**

通常不应该，而且该技能不会阻止。一位用户报告 agent 先写了 Playwright 测试，然后花了很长时间反复运行它，最后得出结论说对于尚不存在的功能，*测试* 本身坏了。浏览器测试慢到足以让 red-green 反馈循环得不偿失。在你的 repo 的 `CLAUDE.md` 中声明浏览器测试在行为工作后再写。

**`/tdd` 替代 `/implement`，还是课程的 `/do-work`？**

不。`/tdd` 记录方法论；`/implement` 是一个简单的工作→反馈→提交循环，是 `/do-work` 的直接替代。课程中的单个 `/do-work` 步骤现在被拆分为 `/implement`、`/tdd` 和 `/code-review`。如果你问哪个应该针对 ticket 运行，答案几乎总是 `/implement`。

**深度模块和接口设计指导去哪儿了？**

在 v1.0 中进入了 [codebase-design](https://aihero.dev/skills-codebase-design)，被泛化以便多个技能共享一个词汇。`refactoring.md` 同时离开了；重构现在是 [code-review](https://aihero.dev/skills-code-review) 的工作，该技能携带了 Fowler 的 smell 基线。

**它知道我的其他 tickets 吗？**

不知道。针对一个 ticket 运行时，它可能提出属于兄弟 ticket 的工作，因为它看不到问题图的其余部分（[issue #129](https://github.com/mattpocock/skills/issues/129)）。这不是 `tdd` 的工作。同时传递 spec 和 ticket 有帮助；首先把 ticket 大小调对更有帮助。

## 正常工作的标志

- 在出现任何测试文件之前，它会停下来命名打算测试的 seam，然后等待。
- 出现一个测试，变红，得到刚好让它通过的代码，然后才出现下一个测试，而不是一批测试后跟一批代码。
- 测试名称读起来像能力（"user can checkout with valid cart"），而不是内部实现（"checkout calls paymentService.process"）。
- 断言中的预期值是可以追溯到 spec 的字面量，而不是按代码计算方式重新计算的值。
- 重命名内部函数不会破坏套件中的任何测试。
- Mock 只出现在外部边界（支付 API、时钟），永远不会围绕你自己的模块。

## 它在何处适用

`tdd` 运行在主链的构建步骤内部；它不是独立的步骤：

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

[to-spec](https://aihero.dev/skills-to-spec) 提前商定测试 seam，[implement](https://aihero.dev/skills-implement) 按 ticket 驱动 `tdd`，然后 [code-review](https://aihero.dev/skills-code-review) 事后检查是否只使用了商定的 seam，并接管 `tdd` 不再做的重构。它的另一个邻居是 [codebase-design](https://aihero.dev/skills-codebase-design)，这是 `tdd` 使用的 seam 和深度模块词汇的共享来源。你也可以单独使用它，只要有具体行为需要构建且没有完整 spec 在起作用时。当你不确定哪个技能适合你的情况时，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你指引。

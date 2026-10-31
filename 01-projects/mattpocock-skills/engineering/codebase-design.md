## 作用

`codebase-design` 修复你用来设计模块的词汇：**模块**、**接口**、**深度**、**接缝**、**适配器**、**杠杆**、**局部性**。它精确地定义了每一个，禁止松散的替代词（"组件"、"服务"、"API"、"边界"），并阐述了从中得出的少数原则。

它是一个参考，而不是一个流程。它不运行循环，不产生产物，也从不停下来问你问题。每个涉及设计的技能都使用它的词汇。单独使用时，它给你词汇就停止。在调用它之前要知道这一点。如果你把一个[会话](https://www.aihero.dev/ai-coding-dictionary/session)指向一个没有流程和停止规则的技能并说"开始"，代理会发明一个流程。下面的问题展示了那是什么样的。

## 何时使用

输入 `/codebase-design`，或当设计任务适合时，代理会自动调用它。

当你已经知道要重新设计哪段代码并需要思考其形状时调用它：接缝放在哪里、接口可以有多小、一次提取是否从调用者那里移除了复杂性。也用它来解决关于设计词汇含义的争论。

几个技能与它接近。根据你的问题来选择：

| 问题 | 技能 |
|---|---|---|
| 一个模块的形状：它的接口、接缝、深度 | `codebase-design` |
| *领域词汇*："account" 有三个含义，两个人对"取消"的理解不同 | [domain-modeling](https://aihero.dev/skills-domain-modeling) |
| 你还不知道要重新设计*哪个*模块 | [improve-codebase-architecture](https://aihero.dev/skills-improve-codebase-architecture)（找到候选者的调查） |
| 你想要设计被争论，而不仅仅是被命名 | [grilling](https://aihero.dev/skills-grilling) |
| 有一个具体的行为要构建，你想要在重构后仍然有效的测试 | [tdd](https://aihero.dev/skills-tdd) |

## 词汇表

词汇表就是这个技能。该技能针对其他术语定义了每个术语，并给出了每个术语所替代的词。

| 术语 | 含义 | 不要说 |
|---|---|---|
| **模块** | 任何有接口和实现的东西。有意不限制规模：一个函数、一个类、一个包、一个跨层切片。 | unit、component、service |
| **接口** | 调用者必须知道的一切才能正确使用它：类型签名，加上不变式、顺序约束、错误模式、所需配置、性能特征。 | API、signature |
| **深度** | 接口上的杠杆：调用者或测试每学习一个单位的接口，能行使多少行为。**深的**：大量行为隐藏在小接口后面。**浅的**：接口几乎与实现一样复杂。 | 无 |
| **接缝** | Michael Feathers 的术语：一个你可以在不编辑该位置的情况下改变行为的地方。它是接口的*位置*，放在哪里是一个独立的决策，与背后放什么分开。 | boundary |
| **适配器** | 在接缝处满足接口的具体东西。它命名的是一个角色，而不是一种东西：内存中的 fake 和 Postgres 仓库都是适配器。 | 无 |
| **杠杆** | 调用者从深度中获得的东西：每学习一个单位的接口，获得更多的能力。 | 无 |
| **局部性** | 维护者从深度中获得的东西：变更、bug 和验证都集中在一个地方，因此一次修复覆盖所有调用者。 | 无 |

该技能*不*将深度定义为实现行数与接口行数的比率，这是 Ousterhout 自己的定义。该指标鼓励填充实现，因此技能使用"深度即杠杆"来代替。

## 四条原则

- **深度是接口的属性，不是实现的属性。** 一个深模块内部可以由小的可替换部件构建。调用者就看不到它们。一个模块可以有内部接缝供自己的测试使用，以及一个位于其接口处的外部接缝。
- **删除测试。** 想象删除这个模块。如果复杂性消失了，这个模块就是一个通道。如果它重新出现在 N 个调用者中，这个模块隐藏了真正的复杂性。
- **接口就是测试面。** 调用者和测试穿过同一个接缝。如果你想测试接口*内部*的东西，这个模块的形状就是错的。
- **一个适配器意味着假设的接缝。两个适配器意味着真实的接缝。** 不要在有东西跨它变化之前切开接缝。单适配器接缝只是间接。

两个支持文件更进一步，技能按需读取而非预先读取。[DEEPENING.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/DEEPENING.md) 将候选者的依赖分为四类（进程内、本地可替换、远程但自有、真正外部），因为类别决定了如何在接缝处测试深化的模块。[DESIGN-IT-TWICE.md](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/DESIGN-IT-TWICE.md) 启动并行[子代理](https://www.aihero.dev/ai-coding-dictionary/subagent)为同一模块生成三个或更多完全不同的接口，然后在深度、局部性和接缝位置上比较它们。

## 常见问题

**如何在 TypeScript 中实际构建一个深模块？**

这是关于这个技能被问得最多的问题，而技能没有回答它。它定义了一个深模块*是什么*；它对于如何阻止一个 stray import 绕过接口只字不提。[Issue #458](https://github.com/mattpocock/skills/issues/458) 说得很直白："假设我们对接口满意，它隐藏了细节，等等。但我们如何执行它？我认为如果没有 lint 或明确的护栏，人类和 LLM 都会开始让它变得混乱。"那个线程中的答案给出了三个选项：将其包装在类或 IIFE 中并承受类变得巨大的代价；在 monorepo 中将其作为一个包并承受 monorepo 工具的代价；或者使用像 [dependency-cruiser](https://github.com/sverweij/dependency-cruiser) 这样的 linter 来禁止绕过接口的导入。在这些机制中，Effect 是最好的，dependency-cruiser 是第二好的。仓库中有一个 `in-progress/` 桶中的 `setup-ts-deep-modules` 技能，它建立了一个 `src/packages/<name>/index.ts` 约定，但它是 beta 通道技能，没有文档页面，也不附带 lint 规则。

**我让一个会话指向它，它烧了 100k [tokens](https://www.aihero.dev/ai-coding-dictionary/token) 重新设计我从未问过的东西。**

这是一个已知问题，记录为 [issue #449](https://github.com/mattpocock/skills/issues/449)。该技能是模型调用的，并将自己描述为词汇，但其中没有什么能硬性阻止代理将其视为可运行的流程。被指示"在 /codebase-design 中继续并推进未决决策"时，代理选择了技能中最接近流程的部分：`DESIGN-IT-TWICE.md` 中的并行子代理。它重新探索了之前会话已经映射过的代码，并在问任何问题之前工作了很长时间。这个技能没有驱动技能所拥有的护栏（检查点、一次一个问题、不自动推进），因为它是一个参考。变通方案是调用一个驱动技能（`/grill-with-docs`、`/improve-codebase-architecture` 或 `/tdd`）并将 `codebase-design` 作为其词汇使用。该问题处于开放状态。

**`design-an-interface` 去哪里了？有 `/interface-design` 技能吗？**

这个技能取代了 `design-an-interface` 并接管了其内容。没有遗漏任何东西。它的"设计两次"技术（并行子代理生成完全不同的设计，来自 Ousterhout）在这里作为 `DESIGN-IT-TWICE.md` 发布。另外，几个人要求一个专用的 `/interface-design` 技能用于深模块/薄接口哲学；这个技能已经涵盖了该哲学，没有单独的计划技能。如果你来找任何一个名字，这就是你要找的页面。

**这不是一种文件结构约定，比如文件夹、barrel 文件、功能切片？**

不是。人们多次反对这一点，技能也没有改变。[Issue #95](https://github.com/mattpocock/skills/issues/95) 提出了一种形式化的分形树文件结构作为深模块的具体实现；回复是两者独立的："深模块是关于接口的设计和通过严格接口访问，无论文件系统看起来如何。完全可能有这种办法下的浅模块，这似乎是可能的。"同样在 #458 中提到："我认为你可能将模块的概念与文件系统绑得太紧了。文件系统当然可以作为模块形状的有用提示，但在深模块的构建中没有必要使用文件系统。"词汇表有意将**模块**定义为不限规模。

**`tdd` 真的使用这个词汇吗？**

现在是的，但长期以来并不是。v1.0 从 `tdd` 中移除了内联的深模块注释，转而使用这个共享技能，但没有人添加指针来替代它们，因此 `tdd` 自己定义了"接缝"并且什么都不引用。现在指针在 `tdd` 中，当开放问题是接口形状而非测试时，代理会跟随它。`tdd` 仍然拥有"接缝"作为你*测试*的边界；这个技能拥有其背后的模块形状。

**设计两次模式在 Claude Code 之外工作吗？**

不能干净地工作。`DESIGN-IT-TWICE.md` 说"使用 Agent 工具并行产生 3 个以上子代理"，"Agent" 是 Claude Code [工具](https://www.aihero.dev/ai-coding-dictionary/tool) 的名称。仓库为其他[工具链](https://www.aihero.dev/ai-coding-dictionary/harness)发布元数据，包括 Codex，这些可能没有该名称的工具。因此并行设计阶段的可移植性低于技能元数据所暗示的。[Issue #564](https://github.com/mattpocock/skills/issues/564) 追踪此问题，处于开放状态。

**我可以向词汇表添加自己的概念吗，比如 connascence、模块秘密、[渐进披露](https://www.aihero.dev/ai-coding-dictionary/progressive-disclosure)？**

人们已经提出了这些。[Issue #180](https://github.com/mattpocock/skills/issues/180) 将 Parnas 的模块秘密和 Page-Jones 的 connascence 添加为*泄漏过接缝的内容*的命名层，附带工作 diff；[issue #303](https://github.com/mattpocock/skills/issues/303) 提议在实现内部进行渐进披露，因此在公共接口深的模块在其内部也有结构。两者都处于开放且未合并状态。发布的词汇表有意保持小巧，技能本身给出了原因：一致的语言才是重点，没有人一致使用的术语比没有术语更糟糕。

## 正常工作的标志

- 设计对话停止产生"组件"、"服务"和"边界"这些词，开始产生"模块"、"接口"和"接缝"。
- 有人可以指着提议的提取说是否通过删除测试，而不需要含糊其辞。
- 一个提议的接缝附带第二个已命名的适配器，而不仅仅是第一个。
- 关于接口的讨论涵盖不变式、顺序和错误模式，而不仅仅是类型签名。
- 调用它不会启动一个会话。如果代理从 `/codebase-design` 开始读取文件并提出重构建议，它已将参考误认为驱动器。

## 它在何处适用

`codebase-design` 是一个**随时可取用的独立技能**，是工程技能下面的词汇层，而不是任何链中的步骤。最近的邻居是 [domain-modeling](https://aihero.dev/skills-domain-modeling)，它是*问题域*词汇的并行参考，而非模块的形状。两者通常一起需要，因为命名一个深模块需要同时用到两者。[improve-codebase-architecture](https://aihero.dev/skills-improve-codebase-architecture) 是另一个：它调查代码库以寻找深化候选者，并用这个词汇表的词汇写出每一个，因此它找到模块，你在这个技能的词汇中设计它。当你不确定哪种技能或流程适合时，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你路由。

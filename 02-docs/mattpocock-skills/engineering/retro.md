## 作用

`retro` 回顾一次编码 [session](https://www.aihero.dev/ai-coding-dictionary/session) 并建议改进 agent 的 **[环境](https://www.aihero.dev/ai-coding-dictionary/environment)**，以便下一次运行更顺利。它读取 session 自己的记录（默认是当前 session，或你指向的 session 日志中的某个 session）。它找到 agent 挣扎的时刻，并给你一个候选修复列表，最严重的在前。

它改变环境，而不是代码。以 agent 交付的 bug、花了二十次 [tool call](https://www.aihero.dev/ai-coding-dictionary/tool-call) 才找到的文件、或审查者错过的规则为例。`retro` 不直接修复任何它们。它问仓库中什么让它们发生，并提议检查、指针或标准来防止下次发生。它也只提议。在你选择候选之前，什么都不会改变。

## 何时使用

你通过输入 `/retro` 来调用它，agent 不会自动使用它。

在比预期更难的 session 结束时使用它。例如，agent 搜索某个东西太久，犯了一个工具本可以捕捉的错误，或需要它无法获得的信息。顺利的 session 没有什么可教的，发现来自困难的部分。如果你想要对 session 产生的代码的裁决，改用 [code-review](https://aihero.dev/skills-code-review)。

## 发现落在哪里

每个候选属于一个类别，类别决定修复去哪里：

| session 中出了什么问题 | 修复方式 |
| --- | --- |
| agent 花了很长时间找到文件或事实 | 一个从它已经读取的文件到另一个文件的**导航指针** |
| 它犯了一个工具本可以捕捉的错误 | 一个**自动化检查**：lint 规则、类型、测试、pre-commit hook、CI job |
| 审查者错过了一个判断性错误 | `CODING_STANDARDS.md` 中审查者 agent 的规则 |
| `AGENTS.md` 或 `CLAUDE.md` 很大 | 将引导移出，到标准或检查中 |
| 一个 tool call 对其返回来说很昂贵 | 简化工具，或替换它 |
| 一个引导文件充满什么都不改变的行 | 删除**无操作** |
| agent 需要它无法到达的信息 | 拓宽访问：将 dev server 日志写入文件，给只读服务访问权限 |

核心思想是标准属于**审查者**，而不是实现者。实现 agent 有最大的上下文压力，因为它要探索、写代码和调试失败。审查 agent 只得到一个 diff，别的什么都没有。所以新规则放到有空间应用它的地方，那就是审查。它永远不会放到 [AGENTS.md](https://www.aihero.dev/ai-coding-dictionary/agents-md) 中，后者无论是否相关都会加载到每个 session 的 [context window](https://www.aihero.dev/ai-coding-dictionary/context-window) 中。

在 `retro` 写任何规则之前，它先对违规进行分类。一个**机械性**违规（被禁止的 API、导入形状、文件位置规则）得到一个确定性检查，因为检查可以失败，而标准文件中的一个句子不能。只有真正的判断性调用，没有任何 linter 能强制执行，才变成散文。如果仓库没有任何 guardrail（没有 pre-commit hook，也没有运行 lint、typecheck 和测试的 CI job），`retro` 会将此作为自己的发现报告。

## 常见问题

**它会自己写 lint 规则吗，还是等 yes？可以配置为每次 session 后运行吗？**

它等待。`retro` 只提议。在你选择候选之前，什么都不会改变，所以不会手动编辑任何东西，也不会自动安装任何 hook。这是设计如此。一位用户在被"自动 hooks 阻止了好的更改"烧伤后要求这样做。决定什么值得永久检查需要判断，所以技能保持 [human-in-the-loop](https://www.aihero.dev/ai-coding-dictionary/human-in-the-loop) 和用户调用。有些用户确实在每次实现运行后运行它。但顺利的 session 没有什么可教的，所以每次 session 后运行大多产生没有人需要的规则。没有 dry-run 模式。提议的检查和其他代码一样，所以在让它阻止合并之前，在仓库上试试。

**这不会堆积 lint 规则吗？它曾经提议移除一个吗？**

部分，这是它最弱的地方。它可以移除散文：引导文件中的无操作，以及属于标准或检查中的 `AGENTS.md` 或 `CLAUDE.md` 中的引导。当文件很大时，它会标记这些进行删除。它根据读取的一个 session 来判断它们，所以把每个都当作删除测试的候选，而不是裁决。它不会审计上个月提议的 lint 规则、hooks 或 CI jobs。它只看一个 session，所以不能告诉你某个规则现在是否触发太频繁，或者背后的 bug 是否已经消失。你仍然需要自己修剪检查。一个在好代码上不断触发的规则是移除它的信号。

**它不会只是编造通用建议来填充类别吗？**

这是对它最强的批评。一位用户发现"一旦工作完成，AI 倾向于忘记 session 中间的挣扎，编造通用建议来满足 retro 类别。"每个候选必须来自 session 自己的记录，所以建议特定于那个 session。这有代价也有收益。它很少编造不相关的东西，但可能给这个 session 涉及的内容太多权重。丢弃任何你无法追溯到特定时刻的候选。把严重性顺序也当作初稿，因为一个安静的昂贵错误可能排名低于一个吵闹的廉价错误。

**我的 session 很长。现在运行，还是重新开始？**

默认情况下它审查当前 session。那是最好的情况，因为挣扎仍在 context window 中。如果 session 已经移出 [smart zone](https://www.aihero.dev/ai-coding-dictionary/smart-zone)，[clear](https://www.aihero.dev/ai-coding-dictionary/clearing) 它，并在 session 日志中指向一个新的 `/retro`。

**agent 一直犯同样的错误。我应该给 `CLAUDE.md` 加一行吗？**

通常不，`retro` 在这件事上比其他任何事情都更坚持。`CLAUDE.md` 中的一行加载到每个 session，降低文件中其他所有内容的权重，并随着代码变化而过时。如果错误是机械性的，修复是一个失败的检查。如果是判断性的，它进入审查者读取的编码标准。`AGENTS.md` 和 `CLAUDE.md` 用于导航指针和其他小东西。出于同样的原因，`retro` 不是一个 [memory system](https://www.aihero.dev/ai-coding-dictionary/memory-system)。它不存储发生了什么。它改变环境，使错误无法再次发生。

**我的设置提到 `CODING_STANDARDS.md`，而我没有。它从哪里来？**

没有技能会运送这个文件。第一次 session 找到一个审查者的判断性规则时，`retro` 提议创建它。在你接受后，[code-review](https://aihero.dev/skills-code-review) 读取它。你已有的任何其他标准文档，如 `CONTRIBUTING.md`，工作方式相同。

**它和 `improve-codebase-architecture` 有什么不同？**

输入不同。[improve-codebase-architecture](https://aihero.dev/skills-improve-codebase-architecture) 只需要代码，寻找结构改进。`retro` 需要 session 历史，改进的是 agent 工作的环境，而不是代码。两者都用；一个不能替代另一个。

## 正常工作的标志

- 每个候选都指向 session 中的一个特定时刻，而不是一个通用最佳实践。
- 重复的错误变成失败的检查，你的 `AGENTS.md` 随时间变短，而不是变长。
- 如果一个检查已经存在但没有连接，发现是连接它，而不是提议构建一个新的。
- 下一个同类型任务的 session 更快地找到它需要的东西。

## 它在何处适用

`retro` 是主链的最后一步，在那里你回顾链的进展：

```txt
grill-with-docs → to-spec → to-tickets → implement → code-review → retro
```

在值得学习的构建之后运行它，在同一个 session 中或指向该 session 的日志。顺利的构建可以跳过。

- [code-review](https://aihero.dev/skills-code-review) 是 `retro` 最常调整的审查者 agent。新的编码标准放在它的 Standards 轴读取的地方。
- [writing-for-agents](https://aihero.dev/skills-writing-for-agents) 设置 `retro` 提议的每个引导文件和技能的写作风格，`retro` 在开始之前加载它。

[ask-matt](https://aihero.dev/skills-ask-matt) 是整个集合的路由器，当你不确定哪种技能适合当前情况时。

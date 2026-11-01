## 作用

`handoff` 将你所处的对话压缩成一份 **handoff 文档**：一个写入你操作系统临时目录的 markdown 文件，而不是工作空间，以便新的 [agent](https://www.aihero.dev/ai-coding-dictionary/agent) 可以读取并接手工作。

它给你的是**可移植性**，而不是压缩，因此该技能比听起来更窄。你只需要一个文件当工作必须*移动*时：到新的 [harness](https://www.aihero.dev/ai-coding-dictionary/harness)、新的目录、同事，或你想分叉的 side task。如果没有什么在移动，你不需要 handoff。留在 [session](https://www.aihero.dev/ai-coding-dictionary/session) 中，`/clear`、[subagent](https://www.aihero.dev/ai-coding-dictionary/subagent) 和 `/compact` 覆盖普通的阶段结束情况，而 `/compact` 比这个技能更常覆盖。

## 何时使用

你通过输入 `/handoff` 来调用它；agent 不会自动触发它。传递一条关于下一个 session 用途的注释，该技能会为此目的编写文档。

有四个触发器，而且只有四个：

| 情况 | 为什么需要文件 |
| --- | --- |
| 切换 harness（Claude → Codex） | 新的 harness 看不到旧的 [context](https://www.aihero.dev/ai-coding-dictionary/context) |
| 移动到不同的目录或 repo | 原型目录是常见的情况 |
| 将工作发送给同事 | 他们需要可以阅读的东西 |
| 分叉阶段中间发现的 side task | 你继续工作；第二个 agent 取走分叉 |

对于其他任何事情（相同的 harness、相同的目录、你完成 [grilling](https://www.aihero.dev/ai-coding-dictionary/grilling) 并转向实现），使用 `/compact`。[ask-matt](https://aihero.dev/skills-ask-matt) 在阶段边界有所有五个选项的有序树。

## Branching 是人们跳过的用途

技能的描述读起来像 session 恢复：写一个摘要，在这里结束，在那里恢复。这样读起来，它看起来像个更差的 `/compact`，所以人们跳过它。Fork 情况是唯一值得了解的。你**留在你的 session 中**，并将累积的 context 副本交给在并行工作的第二个 agent。

这就是通过 [prototype](https://aihero.dev/skills-prototype) 绕路所使用的。你深入设计对话，遇到一个只有运行代码才能解决的问题，而且你不想把构建的线程花在找出答案上。Hand off 到 prototype session，得到答案，把答案交回来，并从原始线程中引用它。工作交叉两次，你的原始对话保持活跃，你无需重新解释任何东西。

阶段边界的五个选项中有三个保留不同的东西：`/compact` 保留你的意图，`/clear` 什么都不保留，`/handoff` 保留工作的移动能力。

## 什么在移动，什么不移动

文档携带实时线程（正在进行什么、为什么、下一步做什么）加上一个**建议技能**部分，命名下一个 agent 应该选择的技能。该技能在写入文件之前 redact secrets。

它故意不携带任何已经写下来的东西。文档引用 specs、plans、ADR、issues、commits 和 diffs 的路径或 URL，从不复制它们。这保持文件小巧，并将已确定的细节保存在一个地方，而不是两份会漂移的副本。

## 常见问题

**Handoff 还是 compact？**

除非有什么在移动，否则 `/compact`。留在同一任务上是 compact，不是 handoff。当 harness 和目录保持不变，而且你需要留在循环中时，阶段边界树大多数日子以 `/compact` 结束。`/handoff` 的摘要不会更好。它的优势在于结果是一个你可以带到 `/compact` 到不了的地方的文件。

**那么 compact、clear 和 handoff 之间的实际区别是什么？**

每个都保留不同的东西。`/compact` 压缩此 context 并在 fresh window 中继续，因此你的意图存活。`/clear` 清空窗口并从零开始。当后面的一切都是一次性的时这是正确的，如果它不是，你就无法撤销它。`/handoff` 写入一个可移植的文件，因此工作 survived 移动到其他地方。三者都将**[一级来源](https://www.aihero.dev/ai-coding-dictionary/primary-source)**（实际发生的对话）变成**[二级来源](https://www.aihero.dev/ai-coding-dictionary/secondary-source)**（其摘要）。继续是唯一不这样做的选项，这就是为什么你首先排除它。

**我的手off文件去了哪里？**

它进入临时目录，这是该技能报告最多的问题。该技能将其解析为 `$TMPDIR`，否则 `/tmp`（Windows 上的 `%TEMP%`），但路径很长。在继续之前要求返回路径并保留它。Temp 是故意的，因为 handoff 是传输中的文档，不是你要维护的 artifact。Temp 也不是耐久的，正如下一个问题所解释的。

**我的手off在 sessions 之间消失了。**

某些环境在 sessions 之间清除 temp（报告的是 Codex），而且重启会清空 `/private/tmp`。如果下一个 session 不是在一小时内开始，或者是在不同的 harness 下开始，自己将文件复制到某个耐久的地方，一旦写入就立即复制。该文档指向的任何内容也是如此：如果 dispatch 引用 temp 中的其他文件，下一个 agent 无法跟随它。

**我如何实际将它交给下一个 agent？**

打开 fresh session 并指向路径：read this file, then continue。指向文件而不是将摘要粘贴到 shell 命令中。当摘要包含 backticks 或 `$(...)` 时，shell 在你将它插入 `claude "<summary>"` 时会破坏它。通常的结果是静默截断而不是错误，因此新的 agent 从一个不完整的 brief 开始，而且没有任何东西告诉你。

**这和 `/branch`、`--fork-session` 或内置的 `/handoff` 相同吗？**

它们相似，但不相同。`/branch` 不是这里发布的技能；`/handoff` 是 canonical 名称。Fork 继承精确的 context 副本；这个技能产生一个*针对*声明的下一个任务的有针对性的压缩，在一个文件中。当 fork 可以工作时（相同的机器、相同的 harness、相同的目录），fork 工作量更小。文件是更好的选择，当目的地是 fork 到不了的地方时。

**什么时候某些东西应该放在 `CLAUDE.md` 中？**

问问它下个月是否仍然为真。`CLAUDE.md` 是关于项目的 standing context，无论是否相关，都加载到每个 session 中。Handoff 是关于正在进行的一项工作，一旦该工作落地就无用了。如果你不断重复解释一个事实，它属于 `CLAUDE.md`。半完成的任务属于 handoff。

**它 captures what，not why。**

这是一个公平的批评，而且人们经常提出。两件事有帮助。传递参数（告诉它下一个 session 是为了什么），这样技能就保留与*那个*相关的推理，而不是将其展平。并 watch session 从未验证过的自信声明，例如 "X isn't built" 或 "Y is done"。下一个 agent 信任该文档，不会重新检查它，因此一个被写成事实的信念成为随后一切的前提。在交给它之前阅读文档，并降级你假设的任何东西。

**为什么它是一个技能而不是 slash command？**

两者都有效；它们适合不同的情况。作为技能，它通过与其他所有东西相同的安装路径来发布和更新，这使它可共享。它的 frontmatter，而不是机制，阻止了 agent 自行触发它。

## 正常工作的标志

- 该文档是 conversation 的一小部分，specs、issues 和 diffs 在其中作为路径和 URL 出现，而不是作为复制文本。
- 你可以在没有原始 session 打开的情况下 cold read 它，并知道下一步该做什么。
- Fresh agent 开始工作，而不是要求你重新解释设置。
- 在 fork 情况下，当你回到它时，你的原始 session 没有改变。
- 建议技能部分命名你自己会选择的技能。
- 其中没有任何东西是 key、token 或 password。

## 它在何处适用

`handoff` 是一个**随时可用的独立工具**。它在 sessions 之间而不是构建链内部工作。它是一个窄的工具，而且你在阶段边界的五个选项中使用它的频率低于其他四个。它最近的邻居是 [prototype](https://aihero.dev/skills-prototype)，因为原型生活在自己的目录中，而出进往返是这个技能所针对的移动。当你处于边界并不确定是继续、clear、hand off、delegate 还是 compact 时，[ask-matt](https://aihero.dev/skills-ask-matt) 有排序这五个的树，并在整个集合中为你指引。

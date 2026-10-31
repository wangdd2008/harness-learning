## 作用

`research` 通过阅读拥有答案的来源来回答一个问题，然后在仓库中留下一个带引用的 Markdown 文件。它只从**一级来源**工作：官方文档、源代码、spec、第一方 API。它追溯每个声明到拥有它的来源，所以它不会重复博客文章对 API 的描述，当 API 自己的文档可达时。

它不会在对话中回答你。输出是一个文件，写在仓库已经保存此类笔记的地方，每个声明都带链接。你得到一个可以反应、交给另一个 agent 或丢弃的文档，而不是一个 [session](https://www.aihero.dev/ai-coding-dictionary/session) 结束时消失的答案。

## 何时使用

输入 `/research`，或者当任务变成阅读工作时 [agent](https://www.aihero.dev/ai-coding-dictionary/agent) 会自动使用它。

当你下一步是*从工作目录外部找出某事*（第三方 API 如何行为、spec 说了什么、版本声明是否成立），而你不愿意在自己的线程中停滞阅读时，使用它。你需要什么决定了使用哪个技能：

| 你需要什么 | 使用 |
| --- | --- |
| 一个决策正在等待的外部事实 | `research` |
| 和你一起做出的决策，通过访谈 | [grilling](https://aihero.dev/skills-grilling) |
| 一个耐用的架构决策，写入 `GLOSSARY.md` 和 ADR | [grill-with-docs](https://aihero.dev/skills-grill-with-docs) |
| 确定某种方法在你的代码库中是否有效 | [prototype](https://aihero.dev/skills-prototype) |
| 一个 session 装不下的计划 | [wayfinder](https://aihero.dev/skills-wayfinder) |

`research` 和 `grill-with-docs` 之间的界限是**产出的保质期**。Research 产生短命的事实，比如这个库本周的认证机制是什么。ADR 记录你保留的决策。如果你产出的是决策而不是事实，你在 [grilling](https://www.aihero.dev/skills-grilling)，而不是 researching。

## 委托工作

阅读作为**后台 agent**运行。你继续工作，而它追溯每个声明到其一级来源，写一个 Markdown 文件，然后报告。Research 是你委托的工作，不是外包的思考。你得到一个可以 grilled、planned 或 designed 的文档，你仍然做出决策。

没有什么阻止后台 agent 生成另一个后台 agent。这是这个技能文档最完善的问题。

仓库决定文件放在哪里，不是技能。它遵循已经存在的笔记约定。如果没有，它选一个合理的地方并告诉你。它每次运行写一个文件。

## 常见问题

**它生成了第二个 research agent。这正常吗？**

不。这是一个开放 bug，[issue #530](https://github.com/mattpocock/skills/issues/530)。技能告诉调用者启动一个后台 agent，但没有限制 agent 类型。所以调用者生成一个 `general-purpose` agent，它有 `Agent` 工具和相同的指令，然后再次遵循它们。一位报告者测量到单个 research task 在三个重叠的运行中花费大约 450k [tokens](https://www.aihero.dev/ai-coding-dictionary/token)，而用户看不到的重复在半小时后完成。它也发生在 Claude Code 之外。用户确认 Codex 中 GPT-5.6-sol 有同样的嵌套。没有已发布的修复。用户已经用一行补丁告诉已经是 [subagent](https://www.aihero.dev/ai-coding-dictionary/subagent) 的 agent 自己完成工作。这有帮助，但它只是一个指令，不是结构性修复。在你调用技能后，监视你的后台任务列表并停止重复。

相反的错误也会发生。如果你自己的全局指令禁止 agent 重新委托工作，后台 agent 拒绝任务，技能在不告诉你的情况下什么都不做。

**文件应该放在哪里，我应该提交它吗？**

技能把文件放在仓库已经保存笔记的地方，没有进一步的意见。社区观点大多已经确定：保留 ADR，不保留 research 文件。关于这个问题的一个 Discord 线程说得最清楚："ADR yes。其他一切完成后归档或删除。否则它会变成工作残留，如果你偏离了 spec/research，可能会毒害未来的仓库读取。"Research 文件记录的是写那天的真相，所以过时的文件比没有更糟。总的来说，这些文件不属于 git，也没有标准的归宿。人们使用 Obsidian、单独的知识仓库或 issue tracker。

**什么算"高信任"一级来源，谁决定？**

[model](https://www.aihero.dev/ai-coding-dictionary/model) 决定。技能命名了*种类*的来源（官方文档、源代码、spec、第一方 API），没有 allowlist，没有 domain gate，也没有验证通过。这是该技能首次提出时最大的反对意见，而且没有人公开回答："五个指向垃圾的 research subagents 只是更快地给你五个自信的错误答案。你如何把关什么算高信任来源？"你唯一的保护是每个声明上的引用。追溯两三个。如果它们落在某个事物的摘要上而不是事物本身，运行就失败了。

**后面的 session 会重用前面运行的发现吗？**

不会。没有什么自动加载过去的 research 文件。文件留在仓库中，直到人或技能指向它。这是设计初期最强的挑战："价值在于 markdown 成为 agent 稍后重新读取的 context，而不是获取本身。一次写入的死文件只是花哨的搜索。"已发布的技能没有解决这个问题。在实践中，文件只有在你自己将其输入下一步时才有用：附加到 spec，引用到 grilling session，指向一个 [ticket](https://www.aihero.dev/ai-coding-dictionary/ticket)。

**为什么不直接让 agent 去读文档？**

你可以，而两句恰好这么说的 prompt 是这个技能替代的做法。技能给了你两句 prompt 给不了的东西。它在后台运行，所以你的 session 的 [context](https://www.aihero.dev/ai-coding-dictionary/context) 保持干净。一级来源约束和引用文件输出每次都是一样的，而不取决于你如何措辞 prompt。与 [harness](https://www.aihero.dev/ai-coding-dictionary/harness) 自己的深度研究模式相比，区别在于文件和一级来源规则，而不是搜索。如果两句 prompt 在小问题上就能满足你的需求，用两句 prompt。

**它什么时候停止阅读？**

技能没有停止标准。这表现为两个看起来相反但原因相同的抱怨：agent 走得太深，agent 涵盖一个主题但错过了重要的细节。一位从业者说"深度研究技能有时太深了。而且告诉 agent 研究通常会导致遗漏关键细节。"你必须设定范围。一个狭窄的、可回答的问题（一个 API、一个行为、一个版本声明）比一个广泛的"研究 X"返回得好得多。

**`/wayfinder` 创建了 research tickets。我需要自己解决它们吗？**

不，它现在会为你触发。在 v1.1 以来的未发布更改中，一次绘图 session 为每个 research ticket 生成一个 `/research` subagent 并并行运行。每个记录其发现到一个一次性的 `research/<name>` 分支，从 ticket 有 [context pointer](https://www.aihero.dev/ai-coding-dictionary/context-pointer)。Research tickets 是 wayfinder 的 one-ticket-per-session 规则的唯一例外，因为它们是 [AFK](https://www.aihero.dev/ai-coding-dictionary/afk)：没有什么等待你。一个已知问题：稍后删除分支会破坏 tickets 中的 context pointers。

## 正常工作的标志

- 你自己的 session 继续前进。如果你坐着看它阅读，委托就没有发生。
- 恰好出现一个新的后台任务。第二个名字几乎相同的是嵌套 bug。
- 出现一个新的 Markdown 文件，在仓库已经使用的笔记文件夹中，agent 告诉你路径。
- 其中每个声明都带链接，随机追溯两个，你落在官方文档、spec 或源代码本身上，而不是某人的撰写上。
- 你可以仅从文件做出你卡住的决策，而不需要自己回到来源。

## 它在何处适用

`research` 是一个随时可用的独立工具。它喂养思考技能，不是构建链中的步骤。你把它的文件*带入*流程。[grilling](https://aihero.dev/skills-grilling) 和 [grill-with-docs](https://aihero.dev/skills-grill-with-docs) 在有事实时问得更尖锐，[to-spec](https://aihero.dev/skills-to-spec) 可以针对它综合。[wayfinder](https://aihero.dev/skills-wayfinder) 是唯一直接调用它的技能。它用 `/research` subagent 解决地图上的每个 research ticket。对于整个地图，见 [ask-matt](https://aihero.dev/skills-ask-matt)。

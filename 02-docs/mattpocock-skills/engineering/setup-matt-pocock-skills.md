## 作用

`setup-matt-pocock-skills` 回答关于一个仓库的三个问题：issues 在哪里、分类标签叫什么、领域文档在哪里。它将答案记录为 `docs/agents/` 下的 markdown 文件。

这些文件是仓库之间唯一变化的东西。技能本身在任何地方都是相同的。它们在运行时读取 `docs/agents/issue-tracker.md` 并按照它说的做。这就是这个集合不绑定到 GitHub 的原因，也是你不需要编辑技能文件来指向另一个 tracker 的原因。用"将技能链接到自定义 issue tracker"来调用它，可以通过编程连接到任何东西，无需更改技能。

它是一个 prompt 驱动的技能，不是确定性脚本。它读取你的 `git remote`、`CLAUDE.md` 和 `GLOSSARY.md`，提出它发现的东西，并在写任何东西之前等待你确认。

## 何时使用

你通过输入 `/setup-matt-pocock-skills` 来调用它；[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 不会自动使用它。它的元数据故意标记为不可调用，所以其他技能不能为你触发它。

每个仓库使用一次，在任何其他工程技能之前。如果 [triage](https://aihero.dev/skills-triage)、[to-spec](https://aihero.dev/skills-to-spec)、[to-tickets](https://aihero.dev/skills-to-tickets) 或 [wayfinder](https://aihero.dev/skills-wayfinder) 开始猜测你的 issues 放在哪里，或应用你的 tracker 没有的标签，这个仓库还没有设置好。你可以在项目进行到一半的仓库中运行它。技能读取已经存在的东西，所以不会丢失早期工作。

## 前置条件

它写入你运行它的仓库：

| 它写入 | 在哪里 |
| --- | --- |
| `issue-tracker.md` | `docs/agents/` |
| `domain.md` | `docs/agents/` |
| `triage-labels.md` | `docs/agents/`，只在 `triage` 技能安装时 |
| `## Agent skills` 块 | 已存在的 `CLAUDE.md` 或 `AGENTS.md` 之一 |

你将所有内容作为 markdown 提交。没有用户级别或全局模式。配置 lives 在仓库中，所以每个仓库都有自己的副本。

## 三个决策

它从每个部分的推荐答案开始，跳过探索已经回答的任何问题。大多数运行只需要两个确认。

| 决策 | 它提议什么 | 何时询问 |
| --- | --- | --- |
| **Issue tracker** | 匹配你 `git remote` 的那个 | 总是，因为这是唯一真正的选择 |
| **分类标签** | 保留五个规范名称（`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`） | 只在 `triage` 技能安装时 |
| **领域文档** | 单上下文：一个根目录的 `GLOSSARY.md` 加上 `docs/adr/` | 只在它发现 monorepo 信号时，然后提供一个多上下文 `GLOSSARY-MAP.md` |

tracker 选项：

| 选项 | issues 在哪里 | 需要什么 |
| --- | --- | --- |
| **GitHub** | 仓库的 GitHub Issues | `gh` CLI |
| **GitLab** | 仓库的 GitLab Issues | `glab` CLI |
| **本地 markdown** | 这个仓库下 `.scratch/<feature>/` 中的文件 | 不需要任何东西，甚至不需要 remote |
| **其他** | 你说的任何地方 | 你的一段描述工作流的散文 |

前三个作为模板随技能一起发布，开箱即用。本地 markdown 是一个完整选项，不是后备。技能支持没有 remote 的 solo 项目。一个注意事项：如果你使用 GitHub，不要使用本地 markdown。它们是替代方案，所以选一个。

"其他"也是一个完整选项。这就是 Jira、Linear、Azure DevOps 和 Beads 的工作方式。你描述工作流，技能将你的散文记录在 `docs/agents/issue-tracker.md` 中，下游技能遵循这些散文。用户已经构建了：一个通过 [MCP](https://www.aihero.dev/ai-coding-dictionary/mcp) 的 Jira 变体、一个类似 `gh` 的 Gitea CLI、一个手写的本地 dashboard。

## 常见问题

**我必须使用 GitHub 吗？**

不。GitHub、GitLab 和 `.scratch/` 下的本地 markdown 都作为现成模板发布，其他任何东西都可以通过"其他"路径工作。这是重复最多的问题，大致是：*"硬锁定到 github"*、*"可以用 GitLab / Jira 吗"*、*"Azure DevOps 呢"*。答案总是一样的：setup 选择 tracker，而不是技能。

**更新技能后我需要重新运行它吗？**

v1.1 之后的直接答案是 yes。技能自己的结束消息更温和。它告诉你只切换 tracker 或重新开始时才重新运行。两者都可以辩护。种子模板在版本之间变化，所以旧版本的 `docs/agents/issue-tracker.md` 可能会对现在读取它的技能过时。如果下游技能做了与文档描述不同的事情，重新运行 setup。它很便宜。

**它写入了 `CLAUDE.md`，但我在 Codex 上。**

这是一个已知的 gap，仍然开放。文件选择规则是"如果 `CLAUDE.md` 存在则编辑，否则 `AGENTS.md`"。它检查哪个文件存在，而不是哪个 [harness](https://www.aihero.dev/ai-coding-dictionary/harness) 在运行。在留有 Claude Code 的 `CLAUDE.md` 的仓库中，技能将 `## Agent skills` 块写入 Codex 从不读取的文件。用户有两个变通方法：手动将块移到 `AGENTS.md`，或保持 `AGENTS.md` 权威并让 `CLAUDE.md` 成为指向它的一行指针。如果两个文件都不存在，技能会问你创建哪个，而不是选择一个。这让期望它做决定的人感到困惑。

**它没有创建我的分类标签。**

它不会创建。`docs/agents/triage-labels.md` 是一个*映射*：它告诉 `/triage` 你的 tracker 中哪些字符串对应五个规范角色。它不会运行 `gh label create`。在一个新的 GitHub 仓库上，标签还不存在，用户多次将此报告为 bug。两个后果：

- 如果你的 tracker 已经使用规范名称，映射是一个 identity table，没有配置要做。这是预期的常见情况，不是缺失步骤。
- 这个技能不会创建 [wayfinder](https://aihero.dev/skills-wayfinder) 的 `wayfinder:map` 和 `wayfinder:<type>` 标签，`gh issue create --label <missing>` 会失败而不是创建标签。在 GitHub 仓库上的第一次 wayfinder 运行之前，手动创建它们。

**我可以在这里配置其他技能的行为吗（[grilling](https://www.aihero.dev/ai-coding-dictionary/grilling) 节奏、问题格式、语气）？**

不。它配置三件事：tracker、标签、文档布局。用户要求将其作为 per-user 偏好的场所。答案是技能保持固执己见，不接受 per-user 配置。偏好属于你的 `CLAUDE.md` 中的普通指令，每个技能都已经读取。

**我可以把配置保存在 `~/.claude` 而不是提交到每个仓库吗？**

目前不行。一位在多个仓库中运行技能的用户有这个开放请求，但目前没有用户级别模式。每个仓库都携带自己的 `docs/agents/`。

**有一个配置其他技能的技能不奇怪吗？**

一个长期存在的抱怨说是的，大意是：*"有一个技能来设置其他技能感觉不对：这意味着 LLM 在配置它自己的技能。"* 权衡是真实的。没有 setup 步骤，每个触及 issues 的技能都需要自己的 tracker 指令副本。输出是你可以阅读和编辑的 markdown，这限制了风险。你可以阅读它写的每个文件并手动更改。日常更改用这种方式，而不是另一次运行。

## 正常工作的标志

- `docs/agents/issue-tracker.md` 和 `docs/agents/domain.md` 存在，如果 `triage` 已安装，则还有 `triage-labels.md`。
- 一个 `## Agent skills` 部分出现在你的 harness 读取的指令文件中，每个文件都有一行摘要指向这些文件。
- 它提议的 tracker 匹配你使用的 remote，标签字符串匹配你的 tracker 中存在的标签。
- 之后，`/to-tickets` 发布时不再问 issues 在哪里，`/triage` 应用标签而不是发明它们。
- 技能文件本身没有任何更改。如果 setup 编辑了 `SKILL.md`，出错了。

## 它在何处适用

`setup-matt-pocock-skills` 是工程流程的**一次 setup**，其他所有东西假定的前置条件，而不是链中的一个步骤。它的邻居是它的读取者：[triage](https://aihero.dev/skills-triage)，应用写在这里的标签词汇；[to-spec](https://aihero.dev/skills-to-spec) 和 [to-tickets](https://aihero.dev/skills-to-tickets)，发布到在这里命名的 tracker；以及 [wayfinder](https://aihero.dev/skills-wayfinder)，读取同一个 tracker 文件的 "Wayfinding operations" 部分，了解如何存储地图和子 [tickets](https://www.aihero.dev/ai-coding-dictionary/ticket)。[domain-modeling](https://aihero.dev/skills-domain-modeling) 稍后填充 setup 记录的领域文档布局。它只在解决术语或决策时创建 `GLOSSARY.md` 和 ADR，所以 setup 后没有领域文档是正常的。对于接下来使用哪个技能，[ask-matt](https://aihero.dev/skills-ask-matt) 路由整个集合。

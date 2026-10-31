## 作用

`wizard` 生成一个交互式 bash 脚本，逐步引导人类完成手动过程：连接第三方服务、运行一次性迁移、将项目从状态 A 移动到状态 B。它打开每个 URL，说明点击和复制什么，捕获返回的内容，并将其写入 `.env` 文件和 GitHub Actions secrets。

[agent](https://www.aihero.dev/ai-coding-dictionary/agent) 编写脚本；它从不运行它。你在自己的机器上运行。Wizard 是一个程序，不是指令列表。脚本按顺序运行每个步骤并保存你输入的值。你的部分是点击、粘贴和按 Enter。

## 何时使用

你可以输入 `/wizard`，agent 也可以自动触发它。当它遇到你必须执行的步骤（它无法生成的密钥、它无法点击的仪表板）时，它会为你构建一个 wizard，而不是将指令写入聊天中，在那里它们会滚动消失。

在下一步阻碍你的是一次仪表板之旅时选择它：

| 情况 | Wizard 做什么 |
| --- | --- |
| 新开发者需要配置六个服务才能启动应用 | 按顺序打开每个仪表板，捕获密钥，写入 `.env` 和 CI |
| 一次性迁移需要按特定顺序拨动开关 | 将不可逆步骤放在确认门后面 |
| 项目必须一次性从状态 A 移动到状态 B | 走过渡并报告它无法完成的内容 |
| 你即将把这些步骤写入 README | 改为编写一个可执行版本，当步骤过时时 visibly 失败 |

不要用它来*决定*构建什么；对于那个，[grill-with-docs](https://aihero.dev/skills-grill-with-docs) 和 [to-spec](https://aihero.dev/skills-to-spec) 是工具。

## 前置条件

生成 wizard 不需要。它编写的脚本在 bash 上运行，当某个阶段设置 GitHub secret 或 variable 时使用 `gh`。如果 `gh` 缺失或未认证，运行不会失败。该阶段显示警告，关闭摘要告诉你需要手动设置什么。

## 阶段

**阶段**是一个屏幕上的一项专注任务。脚本在阶段之间清除终端，因此溢出屏幕的阶段会丢失滚走的部分。你按依赖顺序编写阶段并设置 `TOTAL_STAGES`，它驱动进度显示。

该 [skill](https://www.aihero.dev/ai-coding-dictionary/skill) 在编写任何脚本之前先确定过程范围。它读取 repo 而不是冷问：`.env*`、`docker-compose*`、框架配置，以及 `.github/workflows/` 中每个 `secrets.*` / `vars.*` 引用。每个引用都是 wizard 必须生成的值。然后它向你显示有序的阶段列表以确认。只有在你确认后，它才将每个阶段映射到人类遵循的精确路径（"Dashboard → Developers → API keys → Reveal test key → copy"）。如果它不知道当前的 UI，它会询问你或查阅文档，而不是发明点击。

对于每个捕获的值，scoping 决定它去哪里：

| 目的地 | 何时 |
| --- | --- |
| `.env` only | 本地开发需要它，CI 不需要 |
| GitHub secret | CI 读取它，而且它是敏感的 |
| GitHub variable | CI 读取它，而且它是公共的 |
| `.env` 和 secret 两者 | 本地开发和 CI 都需要它 |
| 无处 | 阶段是纯操作：拨动的开关、升级的计划 |

## 模板已经解决了 UX

[模板](https://github.com/mattpocock/skills/blob/main/skills/engineering/wizard/template.sh) 运送了整个体验：带剩余时间的进度、确认门、包括 WSL 的跨平台 URL 打开、用于 secrets 的隐藏输入、幂等的 `.env` upserts、`gh secret` / `gh variable` 写入，以及关闭时它必须跳过的所有内容的摘要。`STAGES` 标记上方的所有内容都是一个固定库，在每个 wizard 中都相同，从不手动编辑。因为库从不改变，每个 wizard 的行为都相同。每个 wizard 唯一的工作是确定范围并编写其阶段。

编写 wizard 的 agent 从不从头到尾运行它，因为脚本会打开浏览器并等待人类输入。相反，agent 静态检查它：`bash -n`，可用的 `shellcheck`，以及跟踪每个值是否落在 scoping 所说的位置，每个 `set_secret` 名称是否与 CI 中真实的 `secrets.*` 引用匹配。所以第一次运行是你的，那次运行就是测试。

## 默认短暂

| 你有什么 | 如何处理脚本 |
| --- | --- |
| 一次性迁移、个人设置、你不会再重复的过渡 | 保存到 scratch 或 `scripts/` 路径，运行它，删除它 |
| 下一个 repo 上的人也会需要的设置路径 | 提交它并从 README 链接它，这样他们运行脚本而不是再次询问 agent |

## 常见问题

**我的 API keys 最终会进入 model 的 context 吗？**

不。Agent 编写脚本；它不运行它。你自己运行脚本，它通过隐藏终端输入捕获密钥并直接写入 `.env` 或 `gh secret`。Wizard 是一个 CLI，而 model 没有连接到它。这只适用于 wizard 在运行时捕获的值。如果你在确定范围时将密钥粘贴到聊天中，它就像任何其他粘贴的文本一样进入 [context](https://www.aihero.dev/ai-coding-dictionary/context)。

**我可以回去修复我打错的值吗？**

运行中不能。没有后退按钮。阶段向前运行，第 3 阶段的错误答案意味着 Ctrl-C 和重新运行。重新运行很便宜，因为任何已经写入 `.env` 的值都会作为默认值提供回来，所以你可以按 Enter 通过正确的阶段，只重新输入错误的那一个。用户在发布周要求了这个功能，而且它仍然是开放的："loved it! One thing though, is there a way to go back and correct what you've entered?"

**它知道我已经设置了什么吗？**

部分知道，而且比发布反应假设的要少。它在问之前读取 repo（你的 `.env` 文件、`docker-compose`、框架配置、CI 中的 `secrets.*` 引用），因此它确定范围到缺失的值，而不是像 README 那样从零开始。它不做的是检查第三方服务。如果你的 `.env` 中存在密钥，wizard 会提供回来并按 Enter 保留它；如果你已经创建了 Stripe 账户但从未保存密钥，wizard 仍然会把你送到仪表板去获取它。

**在 grilling 和 spec 之后，它在工作流中处于什么位置？**

没有特定的位置。它是独立的，不是链中的一个步骤。常见的猜测是 `/grill-with-docs → /to-spec → /wizard`，这个序列没问题，但触发条件是手动过程的出现，这可能发生在任何时刻：开始之前、构建中间，或发货很久之后。它也可以作为发现工具。确定范围在任务之前找到隐藏的先决条件，比如你没有想到的三个 API keys。

**它在 Claude Code 之外工作吗？**

脚本可以。它是纯 bash，无论哪个 [harness](https://www.aihero.dev/ai-coding-dictionary/harness) 生成它，它都运行相同。该技能本身是 model-invoked 的，因此到处都有列出：在 Claude Code 中输入 `/wizard` 或在 Codex 中输入 `$wizard`，或者只是描述你被卡住的设置。Model-invoked 还使它远离 [#693](https://github.com/mattpocock/skills/issues/693)，在那里 Claude 的桌面和 web apps 会从 [model](https://www.aihero.dev/ai-coding-dictionary/model) 的列表中删除*用户调用*的技能，并将它们报告为未安装。

**这不曾是 user-invoked 的吗？**

是的。现在它是 model-invoked 的，因此 agent 在遇到你必须执行的步骤时自动触发它。你之前能做的任何事情都没有停止工作。Model invocation 让 agent 也能调用该技能，所以 `/wizard` 像以前一样行为。这个改变修复了一个失败。以前，遇到凭证墙的 agent 会在聊天中 dump 六个编号步骤让你手动跟随。现在它编写 wizard。

**它以前在 `in-progress/` 中。现在在哪里？**

`engineering/`，自 v1.2 起。它从 beta 桶毕业，现在随插件一起发布，因此它与其余推广的技能一起到达，而不是需要单独安装。毕业时的行为没有改变。

## 正常工作的标志

- 向你展示有序的阶段列表以及每个阶段产生的值，并在任何脚本存在之前要求你确认。
- 在你被要求粘贴之前，每个 URL 都已打开。你永远不会被要求粘贴还没被发送去获取的东西。
- Secrets 是盲打的。没有敏感内容会回显到你的 scrollback 中。
- 每个阶段适合一个屏幕。你仍然需要的东西没有滚走。
- Ctrl-C 和重新运行从你离开的地方继续，将已保存的值作为默认值提供。
- 最终屏幕列出它写了什么，并单独列出它做不到而你必须手动完成的东西。

## 它在何处适用

`wizard` 是一个随时可用的独立工具，坐在自动化停止而人类必须点击的线上。它最近的邻居是 [setup-matt-pocock-skills](https://aihero.dev/skills-setup-matt-pocock-skills)，因为两者都存在为了让 repo 进入工作状态。那个配置了这个技能集，而 `wizard` 为其他所有东西生成设置路径。它也与 [implement](https://aihero.dev/skills-implement) 配对：当构建落地一个需要凭证或手动切换的功能时，wizard 覆盖只有人类才能执行的步骤。当你不确定哪个技能适合当前时刻时，[ask-matt](https://aihero.dev/skills-ask-matt) 会为你指引。

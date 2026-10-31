# 编写好的规格说明

你很少从空白页开始编写规格说明。你用自然语言描述一个变更，`/opsx:propose` 起草需求和场景，然后你把它们改好。这一页讲的就是最后一步 — "好"的标准是什么，以及如何引导 AI 走向它。

它是 [审查变更](reviewing-changes.md) 的姊妹篇：审查是捕捉草稿中的薄弱环节，而编写是知道一个强有力的草稿由什么构成。

## 规格说明是行为，不是代码

规格说明说的是你的系统 *做什么*，用任何人都能验证的语言 — 而不是如何构建。它由 **需求**（行为声明）和 **场景**（证明它们的实例）组成。

```markdown
### Requirement: Session Timeout
The system SHALL expire a session after 30 minutes of inactivity.

#### Scenario: Idle timeout
- GIVEN an authenticated session
- WHEN 30 minutes pass with no activity
- THEN the session is invalidated and the user must re-authenticate
```

把 *如何* — 队列、库、表结构 — 留在 `design.md` 或代码中。当行为和实现被混进一个需求中时，需求就不再可测试了，并且从代码变化的那一刻起就开始过时。

## 好的需求是什么样的

一个好的需求是一个行为，说得如此直白，你可以把它交给别人去测试。

- **一条陈述，一个 `SHALL`/`MUST`。** 如果一个需求有三个"还有"从句，那它其实是三个需求。拆分开。
- **可观察。** 代码外部的人应该能判断它是否成立。"The system SHALL show an error banner when the upload exceeds 10 MB" 是可观察的。"The system SHALL handle large uploads gracefully" 不是。
- **合适的强度。** OpenSpec 使用 RFC 2119 关键字，它们含义不同：

  | 关键字 | 含义 |
  |---------|---------|
  | `MUST` / `SHALL` | 硬性要求。不可协商。 |
  | `SHOULD` | 强烈建议，但有合理的例外空间。 |
  | `MAY` | 真正可选的。 |

  默认使用 `MUST`/`SHALL`。只有在你真心想说"除非有好理由不这么做"时才用 `SHOULD`。

需求的测试：*一个从没看过代码的测试员能判断它通过了吗？* 如果不能，它还需要打磨。

## 好的场景是什么样的

场景是需求证明自己价值的地方。每一个都是具体的 GIVEN / WHEN / THEN，可以成为自动化测试。

- **它锻炼了自己的需求。** 一个只是换种方式重述需求的场景什么都没测。让它成为一个有具体结果的特定情况。
- **覆盖重要的案例，不只是快乐路径。** 有效登录很简单。空输入、过期 token、第二次点击、出错的情况 — 那些才是 bug 藏身之处，也是场景最有价值的地方。
- **在标题中命名案例。** "Scenario: Rejects an expired token" 让审查者一眼就知道覆盖了什么；"Scenario: Test 2" 则不行。

一个有用的习惯：在批准前，问自己 *我最不想看到哪个案例被破坏？* — 然后确保有一个场景命名了它。

## 选择正确的 delta 类型

一个变更用三种章节类型来描述它对规格说明的编辑。使用正确的类型能让你的归档规格说明保持诚实：

- **`## ADDED Requirements`** — 全新的、以前不存在的行为。
- **`## MODIFIED Requirements`** — 已经存在并且正在改变的行为。包含完整的新版本；简短说明变化内容有助于审查者。
- **`## REMOVED Requirements`** — 正在消失的行为，附带原因说明。

归档时，ADDED 被追加到主规格说明中，MODIFIED 替换旧版本，REMOVED 从主规格说明中删除。移除一个能力的最后一个需求就是退役它：与其让规格说明空着，archive 会删除 `openspec/specs/<capability>/spec.md`。因为这是 archive 中唯一删除文件的步骤，所以需要明确请求 — 在变更的 `.openspec.yaml` 中添加 `retire_capabilities: true`，与其中已有的 `schema:` 并列。没有它，archive 会中止并告诉你。退役会删除整个文件，所以当规格说明的标题、`## Purpose` 和需求块之外还有任何内容时 — 比如 `## Notes` 章节，需求下的注释 — 也会被拒绝。中止时会指出那些行；把它们移到 `## Purpose` 或需求中，或者手动删除规格说明。对于在调用者 checkout 中的规格说明，archive 输出还会给出可以恢复已提交文件的 `git checkout`；选定的存储会收到 checkout 范围恢复指导。

如果你把真实的变化标为 ADDED，你最终会两个竞争的需求；如果你把新行为描述为 MODIFIED，就没有东西可替换。不确定时，打开当前规格说明看看需求是否已经在那里。

还有一个值得了解的章节。当你的 delta 创建了一个尚不存在的能力时，以 `## Purpose` 开头 — 一两句话说明这个能力是做什么的。Archive 用它作为创建的主规格说明的 Purpose；跳过它你会得到一个 `TBD` 占位符，需要手动填写。现有规格说明已经有了 Purpose，所以 delta 的会被忽略 — 直接编辑 `openspec/specs/<capability-path>/spec.md` 来修改它。这里的 `<capability-path>` 是相对于 `specs/` 的目录，如扁平项目中的 `user-auth` 或按域组织项目中的 `identity/user-auth`。

## 控制变更大小

最常见的编写错误不是措辞不当的需求 — 而是一个变更试图同时做三件事。

**一个好的变更有一个可以用一句话说清的意图。** "Add a dark-mode toggle." "Rate-limit the login endpoint." "Migrate sessions off cookies." 如果描述变更需要很多"还有"，那就是拆分的信号。

变更太大的迹象：

- Proposal 的范围读起来像一份不相关的功能列表。
- 审查它需要一下午，所以没人会审。
- 两个人无法在上面工作而不冲突。
- 一半的任务可以独立交付。

更小的变更更容易审查、更容易在一个专注的会话中构建、六个月后也更容易理解。你可以并行运行多个变更 — 参见 [编辑与迭代](editing-changes.md) 和 [工作流](workflows.md)。

反过来也会成立：一行拼写错误不需要三个需求和设计文档。让仪式与风险相匹配。

## 如何引导 AI 写出好的草稿

因为 `/opsx:propose` 做了第一稿，你得到的东西的质量取决于你给它的东西的质量。你不需要手写需求 — 你需要把 AI 瞄准好：

- **说明意图和边界。** *"Add a dark-mode toggle that follows the OS setting on first load — don't touch the existing theme API."* 范围外的部分和范围内的一样重要。
- **命名你在意的案例。** *"Make sure there's a scenario for a user who already picked a theme manually."* AI 会覆盖你指出的东西。
- **然后编辑。** 它就是普通的 Markdown。收紧一个模糊的 `SHALL`，删除一个什么都没测的场景，添加它遗漏的案例 — 或者让 AI 来做：*"the timeout requirement is vague, pin it to 30 minutes."*

起草、打磨、重复。几轮下来就能产生一个你会信任的规格说明，这就是全部意义。

## 快速检查清单

- [ ] 每个需求都是一个可观察的行为，带有 `SHALL`/`MUST`。
- [ ] 没有实现细节被塞进需求中。
- [ ] 每个需求至少有一个真正锻炼它的场景。
- [ ] 重要的边缘和错误案例有场景，不只是快乐路径。
- [ ] Delta 正确使用了 ADDED / MODIFIED / REMOVED。
- [ ] 整个变更有一个可以用一句话说清的意图。

## 下一步去哪

- [审查变更](reviewing-changes.md) — 两分钟捕捉那些漏网之鱼。
- [概念](concepts.md) — 规格说明、变更和 delta 背后的深层模型。
- [示例与配方](examples.md) — 从始至终的真实变更。

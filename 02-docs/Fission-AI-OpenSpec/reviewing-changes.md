# 审查变更

OpenSpec 的全部承诺是你和 AI 在写任何代码之前就 **达成了要构建什么的共识。** 这个共识只有在你真正阅读了 AI 起草的内容之后才有意义。这一页讲的就是你真正阅读的那两分钟 — 打开什么、按什么顺序、找什么。

这个赌注很简单：在一个段落计划中抓住错误转向，几乎是免费的。在 300 行代码中发现同样的错误转向，就不是了。审查就是你兑现这个赌注的地方。

## 你审查的两个时刻

恰好有两个：

```
/opsx:propose ──► REVIEW THE PLAN ──► /opsx:apply ──► REVIEW THE CODE ──► /opsx:archive
                  (before any code)                    (/opsx:verify)
```

1. **在 `/opsx:propose` 之后**（或 `/opsx:ff` 之后），`/opsx:apply` 之前 — 在它还只是文字的时候阅读计划。
2. **构建之后**，用 `/opsx:verify` — 检查代码是否实际执行了计划所说的。

第一次审查是回报最高的，也是人们最容易跳过的。这一页把大部分时间花在那里。

## 按这个顺序阅读

变更是一个纯 Markdown 文件夹，位于 `openspec/changes/<name>/`。按这个顺序阅读文件，让你能在出错时尽早退出：

```
openspec/changes/add-dark-mode/
├── proposal.md      1. 意图和范围   ← 如果这个错了，在这里停下
├── specs/…/spec.md  2. 需求       ← 审查的核心
├── design.md        (仅针对较大变更) — 技术方案
└── tasks.md         3. 工作计划
```

你不需要阅读每一行。你需要回答三个问题，每个文件一个。

## Proposal：这是正确的问题吗？

先打开 `proposal.md`。它捕捉了"为什么"和"什么" — 意图、范围、一两段话的方法。

**好的样子：** 一个清晰的意图，你认识的范围，以及一个现在值得做的理由。

**危险信号：**

- 它解决了一个与你所要求的 *不同* 的问题。
- 范围扩大了 — 你要的是主题切换，proposal 还顺便提到了 auth "既然我们都在这里"。
- 它很模糊。"Improve the settings page" 不是范围；"add a dark-mode toggle that respects the OS preference" 才是。

**要回答的问题：** *这是否与我实际要求的一致，有没有什么东西悄悄溜进来了？* 如果答案是否定的，停下 — 不要再往下读了，修正 proposal（参见 [提出异议](#提出异议是廉价的)）。

## Spec deltas："完成"被正确定义了吗？

这是审查的核心。`specs/` 下的 delta specs 说明了变更交付后什么是 *真的* — 以需求和证明它们的场景的形式：

```markdown
## ADDED Requirements

### Requirement: Dark Mode Toggle
The system SHALL let a user switch between light and dark themes.

#### Scenario: Respects the OS preference on first load
- GIVEN a user who has never set a theme
- WHEN they open the app on a device set to dark mode
- THEN the app renders in dark mode
```

**好的需求看起来是什么样的：** 一个清晰的 `SHALL`/`MUST` 陈述，你可以交给测试员，以及至少一个其 GIVEN/WHEN/THEN 实际锻炼该陈述的场景。

**危险信号：**

- **模糊的需求。** "The system SHALL be fast" 既无法构建也无法测试。多快算快？
- **没有场景的需求**，或者场景不测试它下面的需求。
- **最有价值的发现：遗漏了什么。** AI 忠实地写下你 *说了* 什么。你的工作是注意到你 *忘了* 说什么。如果你最在意的是 OS-preference 案例，但没有任何场景提到它，那就是审查在回报你。

阅读 deltas 时问自己 *如果系统完全按照 — 且只按照 — 这个做，我会满意吗？* 这里还没有涉及代码，所以修改它很便宜。

## Tasks：工作计划合理吗？

最后打开 `tasks.md`。它是 AI 将要执行的实施检查清单。

**好的样子：** 有序的步骤，每个都能追溯到需求，没有什么神秘的。

**危险信号：**

- 没有匹配需求的任务（这是从哪里来的？）。
- 一个巨大的 "implement the feature" 任务，隐藏了所有真正的决策。
- 触及你刚刚批准的范围之外的东西的任务。

你在这里不是在做估算或微观管理 — 你是在检查计划是否与你已经接受的需求相符。

## 提出异议是廉价的

如果上述三个问题中有任何一个错了，说出来。没有阶段锁定，一切都可以修改 — 你修正它然后继续。两种方式，与 [编辑变更](editing-changes.md) 中完全相同：

- **自己编辑文件。** 它是纯 Markdown；修改范围行、收紧需求、删除任务。
- **告诉 AI 哪里错了** 然后让它修改：*"去掉 auth 更改 — 超出范围"，*"添加一个用户已经选择过主题的场景"，*"把任务 3 拆分为 schema 和 UI。"*

然后重新阅读你修改过的部分。反复修改直到它是一个你愿意签名的计划。那个来回 *就是* 产品在发挥作用。

## 代码之后：验证

工作完成后，`/opsx:verify` 是你的第二次审查。它重新阅读产物和代码，并在三个维度上报告不匹配：

| 维度 | 检查什么 |
|-----------|----------------|
| **完整性** | 所有任务完成，每个需求都已实现，场景已覆盖 |
| **正确性** | 实现与 spec 的意图一致，边缘案例已处理 |
| **一致性** | 设计决策实际出现在代码中 |

```
You: /opsx:verify

AI:  Verifying add-dark-mode...

     COMPLETENESS
     ✓ All 8 tasks in tasks.md are checked
     ✓ All requirements in specs have corresponding code
     ⚠ Scenario "Respects the OS preference on first load" has no test coverage
```

它将问题标记为 CRITICAL、WARNING 或 SUGGESTION，并且 **不会** 阻塞归档 — 它会暴露差距，决定权在你。这是"AI 写了代码"和"它是否构建了我们约定的东西"之间的区别。

`/opsx:verify` 在扩展配置文件中可用。如果你没有它，用 `openspec config profile` 打开（然后 `openspec update`），或者自己重新阅读变更和差异。

## 控制审查规模

不是每个变更都需要完整的审查。一个文件的拼写错误值得 20 秒的浏览。一个触及 auth、payments 或你无法恢复的数据的变更值得上面的每一个问题。重点从来不是仪式 — 而是把你的注意力花在错误会很昂贵的地方，在不会的地方就快速浏览。

## 两分钟检查清单

- [ ] Proposal 的意图与我所要求的一致。
- [ ] 没有什么额外的内容悄悄溜进了范围。
- [ ] 每个需求都足够具体，可以测试。
- [ ] 每个需求都有一个实际锻炼它的场景。
- [ ] 我最在意的案例被覆盖了。
- [ ] Tasks 对应需求；没有什么是神秘的或超出范围的。
- [ ] 我会放心让 AI 完全按照这个做，不多不少。

如果七个都通过了，自信地运行 `/opsx:apply`。如果任何一个失败了，那不是挫折 — 是那两分钟在发挥作用。

## 下一步去哪

- [编写好的规格说明](writing-specs.md) — 另一面：如何起草值得批准的需求和场景。
- [编辑与迭代变更](editing-changes.md) — 开始之后修改计划的机制。
- [工作流](workflows.md) — 审查在更大的循环中处于什么位置。

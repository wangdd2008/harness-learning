# mattpocock-skills

Matt Pocock 的 Agent Skills 集合（来源：github.com/mattpocock/skills）。每个技能是一个独立的 Markdown 文件，教会 AI 编码助手如何执行一类任务——从访谈、规划、构建到维护，覆盖 AI 编码工作流的完整生命周期。

- **engineering/**（21 项）：构建软件的核心工作流——规划、实现、审查、调试、维护
- **productivity/**（7 项）：围绕编码的辅助工作流——访谈、交接、教学、文档写作

> 对本仓库的 5 个分类角色与追踪器标签的映射，见根目录的 [`triage-labels.md`](triage-labels.md)。

## 快速导航：按你的处境选择

| 你的处境 | 去哪个技能 |
|---|---|
| 不知道从何开始，想选技能 | [`engineering/ask-matt.md`](engineering/ask-matt.md)（路由器） |
| 想法还很模糊，需要被访谈 | [`productivity/grill-me.md`](productivity/grill-me.md)（无代码库）/ [`engineering/grill-with-docs.md`](engineering/grill-with-docs.md)（有代码库） |
| 决策卡在别人脑子里 | [`productivity/to-questionnaire.md`](productivity/to-questionnaire.md) |
| 已决定，工作够小，一个会话能装下 | [`engineering/implement.md`](engineering/implement.md) |
| 已决定，但跨越多个会话 | [`engineering/to-spec.md`](engineering/to-spec.md) → [`engineering/to-tickets.md`](engineering/to-tickets.md) → [`engineering/implement.md`](engineering/implement.md) / [`engineering/implement-spec.md`](engineering/implement-spec.md) |
| 工作太大、路线不清、要跨会话规划 | [`engineering/wayfinder.md`](engineering/wayfinder.md) |
| 别人报来的 bug / 请求要分类 | [`engineering/triage.md`](engineering/triage.md) |
| 难以解决的 bug 或性能回归 | [`engineering/diagnosing-bugs.md`](engineering/diagnosing-bugs.md) |
| 写完代码要审查 | [`engineering/code-review.md`](engineering/code-review.md) |
| 准备开 PR | [`engineering/pr.md`](engineering/pr.md) |
| 想测试优先地写功能 | [`engineering/tdd.md`](engineering/tdd.md) |
| 想搞清模块该怎么设计 | [`engineering/codebase-design.md`](engineering/codebase-design.md) |
| 想验证某个设计问题（可丢弃代码） | [`engineering/prototype.md`](engineering/prototype.md) |
| 需要查外部事实（官方文档/源码） | [`engineering/research.md`](engineering/research.md) |
| 听不懂 agent 在说什么 | [`productivity/wait-what.md`](productivity/wait-what.md) |
| 要换工具/目录/交接给同事 | [`productivity/handoff.md`](productivity/handoff.md) |
| 长期学习一个主题 | [`productivity/teach.md`](productivity/teach.md) |
| 会话很难，想改进下次运行 | [`engineering/retro.md`](engineering/retro.md) |
| 第一次在新仓库使用本集合 | [`engineering/setup-matt-pocock-skills.md`](engineering/setup-matt-pocock-skills.md)（先跑这个） |

## 完整技能清单

### engineering/ —— 工程工作流

| 技能 | 文件 | 作用 | 调用方式 |
|---|---|---|---|
| ask-matt | [ask-matt.md](engineering/ask-matt.md) | **路由器**：根据你描述的情况，指出合适的技能或技能序列及人工决策点 | `/ask-matt` |
| code-review | [code-review.md](engineering/code-review.md) | 双维度审查 diff（**标准**维度：是否符合仓库写法；**规格**维度：是否满足需求），各自在独立子代理中运行，不合并结论 | `/code-review` 或自动 |
| codebase-design | [codebase-design.md](engineering/codebase-design.md) | 模块设计**词汇参考**：精确定义模块、接口、深度、接缝、适配器、杠杆、局部性；是参考不是流程 | `/codebase-design` 或自动 |
| diagnosing-bugs | [diagnosing-bugs.md](engineering/diagnosing-bugs.md) | 六阶段诊断难以解决的 bug / 性能回归：复现→最小化→假设排序→插桩→修复回归→清理；**必须先有红变反馈循环** | `/diagnosing-bugs` 或自动 |
| domain-modeling | [domain-modeling.md](engineering/domain-modeling.md) | 构建并锐化领域**通用语言**：挑战冲突术语、要求精确用词，术语确定即写入 `GLOSSARY.md` | `/domain-modeling` 或自动 |
| grill-with-docs | [grill-with-docs.md](engineering/grill-with-docs.md) | **有状态访谈**：一轮轮提问直到理解一致，边走边把词汇写入 `GLOSSARY.md`、把决策写入 ADR | `/grill-with-docs` |
| implement-spec | [implement-spec.md](engineering/implement-spec.md) | 接收 spec + tickets，按**任务图**并行调度子代理（各占 git worktree），集成后跑 code-review 并关闭 tickets | `/implement-spec` |
| implement | [implement.md](engineering/implement.md) | 构建**已决定**的工作：驱动 TDD、边做边类型检查、最后 code-review、提交到当前分支；绝不重新打开计划 | `/implement` |
| improve-codebase-architecture | [improve-codebase-architecture.md](engineering/improve-codebase-architecture.md) | 调查代码库**深化机会**（浅模块→深模块），产出 HTML 报告，**永不修改代码** | `/improve-codebase-architecture` |
| pr | [pr.md](engineering/pr.md) | PR 正文模板：**摘要**（视觉优先）→ **证据**（前后对比）→ **合并危险**；是格式参考不是工作流 | `/pr` 或自动 |
| prototype | [prototype.md](engineering/prototype.md) | 写**可丢弃的代码**回答设计问题：状态模型（可共享 HTML）或 UI 变体（`?variant=` 切换） | `/prototype` 或自动 |
| research | [research.md](engineering/research.md) | 只从**一级来源**（官方文档/源码/spec）回答问题，产出带引用链接的 Markdown 文件，不在对话里回答 | `/research` 或自动 |
| resolving-merge-conflicts | [resolving-merge-conflicts.md](engineering/resolving-merge-conflicts.md) | ⚠️ **已归档**（v1.3.0 从插件移除，不再维护），逐 hunk 处理冲突并追溯一级来源；页面仅作参考 | 参考 |
| retro | [retro.md](engineering/retro.md) | 回顾一次编码 session，找出 agent 挣扎时刻，建议改进**环境**（导航指针/自动化检查/审查规则）而非代码 | `/retro` |
| setup-matt-pocock-skills | [setup-matt-pocock-skills.md](engineering/setup-matt-pocock-skills.md) | 每个仓库**首次使用前运行**：确认 issues 位置、分类标签、领域文档，写入 `docs/agents/` | `/setup-matt-pocock-skills` |
| tdd | [tdd.md](engineering/tdd.md) | **测试优先**构建：先写失败测试→刚好通过的代码；写测试前先命名公共 seam 等你确认 | `/tdd` 或自动 |
| to-spec | [to-spec.md](engineering/to-spec.md) | 把**已决定**的对话综合为 spec 并发布为 issue；不做新决策 | `/to-spec` |
| to-tickets | [to-tickets.md](engineering/to-tickets.md) | 把 spec / 计划拆成带**阻塞边**的 tickets；每个 ticket 是贯穿各层的 **tracer bullet**，agent-ready | `/to-tickets` |
| triage | [triage.md](engineering/triage.md) | 分类**外部传入**的 issues（原始 bug 报告/功能请求）通过角色状态机；自己生成的 tickets 不要用它 | `/triage` |
| wayfinder | [wayfinder.md](engineering/wayfinder.md) | 处理**单个 session 装不下**的工作：在 tracker 上绘制由决策 tickets 组成的地图，逐个解决直到路线清晰；只规划不构建 | `/wayfinder` |
| wizard | [wizard.md](engineering/wizard.md) | 生成**交互式 bash 脚本**引导你走完手动过程（连服务、跑迁移、写密钥到 `.env`/CI secrets）；agent 写脚本，你运行 | `/wizard` 或自动 |

### productivity/ —— 辅助工作流

| 技能 | 文件 | 作用 | 调用方式 |
|---|---|---|---|
| grill-me | [grill-me.md](productivity/grill-me.md) | **无状态访谈**：把松散想法问到你敢承诺；不写文件、不留工作空间，在全新对话中启动 | `/grill-me` |
| grilling | [grilling.md](productivity/grilling.md) | 访谈循环核心：把主题映射为**设计树**，按轮次问完整**前沿**（先决条件已定的决策）；grilling 家族中唯一自动触发的 | `/grilling` 或自动 |
| handoff | [handoff.md](productivity/handoff.md) | 把当前对话压缩成 **handoff 文档**（写入系统临时目录），供新 agent 接手；仅当工作要跨 harness/目录/同事移动时使用 | `/handoff` |
| teach | [teach.md](productivity/teach.md) | 把目录变成**长期教学空间**：多 session 教你一个主题，产出简短自包含 HTML lessons，资源记录在 `RESOURCES.md` | `/teach` |
| to-questionnaire | [to-questionnaire.md](productivity/to-questionnaire.md) | 把你无法决定的决策转成**问卷**文档，交给拥有答案的人异步填写或会议中对齐；它审问的是"发送对象"而非主题 | `/to-questionnaire` |
| wait-what | [wait-what.md](productivity/wait-what.md) | 你不理解时让 agent **重新解释**刚才的话：补上缺失上下文、用大白话、借用 `GLOSSARY.md` 词汇 | `/wait-what` |
| writing-for-agents | [writing-for-agents.md](productivity/writing-for-agents.md) | 面向 agent 文档的**写作参考**：技能、`AGENTS.md`/`CLAUDE.md`、spec、README 等；核心思想是两个 budget（context load / cognitive load） | `/writing-for-agents` 或自动 |

### 根目录

| 文件 | 作用 |
|---|---|
| [triage-labels.md](triage-labels.md) | 5 个分类角色（needs-triage / needs-info / ready-for-agent / ready-for-human / wontfix）到追踪器标签的映射表 |

## 技能族速览

```
┌─ 访谈族（把想法变成决定）────────────────────────────────────────┐
│ grill-me（无代码库/无状态）→ grill-with-docs（有代码库/有状态）      │
│ grilling（核心循环）→ wayfinder（太大时的多会话地图）               │
└──────────────────────────────────────────────────────────────┘
┌─ 规划→实现流水线───────────────────────────────────────────────┐
│ to-spec（对话→spec）→ to-tickets（spec→tickets）                │
│   → implement（逐个 ticket）或 implement-spec（任务图并行）       │
└──────────────────────────────────────────────────────────────┘
┌─ 质量与修复────────────────────────────────────────────────────┐
│ tdd（先写测试）→ code-review（双维度审查）→ pr（PR 正文）          │
│ diagnosing-bugs（难 bug）→ prototype（设计验证）→ research（查证） │
└──────────────────────────────────────────────────────────────┘
┌─ 维护与治理────────────────────────────────────────────────────┐
│ triage（外部 issues 分类）→ retro（回顾改进环境）                 │
│ improve-codebase-architecture（架构深化调查）→ wizard（手动流程）  │
└──────────────────────────────────────────────────────────────┘
```

## 使用要点

- **首次使用**：在新仓库先跑 `/setup-matt-pocock-skills`，确认 issues 位置、标签词汇与领域文档位置。
- **不知道怎么选**：输入 `/ask-matt` 描述处境，路由器会给出技能序列。
- **斜杠命令在哪输入**：在你与 AI 助手的聊天中，而不是终端。
- **一个已归档项**：`resolving-merge-conflicts.md`（v1.3.0 移除，仅供历史参考）。

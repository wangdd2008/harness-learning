# AI Agent Handbook · 阅读导航

企业级 Agent 落地实践手册（阿里云开源）：覆盖架构、构建、运行、治理、调优全生命周期，每周更新。

**快速入口**：[我的笔记](./笔记.md) · [调研报告](./2026-agent-survey-report.md) · [前言](./00-preface/00-preface.md) · [架构篇](./01-architecture/) · [构建篇](./02-build/) · [运行篇](./03-run/) · [治理篇](./04-governance/) · [调优篇](./05-optimization/) · [实践篇](./06-case-study/) · [总结与展望](./07-conclusion/)

---

## 章节导航

| 篇章 | 章节 | 核心内容 |
| --- | --- | --- |
| 架构篇 | [第 1 章　AI 原生应用的新阶段](<./01-architecture/第 1 章　AI 原生应用的新阶段.md>) | 应用形态演进、Agentic Application 定义与边界、企业成熟度判断。 |
| 架构篇 | [第 2 章　Agentic Application 参考架构](<./01-architecture/第 2 章　Agentic Application 参考架构.md>) | 组件视图、平台责任与生命周期视图。 |
| 构建篇 | [第 3 章　范式：Harness 的主流构建方式和责任边界](<./02-build/第 3 章 范式：Harness 的主流构建方式和责任边界.md>) | 高代码框架、产品化 Harness、Managed Agents 与平台责任。 |
| 构建篇 | [第 4 章　任务：编排、长程推进与协作流转](<./02-build/第 4 章 任务：编排、长程推进与协作流转.md>) | Agent Loop、任务状态机、计划、阶段门禁、委派与完成证据。 |
| 构建篇 | [第 5 章　信息：上下文、状态与可复用能力资产](<./02-build/第 5 章 信息：上下文、状态与可复用能力资产.md>) | Context Builder、Session、Task State、Memory、Knowledge 与 Skill。 |
| 构建篇 | [第 6 章　行动：受控执行、验证反馈与交付准备](<./02-build/第 6 章 行动：受控执行、验证反馈与交付准备.md>) | Action Plane、Function Calling、MCP、A2A、权限、HITL 与验证闭环。 |
| 运行篇 | [第 7 章　Agent 运行时与沙箱](<./03-run/第 7 章  Agent 运行时与沙箱.md>) | 沙箱、Agent Runtime、工作空间与生产运行条件。 |
| 运行篇 | [第 8 章　Agent 状态存储与语义资产](<./03-run/第 8 章 Agent 状态存储与语义资产.md>) | Event Log、Checkpoint、Artifact、长期记忆、RAG 与业务语义。 |
| 运行篇 | [第 9 章　AI 网关与统一流量治理](<./03-run/第 9 章  AI 网关与统一流量治理.md>) | LLM、MCP、Agent 三类流量的身份、权限、预算、审计与审批。 |
| 运行篇 | [第 10 章　Agent 异步任务与自动化流程](<./03-run/第 10 章  Agent 异步任务与自动化流程.md>) | 同步/异步边界、定时任务、长时任务与自动化工作流。 |
| 运行篇 | [第 11 章　Multi-Agent 协作与编排](<./03-run/第 11章  Multi-Agent 协作与编排.md>) | 异构 Agent 接入、团队拓扑、任务分派与编排职责。 |
| 运行篇 | [第 12 章　Agent 分布式通信](<./03-run/第 12 章 Agent 分布式通信.md>) | 能力面、协作面、内构面和人机面的通信协议。 |
| 治理篇 | [第 13 章　Agent 的可观测性](<./04-governance/第 13 章　Agent 的可观测性.md>) | 指标、日志、Trace、事件、成本归因与审计。 |
| 治理篇 | [第 14 章　Agent 安全](<./04-governance/第 14 章　Agent 安全.md>) | Prompt Injection、身份鉴权、逐次校验与数据出域防护。 |
| 治理篇 | [第 15 章　AI 资产的发现与管理](<./04-governance/第 15 章　AI 资产的发现与管理.md>) | Prompt、Skill、MCP 与 Agent 的注册、版本、发现和发布管理。 |
| 治理篇 | [第 16 章　Agent 行为生成与质量验证](<./04-governance/第 16 章　Agent 行为生成与质量验证.md>) | 用户模拟、环境模拟与上线前 Agent Simulation。 |
| 调优篇 | [第 17 章　模型调优](<./05-optimization/第 17 章　模型调优/>) | SFT、Agentic RL、模型蒸馏与推理框架。 |
| 调优篇 | [第 18 章　Agent 调优总览和实践](<./05-optimization/第 18 章　Agent 调优总览和实践/>) | Agent 调优对象、数据飞轮平台选型与接入实践。 |
| 调优篇 | [第 19 章　Agent 轨迹数据](<./05-optimization/第 19 章　Agent 轨迹数据.md>) | 从 Trace 到 Trajectory，组织可复用的行为证据。 |
| 调优篇 | [第 20 章　Agent 运行时数据处理](<./05-optimization/第 20 章　Agent 运行时数据处理.md>) | 运行数据采集、清洗、加工与声明式 Pipeline。 |
| 调优篇 | [第 21 章　Agent 黄金数据集](<./05-optimization/第 21 章　Agent 黄金数据集.md>) | 构建带输入、轨迹、结果与判据的高质量评估数据资产。 |
| 调优篇 | [第 22 章　Agent 优化：Badcase](<./05-optimization/第 22 章　Agent 优化：Badcase.md>) | Badcase 发现、归因、修复、回归与实验验证。 |
| 调优篇 | [第 23 章　受控自进化](<./05-optimization/第 23 章　受控自进化.md>) | 经验转化为 Memory、Skill、工具，并控制自进化风险。 |
| 调优篇 | [第 24 章　Agent 边缘运行时与全球优化](<./05-optimization/第 24 章　Agent 边缘运行时与全球优化.md>) | 边缘运行时、边缘评估、性能成本与内容分发。 |
| 实践篇 | [第 25 章　研发效能](<./06-case-study/第25章 研发效能/>) | 代码审查、缺陷检测、补丁交付与端到端交付。 |
| 实践篇 | [第 26 章　设计工程](<./06-case-study/第26章 设计工程/>) | Vibe Designing 与 GenUI 的设计范式。 |
| 实践篇 | [第 27 章　运维、安全与企业 IT](<./06-case-study/第27章 运维、安全与企业IT/>) | 汽车、连锁零售和企业软件的智能运维实践。 |
| 实践篇 | [第 28 章　客户、销售与运营](<./06-case-study/第28章 客户、销售与运营/>) | 长周期记忆、内容洞察、办公提效和零售门店实践。 |
| 实践篇 | [第 29 章　GOAI Agent Infra 赛道：多 Agent 协同的前沿实践探索](<./06-case-study/第 29 章 GOAI Agent Infra 赛道：多 Agent 协同的前沿实践探索.md>) | 世界人工智能开源大赛作品与 Agent Infra 探索。 |
| 实践篇 | [Jev 专题](<./06-case-study/Jev 专题/>) | Jev 模型解析、结构化决策与完整 Harness 决策流程。 |
| 实践篇 | [Personal Agent 专题](<./06-case-study/Personal Agent 专题/>) | Personal Agent 产品路线与 Agent as a Service 架构。 |
| 总结与展望 | [第 30 章　从 Agentic Application 到 Agentic OS](<./07-conclusion/第 30 章 从 Agentic Application 到 Agentic OS.md>) | 从单个应用走向可协作、可治理、可持续演进的智能系统。 |

---

## 实践案例导航

| 篇章 | 案例 |
| --- | --- |
| 第 25 章 | [ABACI 内核补丁定向测试与缺陷检测智能体](<./06-case-study/第25章 研发效能/ABACI 内核补丁定向测试与缺陷检测智能体.md>) |
| 第 25 章 | [Kitta：领域专用 Code Review Agent](<./06-case-study/第25章 研发效能/Kitta：领域专用 Code Review Agent.md>) |
| 第 25 章 | [PatchPilot Agents：让内核补丁交付成为可编排、可验证的工程闭环](<./06-case-study/第25章 研发效能/PatchPilot Agents：让内核补丁交付成为可编排、可验证的工程闭环.md>) |
| 第 25 章 | [从报警到自动修复，PolarDB-X 的 Loop 工程实践](<./06-case-study/第25章 研发效能/从报警到自动修复，PolarDB-X 的 Loop 工程实践.md>) |
| 第 25 章 | [从编码提效到端到端交付，云通信的人机协作实践](<./06-case-study/第25章 研发效能/从编码提效到端到端交付，云通信的人机协作实践.md>) |
| 第 25 章 | [从评测驱动到端到端交付：AI Agent 安全产品研发提效实践](<./06-case-study/第25章 研发效能/从评测驱动到端到端交付：AI Agent 安全产品研发提效实践.md>) |
| 第 25 章 | [Agentic SOC 安全产品⾃进化背后的组织重构](<./06-case-study/第25章 研发效能/Agentic SOC 安全产品⾃进化背后的组织重构.md>) |
| 第 25 章 | [多 Agent 组成研发小队：AI 研发如何从写代码走向端到端交付](<./06-case-study/第25章 研发效能/多 Agent 组成研发小队：AI 研发如何从写代码走向端到端交付.md>) |
| 第 25 章 | [完整还原 AIOps Agent 的评测和调优实践](<./06-case-study/第25章 研发效能/完整还原 AIOps Agent 的评测和调优实践.md>) |
| 第 26 章 | [GenUI：让 Agent 从给出答案走向交付结果](<./06-case-study/第26章 设计工程/GenUI：让 Agent 从给出答案走向交付结果.md>) |
| 第 26 章 | [Vibe Designing：意图驱动的AI设计范式进化](<./06-case-study/第26章 设计工程/Vibe Designing：意图驱动的AI设计范式进化.md>) |
| 第 27 章 | [吉利汽车智能运维的落地实践](<./06-case-study/第27章 运维、安全与企业IT/吉利汽车智能运维的落地实践.md>) |
| 第 27 章 | [塔斯汀万店连锁的智能运维闭环实践](<./06-case-study/第27章 运维、安全与企业IT/塔斯汀万店连锁的智能运维闭环实践.md>) |
| 第 27 章 | [畅捷通的可观测与智能运维实践](<./06-case-study/第27章 运维、安全与企业IT/畅捷通的可观测与智能运维实践.md>) |
| 第 28 章 | [MiniMax 构建海量长周期记忆数据底座的实践](<./06-case-study/第28章 客户、销售与运营/MiniMax 构建海量长周期记忆数据底座的实践.md>) |
| 第 28 章 | [会计师事务所信永中和的办公提效探索](<./06-case-study/第28章 客户、销售与运营/会计师事务所信永中和的办公提效探索.md>) |
| 第 28 章 | [哔哩哔哩构建全域内容洞察的实践](<./06-case-study/第28章 客户、销售与运营/哔哩哔哩构建全域内容洞察的实践.md>) |
| 第 28 章 | [从单点探索到规模化运营：滔搏体育的企业级智能体实践](<./06-case-study/第28章 客户、销售与运营/从单点探索到规模化运营：滔搏体育的企业级智能体实践.md>) |
| Jev 专题 | [综述：深度解析 Jev 模型：如何快速做结构化决策](<./06-case-study/Jev 专题/综述：深度解析 Jev 模型：如何快速做结构化决策.md>) |
| Jev 专题 | [开发框架：让 Agent 学会判断，从 Jev 接入到完整 Harness 决策流程](<./06-case-study/Jev 专题/开发框架：让 Agent 学会判断，从 Jev 接入到完整 Harness 决策流程.md>) |
| Jev 专题 | [基于Jev 范式决策模型，构建智能工单分诊助手](<./06-case-study/Jev 专题/基于Jev 范式决策模型，构建智能工单分诊助手.md>) |
| Jev 专题 | [Jev 模型智能路由实践](<./06-case-study/Jev 专题/Jev 模型智能路由实践.md>) |
| Personal Agent | [Personal Agent 产品技术与商业观察](<./06-case-study/Personal Agent 专题/Personal Agent 产品技术与商业观察.md>) |
| Personal Agent | [从 Personal Agent 到企业智能体：AgentScope 的 Agent as a Service 架构](<./06-case-study/Personal Agent 专题/从 Personal Agent 到企业智能体：AgentScope 的 Agent as a Service 架构.md>) |

---

## 推荐阅读路径

- **第一次系统了解企业 Agent**：调研报告 → 第 1–2 章 → 第 3–6 章 → 第 13–16 章。
- **正在把 Agent 接入生产**：第 7–9 章 → 第 13–14 章 → 第 18–23 章。
- **正在建设多 Agent 系统**：第 4–6 章 → 第 10–12 章 → 第 13、16 章。
- **负责评估与持续优化**：第 13 章 → 第 18–23 章 → 对应领域实践案例。
- **负责选型或项目立项**：调研报告 → 第 1–3 章 → 实践篇 → 第 30 章。

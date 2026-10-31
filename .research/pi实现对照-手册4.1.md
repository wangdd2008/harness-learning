# pi 的 Agent Loop 与任务状态机 —— 对照《AI Agent 工程实践手册》4.1

> 对照对象：
> - 材料：《AI Agent 工程实践手册》第 4 章 4.1「Agent Loop 与任务状态机」（`01-projects/ai-agent-handbook-main/02-build/第 4 章 任务：编排、长程推进与协作流转.md`，行 15–114）
> - 实现：`01-projects/pi-main`（@earendil-works/pi），重点 `packages/agent`（低层 Agent Loop）与 `packages/durable`（持久化 Harness 任务运行时）
> - 日期：2026-10-31；基于 pi-main 当前 checkout 的源码，未运行测试。

## 0. 一句话结论

pi 把材料的 **Agent Loop（Prepare/Model/Act/Observe）实现了，且在工程细节上超出材料的抽象描述**；但材料的另外三块核心机制 **没有落地**：① Verify 验收阶段（"模型说完成 ≠ 完成"的门禁）；② 权威任务状态对象（goal/stage/todos/facts/budgets/completion_evidence，材料明确要求"消息历史不应成为任务状态的唯一来源"）；③ 任务级预算与显式生命周期状态（WAITING_INPUT / WAITING_APPROVAL / PAUSED / VERIFYING）。pi 的 durable 层实现了自己的持久化任务状态机（pending/running/waiting/sleeping/completing/terminal），是"部分覆盖"，但缺上述四态、无验收器、无预算。

## 1. 材料 4.1 的核心要求（摘录）

| 机制 | 材料要求 |
| --- | --- |
| Loop | 重复「判断—行动—观察—再判断」，直到任务被验证完成、进入等待、失败或取消；五阶段 Prepare → Model → Act → Observe → Verify |
| 权威状态 | 至少维护一份可机读的权威状态：目标、当前阶段、Plan 与 Todo、已确认事实、阻塞项、子任务、Artifact、剩余预算、等待原因、完成依据；**消息历史不应成为任务状态的唯一来源** |
| 状态机 | CREATED / RUNNING / WAITING_INPUT / WAITING_APPROVAL / WAITING_EVENT / PAUSED / VERIFYING / COMPLETED / FAILED / CANCELLED，每个状态有明确的"允许的下一步" |
| 等待语义 | WAITING 不是失败、PAUSED 也不是结束；显式化后上层 Runtime 才能在等待期间释放计算资源并准确恢复；交互界面能说明在等什么 |
| 预算 | 步骤数、总时长、Token 与费用、工具调用次数、子任务并发数、高风险动作次数都应进入预算；耗尽时产生明确终态与未完成清单 |
| Verify | 不接受"我已经完成"作为唯一依据，运行与任务相匹配的验收器；模型说"修复已完成"时状态只能进入 VERIFYING，验收器补齐证据才 COMPLETED |

## 2. pi 的两层实现

### 2.1 packages/agent —— 低层 Agent Loop（产品实际使用）

`packages/agent/src/agent-loop.ts` 的 `runLoop()` 是双层循环（`agent-loop.ts:172–330`）：

- **内层循环**：处理工具调用与 steering 消息。每轮：声明工具装载变化（`declareToolChanges`，`agent-loop.ts:342–372`，把 toolsAdded/toolsRemoved 以 system message 同步给模型，保证回放一致）→ `prepareRequest` 钩子 → 流式取模型响应（`streamAssistantResponse`，`:390–479`，在此把 AgentMessage[] 转成 LLM Message[]）→ 执行工具调用（并行/顺序，`:518–670`）→ 工具结果写入转录 → `finishTurn` 决策（continue/end，`:295–307`）。
- **外层循环**：agent 本要停止时，检查 follow-up 消息队列（用户排队的新输入），有则继续。
- **终止条件**：stopReason 为 error/aborted（硬退出）；`finishTurn` 返回 `{action:"end"}`；或"无工具调用 + 无 steering/follow-up 消息 + 无显式 continue"。
- **状态**：`AgentState`（`types.ts:382–421`）= systemPrompt / model / thinkingLevel / tools / messages / isStreaming / streamingMessage / pendingToolCalls / errorMessage —— **完全是转录中心**，没有任务对象。
- **等待输入的近似**：`Agent` 类提供 `steer()` / `followUp()` 队列（`agent.ts:149–180, 307–325`），"用户在工作时打字"以排队消息注入；`QueueMode` 支持 all / one-at-a-time（`types.ts:50–55`）。
- **审批的近似**：`beforeToolCall` 钩子可 `{block:true}` 拒绝单次工具调用（`types.ts:66–74`；`agent-loop.ts:718–787`），是工具级门禁，不是任务级审批流。

编码产品 `packages/coding-agent` 只依赖 `@earendil-works/pi-agent-core`（如 `coding-agent/src/core/agent-session.ts:34`），不使用 durable。

### 2.2 packages/durable —— 持久化 Harness 任务运行时

`packages/durable` 是独立的"durable conversation, task, and document runtime"（README `packages` 表）。真正的任务状态机在这里：

- `TaskState`（`durable/src/types.ts:658–702`）：`pending` / `running` / `waiting`（等子任务，join policy failFast/allSettled）/ `sleeping`（睡到时钟）/ `completing` / `terminal`。
- `TaskOutcome`（`:621–655`）：`completed` / `failed` / `aborted` / `orphaned` / `faulted`。
- `TaskDefinition`（`:364–387`）：初始 checkpoint 带 `phase` + 全量 phases 映射 + abort 处理器 + migrate；每个 phase handler 必须 commit 新 checkpoint 或终态（"returning without durable progress faults the task"）。
- 内置 `pi.generation` 任务把一次模型生成做成 durable 任务（`harness/generation.ts:159–163`），可等待工具任务（`:239, 356, 380`），有重启限制 `restartLimit`（`:547–557`）。
- 输入受理：`SubmissionRecord` queued/placed/done/unanswered（`types.ts:506–599`）。
- 崩溃恢复、迁移、abort 协议、compaction 任务化等。

durable 的"等待"确实做到了材料要求的"释放 invocation、持久恢复"（waiting/sleeping 时任务无 invocation，时钟/子任务到达后恢复），且是持久化的。

## 3. 逐项对照

| 材料机制 | pi 对应实现 | 达到程度 |
| --- | --- | --- |
| Loop：Prepare | prepareNextTurn / prepareRequest / transformContext / declareToolChanges | ✅ 达到（更细：工具装载差异显式声明、上下文裁剪、模型/思考级别替换） |
| Loop：Model | streamAssistantResponse（AgentMessage→Message 边界转换） | ✅ 达到 |
| Loop：Act | executeToolCalls 并行/顺序、参数校验、beforeToolCall/afterToolCall、abort | ✅ 达到（含 stopReason=length 时拒绝执行截断工具调用等防御，`agent-loop.ts:488–513`） |
| Loop：Observe | 工具结果写入转录、事件流 message_*/tool_execution_*、steering/follow-up 注入 | ✅ 达到 |
| Loop：Verify | 无 | ❌ 缺失（无验收器、无证据门禁） |
| 权威任务状态对象 | 无（agent 层状态=消息转录 + 运行时旋钮） | ❌ 缺失（恰与材料"消息历史不应成为唯一来源"相反） |
| 状态机 | durable：pending/running/waiting/sleeping/completing/terminal + outcome | 🟡 部分（缺 WAITING_INPUT/WAITING_APPROVAL/PAUSED/VERIFYING 四态） |
| 等待释放资源/准确恢复 | durable waiting/sleeping（无 invocation、持久恢复） | ✅ 达到（durable 层） |
| 等待审批/输入显式状态 | 无；仅 beforeToolCall block（工具级）+ steering/follow-up 队列（近似） | 🟡 仅近似 |
| 任务级预算 | 无（仅 AbortSignal、maxRetryDelayMs、thinkingBudgets 请求级思考 Token 预算） | ❌ 缺失 |
| 子代理 / plan mode | README 明说默认跳过（"skips features like sub-agents and plan mode"，`README.md:19`），以扩展提供（examples/extensions/subagent、plan-mode） | 🟡 设计取舍 |

## 4. 差异点明细

### 4.1 材料要求、pi 没有的

1. **Verify 阶段与完成证据**：pi 的"完成"= 模型无更多工具调用（stopReason 正常）或 `finishTurn` 返回 end（agent 层），或任务自己 commit terminal outcome（durable 层）。没有任何"用环境事实/规则验收、验收不过生成新缺口"的机制。材料"即使模型输出'修复已完成'，状态也只能进入 VERIFYING"在 pi 中不存在。
2. **权威任务对象**：材料要求 goal/stage/facts/todos/artifacts/budgets/completion_evidence 一份可机读状态，模型看到的是"由状态生成的当前任务视图"。pi 的 agent 层状态就是转录本身；`transformContext` / `prepareNextTurn` 钩子可以由上层注入外部上下文，但核心不维护任务对象，也没有"从状态生成任务视图"的机制。
3. **任务级预算**：无步骤数/时长/Token 费用/工具调用次数/并发/高风险动作计数。`maxRetryDelayMs` 是 provider 重试退避上限，`thinkingBudgets` 是单次请求思考 Token 预算，`restartLimit`（durable）是崩溃重试上限——都不是材料意义上的任务预算。
4. **显式等待/暂停状态**：WAITING_INPUT、WAITING_APPROVAL、PAUSED、VERIFYING 四个状态在 durable 状态机中不存在；也没有"在等什么/为什么暂停"的机读字段（材料要求观测系统能区分执行慢、审批慢、工具慢）。

### 4.2 pi 超出材料的地方（工程细节）

- 工具装载差异以 system message 显式声明（toolsAdded/toolsRemoved），回放/重放一致性有保证。
- stopReason=length（输出被 token 上限截断）时拒绝执行该轮全部工具调用并提示模型重新发起，防止截断参数被执行（`agent-loop.ts:488–513`）。
- 并行工具执行 + 按 assistant 原始顺序输出 toolResult 消息（`agent-loop.ts:596–670`）。
- `terminate` 标记支持"整批工具结果都要求停止时提前终止"（`agent-loop.ts:700–702`）。
- durable 层：崩溃恢复、重启限制、abort 协议、join policy、compaction 任务化、submission 输入受理（queued/placed/done/unanswered）、持久化等待/睡眠——远超材料抽象，接近 Temporal 风格的 durable execution。
- Agent 事件流（agent_start/end、turn_start/end、message_*、tool_execution_*）为 UI/观测提供了细粒度生命周期事件（`types.ts:516–539`）。

### 4.3 定位判断

材料 4.1 描述的是**企业 Harness 执行内核**的理想形态；pi 自我定位是 **"minimal, extensible agent harness"**（README.md:15–19），并把 sub-agents、plan mode 等明确排除在默认内核之外。因此差异一部分是**设计取舍**（最小内核 + 扩展机制），一部分是**真实缺口**（若以材料 4.1 为标准，pi 需要自建：任务对象、显式状态枚举、验收器/VERIFYING 门禁、预算执行器——pi 的扩展机制支持这类自建，但默认不提供）。

## 5. 证据索引

- 材料 4.1 全节：`ai-agent-handbook-main/02-build/第 4 章 任务：编排、长程推进与协作流转.md` 行 15–114
- 双层循环：`pi-main/packages/agent/src/agent-loop.ts:172–330`
- 终止条件/finishTurn：`agent-loop.ts:295–307`；error/aborted 硬退出：`:254–265`
- 状态=转录：`pi-main/packages/agent/src/types.ts:382–421`；`agent.ts:83–112`
- steering/follow-up：`agent.ts:149–180, 307–325`；`types.ts:50–55`
- beforeToolCall block：`types.ts:66–74`；`agent-loop.ts:718–787`
- durable TaskState/TaskOutcome/TaskDefinition：`pi-main/packages/durable/src/types.ts:621–702, 364–387`
- pi.generation 内置任务：`durable/src/harness/generation.ts:159–163`
- submission 受理：`durable/src/types.ts:506–599`
- README 定位与跳过项：`pi-main/README.md:15–21`
- coding-agent 仅依赖 agent-core：`packages/coding-agent/src/core/agent-session.ts:34` 等

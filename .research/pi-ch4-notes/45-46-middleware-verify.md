# 4.5 / 4.6 对照笔记

对照对象：`01-projects/pi-main`（TypeScript monorepo，`packages/{agent,ai,coding-agent,durable,telemetry,evals}`）。
手册行号取自 `02-docs/ai-agent-handbook-main/02-build/第 4 章 任务：编排、长程推进与协作流转.md`。
本次只精读手册 330–363（4.5）、366–432（4.6）与 437（4.7 小结）。

## A. 结论速览

- **pi 有三层 middleware，不是一个 hook 系统**：`packages/agent` 的内核 hook、`coding-agent` 的事件 `ExtensionRunner`、`durable` 的 `GenerationHooks`/`ToolHooks`。同一个概念在三层里语义不同，对照手册必须指明层，否则会得出相反结论。
- **手册的 6 个时机在 pi 全部有落点，但"Verify 前后"只有空槽位、没有 verifier**：`turn_end`/`agent_before_settle`/`onYield`/`afterRun` 都只是"再跑一轮"的续跑闸门，pi 不判断任务是否真的完成。
- **pi 最强之处恰好是手册说"最好"的那条**：`turn_end` / `agent_before_settle` 让扩展返回结构化 `SessionBoundaryDraft[]`，由内核 `_commitBoundaryDrafts` 统一提交（`agent-session.ts:1040-1044`），而非任意修改共享对象。
- **pi 最弱之处是"放行/修改/短路"语义按事件各写一套**：`tool_call` 只能 block + 就地改 `event.input`；`tool_result` 只能字段级替换；`finishTurn` 只有 `continue|end`；没有任何 hook 能"拒绝并回滚"。
- **恢复策略分两层、粒度都粗**：`packages/ai` 用错误字符串正则分"瞬时/不可重试"（`retry.ts:270-274`）；`durable` 用任务终态 + `replay` 策略分 `failed/aborted/orphaned/faulted`（`types.ts:621-655`）。手册的参数/环境/权限/重复探索/业务条件五类，pi **没有**独立分类。
- **pi 真的实现了"副作用前先记意图"**：`durable` 的 tool task 执行前提交 `{ phase:"execute", arguments, replay }`；崩溃后只有双方都 `safe` 才重跑，否则结束为 `Tool X was interrupted and may have partially run`（`tool.ts:194-226`）。这是全仓最贴近 4.6.1 第二段的代码。
- **无进展检测：pi 完全没有**。grep `no progress|stuck|consecutive|repeated|loop detect` 在 `packages/coding-agent/src`、`packages/agent/src` 只命中 MIME 探测、diff 连续行、主题/安装检测，无一是 agent 循环检测；最大步数也不存在（仅 `durable` 有 `maxTurns`）。
- **4.5.2 四类测试都有真实资产，但强度不均**：扩展顺序测试最完整（`extensions-runner.test.ts` 14 处）；恢复测试最强的是 `durable`（真 SQLite + close/reopen）；预算测试只有 `durable` 有。

## B. 4.5 扩展点对照

### B.0 三层 hook 速查（先定位，再对照）

| 时机 | `packages/agent` 内核 | `coding-agent` 扩展事件 | `durable` hook |
|---|---|---|---|
| Prepare 前 | `transformContext` | `context`、`context_with_system` | `beforeRequest` |
| Prepare | `prepareRequest`、`prepareNextTurn` | — | — |
| Model 前 | — | `before_provider_headers`、`before_provider_request` | `beforeProviderRequest` |
| Model 后 | — | `after_provider_response`、`provider_stream_event` | `afterResponse` |
| Action 前 | `beforeToolCall` | `tool_call` | `beforeTool` |
| Action 后 | `afterToolCall` | `tool_result` | `afterTool` |
| 轮末/完成前 | `finishTurn` | `turn_end`、`agent_before_settle`、`agent_settled` | `onYield`、`afterRun` |

证据：`packages/agent/src/types.ts:193-342`；`packages/coding-agent/docs/extensions.md:340-357`；`packages/durable/src/harness/types.ts:968-999`。

### B.1 六个时机的语义判定总表

| 手册时机 | 放行 | 可修改 | 可短路 | 可追加 | 结论 |
|---|---|---|---|---|---|
| Task 创建前后 | 是 | prompt 面 | 否 | 否 | **不存在**真正的任务创建中间件 |
| Prepare 前后 | 是 | context/model/thinking/messages 整体替换 | 否 | 是（`messages`） | **pi 更强**（可换模型与上下文） |
| Model 调用前后 | 前否/后是 | payload 与 headers | 否 | 否 | 前**可修改**、后**只放行**；无进度检测 |
| Action 前后 | 是 | 参数就地改 / 结果字段替换 | 是（`block`） | 否 | **可短路 + 可修改**，但改参靠副作用 |
| State 变化前后 | 是 | 否 | 是（`continue:false`） | 是（结构化 draft） | **pi 更强**：内核统一提交 |
| Verify 前后 | 是 | 否 | 只 `end` | 只 `continue` | **空槽位，无 verifier** |

### Task 创建前后 → 无对应 hook（`before_agent_start` 只能改 prompt）

- 证据：`packages/coding-agent/src/core/extensions/types.ts:952-958`
```ts
interface BeforeAgentStartEventBase {
	type: "before_agent_start";
	/** The current system prompt, rendered from systemPromptOptions and earlier handler changes. */
	readonly systemPrompt: string;
	/** Mutable prompt sections. Later handlers observe mutations made by earlier handlers. */
	systemPromptOptions: NormalizedBuildSystemPromptOptions;
}
```
- 语义判定：**可修改（仅 prompt 面）**。返回 `{ systemPrompt?, message? }`（`types.ts:1516-1520`）能换系统提示、注入一条 custom message；**不能**设预算、不能绑版本、不能改目标。
- `durable` 侧任务创建（`submit`）**没有 hook**：`admitSubmission` 只做 `requestId` 幂等去重（`submissions.ts:232-240`），没有中间件切点。
- 判定：手册这一格（任务分类、初始预算、版本绑定）**pi 没有**；`before_agent_start` 是更弱的东西。
- 顺序与失败语义：走 `emitBeforeAgentStart`（`runner.ts:1427-1477`），handler 抛错被 `emitError` 吞掉、后续 handler 继续。

### Prepare 前后 → `transformContext` / `prepareRequest` / `prepareNextTurn` / `context` / `context_with_system`

- 证据：`packages/agent/src/agent-loop.ts:228-248`（`prepareRequest` 返回值整体替换运行时状态）
```ts
const requestUpdate = await config.prepareRequest?.(
	{ context: currentContext, model: config.model, thinkingLevel: config.reasoning ?? "off" },
	signal,
);
if (requestUpdate) {
	currentContext = requestUpdate.context ?? currentContext;
	config = { ...config, model: requestUpdate.model ?? config.model, reasoning: /* ... */ };
}
```
- 语义判定：**可修改，且是最强的一类**——可替换 `context`、`model`、`thinkingLevel`（`AgentRequestUpdate`，`agent/src/types.ts:180`）；`prepareNextTurn` 还能追加 `messages`（`agent-loop.ts:195-209`）。
- **不可短路**：没有 `block`/`abort` 返回值；唯一办法是抛错，而抛错会打断整个 loop（`types.ts:203-204` 明确警告 "Throwing interrupts the low-level agent loop without producing a normal event sequence"）。
- `transformContext`（`agent-loop.ts:399-401`）只做 `AgentMessage[] → AgentMessage[]`，契约要求**必须不抛错**（`types.ts:231-232`）。
- 扩展层等价物：`context`（去掉 system 消息交给 handler，内核再恢复，`runner.ts:292-299`）与 `context_with_system`（handler 拥有完整 transcript、连 prompt 与工具声明一起负责，`types.ts:910-918`）。
- 文档把顺序钉死为 `context → context_with_system → before_provider_headers → before_provider_request → after_provider_response → provider_stream_event`（`docs/extensions.md:340-347`）。
- 顺序与失败语义：`coding-agent` 在 `_installAgentRequestProjection` 里**包住** `prepareRequest`（`agent-session.ts:803-859`），先做投影/compaction 再调上一个 hook，形成链；`durable` 的 `beforeRequest` 更简："result is used for that request only"（`durable/src/harness/types.ts:969-974`）。

### Model 调用前后 → `before_provider_headers` / `before_provider_request` / `after_provider_response` / `provider_stream_event`

- 证据：`packages/coding-agent/src/core/extensions/types.ts:926-934`
```ts
export interface BeforeProviderHeadersEvent {
	type: "before_provider_headers";
	headers: ProviderHeaders;
}
```
- 文档：`before_provider_request` "Returning any other value replaces the payload for later handlers and for the actual request"（`docs/extensions.md:854`）。
- 语义判定：**前=可修改（替换 payload / 就地改 headers）；后=只观察（放行）**。
- `after_provider_response` 只有 `status`/`headers` 入参、无返回值（`types.ts:936-941`）；`provider_stream_event` 明确 "Treat it as read-only because mutation can affect normalization"（`docs/extensions.md:896`）。
- **无进展检测在这里没有实现**：手册把"无进展检测"列为该时机的可加能力（手册 340 行），pi 的该时机只有旁观者。
- 顺序与失败语义：`provider_stream_event` 的 handler **按流顺序 await**，"slow handlers delay stream consumption"，抛错只上报、不改 provider 响应（`docs/extensions.md:896`）。

### Action 前后 → `tool_call` / `tool_result`（扩展层）与 `beforeToolCall` / `afterToolCall`（内核）

- 证据：`packages/coding-agent/src/core/extensions/types.ts:1474-1483`
```ts
export interface ToolCallEventResult {
	/** Block tool execution. To modify arguments, mutate `event.input` in place instead. */
	block?: boolean;
	reason?: string;
	terminate?: boolean;
}
```
- 语义判定：**前=可短路 + 可"就地修改"**（没有结构化 patch，改参数靠副作用）；**后=可修改（字段级替换）**。
- `afterToolCall` 合并语义写得很细：`content` 整体替换、`details` 整体替换、无深合并；替换 `content` 而未给 `structuredContent` 会丢掉结构化内容（`agent/src/types.ts:76-104`，实现 `agent-loop.ts:893-907`）。
- **短路语义有手册没有的维度**：`terminate` 让"整批 tool 都 terminate"时提前结束本轮（`agent-loop.ts:700-702`）；被 block 的调用也能带 `terminate`（`agent-loop.ts:755-765`）。
- 顺序与失败语义：`emitToolCall` **第一个 `block` 立即返回**（`runner.ts:1257-1262`），且**没有 try/catch**——handler 抛错冒泡到 `_beforeToolCall`（`agent-session.ts:691-696`）再被 `prepareToolCall` 捕获成 error tool result（`agent-loop.ts:780-786`），即"抛错=阻断"（`docs/extensions.md:3221`）。
- 相邻路径相反：`tool_result` 抛错被吞、后续 handler 继续（`runner.ts:1223-1232`）。**两条相邻路径的失败语义完全相反。**
- `durable` 侧更干净：`beforeTool` 返回 `{ arguments?, block? }`（结构化换参），注释 "the first `block` wins, otherwise `arguments` replace the call's arguments. A throw blocks"；`afterTool` 直接替换 `ToolExecutionResult`（`durable/src/harness/types.ts:1026-1049`）。

### State 变化前后 → `SessionBoundaryDraft` + `_commitBoundaryDrafts`（pi 最强的一处）

- 证据：`packages/coding-agent/src/core/extensions/types.ts:1042-1045`
```ts
export interface BoundaryResult {
	entries?: SessionBoundaryDraft[];
	continue?: boolean;
}
```
- 内核统一提交：`packages/coding-agent/src/core/agent-session.ts:1040-1044`
```ts
private _commitBoundaryDrafts(drafts: SessionBoundaryDraft[]): void {
	const appended = this._applyBoundaryDrafts(this.sessionManager, drafts);
	this._refreshFinalizedContext();
	for (const entry of appended) this._emit({ type: "entry_appended", entry });
}
```
- 语义判定：**可追加（结构化 patch，由内核提交）+ 可短路（`continue:false`）**；**不能** veto 已完成的状态写入。draft 类型被限定为 `custom | custom_message | context_edit | compaction`（`types.ts:1021-1025`）。
- 顺序与失败语义：`emitBoundary` 逐 handler 累积 `entries`/`continue`，**每个 handler 之后都重建 `context`**，让下一个 handler 看到上一步结果（`runner.ts:1046-1080`）。
- entries 非法时整批作废：`{ entries: [], continue: false, valid: false }`（`runner.ts:1082-1084`）。
- 文档补充："The complete proposal is validated before it is appended in list order after all handlers finish; a handler error is reported and later handlers still run. Validation prevents partially applied semantic errors, but persistence is not transactional."（`docs/extensions.md:734`）。
- 判定：这一处 **pi 比手册更强**（手册说"最好返回结构化 Decision/Patch"，pi 已经这么做）；但只有 `turn_end` / `agent_before_settle` 两个时机有这待遇。

### Verify 前后 → `finishTurn` / `turn_end` / `agent_before_settle` / `onYield` / `afterRun`（全是空槽位）

- 证据：`packages/agent/src/types.ts:146-147`
```ts
/** Decision returned by {@link FinishTurn}. Returning undefined preserves normal scheduling. */
export type AgentTurnDecision = { action: "continue" } | { action: "end" };
```
- 语义判定：**可短路（end），但没有"拒绝完成"的语义**。
- `turn_end` 的 `continue` 只能"再要一次 provider 请求"（`agent-session.ts:894-899`）；`agent_before_settle` 同理（`agent-session.ts:2038-2060`）。
- `durable` 的 `onYield` 返回 `{ continue: UserInput }`："the first `continue` appends a user message and continues the run"（`durable/src/harness/types.ts:987-988`）。
- **pi 没有内置 verifier**：`grep -i "verif(y|ier|ication)" packages/**/*.ts` 的命中全部是 OAuth PKCE 的 `code_verifier`、`packages/evals/src/harness.ts:257` 的 `verifySystemPrompt`（断言系统提示含某段文档）、`package-manager-cli.ts:110` 的 `verifyManagedRelease`（校验自身发布产物）。无一是"任务完成验证器"。
- 顺序与失败语义：`onYield` "reports throws without stopping later handlers"（`test/harness-tools.test.ts:864`）；**循环上界由扩展自己负责**："bounding `onYield` loops is the extension's job"（`generation.ts:881`）。

### 扩展自身：顺序 / 读写范围 / 冲突 / 失败 / 可观测

- **顺序**：load order → registration order，无 priority 字段。`snapshotEventHandlers` 每次 dispatch 取快照（`runner.ts:276-278`）；文档："Adding or removing a handler does not affect a dispatch already in progress"（`docs/extensions.md:1566`）。
- **读写范围**：**没有声明式读写范围**。分两类：就地可变对象（`before_provider_headers.headers`、`before_agent_start.systemPromptOptions`、`tool_call.input`）与"返回值链"（`input`/`context`/`context_with_system`/`message_end`/`tool_result`/`before_provider_request`），见 `docs/extensions.md:404-411`。判定：**更弱**——谁改了共享对象无法从类型上约束。
- **冲突规则**：**分散且不一致**。`tool_call` 第一个 block 胜（`runner.ts:1259`）；`tool_result`/`message_end` 字段级 last-wins（`runner.ts:1201-1222`、`1156-1180`）；`cache_warming_decision` 最后一个 action 胜（`runner.ts:1127-1148`）；`project_trust` 第一个 yes/no 胜（`test/extensions-runner.test.ts:131`）；同名 tool/flag "keeps first"（`test/extensions-runner.test.ts:428,777`）。判定：**有规则但无一览表**。
- **失败语义**：**按事件分别定义**，见 `docs/extensions.md:3218-3223`："Extension errors are logged, agent continues / `tool_call` errors block the tool (fail-safe) / `user_bash` errors block the command"。
- 代码对应：`emit` 吞错（`runner.ts:1102-1120`）、`emitToolCall` 不吞（`runner.ts:1249-1267`）、`emitUserBash` 吞后重抛（`runner.ts:1283-1293`）、`emitBoundary` 吞错但使整批 draft 失效（`runner.ts:1058-1078`）。
- **可观测性**：`emitError` 广播到 `errorListeners`（`runner.ts:749-750`），错误携带 `extensionPath`/`event`/`stack`；内核侧有 `auto_retry_start`/`auto_retry_end` 事件（`agent-session.ts:234-235`）与 `packages/telemetry` 的 span/metric 契约（`src/index.ts`、`src/testing/conformance.ts`）。判定：**有，但是 ad-hoc 事件，不是统一 middleware trace**。

## C. 4.5.2 四类测试 → pi 的真实测试资产

| 手册测试类型 | pi 有的对应物 | 证据 file:line | 判定 |
|---|---|---|---|
| 状态迁移测试（内核） | `finishTurn` 在 tool-result 之后、`turn_end` 之前跑；`action:end` 跳过队列轮询；`terminate` 整批结束；被 block 且 `terminate` 的批次；并行批次部分 terminate | `packages/agent/test/agent-loop.test.ts:1108,1217,1503,1633,1732,1783,1841,1899,1964` | **有**，但断言事件序列，不是白盒状态机模型 |
| 状态迁移测试（session 层） | `agent_before_settle` 的 custom message 续跑；settle 期间 abort 时"提交 drafts 但抑制 continue"；非法显式 continuation 不吞掉自然 tool 续跑 | `packages/coding-agent/test/suite/agent-session-boundaries.test.ts:269,312,439,705` | **有**，且覆盖手册没提的"非法 continuation"分支 |
| 扩展顺序测试 | `project_trust` 首个决策、短路冲突告警、同名 tool 保第一个、抛错触发 error listener、`user_bash` fail-closed、boundary 链式提案、非法 boundary 被后来 handler 修复、抛错前共享 mutation 保留、`tool_result` 链式与部分 patch、dispatch 中注册延后生效、嵌套 dispatch 用新列表、抛错隔离 | `packages/coding-agent/test/extensions-runner.test.ts:131,342,428,603,630,709,919,983,1031,1062,1109,1328,1348,1408` | **有，且很强**——4.5.2 里 pi 覆盖最完整的一类 |
| 扩展顺序测试（事件可见序） | "扩展事件先于公共订阅者"、单 prompt / 单 tool turn 的完整事件序 | `packages/coding-agent/test/suite/agent-session-retry-events.test.ts:229,269,292` | **有** |
| 恢复测试（真实 close/reopen） | unsafe tool 中断后给回 durable partial；safe tool 意图丢失/兄弟已存时重跑；"stored 与 current 双 safe 才重跑"；重跑用重跑时刻的 cwd；意图前中断重跑 `beforeTool` 且只执行一次；generation 工具阶段中断重跑；aborted tool 带 partial 继续；真实 bash 在 close/reopen 后作答；safe 重跑前清上次进度 | `packages/durable/test/harness-tools-recovery.test.ts:108,109,136,200,229,277,316,353,402,430` | **有，全仓最强**：SQLite 落盘 + 真 close/open |
| 恢复测试（任务/生成层） | task 恢复、generation 恢复、restart 失败、嵌套 tool 重启 | `durable/test/harness-tasks-recovery.test.ts:47,878`；`harness-generation-recovery.test.ts`；`harness-restart-failure.test.ts`；`harness-nested-tools-restart.test.ts` | **有** |
| 恢复测试（coding-agent 侧） | resume 后截断的 call 与 result 一起被省略；length 恢复预算；retry 收尾；overflow 恢复；恢复 compaction 失败时不重试 | `coding-agent/test/suite/regressions/11227-recovery-omits-tool-results.test.ts:6,15`；`agent-session-boundaries.test.ts:740,747,780,829,877,895,929,975,1015,1033` | **有但语义更弱**：重放 `SessionManager` 条目，不是真杀进程/断连接 |
| 预算与边界测试 | `maxTurns` 到达即"像失败一样"结束（`reason: turn_limit`、`detail: "1 turn"`），continue 后预算重置；`maxTurns` 校验（≥1 整数）；`restartLimit` 连续截断上限；连续截断但 checkpoint 未变不算 progress | `durable/test/harness-turn-limit.test.ts:1,69,71,106,139,249`；`test/harness-blocked.test.ts:137,233,274,329,370`；`durable/src/harness/generation.ts:1115-1124` | **部分**：只有 `durable` 有步骤/重启预算 |
| 预算与边界测试（coding-agent） | **未找到**。`packages/coding-agent/src` 内 grep `maxSteps|maxTurns|stepLimit|costLimit|maxCost` 无命中；只有 compaction 阈值（context window 预算）与 `settings.retry.maxRetries` | 查过 `coding-agent/src/core/{agent-session,settings-schema,settings-defaults}.ts`、`packages/agent/src` | **没有**：coding-agent 既无步数、无时间、无费用预算 |
| 模型输出替代 | 脚本化 faux provider：`fauxProvider({models})` + `setResponses/appendResponses`、deferred 响应、`fauxAssistantMessage/fauxToolCall/fauxText` | `packages/ai/src/providers/faux.ts:42-80`；装配 `coding-agent/test/suite/harness.ts:151-158`；`durable/test/chat-support.ts`（`setup.faux`） | **有（模拟器/固定样本）**；**未找到"录制回放"**：grep `record|replay` 在 `packages/evals` 只命中 transcript 重放（`src/harness.ts:388`） |

## D. 4.6 可靠性逐条对照

### 4.6.1 按失败类型选恢复策略 → pi 只分两类，且分在不同层

- **瞬时错误 → 有界退避**：`packages/ai/src/utils/retry.ts:209-259` 的 `retryAssistantCall`，`delay = baseDelayMs * 2^(attempt-1)`，被 `maxAgentDelayMs`（默认 60s）截断（`retry.ts:146-150`）。
- `coding-agent` 的 `_prepareRetry` 复用同一策略（`agent-session.ts:3843-3883`），每次重试前 `_omitRecoveryAttempt` 把失败的那一轮从模型投影里剔除（`agent-session.ts:3867-3868`）。
- **不可重试** 靠**字符串正则**：`NON_RETRYABLE_PROVIDER_LIMIT_ERROR_PATTERN` 覆盖配额/账单（`retry.ts:7-35`），`RETRYABLE_PROVIDER_ERROR_PATTERN` 覆盖 429/5xx/网络/流中断（`retry.ts:37-125`）；`isRetryableAssistantError` 先查前者再查后者（`retry.ts:270-274`）。
- **判定**：手册六类失败（瞬时/参数/环境/权限/重复探索/业务条件）在 pi 里只有第 1 类有策略。参数/环境/权限被折叠成"tool 返回 error result 交给模型自己看"，没有恢复分支；grep `permission|denied|EACCES` 在 `packages/agent/src` 无命中。属 **pi 有但语义更弱**。
- **降级路径记录**：**没有**。`prepareRequest`/`beforeRequest` 能换 model（`agent-session.ts:838-858` 的虚拟模型路由），但**不写降级原因**到会话；只有 `reason: "retry" | "user" | "continuation"` 作为 router 输入，不是持久化审计。

### 4.6.1 "上次到底有没有发生" → pi 有真实实现（`durable`），但答案来自静态策略而非状态查询

- 执行前提交意图：`packages/durable/src/harness/tool.ts:194-197`
```ts
await runtime.commit(() => {
	const intent = { phase: "execute", arguments: final, replay: tool.replay ?? "unsafe" } as const;
	return { status: "running", checkpoint: intent };
}, context);
await run(runtime, task.input, call, tool, final, context);
```
- 恢复时判定（`tool.ts:200-226`）：`if (replay === "safe" && tool?.replay === "safe")` 才重跑；否则 `const message = "Tool ${call.name} was interrupted and may have partially run"`，以 `ending = { status: "failed", message }` 落成 error result。
- 幂等键：**两级**。输入级 `requestId` 去重（`submissions.ts:232-240`）；嵌套调用级 "Each nested call has a key ... A replay-safe caller that reruns after a crash and calls in the same order, or passes the same keys, gets the nested calls it already made back"（`durable/README.md:328`，实现 `tool.ts:894`）。
- **缺失**：手册要求"优先查询状态"（去问外部系统上次成没成）。pi **不查**——`replay` 是工具作者声明的静态属性（`agent/src/types.ts:489-490`："Recovery policy for an effect whose durable intent exists but whose outcome is unknown"），没有"先 query 再决定"的框架能力。
- README 自认："a replay-safe tool with external effects still needs its own idempotency"（`durable/README.md:328`）。判定：**机制强、语义弱半格**。
- 测试佐证：`harness-tasks-recovery.test.ts:47` 的 "Fake external service whose operations are idempotent by request key"——幂等由被测方自己实现，不是 harness 提供。

### 4.6.1 无进展检测 → pi 完全没有

- 查过 `packages/coding-agent/src`、`packages/agent/src` 全量 grep `no progress|noProgress|stuck|consecutive|repeated|repetition|same arguments|loop detect`。
- 命中仅为：MIME 探测（`utils/mime.ts`）、diff 连续行（`components/diff.ts:95,104`）、主题/安装检测、`tool-search` 的参数不重复注释（`extensions/codemode/tool.ts:325`）。
- 唯一的"进度"概念在 `durable` 且语义不同：`restartLimit` 统计"连续被崩溃截断且 checkpoint 未变"的次数（`harness-blocked.test.ts:329` "does not count the same checkpoint committed again as progress"；`types.ts:632-640`）。这是**崩溃恢复**的进度，不是"模型在打转"。
- 判定：**没有**。最大步数也不存在（见 C 表），所以手册"无进展检测比最大步数更早发现问题"在 pi 里两者皆无。

### 4.6.2 完成由证据决定 → pi 是"完成由调度决定"

- 模型只能"申请完成"这一结构**成立**：模型只有 `stopReason`（`stop`/`toolUse`/`length`/`error`/`aborted`），loop 在"无 tool call、无 steering、无 followup、无显式续跑"时退出（`agent-loop.ts:305-329`）。
- 但 harness 侧"提交完成"的动作**只是停止调度**。
- `durable` 显式区分两件事：run 以 `{ status: "done", answer }` 结束（`generation.ts:887`、`963`、`1113`），任务终态由任务实现提交 `{ status: "completed", result }`（`generation.ts:1140`；类型 `types.ts:621-627`）。**terminal outcome 的写者是 harness 代码，不是模型**——手册这条在 pi 里成立。
- 但"依据事实"不成立：`answer` 是**一条 assistant entry 的 id**（`RunSummary.answer`，`types.ts:1010-1011`），不是 artifact 集合、不是结构化缺口。判定：**有"申请/提交"的分离，没有"证据"这一层**。

### 4.6.2 验证强度五层 → 只有第 1、2 层存在，且都不是"验证完成"

- **结构验证**：有，但作用于工具参数/输出 schema，不是完成产物——`validateToolArguments`（`agent-loop.ts:737`）、`outputSchema`/`structuredContent`（`agent/src/types.ts:474-478,433`）。对"任务产物"无任何 schema 校验。
- **环境验证**：有，是工具的事不是 harness 的事——`durable` 的 `ExecutionEnv`（`src/env/`）、`tools/read.ts` 读真实文件。harness 不比对"预期状态 vs 实际状态"。
- **确定性验证**：**没有内建**。没有 verifier 跑测试并解析结果；`durable/test/examples/32-tests-after-edits.ts` 用扩展实现"改完跑测试"，是示例不是内核。
- **独立模型验证**：**结构上可搭、无内建**。`durable/test/examples/27-reviewer.ts:33-44` 是唯一范例——独立 conversation、独立 model、只有 `read` 工具、独立 cwd（`27-reviewer.ts:79-90`），而断言"完成"的方式是
```ts
onYield: (answer) =>
	textOf(answer).includes(DONE)
		? undefined
		: { continue: `Look again ... Say "${DONE}" when there is nothing left.` },
```
  即**靠模型自述**——恰好是手册 4.5.1 "Verify 前后 — 不应做的事"点名的"仅凭模型自述标记完成"。
- **人工验收**：有，但在 coding-agent 的交互面、不在完成判定里：`tool_call` 拦截 + UI confirm（`docs/extensions.md:2740` 用 `annotations` 决定是否确认）。判定：**pi 把人工确认放在"执行前"，手册要求放在"完成前"**。

### 4.6.2 "验证失败是新的 Observation" → pi 有这个形状，但没人往里填

- `turn_end` / `agent_before_settle` 的 `continue` + draft entries 就是"把验证结果写成新 observation 再继续"的通道（`types.ts:1042-1045`、`agent-session.ts:2038-2060`）；`onYield` 的 `{ continue: UserInput }` 同理（`durable/src/harness/types.ts:987-988`）。
- **但 Verifier 该返回的"结构化缺口 / 失败证据 / 可修复性"没有类型**。最接近的是工具结果的 `isError` + `details`（`agent/src/types.ts:423-446`）与 `TaskOutcomeError.detail`（`durable/src/types.ts:613-618`）。
- 判定：**有，但只是"再要一轮"，没有"缺口"这个概念**。

### 4.6.3 完成证据集合 / 4.6.4 平台只观测

- 4.6.3：pi **没有 artifact 引用模型**。最接近的持久化证据是 session entry id（`answer`）、`ToolResultEntry`（`ToolResultEntry.is(entry)`，`harness-tools-recovery.test.ts:67-69`）、`structuredContent`/`details`。
- 没有 `artifacts/**` 形式的任意文件引用与校验。`evals` 有 `PI_SESSION_SNAPSHOT_ARTIFACT`（`src/harness.ts:35` 导入，`src/report.ts` 定义），但那是**评测**产物快照，不是任务完成证据。查过 `grep -i "artifact"` 在 `packages/durable/src`、`packages/coding-agent/src` 无任务级命中。
- 4.6.4：**pi 的分层与手册一致**。`packages/telemetry` = 契约 + 适配器（`memory`/`noop`）+ 一致性测试（`src/index.ts`、`src/noop.ts`、`src/testing/conformance.ts`，由 `test/conformance.test.ts` 覆盖）。
- `packages/evals` 驱动真实 `AgentSession`（`src/harness.ts:11-20`），`verifySystemPrompt` 校验系统提示（`src/harness.ts:257`），落 `PI_SESSION_SNAPSHOT_ARTIFACT`（`src/harness.ts:35`）。
- `durable/src/harness/telemetry.ts:17,105,113` 定义任务级事件名（含 `task_faulted`/`task_orphaned`、`pi.durable.replay`）。
- 判定：**pi 与手册一致**——观测/评估是独立包，不参与"这次任务算不算完成"：evals 给分，`GenerationTask` 给 `done`，两者不通信。

## E. 完成验证：pi 到底怎么算"完成"

**【链路一：内核 loop —— 没有"完成"这个概念】**

1. provider 给 `stopReason`（`stop`/`toolUse`/`length`/`error`/`aborted`）。
2. 有 tool call → 执行；无 tool call → `hasMoreToolCalls = false`（`agent-loop.ts:271`）。
3. `finishTurn` 决定 `continue`/`end`（`agent-loop.ts:295-303`）。
4. 无 steering / follow-up / 显式续跑 → `break` → `agent_end`（`agent-loop.ts:325-329`）。
- 这条链里唯一类似"完成"的是 `stopReason === "stop"`，它是**模型输出格式的属性**，不是任务属性。

**【链路二：coding-agent —— 把 stopReason 翻译成 outcome】**

- `agent-session.ts:866-867`
```ts
this._lastActivityOutcome =
	message.stopReason === "aborted" ? "aborted" : message.stopReason === "error" ? "error" : "completed";
```
- 即 `"completed"` 的含义是"这一轮没报错"，不是"目标达成"。
- 之后：`_handlePostAgentRun` → 可重试？→ 可 compaction？→ 有队列？→ `_runBeforeSettleBoundary`（`agent-session.ts:2000-2060`）→ `_emitAgentSettled`（`agent-session.ts:1094-1116`）。
- **`agent_before_settle` 是唯一能"在完成前拦一下"的地方**，但它只能 `continue`（再跑一轮）或什么都不做；不能标 failed、不能写"验证未通过"。没有 handler 时直接跳过（`agent-session.ts:2039`）。

**【链路三：durable —— 把"完成"写成持久化终态】**

- 答完（模型不再调工具）→ `endRun(..., { status: "done", answer: entry.id })`（`generation.ts:887`）→ inputs settle `done`（`live.ts:290-300`）→ generation 任务 `{ status: "completed", result: { entryId } }`（`generation.ts:871`、`1140`）。
- 失败路径有 10 个具名理由（`live.ts:108-118`：`model_error`/`no_model`/`aborted`/`reset`/`faulted`/`orphaned`/`interrupted`/`restart_limit`/`nothing_to_answer`/`turn_limit`），全部由 **harness 判定**，模型无法自称。
- `onYield`（完成申请前）与 `afterRun`（提交后、run 真正结束前）是两个验证钩子位置；`afterRun` 还能创建子任务把 run 拖住直到子任务终态（`types.ts:991-999`："The requested tasks of every hook are created together as children of the generation, which keeps the run, and the conversation busy, until they are terminal"）。
- **这是 pi 里最像 Verifier 的机制**，但没有内置实现，也没有"缺口"返回类型。

**【缺什么】**

1. 没有 Verifier 抽象：无 `verify(): { ok, gaps }` 之类的类型；`packages/agent`、`packages/coding-agent` 全无。
2. 没有证据模型：`answer` 是 entry id，不是 artifact 清单；无 `evidence: { key -> uri }`。
3. 完成判定不读事实：`"completed"` 只由 `stopReason` 推出（`agent-session.ts:866-867`），`done` 只由"没有下一轮"推出（`generation.ts:887`）。
4. 验证失败无落点：没有"验证未通过"这一终态，只有"再跑一轮"（`continue`）或"失败"（`failed`），中间状态缺失。
5. 无缺口结构：`TaskOutcomeError.detail?: JsonValue`（`types.ts:613-618`）是自由 JSON，没有 schema 强制"缺口/证据/可修复性"三件套。

## F. 与手册根本分歧 / 待确认

1. **"Middleware"在 pi 里不是一个可命名的一层。** 手册假定存在统一 middleware 契约；pi 实际是三层各自演化：`agent` 6 个函数字段 hook、`coding-agent` 40+ 事件、`durable` 4 组 hook。**同一概念（如 beforeTool）三层语义不同**：`agent.beforeToolCall` 只能 block（`types.ts:66-74`）；`extension.tool_call` 能 block + 就地改参（`types.ts:1474-1483`）；`durable.beforeTool` 能 block + 结构化换参（`types.ts:1026-1031`）。
2. **"放行/修改/短路/追加"作为统一返回值类型在 pi 里不存在**，只有逐事件的 ad-hoc 形状。手册第 345 行说"最好让扩展返回结构化 Decision 或 Patch"，pi 只在 `turn_end`/`agent_before_settle` 做到（`BoundaryResult`），其余靠就地修改——正是手册警告的"任意修改共享对象"。
3. **"验证"与"完成"在 pi 里被有意分开，但分开的方式是"都不做"。** pi 的立场看起来是"harness 只提交**终态**，完成语义属于调用方"（`durable` 的 `RunSummary`/`TaskOutcome` 可观测，但不含价值判断）。手册认为提交完成是 harness 的责任。这是**设计哲学分歧，不是遗漏**，需要确认哪一边是目标。
4. **待确认：`onYield` 的循环上界归谁。** 代码注释明确 "bounding `onYield` loops is the extension's job"（`generation.ts:881`），`examples/32-tests-after-edits.ts:89` 也写 "the extension caps the loop itself"。手册 4.6.1 认为无进展检测是 harness 职责；pi 推给扩展。若要在 pi 上实现手册的 Verify，这一条必须先定归属。
5. **待确认：`packages/chord` 是否纳入对照。** 它也有 job dedupe / idempotent stop / restart 语义（`src/next/jobs/definition.ts:33`、`docs/next/decisions.md:648`），但看起来是比 `durable` 更新的存储/调度层（`docs/next/slices.md`），与本节关系间接，本次未展开。
6. **代码成立但测试未覆盖的一处**：`docs/extensions.md:3221` 说 "`tool_call` errors block the tool (fail-safe)"，代码路径是 `emitToolCall` 抛错 → `_beforeToolCall` 重抛（`agent-session.ts:691-696`）→ `prepareToolCall` catch 成 error result（`agent-loop.ts:780-786`）。链读通了，但**没有找到直接覆盖它的测试**（`extensions-runner.test.ts:603` 测"handler 抛错触发 error listener"，`630` 测 `user_bash` fail-closed）。
7. **待确认：手册 4.5.2 的"暂停"语义在 pi 里对应什么。** 手册说"每个状态只接受合法事件，暂停、取消和失败正确传播"。pi 有取消（`AbortSignal` 贯穿 `agent-loop.ts` 每个 hook 调用点，如 `748`、`767`、`585`）与失败（`stopReason: "error"`），但**没有"暂停"**：grep `pause` 在 `packages/agent/src`、`packages/coding-agent/src/core/agent-session.ts` 只命中 UI/主题。`durable` 有暂停态 `status: "waiting"`（`durable/src/types.ts:673-677`），但那是等待子任务终态，不是可恢复的用户暂停。

## G. 4.7 小结里与本任务相关的两句，逐句检验

- 小结原句（手册 437 行）："稳定的 Agent Loop 以 Prepare、Model、Act、Observe、Verify 推进任务"。
  - **前半成立**：`agent-loop.ts:172-330` 就是 Prepare（`prepareRequest`）→ Model（`streamAssistantResponse`）→ Act（`executeToolCalls`）→ Observe（tool result 入 context）→ 下一轮。
  - **Verify 不成立**：这个五段里没有 Verify 阶段。`finishTurn` 在 Observe 之后只决定"是否再来一轮"，不做任何验证（`agent-loop.ts:289-303`）。
- 小结原句（手册 437 行）："Middleware 则使能力可以在不重写核心 Loop 的前提下组合演进"。
  - **成立，且是 pi 的设计主线**：`agent-loop.ts` 全 959 行里没有任何"压缩/计划/权限/路由"分支；这些能力全部通过 hook 注入——compaction 走 `prepareRequest`/`prepareNextTurn`（`agent-session.ts:792-859, 914-947`），模型路由走 `prepareRequest`（`agent-session.ts:838-858`），权限走 `tool_call`（`types.ts:1474-1483`）。
  - **代价**：能力组合顺序由包装链决定（`previousPrepareRequest` 闭包叠加，`agent-session.ts:804-805`），没有声明式顺序，正是手册提醒"应用团队要为能力组合、生命周期顺序负责"的那一点。

## 附录 A：缺失判定的检索覆盖（供复核）

| 结论 | 检索方式 | 覆盖范围 |
|---|---|---|
| 无 verifier | `grep -i "verif(y\|ier\|ication)"` include `*.ts` | 全 `packages/`：命中仅为 OAuth PKCE、`evals/src/harness.ts:257`、`package-manager-cli.ts:110` |
| 无无进展检测 | `grep "no progress\|noProgress\|stuck\|same tool\|repeat(ed)? (call\|tool)\|loop detect"` | 全 `packages/`：命中仅为 chord/durable 的 drain timeout、UI 测试、CHANGELOG |
| 无重复调用检测（coding-agent） | `grep "consecutive\|repeated\|repetition\|identical call\|same arguments\|detect"` | `packages/coding-agent/src`：命中仅为 MIME、diff 连续行、主题、安装检测、`codemode/tool.ts:325` |
| 无步数/费用预算 | `grep "maxSteps\|maxTurns\|stepLimit\|budget\|maxCost\|costLimit"` include `*.ts` | 全 `packages/`：`maxTurns` 只出现在 `durable`；`budget` 全为思考 token / compaction / codemode 中断预算 |
| 无 artifact 证据模型 | `grep -i "artifact"` 目检 | `packages/durable/src`、`packages/coding-agent/src`：无任务级命中；`evals` 的 `PI_SESSION_SNAPSHOT_ARTIFACT` 是评测快照 |
| 无工具级重试 | 读 `prepareToolCall`（`agent-loop.ts:718-787`）与 `executePreparedToolCall`（`831-867`） | 工具抛错直接转 error result，**不重试**；重试只存在于 provider 调用层 |
| 无"先查状态"恢复 | 读 `durable/src/harness/tool.ts:194-226` 全段 | 恢复分支只有 `replay === "safe" && tool.replay === "safe"` 一条，无 query 路径 |
| 无录制回放 | `grep "record\|replay\|snapshot"` include `*.ts` | `packages/evals`：命中为 transcript 重放（`src/harness.ts:388`）与 report 打分，无 provider 流录制 |

## 附录 B：本次精读的文件（断言的事实来源）

- `packages/agent/src/types.ts`（全 539 行）、`packages/agent/src/agent-loop.ts`（全 959 行）
- `packages/ai/src/utils/retry.ts`（全 275 行）、`packages/ai/src/providers/faux.ts:1-80`
- `packages/coding-agent/src/core/extensions/types.ts:900-1060, 1425-1565`；`.../runner.ts:240-300, 1036-1300`；`.../agent-session.ts:640-948, 1000-1130, 1180-1300, 1975-2085, 3820-3940`
- `packages/coding-agent/src/core/event-bus.ts`（全 33 行）、`output-guard.ts:1-60`（判定：TUI stdout 接管，与验证无关）
- `packages/coding-agent/docs/extensions.md:295-420, 3214-3243` 及事件表 grep
- `packages/durable/src/types.ts:608-680`、`harness/types.ts:55-100, 542-680, 950-1070`、`harness/tool.ts:180-250`、`harness/generation.ts:620-770, 860-990, 1080-1144`、`harness/live.ts:95-134`、`harness/submissions.ts:222-251`、`errors.ts`（全 83 行）
- `packages/durable/test/harness-tools-recovery.test.ts:1-120` 及其 it 清单；`harness-turns-limit`→实为 `harness-turn-limit.test.ts:1-80`；`harness-blocked.test.ts` it 清单；`harness-after-run.test.ts`、`harness-tools.test.ts`、`harness-inbox.test.ts` 的 `onYield`/`afterRun` grep
- `packages/durable/test/examples/27-reviewer.ts`（全 111 行）
- `packages/agent/test/agent-loop.test.ts` it 清单（38 处）
- `packages/coding-agent/test/extensions-runner.test.ts` it 清单（68 处）；`test/suite/agent-session-boundaries.test.ts` it 清单（28 处）；`test/suite/agent-session-retry-events.test.ts:229-273`；`test/suite/harness.ts:145-272`；`test/suite/regressions/11227-*.test.ts:1-60`
- `packages/evals/src/harness.ts:1-55`；`packages/telemetry/src` 文件清单

**未运行**：任何 build / test / git 命令（遵守只读约束）。因此"测试能过"不是本笔记的断言，"测试存在且断言了什么"是。

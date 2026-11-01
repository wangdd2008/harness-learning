# 4.2 / 4.3 对照笔记

对照对象：`01-projects/pi-main`（commit 状态未记录，只读）。手册两节：4.2 Planning/Todo/阶段目标、4.3 Subagent 与任务委派。
前提事实：pi 明确把这两块**排除在默认功能外**，以 extension 示例提供。
- 证据：`README.md:19` —— "Pi ships with powerful defaults but skips features like sub-agents and plan mode. Ask Pi to build what you want, or install a package that does it your way."
- 因此下文的 "pi 实现" 若无特殊说明，均指 `packages/coding-agent/examples/extensions/` 下的示例扩展，而非 `packages/coding-agent/src/` 的内核能力。这个区分是全文的主轴。

---

## 4.2 Planning、Todo、阶段门禁

### 4.2.1 计划应外部化为可读/可改/可验证的控制对象

- pi 实现：计划**不是**类型化对象，而是助手回复里一段以 `Plan:` 为标题的编号文本，由正则解析成 `TodoItem[]`；状态经 `pi.appendEntry("plan-mode", …)` 写进 session 的 custom entry，因此可跨 resume 恢复、可在 TUI widget 里读。
- 证据：`packages/coding-agent/examples/extensions/plan-mode/utils.ts:129-135`
```ts
export function extractTodoItems(message: string): TodoItem[] {
	const items: TodoItem[] = [];
	const headerMatch = message.match(/\*{0,2}Plan:\*{0,2}\s*\n/i);
	if (!headerMatch) return items;
	const planSection = message.slice(message.indexOf(headerMatch[0]) + headerMatch[0].length);
	const numberedPattern = /^\s*(\d+)[.)]\s+\*{0,2}([^*\n]+)/gm;
```
- 证据（持久化）：`plan-mode/index.ts:116-123` —— `persistState()` 用 `pi.appendEntry("plan-mode", { enabled, todos, executing, toolsBeforePlanMode })` 把四个字段写进 session custom entry。
- 判定：**部分覆盖**。可读、可改（`/plan` 切换、`Refine` 重写）、可恢复三点成立；但计划的数据结构只有 `{step, text, completed}`（`utils.ts:103-107`），没有依赖关系、没有阶段目标、没有完成证据字段，协议靠正则从自然语言里"捞"，格式一变就退化为空列表（`extractTodoItems` 返回 `[]` 时 `agent_end` 直接 return，见 `index.ts:294`）。

### 4.2.2 三种控制强度：轻量 Todo / Plan Mode / Planner–Executor

- pi 实现：三种**都存在，但都是示例扩展**，互不复用、互不感知。
  - 轻量 Todo：`examples/extensions/todo.ts` 注册一个 LLM 可调的 `todo` 工具，state 存在 toolResult 的 `details` 里，按分支重建（`todo.ts:114-129`）；`/todos` 命令给用户看（`todo.ts:291-303`）。
  - Plan Mode：`examples/extensions/plan-mode/`，见 4.2.5。
  - Planner–Executor：`subagent` 扩展的 chain 模式 + `agents/planner.md`（只读、输出 "## Plan" 编号步骤）+ `prompts/implement.md`（scout → planner → worker）。
- 证据：`packages/coding-agent/examples/extensions/todo.ts:114-123` —— `reconstructState()` 遍历 `ctx.sessionManager.getBranch()`，只挑 `msg.role === "toolResult" && msg.toolName === "todo"`，从 `msg.details` 复原 `todos`/`nextId`；分支切换时状态自动正确（文件头注释 `todo.ts:8-10`）。
- 证据：`packages/coding-agent/examples/extensions/subagent/agents/planner.md:4-10` —— `tools: read, grep, find, ls` / "You must NOT make any changes. Only read, analyze, and plan."
- 判定：**有但不同**。三档强度齐备，但"强度"不是配置项而是装哪个扩展；没有统一的状态模型，`todo` 工具与 plan-mode 的 `todoItems` 是两套互不相干的数据。

### 4.2.3 计划必须可修订，重规划要说明触发事实、保留已完成项

- pi 实现：`agent_end` 里三选一对话框 "Execute the plan / Stay in plan mode / Refine the plan"；选 Refine 时**不动** `todoItems`，把用户补充当作普通 user message 以 `followUp` 投递；执行阶段用 `[DONE:n]` 标记推进，`turn_end` 逐轮打勾，resume 时只重扫最后一次 `plan-mode-execute` 之后的助手消息来重建完成状态。
- 证据：`plan-mode/index.ts:334-339`
```ts
		} else if (choice === "Refine the plan") {
			const refinement = await ctx.ui.editor("Refine the plan:", "");
			if (refinement?.trim()) {
				pi.sendMessage(planTodoListMessage, { deliverAs: "followUp" });
				pi.sendUserMessage(refinement.trim(), { deliverAs: "followUp" });
			}
		}
```
- 证据（保留已完成项 + 只扫执行段）：`plan-mode/index.ts:365-372`
```ts
		const isResume = planModeEntry !== undefined;
		if (isResume && executionMode && todoItems.length > 0) {
			// Find the index of the last plan-mode-execute entry (marks when current execution started)
			let executeIndex = -1;
			for (let i = entries.length - 1; i >= 0; i--) {
				const entry = entries[i] as { type: string; customType?: string };
				if (entry.customType === "plan-mode-execute") {
					executeIndex = i;
```
- 判定：**部分覆盖**。"保留已完成项"成立（refine 不清空 `todoItems`），"说明触发事实"不成立——没有 replan 记录，没有触发原因字段，`appendEntry` 只存快照 `{enabled,todos,executing,toolsBeforePlanMode}`；修订史只留在对话文本里，状态层看不到"为什么改"。

### 4.2.4 阶段门禁：每阶段有产物 + 进入下一阶段的门禁

- pi 实现（coding-agent）：**没有**阶段/产物/门禁概念。阶段只有"plan mode ↔ execution mode"这一次跳转，产物也没有登记处，进度靠 `[DONE:n]` 文本标记。
- 查询位置：`grep -i 'artifact|completion evidence|approval gate'` 于 `packages/coding-agent/src` 与 `examples`，命中全部无关（`session-share.ts` 的分享 artifact、`package-manager-cli.ts` 的 `fetchInstallerArtifact`、`session-manager.ts:96` 的注释示例），无阶段产物登记。
- pi 实现（durable 内核，另一条线）：`phase` 是 checkpoint 的强制字段，且被投影到任务图节点上。
- 证据：`packages/durable/src/types.ts:390-391` 与 `packages/durable/src/harness/task-graph.ts:293-302`
```ts
export interface Task<I, S extends { phase: string }, R, H extends object> {
	readonly definition: TaskDefinition<I, S, R, H>;
```
```ts
		case "waiting":
			return { status: "waiting", phase: phaseOf(state.checkpoint), on: [...state.on], policy: state.policy };
		case "sleeping":
			return { status: "sleeping", phase: phaseOf(state.checkpoint), until: state.until };
```
- 判定：**缺失（设计取舍）**。durable 有可观测的 `phase`，但 phase 只是断点续跑的定位符，不是"产物 + 门禁"；coding-agent 侧连 phase 都没有——pi 把阶段边界交给会话分支与 compaction，而不是门禁表。

### 4.2.5 探索/计划/执行分离，以及"计划获批前不可写"的四个必要条件

- pi 实现：五件套里 pi 有四件，缺"权限模式"。
  1. 工具白名单：`setActiveTools` 摘掉 `edit`/`write`（`plan-mode/index.ts:104-114`，`extensions/types.ts:1802`）。
  2. bash 白名单：`tool_call` 事件里按 `DESTRUCTIVE_PATTERNS`/`SAFE_PATTERNS` 双向判定，非安全即 `{block:true}`（`utils.ts:97-101`，`index.ts:164-174`）。
  3. 持久状态：`appendEntry("plan-mode", …)` + `session_start` 恢复（`index.ts:344-361`）。
  4. HITL：执行前必须由用户 `ctx.ui.select` 选 "Execute the plan" 才 `restoreNormalModeTools()`（`index.ts:305-319`）。
  5. 权限模式：**没有**。pi 无 permission mode 抽象，安全模型明确写"不对每次 tool call 求批准"。
- 证据：`packages/coding-agent/docs/security.md:3`
```
Treat model-generated commands and code as untrusted. Pi can read, change, and execute files with the permissions of the account that started it, and it does not ask for approval before every tool call.
```
- 证据（门禁唯一入口）：`plan-mode/index.ts:311-317`
```ts
		if (choice?.startsWith("Execute")) {
			const firstTodoItem = todoItems[0];
			if (!firstTodoItem) return;

			planModeEnabled = false;
			executionMode = true;
			restoreNormalModeTools();
```
- 判定：**部分覆盖**，且手册那句关键论断在 pi 上只能部分成立。pi 的"不可写"是**工具注册表级**约束，不是进程级约束：
  - `PLAN_MODE_DISABLED_TOOLS` 只含 `edit`、`write`（`index.ts:24`），`getPlanModeTools` 保留其余所有 active 工具（`index.ts:90-95`）；任何自定义写工具（包括 `subagent`）在 plan mode 下依然可调。
  - `subagent` 子进程用默认工具集启动（`subagent/index.ts:298`），plan mode 的白名单**不传播**给子进程，于是"委派一次就绕过只读门禁"。
  - bash 白名单是启发式正则（`utils.ts:7-95`），能拦 `> file`、`rm`、`git commit`，但不是能力边界。

---

## 4.3 Subagent 与委派

### 4.3.1 何时值得委派：上下文隔离 / 能力隔离 / 并行

- pi 实现：三条价值全部落地，机制很硬：每个子代理是**独立 `pi` 子进程**，`--no-session` 起全新会话，模型与工具逐 agent 可配，并行有并发上限。
- 证据：`packages/coding-agent/examples/extensions/subagent/index.ts:298-305`
```ts
	const args: string[] = ["--mode", "json", "-p", "--no-session"];
	const inheritsDispatchConfig = !agent.model;
	const model = agent.model ?? dispatchDefaults.model;
	if (model) args.push("--model", model);
	if (inheritsDispatchConfig && dispatchDefaults.thinkingLevel) args.push("--thinking", dispatchDefaults.thinkingLevel);
	if (agent.tools && agent.tools.length > 0) args.push("--tools", agent.tools.join(","));
```
- 证据（并行上限）：`subagent/index.ts:34-35` —— `MAX_PARALLEL_TASKS = 8` / `MAX_CONCURRENCY = 4`；调度实现 `mapWithConcurrencyLimit`（`index.ts:217-235`）。
- 判定：**覆盖**。上下文隔离比手册假设的更彻底（进程级，连内存都不共享），代价是每次委派都要付进程启动 + 无缓存前缀。

### 4.3.2 委派契约七项

#### 目标与边界

- pi 实现：目标=task 字符串，边界=cwd 参数（单任务可覆写）+ 该 agent 的 tools 白名单；没有目录级、系统级的范围声明。
- 证据：`subagent/index.ts:440-444` —— `TaskItem` 只有 `agent`、`task`、`cwd` 三个字段，没有范围/边界声明。
- 判定：**部分覆盖**。有目标与工作目录，无"哪些目录/动作在范围内"的结构化边界——边界完全靠 system prompt 自然语言（如 `agents/reviewer.md:10` "Bash is for read-only commands only"）。

#### 已知上下文

- pi 实现：**不 fork 父转录**。子进程只拿到 `--append-system-prompt <临时文件>` + 一行 `Task: <task>`，其余靠调用方把上下文写进 task 文本；chain 模式用 `{previous}` 占位符串接上一步输出。
- 证据：`subagent/index.ts:332-339`
```ts
		if (agent.systemPrompt.trim()) {
			const tmp = await writePromptToTempFile(agent.name, agent.systemPrompt);
			tmpPromptDir = tmp.dir;
			tmpPromptPath = tmp.filePath;
			args.push("--append-system-prompt", tmpPromptPath);
		}
		args.push(`Task: ${task}`);
```
- 判定：**覆盖（强于手册默认）**。手册说"子代理默认不应继承父的全部上下文"，pi 直接做到了不继承；"已确认事实/不可自行改变的决定"没有独立字段，只能塞进 task 或 agent prompt。

#### 能力与权限

- pi 实现：`AgentConfig` 只有 `name/description/tools?/model?/systemPrompt/source/filePath`；权限继承自子进程的操作系统账户，没有降权。
- 证据：`subagent/agents.ts:14-18`（`AgentConfig` 的字段里没有权限项）
```ts
	tools?: string[];
	model?: string;
	systemPrompt: string;
	source: "user" | "project";
	filePath: string;
```
- 判定：**部分覆盖 / 有但不同**。模型与工具可配（能力隔离成立），权限不可配：`tools` 只是"给模型声明哪些工具"，不是 OS 级限制；`agents/worker.md` 不写 `tools` 字段即获得全部默认工具。项目级 agent 是仓库可控的 prompt，因此有信任门（`index.ts:518-546`，非信任项目要 `ctx.ui.confirm`；`README.md:55-65`）。

#### 预算

- pi 实现：**没有**步数/token/时间/费用预算。只有三个硬上限：并行任务数 8、并发 4、单任务回传 50 KB；取消只能靠外部 abort signal（SIGTERM，5 秒后 SIGKILL）。
- 证据：`subagent/index.ts:34-37`
```ts
const MAX_PARALLEL_TASKS = 8;
const MAX_CONCURRENCY = 4;
const COLLAPSED_ITEM_COUNT = 10;
const PER_TASK_OUTPUT_CAP = 50 * 1024;
```
- 证据（无超时，只有取消传播）：`subagent/index.ts:408-414`
```ts
			if (signal) {
				const killProc = () => {
					wasAborted = true;
					proc.kill("SIGTERM");
					setTimeout(() => {
						if (!proc.killed) proc.kill("SIGKILL");
					}, 5000);
```
- 判定：**缺失**。查询位置：`grep -i 'budget|maxSteps|remainingSteps|tokenBudget|deadline'` 于 `packages/durable/src`，命中的 37 处全部是 codemode 输出 token 预算、session 文档 hold deadline 之类，**没有一处是任务级预算**；durable 的 `TaskOptions`（`types.ts:400-421`）也没有预算字段。

#### 输出与证据

- pi 实现：结果=子进程 JSON 流的最后一条 assistant 文本；`details` 里保留完整 `messages`、usage、exitCode、stopReason。没有 schema。
- 证据：`subagent/index.ts:168-178` —— `getFinalOutput()` 从后往前找第一条 `role === "assistant"` 消息的第一个 text block 直接返回，无解析、无校验。
- 判定：**部分覆盖**。证据（原始消息 + usage + 退出码）保留得比手册要求还全；但"结果采用何种结构"没有任何强制——scout/planner/reviewer 的输出格式全写在各自的 markdown system prompt 里（如 `agents/scout.md:23-50`），是提示词约定，不是可校验契约。

#### 失败语义

- pi 实现：定义得很薄。失败判据 `exitCode !== 0 || stopReason === "error" || stopReason === "aborted"`；chain 遇错即停并报告第几步；parallel 跑完全部再汇总 `successCount`。
- 证据：`subagent/index.ts:180-182` —— `isFailedResult` 判据仅 `exitCode !== 0 || stopReason === "error" || stopReason === "aborted"`；`index.ts:585-593` 是 chain 的 FAIL_FAST 分支，遇错即 `return` 并带 `isError: true`。
- 判定：**部分覆盖**。FAIL_FAST（chain）与 BEST_EFFORT（parallel）有，且是硬编码在模式里而非可选策略；**RETRY_OR_REASSIGN 与 ESCALATE 完全缺失**——`grep` 不到重试/改派/升级路径，失败就是以 `isError` 工具结果回到父会话。

#### 验收条件

- pi 实现：**没有显式验收步骤**。父 Agent 拿到的就是一段文本 + details，是否采用由模型自己在下一轮决定。
- 判定：**缺失**。这正是 4.3.5 的问题，见下。

### 4.3.3 Delegation vs Handoff

- pi 实现（Delegation）：`subagent` 是标准的 delegation——父保留责任，结果以工具结果形式回到父会话，父继续整合。证据：`subagent/index.ts:708-711` 返回 `getFinalOutput(...)` 作为 tool content。
- pi 实现（Handoff）：pi 有同名扩展，但**语义不同**。`handoff.ts` 做的是"把上下文提炼成一条 prompt，开一个新 session"，用 `parentSession` 记录血缘，让用户在编辑器里改完再手动提交；没有任务关系、没有责任变更、没有状态转移。
- 证据：`packages/coding-agent/examples/extensions/handoff.ts:177-183`
```ts
			const newSessionResult = await ctx.newSession({
				parentSession: currentSessionFile,
				withSession: async (replacementCtx) => {
					replacementCtx.ui.setEditorText(editedPrompt);
					replacementCtx.ui.notify("Handoff ready. Submit when ready.", "info");
				},
			});
```
- pi 实现（内核侧的血缘记录）：durable 的 `ConversationRecord` 有两个独立边——`parent`（fork 来源 + 到哪一条 entry）和 `owner`（创建者任务，用于归属、子树取消、子树 idle 等待）。这比 handoff 扩展的记录强得多。
- 证据：`packages/durable/src/types.ts:428-438`
```ts
	/** Fork source and inclusive parent entry through which history is inherited. */
	readonly parent?: {
		readonly conversationId: ConversationId;
		readonly at: EntryId;
	};
	/** Creator edge used for attribution, subtree abort, and subtree idle waits. */
	readonly owner?: {
		readonly conversationId: ConversationId;
		readonly taskId: TaskId;
	};
```
- 判定：Delegation **覆盖**；Handoff **有但不同**（名字相同、语义是 context transfer 而非控制权转移）。手册要求的"状态与责任变更记录"在 coding-agent 侧不存在，只在 durable 的 `owner`/`parent` 边里有形式化的雏形。

### 4.3.4 合并结果与失败传播

- pi 实现（extension 层）：chain 是严格串行 + FAIL_FAST；parallel 是"全部跑完再汇总"，把每个子任务的输出截到 50 KB 后拼成 markdown 给父模型；父模型没有机器可读的合并 API。
- 证据：`subagent/index.ts:667-679`
```ts
				const successCount = results.filter((r) => !isFailedResult(r)).length;
				const summaries = results.map((r) => {
					const output = truncateParallelOutput(getResultOutput(r));
					const status = isFailedResult(r)
						? `failed${r.stopReason && r.stopReason !== "end" ? ` (${r.stopReason})` : ""}`
						: "completed";
					return `### [${r.agent}] ${status}\n\n${output}`;
				});
```
- pi 实现（durable 内核，另一条线）：`JoinPolicy = "failFast" | "allSettled"` 是持久化的等待策略；`failFast` 只能等待**自己拥有的**任务（否则拒绝），等待图必须无环，失败会通过 abort 级联给同组其它任务。
- 证据：`packages/durable/src/types.ts:394-398`
```ts
/** Who owns a task: its conversation (a top-level task) or another task of the same conversation (a child task). */
export type TaskOwnership = { readonly kind: "conversation" } | { readonly kind: "task"; readonly taskId: TaskId };

/** How a waiting task treats the tasks it waits on (spec §5.5). */
export type JoinPolicy = "failFast" | "allSettled";
```
- 证据（failFast 的归属限制 + 级联）：`packages/durable/src/harness/scheduler.ts:2515-2516`
```ts
			if (policy === "failFast" && member.owner !== current.id) {
				return { error: new Error(`Task ${current.id} can wait failFast only on tasks it owns; ${id} is not one`) };
```
- 证据（取消向下级联）：`scheduler.ts:1107-1109`
```ts
			for (const { node, live } of this.#walkDown(id, { enter: (below) => !this.#intent.has(below) })) {
				if (live !== undefined && !node.background) mark(live, restart ? "restart" : undefined);
			}
```
- 判定：extension 层 **部分覆盖**（只有两种策略，无 retry/escalate）；durable 内核 **有且更强**（策略持久化、等待图无环校验、取消级联、`allSettled`/`failFast` 语义明确）。
- 手册的"校验输入版本与证据时间"：**缺失**。`subagent` 不校验任何版本/时间戳；durable 的 `version`（`types.ts:714-715`）用于 checkpoint 迁移而非证据新鲜度，`startedAt/endedAt`（`types.ts:732-739`）只是计时。唯一的"固定到某个历史点"的机制是 `ConversationRecord.parent.at`（entry ID），粒度到 entry。

### 4.3.5 子代理产物 = 新的 Observation，需 Schema 校验 + 父验收才进权威状态

- pi 实现：产物确实变成了新的 Observation——它作为 toolResult 消息进入父会话转录，父模型下一轮才看到并决定如何处理。但没有 schema 校验，也没有独立的验收动作。
- 证据：`subagent/index.ts:708-711`
```ts
				return {
					content: [{ type: "text", text: getFinalOutput(result.messages) || "(no output)" }],
					details: makeDetails("single")([result]),
				};
```
- 对照（内核侧的归属）：durable 的每个 entry 有 `byTaskId`，能把一条上下文归因到产生它的任务，这是"产物进权威状态"的形式化基础。
- 证据：`packages/durable/src/types.ts:471-472`
```ts
	/** Task that appended this entry, when it was produced by durable work. */
	readonly byTaskId?: TaskId;
```
- 判定：**部分覆盖**。"是新的 Observation"成立（进程边界 + 工具结果边界）；"Schema 校验"与"父验收"缺失——父模型只能靠读文本自行判断，工具调用本身不带校验环节。`structuredOutput`/`structured-output.ts` 示例提供了结构化输出的机制，但 `subagent` 没用它。

### 4.3.6 多执行者并发写同一工作区：隔离分支 / 对象级锁 / 补丁合并

- pi 实现：parallel 模式下多个子进程共用同一个 `cwd`（`cwd ?? defaultCwd`，`index.ts:345`），**没有** worktree 隔离、没有分支、没有补丁合并、没有跨进程文件锁。
- 唯一的串行化是进程内的按路径变更队列，而且它的注释直接声明不覆盖跨进程场景。
- 证据：`packages/coding-agent/src/core/tools/file-mutation-queue.ts:28-32` —— 注释原文 "Serialize file mutation operations targeting the same file. Operations for different files still run in parallel."
- 证据（durable 版本把边界写得更明确）：`packages/durable/src/tools/file-mutation-queue.ts:28-32`
```ts
 * Serialize `edit` and `write` mutations of one file within this process: same file system id and canonical path,
 * whichever environment object the call got. Other files, and other file systems, never wait. Concurrent calls on one
 * file run in the order their keys resolve. Not a lock against `bash` or other processes.
```
- 判定：**缺失（设计取舍 + 明确缺口）**。既有的是"对象级锁"的进程内近似（`edit`/`write` 走 `withFileMutationQueue`，见 `core/tools/write.ts:67`、`core/tools/edit.ts:163`），但 subagent 是子进程，队列键（模块级 `Map`）不共享；何况 `bash` 完全绕过该队列。相关示例扩展只覆盖周边（`git-checkpoint.ts`、`dirty-repo-guard.ts`、`git-merge-and-resolve.ts`），都不是并行写隔离。

---

## 与手册的根本分歧

1. **默认是否内置**。手册假设 harness 自带 plan/todo/subagent 三档；pi 明确不装（`README.md:19`），只提供可复制的示例。这是取舍：pi 把"任务编排"当成用户可替换的策略层，而不是内核职责。
2. **计划是"文本 + 正则"还是"类型化控制对象"**。手册要阶段目标/依赖/证据；pi 的计划是助手回复里的 `Plan:` 段落（`utils.ts:131`）+ `[DONE:n]` 标记（`utils.ts:154`）。差别不是实现深度，而是**谁是真相源**：pi 让对话转录当真相源，手册让状态对象当真相源。这是取舍，但代价明确——计划格式漂移就得靠 `appendEntry` 快照兜底。
3. **"计划获批前不可写"的边界在哪**。手册要求权限模式 + 工具白名单 + 持久状态 + HITL 共同生效；pi 有白名单 + 状态 + HITL，没有权限模式，且白名单只挡 `edit`/`write` 两个名字（`index.ts:24`）、不传播到子进程。这不是笔误而是架构取向：pi 的信任边界在 OS/容器层（`docs/security.md:3`、`docs/containerization.md`），不在进程内的 permission mode。按手册标准判为**缺口**，按 pi 自己的安全模型判为**取舍**。
4. **父子任务语义住在两个互不连通的包里**。durable 有完整的父子任务（`TaskOwnership`、`wait`/`JoinPolicy`、`failFast`、取消级联、`TaskGraphState`），但 `packages/coding-agent/package.json:43-66` 的 dependencies 里**没有** `@earendil-works/pi-durable` 也没有 `chord`；`pi` CLI 的子代理走的是 `child_process.spawn` 一个 `pi` 子进程（`subagent/index.ts:344`）。所以"pi 内核有没有父子任务"的答案是：**有一个更强的，但 CLI 这个产品没用它**。
5. **委派的隔离方式：进程 vs 任务**。手册的委派契约七项预设"同一个 runtime 里的子任务"；pi 的答案是 OS 进程 + `--no-session`（`index.ts:298`）。上下文隔离因此更强，但预算、验收、合并、并发写全都失去内核支撑——只能靠父子两段自然语言约定。这是取舍的必然代价，不完全是疏忽。
6. **Handoff 的语义**。手册：控制权转移 + 责任变更记录；pi `handoff.ts`：上下文提炼 + 开新会话 + `parentSession` 血缘。同名不同物。真正接近手册 Handoff 的是 durable 的 `ConversationRecord.parent/owner` 双记录（`types.ts:428-438`）。

## 待确认/我没读到的地方

- **两套实现是否会在生产路径上汇合**：我只查了 `packages/coding-agent/package.json` 与各包 dependencies，未见 coding-agent → durable 的依赖；但 `packages/env` 同时依赖 `chord` 和 `pi-durable`，我**没有**读 `packages/env` 的用途，因此不能断言 durable 不被任何 CLI 路径使用。
- `packages/durable/src/harness/scheduler.ts` 共 3158 行，我只精读了 failFast/级联/等待校验三段（约 355-399、1060-1129、2440-2569）与 grep 命中行，其余调度/恢复/持久化细节未读。
- `packages/coding-agent/docs/extensions.md` 我只做了关键词定位（事件表、`setActiveTools`、示例索引第 3307/3315 行），未通读该文件（2300+ 行）。
- `docs/cli.md` 未读，因此 `--no-session`、`--tools`、`--append-system-prompt` 的精确语义（尤其 `--no-session` 是否完全禁用会话持久化、`--tools` 的默认集合是什么）是**从调用点反推**的，未与 CLI 文档交叉验证。
- `git-merge-and-resolve.ts`、`sandbox/`、`dirty-repo-guard.ts`、`git-checkpoint.ts` 四个扩展未打开，只按文件名与 README 索引归类到"周边机制"，未验证它们是否具备并发写隔离能力。
- `packages/agent`（`pi-agent-core`）的循环与工具调度未读，因此"同一会话内是否允许并发工具调用"这一点没有证据，未写进 4.3.6。
- durable 的 `SubmissionRecord`（`types.ts:495` 起）只读到字段开头，未核对其与"任务身份/责任"的关系。

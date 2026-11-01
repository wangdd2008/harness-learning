# 4.4 对照笔记

对照对象：`packages/durable`（下一代的 durable harness）与 `packages/coding-agent`（当前产品形态）。两者**不互相依赖**：`packages/coding-agent/package.json:43-44` 的依赖里没有 `pi-durable`，coding-agent 只依赖 `pi-agent-core`/`pi-ai`。

## A. 结论速览

- **waiting/sleeping 真的释放了"执行",但没有释放"进程"**：这两个状态的任务"Parked without an invocation"（`packages/durable/src/types.ts:673-690`），调度器把它们的候选丢掉（`packages/durable/src/harness/scheduler.ts:2012-2019`）；可是同一进程里 earliest-sleep 的定时器"keeps the process alive"（`scheduler.ts:1786-1801`），要靠宿主 evict + `onWake` 才真正释放算力（`README.md:166`）。
- **没有任务级事件序号/游标**。只有三样东西：commit 级 `Seq`（`types.ts:36-37`、`1117-1127`）、entry 级 `Cursor`（`types.ts:812-822`）、以及 watch 的 `from` 窗口续接（`transcript.ts:88-97`）。RPC/coding-agent 侧也只有 `get_entries { since }` 的 entry id 游标（`packages/coding-agent/src/modes/rpc/rpc-types.ts:65`、`rpc-mode.ts:639-644`）。
- **取消沿所有权树自底向上传播**：abort mark → reconcile 派生子树标记（`scheduler.ts:1102-1110`）→ 子任务 abort handler 先跑、父任务 abort handler 后跑（`docs/spec.md:2442-2450`、`2750-2759`）。background 任务是边界（`spec.md:2467-2474`）。
- **恢复时不会重放"可能已执行"的工具**：intent 先落盘（`tool.ts:194-197`），重跑时只有 `replay: "safe"` 才再跑，否则给模型一条 `interrupted ... may have partially run` 的结果（`tool.ts:200-225`）。没有通用幂等键，幂等靠任务作者自己的 `checkpoint`/`memos`（`spec.md:2284-2299`）。
- **多实例只做到"一个写者 + N 个只读 viewer"**：`README.md:881` 明写 "One process owns a storage at a time; there is no cross-process locking"；`readOnly` 打开的是"a viewer of a session another process drives"（`spec.md:838-845`）。手册 4.4.2 的"任意实例可 resume"在 pi 里是"任意实例可读，写者只能一个"。
- **手册的 Continuation 在 pi 里不存在为统一结构**，被拆成三块：typed checkpoint `S`（任务作者定义，`types.ts:657-690`）、压缩摘要**文本**（`packages/durable/src/harness/compaction.ts:76-107`）、扩展自定义 document（`test/examples/26-plan-mode.ts:29-37` 的 `app.plan`）。
- **手册的 WAITING_INPUT / WAITING_APPROVAL / VERIFYING 没有对应状态**：`TaskState` 只有 pending/running/waiting/sleeping/completing/terminal（`types.ts:657-702`），`waiting` 只等 `TaskId[]`（`types.ts:677`）；审批是 hook 直接 `{ block }`（`spec.md:3220-3222`），等于让这次调用失败，而不是挂起后恢复。
- **coding-agent 的"续行"是会话文件重放，不是任务续行**：JSONL append（`session-manager.ts:1172-1189`）+ 打开时重建 context（`session-manager.ts:1776-1796`），没有 run/task 记录；崩溃在途的工具调用没有 intent 记录可对账。

## B. 逐条对照

### 4.4.1-a 任务身份与连接解耦：提交拿稳定 ID，可消费可断开，等待时释放算力，条件满足后从权威状态恢复

- pi 实现：`submit()` 立即返回持久化的 `Submission`（`id` / `status()` / `wait()`），等待只是调用方持有一个 promise；`harness.submission(id)` 可在重启后重新接管同一个提交。
- 证据：`packages/durable/src/types.ts:121-124`
```ts
export interface Submission {
	readonly id: SubmissionId;
	status(context: Context): Promise<SubmissionRecord>;
	wait(context: Context): Promise<SettledSubmissionRecord>;
```
- 证据：`packages/durable/src/types.ts:897-898`（"Reacquire a submission, for example after reopen"）。
- 恢复靠调度器重启时把 `running` 改回 `pending`，**并给 restart 计数 +1**：`packages/durable/src/harness/scheduler.ts:452-457`
```ts
if (record.state.status === "running") {
	const restarts = (record.restarts ?? 0) + 1;
	const pending = withState(record, { status: "pending", checkpoint: record.state.checkpoint });
	tx.setTask({ ...pending, restarts } as AnyTaskRecord);
}
```
- 判定：**覆盖**（身份/断连/恢复）；"释放计算资源"见 A 第 1 条，是部分覆盖。

### 4.4.1-b 后台任务/事件/恢复共用的契约（9 个字段）

- pi 实现：契约不是一件 record，而是 `TaskRecord` + `TaskState` + `SubmissionRecord` + commit `Seq` 拼出来的。逐项：

| 手册字段 | pi 的落点 | 判定 |
|---|---|---|
| 稳定任务 ID | `TaskRecord.id`（`types.ts:710`），`TaskId<R>` 带结果类型 | 覆盖 |
| 父任务 ID | `TaskRecord.owner?: TaskId` + `conversationId`（`types.ts:711-719`）；owner 边不可变（`spec.md:2671-2677`） | 覆盖 |
| 当前状态 | `TaskState` 六态（`types.ts:657-702`） | 部分：缺 PAUSED/WAITING_INPUT/APPROVAL/VERIFYING |
| 创建者与执行者 | 只有 entry 上的 `byTaskId`（`types.ts:471-472`）和遥测 carrier（`types.ts:706-709`）；没有 creator/executor 字段 | 缺失（设计取舍：owner + trace 足够） |
| 输入与 Artifact 引用 | `input: I` 永久保留（`types.ts:716-717`）；大结果"put large results in entries and retain only their IDs"（`spec.md:6471-6473`） | 部分：Artifact 是约定不是字段 |
| 事件序号 | 无任务级序号；只有 commit `Seq`（`types.ts:36-37`）和 `observeCommits()`（`types.ts:1117-1127`） | 部分 |
| 超时 | `TaskRecord`/`TaskState` 里没有 deadline 字段；超时只在工具内（`src/tools/bash.ts:55-61`）和 `settings.stream.timeoutMs`（`src/harness/types.ts:538`）；sleep 明确"cannot be woken early except by an abort"（`spec.md:2799`） | 缺失（有意：只用 abort） |
| 取消与幂等 | `abortRequested`/`abortReason`（`types.ts:722-729`）+ memos first-writer-wins（`types.ts:757-758`）+ `requestId` 去重（`types.ts:501-502`）+ `replay` 策略（`tool.ts:195`） | 覆盖 |
| 结果位置 | 终态记录本身就是 receipt（`types.ts:697-702`，`spec.md:2390-2408`） | 覆盖 |
| 错误分类 | `TaskOutcome` 五态 completed/failed/aborted/orphaned/faulted（`types.ts:620-655`）+ `ReportInfo` 十种 kind（`types.ts:171-201`） | 覆盖 |
| 恢复所需的 Continuation | checkpoint `S` 是"complete durable state from which execution resumes"（`types.ts:662-663`），每次 commit 整体替换（`spec.md:2258-2259`） | 部分：有容器，无约定字段 |

- 判定：**部分覆盖**。pi 的契约是"每类记录各管一段"，手册要求的是"一套可机读 schema 贯穿后台任务/事件/恢复"。

### 4.4.1-c 暂停前：停止新行动、处理可中断操作、保存最新状态；恢复时重新检查目标/外部条件/工具是否执行过/权限/工作区/预算

- 暂停前，pi 用"durable abort mark 一旦提交，run invocation 就不能再写"来实现"停止创建新行动"：`packages/durable/docs/spec.md:2452-2461`
```
A run invocation may not commit after its durable abort mark appears.
Every runtime operation rejects after its owning invocation ends ...
Cancelling one caller's `Context` only cancels that call or wait;
```
- 保存最新状态：checkpoint 是整体替换，"each durable checkpoint is a full replacement"（`spec.md:2257-2259`）；terminal 转换在同一次 commit 里写 task 记录 + result entry + retire 文档（`spec.md:2399-2404`）。
- 恢复时"工具是否真的执行过"：这是 pi 做得最实的一条。intent 先提交，恢复时按策略二选一：
```ts
const intent = { phase: "execute", arguments: final, replay: tool.replay ?? "unsafe" } as const;
return { status: "running", checkpoint: intent };
```
（`packages/durable/src/harness/tool.ts:194-197`）
```ts
if (replay === "safe" && tool?.replay === "safe") { ... return run(...); }
const message = `Tool ${call.name} was interrupted and may have partially run`;
```
（`packages/durable/src/harness/tool.ts:207-221`）
- 恢复时"权限是否仍有效 / 工具是否还有"：每 phase 重新解析 agent 与 registry 快照（`types.ts:269-272`、`spec.md:3201-3207`），工具不在就给 `tool_unavailable` 结果（`tool.ts:232-233`）。
- 恢复时"工作区是否变化"：环境**每次使用**重建，cwd 取当前值（`README.md:402`）；spec 把这点列为 footgun："a tool rerun after recovery builds its environment again, with the conversation's current `cwd`, which may differ from the first attempt's"（`spec.md:6493-6495`）。
- 恢复时"剩余预算"：只有"被中断次数"（`restarts`，`types.ts:740-746`）和每 run 的 `maxTurns`（`README.md:404`）；没有 token/费用/时长预算字段。
- 恢复时"目标 / 外部条件"：**没有重新检查**。checkpoint 对 Harness 是不透明的 `S`，Harness 不知道目标是什么，也不去探外部世界；重跑 phase 完全靠任务作者在 handler 里自己查（`spec.md:2372-2383` 的 effect sandwich 只规定顺序，不规定复查内容）。
- "处理可中断操作"在 pi 里被拆成 close 与 crash 两种：close 会 signal 并 join 所有 invocation，然后把任务写回 `pending` **不计数**（`scheduler.ts:568-583`，"A close is not a crash"）；只有进程死掉/evict/reset 才留下 `running` 记录并计数（`spec.md:2530-2537`）。close 也不写 outcome、不 terminalize（`spec.md:2359-2366`）。
- 判定：**部分覆盖**。工具执行状态、权限/工具集、工作区三项覆盖得很好；目标/外部条件/预算是留给任务作者的。

### 4.4.1-d 取消沿父子任务传播；已发生的外部副作用不能假装消失，要保留事实并必要时补偿

- pi 实现：取消是"派生标记"而不是"递归调用"。取消意图是"a live owner's own record: its abort mark, or a held non-`completed` outcome"（`spec.md:2492-2494`），reconcile 每轮从意图节点向下走一遍：
```ts
for (const id of this.#intent) {
	const owner = this.#liveRecord(id)!;
	const restart = owner.abortReason === "restart" && !failedOutcome(owner);
	for (const { node, live } of this.#walkDown(id, { enter: (below) => !this.#intent.has(below) })) {
		if (live !== undefined && !node.background) mark(live, restart ? "restart" : undefined);
	}
}
```
（`packages/durable/src/harness/scheduler.ts:1103-1110`）
- 为什么是"每轮重算"而不是"一次传播"：崩溃会丢掉在途的传播，"The scheduler derives the marks in a later reconcile commit, and again at open, so a crash in between loses nothing"（`spec.md:2499-2501`）。
- 顺序是自底向上：abort invocation 只有在自己的 ordinary owned work 都不 live 之后才开始（`spec.md:2442-2450`、`2750-2752`）；调度器里对应 `#waitingOn()` 对 abort-marked 任务返回 owned live（`scheduler.ts:2034-2036`）。
- 副作用不消失：non-replay-safe 工具给的是"interrupted and may have partially run"（`tool.ts:221`）；没有定义可跑的取消是 `orphaned` 而不是 `aborted`，spec 直接写明理由："`orphaned` means no task code ran, so external effects the task started may remain uncleaned"（`spec.md:2592-2597`）。
- 补偿：abort handler 就是补偿点，但"an abort handler cannot create owned children, because its task is abort-marked"，只能内联补偿或用 background 任务（`spec.md:6400-6405`）。
- 判定：**覆盖**，且比手册更狠：连"补偿失败"都有终点（`restartLimit` 后 faulted，`README.md:216`）。

### 4.4.1-e Context Reset 只负责控制语义；Continuation 应含目标/Plan/事实/失败尝试/Artifact/等待项/预算/权限模式

- pi 实现：reset 是一次 **write submission**，写一条 `head: "self"` 的 `pi.reset` entry，handoff 文本作为 user message；旧 context 只是"看不见"，entry 仍在存储里。
- 证据：`packages/durable/docs/spec.md:1071-1074`
```
`reset()` durably admits a write submission of a `pi.reset` entry
with `head: "self"`, carrying the handoff text as a user message when given,
and then resolves; while busy, placement follows section 6 and may occur later.
```
- handoff 文本来自工具：`control: { handoff: "..." }` 写同样的 reset，但 run 继续（`README.md:604`）。所以"一致继续点"由**调用方给的字符串**保证，Harness 不校验里面有什么。
- 另一条 reset 路径是压缩：`pi.compaction` entry 带 `head`（第一个保留的 entry），摘要 prompt 要求固定小节 Goal / Constraints / Progress(Done/In Progress/Blocked) / Key Decisions / Next Steps / Critical Context（`packages/durable/src/harness/compaction.ts:76-107`）。这实际上覆盖了手册 Continuation 里的"目标/Plan/失败尝试"三项，但是**自然语言**。
- 权限模式与剩余预算不在 reset/摘要里：权限是 agent 的 `tools`/`modelTools` 与 hooks（`README.md:380-404`、`spec.md:3220-3222`），预算只有 `maxTurns` 与 `pi.usage`（`src/harness/live.ts:143-144`）。
- 判定：**部分覆盖**。"旧窗口形成一致继续点"覆盖（head 标记 + 不可变 entry）；"新窗口从权威状态重建任务视图"只覆盖到模型上下文（`context.ts:339-348` 从 head 起重建并补 tool result），不覆盖任务视图；Continuation 的 8 个字段里没有一个是 Harness 定义的。

### 4.4.2 成熟 Harness 嵌入企业服务：SDK 提交任务 + 限制工具 + 消费事件；多实例下 Session 存共享存储、用 session_id resume、任意实例可读

- pi 实现（SDK 侧）：`createAgentSession()` 返回进程内 `AgentSession`，`prompt()` 解析为"run 结束"，`subscribe()` 消费事件，工具集通过 `tools`/`noTools`/`excludeTools` 限制（`packages/coding-agent/docs/sdk.md:8-20`、`72-94`、`96-107`）。
- "限制工具"在 durable 侧是两层：`tools` 决定启用哪些，`modelTools` 只在其中挑选"给模型看哪些"，`callers: ["model"|"tools"]` 再按调用方收窄（`README.md:335-347`）；per-conversation 落盘在 `pi.agent`（`README.md:384-398`）。
- 事件流没有序号：RPC/JSON 事件是"session event"流，客户端靠 `message_end`/`agent_settled` 判定边界（`packages/coding-agent/docs/json.md:31-48`），断线后重新 `get_entries` 拿 entry id `since` 游标（`rpc-types.ts:65`、`rpc-mode.ts:639-644`）。
- pi 实现（durable 侧）：`Harness.open(storage)` + `submit()` + `watch()`；多进程只支持"一个写者、多个只读 viewer"：
```ts
/**
 * `HarnessOptions.readOnly` opens a viewer of a session another process drives,
 * such as a synced copy on a device that only shows it.
 */
```
（`packages/durable/docs/spec.md:838-841`）
- 共享存储的边界在 README 里说死了：`packages/durable/README.md:881`
```
One process owns a storage at a time; there is no cross-process locking.
```
- JSONL 后端只有单写者追加协议（append sidecar → append main marker，`spec.md:6302-6310`），没有跨进程锁；SQLite 后端是 WAL，但同样假定一个 Session 一条 mutation line（`spec.md:6269-6281`）。
- "Session 存共享存储、任意实例可读"：**部分覆盖**。"任意实例可读"成立（readOnly viewer + SQLite/JSONL 共享文件）；"任意实例可 resume"只在"前一个实例已死"的意义上成立——两个活实例同时非 readOnly 打开同一 storage 时，后开的会把自己看到的 `running` 任务计为 crash 并改回 `pending`（`scheduler.ts:452-457`），没有 lease/fencing 保护。
- 判定：**部分覆盖**。SDK 嵌入这一段基本对应（只是没有 `session_id` 参数，durable 用 `Harness.open` + 存储路径/前缀）；"多实例共享 Session"是明确的非目标方向。

### 4.4.3 平台承载长任务（Agent / Environment / Session / Event 四对象）

- pi 实现：durable 的对象是 Session / Conversation / Task / Document / Submission（`types.ts:50-63`、`README.md:92-104`），加上可注入的 `env`（每次调用构建 `ExecutionEnv`，`README.md:430-444`）。没有"Agent"对象（agent 是 conversation 的 `pi.agent` 文档，`README.md:380-402`），也没有独立"Event"对象（事件是 commit 的派生观察，`types.ts:1096-1124`）。
- 托管形态是宿主自己写：Cloudflare Durable Object 的 `alarm()` + `onWake` + `resume()` 示例（`README.md:166-210`），以及 `wake()` 的 `{ active, at }`（`scheduler.ts:514-531`）。
- 判定：**设计取舍**。pi 把"平台"降级为两个宿主回调（`setTimer` / `onWake`）+ 一个 `wake()`，而不是四个对象。

## C. pi 的两套东西：coding-agent 的 session 续行 vs durable 的任务续行

- **谁在用谁**：互不依赖。coding-agent 依赖 `pi-agent-core` + `pi-ai`（`packages/coding-agent/package.json:43-44`）；durable 依赖 `pi-ai` + `chord`，自带一套 `CodingTools`（`packages/durable/src/tools/index.ts`）。共享的是模型访问层（pi-ai）和工具语义，不共享持久化内核。
- **coding-agent 的续行**：存储 = 一个 append-only JSONL，每行一条 entry（`session-manager.ts:1172-1189`）；续行 = `SessionManager.open()` 重新加载文件、按 leaf 走父链重建 context（`session-manager.ts:1776-1796`、`session-format.md:224-248`）。它**没有** run 记录、没有 task 记录、没有 checkpoint、没有崩溃计数。进程在工具中途死掉，文件里留下的就是半截对话；下次 prompt 只是继续往树上追加。恢复语义全靠"entry 不可变 + 分支可选"。
- **durable 的任务续行**：存储 = Session（entries + task 记录 + documents + submissions 一次原子提交，`spec.md:42-46`）；续行 = `open()` 把 `running` 改 `pending` 并计数（`scheduler.ts:452-457`），`resume()` 启动调度（`scheduler.ts:475-480`），phase 从 checkpoint 顶部重跑（`spec.md:2782-2795`）。
- **缺什么**：
  - coding-agent 缺"任务"这一层：没有父任务、没有 waiting/sleeping、没有取消传播（`abort()` 只 abort 当前 agent run 与后台 retry/compaction/bash，`agent-session.ts:2519-2529`）。
  - durable 缺"产品化的会话语义"：没有 `--resume` 选择器、没有 tree/fork UI、没有 compaction 的 branch summary；compact 是任务（`spec.md:1066-1071`）。
  - 两者都缺手册要求的"任务事件流 + 游标"：一个只有 entry id，一个只有 commit `Seq`。
- 一句话：**coding-agent 的续行是"把聊天记录再读一遍"，durable 的续行是"把状态机从 checkpoint 再跑一遍"**。手册 4.4 讲的是后者，但要求的事件/契约/多实例是两者都没做的部分。

## D. 与手册根本分歧

1. **"权威状态"的位置不同**。手册要求一份跨任务可读的机读状态（目标/阶段/Plan/事实/阻塞/Artifact/预算）；pi 的权威状态是"不可变 entries + 每任务的 opaque checkpoint + 扩展自己的 document"。`pi.live` 明确只是 "Run control and presentation"（`live.ts:158`），`pi.agent` 只是配置（`README.md:380-402`）。pi 的答案是"状态归任务作者"，手册的答案是"状态归 Harness"。
2. **等待不是一种业务状态，只是两种排队**。手册有 WAITING_INPUT / WAITING_APPROVAL / WAITING_EVENT / PAUSED / VERIFYING；pi 只有 `waiting`（等 TaskId）和 `sleeping`（等时钟）。等外部系统必须写成"轮询任务"或"sleep + 查"，等审批只能 block 掉这次调用（`spec.md:3220-3222`）。这是更小、更可判定的状态机，但表达力确实弱。
3. **恢复不复查目标，只复查可执行性**。pi 恢复时会重建 registry/agent/env、按 replay 策略决定工具是否重跑、按 `restarts` 判断是否该放弃；它不会去问"目标还成立吗、外部条件变了吗、预算还剩多少"。手册把这几项列为恢复必检，pi 把它们留给任务作者。
4. **取消是"标记 + 派生"，不是"调用链"**。pi 不在取消时同步递归调用子任务的 abort，而是提交标记、由 reconcile 每轮重算、由调度器保证顺序。好处是崩溃不丢标记（`spec.md:2497-2501`）；代价是取消的可见延迟与"多一次 commit"。
5. **多实例是"读扩散、写单点"**。手册 4.4.2 的"任意实例 resume"在 pi 里被明确否掉（`README.md:881`）；pi 用 `readOnly` viewer 换来了"另一台设备能看"，没有换"另一台机器能接管"。

## E. 待确认

- `Seq` 是否被任何宿主当作游标用过：只在 `observeCommits()`（`types.ts:1117-1127`）和 `CommitPublication`（`types.ts:977-980`）出现，仓库内没找到把 `seq` 传给客户端的适配层；不确定是否在其它仓库/宿主里承担了事件游标角色。
- 两个非 readOnly 实例同时打开同一 storage 的实际后果：代码上第二个 `open()` 会把 `running` 计数为 crash（`scheduler.ts:452-457`），但没有测试或文档描述这种并发；"会不会互相踩"未验证。
- SQLite WAL 下第二个进程**只读**打开的并发安全性：`spec.md:838-845` 说 readOnly 可以，`README.md:881` 说 no cross-process locking；两者不矛盾（一个写者），但并发读的隔离级别没有文档承诺，未验证。
- `Submission.wait()` 在被等待期间是否持有额外资源：`wait()` 只是 promise（`types.ts:124`），但 `Submissions` 是否在内存里留 waiter 索引未逐行确认（`src/harness/submissions.ts` 未通读）。
- coding-agent 崩溃在途的工具调用，恢复后给模型看的是什么：`orderToolResults()` 会合成缺失结果（`durable/src/harness/context.ts:344-348`），但 coding-agent 侧没有对应逻辑；我在 `packages/coding-agent/src` 与 `packages/agent/src` grep `unmatched|dangling|orphanedTool|without result` 只命中测试注释，未找到合成路径。需要跑一次真实崩溃复现才能定论。
- 手册 4.4.1 的"event cursor"具体粒度（按事件还是按任务）不明确，因此"pi 缺"的判定按"任务级事件序号"理解；若手册指 entry 级游标，则 pi 的 `ConversationTranscript.resume`（`transcript.ts:88-97`）已覆盖。

## F. 五个具体问题的直接回答

**1) durable 有没有真正"释放计算资源"？waiting 时还有没有 invocation / 循环在跑？**

- 任务层：没有 invocation。`waiting` 的定义就是 "Parked **without an invocation**"（`packages/durable/src/types.ts:674-675`），`sleeping` 同（`types.ts:681-688`）；reservation 候选会把它们丢掉，注释也写明 "a sleep at the first pass after its time comes"（`scheduler.ts:2010-2019`）。
- 进程层：还在。没有 `onWake` 时，earliest-sleep 的 foreground 定时器 "keeps the process alive, unlike the context expiry timer"（`scheduler.ts:1787-1789`）；`wake()` 的 `active` 只要"有任务现在能跑或正在跑"就为真（`spec.md:2819-2831`）。
- 内存层：不释放。调度器在 `#live` 里"mirrors every committed non-terminal task record"（`scheduler.ts:259-263`），waiting/sleeping 也在内。
- 结论：**释放了"执行"，没有释放"进程与内存"**；真正的算力释放要宿主 evict（Durable Object `alarm()`，`README.md:166-210`）。

**2) 事件有没有序号 / 游标？**

- 有 commit 级：`Seq` 是"Strictly increasing sequence assigned to one atomic storage commit; gaps are permitted"（`types.ts:36-37`），通过 `CommitObserver`/`CommitPublication{seq, changes}` 暴露（`types.ts:1117-1127`、`977-980`）。
- 有 entry 级：`Cursor` 只是"opaque continuation state"（`types.ts:812-822`），客户端续接用 `ConversationTranscript.resume` 给出的 `{ from }`（`transcript.ts:88-97`），并显式承认 entry id "has holes"（`transcript.ts:42-45`）。
- 没有"任务事件流 + 序号"：`TaskRecord` 无 `seq`/`version` 之外的进度号（`types.ts:704-747`），coding-agent 的 JSON/RPC 事件也没有 seq 字段（`json.md:31-48`）。
- 结论：**部分覆盖**。游标是存储层的（commit / entry），不是任务层的（"这个任务的第 N 个事件"）。

**3) 取消如何沿父子传播？**

- 协议四步：commit `abortRequested` → signal/join 当前 run invocation → 等 ordinary owned work 不再 live → 起一个新的 abort invocation 跑 abort handler（`spec.md:2442-2450`）。
- 传播不是递归调用，而是每轮 reconcile 从"意图所有者"向下走，跳过 background 节点（`scheduler.ts:1103-1110`）；意图 = abort mark 或 held 的 non-`completed` outcome（`spec.md:2492-2494`）。
- 顺序自底向上：abort 只在自己的 owned work 都不 live 之后才开始（`spec.md:2750-2752`），调度器用 `#waitingOn()` 的 `abortRequested` 分支实现（`scheduler.ts:2034-2036`）。
- 崩溃安全：标记是推导出来的，"and again at open, so a crash in between loses nothing"（`spec.md:2499-2501`）。
- 结论：**覆盖**，粒度到 background 边界（`spec.md:2467-2474`）。

**4) 恢复时会不会重复副作用？有没有幂等键 / 执行记录？**

- 有"执行记录"：工具执行前的 intent（arguments + replay 策略）是一个 durable checkpoint（`tool.ts:194-197`）。
- 没有通用幂等键，只有**重放策略**：重跑时 `replay === "safe" && tool?.replay === "safe"` 才再跑，否则写一条 `interrupted ... may have partially run` 的结果给模型（`tool.ts:207-225`）。
- 幂等的其它工具：`memo()` 是 first-writer-wins（`types.ts:757-758`）；提交层用 `requestId` 去重（`types.ts:501-502`，`spec.md:2928-2929`）；任务作者用 "idempotent by key" 的 charge 模式（`spec.md:2284-2299`）。
- 结论：**部分覆盖**。pi 不保证 exactly-once，它保证"不假装成功"（interrupted 结果 + orphaned 的语义，`spec.md:2592-2597`），把幂等推给任务作者。

**5) 多实例共享存储做到了吗？**

- 做到"一个写者 + N 个只读"：`readOnly` = "a viewer of a session another process drives"（`spec.md:838-845`）。
- 没做到"多写者"：`README.md:881` "One process owns a storage at a time; there is no cross-process locking"；JSONL 只有单写者追加协议（`spec.md:6302-6310`）；多写合并被列为非目标 "CRDT/offline multi-writer merge"（`spec.md:6527`）。
- 危险点：第二个非 readOnly 实例 `open()` 时会把看到的 `running` 当成 crash 并 `restarts + 1` 改回 `pending`（`scheduler.ts:452-457`），没有 lease/fencing。
- 结论：**部分覆盖**（读共享覆盖，写共享缺失，且是明示的设计取舍）。

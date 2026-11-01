# 09 SDK 与集成

> 本页覆盖：SDK 进程内集成（sdk）、CLI 集成模式（cli-integration）、RPC 协议（rpc/rpc-commands/rpc-extension-ui）、JSON 事件流（json）、codemode 脚本工具（codemode）。Pi 的对外集成层基本都在这里。

## sdk.md — SDK（进程内集成）

> 原文存档：[source/sdk.md](source/sdk.md)

`@earendil-works/pi-coding-agent` 把 Pi 嵌入 Node.js/Bun 进程，提供对 agent/会话/工具/模型/资源的直接 TypeScript 访问。**进程内 TS 集成用 SDK；跨语言或隔离子进程用 CLI 集成（RPC）。**

```typescript
import { createAgentSession } from "@earendil-works/pi-coding-agent";

const { session } = await createAgentSession();
try {
  await session.prompt("What files are in the current directory?");
  console.log(session.getLastAssistantText());
} finally {
  session.dispose();
}
```

默认使用工作目录、发现的资源、存储设置与配置的凭据；`prompt()` 在 run 完成时 resolve（含自动重试）。

### 会话生命周期

- `createAgentSession()` 建 `AgentSession`：一个会话拥有对话、模型与工具、排队消息、压缩状态、扩展运行时。读状态：`session.messages` / `session.model` / `session.thinkingLevel` / `session.systemPrompt` / `session.getActiveToolNames()`。
- **会话默认持久化**。`SessionManager` 拥有持久/内存条目树与活动叶子；重建模型上下文时选活动分支并应用压缩。**`SessionManager` 是最终模型上下文的权威**——`session.agent.state.messages` 赋值不能替代持久化上下文；外部历史用带条目的 manager 构造会话。
- 不要会话文件：`createAgentSession({ sessionManager: SessionManager.inMemory() })`。
- `cwd` 显式传（区别于 `process.cwd()`）；`session.dispose()` 中止活动工作、失效扩展上下文、断开 agent。
- `AgentSessionRuntime`（createAgentSession 返回的 runtime）加 `newSession()` / `switchSession()` / `fork()` / `importFromJsonl()`——每次替换活动 AgentSession 并为目标工作目录重建服务；**runtime 替换后订阅要重新绑定**。

### Prompting 与事件

- `prompt()` 处理扩展命令并展开文件提示模板；流式中必须指明 steer（当前 assistant turn 工具跑完后插入）或 followUp（run 完成 pending 工作后），否则拒绝。`steer()` / `followUp()` 直接暴露两种行为，返回 `"queued"` 或 `"handled"`。
- `abort()` 中止并等空闲；`waitForIdle()` 只等待。
- `session.subscribe((event) => ...)` 流式订阅：`message_end` 是权威完成消息；`agent_end` 只是低层 run 结束（后面还可能有自动恢复/排队工作）；**`agent_settled` 才表示 Pi 不会自动继续**。

### 配置会话

无覆盖时工厂创建 ModelRuntime + 文件 SettingsManager + 持久 SessionManager + DefaultResourceLoader + 默认工具。各边界可显式注入：`modelRuntime/model/thinkingLevel/scopedModels`、`settingsManager`、`sessionManager`、`resourceLoader`、`tools/noTools/excludeTools/customTools`。

- **Inline extensions**：经 `DefaultResourceLoader.extensionFactories` 提供工厂；`InlineExtension` 名仅用于诊断稳定名；`builtin: true` 的命名条目不是内联扩展，而是提供 `builtin:<name>` 扩展代码（默认加载、可 `-builtin:<name>` 禁用）。CLI 的 codemode/tool_search/MCP 内置扩展即如此。
- **Codemode 与 MCP**：SDK 会话**不加载内置扩展**——需手动把 `createCodemodeExtension()`、`createToolSearchExtension()`、`createMcpExtension()` 加进 `extensionFactories`；codemode/tool_search 注册为不活跃，经 `defaultTools: ["+codemode", "+tool_search"]` 或 MCP 扩展自动激活；MCP 扩展在 `session_start` 连服务器，所以要先 `session.bindExtensions()`。

### SDK 示例清单（原文全表）

01-minimal（最小）、02-custom-model、03-custom-prompt、04-skills、05-tools、06-extensions、07-context-files、08-prompt-templates、09-api-keys-and-oauth、10-settings、11-sessions、12-full-control、13-session-runtime、14-codemode-mcp。

## cli-integration.md — CLI 集成模式

> 原文存档：[source/cli-integration.md](source/cli-integration.md)

默认 `pi` 打开交互 TUI；输入/输出被管道化时自动转 print 模式。四种模式共用同一 agent/会话/资源/工具，区别在输入进入方式、输出暴露方式、进程存活时间。**SDK 不是 CLI 模式**（进程内嵌入）。

| 模式 | 界面 | 生命周期 | 何时用 |
| --- | --- | --- | --- |
| 交互 Interactive | 终端 UI | 直到用户退出 | 人直接使用 |
| Print | stdout 最终文本 | 单次调用 | 脚本只要最终回复 |
| JSON | stdout JSONL 事件 | 单次调用 | 进程要一次 run 的结构化进度 |
| RPC | stdin 命令 + stdout 响应/事件 | 长驻 | 进程需要双向控制 |

- **Print**：`pi --print "..."`，只出最终文本；错误写 stderr；`error`/`aborted` stop reason 非零退出；`length`（输出截断）仍打印部分文本+stderr 警告+非零退出。非 TTY 的 stdin/stdout 自动选 print。
- **JSON**：`pi --mode json "..." > events.jsonl`，会话头 + agent/会话事件，跑完即退（不收后续命令）。失败/中止在事件流里出现但**不**因此非零退出。`message_update` 是**增量 delta**，用 `message_end` 的权威消息替换组装结果；`agent_settled` 标志本次 run 自动工作结束。stdout 只留 JSONL，诊断/日志走 stderr。
- **RPC**：`pi --mode rpc --no-session` 长驻；stdin 每行一个命令 JSON，stdout 每行响应/事件。加 `id` 关联命令（响应复读该 id；`bash_execution_update` 例外）。`prompt` 成功只表示已接受/排队/处理——**完成要看 `agent_settled`**。扩展对话框是请求-响应子协议；其余扩展 UI 更新是通知可忽略。TS 集成优先用 `RpcClient`（起子进程、关联请求、类型化命令、事件投递）；`RpcClient.promptAndWait()` 先装监听再发 prompt 避免竞态。
- **Fork/rebrand**：`package.json` 的 `piConfig: { name, configDir }` 改 CLI 名与配置目录（影响横幅、配置路径、派生环境变量名）；`bin` 改可执行名。

## rpc.md — RPC 协议

> 原文存档：[source/rpc.md](source/rpc.md)

长驻子进程集成（跨语言/隔离/IDE/自定义 UI）。SDK 进程内、RpcClient 子进程 TS，都是更优选择。

- **启动**：`pi --mode rpc --no-session`（其余 CLI 选项照常）；拒绝 `@file` prompt 参数。
- **四类记录**：stdin Command；stdout `response`（成败+数据）；stdout 会话事件（run/消息/工具/队列/压缩/重试）；双向扩展 UI 记录。
- **关联**：命令可选 `id`，响应复读；命令处理异步，按 id 而非顺序关联。会话事件一般无命令 id。
- **Framing**：**严格 JSONL**——每行一个完整 JSON 对象、LF 结尾、只在 LF 切分、可剥可选前置 CR。不要用通用行读取器（Node `readline` 会把 JSON 字符串内合法的 U+2028/U+2029 当分隔符）。持续读 stdout（不读会反压卡进程）；stdout 只留协议记录，诊断走 stderr。
- **生命周期**：`prompt` 响应后继续消费事件；`data.disposition`：`"handled"`（无 run 开始，别等 agent_settled）/ `"queued"` / `"started"`。`agent_end` 后有重试/溢出恢复/压缩/steer/followUp；**等 `agent_settled`**。先订阅再发 prompt（RpcClient.promptAndWait 内部已做）。
- **错误**：命令失败 → 一个 `success: false` response；畸形 JSON → 无请求 id 的 `parse` 响应；成功响应只覆盖命令处理，提供方失败/中止出现在消息与事件流。客户端还要处理子进程启动失败、意外退出、stderr 诊断、取消与自己的超时。
- **关闭**：关子进程 stdin 请求有序关闭（Pi 先 dispose 活动 runtime 再退出）；扩展也可请求关闭。

## json.md — JSON 事件流

> 原文存档：[source/json.md](source/json.md)

JSON/RPC 模式共享的事件规范（严格 JSONL，规则同 rpc）。首条记录是会话头（`{"type":"session","version":3,...}`；RPC 无此头，用 `get_state`）。

**基本 run 序列**：`agent_start` → `turn_start` → `message_start`（user）→ `message_end` → `message_start`（assistant）→ `message_update`（增量）→ `message_end`（权威）→ `turn_end`（含 toolResults）→ `agent_end`（messages/willRetry）→ `agent_settled`（aborted）。

**消息事件**：`message_start` / `message_update`（usage + assistantMessageEvent）/ `message_end`（权威完成消息）。增量事件类型：`start` / `text_start/text_delta/text_end` / `thinking_start/thinking_delta/thinking_end` / `toolcall_start/toolcall_delta/toolcall_end` / `done`（reason/message）/ `error`。用 `contentIndex` 定位块；组装 delta 做实时显示，完成后用 `text_end`/`thinking_end`/`toolcall_end` 的内容替换，最终整条用 `message_end.message` 替换。顶层 `usage` 是最新累计值（流式中可能到完成才非零）。

**工具事件**：`tool_execution_start`（toolCallId/toolName/args）/ `tool_execution_update`（partialResult）/ `tool_execution_end`（result/isError/durationMs）；用 toolCallId 关联生命周期。

**队列与状态**：`queue_update`（steering/followUp 完整队列）、`entry_appended`（appendEntry 自定义条目）、`session_info_changed`（name）、`thinking_level_changed`。

**压缩事件**：`compaction_start`（reason: manual/threshold/overflow）；`compaction_end`（成功带 result：summary/firstKeptEntryId/tokensBefore/estimatedTokensAfter/usage；中止无 result 且 aborted=true；失败无 result 且带 errorMessage；溢出恢复成功 willRetry=true 后重试 prompt）。

**重试事件**：`auto_retry_start`（attempt/maxAttempts/delayMs/errorMessage）/`auto_retry_end`（success/finalError）；压缩与分支摘要重试：`summarization_retry_scheduled` / `summarization_retry_attempt_start`（source: compaction|branchSummary，reason）/ `summarization_retry_finished`。

**RPC-only**：`bash_execution_update`（id 匹配命令 id，流式全部输出）、`extension_error`（extensionPath/event/error）。类型用 `JsonAgentSessionEvent`。

## rpc-commands.md — RPC 命令参考

> 原文存档：[source/rpc-commands.md](source/rpc-commands.md)

| 类别 | 命令 | 要点 |
| --- | --- | --- |
| Prompting | `prompt` | 可带 `images`（base64 ImageContent）；流式中必须给 `streamingBehavior`（steer/followUp）；扩展命令立即执行；skill/模板先展开；`data.disposition` = handled/queued/started |
| | `steer` / `follow_up` | 流式中排队；展开 skill/模板；不允许扩展命令（用 prompt） |
| | `abort` / `clear_queue` | 中止并等空闲；清队返回被删消息文本（实现 Esc：先 clear_queue 再 abort） |
| 会话 | `new_session`（可被 session_before_switch 取消，返回 cancelled）、`switch_session`、`fork`（返回 fork 源文本）、`clone`、`get_fork_messages` | |
| 状态 | `get_state`（model/thinkingLevel/isStreaming/isCompacting/steeringMode/followUpMode/sessionFile/sessionId/sessionName/autoCompactionEnabled/messageCount/pendingMessageCount）、`get_messages`、`get_entries`（追加序全部条目，含压缩前历史与废弃分支；`since` 作持久游标，返回 leafId）、`get_tree`（树节点 {entry,children,label?,labelTimestamp?}，多根数组）、`get_last_assistant_text` | |
| 模型 | `set_model`（provider+modelId）、`cycle_model`、`get_available_models` | 返回完整 Model 对象 |
| 思考 | `set_thinking_level`（off/minimal/low/medium/high/xhigh/max）、`cycle_thinking_level`、`get_available_thinking_levels` | |
| 队列模式 | `set_steering_mode` / `set_follow_up_mode`（all / one-at-a-time 默认） | |
| 压缩 | `compact`（可带 customInstructions；响应含 summary/firstKeptEntryId/tokensBefore/estimatedTokensAfter/usage）、`set_auto_compaction` | |
| 重试 | `set_auto_retry`、`abort_retry` | |
| Bash | `bash`（执行 shell 命令并入上下文；输出流式 `bash_execution_update`；`excludeFromContext: true` 存会话不进模型；输出超限截断给 `fullOutputPath`。**入模型在下一个 prompt**：变成 "Ran `cmd`\n```...```" 的 UserMessage）、`abort_bash` | |
| 统计/导出 | `get_session_stats`（tokens/cost 含工具 usage 与压缩生成；contextUsage 为实际上下文占用；压缩后立即为 null 直到新回复）、`export_html`（可指定 outputPath） | |
| 命名/发现 | `set_session_name`（或启动 `--name`）、`get_commands`（extension/prompt/skill 三类 + sourceInfo 溯源；**不含内置 TUI 命令**） | |

## rpc-extension-ui.md — RPC 扩展 UI 子协议

> 原文存档：[source/rpc-extension-ui.md](source/rpc-extension-ui.md)

扩展经 `ctx.ui` 请求用户交互，RPC 模式下成为请求/响应子协议：

- **对话框方法**（`select`/`confirm`/`input`/`editor`）：发 `extension_ui_request`（唯一 id + method），阻塞等客户端回 `extension_ui_response`（id 匹配）。带 `timeout` 时 agent 侧超时自动用默认值解决（select/input/editor → undefined，confirm → false），客户端无需计时。
- **Fire-and-forget**（`notify`/`setStatus`/`setWidget`/`setTitle`/`set_editor_text`）：只发请求不期待响应。

**RPC 模式限制**：`custom()` 返回 undefined；`onTerminalInput()` no-op；`setWorkingMessage/setWorkingVisible/setWorkingIndicator/setHiddenThinkingLabel/setFooter/setHeader/addAutocompleteProvider/setEditorComponent/setToolsExpanded` no-op；`getEditorText()` 返回 ""；`getAllThemes()` 返回 []；`setTheme()` 报 "Theme switching not supported in RPC mode"。注意 `ctx.mode === "rpc"` 但 `ctx.hasUI === true`（对话框/通知可用），TUI 专属功能用 `ctx.mode === "tui"` 守护。

## codemode.md — Codemode 脚本工具

> 原文存档：[source/codemode.md](source/codemode.md)

`codemode` 工具让模型写 JavaScript 脚本调用 pi 的其他工具和**非 LLM 模型**（分类器/图像模型）。**只有脚本输出进模型**，所以脚本可并行调用、在模型看到前过滤大结果。

### 脚本

- 输入是**裸 JS 源码**（非 JSON/非代码围栏），作为 async 函数体在 **QuickJS 沙箱**里运行，顶层 `await`/`return` 可用。沙箱**无 Node API/文件系统/网络/定时器**——只能经工具与 `models` 触达外部。
- 首行可选 options 行（必须在第一行，否则调用先失败）：`// @options: {"max_output_tokens": 2000, "timeout_ms": 60000}`。`max_output_tokens` 默认 10000，超限保留头尾并写临时文件；`timeout_ms` 整脚本硬截止（生图可能几分钟，别设短）。
- 结果以 `Script completed/failed` + 墙钟时间 + 输出开始；多个 text 项各带 `==> text N/M <==`；console 汇总在 `<console_output>`；失败保留部分输出 + `Script error:`。失败前的工具调用不撤销；脚本结束时仍在跑的被取消。

### 全局量

| 全局 | 用途 |
| --- | --- |
| `tools.<name>(args)` | 调用工具（非法 JS 标识符字符变 `_`：`mcp__dev-radius__search` → `tools.mcp__dev_radius__search`）；失败/被拦/参数错 reject 带错误文本 |
| `text(value)` / `image(value)` | 输出文本 / 图片（base64 data: URL、{image_url} 或 image block；远程 URL 不支持；PNG/JPEG/GIF/WebP；同时存临时文件并指名路径） |
| `console.log/info/warn/error/debug` | 进 `<console_output>` 块 |
| `return value` / `exit()` | 顶层 return 同 text()；正常结束 |
| `store(key, value)` / `load(key)` | 跨 codemode 调用存小 JSON（单值 ≤262144 字符、总值 ≤1048576；只存成功的脚本——失败不写；每条写操作追加 codemode-store 自定义条目，分支各见其路径上写的值） |
| `ALL_TOOLS` / `searchTools(query, {limit?, namespace?})` / `describeTool(name)` / `describeNamespace(name)` | 枚举/检索/查看工具与命名空间（MCP 服务器） |
| `models` | 见下 |

**工具解析结果**：有 outputSchema 的工具 → 结构化值（`bash` → {output, truncated, full_output_path?, exit_code, wall_time_seconds}，output 上限 1MiB，超长保头尾各 512KiB）；MCP 工具 → 完整 CallToolResult（isError/structuredContent）；`read` → 文本或图片 block（`image()` 可显示）；其他（edit/write）→ 文本。用 `Promise.allSettled()` 保留成功者结果。

**描述与模式**：codemode 描述列出带 TS 声明的工具（按命名空间分组）；deferred 曝光工具不列出（MCP 默认 codemode 曝光即如此）；列出的声明共享 3000 估计 token 预算（`codemode.inlineBudget`）。`codemode.mode` 设置：`on`（默认，声明工具保持声明，描述说明如何从脚本调用）/ `only`（工具对模型隐藏、只列在 codemode 描述里，模型经脚本调用）。

### Models（非 LLM 模型）

`models.getModelsOfType(type, provider?)` / `getAvailableOfType`（有可用凭据的）/ `getModelOfType`；`classify(model, context)` 一次回答多个问题（questions 按 id，答案在 result.answers；不抛错，查 stopReason/errorMessage）；`generateImages(model, context)` 生图（可能几分钟）。chat 模型只列出**不能**从脚本运行。至多 4 个并发调用，更多排队等空位。模型 id 各提供方不同，用 `getAvailableOfType` 找当前凭据可用的 id。

- **classify**：questions 三种：`choice`（pick label，criteria 映射）/ `score`（有序量表，criteria 从低到高，answer.score 为期望级别下标）/ `bool`（概率）。`input` 含 "image" 的分类器可连带图片（`tools.read()` 图片文件返回 image block 可直接传）。
- **generateImages**：`input` 为文本块 + 图片块（编辑/参考）；`output` 为生成图片 + 文本块；用 `image(block)` 展示，别用 text()/console/return 打印 base64。

### 限制

- VM 256MB 内存；超限 `InternalError: out of memory`（过滤/聚合大数据）。
- 至多 2 个 codemode worker/进程（`PI_CODEMODE_MAX_WORKERS` 改）；满时按到达顺序等空位，60 秒或 timeout_ms 内没空位则失败。
- 无定时器：等一个永不 settle 的 promise 立即失败；脚本不能启动其他 codemode 脚本。

**相关页面**：[02-总览与快速上手.md](02-总览与快速上手.md) · [07-扩展与资源.md](07-扩展与资源.md) · [08-MCP集成.md](08-MCP集成.md) · [11-命令行.md](11-命令行.md)

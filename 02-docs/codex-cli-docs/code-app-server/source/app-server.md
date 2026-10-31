# 原文存档元信息
- 来源 URL: https://www.codex-docs.com/docs/app-server
- 抓取日期: 2026-10-31
- 原文语言: 中文（codex-docs.com 第三方整理的中文文档站）

---

<!-- normalized-upstream-mdx: inert-v1; never execute raw source -->

# Codex App Server

Codex app-server 是 Codex 用于支持富客户端（例如 Codex VS Code 扩展）的接口。当你希望在自己的产品中进行深度集成时，可使用它来实现身份验证、对话历史记录、审批和流式智能体事件。app-server 的实现已在 Codex GitHub 仓库中开源（[openai/codex/codex-rs/app-server](https://github.com/openai/codex/tree/main/codex-rs/app-server)）。有关 Codex 开源组件的完整列表，请参阅[开源](/docs/open-source)页面。

<aside class="doc-callout doc-callout--note">
  <p>如果你要自动执行作业或在 CI 中运行 Codex，请改用 <a href="/docs/codex-sdk">Codex SDK</a>。</p>
</aside>

## 连接 CLI 终端 UI

远程终端 UI 模式允许你在一台机器上运行 app-server，并从另一台机器连接
Codex CLI 终端界面。首先启动 WebSocket 监听器：

```bash
codex app-server --listen ws://127.0.0.1:4500
```

然后连接终端 UI：

```bash
codex --remote ws://127.0.0.1:4500
```

对于非本地连接，请配置 WebSocket 身份验证，并将
连接置于 TLS 之后。将 bearer token 存储在环境变量中，并
传入该变量的名称，不要将 token 直接放在命令行中：

```bash
export CODEX_REMOTE_TOKEN="$(cat "$HOME/.codex/app-server-token")"
codex --remote wss://remote-host:4500 \
  --remote-auth-token-env CODEX_REMOTE_TOKEN
```

`--remote` 选项接受 `ws://`、`wss://`、`unix://` 和
`unix://PATH` 端点。仅对 localhost 或通过 SSH
端口转发的连接使用普通 WebSocket。

## 连接远程 Code Mode 主机

默认情况下，app-server 会启动本地 Code Mode 主机。若要改用远程主机，
请传入其安全 WebSocket URL：

```bash
codex app-server --code-mode-host wss://code-mode.example.com/host
```

`--code-mode-host` 控制从 app-server 到其 Code
Mode 主机的出站连接。它不会更改 `--listen`；后者控制客户端如何连接到
app-server。同一 app-server 进程中的所有聊天共享所选的
Code Mode 主机连接。

远程主机应使用 `wss://`。仅对 localhost 或
通过 SSH 转发的连接使用 `ws://`。app-server 命令和 WebSocket 传输
仍处于实验阶段，不支持生产工作负载。

## 协议

与 [MCP](https://modelcontextprotocol.io/) 类似，`codex app-server` 使用 JSON-RPC 2.0 消息支持双向通信（在线路上传输时省略 `"jsonrpc":"2.0"` 标头）。

支持的传输方式：

- `stdio`（`--listen stdio://`，默认）：以换行符分隔的 JSON（JSONL）。
- `websocket`（`--listen ws://IP:PORT`，实验性且不受支持）：每个 WebSocket 文本帧包含一条
  JSON-RPC 消息。
- Unix socket（`--listen unix://` 或 `--listen unix://PATH`）：通过 Codex 的默认 app-server 控制套接字或自定义 Unix
  socket 路径建立 WebSocket 连接，并使用标准 HTTP Upgrade 握手。
- `off`（`--listen off`）：不公开本地传输。

使用 `--listen ws://IP:PORT` 运行时，同一监听器还会提供基本的
HTTP 健康探测：

- 监听器可以接受新连接后，`GET /readyz` 返回 `200 OK`。
- 请求不包含 `Origin`
  标头时，`GET /healthz` 返回 `200 OK`。
- 带有 `Origin` 标头的请求会被拒绝，并返回 `403 Forbidden`。

WebSocket 传输仍处于实验阶段且不受支持。`ws://127.0.0.1:PORT` 等
本地监听器适用于 localhost 和 SSH 端口转发
工作流。在逐步推出期间，非环回 WebSocket 监听器目前默认允许未经身份验证的
连接，因此在远程公开监听器之前，请先配置 WebSocket 身份验证。

支持的 WebSocket 身份验证标志：

- `--ws-auth capability-token --ws-token-file /absolute/path`
- `--ws-auth capability-token --ws-token-sha256 HEX`
- `--ws-auth signed-bearer-token --ws-shared-secret-file /absolute/path`

对于已签名的 bearer token，你还可以设置 `--ws-issuer`、`--ws-audience` 和
`--ws-max-clock-skew-seconds`。客户端在 WebSocket 握手期间以
`Authorization: Bearer <token>` 形式提供凭据，app-server 会在处理 JSON-RPC `initialize` 之前
强制执行身份验证。

应优先使用 `--ws-token-file`，不要在命令行中传入原始 bearer token。仅当客户端将原始高熵 token 保存在
单独的本地机密存储中时，才使用 `--ws-token-sha256`；该哈希仅用作验证器，客户端仍需持有
原始 token。

在 WebSocket 模式下，app-server 使用有界队列。当请求入口已满时，
服务器会拒绝新请求，并返回 JSON-RPC 错误代码 `-32001` 和消息
`"Server overloaded; retry later."` 客户端应采用带抖动的指数递增延迟进行重试。

## 消息数据结构（schema）

请求包含 `method`、`params` 和 `id`。

示例使用 [GPT-6.1 Sol](/docs/models#gpt-6.1-sol)，你登录的账户或工作区
必须有权使用该模型。如有需要，可使用 [`model/list`](#list-models-modellist)
选择可用的模型。

```json
{ "method": "thread/start", "id": 10, "params": { "model": "gpt-6.1-sol" } }
```

响应会回显 `id`，并包含 `result` 或 `error`：

```json
{ "id": 10, "result": { "thread": { "id": "thr_123" } } }
```

```json
{ "id": 10, "error": { "code": 123, "message": "Something went wrong" } }
```

通知省略 `id`，仅使用 `method` 和 `params`：

```json
{ "method": "turn/started", "params": { "turn": { "id": "turn_456" } } }
```

你可以通过 CLI 生成 TypeScript 数据结构或 JSON Schema 包。每份输出都对应你运行的具体 Codex 版本，因此生成的产物会与该版本完全匹配：

```bash
codex app-server generate-ts --out ./schemas
codex app-server generate-json-schema --out ./schemas
```

## 开始使用

1. 使用 `codex app-server`（默认 stdio 传输）、
   `codex app-server --listen ws://127.0.0.1:4500`（TCP WebSocket）或
   `codex app-server --listen unix://`（默认 Unix socket）启动服务器。
2. 通过所选传输方式连接客户端，然后发送 `initialize`，接着发送 `initialized` 通知。
3. 启动一个聊天和一个轮次，然后持续从活动传输流中读取通知。

示例（Node.js / TypeScript）：

```typescript
import { spawn } from "node:child_process";

const proc = spawn("codex", ["app-server"], {
  stdio: ["pipe", "pipe", "inherit"],
});
const rl = readline.createInterface({ input: proc.stdout });
const send = (message: unknown) => {
  proc.stdin.write(`${JSON.stringify(message)}\n`);
};
let threadId: string | null = null;
rl.on("line", (line) => {
  const msg = JSON.parse(line) as any;
  console.log("server:", msg);
  if (msg.id === 1 && msg.result?.thread?.id && !threadId) {
    threadId = msg.result.thread.id;
    send({
      method: "turn/start",
      id: 2,
      params: {
        threadId,
        input: [{ type: "text", text: "Summarize this repo." }],
      },
    });
  }
});
send({
  method: "initialize",
  id: 0,
  params: {
    clientInfo: {
      name: "my_product",
      title: "My Product",
      version: "0.1.0",
    },
  },
});
send({ method: "initialized", params: {} });
send({ method: "thread/start", id: 1, params: { model: "gpt-6.1-sol" } });
```

## 核心原语

- **聊天**：用户与 Codex 智能体之间的对话。聊天包含轮次。
- **轮次**：单个用户请求及其后续的智能体工作。轮次包含条目，并以流式方式传输增量更新。
- **条目**：输入或输出的一个单元（用户消息、智能体消息、命令运行、文件更改、工具调用等）。

使用聊天 API 创建、列出或归档对话。使用轮次 API 驱动对话，并通过轮次通知以流式方式获取进度。

## 生命周期概览

- **每个连接初始化一次**：打开传输连接后，立即发送包含客户端元数据的 `initialize` 请求，然后发出 `initialized`。服务器会拒绝该连接上握手之前的任何请求。
- **启动（或恢复）聊天**：调用 `thread/start` 创建新对话，调用 `thread/resume` 继续现有对话，或调用 `thread/fork` 将历史记录分支到新的聊天 id。
- **开始轮次**：使用目标 `threadId` 和用户输入调用 `turn/start`。可选字段可覆盖模型、个性、`cwd`、沙箱策略等设置。
- **引导活动轮次**：调用 `turn/steer`，将用户输入追加到当前正在进行的轮次，而不创建新轮次。
- **流式传输事件**：发送 `turn/start` 后，持续读取 stdout 上的通知：`thread/archived`、`thread/unarchived`、`item/started`、`item/completed`、`item/agentMessage/delta`、工具进度及其他更新。
- **结束轮次**：模型完成工作或执行 `turn/interrupt` 取消后，服务器会发出带有最终状态的 `turn/completed`。

## 初始化

客户端必须在每个传输连接上调用任何其他方法之前发送一次 `initialize` 请求，然后以 `initialized` 通知进行确认。初始化之前发送的请求会收到 `Not initialized` 错误；在同一连接上重复调用 `initialize` 则会返回 `Already initialized`。

服务器会返回其向上游服务提供的 user agent 字符串，以及描述运行时目标的 `platformFamily` 和 `platformOs` 值。设置 `clientInfo` 以标识你的集成。

`initialize.params.capabilities` 还支持以下客户端功能：

- `optOutNotificationMethods` - 要为此连接屏蔽的确切通知方法名称。
  匹配为精确匹配（不支持通配符或前缀）；未知名称会被接受并忽略。
- `requestAttestation` - 选择启用由服务器发起的 `attestation/generate`
  请求。提供上游证明的桌面主机会以不透明的
  `{ "token": "..." }` 值响应。
- `mcpServerOpenaiFormElicitation` - 允许下游 MCP server 发送
  `mcpServer/elicitation/request` 的 OpenAI 扩展形式变体。

**重要提示**：使用 `clientInfo.name` 向 OpenAI Compliance Logs Platform 标识你的客户端。如果你正在开发面向企业使用的新 Codex 集成，请联系 OpenAI，将其添加到已知客户端列表中。有关更多背景信息，请参阅 [Codex 日志参考](https://chatgpt.com/public/admin/api-reference#tag/Codex)。

示例（来自 Codex VS Code 扩展）：

```json
{
  "method": "initialize",
  "id": 0,
  "params": {
    "clientInfo": {
      "name": "codex_vscode",
      "title": "Codex VS Code Extension",
      "version": "0.1.0"
    }
  }
}
```

选择不接收通知的示例：

```json
{
  "method": "initialize",
  "id": 1,
  "params": {
    "clientInfo": {
      "name": "my_client",
      "title": "My Client",
      "version": "0.1.0"
    },
    "capabilities": {
      "experimentalApi": true,
      "optOutNotificationMethods": ["thread/started", "item/agentMessage/delta"]
    }
  }
}
```

## 选择启用实验性 API

某些 app-server 方法和字段有意受 `experimentalApi` 功能限制。

- 省略 `capabilities`（或将 `experimentalApi` 设置为 `false`）可继续使用稳定 API 范围，此时服务器会拒绝实验性方法/字段。
- 将 `capabilities.experimentalApi` 设置为 `true` 可启用实验性方法和字段。

```json
{
  "method": "initialize",
  "id": 1,
  "params": {
    "clientInfo": {
      "name": "my_client",
      "title": "My Client",
      "version": "0.1.0"
    },
    "capabilities": {
      "experimentalApi": true
    }
  }
}
```

如果客户端未选择启用就发送实验性方法或字段，app-server 会返回以下错误：

`<descriptor> requires experimentalApi capability`

## API 概览

- `thread/start` - 创建新聊天；发出 `thread/started`，并自动订阅该聊天的轮次/条目事件。
- `thread/resume` - 按 id 重新打开现有聊天，以便后续 `turn/start` 调用追加到该聊天。
- `thread/fork` - 通过复制已存储的历史记录，将聊天派生为具有新聊天 id 的聊天。传入 `lastTurnId` 可复制截至该轮次的历史记录并忽略后续轮次，传入 `ephemeral: true` 则可创建内存中的派生聊天。为新聊天发出 `thread/started`；返回的聊天在可用时包含 `forkedFromId`。
- `thread/read` - 按 ID 读取已存储的聊天元数据，而不恢复聊天。使用 `thread/turns/list` 和 `thread/items/list` 加载历史记录。返回的 `thread` 对象包含运行时 `status`。
- `thread/list` - 分页浏览已存储的聊天日志；支持基于游标的分页，以及 `modelProviders`、`sourceKinds`、`archived`、`isPinned`、`cwd`、`useStateDbOnly`、`searchTerm` 和实验性 `parentThreadId` 或 `ancestorThreadId` 筛选器。返回的 `thread` 对象包含运行时 `status`。
- `thread/turns/list` - 分页浏览已存储聊天的轮次历史记录，而不恢复聊天。`itemsView` 控制是省略轮次条目、加载摘要，还是完整加载。
- `thread/items/list` - 分页浏览已持久化的聊天条目，可选择仅限于某个 `turnId`。当前聊天存储必须支持条目分页。
- `thread/loaded/list` - 列出当前加载到内存中的聊天 id。
- `thread/name/set` - 为已加载的聊天或持久化的 rollout 设置或更新面向用户的聊天名称；发出 `thread/name/updated`。
- `thread/goal/set` - 设置聊天目标；发出 `thread/goal/updated`。
- `thread/goal/get` - 读取聊天的当前目标。
- `thread/goal/clear` - 清除聊天目标；发出 `thread/goal/cleared`。
- `thread/metadata/update` - 修补由 SQLite 支持的已存储聊天元数据，包括持久化的 `gitInfo` 和 `isPinned`。
- `thread/archive` - 将聊天的日志文件移至归档目录，并尝试归档尚未归档的已派生后代聊天日志；成功时返回 `{}`，并为每个已归档聊天发出 `thread/archived`。
- `thread/delete` - 永久删除持久化的活动或已归档聊天，以及所有已派生的后代聊天；成功时返回 `{}`，并为每个已删除聊天发出 `thread/deleted`。
- `thread/unsubscribe` - 取消此连接对聊天轮次/条目事件的订阅。如果这是最后一个订阅方，服务器会在聊天进入无订阅方状态并经过一段不活动宽限期后卸载该聊天，同时发出 `thread/closed`。
- `thread/unarchive` - 将已归档的聊天 rollout 恢复到活动会话目录；返回已恢复的 `thread`，并且发出 `thread/unarchived`。
- `thread/status/changed` - 当已加载聊天的运行时 `status` 发生变化时发出的通知。
- `thread/compact/start` - 触发聊天的对话历史记录压缩；立即返回 `{}`，同时通过 `turn/*` 和 `item/*` 通知流式传输进度。
- `thread/shellCommand` - 针对聊天运行用户发起的 shell 命令。该命令在沙箱外运行，拥有完全访问权限，且不继承聊天的沙箱策略。
- `thread/backgroundTerminals/clean` - 停止聊天的所有运行中后台终端（实验性功能；需要 `capabilities.experimentalApi`）。
- `thread/backgroundTerminals/list` - 列出已加载聊天的运行中后台终端（实验性功能；需要 `capabilities.experimentalApi`）。
- `thread/backgroundTerminals/terminate` - 按 app-server `processId` 终止一个运行中的后台终端（实验性功能；需要 `capabilities.experimentalApi`）。
- `thread/revert` - 从持久化分页聊天的历史记录中移除指定轮次及其后所有轮次；返回更新后的元数据和历史记录游标，然后发出 `thread/reverted`。
- `turn/start` - 向聊天添加用户输入或独立工具输出，并开始 Codex 生成；以初始 `turn` 响应并流式传输事件。对于 `collaborationMode`，`settings.developer_instructions: null` 表示“使用所选模式的内置指令”。
- `thread/inject_items` - 将原始 Responses API 条目追加到已加载聊天中模型可见的历史记录，而不启动用户轮次。
- `turn/steer` - 将用户输入追加到聊天当前正在进行的轮次；返回已接受的 `turnId`。
- `turn/interrupt` - 请求取消正在进行的轮次；成功时为 `{}`，且该轮次以 `status: "interrupted"` 结束。
- `review/start` - 为聊天启动 Codex 评审器；发出 `enteredReviewMode` 和 `exitedReviewMode` 条目。
- `command/exec` - 在服务器沙箱下运行单条命令，而不启动聊天/轮次。
- `command/exec/write` - 将 `stdin` 字节写入运行中的 `command/exec` 会话，或关闭 `stdin`。
- `command/exec/resize` - 调整运行中、由 PTY 支持的 `command/exec` 会话大小。
- `command/exec/terminate` - 停止运行中的 `command/exec` 会话。
- `command/exec/outputDelta`（通知）- 针对流式 `command/exec` 会话中经 base64 编码的 stdout/stderr 数据块发出。
- `process/spawn` - 在 Codex 沙箱外启动显式进程会话（实验性功能；需要 `capabilities.experimentalApi`）。
- `process/writeStdin` - 将 stdin 字节写入运行中的 `process/spawn` 会话，或关闭 stdin（实验性功能）。
- `process/resizePty` - 调整运行中、由 PTY 支持的进程会话大小（实验性功能）。
- `process/kill` - 终止运行中的进程会话（实验性功能）。
- `process/outputDelta` 和 `process/exited`（通知）- 针对流式进程输出和进程退出状态发出（实验性功能）。
- `model/list` - 列出可用模型（设置 `includeHidden: true` 可包含具有 `hidden: true` 的条目），以及推理强度选项、可选 `upgrade` 和 `inputModalities`。
- `modelProvider/capabilities/read` - 读取模型/提供商组合的能力边界。
- `experimentalFeature/list` - 列出功能开关及其生命周期阶段元数据，并支持游标分页。
- `experimentalFeature/enablement/set` - 修补受支持功能键（例如 `apps` 和 `plugins`）的内存运行时设置。
- `environment/info` - 实验性功能；连接到已配置的执行环境，并返回其 shell 和默认工作目录。
- `permissionProfile/list` - 列出 beta 权限配置档案，以及生效的要求是否允许这些配置档案，并支持游标分页。
- `collaborationMode/list` - 列出协作模式预设（实验性功能，不分页）。
- `skills/list` - 列出一个或多个 `cwd` 值对应的技能（支持 `forceReload` 和可选 `perCwdExtraUserRoots`）。
- `skills/extraRoots/set` - 替换用于发现独立技能的进程级额外根目录，但不将其持久化。
- `skills/changed`（通知）- 当受监视的本地技能文件发生变化时发出。
- `hooks/list` - 列出为一个或多个 `cwd` 值发现的生命周期钩子。
- `marketplace/add` - 添加远程插件市场，并将其持久化到用户的市场配置中。
- `marketplace/remove` - 移除已配置的市场及其已安装的市场根目录（如果存在）。
- `marketplace/upgrade` - 刷新已配置的 Git 市场；如果省略市场名称，则刷新所有已配置的 Git 市场。
- `plugin/list` - 开发中；列出已发现的插件市场和插件状态，包括安装/身份验证策略元数据、市场加载错误、精选插件 id，以及本地、Git、包注册表或远程插件源元数据。摘要可包含远程 `version`、本地 `localVersion`、结构化浅色/深色图标和 `installPolicySource`；对于当前的远程行，后者可以是 `null`、`WORKSPACE_SETTING` 或 `IMPLICIT_CANONICAL_APP`。暂勿从生产客户端调用此方法。
- `plugin/read` - 开发中；按市场路径读取一个插件，或按远程市场名称和插件名称读取一个插件，包括捆绑的技能、应用、MCP server 名称，以及远程目录提供的远程插件 `shareUrl`。暂勿从生产客户端调用此方法。
- `plugin/install` - 开发中；从市场路径或远程市场名称安装插件。暂勿从生产客户端调用此方法。
- `plugin/uninstall` - 开发中；卸载已安装的插件。暂勿从生产客户端调用此方法。
- `plugin/skill/read` - 按需读取远程插件技能 Markdown，需指定远程市场、插件 id 和技能名称。
- `app/installed` - 读取已安装应用的运行时状态，包括每个应用实际生效的启用状态和可调用状态。
- `app/list` - 分页列出可用应用（连接器），以及可访问性/启用状态元数据。
- `app/read` - 获取指定应用 id 的元数据和可选的仅供显示的工具摘要。
- `skills/config/write` - 按路径启用或禁用技能。
- `mcpServer/oauth/login` - 为已配置的 MCP server 启动 OAuth 登录；返回授权 URL，并在完成时发出 `mcpServer/oauthLogin/completed`。
- `tool/requestUserInput` - 通过工具调用向用户提出 1–3 个简短问题（实验性功能）；问题可设置 `isOther` 以提供自由填写选项。
- `mcpServer/elicitation/request`（服务器请求）- 请求客户端提供结构化表单输入，或确认 MCP server 所请求的 URL 流程。
- `item/permissions/requestApproval`（服务器请求）- 请求客户端授予内置 `request_permissions` 工具所请求的网络或文件系统权限子集。
- `config/mcpServer/reload` - 从磁盘重新加载 MCP server 配置，并为已加载聊天将刷新加入队列。
- `mcpServerStatus/list` - 列出 MCP server、工具、资源和身份验证状态（游标 + 数量限制分页）。使用 `detail: "full"` 获取完整数据，或使用 `detail: "toolsAndAuthOnly"` 省略资源。传入 `serverName` 可发现单个服务器；提供 `threadId` 时，请求会复用该聊天的 MCP 连接。
- `mcpServer/resource/read` - 通过已初始化的 MCP server 读取单个 MCP 资源。
- `mcpServer/tool/call` - 调用聊天所配置的 MCP server 上的工具。
- `mcpServer/startupStatus/updated`（通知）- 当已加载聊天所配置的 MCP server 启动状态发生变化时发出。
- `windowsSandbox/setupStart` - 为 `elevated` 或 `unelevated` 模式启动 Windows 沙箱设置；该调用会快速返回，随后发出 `windowsSandbox/setupCompleted`。
- `feedback/upload` - 提交反馈报告（分类 + 可选原因/日志 + 对话 id，以及可选的 `extraLogFiles` 附件）。
- `config/read` - 在解析配置分层后，获取磁盘上的生效配置。
- `externalAgentConfig/detect` - 检测可使用 `includeHome` 和可选 `cwds` 迁移的外部智能体产物；每个检测到的条目都包含 `cwd`（主目录使用 `null`）。
- `externalAgentConfig/import` - 通过传入带有 `cwd` 的显式 `migrationItems`（主目录使用 `null`），应用选定的外部智能体迁移项。支持的条目类型包括配置、技能、`AGENTS.md`、插件、MCP server 配置、子智能体、钩子、命令和会话；非空导入会在工作完成时发出 `externalAgentConfig/import/progress` 和 `externalAgentConfig/import/completed`。插件和会话导入可以异步完成。
- `config/value/write` - 将单个配置键/值写入磁盘上的用户 `config.toml`。
- `config/batchWrite` - 以原子方式将配置编辑应用到磁盘上的用户 `config.toml`。
- `configRequirements/read` - 从 `requirements.toml` 和/或 MDM 获取要求，包括确切的受管配置、允许列表、固定的 `featureRequirements` 和网络要求（如果尚未设置，则为 `null`）。
- `fs/readFile`、`fs/writeFile`、`fs/createDirectory`、`fs/getMetadata`、`fs/readDirectory`、`fs/remove`、`fs/copy`、`fs/watch`、`fs/unwatch` 和 `fs/changed`（通知）- 通过 app-server v2 文件系统 API 对绝对文件系统路径执行操作。

插件摘要包含一个 `source` 联合类型。本地插件返回
`{ "type": "local", "path": ... }`，由 Git 支持的市场条目返回
`{ "type": "git", "url": ..., "path": ..., "refName": ..., "sha": ... }`，
包注册表条目返回
`{ "type": "npm", "package": ..., "version": ..., "registry": ... }`，远程目录条目返回 `{ "type": "remote" }`。对于仅存在于远程目录的
条目，`PluginMarketplaceEntry.path` 可以是 `null`；读取或安装
这些插件时，请传入 `remoteMarketplaceName`，而不是 `marketplacePath`。

## 模型

### 列出模型（`model/list`）

在呈现模型或个性选择器之前，调用 `model/list` 以发现可用模型及其功能。

以下响应展示了其结构。可用模型、推理
强度和默认值取决于客户端和账户；请使用返回的
值，而不要对本示例中的值进行硬编码。

```json
{ "method": "model/list", "id": 6, "params": { "limit": 20, "includeHidden": false } }
{ "id": 6, "result": {
  "data": [{
    "id": "gpt-6.1-sol",
    "model": "gpt-6.1-sol",
    "displayName": "GPT-6.1 Sol",
    "hidden": false,
    "defaultReasoningEffort": "medium",
    "supportedReasoningEfforts": [{
      "reasoningEffort": "medium",
      "description": "Balances speed and reasoning depth for everyday tasks"
    }],
    "inputModalities": ["text", "image"],
    "supportsPersonality": false,
    "isDefault": true
  }],
  "nextCursor": null
} }
```

每个模型条目可以包含：

- `supportedReasoningEfforts` - 模型支持的推理强度选项。
- `defaultReasoningEffort` - 建议客户端使用的默认推理强度。
- `upgrade` - 可选的建议升级模型 id，用于客户端中的迁移提示。
- `upgradeInfo` - 可选的升级元数据，用于客户端中的迁移提示。
- `hidden` - 是否在默认选择器列表中隐藏该模型。
- `inputModalities` - 模型支持的输入类型（例如 `text`、`image`）。
- `supportsPersonality` - 已弃用的兼容性字段；始终为 `false`。模型不再支持个性选择。
- `isDefault` - 模型是否为建议的默认模型。

默认情况下，`model/list` 仅返回在选择器中可见的模型。如果你需要完整列表，并希望使用 `hidden` 在客户端进行筛选，请设置 `includeHidden: true`。

如果缺少 `inputModalities`（较旧的模型目录），为保持向后兼容，请将其视为 `["text", "image"]`。

### 列出实验性功能（`experimentalFeature/list`）

使用此端点发现带有元数据和生命周期阶段的功能开关：

```json
{ "method": "experimentalFeature/list", "id": 7, "params": { "limit": 20 } }
{ "id": 7, "result": {
  "data": [{
    "name": "unified_exec",
    "stage": "beta",
    "displayName": "Unified exec",
    "description": "Use the unified PTY-backed execution tool.",
    "announcement": "Beta rollout for improved command execution reliability.",
    "enabled": false,
    "defaultEnabled": false
  }],
  "nextCursor": null
} }
```

`stage` 可以是 `beta`、`underDevelopment`、`stable`、`deprecated` 或 `removed`。对于非 beta 标志，`displayName`、`description` 和 `announcement` 可以是 `null`。

### 检查执行环境（实验性）

在已配置的远程环境中开始工作之前，使用 `environment/info` 检查该环境。
此方法需要 `capabilities.experimentalApi = true`。

```json
{ "method": "environment/info", "id": 8, "params": { "environmentId": "devbox" } }
{ "id": 8, "result": {
  "shell": { "name": "zsh", "path": "/bin/zsh" },
  "cwd": "file:///workspace/project"
} }
```

`cwd` 可以是 `null`。存在时，它是使用该
环境原生路径语法的规范 `file:` URI。未知环境 ID 以及连接或
协议故障会返回请求错误。

## 聊天

- `thread/read` 读取已存储的聊天元数据，而不订阅聊天。
- `thread/turns/list` 分页浏览已存储聊天的轮次历史记录，而不
  恢复聊天。使用 `itemsView` 选择省略轮次条目、
  加载摘要或完整加载。
- `thread/items/list` 分页浏览已持久化的聊天条目，可选择仅限于某个轮次。
- `thread/list` 支持游标分页，以及 `modelProviders`、`sourceKinds`、`archived`、`isPinned`、`cwd`、`useStateDbOnly`、`searchTerm` 和实验性 `parentThreadId` 或 `ancestorThreadId` 筛选。
- `thread/loaded/list` 返回当前位于内存中的聊天 ID。
- `thread/archive` 将聊天的持久化 JSONL 日志移入归档目录，并尝试归档尚未归档的衍生后代聊天日志。
- `thread/delete` 永久删除持久化的活动或已归档聊天及其衍生后代聊天。
- `thread/metadata/update` 修补已存储聊天的元数据，包括持久化的 `gitInfo` 和 `isPinned`。
- `thread/unsubscribe` 取消当前连接对已加载聊天的订阅，并可能在非活动宽限期后触发 `thread/closed`。
- `thread/unarchive` 将已归档的聊天 rollout 恢复到活动会话目录。
- `thread/compact/start` 触发压缩并立即返回 `{}`。
- `thread/revert` 从持久化分页聊天的历史记录中移除指定轮次及其后所有轮次。它不会更改本地文件。
- `thread/inject_items` 将原始 Responses API 条目追加到已加载聊天中模型可见的历史记录，而不启动用户轮次。

### 启动或恢复聊天

需要新的 Codex 对话时，请启动一个新聊天。

```json
{ "method": "thread/start", "id": 10, "params": {
  "model": "gpt-6.1-sol",
  "cwd": "/Users/me/project",
  "approvalPolicy": "never",
  "sandbox": "workspaceWrite",
  "serviceName": "my_app_server_client"
} }
{ "id": 10, "result": {
  "thread": {
    "id": "thr_123",
    "sessionId": "thr_123",
    "preview": "",
    "ephemeral": false,
    "modelProvider": "openai",
    "createdAt": 1730910000
  }
} }
{ "method": "thread/started", "params": { "thread": { "id": "thr_123" } } }
```

`serviceName` 是可选的。如果你希望 app-server 使用集成的服务名称标记聊天级指标，请设置此项。

`thread/start`、`thread/resume` 和 `thread/fork` 返回
`instructionSources`，即已加载的指令文件路径数组。每个路径都使用
其源环境的原生绝对路径语法，远程
环境也不例外。

新的持久化本地聊天默认使用分页历史记录。使用
`thread/turns/list` 和 `thread/items/list` 加载历史记录。显式将
`historyMode` 设置为 `"legacy"` 或 `"paginated"`（在 `thread/start` 上）属于
实验性功能，需要 `capabilities.experimentalApi = true`。

选择启用 `capabilities.experimentalApi` 的 beta 客户端可以在 `permissions` 中传入命名的
权限配置档案 id，而不是旧版 `sandbox` 字段。
不要同时发送 `permissions` 和 `sandbox`。使用
带项目 `cwd` 的 `permissionProfile/list`，可发现可用的配置档案，
以及受管要求是否允许每个配置档案。

`thread.sessionId` 标识当前实时会话树的根。根聊天
使用自己的聊天 id 作为会话 id；分支聊天保留其来源根聊天的会话 id。
客户端应从 `thread.sessionId` 读取会话 id，而不是根据聊天 id 推导。

要继续已存储的会话，请使用之前记录的 `thread.id` 调用 `thread/resume`。传入 `excludeTurns: true` 以返回聊天元数据和实时会话状态，然后使用分页方法加载历史记录：

```json
{ "method": "thread/resume", "id": 11, "params": {
  "threadId": "thr_123",
  "excludeTurns": true
} }
{ "id": 11, "result": { "thread": { "id": "thr_123", "name": "Bug bash notes", "ephemeral": false } } }
```

对于分页聊天，`thread/resume` 和
`thread/fork` 返回完整历史记录的方式已弃用，并会发出 `deprecationNotice`。这两个方法都接受
`excludeTurns: true`，无需启用实验性 API。`thread/resume` 响应
还可以返回 `turnsBackwardsCursor` 和 `itemsBackwardsCursor`。将它们分别传给
对应的分页方法，并指定 `sortDirection: "desc"`；第一页
包含游标的锚点。

恢复聊天本身不会更新 `thread.updatedAt`（也不会更新 rollout 文件的修改时间）。时间戳会在你启动轮次时更新。

如果在配置中将已启用的 MCP server 标记为 `required`，而该服务器初始化失败，`thread/start` 和 `thread/resume` 会失败，而不是在缺少该服务器的情况下继续运行。

`thread/start` 上的 `dynamicTools` 是实验性字段（需要 `capabilities.experimentalApi = true`）。Codex 会将这些动态工具持久化到聊天 rollout 元数据中，并在你未提供新动态工具时通过 `thread/resume` 恢复它们。

如果你使用与 rollout 中记录不同的模型恢复聊天，Codex 会发出警告，并在下一轮次应用一次性模型切换指令。

### 管理聊天目标

使用 `thread/goal/set`、`thread/goal/get` 和 `thread/goal/clear` 管理
与 TUI 中 `/goal` 所呈现内容相同的持久化目标状态。

```json
{ "method": "thread/goal/set", "id": 13, "params": {
  "threadId": "thr_123",
  "objective": "Finish the migration and keep tests green",
  "status": "active",
  "tokenBudget": 40000
} }
{ "id": 13, "result": { "goal": {
  "threadId": "thr_123",
  "objective": "Finish the migration and keep tests green",
  "status": "active",
  "tokenBudget": 40000,
  "tokensUsed": 0,
  "timeUsedSeconds": 0
} } }
{ "method": "thread/goal/updated", "params": {
  "threadId": "thr_123",
  "goal": {
    "threadId": "thr_123",
    "objective": "Finish the migration and keep tests green",
    "status": "active",
    "tokenBudget": 40000,
    "tokensUsed": 0,
    "timeUsedSeconds": 0
  }
} }
```

目标内容不得为空，且最多为 4,000 个字符。提供新
目标会替换原目标并重置用量统计。提供当前尚未终止的
目标或省略 `objective`，会在保留用量历史记录的同时更新状态或 token 预算。

若要从已存储会话创建分支，请使用 `thread.id` 调用 `thread/fork`。这会创建新的聊天 id，并为其发出 `thread/started` 通知。传入
`lastTurnId` 可复制截至该轮次（含该轮次）的历史记录，并省略后续
轮次：

```json
{ "method": "thread/fork", "id": 12, "params": { "threadId": "thr_123", "lastTurnId": "turn_456", "excludeTurns": true } }
{ "id": 12, "result": { "thread": { "id": "thr_456", "sessionId": "thr_123", "forkedFromId": "thr_123" } } }
{ "method": "thread/started", "params": { "thread": { "id": "thr_456" } } }
```

app-server 会拒绝正在进行的 `lastTurnId`。如果在源聊天处于轮次中途时省略该字段，
分支会记录中断标记，而不会保留未标记的部分轮次。

传入 `ephemeral: true` 可创建内存中分支，而不将其添加到已存储的
聊天列表：

```json
{
  "method": "thread/fork",
  "id": 13,
  "params": {
    "threadId": "thr_123",
    "ephemeral": true,
    "excludeTurns": true
  }
}
{
  "id": 13,
  "result": {
    "thread": {
      "id": "thr_789",
      "sessionId": "thr_789",
      "forkedFromId": "thr_123",
      "ephemeral": true
    }
  }
}
```

分页聊天的临时分支需要 `excludeTurns: true`。

设置面向用户的聊天标题后，app-server 会在 `thread/list`、`thread/read`、`thread/resume` 和 `thread/unarchive` 响应中填充 `thread.name`。在后续设置标题之前，`thread/start` 和 `thread/fork` 可能省略 `name`（或返回 `null`）。

### 读取已存储聊天（不恢复）

如果你需要已存储的聊天数据，但不想恢复该聊天或订阅其事件，请使用 `thread/read`。

- `includeTurns` - 为 `false` 或省略时，仅返回聊天摘要。将其设为 `true` 会加载完整历史记录，这种方式对于分页聊天已弃用，并会发出 `deprecationNotice`。请改用分页方法。
- 返回的 `thread` 对象包含运行时 `status`（`notLoaded`、`idle`、`systemError`，或带有 `activeFlags` 的 `active`）。

```json
{ "method": "thread/read", "id": 19, "params": { "threadId": "thr_123" } }
{ "id": 19, "result": { "thread": { "id": "thr_123", "name": "Bug bash notes", "ephemeral": false, "status": { "type": "notLoaded" }, "turns": [] } } }
```

与 `thread/resume` 不同，`thread/read` 不会将聊天加载到内存中，也不会发出 `thread/started`。

### 列出聊天轮次

使用 `thread/turns/list` 分页获取已存储聊天的轮次历史记录，无需恢复聊天。结果默认按从新到旧的顺序排列，因此客户端可以通过 `nextCursor` 获取更早的轮次。响应还包含 `backwardsCursor`；将其作为 `cursor` 传入，并使用相反的 `sortDirection` 即可反向分页。此时会再次包含锚点轮次，以便获取该轮次的更新。

`itemsView` 控制响应包含多少轮次条目数据：

- `notLoaded` 省略条目。
- `summary` 返回汇总后的条目数据，并且在省略时为默认值。
- `full` 返回完整的条目数据。

```json
{ "method": "thread/turns/list", "id": 20, "params": {
  "threadId": "thr_123",
  "limit": 50,
  "sortDirection": "desc",
  "itemsView": "summary"
} }
{ "id": 20, "result": {
  "data": [],
  "nextCursor": "older-turns-cursor-or-null",
  "backwardsCursor": "newer-turns-cursor-or-null"
} }
```

### 列出聊天条目

`thread/items/list` 可分页获取已持久化的条目，无需
恢复聊天。传入 `turnId` 可将结果限制在一个轮次内，省略它则
可分页获取整个聊天的条目。结果默认按从旧到新的顺序排列
（`sortDirection: "asc"`）。当前聊天存储必须支持条目分页；
否则，服务器会返回不支持该方法的错误。

传入先前响应中的不透明游标 `nextCursor` 即可继续分页。要
从某个已知条目之后开始，请传入条目锚点和非空的 `turnId`：

```json
{ "method": "thread/items/list", "id": 21, "params": {
  "threadId": "thr_123",
  "turnId": "turn_456",
  "cursor": { "type": "item", "itemId": "item_123" },
  "sortDirection": "asc",
  "limit": 50
} }
{ "id": 21, "result": {
  "data": [],
  "nextCursor": null,
  "backwardsCursor": null
} }
```

使用条目锚点时，结果不包含锚点本身：升序返回较新的条目，
降序返回较早的条目。该条目必须属于
所请求轮次的可见历史记录。缺少 `turnId`、条目 ID 为空，或
条目未知或超出范围时，都会返回参数无效错误（`-32602`）。使用
返回的字符串 `nextCursor` 继续分页。每个结果条目包含 `turnId`、`item`，
以及可选的已记录开始和完成时间戳。

### 列出聊天（支持分页和筛选）

`thread/list` 可用于呈现历史记录 UI。结果默认按 `createdAt` 从新到旧排序。筛选会在分页之前应用。可传入以下任意组合：

- `cursor` - 上一次响应中的不透明字符串；第一页应省略。
- `limit` - 未设置时，服务器默认为合理的页大小。
- `sortKey` - `created_at`（默认）、`updated_at` 或 `recency_at`。
- `sortDirection` - `desc`（默认）或 `asc`。
- `modelProviders` - 将结果限定为特定提供商；未设置、为 null 或为空数组时包含所有提供商。
- `sourceKinds` - 将结果限定为特定聊天来源。省略或为 `[]` 时，服务器默认仅包含交互式来源：`cli` 和 `vscode`。
- `archived` - 为 `true` 时，仅列出已归档聊天。为 `false` 或省略时，列出未归档聊天（默认）。
- `isPinned` - 提供时，仅返回持久化置顶状态匹配的聊天。省略时同时返回已置顶和未置顶聊天。
- `cwd` - 将结果限定为会话当前工作目录与此路径或数组中的某个路径完全匹配的聊天。相对路径从 app-server 进程的工作目录解析。
- `useStateDbOnly` - 为 `true` 时，返回状态数据库结果，而不扫描 JSONL 聊天日志来修复元数据。省略或传入 `false` 时，使用默认的扫描并修复行为。
- `searchTerm` - 将结果限定为提取出的标题包含此区分大小写文本片段的聊天。
- `parentThreadId` - 将结果限定为给定父聊天的直接子聊天。此筛选条件是实验性的，需要 `capabilities.experimentalApi = true`。
- `ancestorThreadId` - 将结果限定为给定聊天任意深度的衍生后代。此筛选条件是实验性的，需要 `capabilities.experimentalApi = true`；请勿将其与 `parentThreadId` 组合使用。

`sourceKinds` 接受以下值：

- `cli`
- `vscode`
- `exec`
- `appServer`
- `subAgent`
- `subAgentReview`
- `subAgentCompact`
- `subAgentThreadSpawn`
- `subAgentOther`
- `unknown`

示例：

```json
{ "method": "thread/list", "id": 20, "params": {
  "cursor": null,
  "limit": 25,
  "sortKey": "created_at"
} }
{ "id": 20, "result": {
  "data": [
    { "id": "thr_a", "preview": "Create a TUI", "ephemeral": false, "isPinned": true, "modelProvider": "openai", "createdAt": 1730831111, "updatedAt": 1730831111, "name": "TUI prototype", "status": { "type": "notLoaded" } },
    { "id": "thr_b", "preview": "Fix tests", "ephemeral": false, "isPinned": false, "modelProvider": "openai", "createdAt": 1730750000, "updatedAt": 1730750000, "status": { "type": "notLoaded" } }
  ],
  "nextCursor": "opaque-token-or-null"
} }
```

当 `nextCursor` 为 `null` 时，表示已到达最后一页。

### 更新已存储聊天的元数据

使用 `thread/metadata/update` 修补已存储聊天的元数据，而不恢复
聊天。设置 `isPinned` 可置顶或取消置顶聊天，更新 `gitInfo` 可更改
持久化的 Git 元数据。省略的字段保持不变；显式传入 `null` 会清除
已存储的 Git 元数据值。

```json
{ "method": "thread/metadata/update", "id": 21, "params": {
  "threadId": "thr_123",
  "isPinned": true,
  "gitInfo": { "branch": "feature/sidebar-pr" }
} }
{ "id": 21, "result": {
  "thread": {
    "id": "thr_123",
    "isPinned": true,
    "gitInfo": { "sha": null, "branch": "feature/sidebar-pr", "originUrl": null }
  }
} }
```

### 跟踪聊天状态变化

已加载聊天的运行时状态发生变化时会发出 `thread/status/changed`。有效载荷包含 `threadId` 和新的 `status`。

```json
{
  "method": "thread/status/changed",
  "params": {
    "threadId": "thr_123",
    "status": { "type": "active", "activeFlags": ["waitingOnApproval"] }
  }
}
```

### 列出已加载聊天

`thread/loaded/list` 返回当前已加载到内存中的聊天 ID。

```json
{ "method": "thread/loaded/list", "id": 21 }
{ "id": 21, "result": { "data": ["thr_123", "thr_456"] } }
```

### 取消订阅已加载聊天

`thread/unsubscribe` 会移除当前连接对聊天的订阅。响应状态为以下值之一：

- 连接之前已订阅且现已移除时为 `unsubscribed`。
- 连接未订阅该聊天时为 `notSubscribed`。
- 聊天未加载时为 `notLoaded`。

如果这是最后一个订阅者，服务器会让聊天保持加载，直到该聊天 30 分钟内既无订阅者也无活动。宽限期到期后，app-server 会卸载该聊天，并且发出一个到 `notLoaded` 的 `thread/status/changed` 转换以及 `thread/closed`。

```json
{ "method": "thread/unsubscribe", "id": 22, "params": { "threadId": "thr_123" } }
{ "id": 22, "result": { "status": "unsubscribed" } }
```

如果聊天稍后过期：

```json
{ "method": "thread/status/changed", "params": {
    "threadId": "thr_123",
    "status": { "type": "notLoaded" }
} }
{ "method": "thread/closed", "params": { "threadId": "thr_123" } }
```

### 归档聊天

使用 `thread/archive` 将持久化的聊天日志（以 JSONL 文件形式存储在磁盘上）移入已归档会话目录。归档聊天时，还会尝试归档尚未归档的衍生后代聊天。

```json
{ "method": "thread/archive", "id": 22, "params": { "threadId": "thr_b" } }
{ "id": 22, "result": {} }
{ "method": "thread/archived", "params": { "threadId": "thr_b" } }
{ "method": "thread/archived", "params": { "threadId": "thr_child" } }
```

除非传入 `archived: true`，否则已归档聊天不会出现在后续的 `thread/list` 调用中。服务器会为实际归档的每个聊天发出一条 `thread/archived` 通知；如果某个衍生后代无法归档，请求仍可能成功，但不会为该后代发出归档通知。

### 删除聊天

使用 `thread/delete` 可永久删除已持久化的活跃或已归档聊天
及其派生的后代聊天。服务器会先移除现有的 rollout 文件和
关联元数据，然后再返回成功；缺失的 rollout 文件会被视为
已经删除。临时根聊天无法删除。

```json
{ "method": "thread/delete", "id": 23, "params": { "threadId": "thr_b" } }
{ "id": 23, "result": {} }
{ "method": "thread/deleted", "params": { "threadId": "thr_b" } }
{ "method": "thread/deleted", "params": { "threadId": "thr_child" } }
```

### 取消归档聊天

使用 `thread/unarchive` 可将已归档聊天的 rollout 移回活跃会话目录。

```json
{ "method": "thread/unarchive", "id": 24, "params": { "threadId": "thr_b" } }
{ "id": 24, "result": { "thread": { "id": "thr_b", "name": "Bug bash notes" } } }
{ "method": "thread/unarchived", "params": { "threadId": "thr_b" } }
```

### 触发聊天压缩

使用 `thread/compact/start` 可手动触发聊天的历史记录压缩。请求会立即返回 `{}`。

App-server 会在同一 `threadId` 上通过标准 `turn/*` 和 `item/*` 通知发送进度，其中包括 `contextCompaction` 项的生命周期（先是 `item/started`，然后是 `item/completed`）。

```json
{ "method": "thread/compact/start", "id": 25, "params": { "threadId": "thr_b" } }
{ "id": 25, "result": {} }
```

### 在聊天中运行 shell 命令

对于属于某个聊天、由用户发起的 shell 命令，请使用 `thread/shellCommand`。请求会立即返回 `{}`，进度则通过标准 `turn/*` 和 `item/*` 通知流式传输。

此 API 在沙箱外运行，拥有完整访问权限，并且不会继承聊天的沙箱策略。客户端应仅针对用户明确发起的命令提供此功能。

如果聊天已有活跃的轮次，该命令会作为该轮次的辅助操作运行，其格式化输出将注入该轮次的消息流。如果聊天处于空闲状态，app-server 会为该 shell 命令启动一个独立轮次。

设置 `timeoutMs` 可限制执行时间（以毫秒为单位）。省略该参数或传入
`null` 时使用默认的一小时。`0` 表示请求立即超时；负
值会被拒绝。超时设置不会延迟即时 RPC 确认。

```json
{ "method": "thread/shellCommand", "id": 26, "params": { "threadId": "thr_b", "command": "git status --short", "timeoutMs": 10000 } }
{ "id": 26, "result": {} }
```

### 清理后台终端

使用 `thread/backgroundTerminals/clean` 可停止与某个聊天关联的所有正在运行的后台终端。此方法为实验性方法，需要 `capabilities.experimentalApi = true`。

```json
{ "method": "thread/backgroundTerminals/clean", "id": 27, "params": { "threadId": "thr_b" } }
{ "id": 27, "result": {} }
```

使用 `thread/backgroundTerminals/list` 可检查已加载聊天中正在运行的后台终端。
请求支持标准的 `cursor` 和 `limit` 分页，返回的 `processId` 是
app-server 的进程 ID。此方法为实验性方法，需要 `capabilities.experimentalApi = true`：

```json
{ "method": "thread/backgroundTerminals/list", "id": 28, "params": { "threadId": "thr_b" } }
{ "id": 28, "result": { "data": [
  {
    "itemId": "item_456",
    "processId": "42",
    "command": "python3 -m http.server",
    "cwd": "/workspace",
    "osPid": null,
    "cpuPercent": null,
    "rssKb": null
  }
], "nextCursor": null } }
```

使用 `thread/backgroundTerminals/terminate` 并传入该 `processId`，可停止一个
后台终端。此方法为实验性方法，需要
`capabilities.experimentalApi = true`：

```json
{ "method": "thread/backgroundTerminals/terminate", "id": 29, "params": { "threadId": "thr_b", "processId": "42" } }
{ "id": 29, "result": { "terminated": true } }
```

### 回退对话历史记录

使用 `thread/revert` 可从持久化分页聊天的对话历史记录中移除 `beforeTurnId`
及其之后的所有轮次。这不会还原本地
文件更改。如果聊天尚未加载，请先恢复聊天。不支持临时聊天
和使用旧版历史记录的聊天。

```json
{ "method": "thread/revert", "id": 30, "params": { "threadId": "thr_b", "beforeTurnId": "turn_456" } }
{ "id": 30, "result": {
  "thread": { "id": "thr_b", "ephemeral": false, "turns": [] },
  "turnsBackwardsCursor": "retained-turn-cursor-or-null",
  "itemsBackwardsCursor": "retained-item-cursor-or-null"
} }
{ "method": "thread/reverted", "params": { "threadId": "thr_b" } }
```

返回的 `thread.turns` 始终为空。将返回的游标传给
`thread/turns/list` 或 `thread/items/list`，并指定 `sortDirection: "desc"`，即可加载
保留的历史记录，其中包含游标的锚点。

`thread/rollback` 已移除，调用时会返回未知方法错误。
较早保存的聊天中已有的回滚标记仍可读取。

## 轮次

`input` 字段接受一个条目列表：

- `{ "type": "text", "text": "Explain this diff" }`
- `{ "type": "image", "url": "https://.../design.png" }`
- `{ "type": "localImage", "path": "/tmp/screenshot.png" }`

你可以为每个轮次覆盖配置设置（模型、推理强度、`cwd`、沙箱策略、摘要）。指定后，这些设置会成为同一聊天中后续轮次的默认值。`outputSchema` 仅适用于当前轮次。对于 `sandboxPolicy.type = "externalSandbox"`，将 `networkAccess` 设为 `restricted` 或 `enabled`；对于 `workspaceWrite`，`networkAccess` 仍为布尔值。

对于 `turn/start.collaborationMode`，`settings.developer_instructions: null` 表示“使用所选模式的内置指令”，而不是清除模式指令。

### 沙箱读取权限（`ReadOnlyAccess`）

`sandboxPolicy` 支持显式的读取权限控制：

- `readOnly`：可选的 `access`（默认为 `{ "type": "fullAccess" }`，也可设为受限根目录）。
- `workspaceWrite`：可选的 `readOnlyAccess`（默认为 `{ "type": "fullAccess" }`，也可设为受限根目录）。

受限读取权限的结构：

```json
{
  "type": "restricted",
  "includePlatformDefaults": true,
  "readableRoots": ["/Users/me/shared-read-only"]
}
```

在 macOS 上，`includePlatformDefaults: true` 会为受限读取会话追加一组经过筛选的平台默认 Seatbelt 策略。这样可以提高工具兼容性，同时不会宽泛地允许访问整个 `/System`。

示例：

```json
{ "type": "readOnly", "access": { "type": "fullAccess" } }
```

```json
{
  "type": "workspaceWrite",
  "writableRoots": ["/Users/me/project"],
  "readOnlyAccess": {
    "type": "restricted",
    "includePlatformDefaults": true,
    "readableRoots": ["/Users/me/shared-read-only"]
  },
  "networkAccess": false
}
```

### 启动轮次

```json
{ "method": "turn/start", "id": 30, "params": {
  "threadId": "thr_123",
  "input": [ { "type": "text", "text": "Run tests" } ],
  "cwd": "/Users/me/project",
  "approvalPolicy": "unlessTrusted",
  "sandboxPolicy": {
    "type": "workspaceWrite",
    "writableRoots": ["/Users/me/project"],
    "networkAccess": true
  },
  "model": "gpt-6.1-sol",
  "effort": "medium",
  "summary": "concise",
  "personality": "friendly",
  "outputSchema": {
    "type": "object",
    "properties": { "answer": { "type": "string" } },
    "required": ["answer"],
    "additionalProperties": false
  }
} }
{ "id": 30, "result": { "turn": { "id": "turn_456", "status": "inProgress", "items": [], "error": null } } }
```

若要使用客户端所运行工具的输出来启动轮次，请传入 `toolOutput`，
其中包含非空的 `name`、可选的 `namespace`，以及作为字符串或
内容条目数组的 `output`。将 `input` 设置为空数组；不能将
`toolOutput` 与非空用户输入结合使用。

```json
{
  "method": "turn/start",
  "id": 31,
  "params": {
    "threadId": "thr_123",
    "input": [],
    "toolOutput": {
      "name": "run_tests",
      "namespace": null,
      "output": "All 42 tests passed."
    }
  }
}
```

该输出在对话中仍作为工具输出，并在通知和持久化历史记录中显示为
`functionCallOutput` 条目。如果常规轮次已在进行中，Codex 会将该输出加入该轮次的队列。

### 向聊天注入条目

使用 `thread/inject_items` 可将预先构建的 Responses API 条目追加到已加载聊天的提示词历史记录中，而无需启动用户轮次。这些条目会持久化到 rollout，并包含在后续模型请求中。

```json
{ "method": "thread/inject_items", "id": 31, "params": {
  "threadId": "thr_123",
  "items": [
    {
      "type": "message",
      "role": "assistant",
      "content": [{ "type": "output_text", "text": "Previously computed context." }]
    }
  ]
} }
{ "id": 31, "result": {} }
```

### 引导活跃轮次

使用 `turn/steer` 可向正在进行的活跃轮次追加更多用户输入。

- 包含 `expectedTurnId`；它必须与活跃轮次 ID 匹配。
- 如果聊天没有活跃轮次，请求将失败。
- `turn/steer` 不会发出新的 `turn/started` 通知。
- `turn/steer` 不接受轮次级覆盖项（`model`、`cwd`、`sandboxPolicy` 或 `outputSchema`）。

```json
{ "method": "turn/steer", "id": 32, "params": {
  "threadId": "thr_123",
  "input": [ { "type": "text", "text": "Actually focus on failing tests first." } ],
  "expectedTurnId": "turn_456"
} }
{ "id": 32, "result": { "turnId": "turn_456" } }
```

### 启动轮次（调用技能）

要显式调用技能，请在文本输入中包含 `$<skill-name>`，并在旁边添加一个 `skill` 输入条目。

```json
{ "method": "turn/start", "id": 33, "params": {
  "threadId": "thr_123",
  "input": [
    { "type": "text", "text": "$skill-creator Add a new skill for triaging flaky CI and include step-by-step usage." },
    { "type": "skill", "name": "skill-creator", "path": "/Users/me/.codex/skills/skill-creator/SKILL.md" }
  ]
} }
{ "id": 33, "result": { "turn": { "id": "turn_457", "status": "inProgress", "items": [], "error": null } } }
```

### 中断轮次

```json
{ "method": "turn/interrupt", "id": 31, "params": { "threadId": "thr_123", "turnId": "turn_456" } }
{ "id": 31, "result": {} }
```

成功后，该轮次将以 `status: "interrupted"` 状态结束。

## 评审

`review/start` 会为聊天运行 Codex 评审器，并流式传输评审条目。目标包括：

- `uncommittedChanges`
- `baseBranch`（与某个分支比较差异）
- `commit`（评审特定提交）
- `custom`（自由格式指令）

使用 `delivery: "inline"`（默认值）在现有聊天中运行评审。
如需单独的评审聊天，请调用 `thread/start`，然后在新聊天中运行内联
评审。

请求/响应示例：

```json
{ "method": "review/start", "id": 40, "params": {
  "threadId": "thr_123",
  "delivery": "inline",
  "target": { "type": "commit", "sha": "1234567deadbeef", "title": "Polish tui colors" }
} }
{ "id": 40, "result": {
  "turn": {
    "id": "turn_900",
    "status": "inProgress",
    "items": [
      { "type": "userMessage", "id": "turn_900", "content": [ { "type": "text", "text": "Review commit 1234567: Polish tui colors" } ] }
    ],
    "error": null
  },
  "reviewThreadId": "thr_123"
} }
```

`delivery: "detached"` 已弃用，会发出 `deprecationNotice`，且不
支持分页父聊天。如果单独的评审需要
现有对话历史记录，请使用 `thread/fork`，然后调用 `turn/start`
并传入评审指令。

Codex 会先流式传输常规的 `turn/started` 通知，然后发送一个带有 `enteredReviewMode` 项的 `item/started`：

```json
{
  "method": "item/started",
  "params": {
    "item": {
      "type": "enteredReviewMode",
      "id": "turn_900",
      "review": "current changes"
    }
  }
}
```

评审器完成后，服务器会发出 `item/started` 和 `item/completed`，其中包含带有最终评审文本的 `exitedReviewMode` 项：

```json
{
  "method": "item/completed",
  "params": {
    "item": {
      "type": "exitedReviewMode",
      "id": "turn_900",
      "review": "Looks solid overall..."
    }
  }
}
```

使用此通知在客户端中呈现评审器输出。

## 进程执行

`process/*` 是一个实验性的显式进程控制 API。它需要
`capabilities.experimentalApi = true`，并在 Codex 沙箱外运行。仅当你的客户端有意提供
不受沙箱保护的本地进程控制时，才使用它。

使用 `process/spawn` 启动进程并提供一个 `processHandle`，然后使用
该句柄发送 stdin、调整大小和终止请求。输出通过
`process/outputDelta` 通知流式传输，完成状态通过
`process/exited` 流式传输。

```json
{ "method": "process/spawn", "id": 48, "params": {
  "command": ["python3", "-m", "pytest", "-q"],
  "processHandle": "pytest-1",
  "cwd": "/Users/me/project",
  "tty": true
} }
{ "id": 48, "result": {} }
{ "method": "process/outputDelta", "params": {
  "processHandle": "pytest-1",
  "stream": "stdout",
  "deltaBase64": "Li4u"
} }
{ "method": "process/exited", "params": {
  "processHandle": "pytest-1",
  "exitCode": 0
} }
```

使用 `process/writeStdin` 并传入 `deltaBase64`、`closeStdin` 或两者来发送
输入。使用 `process/resizePty` 处理 PTY 大小调整事件，并使用 `process/kill`
终止正在运行的进程。

## 命令执行

`command/exec` 在服务器沙箱中运行单条命令（`argv` 数组），且不创建聊天。

```json
{ "method": "command/exec", "id": 50, "params": {
  "command": ["ls", "-la"],
  "cwd": "/Users/me/project",
  "sandboxPolicy": { "type": "workspaceWrite" },
  "timeoutMs": 10000
} }
{ "id": 50, "result": { "exitCode": 0, "stdout": "...", "stderr": "" } }
```

如果你已对服务器进程进行沙箱隔离，并希望 Codex 跳过自身的沙箱强制执行，请使用 `sandboxPolicy.type = "externalSandbox"`。对于外部沙箱模式，请将 `networkAccess` 设置为 `restricted`（默认）或 `enabled`。对于 `readOnly` 和 `workspaceWrite`，请使用上文所示的相同可选 `access` / `readOnlyAccess` 结构。

注意：

- 服务器会拒绝空的 `command` 数组。
- `sandboxPolicy` 接受与 `turn/start` 相同的结构（例如 `dangerFullAccess`、`readOnly`、`workspaceWrite`、`externalSandbox`）。
- 省略时，`timeoutMs` 会回退到服务器默认值。
- 对于由 PTY 支持的会话，请设置 `tty: true`；如果计划后续调用 `command/exec/write`、`command/exec/resize` 或 `command/exec/terminate`，请使用 `processId`。
- 设置 `streamStdoutStderr: true`，可在命令运行时接收 `command/exec/outputDelta` 通知。

### 读取管理员要求（`configRequirements/read`）

使用 `configRequirements/read` 可检查从 `requirements.toml` 和/或 MDM 加载的有效管理员要求。

```json
{ "method": "configRequirements/read", "id": 52, "params": {} }
{ "id": 52, "result": {
  "requirements": {
    "allowedApprovalPolicies": ["onRequest", "unlessTrusted"],
    "allowedSandboxModes": ["readOnly", "workspaceWrite"],
    "featureRequirements": {
      "personality": true,
      "unified_exec": false
    },
    "network": {
      "enabled": true,
      "allowedDomains": ["api.openai.com"],
      "allowUnixSockets": ["/tmp/example.sock"],
      "dangerouslyAllowAllUnixSockets": false
    }
  }
} }
```

未配置要求时，`result.requirements` 为 `null`。有关支持的键和值的详细信息，请参阅 [`requirements.toml`](/docs/config-file/config-reference#requirementstoml) 文档。

### Windows 沙箱设置（`windowsSandbox/setupStart`）

自定义 Windows 客户端可以异步触发沙箱设置，而不必阻塞启动检查。

```json
{ "method": "windowsSandbox/setupStart", "id": 53, "params": { "mode": "elevated" } }
{ "id": 53, "result": { "started": true } }
```

App-server 会在后台启动设置，稍后再发出完成通知：

```json
{
  "method": "windowsSandbox/setupCompleted",
  "params": { "mode": "elevated", "success": true, "error": null }
}
```

模式：

- `elevated` - 运行需要提升权限的 Windows 沙箱设置流程。
- `unelevated` - 运行旧版设置/预检流程。

## 文件系统

v2 文件系统 API 使用绝对路径。当文件或目录发生变化后，客户端需要使 UI 状态失效时，请使用 `fs/watch`。

```json
{ "method": "fs/watch", "id": 54, "params": {
  "watchId": "0195ec6b-1d6f-7c2e-8c7a-56f2c4a8b9d1",
  "path": "/Users/me/project/.git/HEAD"
} }
{ "id": 54, "result": { "path": "/Users/me/project/.git/HEAD" } }
{ "method": "fs/changed", "params": {
  "watchId": "0195ec6b-1d6f-7c2e-8c7a-56f2c4a8b9d1",
  "changedPaths": ["/Users/me/project/.git/HEAD"]
} }
{ "method": "fs/unwatch", "id": 55, "params": {
  "watchId": "0195ec6b-1d6f-7c2e-8c7a-56f2c4a8b9d1"
} }
{ "id": 55, "result": {} }
```

监视文件时，该文件路径会发出 `fs/changed`，其中包括通过替换或重命名操作产生的更新。

## 事件

事件通知是服务器发起的流，用于传输聊天生命周期、轮次生命周期及其中的条目。启动或恢复聊天后，请继续读取活跃传输流中的 `thread/started`、`thread/archived`、`thread/unarchived`、`thread/closed`、`thread/status/changed`、`turn/*`、`item/*` 和 `serverRequest/resolved` 通知。

### 选择不接收通知

客户端可以在 `initialize.params.capabilities.optOutNotificationMethods` 中发送准确的方法名称，按连接禁止特定通知。

- 仅精确匹配：`item/agentMessage/delta` 只会禁止该方法。
- 未知的方法名称将被忽略。
- 适用于当前的 `thread/*`、`turn/*`、`item/*` 及相关 v2 通知。
- 不适用于请求、响应或错误。

### 模糊文件搜索事件（实验性）

模糊文件搜索会话 API 会按查询发出通知：

- `fuzzyFileSearch/sessionUpdated` - `{ sessionId, query, files }`，包含活跃查询的当前匹配项。
- `fuzzyFileSearch/sessionCompleted` - 为该查询完成索引和匹配后发出一次 `{ sessionId }`。

### 警告事件

- `configWarning` - 针对可恢复的配置或初始化问题发出
  `{ summary, details?, path?, range? }`。
- `warning` - 针对非致命运行时警告发出 `{ threadId?, message }`。

### Windows 沙箱设置事件

- `windowsSandbox/setupCompleted` - 在 `windowsSandbox/setupStart` 请求完成后发出 `{ mode, success, error }`。

### 轮次事件

- `turn/started` - `{ turn }`，包含轮次 ID、空的 `items` 和 `status: "inProgress"`。
- `turn/completed` - `{ turn }`，其中 `turn.status` 为 `completed`、`interrupted` 或 `failed`；失败时会携带 `{ error: { message, codexErrorInfo?, additionalDetails? } }`。
- `turn/diff/updated` - `{ threadId, turnId, diff }`，包含该轮次所有文件更改的最新聚合统一差异。
- `turn/plan/updated` - 每当智能体共享或更改其计划时发出 `{ turnId, explanation?, plan }`；每个 `plan` 条目都是 `{ step, status }`，其中 `status` 为 `pending`、`inProgress` 或 `completed`。
- `hook/started` 和 `hook/completed` - 在同步生命周期钩子启动时以及其最终运行摘要可用时发出 `{ threadId, turnId?, run }`。异步钩子不会发出这些通知。
- `model/safetyBuffering/updated` - 响应进入暂时性安全缓冲时发出 `{ threadId, turnId, model, useCases, reasons, showBufferingUi, fasterModel }`。
- `model/rerouted` - 服务将请求路由到另一模型时发出 `{ threadId, turnId, fromModel, toModel, reason }`。
- `model/verification` - 服务要求进行额外账户验证时发出 `{ threadId, turnId, verifications }`。
- `thread/tokenUsage/updated` - 活跃聊天的用量更新。

即使条目事件以流式方式传输，`turn/diff/updated` 和 `turn/plan/updated` 目前仍包含空的 `items` 数组。请将 `item/*` 通知作为轮次条目的事实来源。

### 条目

`ThreadItem` 是轮次响应和 `item/*` 通知中携带的带标签联合类型。常见条目类型包括：

- `userMessage` - `{id, content}`，其中 `content` 是用户输入列表（`text`、`image` 或 `localImage`）。
- `functionCallOutput` - `{id, name, namespace, output}`，用于表示通过 `turn/start.toolOutput` 提供的独立工具输出。`namespace` 可以是 `null`。
- `agentMessage` - `{id, text, phase?}`，包含累积的智能体回复。若存在，`phase` 使用 Responses API 的传输协议值（`commentary`、`partial_answer`、`final_answer`）。`partial_answer` 是稳定的回答文本，其后可能还有更多输出或工具调用。
- `plan` - 包含规划模式下所提议计划文本的 `{id, text}`。应以 `item/completed` 中最后一个 `plan` 条目为准。
- `reasoning` - `{id, summary, content}`，其中 `summary` 保存流式推理摘要，`content` 保存原始推理块。
- `commandExecution` - `{id, command, cwd, status, commandActions, aggregatedOutput?, exitCode?, durationMs?}`。
- `fileChange` - 描述所提议编辑的 `{id, changes, status}`；`changes` 列出 `{path, kind, diff}`。
- `mcpToolCall` - `{id, server, tool, status, arguments, appContext?, pluginId?, result?, error?}`。对于受信任的 MCP 应用，`appContext` 可以包含 `connectorId`、`linkId`、`resourceUri`、`appName`、`templateId` 和稳定的连接器 `actionName`。较旧的持久化条目可能省略较新的元数据。请使用 `appContext.resourceUri`，而不是已弃用的顶层 `mcpAppResourceUri`。
- `dynamicToolCall` - 用于客户端执行的动态工具调用的 `{id, tool, arguments, status, contentItems?, success?, durationMs?}`。
- `collabToolCall` - `{id, tool, status, senderThreadId, receiverThreadId?, newThreadId?, prompt?, agentStatus?}`。
- `webSearch` - 用于智能体发出的 Web 搜索请求的 `{id, query, action?}`。
- `imageView` - 智能体调用图像查看器工具时发出的 `{id, path}`。
- `enteredReviewMode` - 评审器启动时发送的 `{id, review}`。
- `exitedReviewMode` - 评审器完成时发出的 `{id, review}`。
- `contextCompaction` - Codex 压缩对话历史记录时发出的 `{id}`。

对于 `webSearch.action`，操作 `type` 可以是 `search`（`query?`、`queries?`）、`openPage`（`url?`）或 `findInPage`（`url?`、`pattern?`）。

App server 已弃用旧版 `thread/compacted` 通知；请改用 `contextCompaction` 项。

所有条目都会发出两个共享生命周期事件：

- `item/started` - 新工作单元开始时发出完整的 `item`；`item.id` 与增量所用的 `itemId` 匹配。
- `item/completed` - 工作完成后发送最终的 `item`；应以此状态为准。

### 条目增量

- `item/agentMessage/delta` - 追加智能体消息的流式文本。
- `item/plan/delta` - 流式传输建议的计划文本。最终的 `plan` 项可能与拼接后的增量并不完全相同。
- `item/reasoning/summaryTextDelta` - 流式传输可读的推理摘要；打开新的摘要区段时，`summaryIndex` 会递增。
- `item/reasoning/summaryPartAdded` - 标记推理摘要区段之间的边界。
- `item/reasoning/textDelta` - 流式传输原始推理文本（模型支持时）。
- `item/commandExecution/outputDelta` - 流式传输命令的 stdout/stderr；按顺序追加增量。
- `item/fileChange/outputDelta` - 用于旧版 `apply_patch` 文本输出的已弃用兼容性通知。当前 app-server 版本不再发出此通知；请改用 `fileChange` 项和 `turn/diff/updated`。

## 错误

如果轮次失败，服务器会发出带有 `{ error: { message, codexErrorInfo?, additionalDetails? } }` 的 `error` 事件，然后以 `status: "failed"` 状态结束该轮次。如果上游 HTTP 状态可用，它会出现在 `codexErrorInfo.httpStatusCode` 中。

常见的 `codexErrorInfo` 值包括：

- `ContextWindowExceeded`
- `UsageLimitExceeded`
- `HttpConnectionFailed`（上游 4xx/5xx 错误）
- `ResponseStreamConnectionFailed`
- `ResponseStreamDisconnected`
- `ResponseTooManyFailedAttempts`
- `BadRequest`、`Unauthorized`、`SandboxError`、`InternalServerError`、`Other`

如果上游 HTTP 状态可用，服务器会通过相关 `codexErrorInfo` 变体中的 `httpStatusCode` 转发该状态。

## 审批

根据用户的 Codex 设置，命令执行和文件更改可能需要审批。App-server 会向客户端发送由服务器发起的 JSON-RPC 请求，客户端则以决策载荷响应。

- 命令执行决策：`accept`、`acceptForSession`、`decline`、`cancel` 或 `{ "acceptWithExecpolicyAmendment": { "execpolicy_amendment": ["cmd", "..."] } }`。
- 文件更改决策：`accept`、`acceptForSession`、`decline`、`cancel`。

- 请求包含 `threadId` 和 `turnId`——使用它们可将 UI 状态限定到活跃对话。
- 服务器会恢复或拒绝相关工作，并以 `item/completed` 结束该条目。

### 命令执行审批

消息顺序：

1. `item/started` 显示待处理的 `commandExecution` 项，其中包含 `command`、`cwd` 和其他字段。
2. `item/commandExecution/requestApproval` 包含 `itemId`、`threadId`、`turnId`、可选的 `reason`、可选的 `command`、可选的 `cwd`、可选的 `commandActions`、可选的 `proposedExecpolicyAmendment`、可选的 `networkApprovalContext` 以及可选的 `availableDecisions`。当 `initialize.params.capabilities.experimentalApi = true` 时，载荷还可以包含实验性的 `additionalPermissions`，用于描述请求的逐命令沙箱权限。`additionalPermissions` 内的所有文件系统路径在线上传输时均为绝对路径。
3. 客户端使用上述某个命令执行审批决策进行响应。
4. `serverRequest/resolved` 确认待处理请求已得到响应或已清除。
5. `item/completed` 返回最终的 `commandExecution` 项，其中包含 `status: completed | failed | declined`。

当存在 `networkApprovalContext` 时，该提示针对的是受管网络访问，而不是一般 shell 命令审批。当前 v2 数据结构会公开目标 `host` 和 `protocol`；客户端应呈现网络专用提示，不应依赖 `command` 作为对用户有意义的 shell 命令预览。

Codex 会按目标（`host`、协议和端口）对并发网络审批提示进行分组。因此，app-server 可能发送一个提示，解除对发往同一目标的多个排队请求的阻塞；而同一主机上的不同端口会被分别处理。

### 文件更改审批

消息顺序：

1. `item/started` 发出一个 `fileChange` 项，其中包含建议的 `changes` 和 `status: "inProgress"`。
2. `item/fileChange/requestApproval` 包含 `itemId`、`threadId`、`turnId`、可选的 `reason` 和可选的 `grantRoot`。
3. 客户端使用上述某个文件更改审批决策进行响应。
4. `serverRequest/resolved` 确认待处理请求已得到响应或已清除。
5. `item/completed` 返回最终的 `fileChange` 项，其中包含 `status: completed | failed | declined`。

### `tool/requestUserInput`

当客户端响应 `item/tool/requestUserInput` 时，app-server 会发出带有 `{ threadId, requestId }` 的 `serverRequest/resolved`。如果待处理请求在客户端响应前因轮次启动、轮次完成或轮次中断而被清除，服务器也会为该清理操作发出相同通知。

请求参数包含 `autoResolutionMs`（整数毫秒超时值）或
`null`。如果存在，且用户未作答，宿主客户端可以在该
时间间隔后自动处理提示。

### 权限请求

内置的 `request_permissions` 工具会发送
`item/permissions/requestApproval`，其中包含 `threadId`、`turnId`、`itemId`、
`environmentId`、`cwd`、可选的 `reason`，以及请求的网络或文件系统
权限。请使用 `permissions` 进行响应，其中仅包含授予的子集。
将 `scope` 设置为 `"session"`，可在同一会话的后续轮次中保留授权；
省略它或使用 `"turn"`，则授权仅限当前轮次。未请求的权限
将被忽略。

### MCP server 信息征询请求

MCP server 可以使用 `mcpServer/elicitation/request` 中断轮次。该
请求包含 `threadId`、可选的 `turnId`、`serverName`，以及以下
某种请求结构：

- `mode: "form"` 或 `mode: "openai/form"`，包含 `message` 和
  `requestedSchema`。
- `mode: "url"`，包含 `message`、`url` 和 `elicitationId`。

使用 `action: "accept"` 和请求的 `content` 进行响应，或使用
`action: "decline"` 或 `"cancel"` 以及 `content: null` 进行响应。随后 app-server 会发出
`serverRequest/resolved`。要接收 `openai/form` 变体，请通过
`initialize.params.capabilities.mcpServerOpenaiFormElicitation` 选择加入。

### 动态工具调用（实验性）

`thread/start` 上的 `dynamicTools` 以及相应的 `item/tool/call` 请求或响应流程均为实验性 API。

动态工具名称和命名空间名称必须遵循 Responses API 的命名
约束。请避免使用 Codex 内置工具所用的保留命名空间名称。

在轮次中调用动态工具时，app-server 会发出：

1. `item/started`，包含 `item.type = "dynamicToolCall"`、`status = "inProgress"`，以及 `tool` 和 `arguments`。
2. `item/tool/call`，作为服务器发送给客户端的请求。
3. 包含返回内容条目的客户端响应载荷。
4. `item/completed`，包含 `item.type = "dynamicToolCall"`、最终的 `status`，以及返回的任何 `contentItems` 或 `success` 值。

### MCP 工具调用审批（应用）

应用（连接器）工具调用也可能需要审批。当应用工具调用具有副作用时，服务器可能会通过 `tool/requestUserInput` 征求审批，并提供 **接受**、**拒绝** 和 **取消** 等选项。即使工具同时声明了权限较低的提示，破坏性工具注解也始终会触发审批。如果用户拒绝或取消，相关的 `mcpToolCall` 项将以错误状态完成，而不会运行该工具。

## 技能

在用户文本输入中包含 `$<skill-name>` 可调用技能。添加一个 `skill` 输入条目（推荐），这样服务器会注入完整的技能指令，而不是依赖模型解析名称。

```json
{
  "method": "turn/start",
  "id": 101,
  "params": {
    "threadId": "thread-1",
    "input": [
      {
        "type": "text",
        "text": "$skill-creator Add a new skill for triaging flaky CI."
      },
      {
        "type": "skill",
        "name": "skill-creator",
        "path": "/Users/me/.codex/skills/skill-creator/SKILL.md"
      }
    ]
  }
}
```

如果省略 `skill` 项，模型仍会解析 `$<skill-name>` 标记并尝试定位技能，这可能会增加延迟。

示例：

```
$skill-creator Add a new skill for triaging flaky CI and include step-by-step usage.
```

使用 `skills/list` 获取可用技能（可以通过带有 `forceReload` 的 `cwds` 限定范围）。你还可以包含 `perCwdExtraUserRoots`，将额外的绝对路径作为特定 `cwd` 值的 `user` 范围进行扫描。如果条目的 `cwd` 不在 `cwds` 中，app-server 会将其忽略。`skills/list` 可以按 `cwd` 复用缓存结果；将 `forceReload: true` 设置为从磁盘刷新。`SKILL.json` 存在时，服务器会从中读取 `interface` 和 `dependencies`。

```json
{ "method": "skills/list", "id": 25, "params": {
  "cwds": ["/Users/me/project", "/Users/me/other-project"],
  "forceReload": true,
  "perCwdExtraUserRoots": [
    {
      "cwd": "/Users/me/project",
      "extraUserRoots": ["/Users/me/shared-skills"]
    }
  ]
} }
{ "id": 25, "result": {
  "data": [{
    "cwd": "/Users/me/project",
    "skills": [
      {
        "name": "skill-creator",
        "description": "Create or update a Codex skill",
        "enabled": true,
        "interface": {
          "displayName": "Skill Creator",
          "shortDescription": "Create or update a Codex skill"
        },
        "dependencies": {
          "tools": [
            {
              "type": "env_var",
              "value": "GITHUB_TOKEN",
              "description": "GitHub API token"
            },
            {
              "type": "mcp",
              "value": "github",
              "transport": "streamable_http",
              "url": "https://example.com/mcp"
            }
          ]
        }
      }
    ],
    "errors": []
  }]
} }
```

受监视的本地技能文件发生变化时，服务器也会发出 `skills/changed` 通知。请将其视为失效信号，并在需要时使用当前参数重新运行 `skills/list`。

要按路径启用或禁用技能：

```json
{
  "method": "skills/config/write",
  "id": 26,
  "params": {
    "path": "/Users/me/.codex/skills/skill-creator/SKILL.md",
    "enabled": false
  }
}
```

## 应用（连接器）

使用 `app/installed` 可读取最新提交的已安装应用运行时快照。
每个结果都包含应用的 `id`、`runtimeName`（或 `null`）、有效的
`enabled` 状态以及 `callable` 状态。仅当有效
配置启用了应用，并且至少有一个对模型可见的工具符合应用和工具策略时，
该应用才可调用。

```json
{
  "method": "app/installed",
  "id": 49,
  "params": {
    "threadId": "thread-1",
    "forceRefresh": false
  }
}
{
  "id": 49,
  "result": {
    "apps": [
      {
        "id": "demo-app",
        "runtimeName": "Demo App",
        "enabled": true,
        "callable": true
      }
    ]
  }
}
```

省略 `threadId`，可使用全局配置而不是已加载聊天的
配置。将 `forceRefresh: true` 设置为在读取前刷新连接器运行时
快照。当全局或工作区策略阻止应用访问时，已观测到的应用仍可能出现，
其 `enabled` 和 `callable` 会被设置为 `false`。

使用 `app/list` 获取可用应用。在 CLI/TUI 中，`/apps` 是面向用户的选择器；在自定义客户端中，请直接调用 `app/list`。每个条目都同时包含 `isAccessible`（对用户可用）和 `isEnabled`（已在 `config.toml` 中启用），以便客户端区分安装/访问状态与本地启用状态。应用条目还可以包含可选的 `branding`、`appMetadata` 和 `labels` 字段。

```json
{ "method": "app/list", "id": 50, "params": {
  "cursor": null,
  "limit": 50,
  "threadId": "thread-1",
  "forceRefetch": false
} }
{ "id": 50, "result": {
  "data": [
    {
      "id": "demo-app",
      "name": "Demo App",
      "description": "Example connector for documentation.",
      "logoUrl": "https://example.com/demo-app.png",
      "logoUrlDark": null,
      "distributionChannel": null,
      "branding": null,
      "appMetadata": null,
      "labels": null,
      "installUrl": "https://chatgpt.com/apps/demo-app/demo-app",
      "isAccessible": true,
      "isEnabled": true
    }
  ],
  "nextCursor": null
} }
```

如果提供 `threadId`，应用功能门控（`features.apps`）会使用该聊天的配置快照。如果省略，app-server 会使用最新的全局配置。

`app/list` 会在可访问应用和目录应用都加载完成后返回。设置 `forceRefetch: true` 可绕过应用缓存并获取最新数据。只有刷新成功时，缓存条目才会被替换。

任一来源（可访问应用或目录应用）完成加载时，服务器也会发出 `app/list/updated` 通知。每条通知都包含最新合并的应用列表。

```json
{
  "method": "app/list/updated",
  "params": {
    "data": [
      {
        "id": "demo-app",
        "name": "Demo App",
        "description": "Example connector for documentation.",
        "logoUrl": "https://example.com/demo-app.png",
        "logoUrlDark": null,
        "distributionChannel": null,
        "branding": null,
        "appMetadata": null,
        "labels": null,
        "installUrl": "https://chatgpt.com/apps/demo-app/demo-app",
        "isAccessible": true,
        "isEnabled": true
      }
    ]
  }
}
```

当你已知应用 ID 并且需要应用元数据而不是已安装的运行时状态时，
请使用 `app/read`。最多传入 100 个 `appIds`。服务器仅保留
每个重复 ID 第一次出现的位置，并在 `apps` 和 `missingAppIds` 中
保留该顺序。未知或无法访问的应用会在 `missingAppIds` 中返回，
而不会导致整个请求失败。

```json
{
  "method": "app/read",
  "id": 52,
  "params": {
    "appIds": ["demo-app", "missing-app"],
    "includeTools": true
  }
}
{
  "id": 52,
  "result": {
    "apps": [
      {
        "id": "demo-app",
        "name": "Demo App",
        "description": "Example connector for documentation.",
        "iconUrl": null,
        "iconUrlDark": null,
        "distributionChannel": null,
        "installUrl": null,
        "pluginDisplayNames": [],
        "toolSummaries": [
          {
            "name": "search",
            "title": "Search",
            "description": "Search the app.",
            "isEnabled": true,
            "disabledReason": null,
            "isReadOnly": true
          }
        ]
      }
    ],
    "missingAppIds": ["missing-app"]
  }
}
```

设置 `includeTools: true` 可请求仅供显示的公开工具摘要。该
元数据响应不包含已安装应用的运行时状态，也不会授权
工具调用；请使用 `app/installed` 检查有效的 `enabled` 和 `callable`
状态。

要调用应用，请在文本输入中插入 `$<app-slug>`，并添加一个包含 `app://<id>` 路径的 `mention` 输入条目（推荐）。

```json
{
  "method": "turn/start",
  "id": 51,
  "params": {
    "threadId": "thread-1",
    "input": [
      {
        "type": "text",
        "text": "$demo-app Pull the latest updates from the team."
      },
      {
        "type": "mention",
        "name": "Demo App",
        "path": "app://demo-app"
      }
    ]
  }
}
```

### 应用设置的配置 RPC 示例

使用 `config/read`、`config/value/write` 和 `config/batchWrite` 可检查或更新 `config.toml` 中的应用控制项。

读取有效的应用配置结构（包括 `_default` 和逐工具覆盖项）：

```json
{ "method": "config/read", "id": 60, "params": { "includeLayers": false } }
{ "id": 60, "result": {
  "config": {
    "apps": {
      "_default": {
        "enabled": true,
        "destructive_enabled": true,
        "open_world_enabled": true,
        "approvals_reviewer": "user",
        "default_tools_approval_mode": "auto"
      },
      "google_drive": {
        "enabled": true,
        "destructive_enabled": false,
        "approvals_reviewer": "auto_review",
        "default_tools_approval_mode": "prompt",
        "tools": {
          "files/delete": { "enabled": false, "approval_mode": "approve" }
        }
      }
    }
  }
} }
```

除非逐应用值将其覆盖，否则 `apps._default.approvals_reviewer` 会为所有应用设置评审器。如果两者都省略，应用会继承顶层的 `approvals_reviewer` 值。`apps._default.default_tools_approval_mode` 会为没有逐应用或逐工具覆盖项的工具设置回退审批模式。受管审批模式要求会覆盖工具审批模式设置。

更新单个应用设置：

```json
{
  "method": "config/value/write",
  "id": 61,
  "params": {
    "keyPath": "apps.google_drive.default_tools_approval_mode",
    "value": "prompt",
    "mergeStrategy": "replace"
  }
}
```

以原子方式应用多项应用编辑：

```json
{
  "method": "config/batchWrite",
  "id": 62,
  "params": {
    "edits": [
      {
        "keyPath": "apps._default.destructive_enabled",
        "value": false,
        "mergeStrategy": "upsert"
      },
      {
        "keyPath": "apps.google_drive.tools.files/delete.approval_mode",
        "value": "approve",
        "mergeStrategy": "upsert"
      }
    ]
  }
}
```

### 检测并导入外部智能体配置

使用 `externalAgentConfig/detect` 可发现能够迁移的外部智能体产物，然后将选定条目传递给 `externalAgentConfig/import`。

检测示例：

```json
{ "method": "externalAgentConfig/detect", "id": 63, "params": {
  "includeHome": true,
  "cwds": ["/Users/me/project"]
} }
{ "id": 63, "result": {
  "items": [
    {
      "itemType": "AGENTS_MD",
      "description": "Import /Users/me/project/CLAUDE.md to /Users/me/project/AGENTS.md.",
      "cwd": "/Users/me/project"
    },
    {
      "itemType": "SKILLS",
      "description": "Copy skill folders from /Users/me/.claude/skills to /Users/me/.agents/skills.",
      "cwd": null
    }
  ]
} }
```

导入示例：

```json
{ "method": "externalAgentConfig/import", "id": 64, "params": {
  "migrationItems": [
    {
      "itemType": "AGENTS_MD",
      "description": "Import /Users/me/project/CLAUDE.md to /Users/me/project/AGENTS.md.",
      "cwd": "/Users/me/project"
    }
  ],
  "source": "claude-code"
} }
{ "id": 64, "result": { "importId": "8ae96ff3-3425-4f4c-8772-b6fd61502868" } }
```

可选的顶层 `source` 导入参数用于标记生成所选迁移项的
产品。

各条目类型完成时，服务器会发出 `externalAgentConfig/import/progress`；
所有同步和后台导入完成后，会发出 `externalAgentConfig/import/completed`。
这些通知包含响应中的同一个 `importId`，以及带有逐类型 `successes` 和 `failures` 的
`itemTypeResults`。完成通知可能紧随响应到达，也可能在后台远程
导入完成后到达。

```json
{ "method": "externalAgentConfig/import/progress", "params": {
  "importId": "8ae96ff3-3425-4f4c-8772-b6fd61502868",
  "itemTypeResults": [
    {
      "itemType": "AGENTS_MD",
      "successes": [
        { "itemType": "AGENTS_MD", "cwd": "/Users/me/project", "source": null, "target": "/Users/me/project/AGENTS.md" }
      ],
      "failures": []
    }
  ]
} }
{ "method": "externalAgentConfig/import/completed", "params": {
  "importId": "8ae96ff3-3425-4f4c-8772-b6fd61502868",
  "itemTypeResults": [
    {
      "itemType": "AGENTS_MD",
      "successes": [
        { "itemType": "AGENTS_MD", "cwd": "/Users/me/project", "source": null, "target": "/Users/me/project/AGENTS.md" }
      ],
      "failures": []
    }
  ]
} }
```

读取先前已完成的导入：

```json
{ "method": "externalAgentConfig/import/readHistories", "id": 65 }
{ "id": 65, "result": { "data": [
  {
    "importId": "8ae96ff3-3425-4f4c-8772-b6fd61502868",
    "completedAtMs": 1781784000000,
    "successes": [
      { "itemType": "AGENTS_MD", "cwd": "/Users/me/project", "source": null, "target": "/Users/me/project/AGENTS.md" }
    ],
    "failures": []
  }
] } }
```

支持的 `itemType` 值包括 `AGENTS_MD`、`CONFIG`、`SKILLS`、`PLUGINS`、
`MCP_SERVER_CONFIG`、`SUBAGENTS`、`HOOKS`、`COMMANDS` 和 `SESSIONS`。对于
`PLUGINS` 项，`details.plugins` 会列出每个 `marketplaceName` 以及
Codex 可以尝试迁移的 `pluginNames`。检测只返回仍有工作待完成的条目。
例如，当 `AGENTS.md` 已存在且非空时，Codex 会跳过 AGENTS 迁移；
技能导入也不会覆盖现有技能目录。

从 `.claude/settings.json` 检测插件时，Codex 会从
`extraKnownMarketplaces` 读取已配置的市场来源。如果 `enabledPlugins` 包含
来自 `claude-plugins-official` 的插件，但缺少市场来源，
Codex 会推断以 `anthropics/claude-plugins-official` 作为来源。

## 身份验证端点

<aside class="doc-callout doc-callout--note">
<div class="doc-callout__content">
<p>如果你使用 Codex app-server 身份验证构建了本地或开源应用，可以继续使用，但我们建议迁移到 Sign in with ChatGPT，让用户能够更好地掌控和了解自己的用量。请在<a href="https://developers.openai.com/siwc">此处</a>查看 Sign in with ChatGPT 的开发者文档，并在<a href="https://developers.openai.com/cookbook/articles/sign-in-with-chatgpt">此处</a>查看我们的实现指南。App-server 身份验证从未获准用于商业服务或托管服务。我们推出 Sign in with ChatGPT 来支持这些使用场景，并期待看到你构建的应用。请在<a href="https://openai.com/form/sign-in-with-chatgpt-interest/">此处</a>加入合作伙伴候补名单。</p>
</div>
</aside>

JSON-RPC 身份验证/账户接口提供请求/响应方法和服务器发起的通知（无 `id`）。使用这些接口可确定身份验证状态、启动或取消登录、退出登录、检查 ChatGPT 速率限制，以及在点数耗尽或达到用量限制时通知工作区所有者。

### 身份验证模式

Codex 支持以下身份验证模式。`account/updated.authMode` 会显示活跃模式，并在可用时包含当前 ChatGPT `planType`。`account/read` 还会报告账户和套餐详细信息。

- **API key（`apikey`）** - 调用方通过 `type: "apiKey"` 提供 OpenAI API key，Codex 会存储该密钥以用于 API 请求。
- **ChatGPT 托管（`chatgpt`）** - Codex 负责 ChatGPT OAuth 流程、持久化令牌并自动刷新。浏览器流程使用 `type: "chatgpt"` 启动，设备码流程使用 `type: "chatgptDeviceCode"` 启动。
- **ChatGPT 外部令牌（`chatgptAuthTokens`）** - 此功能为实验性功能，适用于已经负责用户 ChatGPT 身份验证生命周期的宿主应用。宿主应用直接提供 `accessToken`、`chatgptAccountId` 和可选的 `chatgptPlanType`，并且必须在收到请求时刷新令牌。
- **Amazon Bedrock** - `account/read` 将 Bedrock 账户报告为 `type: "amazonBedrock"`，并指明凭据来自 Codex 管理的 Bedrock API key（`credentialSource: "codexManaged"`）还是外部 AWS 凭据链（`credentialSource: "awsManaged"`）。`account/updated.authMode` 使用 `bedrockApiKey` 处理 Codex 管理的 Bedrock API key。

### API 概览

- `account/read` - 获取当前账户信息；可以选择刷新令牌。
- `account/login/start` - 开始登录（`apiKey`、`chatgpt`、`chatgptDeviceCode` 或实验性的 `chatgptAuthTokens`）。
- `account/login/completed`（通知）- 登录尝试完成（成功或出错）时发出。
- `account/login/cancel` - 通过 `loginId` 取消待处理的托管 ChatGPT 登录。
- `account/logout` - 退出登录；会触发 `account/updated`。
- `account/updated`（通知）- 身份验证模式发生变化时发出（`authMode`：`apikey`、`chatgpt`、`chatgptAuthTokens`、`agentIdentity`、`personalAccessToken`、`bedrockApiKey` 或 `null`），并在可用时包含 `planType`。
- `account/chatgptAuthTokens/refresh`（服务器请求）- 发生授权错误后，请求新的外部托管 ChatGPT 令牌。
- `account/rateLimits/read` - 获取 ChatGPT 速率限制。
- `account/rateLimits/updated`（通知）- 用户的 ChatGPT 速率限制发生变化时发出。
- `account/sendAddCreditsNudgeEmail` - 请求 ChatGPT 在点数耗尽或达到用量限制时向工作区所有者发送电子邮件。
- `account/rateLimitResetCredit/consume` - 使用调用方提供的 `idempotencyKey` 值消耗一次已获得的速率限制重置机会。
- `account/usage/read` - 获取 ChatGPT 账户token活动摘要和每日分桶。
- `account/workspaceMessages/read` - 获取活跃的工作区消息，包括可用的通知标题。
- `mcpServer/oauthLogin/completed`（通知）- `mcpServer/oauth/login` 流程完成后发出；载荷包含 `{ name, threadId, success, error? }`。对于应用范围或插件 OAuth 流程，`threadId` 可以是 `null`。
- `mcpServer/startupStatus/updated`（通知）- 已配置 MCP server 的启动状态发生变化时发出；载荷包含 `{ threadId, name, status, error, failureReason }`。对于应用范围的启动，`threadId` 为 `null`。启动失败时，`failureReason: "reauthenticationRequired"` 表示存储的 OAuth 凭据已过期且无法刷新，因此客户端应提供重新连接服务器的选项。

### 1）检查身份验证状态

请求：

```json
{ "method": "account/read", "id": 1, "params": { "refreshToken": false } }
```

响应示例：

```json
{ "id": 1, "result": { "account": null, "requiresOpenaiAuth": false } }
```

```json
{ "id": 1, "result": { "account": null, "requiresOpenaiAuth": true } }
```

```json
{
  "id": 1,
  "result": { "account": { "type": "apiKey" }, "requiresOpenaiAuth": true }
}
```

```json
{
  "id": 1,
  "result": {
    "account": {
      "type": "amazonBedrock",
      "credentialSource": "codexManaged"
    },
    "requiresOpenaiAuth": false
  }
}
```

```json
{
  "id": 1,
  "result": {
    "account": {
      "type": "amazonBedrock",
      "credentialSource": "awsManaged"
    },
    "requiresOpenaiAuth": false
  }
}
```

```json
{
  "id": 1,
  "result": {
    "account": {
      "type": "chatgpt",
      "email": "user@example.com",
      "planType": "pro"
    },
    "requiresOpenaiAuth": true
  }
}
```

字段说明：

- `refreshToken`（布尔值）：将 `true` 设置为强制在托管 ChatGPT 模式下刷新令牌。在外部令牌模式（`chatgptAuthTokens`）下，app-server 会忽略此标志。
- 当 ChatGPT 账户没有电子邮件地址时，`email` 为 `null`。
- `requiresOpenaiAuth` 反映活跃的提供商；当其为 `false` 时，Codex 无需 OpenAI 凭据即可运行。
- 当 Amazon Bedrock 使用由 Codex 管理的
  Bedrock API key 时，会报告 `credentialSource: "codexManaged"`。对于外部 AWS 凭据路径，
  它会报告 `credentialSource: "awsManaged"`。这用于标识所选的凭据
  来源，并不会验证 AWS 凭据链是否能够解析出
  凭据。

### 2）使用 API key 登录

1. 发送：

```json
   {
     "method": "account/login/start",
     "id": 2,
     "params": { "type": "apiKey", "apiKey": "sk-..." }
   }
```

2. 预期响应：

```json
   { "id": 2, "result": { "type": "apiKey" } }
```

3. 通知：

```json
   {
     "method": "account/login/completed",
     "params": { "loginId": null, "success": true, "error": null }
   }
```

```json
   {
     "method": "account/updated",
     "params": { "authMode": "apikey", "planType": null }
   }
```

### 3）使用 ChatGPT 登录（浏览器流程）

1. 启动：

```json
   {
     "method": "account/login/start",
     "id": 3,
     "params": {
       "type": "chatgpt",
       "useHostedLoginSuccessPage": true,
       "appBrand": "chatgpt"
     }
   }
```

   默认情况下，浏览器回调成功后会重定向到本地成功页面。
   如果不需要进行组织设置，请设置 `useHostedLoginSuccessPage: true` 以使用托管的成功页面。
   启用托管成功页面后，`appBrand` 可以是 `"codex"` 或 `"chatgpt"`；
   省略该值或设为 `null` 时，默认为
   `"codex"`。

```json
   {
     "id": 3,
     "result": {
       "type": "chatgpt",
       "loginId": "<uuid>",
       "authUrl": "https://chatgpt.com/...&redirect_uri=http%3A%2F%2Flocalhost%3A<port>%2Fauth%2Fcallback"
     }
   }
```

2. 在浏览器中打开 `authUrl`；app-server 会托管本地回调。
3. 等待通知：

```json
   {
     "method": "account/login/completed",
     "params": { "loginId": "<uuid>", "success": true, "error": null }
   }
```

```json
   {
     "method": "account/updated",
     "params": { "authMode": "chatgpt", "planType": "plus" }
   }
```

### 3b）使用 ChatGPT 登录（设备码流程）

如果客户端负责登录交互，或浏览器回调不稳定，请使用此流程。

1. 启动：

```json
   {
     "method": "account/login/start",
     "id": 4,
     "params": { "type": "chatgptDeviceCode" }
   }
```

```json
   {
     "id": 4,
     "result": {
       "type": "chatgptDeviceCode",
       "loginId": "<uuid>",
       "verificationUrl": "https://auth.openai.com/codex/device",
       "userCode": "ABCD-1234"
     }
   }
```

2. 向用户显示 `verificationUrl` 和 `userCode`；前端负责 UX。
3. 等待通知：

```json
   {
     "method": "account/login/completed",
     "params": { "loginId": "<uuid>", "success": true, "error": null }
   }
```

```json
   {
     "method": "account/updated",
     "params": { "authMode": "chatgpt", "planType": "plus" }
   }
```

### 3c）使用外部管理的 ChatGPT 令牌登录（`chatgptAuthTokens`）

仅当宿主应用负责用户的 ChatGPT 身份验证生命周期并直接提供令牌时，才使用此实验性模式。使用此登录类型之前，客户端必须在 `initialize` 期间设置 `capabilities.experimentalApi = true`。

1. 发送：

```json
   {
     "method": "account/login/start",
     "id": 7,
     "params": {
       "type": "chatgptAuthTokens",
       "accessToken": "<jwt>",
       "chatgptAccountId": "org-123",
       "chatgptPlanType": "business"
     }
   }
```

2. 预期响应：

```json
   { "id": 7, "result": { "type": "chatgptAuthTokens" } }
```

3. 通知：

```json
   {
     "method": "account/login/completed",
     "params": { "loginId": null, "success": true, "error": null }
   }
```

```json
   {
     "method": "account/updated",
     "params": { "authMode": "chatgptAuthTokens", "planType": "business" }
   }
```

服务器收到 `401 Unauthorized` 时，可能会向宿主应用请求刷新后的令牌：

```json
{
  "method": "account/chatgptAuthTokens/refresh",
  "id": 8,
  "params": { "reason": "unauthorized", "previousAccountId": "org-123" }
}
{ "id": 8, "result": { "accessToken": "<jwt>", "chatgptAccountId": "org-123", "chatgptPlanType": "business" } }
```

刷新响应成功后，服务器会重试原始请求。请求会在约 10 秒后超时。

### 4）取消 ChatGPT 登录

```json
{ "method": "account/login/cancel", "id": 4, "params": { "loginId": "<uuid>" } }
{ "method": "account/login/completed", "params": { "loginId": "<uuid>", "success": false, "error": "..." } }
```

### 5）退出登录

```json
{ "method": "account/logout", "id": 5 }
{ "id": 5, "result": {} }
{ "method": "account/updated", "params": { "authMode": null, "planType": null } }
```

### 6）速率限制（ChatGPT）

```json
{ "method": "account/rateLimits/read", "id": 6 }
{ "id": 6, "result": {
  "rateLimits": {
    "limitId": "codex",
    "limitName": null,
    "primary": { "usedPercent": 25, "windowDurationMins": 15, "resetsAt": 1730947200 },
    "secondary": null,
    "rateLimitReachedType": null
  },
  "rateLimitsByLimitId": {
    "codex": {
      "limitId": "codex",
      "limitName": null,
      "primary": { "usedPercent": 25, "windowDurationMins": 15, "resetsAt": 1730947200 },
      "secondary": null,
      "rateLimitReachedType": null
    },
    "codex_other": {
      "limitId": "codex_other",
      "limitName": "codex_other",
      "primary": { "usedPercent": 42, "windowDurationMins": 60, "resetsAt": 1730950800 },
      "secondary": null,
      "rateLimitReachedType": null
    }
  },
  "rateLimitResetCredits": {
    "availableCount": 2,
    "credits": [{
      "id": "RateLimitResetCredit_1",
      "resetType": "codexRateLimits",
      "status": "available",
      "grantedAt": 1781654400,
      "expiresAt": 1784246400,
      "title": "Rate-limit reset",
      "description": "Reset an eligible Codex rate-limit window."
    }]
  }
} }
{ "method": "account/rateLimits/updated", "params": {
  "rateLimits": {
    "limitId": "codex",
    "primary": { "usedPercent": 31, "windowDurationMins": 15, "resetsAt": 1730948100 }
  }
} }
```

字段说明：

- `rateLimits` 是向后兼容的单分桶视图。
- `rateLimitsByLimitId`（如果存在）是按计量的 `limit_id`（例如 `codex`）设键的多分桶视图。
- `limitId` 是计量分桶标识符。
- `limitName` 是分桶的可选用户可见标签。
- `usedPercent` 是配额窗口内的当前用量。
- `windowDurationMins` 是配额窗口长度。
- `resetsAt` 是下一次重置时间的 Unix 时间戳（秒）。
- 当服务器返回与分桶关联的 ChatGPT 套餐时，会包含 `planType`。
- 当服务器返回工作区剩余点数详情时，会包含 `credits`。
- 达到限制时，`rateLimitReachedType` 用于标识服务器分类的限制状态。
- 当服务提供可用的已获得重置次数时，`rateLimitResetCredits` 包含该次数；否则为 `null`。
- 当仅知道数量时，`rateLimitResetCredits.credits` 为 `null`。空数组表示服务已获取详情，但没有返回可用点数。服务可能会限制详细信息行数，因此应以 `availableCount` 为准。
- 每个详情行都包含不透明的 `id`、`resetType`、`status`、`grantedAt`、`expiresAt`（可以是 `null`）、`title`（可以是 `null`）和 `description`（可以是 `null`）。
- 消耗重置机会后，获取 `account/rateLimits/read`。

### 7）token 用量（ChatGPT）

使用 `account/usage/read` 获取 ChatGPT token活动摘要字段和
可选的每日分桶。

```json
{ "method": "account/usage/read", "id": 7 }
{ "id": 7, "result": {
  "summary": {
    "lifetimeTokens": 1234567,
    "peakDailyTokens": 45678,
    "longestRunningTurnSec": 540,
    "currentStreakDays": 8,
    "longestStreakDays": 14
  },
  "dailyUsageBuckets": [
    { "startDate": "2026-06-18", "tokens": 12345 }
  ]
} }
```

字段说明：

- 如果服务尚未返回相应指标，`summary` 值可能为 `null`。
- `dailyUsageBuckets` 可能为 `null`；如果存在，每个分桶都包含 `startDate` 和 `tokens`。
- 此端点需要由 Codex 服务支持的身份验证。支持 ChatGPT、
  外部 ChatGPT 令牌、智能体身份和个人访问令牌身份验证；
  仅使用 API key 和 Bedrock 身份验证则不支持。

### 8）已获得的速率限制重置机会（ChatGPT）

使用 `account/rateLimitResetCredit/consume` 可消耗一次已获得的重置机会。

```json
{ "method": "account/rateLimitResetCredit/consume", "id": 8, "params": { "idempotencyKey": "8ae96ff3-3425-4f4c-8772-b6fd61502868", "creditId": "RateLimitResetCredit_1" } }
{ "id": 8, "result": { "outcome": "reset" } }
```

字段说明：

- `idempotencyKey` 不得为空。为每次逻辑兑换尝试使用一个 UUID；重试同一次尝试时，请复用相同的值。
- `creditId` 是可选的。如果提供，它必须是来自 `account/rateLimits/read` 的非空不透明 ID。如果省略，服务会选择下一个可用点数。
- `reset` 表示已消耗一个点数。
- `alreadyRedeemed` 表示同一兑换之前已经完成。请将其视为幂等成功，并刷新账户限制。
- `nothingToReset` 表示没有符合条件的速率限制窗口可供重置。
- `noCredit` 表示账户没有可用的已获得重置机会。
- 消耗重置机会后，请获取 `account/rateLimits/read`，不要根据此响应推断更新后的窗口。

### 9）向工作区所有者发送限制通知

使用 `account/sendAddCreditsNudgeEmail` 可请求 ChatGPT 在点数耗尽或达到用量限制时向工作区所有者发送电子邮件。

```json
{ "method": "account/sendAddCreditsNudgeEmail", "id": 9, "params": { "creditType": "credits" } }
{ "id": 9, "result": { "status": "sent" } }
```

工作区点数耗尽时使用 `creditType: "credits"`，达到工作区用量限制时使用 `creditType: "usage_limit"`。如果最近已经通知过所有者，响应状态为 `cooldown_active`。

### 10）工作区消息（ChatGPT）

使用 `account/workspaceMessages/read` 获取当前工作区的活跃消息，
包括可用的通知标题。

```json
{ "method": "account/workspaceMessages/read", "id": 10 }
{ "id": 10, "result": { "featureEnabled": true, "messages": [
  { "messageId": "msg_123", "messageType": "headline", "messageBody": "Workspace maintenance starts at 5pm.", "createdAt": 1781395200, "archivedAt": null }
] } }
```
# 08 MCP 集成

> 本页覆盖：MCP 服务器配置、OAuth 认证、工具曝光控制、资源读取、权限与扩展/SDK 集成。Pi 通过 stdio 或 streamable HTTP 连接 [MCP](https://modelcontextprotocol.io) 服务器，把其工具与资源交给模型。

## mcp.md — MCP 服务器

> 原文存档：[source/mcp.md](source/mcp.md)

### 快速上手

```bash
# 本地 stdio 服务器
pi mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem .
pi mcp list
pi

# 远程 HTTP 服务器
pi mcp add docs --url https://example.com/mcp --bearer-token-env-var DOCS_TOKEN

# 写项目配置（-l/--local），env 可插值环境变量
pi mcp add -l tools --env API_KEY='${TOOLS_KEY}' -- uvx tools-mcp
```

- 默认写入用户级 `~/.pi/agent/mcp.json`；`--local` 写项目级 `.pi/mcp.json`（需项目信任后读取）。项目条目替换同名用户条目。
- 会话内用 `/mcp` 查看/登录/重连/改曝光/启停；会话外改配置后 `/reload`。
- shell 命令（无会话）：`pi mcp add/remove/list/login/logout`——**不加载扩展**，只看到文件配置的服务器。

### 配置格式

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    },
    "docs": {
      "url": "https://example.com/mcp",
      "headers": { "Authorization": "Bearer ${DOCS_TOKEN}" },
      "description": "Search and read the product documentation"
    }
  }
}
```

- **stdio**：`command`（单个可执行，非 shell 字符串）+ `args` + `env` + `cwd`（相对路径按会话目录解析；`~/` 指家目录）。
- **HTTP**：`url` + `headers` + `oauth`；**不支持 legacy SSE**（用 `sse` 会报错——很多文档 SSE 端点其实同时提供 streamable HTTP，常在 `/mcp`）。
- 两者通用：`timeout`（秒，默认 60，进度通知重置）、`enabled: false`、`exposure`/`toolExposure`、`description`（一句话说明服务器提供什么，进系统提示词与 tool_search 排序）。
- **规则**：服务器名只能含字母/数字/`_`/`-`；工具名为 `mcp__<server>__<tool>`（非法字符变 `_`，碰撞加哈希后缀）；仅 `-`/`_` 有别的同名算同一服务器（拒绝第二个）；`type` 可选（`stdio`/`http`/`streamable-http`）；`env`/`headers` 值支持 `${ENV_VAR}` 与整值 `!command`；非法条目跳过并报告，不影响其他服务器连接。
- **只覆盖启停/曝光的项目条目**：无 `command`/`url`/`type` 时只覆盖 `enabled`/`exposure`/`toolExposure`，保留 env/headers/auth 等——例如在某项目里关掉用户级服务器：`{"mcpServers": {"internal-tools": { "enabled": false }}}`。

### 连接行为与诊断

- 会话启动时后台连接所有启用服务器；`direct` 工具的服务器首条 prompt 最多等 10 秒（必须声明进请求）；其余按需等待（codemode 脚本等它点名的服务器；`searchTools()`/`ALL_TOOLS`/`tool_search`/资源工具等全部）。
- HTTP 瞬时错误（408/429/5xx）重试两次；断连下次调用自动重连；工具列表变化时新增工具、撤回工具不可达。
- 停 stdio 服务器：关 stdin → SIGTERM → 5 秒后 SIGKILL 进程组（能连带停掉 npx/uvx 包装的进程）。
- 诊断：`pi mcp list` 连接所有启用服务器并打印状态/工具/错误（有非法条目或未连接则退出码 1）；`/mcp` 显示完整连接错误与 stderr 尾部。启动后一次性报告配置错误/连接失败/需登录。日志追加 `~/.pi/agent/mcp.log`（超 5MB 轮转 mcp.log.1）。

### 迁移配置

| 来源 | 转换 |
| --- | --- |
| Claude Desktop / Claude Code / Cursor | 直接复制 `mcpServers` 条目 |
| VS Code | 从顶层 `servers` 移入，`${input:...}` 换成 `${NAME}` 环境变量 |
| Codex | `[mcp_servers.<name>]` TOML 的 command/args/env/url 转 JSON |
| OpenCode | `"type":"local"` → stdio 条目（拆分 command 数组、`environment`→`env`、`{env:NAME}`→`${NAME}`）；`"type":"remote"` → URL 条目 |

### OAuth 认证

远程 OAuth 服务器（如 Sentry）无需在 mcp.json 存凭据，`/mcp` 提示需登录时选 Sign in、`/mcp login sentry` 或 `pi mcp login sentry`；浏览器在别的机器（SSH）时粘贴重定向 URL。新凭据下个 turn 生效。

- 令牌存 `~/.pi/agent/mcp-auth.json`，过期或服务器拒绝时自动刷新；需要额外 scope 时再次登录；登出删除凭据。
- 凭据绑定"服务器名 + URL"：同名同 URL 的 mcp.json 共享一次登录。
- 不支持动态客户端注册的服务器可配置 `oauth.clientId` + `clientSecret` + `callbackPort`（重定向 `http://127.0.0.1:<port>/callback`；`callbackUrl` 自定义须 HTTP 且 localhost/127.0.0.1/[::1]）；`scope` 空格分隔；`clientName` 指定注册名（如某些服务器只认 "Claude Code"）；`clientRegistration`: `auto`（默认）/`dcr`（总是注册，登录页报 invalid client 时用）/`cimd`（总用文档）；`authServerMetadataUrl` 纠正广告错误的授权服务器（只指向可信文档，须 HTTPS）。

### 工具曝光控制

每个服务器工具注册为 `mcp__<server>__<tool>`，服务器 `exposure` 决定模型如何触达：

| Exposure | 行为 | 典型用途 |
| --- | --- | --- |
| `codemode`（默认） | 可从 codemode 脚本调用，但不声明给模型、不进 codemode 描述；脚本用 `searchTools()`/`describeTool()`/`ALL_TOOLS` 找工具 | 通用 MCP 服务器，脚本组合/过滤调用 |
| `deferred` | 直到 `tool_search` 为下一次模型调用加载匹配才声明 | 大服务器，发现后直接调用 |
| `direct` | 像内置工具一样声明给模型，也可被 codemode 调用 | 小且常用的工具集 |
| `hidden` | 注册但不可达 | 保持不可用的服务器/工具 |

- `toolExposure` 按工具覆盖：精确名或 `*` 通配模式，精确名优先、模式首匹配胜；hidden 服务器可只暴露选中工具。
- codemode/deferred 工具的服务器列在系统提示词 `mcp_servers` 段（含触达方式+description 一行）；连接后摘要变化时追加新段（不改工具声明，保持前文缓存）。
- 自动激活：服务器 `codemode` 曝光→激活 `codemode` 工具；`deferred`→激活 `tool_search`。`defaultTools: ["+codemode"]` 保活 codemode；`autoEnableCodemode: false` 禁自动激活；`--tools`/`--exclude-tools` 支持 `mcp__radius__*` 模式；`--no-mcp` 单次禁用。
- 大文本：20KB 以上结果去中段（`…N chars truncated…` 标记），全文存临时文件并指名路径；codemode 脚本拿完整 `CallToolResult`（content/structuredContent/isError），`image()` 转发图片块。

### 资源（Resources）

服务器提供资源时，Pi 增加资源工具：`list_mcp_resources`（列出资源，支持 `server` 分页与 `cursor`）、`list_mcp_resource_templates`（URI 模板）、`read_mcp_resource`（按 `server`+`uri` 读取，文本进模型、图片进模型、其他二进制存临时文件给路径；脚本拿 `{ server, uri, contents }`）。曝光取各服务器最宽者（direct > codemode/deferred）；`ui://` 或 `mcp-app` 资源不渲染被省略。

### 权限与扩展

- 所有 MCP 调用走 Pi 工具管线：扩展的 `tool_call`/`tool_result` 处理器（含权限门）对 MCP 工具生效；codemode 调用带 `parentToolCallId`。
- `pi.getAllTools()` 报告服务器声明的 annotations（readOnlyHint/destructiveHint/idempotentHint/openWorldHint），权限扩展可据此决定是否确认调用（见 07 页 Tool Exposure）。
- **扩展加服务器**：`pi.registerMcpServer(name, config)`（会话级，格式同 mcp.json 条目）；文件配置同名优先；`pi mcp` shell 命令看不到扩展注册的服务器。
- **替换内置 MCP**：装了注册 `/mcp` 的扩展（如 `pi-mcp-adapter`）即整体接管；`pi config` 里禁用 `mcp` 或 `"extensions": ["-builtin:mcp"]` 可关内置。
- **SDK**：SDK 会话不加载内置扩展，需自行把 MCP 扩展、codemode 扩展（codemode 服务器）、tool-search 扩展（deferred 服务器）加进资源加载器（见 09 页 sdk.md 的 Codemode and MCP）。

**相关页面**：[07-扩展与资源.md](07-扩展与资源.md) · [09-SDK与集成.md](09-SDK与集成.md) · [11-命令行.md](11-命令行.md)

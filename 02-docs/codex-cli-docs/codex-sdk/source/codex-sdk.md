# 原文存档元信息
- 来源 URL: https://www.codex-docs.com/docs/codex-sdk
- 抓取日期: 2026-10-31
- 原文语言: 中文（codex-docs.com 第三方整理的中文文档站）

---

<!-- normalized-upstream-mdx: inert-v1; never execute raw source -->

# Codex SDK

> 以编程方式控制本地 Codex 智能体

如果你通过 Codex CLI、IDE 扩展或 Codex 云端使用 Codex，也可以通过编程方式控制它。

当你需要执行以下操作时，可使用 SDK：

- 在 CI/CD 流水线中控制 Codex
- 创建自己的智能体，与 Codex 交互以执行复杂的工程任务
- 将 Codex 集成到自己的内部工具和工作流中
- 将 Codex 集成到自己的应用中

使用 Codex SDK 自动执行编码任务，包括 CI 中的作业。使用 [Codex 应用服务器](/docs/app-server)构建自定义客户端，以处理身份验证、对话历史记录、审批和流式智能体事件。

`codex mcp-server` 命令和独立的 `codex-mcp-server` 二进制文件已被移除。现有集成请改用 [Codex 应用服务器](/docs/app-server)。

如果你拥有测试版访问权限，并且需要扫描代码仓库或变更，以获取结构化的
安全发现和覆盖情况，请使用 [Codex Security TypeScript
SDK](/docs/security/sdk)。

## TypeScript 库

TypeScript 库可让你的应用启动、继续和恢复本地 Codex 线程。

请在服务端使用该库；它需要 Node.js 18 或更高版本。

### 安装

首先，使用 `npm` 安装 Codex SDK：

```bash
npm install @openai/codex-sdk
```

### 用法

创建一个 Codex 线程，并使用你的提示词运行它。

```ts


const codex = new Codex();
const thread = codex.startThread();
const result = await thread.run(
  "Make a plan to diagnose and fix the CI failures"
);

console.log(result.finalResponse);
```

再次调用 `run()` 可继续同一线程，也可以通过提供线程 ID 来恢复以前的线程。

```ts
// running the same thread
const result = await thread.run("Implement the plan");

console.log(result.finalResponse);

// resuming past thread

const threadId = "<thread-id>";
const thread2 = codex.resumeThread(threadId);
const result2 = await thread2.run("Pick up where you left off");

console.log(result2.finalResponse);
```

### 配置覆盖

传入 `config` 可设置结构化的 Codex 配置。对于无法
表示为点分路径的键，使用 `configOverrides` 将原始 TOML 字符串作为
独立的 `--config` 参数传入：

```ts
const codex = new Codex({
  config: { default_permissions: "audit" },
  configOverrides: [
    'permissions.audit.filesystem={":root"="read","/path/to/project/.env"="deny"}',
  ],
});
```

原始覆盖项优先于结构化的 `config`。SDK 会在之后应用
`baseUrl` 等受管设置以及线程专属选项，因此
这些设置和选项的优先级高于前两者。这些覆盖项不会更改 Codex 配置
文件。

更多详情，请参阅 [TypeScript 仓库](https://github.com/openai/codex/tree/main/sdk/typescript)。

## Python 库

Python SDK 通过 JSON-RPC 控制本地 Codex app-server。它需要 Python 3.10 或更高版本。已发布的 SDK 构建版本包含固定版本的 Codex CLI 运行时依赖项。

### 安装

运行以下命令安装 SDK：

```bash
pip install openai-codex
```

已发布的 SDK 构建版本会自动使用其固定版本的运行时。仅当你明确希望使用特定的本地 Codex 可执行文件运行时，才传入 `CodexConfig(codex_bin=...)`。

Python SDK 已提供稳定版。`pip install openai-codex`
会安装最新稳定版。使用 `pip install --pre openai-codex` 可选择
安装更新的预发布构建版本。

### 用法

启动 Codex，创建线程，然后运行提示词。示例使用 GPT-6.1 Sol，
你登录的账户必须有权使用该模型。否则，请省略 `model`，以
使用你配置的默认模型。请参阅[各套餐的 GPT-6.1 Sol 可用情况](/docs/models#gpt-6.1-sol)。

```python
from openai_codex import Codex, Sandbox
with Codex() as codex:
    thread = codex.thread_start(
        model="gpt-6.1-sol",
        sandbox=Sandbox.workspace_write,
    )
    result = thread.run("Make a plan to diagnose and fix the CI failures")
    print(result.final_response)
```

如果你的应用已采用异步方式，请使用 `AsyncCodex`：

```python
import asyncio
from openai_codex import AsyncCodex
async def main() -> None:
    async with AsyncCodex() as codex:
        thread = await codex.thread_start(model="gpt-6.1-sol")
        result = await thread.run("Implement the plan")
        print(result.final_response)
asyncio.run(main())
```

### 沙箱预设

创建线程或为后续轮次更改其文件系统访问权限时，使用同一组 `Sandbox`
预设：

```python
from openai_codex import Codex, Sandbox

with Codex() as codex:
    thread = codex.thread_start(sandbox=Sandbox.workspace_write)
    thread.run("Make the requested change.")
    review = thread.run("Review the diff only.", sandbox=Sandbox.read_only)
```

可用预设：

- `Sandbox.read_only`：允许读取文件，不允许写入。
- `Sandbox.workspace_write`：允许读取文件，并在工作区和配置的可写根目录内写入。
- `Sandbox.full_access`：运行时不限制文件系统访问。

省略 `sandbox=` 时，app-server 会使用配置的默认值。传给
`run(...)` 或 `turn(...)` 的沙箱设置会应用于当前轮次及该线程的后续
轮次。

更多详情，请参阅 [Python 仓库](https://github.com/openai/codex/tree/main/sdk/python)。
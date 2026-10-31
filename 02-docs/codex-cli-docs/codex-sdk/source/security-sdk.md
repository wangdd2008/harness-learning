# 原文存档元信息
- 来源 URL: https://www.codex-docs.com/docs/security/sdk
- 抓取日期: 2026-10-31
- 原文语言: 中文（codex-docs.com 第三方整理的中文文档站）

---

<!-- normalized-upstream-mdx: inert-v1; never execute raw source -->

# Codex Security TypeScript SDK

> 从 TypeScript 运行 Codex Security 扫描，选择目标和提供商，检查结果并管理扫描生命周期。

使用 Codex Security TypeScript SDK，可从你的应用程序或开发者工具中对仓库和
代码更改运行安全扫描。SDK 会返回类型化的
发现、覆盖范围详情和扫描产物路径。对于耗时较长的扫描，它
支持预检、成本限制、进度回调和取消操作。

SDK 使用 ECMAScript 模块（ESM），在服务端运行，支持 Node.js 24 或 26，或 22.13.0 及以上的 Node.js 22。扫描还需要 Python 3.10 或更高版本。
Python 3.10 还需要 `tomli` 软件包。

<aside class="doc-callout doc-callout--note">
  <p>运行扫描需要 Codex Security 访问权限。有关通用编码智能体，请参阅 <a href="/docs/codex-sdk">Codex SDK 指南</a>。有关终端和 CI 工作流，请参阅 <a href="/docs/security/cli">Codex Security CLI 快速入门</a>。</p>
</aside>

## 设置 SDK

安装 SDK：

```bash
npm install @openai/codex-security
```

开始扫描前，请设置 `OPENAI_API_KEY` 或 `CODEX_API_KEY`、使用
现有的文件型 Codex 登录信息，或[配置其他
提供商](#configure-the-runtime-and-credentials)。Amazon Bedrock 使用 AWS
凭据；OpenRouter 和 Fireworks 使用提供商专用的 API key 和
配置。

为获得最佳效果，请使用已通过 [Trusted Access for Cyber](https://chatgpt.com/cyber) 验证的账户。登录或提供 API key 并不会
授予 Trusted Access 权限。

## 运行扫描

SDK 使用你的本地操作系统权限运行，且不会暂停
以等待批准。
扫描进程可能继承你的环境，因此请在开始前移除无关凭据。
请参阅[本地扫描
权限](/docs/security/cli/reference#local-scan-permissions)。

将此示例保存为 `scan.mjs`。替换路径，运行标准仓库
扫描，并在工作完成后关闭客户端。传入 `outputDir`，以选择位于
所在 Git 工作树之外的私有结果目录。

如果省略 `outputDir`，Codex Security 会将结果保存到自己的持久化
状态目录中。结果可能包含源代码片段和漏洞
详情。请设置可读取结果的人员范围和保留时长。

```ts


const security = new CodexSecurity();

try {
  const result = await security.run("/path/to/repository", {
    outputDir: "/path/outside/repository/results",
  });

  console.log(result.reportPath);
  console.log(result.manifest.scan.status);
  console.log(result.findings.findings.length);
} finally {
  await security.close();
}
```

使用 Node.js 运行：

```bash
node scan.mjs
```

该示例会打印报告路径、扫描状态和发现项数量。
打开报告以审查证据。数量会因仓库
和扫描而异，因此不要用预期数量来判断集成是否正常工作。

`run` 会验证已保存的产物，并在
`result.manifest.scan.status` 为 `"completed"` 时返回 `ScanResult`。查看 `result.coverage`，了解
已审查的范围、排除项和推迟的工作。已完成的扫描仍可能
存在覆盖缺口。运行时、输入或结果完整性方面的故障可能抛出
[错误](#handle-scan-errors)。

在后续示例中，复用已打开的 `security` 客户端，并将 `close()` 保留在
`finally` 中，以释放运行时。将其他需要的导入语句添加到
`scan.mjs` 的顶部。

## 使用预检检查输入

使用 `preflight` 可在开始扫描前检查仓库、目标、模式、知识库文档、
输出位置和 Codex 配置：

```ts
const plan = await security.preflight("/path/to/repository", {
  target: ["services/billing", "packages/auth"],
  knowledgeBasePaths: ["/path/to/architecture.md"],
  outputDir: "/path/outside/repository/results",
});

console.log(plan.repository);
console.log(plan.target.kind);
console.log(plan.mode);
console.log(plan.outputDir);
```

预检会检查本地输入，不会启动 Codex、加载凭据，或
检查 Python 和插件是否可用。预检成功并不能证明
扫描能够通过身份验证或启动。

若要预览现有结果目录的归档操作，请设置
`archiveExisting: true`：

```ts
const plan = await security.preflight("/path/to/repository", {
  outputDir: "/path/outside/repository/results",
  archiveExisting: true,
});

console.log(plan.archiveDir);
```

返回的 `archiveDir` 会预览归档名称。最终路径可能
不同，因为 `run` 会生成自己的唯一目标位置。使用 `onOutputArchived`
获取实际归档路径：

```ts
await security.run("/path/to/repository", {
  outputDir: "/path/outside/repository/results",
  archiveExisting: true,
  onOutputArchived(archiveDir) {
    console.log("Archived results:", archiveDir);
  },
});
```

扫描会归档先前的结果，并从空的输出
目录开始。

## 选择扫描目标

SDK 支持仓库、路径、已提交差异和工作树目标。
默认目标是完整仓库。

### 扫描选定路径

传入仓库内的路径数组：

```ts
const result = await security.run("/path/to/repository", {
  target: ["services/billing", "packages/auth"],
});
```

路径可以指向文件或目录。SDK 会解析仓库内的每条路径并
移除重复项。

### 扫描已提交的更改

使用 `DiffTarget.refs` 扫描两个本地可用
Git 修订版本之间已提交的更改：

```ts


const target = DiffTarget.refs({
  base: "origin/main",
  head: "HEAD",
});

const result = await security.run("/path/to/repository", { target });
```

目标修订版本默认为 `HEAD`。差异目标要求仓库参数
为 Git 工作树根目录。

### 扫描工作树

使用 `DiffTarget.workingTree` 扫描相对于基准
修订版本的暂存和未暂存更改：

```ts
const target = DiffTarget.workingTree({ base: "HEAD" });
const result = await security.run("/path/to/repository", { target });
```

基准默认为 `HEAD`。开始差异或工作树扫描前，请获取选定的修订版本。

### 选择深度模式

对于需要更广泛评审的仓库或路径扫描，请设置 `mode: "deep"`：

```ts
const result = await security.run("/path/to/repository", {
  target: ["services/billing"],
  mode: "deep",
  workers: 2,
  subagents: 0,
  stopAfterNoNew: 3,
  maxDiscoveryRuns: 10,
  maxTimeHours: 1.5,
});
```

深度模式支持仓库和路径目标。差异和
工作树扫描请使用标准模式。可选设置用于控制并发的独立
标准扫描工作进程、每个工作进程的子智能体数量、连续完成但
没有新发现的工作进程扫描次数，以及工作进程运行的总次数和时长。这些设置
需要 `mode: "deep"`。

`maxTimeHours` 默认为 `96`，接受不超过 `96` 的正数，
小时数可以为小数。到达截止时间时，Codex Security 会停止未完成的
工作进程，保留已完成的扫描结果，并将其汇总到最终
报告中。查看 `result.coverage`，了解推迟的工作和待解答的问题。

### 添加安全知识库

通过 `knowledgeBasePaths` 传入架构文档、威胁模型或安全策略：

```ts
const result = await security.run("/path/to/repository", {
  knowledgeBasePaths: [
    "/path/to/architecture.md",
    "/path/to/security-policies",
  ],
});
```

SDK 接受文件或目录，并会递归搜索目录。
支持的文档格式为 `.md`、`.markdown`、`.txt`、`.pdf` 和 `.docx`。
SDK 会拒绝符号链接输入路径、跳过符号链接目录条目，并将
提取的文档内容保存在扫描结果之外。

### 添加扫描和后续指令

使用 `scanPrompt` 聚焦扫描，并使用 `postScanPrompt` 请求后续操作：

```ts
const result = await security.run("/path/to/repository", {
  scanPrompt: "Focus on tenant isolation and authorization checks.",
  postScanPrompt: "Write confirmed findings to post-scan-summary.md.",
});
```

如果后续操作失败，SDK 会保留已完成的扫描，并通过
`onWarning` 报告错误。它还会恢复被后续操作更改的所有已完成扫描产物。

### 设置扫描预算

设置 `maxCostUsd`，在扫描的估算模型成本超过限制时停止扫描。
使用 `onCost` 可在扫描运行期间跟踪成本：

```ts
const result = await security.run("/path/to/repository", {
  maxCostUsd: 5,
  onCost(cost) {
    console.log(cost.estimatedUsd);
  },
});

console.log(result.cost?.estimatedUsd);
```

该限制用于估算支出，并非严格的上限，因此已经在
进行中的请求完成时，费用可能略微超出限制。如果深度扫描在
Codex Security 汇总已完成的工作进程结果后达到限制，`run` 可以返回一个
将 `manifest.scan.status` 设为 `"completed"` 的结果，并通过
`onWarning` 报告预算警告。查看 `result.coverage`，了解尚未完成的工作。

如果扫描无法生成有效的已完成结果，`run` 会抛出
`ScanCostLimitExceededError`，并保留所有可用输出。

## 使用扫描结果

`ScanResult` 会提供结构化文档、扫描元数据和产物
路径：

| 属性             | 内容                                                                           |
| -------------------- | ---------------------------------------------------------------------------------- |
| `manifest`           | 已封存的扫描清单，包含目标、范围、生成方和产物记录。 |
| `findings`           | 当前扫描的发现项。从 `findings.findings` 读取发现项对象。     |
| `repositoryFindings` | 扫描历史可用时，提供仓库历次扫描中尚未关闭的发现项。             |
| `coverage`           | 已审查的范围、排除项、推迟的工作和待解答的问题。                  |
| `scanDir`            | 扫描目录。                                                                |
| `threadId`           | 此次扫描的 Codex 线程标识符。                                          |
| `turnResult`         | 轮次状态、响应和可用的用量元数据。                               |
| `cost`               | 预估的模型和 token 费用，不可用时为 `null`。                        |
| `reportPath`         | `report.md` 的路径。                                                           |
| `manifestPath`       | `scan-manifest.json` 的路径。                                                  |
| `findingsPath`       | `findings.json` 的路径。                                                       |
| `coveragePath`       | `coverage.json` 的路径。                                                       |
| `artifactsDir`       | 辅助产物目录。                                                |
| `sarifPath`          | 生成的 SARIF 路径，不存在 SARIF 时为 `null`。                          |
| `pluginVersion`      | 扫描生成方记录的版本。                                         |

若要要求后续扫描使用相同插件，请传入
`expectedPluginVersion: result.pluginVersion`。如果
已安装的插件版本不同，SDK 会拒绝扫描。

直接使用结构化发现和覆盖范围：

```ts
for (const finding of result.findings.findings) {
  const location = finding.locations[0];
  if (location === undefined) continue;

  console.log(
    finding.severity.level,
    `${location.path}:${location.startLine}`,
    finding.title
  );
}

for (const deferred of result.coverage.deferred) {
  console.log(deferred.id, deferred.reason);
}
```

发现可以包含可选的 `codeEvidence`、`rootCause`、`validation`、
`attackPath`、`remediationTests` 和 `preventiveControls` 字段。

对于仓库范围的发现，`confirmedInLatestScan` 会区分
最新扫描中发现的问题与先前扫描中仍未解决的问题：

```ts
for (const finding of result.repositoryFindings ?? []) {
  console.log(finding.title, finding.confirmedInLatestScan);
}
```

新结果不包含 `coverage.completeness`。使用 `manifest.scan.status`
查看执行状态，并审查 `coverage` 中推迟审查的范围、排除项和待解答的
问题，了解扫描审查了哪些内容。

`result.toJSON()` 会在一个可直接转换为 JSON 的对象中返回清单、仓库和当前扫描的发现、
覆盖范围、扫描和聊天标识符、`reportPath`、`artifactsDir`、
`sarifPath`、成本以及轮次元数据。

## 跟踪或取消扫描

传入 `ScanOptions` 回调，以报告扫描启动、工作进程进度和
连接重试：

```ts
const result = await security.run("/path/to/repository", {
  outputDir: "/path/outside/repository/results",
  onScanStarted() {
    console.log("Scan started");
  },
  onProgress(progress) {
    console.log(progress.phase, progress.filesCompleted, progress.filesTotal);
  },
  onWorkerStatus(status) {
    console.log(status.kind, status);
  },
  onSessionEvent(session) {
    console.log(session.threadId, session.worker, session.event["type"]);
  },
  onReconnect(attempt, maxAttempts) {
    console.log(`Reconnect attempt ${attempt} of ${maxAttempts}`);
  },
  onObserverError(observer, error) {
    console.error(`${observer} failed`, error);
  },
});

console.log(result.reportPath);
```

传入请求或作业控制器提供的 `AbortSignal`，以取消扫描。
如果扫描在 30 分钟后仍在运行，此示例会中断扫描，并
打印包含已保存输出的目录：

```ts


try {
  await security.run("/path/to/repository", {
    outputDir: "/path/outside/repository/results",
    signal: AbortSignal.timeout(30 * 60 * 1000),
  });
} catch (error) {
  if (error instanceof ScanInterruptedError) {
    console.error(error.scanDir);
  } else {
    throw error;
  }
}
```

中断的扫描可能会在 `scanDir` 中留下部分输出。当需要调查
结果时，请保留该目录。

显示扫描设置进度的应用程序还可以使用 `ScanOptions`
生命周期回调：

| 回调                            | 调用时机                                          |
| ----------------------------------- | ---------------------------------------------------- |
| `onAuthentication(authentication)`  | 扫描选择身份验证方法时。          |
| `onOutputArchived(archiveDir)`      | 现有结果移动到归档目录时。      |
| `onOutputDirReady(scanDir)`         | 私有扫描目录准备就绪时。                 |
| `onScanStarted()`                   | 扫描设置完成并开始执行时。           |
| `onTrustedAccessStatus(status)`     | Trusted Access 状态变为可用时。             |
| `onReconnect(attempt, maxAttempts)` | SDK 重试已断开的扫描流时。          |
| `onActivity(activity)`              | 命令、工具、推理步骤或消息更新时。 |
| `onProgress(progress)`              | 扫描阶段或已评审文件数发生变化时。       |
| `onWorkerStatus(status)`            | 工作进程预检或分派状态发生变化时。         |
| `onSessionEvent(session)`           | 扫描或工作进程会话发出事件时。             |
| `onCost(cost)`                      | 有更新后的扫描成本估算值可用时。         |
| `onWarning(warning)`                | 扫描报告警告时。                          |
| `onObserverError(observer, error)`  | 其他扫描生命周期回调引发错误时。     |

Trusted Access 状态为 `granted`、`not_granted` 或 `unknown`。缺失或
未知的访问权限也会触发 `onWarning`。

`onSessionEvent` 接收未经脱敏的事件，其中可能包含源
代码或凭据。请先过滤这些事件，再将其发送到共享日志或其他
服务。

## 配置运行时和凭据

需要特定插件、解释器或
Codex 设置时，请传入运行时配置。请选择你的凭据有权访问的模型。如果你使用 ChatGPT
登录，请先查看 [GPT-6.1 Sol 可用性](/docs/models#gpt-6.1-sol)，再
使用此示例：

```typescript
const security = new CodexSecurity({
  pluginPath: "/path/to/codex-security-plugin",
  pythonPath: "/path/to/python",
  codexOverrides: {
    model: "gpt-6.1-sol",
    model_reasoning_effort: "medium",
  },
});
```

`pluginPath` 接受插件目录或 ZIP。`pythonPath` 选择
插件解释器。`codexOverrides` 会将支持的值合并到隔离的
Codex 配置中。扫描默认使用 `gpt-5.6-sol` 和超高推理强度。
在 `codexOverrides` 中设置 `model` 和 `model_reasoning_effort`，可使用
其他模型或推理强度。若要使用 [Amazon
Bedrock](/docs/security/cli/reference#use-amazon-bedrock)，请在 `codexOverrides` 中设置
`model_provider` 和 `model`。

`codexOverrides` 无法限制扫描的文件系统访问权限或更改其
批准策略。请参阅[本地扫描
权限](/docs/security/cli/reference#local-scan-permissions)。

对于 OpenRouter 或 Fireworks，还需提供相应的 API key，并在
`codexOverrides` 中提供完整的提供商配置。例如，设置
`OPENROUTER_API_KEY` 并配置 OpenRouter：

```ts
const security = new CodexSecurity({
  codexOverrides: {
    model: "anthropic/claude-sonnet-4.5",
    model_provider: "openrouter",
    model_providers: {
      openrouter: {
        name: "OpenRouter",
        base_url: "https://openrouter.ai/api/v1",
        env_key: "OPENROUTER_API_KEY",
        wire_api: "responses",
      },
    },
  },
});
```

对于 Fireworks，请将两个 `openrouter` 键都改为 `fireworks`，将 `name` 设置为
`Fireworks AI`，将 `env_key` 设置为 `FIREWORKS_API_KEY`，使用
`https://api.fireworks.ai/inference/v1` 作为 `base_url`，并选择一个 Fireworks
模型。

客户端还提供受支持的身份验证方法：

| 方法                     | 用途                                                     |
| -------------------------- | ----------------------------------------------------------- |
| `loginApiKey(apiKey)`      | 使用 API key 对隔离的运行时进行身份验证。          |
| `loginChatGPT()`           | 启动浏览器登录流程并返回登录句柄。     |
| `loginChatGPTDeviceCode()` | 启动设备码登录流程并返回登录句柄。 |
| `account()`                | 返回当前身份验证状态。                    |
| `logout()`                 | 清除隔离环境中的身份验证信息。                              |

登录句柄提供 `waitForInstructions`、`authUrl`、`verificationUrl`、
`userCode`、`wait` 和 `cancel`，以便应用呈现并完成
所选的登录流程。SDK 可以复用基于文件存储的 Codex 登录信息。对于 CI 和服务端自动化，
请使用 API key。

当 API key 和已存储的登录信息同时可用时，SDK 默认使用 API
key。若要改用你的 ChatGPT 登录信息，请为扫描选择该信息：

```ts
const result = await security.run("/path/to/repository", {
  auth: "chatgpt",
});
```

设置 `auth: "api-key"` 可要求使用环境中的 API key。`preflight` 接受
相同的 `auth` 选项。

## 处理扫描错误

捕获与应用程序可采取操作相对应的导出错误类：

| 错误                            | 含义                                                            |
| -------------------------------- | ------------------------------------------------------------------ |
| `AuthenticationRequiredError`    | 扫描需要受支持的凭据。                               |
| `ConfigurationError`             | Codex 配置或覆盖值不适用。                  |
| `InvalidTargetError`             | 仓库、路径、模式或 Git 目标不适用。           |
| `OutputDirectoryError`           | 输出位置或其权限不适用。             |
| `OutputInsideProtectedRootError` | 输出目录位于被扫描的仓库或工作树内。 |
| `PluginPythonUnavailableError`   | 没有可用的 Python 解释器。                        |
| `PluginBootstrapError`           | 插件运行时无法启动。                                |
| `ScanCostLimitExceededError`     | 扫描超出其估算成本限制。                        |
| `IncompleteScanError`            | 扫描在生成所需结果前结束。               |
| `ContractValidationError`        | 已完成的扫描返回了结构化契约错误。             |
| `ScanInterruptedError`           | 中断停止了扫描，并且可能留下部分输出。 |

接下来可参阅 [CLI 快速入门](/docs/security/cli)、[CI
指南](/docs/security/cli/ci)或 [CLI
参考](/docs/security/cli/reference)。
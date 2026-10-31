# PaintCodex 架构调研报告

> 调研日期：2026-10-31
> 参考框架：《AI Agent 实战手册（ai-agent-handbook）》第 2 章「Agentic Application 参考架构」、第 3 章「范式：Harness 的主流构建方式和责任边界」
> 调研对象：`C:\Users\Administrator\Documents\Src\PaintCodex`（教学用 AI 绘画应用，Codex CLI app-server + dynamic tools 驱动画布）
> 对照资料：`02-docs/codex-cli-docs/`（Codex CLI 官方文档离线资料集，2026-10-31 抓取）

---

## 0. TL;DR（结论摘要）

PaintCodex 是**「高代码 Agent Framework 自主构建 Harness」路线的极简单机版**：它没有用 AgentScope/LangChain 这类通用框架，而是把 Codex CLI 的 `app-server` 实验协议当作模型接入层，**从零手写了几乎全部 Harness 编排层**（Agent Loop、Context 策略、State、Tool、Permission、Observability、Verification）。同时又把「模型会话状态（thread transcript）与沙箱」外包给了 Codex 产品能力。

它在个人项目层面**完成度很高、工程质量意识强**：人机同权 + actor 归因 + revision 乐观并发、失败对模型可见、拉为主的上下文、fail-closed 确认通道、sandbox read-only、四级 trace + 拓扑监控页、版本闸门 + 升级纪律、40 个测试文件。这些恰是第 2 章「状态外置」「自主性与权限匹配」「可观测是运行前提」三原则的教科书级落实。

但对照第 2 章的企业级参考架构，它**整体还停留在「一次性的 Agent 演示」与「可运营的企业系统」之间的分界线上**，核心缺口集中在五个方面：

1. **没有 Task/Session 数据模型**（原则三「状态外置」只完成了一半）：daemon 只有「画布文档 + 一次性 turn」，turn 中途崩溃即丢失，无 Event Log / Checkpoint / Plan / Todo；
2. **会话状态所有权在 Codex 内部**：thread transcript 由 codex 自己的 SQLite 持有，daemon 数据面无会话记录，无法做会话续接、审计与迁移；
3. **没有 Agent Release 概念**：prompt、工具集、评估无版本，无法回答「生产中某次任务用的是哪个 release」；
4. **没有评估闭环**：无 Dataset / Evaluator / 基线，无法证明「新版本更好」；
5. **单用户、无身份、无网关**：无租户隔离、无配额/预算/成本归因、无模型路由、无集中 Policy。

改造路线建议分三阶段：**A 稳定内核**（补 Task 状态与 Checkpoint、Agent Release、CI 与协议漂移门禁、最小评估基线，仍保持单用户本地）→ **B 企业化**（身份与租户、集中 Policy、AI Gateway、服务端制品存储、任务队列与恢复）→ **C 平台化**（三平面分离、多 Agent 编排、容器化沙箱、托管/私有执行面部署形态）。详见第 7 节。

---

## 1. 调研范围与方法

- **参考框架**：完整读取第 2 章（三视图、五能力责任域、五原则、Runtime/Sandbox/State/Gateway、生命周期闭环）与第 3 章（Agent = Model + Harness、四类构建入口、三类工程契约、Agent Platform）。
- **代码证据**：以 PaintCodex 真实代码与文档为样本，逐文件核对后引用：
  - 架构：`MISSION.md`、`README.md`、`docs/architecture-design.md`、`docs/adr/0002/0006/0009` 等；
  - 运行时：`apps/daemon/src/main.ts`、`api/server.ts`、`api/routes.ai.ts`、`paint/agent/runtime/codex-runtime.ts`、`tools.ts`、`confirmation.ts`、`prompt.ts`、`paint/command-dispatcher.ts`、`paint/service.ts`、`storage/database.ts`；
  - 质量与债务：`.scratch/codex-native-tools/spec.md`、`issues/08-quality-debt.md`、`NOTES.md`。
- **对照资料**：`02-docs/codex-cli-docs/` 中文主题页 03（命令参考与自动化）、07（环境与沙箱）、08（权限与安全）及其 `source/` 英文原文。

---

## 2. 参考框架速览（第 2 / 3 章要点）

### 2.1 第 2 章：Agentic Application 企业级参考架构

三个正交视图：
- **组件视图**：系统由什么组成（Model、Harness 编排层、Context、State、Memory、Knowledge、Skill、Tool、Runtime、Sandbox、Gateway、Observability、Evaluation、Security）。
- **平台视图**：这些组件在哪里运行、由谁负责（执行面 / 数据与资源面 / 控制面）。
- **生命周期视图**：系统如何从架构决策走向运行，并被治理和改进（架构设计 → 构建 → 运行 → 治理 → 调优闭环）。

五个能力责任域：业务与应用层、Agent 构建与编排层、生产运行层、治理与控制层、调优层。

五项设计原则：
1. **Model 与 Harness 解耦**——模型是可替换的认知核心，Harness 是工程外壳，模型与 Harness 一起评估、但不实现强绑定；
2. **编排层与 Runtime 解耦**——编排层定义如何思考和行动，Runtime 定义在什么资源和故障条件下持续运行；
3. **状态外置，执行实例可替换**——会话、计划、待办、工具结果、工作区、记忆、制品不应只存在于模型上下文或 Runtime 内存中，Event Log / Checkpoint / Workspace 是长任务恢复的前提；
4. **自主性必须与权限和可验证性匹配**——最小权限、短期凭证、网络出站控制、Sandbox 隔离、结果校验、高风险动作审批；
5. **可观测、安全和评估是运行前提**——不记录轨迹和环境结果，就无法定位、复现或证明改进。

生命周期的最小发布单元是 **Agent Release**：至少绑定模型版本与路由策略、Harness 编排代码与配置、Prompt/Context/Memory/Skill/Knowledge 版本、Tool/权限策略/凭证范围、Runtime/Sandbox/资源/网络配置、评估数据集/Evaluator/基线/准入阈值。

### 2.2 第 3 章：Harness 的主流构建方式（四类入口）

| 构建入口 | 示例 | 企业直接控制 | 可复用/托管 | 企业仍要承担 |
| --- | --- | --- | --- | --- |
| 高代码 Framework 自主构建 Harness | AgentScope、LangChain、DeepSeek Harness | Loop、Context、Planning、状态语义、工具策略、验证逻辑 | 模型、消息、工具、状态、编排基础抽象 | 组合后的行为、执行基础、安全、恢复、评估、业务验收 |
| 产品化 Harness | QwenPaw、Hermes | 业务目标、工具扩展、权限回调、Workspace、应用集成 | 工作区理解、规划、工具执行、Session、事件 | 多租户、业务 Task、隔离环境、凭证、Artifact、Outcome |
| 基于模型构建 Agent | Qoder Cloud Agents、Claude Managed Agent | Agent 定义、Environment 配置、企业能力接入、任务委派、验收 | 约定范围内 Harness、Session 推进、事件流、隔离执行 | 身份映射、业务状态、审批、数据边界、结果验收 |
| 云产品快速构建 | 阿里云 AgentCore | 业务目标、Agent 配置、共享资源组合、发布范围、验收 | 预置模型/知识/工具/运行环境/管理能力 | 业务 Task、数据与权限边界、扩展集成、效果评估 |

构建 Harness 需要实现的工程对象（第 3.1.2 节）：Agent Contract、Execution、Context & State、Capability、Environment、Control、Interaction、Quality。

---

## 3. PaintCodex 现状架构（代码证据）

### 3.1 组件与数据流

```
浏览器前端 (apps/web: React + Fabric.js)
  │  REST + SSE
  ▼
apps/daemon (Fastify 单进程)
  ├─ api/routes.*        REST：/paint/canvas·ai/chat·ai/confirm·render-result·export-result·monitor
  ├─ paint/service.ts    画布领域服务（create/rename/applyAction/undo/redo）
  ├─ paint/command-dispatcher.ts   ← 人机同权唯一写入口（actor: 'user' | 'agent'）
  ├─ paint/agent/runtime/codex-runtime.ts  ← 唯一接缝：长驻 codex app-server 子进程
  │     · thread/turn 管理（一画布一 thread、一消息一 turn）
  │     · 工具执行（进程内、经 dispatcher、串行队列、30s 超时）
  │     · 确认通道（SSE confirm 帧 + /paint/ai/confirm，60s 超时 fail-closed）
  │     · 崩溃懒重启 + thread/resume
  ├─ paint/agent/runtime/tools.ts   ← 8 个 dynamic tools（声明 + 执行）
  ├─ paint/agent/prompt.ts          ← 拉为主：只放画布标识/尺寸/revision/图层名
  ├─ storage/database.ts            ← SQLite(WAL)：canvases/layers/snapshots/agent_logs/canvas_thumbnails
  └─ observability/                 ← agent_logs + trace/span + source/target 方向 + monitor 页
```

关键事实（均有代码出处）：

1. **模型接入**：`spawn('codex app-server')` 长驻子进程，JSONL-over-stdio；`initialize → thread/start|resume → turn/start → item/tool/call → turn/completed`。启动时 `probeCodexVersion` 校验 `>= 0.164.0`，不满足则整个 AI 路由不注册（`server.ts`）。
2. **线程/会话**：一画布一条 thread，thread id 持久化在 `canvases.codexThreadId`；daemon 重启后 `thread/resume`；resume 失败则重建 thread 并 `onNotice('会话已重置')`；app-server 崩溃**懒重启**（不在崩溃回调里立刻拉起），崩溃后下一句话才恢复（ADR-0009 修订）。
3. **工具**：`canvas_get_context / canvas_create_layer / canvas_update_layer / canvas_delete_layer / canvas_select / canvas_export_png / canvas_undo / canvas_render_preview`。工具在 **daemon 进程内**执行，`actor='agent'`，经 `CommandDispatcher` 落到与人类完全相同的 `PaintAction`（ADR-0009 §1）。无画布的对话使用 `EMPTY_CANVAS_TOOLS`（声明 0 工具）。
4. **失败对模型可见**：工具失败返回 `{ ok:false, code, message }`（含 `revision_conflict`、`tool_timeout`、`unknown_tool` 等），不做静默重试（ADR-0009 §4）。
5. **上下文**：prompt 只给画布身份/尺寸/revision/图层名列表，细节靠 `canvas_get_context` 执行中拉取（ADR-0009 §3）——「拉为主」。
6. **并发控制**：`expectedRevision` + `revision_conflict`（409），画布单写者（每 thread 工具串行队列 `toolQueues`）。
7. **撤销归因**：`canvas_undo` 只撤 agent 自己的动作，栈顶是用户动作则返回 `top_action_is_user`（ADR-0009 §5）。
8. **确认**：`canvas_delete_layer`、`canvas_export_png` 执行前经 daemon 自有确认通道（SSE `confirm` + `/paint/ai/confirm`），60s 无答复视为拒绝，SSE 断开 / turn 中断立即结算为 `disconnected`/`interrupted`（fail-closed）；不走 Codex 的 `ToolRequestUserInput`（ADR-0009 §6 修订）。
9. **安全**：codex 子进程 `sandbox: 'read-only'` + `approvalPolicy: 'never'`——模型根本碰不到文件系统；工具入参校验（`additionalProperties:false` + SVG 白名单 `isSafeSvg`，拒绝脚本/事件/内嵌图/远程引用）。
10. **可观测**：SQLite `agent_logs`（trace_id/span_id/parent_id/source/target/category/level/payload）；HTTP、chat turn、tool call、画布落库四级 span；`source→target` 方向拓扑；web 端 monitor 页（拓扑图 / 时序 / 聚合）。`tool_call` 是 AI 行为统计锚点。
11. **测试**：40 个 vitest 文件；Runtime / Confirmation / Render / Export / VersionProbe 全部可注入（`ServerOptions` seam），测试不 spawn 真实 codex。
12. **无 CI**：ADR-0009 修订明确「本仓库没有 CI」，协议类型是 `generate-json-schema --experimental` 输出**手工转写子集**，升级靠「重新生成 + 手工比对 + 全链路测试」纪律兜底。

### 3.2 数据模型（schema 级）

- `canvases`：id / name / width / height / backgroundColor / revision / undoCursorRevision / codexThreadId / createdAt / updatedAt —— **画布文档状态外置**；
- `layers`：图层，外键级联；`snapshots`：撤销快照（state JSON，保留 20 条），`actor CHECK IN ('user','agent')`；
- `agent_logs`：观测日志（trace/span/parent/source/target）；
- `canvas_thumbnails`：缩略图（浏览器渲染后上传）。

**注意**：整个 schema 里**没有** Session / Task / Event Log / Checkpoint / Workspace / Artifact / Memory / Knowledge / 用户 / 租户 表。对话 transcript 由 Codex 在自己侧（CODEX_HOME SQLite）持有，daemon 只存一个 thread id。

---

## 4. 架构模式判定：它属于哪种 Harness 构建方式

### 4.1 判定结论

**PaintCodex ≈ 「高代码 Agent Framework 自主构建 Harness」路线（第 3.2 节）的极简单机个人版**，但有两个显著特征使它不完全等同于教材示例：

1. **"Framework"被替换为 Codex app-server 实验协议**：教材示例（AgentScope）的 Framework 提供模型/消息/工具/状态/编排的稳定抽象；PaintCodex 的"框架层"是一个标记为 `[experimental]`、官方定位为 "primarily for development and debugging and may change without notice" 的协议（`codex-cli-docs/source/developer-commands.md` 第 95 行）。因此它**既要自建 Harness 编排，又要自建协议适配与协议漂移兜底**，比用稳定框架的团队承担更多。
2. **"会话状态"外包给了产品能力**：Codex CLI 自己管理 thread 持久化（`codex app-server` 的 thread/resume + 磁盘 SQLite），PaintCodex 只持久化 thread id 映射。这相当于第 3.3 节「复用产品化 Harness」的局部借用——但它复用的不是完整 Harness，只是「模型会话 + 沙箱」两块。

对照表 3-2 逐项：

| 维度 | PaintCodex 实际 | 判定 |
| --- | --- | --- |
| 企业直接控制的重点（Loop/Context/状态语义/工具策略/验证） | turn 管理、拉为主 Context、revision+actor 状态语义、8 工具+确认通道、undo 归因+SVG 校验 —— 全部自建 | ✅ 高度自主 |
| 可复用/托管能力 | Codex：模型接入、thread 持久化、read-only 沙箱、事件流 | ✅ 局部复用 |
| 企业仍需承担 | 执行基础（子进程管理/懒重启）、安全（sandbox+SVG 白名单）、恢复（thread/resume）、**评估（缺失）**、**业务验收（缺失）** | ⚠️ 评估与验收两项空白 |

### 4.2 对照第 3.1.2 节工程对象清单

| 构建对象 | PaintCodex 现状 |
| --- | --- |
| Agent Contract | 半有：MISSION.md 定义目标与约束；无机器可读的成功标准/禁止项 |
| Execution | 有：turn 状态机、串行工具队列、interrupt、超时；无 Plan/Todo、无 Checkpoint |
| Context & State | Context 策略优秀（拉为主）；State 只有画布文档，无 Task/Session/Workspace/Memory |
| Capability | 有：8 工具 + schema 校验 + SVG 白名单；无 Skill 版本化/渐进披露/能力目录 |
| Environment | 有：sandbox read-only + 进程内工具执行；无容器/网络出站/凭证管理 |
| Control | 有：确认通道 fail-closed、actor 归因；无集中 Permission Policy（硬编码在工具里） |
| Interaction | 有：SSE 流、confirm 帧、中断恢复游标（thread/resume）；无「恢复游标」的 turn 级语义 |
| Quality | 半有：Trace + 结构化错误 + 40 测试；无 Outcome 定义、无评估基线 |

---

## 5. 对照第 2 章五责任域的落实与缺口

### 5.1 原则级对照

| 第 2 章原则 | PaintCodex 落实 | 缺口 |
| --- | --- | --- |
| 原则一：Model 与 Harness 解耦 | `CodexRuntime` 是唯一接缝；版本闸门；协议类型按需转写 | 协议 experimental、无 CI 兜底；**无模型路由**（单一 codex CLI 直连）；模型升级无回归评估 |
| 原则二：编排层与 Runtime 解耦 | 编排（service/dispatcher/tools）与 Runtime（codex-runtime 进程承载）边界清晰 | Runtime 单进程单子进程；**无队列/调度/配额**；`activeTurns` 全在内存，turn 中途 daemon 崩溃即丢失 |
| 原则三：状态外置，实例可替换 | 画布文档外置 SQLite；thread id 持久化可 resume | **无 Task/Session/Event/Checkpoint/Workspace/Artifact**；snapshots 仅 20 条；对话 transcript 归 codex 所有；崩溃后 turn 只能整体重发 |
| 原则四：自主性与权限/可验证性匹配 | sandbox read-only（blast radius 主动收窄）；SVG 白名单；确认 fail-closed；revision 并发；undo 归因 | 无身份/租户；无凭证管理；确认策略硬编码；渲染/导出依赖浏览器在线（部分影响面在客户端）；无网络出站控制维度 |
| 原则五：可观测/安全/评估是运行前提 | 四级 trace + 方向拓扑 + monitor 页；结构化错误 | **无成本采集、无 Outcome 判定、无评估集/回归、无告警/SLO** |

### 5.2 组件视图缺口（2.2.3 五类信息对象）

| 对象 | PaintCodex 现状 | 对照第 2 章要求 |
| --- | --- | --- |
| Context | 拉为主、最小摘要、不会随图层数膨胀 ✅ | 符合最佳实践 |
| State | 画布文档 = 强一致持久化 ✅；**但 Task/Session/Plan/Todo/Checkpoint 缺失** ❌ | 只满足一半 |
| Memory | **无** | 跨会话偏好/经验无写入策略、无遗忘治理 |
| Knowledge | **无**（当前领域不需要，但无扩展位） | 未来接业务文档/RAG 时需权限过滤与来源追溯 |
| Skill | 工具集固定、无版本化、无渐进披露 | 无发布/复用/回滚语义 |

### 5.3 平台视图缺口（2.3.2 三平面）

| 平面 | 现状 |
| --- | --- |
| 执行面 | 单 Fastify 进程 + 单 codex 子进程；无 Worker 池、无队列、无租户并发 |
| 数据与资源面 | 只有画布业务库；无 Task State / Event Log / Checkpoint / Workspace / Artifact / Memory / Knowledge |
| 控制面 | 有 ADR + 版本闸门 + 观测雏形；无 Agent Registry / Model & Tool Registry / Tenant / IAM / Policy / Budget / Audit / Evaluation / Deployment |

### 5.4 生命周期视图缺口（2.4）

| 阶段 | 现状 | 缺口 |
| --- | --- | --- |
| 架构设计 | ADR-0001~0012+、architecture-design.md、.scratch spec/issues —— 文档纪律优秀 ✅ | 无威胁建模/影响半径评估的显式产出（单用户场景可接受） |
| 构建 | 40 测试 + 注入 seam；工具集最小化是刻意决策 | **无 CI**；无 Agent Release（prompt/工具/评估不版本化） |
| 运行 | 懒重启 + thread/resume + 版本闸门；health 端点 ✅ | 无 Checkpoint/恢复点；无任务队列；无成本/配额 |
| 治理 | monitor 页 + 方向拓扑 + 审计日志（agent_logs）✅ | 无 Policy 集中定义；无审批留痕语义（确认只有日志）；无告警 |
| 调优 | **无** | 无 Dataset/Evaluator/基线/灰度/回滚 |

---

## 6. 架构存在的问题（按严重度分级）

### P0 —— 直接阻碍企业化/规模化

**P0-1 没有 Task/Session 层：turn 不可恢复。**
daemon 只有「画布文档 + 一次性 turn」。`activeTurns` 是内存 Map；daemon 崩溃、turn 中途进程退出时，用户只能**整体重发消息**，已完成的工具副作用（部分图层已创建）与失败状态无法衔接。违背原则三「状态外置，执行实例可替换」。第 3.3.2 节明确警告「不能因为 Session 能被读取就直接重放最后一次工具调用」，PaintCodex 连 turn 级 Checkpoint 都没有。

**P0-2 会话/对话状态所有权在 Codex 内部，daemon 数据面无会话记录。**
thread transcript 由 codex 自己的 SQLite（CODEX_HOME/CODEX_SQLITE_HOME）持有，daemon 只存一个 `codexThreadId`。后果：①无法在 daemon 侧做会话审计/合规留痕；②无法跨 Runtime 迁移（换了机器/换了 codex 安装即丢）；③无法做「会话续接」之外的任何产品语义（回顾、导出、多端同步）；④协议一旦大改，历史 transcript 可能不可读。第 3.3.2 节：「外部 Session Store 只负责 Session Transcript，不等于完整的企业任务存储」。

**P0-3 没有 Agent Release / 版本化发布单元。**
prompt 是 `prompt.ts` 里的字符串常量；工具集在 `tools.ts` 固定；无 releaseId 与 trace 关联。升级 codex、改 prompt、加工具后，无法复现历史任务、无法回答「这次任务用的是哪个版本」。第 2.4.1 节：Agent Release 是生命周期的最小可复现单元。

**P0-4 没有评估闭环。**
无 golden 数据集、无 Evaluator、无基线阈值。MISSION.md 的成功标准全部是「人能学会」而不是「系统可判定」。第 2 章原则五与 2.4.2 调优阶段都要求：没有可复现证据，调优只能依赖主观印象。

**P0-5 单用户、无身份/租户/配额。**
画布库所有记录隐含属于唯一用户；无 IAM、无租户隔离、无配额/预算/成本归因。单机阶段可接受，但 MISSION.md 的目标是「迁移到下一个 Web 产品」，该产品一旦多用户即成为硬缺口。

### P1 —— 企业化会痛、可后补

**P1-1 权限/确认策略硬编码在工具实现里。**
`deleteLayer`/`exportPng` 各自 `await requestConfirmation(...)`，确认点散落在工具代码中；无集中 Policy（allow/deny/ask 按工具+参数+风险级别判定），无审批人身份绑定、无 Policy 版本。第 2 章 2.2.2 表 2-2「Middleware 与 Policy Hook」缺失。

**P1-2 无 AI Gateway（LLM/MCP/Agent 三层均无）。**
模型接入 = 直连本机 codex CLI 一条路；无路由（按任务类型/预算/负载）、无降级、无限流、无 Token 成本记录、无协议适配层（MCP/A2A 未接入，虽是 ADR-0009 的刻意取舍，但企业化需要重新评估）。第 2.3.4 节三层 Gateway 粒度全部缺失。

**P1-3 无 Memory 与 Knowledge。**
跨会话的用户偏好（常用色板、风格习惯）、画布级决策无写入策略；无知识检索位。第 2.2.3 节五类信息对象缺两类。

**P1-4 渲染/导出/缩略图依赖浏览器在线，无服务端制品。**
`canvas_render_preview` 通过 SSE 让**浏览器**渲染后回传；导出是浏览器下载；缩略图浏览器渲染后上传。Agent 的「可交付结果」没有服务端副本，无法异步任务化、无法离线生成、无法制品审计。第 2 章 Artifact Store（可寻址、可保留）缺失。

**P1-5 运行时无队列/调度/暂停-恢复。**
interrupt 有，但无任务排队、无「挂起-恢复」语义、无跨画布并发治理。单画布串行是对的，但整个 daemon 只有一个进程、一个子进程，任务长时间等待确认时会阻塞资源模型（当前靠 `suspendTimeout` 暂停工具计时，但 turn 仍占着进程）。

**P1-6 无成本与配额观测。**
agent_logs 有 toolCallCount，但无 token/费用；无法做任务级成本归因与预算控制。

### P2 —— 工程质量/技术债（项目已自知）

- **协议类型手工转写子集 + 无 CI**：ADR-0009 修订自认「本仓库没有 CI」，升级靠纪律而非流水线（08-quality-debt 亦未列，但风险已文档化）。
- **重复实现**：`render-preview.ts` 与 `export-png.ts` 同构（pending 表/settle/超时脚手架）；`humanWait` 模式写了两遍以上；用 `call.tool === 'canvas_create_layer'` 反向反推工具表；`readRegion` 双端漂移；`CanvasToolResult.code` 裸 string、超时常量双端各写一份 —— 全部已在 `issues/08-quality-debt.md` 列票。
- **agent_logs 无保留策略**：SQLite 日志无限增长，无归档/清理/容量告警。
- **单机 SQLite(WAL)**：无备份/恢复演练、无数据保留策略（多用户后需迁移到可托管存储）。
- **getActiveTurn/getThreadId/pendingCount 无生产调用方**（投机性通用，08 已列）。

### 亮点（必须肯定，避免改造时误伤）

1. **人机同权 + actor 归因 + revision 乐观并发**：这是「状态外置 + 可验证性」最扎实的落实。人类与 AI 走同一个 `CommandDispatcher`，`actor` 随 `PaintAction` 入库、入 undo 快照，`canvas_undo` 只撤 agent 自己的动作 —— 同权但不代权（ADR-0009 §5）。
2. **失败对模型可见**：结构化错误、无静默重试 —— 与第 3 章「Failure-visible」完全一致，是很多企业系统都做不到的纪律。
3. **拉为主 + 最小工具集**：prompt 不随图层数膨胀、细节按需拉取；工具从「能用」克制到「必要」，是 Context Engineering 与能力治理的正确姿态。
4. **确认通道 fail-closed**：60s 超时、断开、中断全部按拒绝结算；工具超时与人类等待分开计时（`suspendTimeout`）——设计非常细。
5. **sandbox read-only + approval never**：把模型的 blast radius 主动关进笼子，是「自主性必须与权限匹配」的正确决策（第 2 章原则四）。
6. **可观测分层**：HTTP/chat/turn/tool/canvas 四级 span + source→target 拓扑 + monitor 页，已具备第 13 章「Agent 可观测性」的雏形。
7. **工程纪律**：版本闸门、ADR、.scratch 票据驱动、handoff 文档、40 个测试 + 全可注入 seam —— 生命周期「治理」意识远超同类个人项目。

---

## 7. 企业级 Agent 架构改造建议

> 依据第 2 章「最低充分架构」原则与表 2-5 部署形态；先补齐可恢复性与可复现性，再谈多租户与平台化。

### 阶段 A：稳定内核（保持单用户本地，先解决 P0-1~P0-4）

**A-1 引入 Task / Session / Event / Checkpoint 数据模型（数据与资源面）。**
新增表：`sessions`（会话：id、canvasId、userId、status、createdAt）、`task_turns`（每次 turn：id、sessionId、releaseId、message、status、promptHash、toolCallCount、outcome）、`task_events`（Event Log：turn 内每个工具调用/状态迁移/确认结果，强一致顺序）、`checkpoints`（turn 级：启动时写快照，工具副作用落库即天然 checkpoint，崩溃后按 checkpoint 判定恢复或标记失败）。改造后：turn 中途崩溃可「从已落库副作用 + 事件序列」向用户/上层给出确定性失败结论，而不是「消息消失」。

**A-2 引入 Agent Release（生命周期最小发布单元）。**
把 `prompt.ts` 文案、`tools.ts` 工具声明、runtime 版本、codex 版本下限、路由配置打包为版本化 `AgentDefinition`（如 `agent-definitions/v1.ts`），写入库并在每次 turn 记录 `releaseId`；升级即新 release，trace 可关联到具体 release，为复现与回滚打底。对应第 2.4.1 节六类要素中的 Prompt/Context/Skill/Tool/Runtime 版本化。

**A-3 建立 CI + 协议漂移门禁。**
GitHub Actions（或等价）：`pnpm -r typecheck && pnpm -r test` + `codex:protocol-schema` 重新生成并 `diff` 与 `protocol.ts` 的差异（差异过大即红）。把 ADR-0009 修订里的「手工比对纪律」变成流水线门禁。

**A-4 建立最小评估基线（Quality 对象）。**
构造一组 golden user stories（输入消息 → 期望的最终画布状态：图层数、SVG 内容断言、工具调用序列、revision 单调性），写成 `test/eval/` 下的回归用例；每个新 release 必须通过。这是「评估基线」的最轻形态，为阶段 C 的 Evaluator 留接口。

**A-5 观测补成本与 Outcome。**
turn 记录 token/费用（如 codex 事件可得；不可得则按 turn+toolCallCount 估算并标注口径）；定义机器可判定的 Outcome（如：turn 完成 + 全部工具成功 + 无 revision_conflict 遗留 + 用户未手动撤销 = `success`；否则 `needs_review`），写入 task_turns.outcome。

### 阶段 B：企业化（多用户/多画布，治理完备）

**B-1 身份与租户。**
引入 `users`/`tenants` 与画布归属；daemon API 鉴权（本地可先 bearer token，企业化接 SSO/IAM）；所有表加 `tenantId`/`userId` 隔离键；每租户配额与预算。

**B-2 集中 Policy 层（Control 对象）。**
把「哪个工具、什么参数、什么风险级别需要确认」抽成 `Policy`（allow/deny/ask 判定函数 + 风险分级表），确认通道保留但由 Policy 驱动；审批留痕（谁、何时、结果、关联 turnId）。对应第 2 章「策略集中定义、判定点分布式执行」。

**B-3 AI Gateway 化（LLM/MCP/Agent 三层起步）。**
把 codex 接入收敛为 LLM 接入适配层（可路由：规划/执行/摘要任务走不同配置；可降级；有限流）；加 Token 成本记录；为未来 MCP 工具预留 Tool Registry（Server 注册、凭证托管、工具级 ACL 的接口位）。评估是否引入 MCP：ADR-0009 拒绝 MCP 的理由在单机成立，但企业化后「能力发现、凭证、审计」需要注册表面，可在 Gateway 层先留接口不实现。

**B-4 服务端制品存储（Artifact Store）。**
引入服务端 SVG→PNG 渲染（sharp 或等效），`canvas_render_preview` 不再依赖浏览器在线回传；导出/缩略图服务端生成并入制品表（可寻址、可保留、关联 turn）。浏览器渲染保留为「交互预览」的客户端优化，不再是唯一通道。

**B-5 任务队列与恢复。**
把 turn 提交进任务队列（单画布串行、跨画布并行）；幂等键 = canvasId + messageHash；daemon 重启后从 `task_turns` 恢复或明确标记失败，遵守「先核对副作用再决定 Resume/Retry/转人工」（第 3.3.2 节）。

**B-6 Memory 与 Knowledge（可选起步）。**
新增 `memories`（用户偏好、跨会话事实：如常用色板/风格），由 prompt 注入或新增工具读取，带写入策略与删除入口；业务知识库按需接入（权限过滤 + 来源可追溯）。

### 阶段 C：平台化（规模化/多 Agent）

**C-1 三平面分离。**
执行面（worker 池 + 队列 + 每任务 sandbox）、数据与资源面（Task State/Event/Checkpoint/Workspace/Artifact/Memory/Knowledge 独立存储）、控制面（Agent Registry/Model & Tool Registry/Tenant/IAM/Policy/Budget/Deployment/Observability/Evaluation/Audit）。对应第 2.3.2 节表 2-4。

**C-2 多 Agent 与协作。**
规划 Agent + 执行 Agent 拆分；Subagent 并行构图（如多图层同时生成）与 Handoff 契约；Task/Dependency/Delegation/Result 聚合语义。对应第 3.6 节 Agent Team。

**C-3 安全升级。**
若未来工具需要动文件/网络：容器级 sandbox（每任务隔离），短期凭证，网络出站白名单，数据保留策略；高风险策略（凭证吊销/租户封禁）辅以强制刷新。

**C-4 部署形态选型。**
从「应用内嵌」走向表 2-5 的「托管控制面 + 私有执行面」（若数据边界敏感）或「托管 Harness 与 Runtime」（若可接受外包）；容器化 daemon，标准 health/readiness、优雅关停（当前 onClose 已有）、日志导出到集中平台。

### 不建议做的事（避免过度工程）

- **阶段 A/B 不要引入通用 Agent Framework**（AgentScope/LangChain）：PaintCodex 的差异化恰在「人机同权 + 画布状态语义」，通用框架会稀释它；保持自建但补齐契约。
- **不要为单用户本地场景建设完整 IAM/容器池**：B/C 阶段的能力只在进入多用户/云端时启用，符合「最低充分架构」。
- **不要丢掉确认通道换 Codex approval policy**：两类授权不是同一件事（ADR-0009 §6 修订的结论继续成立）。

---

## 8. 结论

PaintCodex 作为个人教学项目，在「Harness 编排层」这一责任域上的完成度显著高于同类项目，尤其在**状态语义、失败可见性、上下文策略、确认 fail-closed、可观测**五个子域；它缺的不是「再多写一些代码」，而是**把一次性 turn 提升为可恢复的任务、把 prompt+工具+运行环境提升为版本化 Agent Release、把 trace 提升为评估证据**这三件生命周期层面的事（对应第 2 章 P0-1~P0-4）。

改造顺序建议严格按 A→B→C：**先让每一次任务可复现、可恢复、可判定（A）**，再谈多用户与治理（B），最后平台化（C）。每一阶段都保持「被授予的自主性都有匹配的边界、证据和验证手段」（第 2 章原则五的表述）。

---

## 附录：证据来源

### PaintCodex 代码与文档（`C:\Users\Administrator\Documents\Src\PaintCodex`）

- `MISSION.md`（目标：把 Codex 变成 Web 产品的 AI 引擎；Out of scope 明确排除多 agent/计费）
- `docs/architecture-design.md`、`docs/adr/0002-codex-cli-local-process.md`、`docs/adr/0006-agent-observability.md`、`docs/adr/0009-ai-drives-canvas-through-codex-dynamic-tools.md`（含 2026-10-28 修订：无 CI、崩溃懒重启、协议子集转写、确认通道自建）
- `apps/daemon/src/main.ts`、`api/server.ts`（版本闸门、装配、onClose）、`api/routes.ai.ts`（SSE 流与 render/export 通道）
- `paint/agent/runtime/codex-runtime.ts`（thread/turn/工具队列/确认/懒重启/thread resume/沙箱参数 `sandbox:'read-only', approvalPolicy:'never'`）
- `paint/agent/runtime/tools.ts`（8 工具声明与执行、`{ok:false,code,message}`）
- `paint/agent/runtime/confirmation.ts`（60s 超时、settledRetention、canvas 隔离）
- `paint/agent/prompt.ts`（拉为主上下文）
- `paint/command-dispatcher.ts`、`paint/service.ts`（人机同权、actor 归因、undo 快照）
- `storage/database.ts`（5 表 schema）
- `.scratch/codex-native-tools/issues/08-quality-debt.md`（重复实现债务清单）
- `apps/daemon/test/`（40 个测试文件）

### 参考框架（`C:\Users\Administrator\Documents\Src\harness-learning\01-projects\ai-agent-handbook-main`）

- `01-architecture/第 2 章　Agentic Application 参考架构.md`（三视图 / 五责任域 / 五原则 / Runtime·Sandbox·State·Gateway / Agent Release / 五阶段闭环 / 表 2-5 部署形态）
- `02-build/第 3 章 范式：Harness 的主流构建方式和责任边界.md`（Agent=Model+Harness / 四类构建入口表 3-2 / 工程对象清单 3.1.2 / 分布式化要求 3.2.2 / Session Store 边界 3.3.2 / Agent Platform 3.6）

### Codex CLI 官方文档（`02-docs/codex-cli-docs/`，2026-10-31 抓取）

- `03-命令参考与自动化.md` / `source/developer-commands.md`：`codex app-server` 定位 —— "primarily for development and debugging and may change without notice"（源档第 95 行）；`--experimental` 生成 schema
- `07-环境与沙箱.md` / `source/sandboxing.md`：沙箱模式（`read-only` 等）、`approval_policy`（`never`/`on-request`）、worktree/会话隔离
- `08-权限与安全.md` / `source/permissions.md`：权限 Profiles、最小权限、审批策略（`on-request`/`never`/`granular`）

# OpenAI Codex 中文资料 · 索引

本目录为 OpenAI Codex 系列学习资料的主体域（由原离线资料包整理归档），按产品大类分为三个子目录：**Codex CLI**、**Codex App Server**、**Codex SDK**。从本文件开始，按分类进入对应资料集。

抓取日期：2026-10-30 ~ 2026-10-31

---

## 一、资料分类导航

| 分类 | 目录 | 内容简介 | 入口 |
|---|---|---|---|
| **1. Codex CLI（终端 AI 编程助手）** | `codex-cli/` | Codex CLI 产品介绍、命令参考、配置（基础/高级/参考）、Agent 配置、环境与沙箱、权限与安全、扩展能力（MCP/技能/插件/代码审查/图片输入/联网搜索/Cloud）、故障排查；**31 页英文原文存档 + 中文主题页** | [01-索引.md](codex-cli/01-索引.md) |
| **2. Codex App Server（嵌入产品与协议集成）** | `code-app-server/` | 连接 CLI 终端 UI、协议与传输（stdio/WebSocket/Unix socket）、消息结构（JSON-RPC 2.0）、完整 API 概览、聊天/轮次/审批/技能/应用/身份验证；**1 页中文原文存档（codex-docs.com 中文整理站）** | [01-索引.md](code-app-server/01-索引.md) |
| **3. Codex SDK（编程式控制与安全扫描）** | `codex-sdk/` | Codex SDK（TypeScript/Python 库、沙箱预设）+ Codex Security SDK（安全扫描）；**2 页中文原文存档（codex-docs.com 中文整理站）** | [01-索引.md](codex-sdk/01-索引.md) |

> 来源说明：`codex-cli/` 源自 OpenAI 官方文档站 learn.chatgpt.com，为英文原文 + 中文翻译整理；`code-app-server/` 与 `codex-sdk/` 源自第三方中文整理站 codex-docs.com，原文即为中文，直接存档。

---

## 二、每份资料的使用方式

### 1. Codex CLI 中文资料（codex-cli/）
- **断网阅读入口**：`codex-cli/01-索引.md`
- 结构：`source/`（31 个英文原文存档）+ `00-说明.md`（任务与来源清单）+ `01-索引.md`（总览）+ 02–10 九个中文主题页
- 阅读顺序：`00-说明.md` → `01-索引.md` → 按主题阅读 02–10

### 2. Codex App Server 中文资料（code-app-server/）
- **断网阅读入口**：`code-app-server/01-索引.md`
- 结构：`source/`（1 个中文原文存档）+ `00-说明.md`（任务与来源说明）+ `01-索引.md`（总览）

### 3. Codex SDK 中文资料（codex-sdk/）
- **断网阅读入口**：`codex-sdk/01-索引.md`
- 结构：`source/`（2 个中文原文存档）+ `00-说明.md`（任务与来源说明）+ `01-索引.md`（总览）

---

## 三、离线拷贝指引

- 本目录（含 `codex-cli/`、`code-app-server/`、`codex-sdk/`、`README.md`）可整体拷贝进内网（U 盘 / 内网共享均可）。
- 所有页面均为本地相对链接，正文不依赖外网资源；`code-app-server/` 与 `codex-sdk/` 存档中指向 codex-docs.com 其它页面的站内链接离线不可用，仅作原始引用保留。
- 若内网需要网页版阅读，可另行将 md 系列转为 HTML/PDF（需另行处理）。

> 归档说明：2026-10-31 由原「离线包」结构（`003-codex-cli-docs/`、`004-codex-sdk-appserver/` + 顶层总入口 README）整理为本目录结构，分类与来源信息不变。

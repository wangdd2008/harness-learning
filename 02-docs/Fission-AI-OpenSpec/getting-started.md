# 开始使用

本指南解释了安装和初始化 OpenSpec 后它的工作方式。有关安装说明，请参阅[主 README](../README.md#quick-start)或[安装指南](installation.md)。刚接触整套文档？[文档首页](README.md)提供了完整地图。

> **我在哪里输入这些命令？**两个地方，混淆它们是最常见的早期失误。
>
> - `openspec ...` 命令（如 `openspec init`）在你的**终端**中运行。
> - `/opsx:...` 命令（如 `/opsx:propose`）在你的**AI 助手的聊天**中运行，与你要求它编写代码的同一个框中。
>
> 没有单独的"交互模式"需要启动。你只需在聊天中输入斜杠命令，你的助手就会接手。完整解释：[命令如何工作](how-commands-work.md)。

## 你的前五分钟

整个循环，每个步骤都标明了发生地点：

```text
终端   $ npm install -g @fission-ai/openspec@latest
终端   $ cd your-project && openspec init
AI 聊天  /opsx:explore                    （可选：先想清楚）
AI 聊天  /opsx:propose add-dark-mode      （AI 起草计划；你审查它）
AI 聊天  /opsx:apply                      （AI 构建它）
AI 聊天  /opsx:archive                    （规格更新，变更归档）
```

两个终端步骤来设置，然后你就生活在聊天中。本指南的其余部分解释了每个步骤的作用以及你会看到什么。

**不想自己做终端部分？**将[设置提示](installation.md#install-with-your-ai-assistant)粘贴到你的助手中，它会处理这两行，然后报告它创建了什么。

> **还不确定要构建什么？从 `/opsx:explore` 开始。**它是一个无风险的思考伙伴，阅读你的代码库，权衡选项，并将一个模糊的想法变成一个具体的计划，一切都在编写任何代码之前。当画面清晰时，它会移交给 `/opsx:propose`。这是与 AI 一起工作的最佳习惯，否则它会自信地构建错误的东西。请参阅[探索指南](explore.md)。

## 它是如何工作的

OpenSpec 帮助你和你的 AI 编程助手在编写任何代码之前就构建什么达成一致。

**默认快速路径（核心配置文件）：**

```text
/opsx:explore ──► /opsx:propose ──► /opsx:apply ──► /opsx:sync ──► /opsx:archive
   （可选）
```

当你弄清楚要做什么时从 `/opsx:explore` 开始，或者当你已经知道时直接跳到 `/opsx:propose`。探索在默认配置文件中，所以当你想要时它总是在那里。

**扩展路径（自定义工作流选择）：**

```text
/opsx:new ──► /opsx:ff 或 /opsx:continue ──► /opsx:apply ──► /opsx:verify ──► /opsx:archive
```

默认的全局配置文件是 `core`，包括 `propose`、`explore`、`apply`、`update`、`sync` 和 `archive`。你可以通过 `openspec config profile` 启用扩展工作流命令，然后运行 `openspec update`。

## OpenSpec 创建了什么

运行 `openspec init` 后，你的项目具有以下结构：

```
openspec/
├── specs/              # 真相的来源（你的系统行为）
│   └── <domain>/
│       └── spec.md
├── changes/            # 提议的更新（每个变更一个文件夹）
│   └── <change-name>/
│       ├── proposal.md
│       ├── design.md
│       ├── tasks.md
│       └── specs/      # 差异规格（正在更改的内容）
│           └── <domain>/
│               └── spec.md
└── config.yaml         # 项目配置（可选）
```

**两个关键目录：**

- **`specs/`** - 真相的来源。这些规格说明描述了你的系统当前的行为。按领域组织（例如 `specs/auth/`、`specs/payments/`）。

- **`changes/`** - 提议的修改。每个变更都有自己的文件夹，包含所有相关产物。当变更完成时，其规格说明会合并到主 `specs/` 目录中。

## 理解产物

每个变更文件夹包含指导工作的产物：

| 产物 | 目的 |
|------|------|
| `proposal.md` | "为什么"和"什么" - 捕获意图、范围和方法 |
| `specs/` | 显示 新增/修改/删除 需求的差异规格 |
| `design.md` | "如何" - 技术方法和架构决策 |
| `tasks.md` | 带有复选框的实现清单 |

**产物相互构建：**

```
proposal ──► specs ──► design ──► tasks ──► implement
   ▲           ▲          ▲                    │
   └───────────┴──────────┴────────────────────┘
            随着你的学习而更新
```

你随时可以返回并优化早期的产物，当你在实施过程中学到更多时。

## 差异规格如何工作

差异规格是 OpenSpec 中的关键概念。它们显示了相对于当前规格说明的变化。

### 格式

差异规格使用章节来表示变更类型：

```markdown
# Auth 的差异

## 新增需求

### 需求：双因素认证
系统必须要求登录时提供第二个因素。

#### 场景：需要 OTP
- 给定一个启用了 2FA 的用户
- 当用户提交有效凭据时
- 然后会呈现 OTP 挑战

## 修改需求

### 需求：会话超时
会话将在 30 分钟不活动后过期。
（之前：60 分钟）

#### 场景：空闲超时
- 给定一个已认证的会话
- 当 30 分钟过去而没有活动时
- 然后会话失效

## 移除需求

### 需求：记住我
（已弃用，改为支持 2FA）
```

### 归档时会发生什么

当你归档一个变更时：

1. **新增** 需求被追加到主规格说明中
2. **修改** 需求替换现有版本
3. **移除** 需求从主规格说明中删除

变更文件夹移动到 `openspec/changes/archive/` 以供审计历史使用。

## 示例：你的第一次变更

让我们逐步介绍向应用程序添加深色模式。

### 1. 开始变更（默认）

```text
你：/opsx:propose add-dark-mode

AI： 创建了 openspec/changes/add-dark-mode/
     ✓ proposal.md — 我们为什么这样做，正在更改什么
     ✓ specs/       — 需求和场景
     ✓ design.md    — 技术方法
     ✓ tasks.md     — 实现清单
     准备好实现！
```

如果你启用了扩展工作流配置文件，你也可以将其分为两个步骤：`/opsx:new` 然后 `/opsx:ff`（或 `/opsx:continue` 增量地）。

### 2. 创建了什么

**proposal.md** - 捕获意图：

```markdown
# 提议：添加深色模式

## 意图
用户请求一个深色模式选项以减少夜间使用时的眼睛疲劳。

## 范围
- 在设置中添加主题切换
- 支持系统偏好检测
- 在 localStorage 中持久化偏好

## 方法
使用 CSS 自定义属性进行主题设置，并使用 React context 进行状态管理。
```

**specs/ui/spec.md** - 显示新需求的差异：

```markdown
# UI 的差异

## 新增需求

### 需求：主题选择
系统应允许用户在浅色和深色主题之间进行选择。

#### 场景：手动切换
- 给定任何页面上的用户
- 当用户点击主题切换时
- 然后主题立即切换
- 并且偏好跨会话持久化

#### 场景：系统偏好
- 给定一个没有保存偏好的用户
- 当应用程序加载时
- 然后使用系统偏好的配色方案
```

**tasks.md** - 实现清单：

```markdown
# 任务

## 1. 主题基础设施
- [ ] 1.1 创建带有浅色/深色状态的 ThemeContext
- [ ] 1.2 为颜色添加 CSS 自定义属性
- [ ] 1.3 实现 localStorage 持久化

## 2. UI 组件
- [ ] 2.1 创建 ThemeToggle 组件
- [ ] 2.2 在设置页面添加切换
- [ ] 2.3 更新 Header 以包含快速切换

## 3. 样式
- [ ] 3.1 定义深色主题调色板
- [ ] 3.2 更新组件以使用 CSS 变量
```

### 3. 实现

```
你：/opsx:apply

AI： 正在处理任务...
     ✓ 1.1 创建了带有浅色/深色状态的 ThemeContext
     ✓ 1.2 向 globals.css 添加了 CSS 自定义属性
     ✓ 1.3 实现了 localStorage 持久化
     ✓ 2.1 创建了 ThemeToggle 组件
     ...
     所有任务完成！
```

在实施过程中，如果你发现设计需要调整，只需更新产物并继续。

### 4. 归档

```
你：/opsx:archive

AI： 正在归档 add-dark-mode...
     ✓ 规格已合并到 openspec/specs/ui/spec.md
     ✓ 移动到 openspec/changes/archive/2025-01-24-add-dark-mode/
     完成！准备好进行下一个功能。
```

你的差异规格现在已成为主规格的一部分，记录着你的系统如何工作。

## 验证和审查

使用 CLI 检查你的变更：

```bash
# 列出活跃变更
openspec list

# 查看变更详情
openspec show add-dark-mode

# 验证规格格式
openspec validate add-dark-mode

# 交互式仪表板
openspec view
```

## 下一步

- [先探索](explore.md) - 使用 `/opsx:explore` 在承诺之前思考一个想法
- [审查变更](reviewing-changes.md) - 在编写任何代码之前检查 AI 起草的计划
- [编写好的规格](writing-specs.md) - 强大的需求和场景是什么样的
- [在现有项目中使用 OpenSpec](existing-projects.md) - 在大型遗留代码库上开始
- [编辑和迭代变更](editing-changes.md) - 更新产物、回退、协调手动编辑
- [核心概念速览](overview.md) - 一页纸上的完整心智模型
- [示例与配方](examples.md) - 真实变更，从头到尾
- [工作流](workflows.md) - 常见模式以及何时使用每个命令
- [命令](commands.md) - 所有斜杠命令的完整参考
- [概念](concepts.md) - 对规格说明、变更和模式的深入理解
- [自定义](customization.md) - 让 OpenSpec 按你的方式工作
- [存储](stores-beta/user-guide.md) - 规划跨越仓库或团队？将其保存在自己的仓库中（测试版）
- [常见问题](faq.md)和[故障排除](troubleshooting.md) - 当你卡住时

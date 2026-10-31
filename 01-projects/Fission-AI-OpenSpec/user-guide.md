# Store：在独立仓库中规划

> **测试版。** Store、引用、工作上下文和工作集是
> 新功能。命令名称、标志、文件格式和 JSON 输出在版本之间仍可能
> 发生变化。以下每个演练都是针对当前构建运行的，但升级后请重新阅读本指南。

## 它解决的问题

OpenSpec 通常存在于一个代码仓库中：一个 `openspec/` 文件夹紧挨着
你的代码，为该仓库保存规格和变更。

当你的规划超过一个仓库时，这就不管用了：

- 你的工作跨越多个仓库——一个功能涉及 API 服务器、
  Web 应用和共享库。谁的 `openspec/` 文件夹应该存放这个计划？
- 你的团队在代码存在之前进行规划，或规划永远不会变成
  *这个*仓库中代码的内容。
- 需求由一个团队拥有，由其他团队消费。Wiki
  版本会漂移，而且你的编码 Agent 反正也读不了。

**Store** 就是答案：一个独立的仓库，其全部工作就是规划。
它有你已熟悉的相同 `openspec/` 结构——规格和变更——
再加上一个小的身份文件。你在你的机器上按名称注册一次，
然后每个正常的 OpenSpec 命令都可以从任何地方在其中工作。

## 结构

```
            team-plans  (一个 store: 在独立仓库中规划)
            ├── .openspec-store/store.yaml     身份: "我是 team-plans"
            └── openspec/
                ├── specs/      什么是对的
                └── changes/    什么在进行中
                      ▲
                      │ 在每台机器上按名称注册;
                      │ 像任何仓库一样通过推送/克隆共享
        ┌─────────────┼─────────────┐
        │             │             │
    web-app       api-server     mobile-app
   (代码仓库)   (代码仓库)    (代码仓库)
```

两条规则保持简单：

1. **Store 只是一个 git 仓库。** 你自己提交、推送、拉取和审查它。
   OpenSpec 不会自动克隆、同步或推送任何内容。
2. **声明而非机制。** 仓库可以*声明*它们与 store 的关系
   （如下所示）。声明改变 OpenSpec 能告诉你什么——
   永远不是命令在哪里执行。

## 五分钟创建你的第一个 store

两个命令让你从无到有到拥有一个有效的、store 范围的变更：

```bash
openspec store setup team-plans --path ~/openspec/team-plans
```

```
Store ready: team-plans
Location: /Users/you/openspec/team-plans
OpenSpec root: ready
Registry: registered

Next: 运行普通的 OpenSpec 命令针对此 store，例如：
  openspec new change <change-id> --store team-plans
通过像任何 Git 仓库一样提交和推送来共享此 store。
```

```bash
openspec new change add-login --store team-plans
```

```
Using OpenSpec root: team-plans (/Users/you/openspec/team-plans)
Created change 'add-login' at /Users/you/openspec/team-plans/openspec/changes/add-login/
Schema: spec-driven
Next: openspec status --change add-login --store team-plans
```

这就是整个模型。从这里开始，生命周期正是你所知道的——
`status`、`instructions`、`validate`、`archive`——每个命令都带上 `--store team-plans`，
每个打印的提示都为你携带该标志。`Using OpenSpec root:` 这一行始终告诉你命令正在哪里执行。

## 故事：一个团队，一个规划仓库

一个团队将其规格和变更保存在 `team-plans` 中，而不是分散在
代码仓库里。

**第一天（无论谁设置它）：**

```bash
openspec store setup team-plans --path ~/openspec/team-plans \
  --remote git@github.com:acme/team-plans.git
git -C ~/openspec/team-plans push -u origin main
```

传递 `--remote` 在 store 自己的身份
文件（`.openspec-store/store.yaml`）的初始提交中记录克隆 URL。未来每次
克隆都知道它来自哪里，因此健康检查和错误
消息可以为尚未获得它的队友打印一个完整的、可粘贴的修复。

**每个队友（每台机器一次）：**

```bash
git clone git@github.com:acme/team-plans.git ~/openspec/team-plans
openspec store register ~/openspec/team-plans
```

从那时起，每个人都在同一个规划仓库中按名称工作：

```bash
openspec status --store team-plans --change add-login
openspec show add-login --store team-plans
```

**共享工作是 git，这是故意的。** 你创建的变更
只存在于你的本地检出中，直到你提交并推送它——与代码一样。计划免费获得分支、拉取请求和审查，因为 store 是一个普通的仓库。

**连接团队的代码仓库。** 一个规划完全外部化的代码仓库只需要一行，在 `openspec/config.yaml` 中：

```yaml
# web-app/openspec/config.yaml
store: team-plans
```

现在在 `web-app` 中运行的每个 OpenSpec 命令都作用于 `team-plans`，而
无需任何标志：

```bash
cd ~/src/web-app
openspec status --change add-login
```

```
Using OpenSpec root: team-plans (/Users/you/openspec/team-plans)
...
```

这个指针是后备，不是覆盖：显式的 `--store` 总是
胜出，如果仓库有了自己的真实规划文件夹，那些会胜出
（并带有警告以移除过时的指针）。

**你机器上每个仓库的默认设置。** 如果你在许多
都计划到同一个 store 的代码仓库中工作，请全局设置一次，
而不是在每个仓库中添加 `store:` 行：

```bash
openspec config set defaultStore team-plans
```

现在任何在规划根之外运行的命令——且没有 `--store` 且没有
项目指针——都会解析为 `team-plans`。它位于优先级列表的底部，因此 `--store`、本地根和项目 `store:` 指针
都会胜出。根横幅和 JSON `root` 块报告
`source: "global_default"` 以及 store id，因此你总是可以分辨出
全局默认设置和仓库自己的指针。使用
`openspec config unset defaultStore` 清除它。如果 id 未注册，命令
会报错并告诉你注册它或清除过时的默认设置。

## 示例：一个功能，两个组件仓库

假设 `add-checkout-promo` 同时更改了 `checkout-api` 和
`checkout-web`。团队想要一个共享的产品契约，而每个代码
仓库仍需要自己的实现任务、分支和审查。

使用两层：

1. 将共享行为保留在 `team-plans` 中。
2. 在每个组件仓库中保留实现计划，并将 store
   作为只读上游上下文引用。

首先，在 store 中规划共享契约：

```bash
openspec new change add-checkout-promo --store team-plans
openspec status --change add-checkout-promo --store team-plans
```

提案和规格应描述组件边界处的
行为——例如，服务返回的促销字段
以及前端如何处理不合格的结账。像审查任何其他分支和拉取请求一样在 store 仓库中审查此变更。

### 规划能看到什么上下文？

选择 store 会改变 OpenSpec 根；它不会发现或读取
使用该 store 的每个代码仓库。Store 指令看到 store 中的产物
和配置的上下文。它们仅在那些
文件夹也对 Agent 或编辑器可用且 Agent 读取它们时，才能看到组件代码。

工作集是一种方便的方式，将规划 store 和两个代码仓库
一起打开：

```bash
openspec workset create checkout-promo \
  --member ~/openspec/team-plans \
  --member ~/src/checkout-api \
  --member ~/src/checkout-web \
  --tool code
openspec workset open checkout-promo
```

这使文件夹在一个 IDE 工作区中可见。它不会将源
上下文复制到 store 中，选择受影响的仓库，或授予 Agent
编辑它们的权限。将持久的跨组件事实放在共享规格中；不要
依赖规划者记住它碰巧检查过的源。

### 实现如何在每个仓库中开始？

当没有显式的 `--store` 或更近的 `openspec/` 根适用时，一个
`store: team-plans` 指针将命令路由到该 store。它不会根据
调用 `apply` 的目录拆分一个 store 任务列表。OpenSpec
目前不会将任务路由到仓库。

当每个组件需要一个独立范围的 apply/review 周期时，给它
一个本地的 OpenSpec 根并引用中心 store，而不是指向
它：

```yaml
# checkout-api/openspec/config.yaml (同样在 checkout-web 中)
schema: spec-driven
references:
  - team-plans
```

在共享契约被批准并在 store 的主
规格中可用后，为组件的部分创建一个小的本地变更：

```bash
cd ~/src/checkout-api
openspec new change implement-checkout-promo-api

cd ~/src/checkout-web
openspec new change implement-checkout-promo-ui
```

每个仓库的指令中的引用索引提供 store 规格的
摘要和精确的 `openspec show ... --store team-plans` 获取命令。每个
本地提案引用该共享契约，其任务仅描述该组件中的工作。然后分别在每个仓库中运行 `/opsx:apply`；根
解析保持产物和实现编辑限定在该仓库内。
服务和前端变更现在可以独立测试、审查、合并
和归档。

如果实现必须在共享 store 变更仍处于活跃状态时开始，
使用
`openspec show add-checkout-promo --store team-plans` 显式获取它；引用索引列出
规范的 store 规格，而非活跃的 store 变更。在它们的拉取请求描述中保持 store 分支和
组件分支的链接，以便审查者可以看到每个实现遵循的是哪个版本的契约。

## 故事：跨团队线的需求

一个平台团队拥有需求。产品团队基于它们构建，
在他们自己的仓库中，用他们自己的设计。一个引用描述了该
关系，而不会移动任何人的工作。

```
   platform-reqs (store)                 api-server (代码仓库)
   由平台团队拥有                         由产品团队拥有
   ┌──────────────────────────┐          ┌──────────────────────────┐
   │ openspec/specs/          │ ◀────────│ openspec/config.yaml     │
   │   payments/spec.md       │ 读取     │   references:            │
   │   auth/spec.md           │          │     - platform-reqs      │
   │                          │          │ openspec/specs/          │
   │ openspec/changes/        │          │   (他们自己的设计)        │
   │   平台工作                │          │ openspec/changes/        │
   │                          │          │   (他们自己的工作)        │
   │                          │          └──────────────────────────┘
   └──────────────────────────┘
```

**产品团队声明它依赖什么** 在其仓库的
`openspec/config.yaml` 中：

```yaml
references:
  - platform-reqs
```

引用是只读上下文。仓库保留自己的 `openspec/` 根；
工作留在那里。变化的是：该仓库中的 `openspec instructions` 现在
包含引用 store 规格的索引——每个规格都有一行
摘要和精确的获取命令（`openspec show <spec-id> --type spec
--store platform-reqs`）。在 `api-server` 中工作的 Agent 可以找到
上游支付需求，引用它们，并在
仓库自己的根中编写其低级设计——无需任何人粘贴上下文。

一个引用可以携带其克隆源，因此尚未获得 store 的队友会获得一个完整的修复，而不是死胡同：

```yaml
references:
  - { id: platform-reqs, remote: "git@github.com:acme/platform-reqs.git" }
```

**当你想将计划和代码一起打开时，使用工作集。** 这是
个人的和显式的：每个人选择他们实际在
其机器上工作的文件夹。关于这些本地检出路径没有任何内容
被提交到共享规划仓库。

```bash
openspec workset create platform \
  --member ~/openspec/platform-reqs \
  --member ~/src/api-server \
  --member ~/src/web-app
```

## 你总是可以问的两个问题

**"我的设置健康吗？"** — `openspec doctor` 检查当前根及其
引用的 store，只读，每个发现提供一个可粘贴的修复：

```
Doctor

Root
  Location: /Users/you/src/api-server
  OpenSpec root: ok

References
  - platform-reqs: ok (/Users/you/openspec/platform-reqs)
  - design-system: Referenced store 'design-system' is not registered on this machine.
    Fix: git clone -- git@github.com:acme/design-system.git '/Users/you/openspec/design-system' && openspec store register '/Users/you/openspec/design-system' --id design-system

```

**"我在用什么工作？"** — `openspec context` 从 OpenSpec 声明组装工作
集：根及其引用的 store。

```
Working context for api-server (/Users/you/src/api-server)

OpenSpec root
  api-server  /Users/you/src/api-server

Referenced stores
  platform-reqs  /Users/you/openspec/platform-reqs
    Fetch: openspec show <spec-id> --type spec --store platform-reqs
```

两者都支持 `--json` 用于 Agent。`openspec context --code-workspace
<path>` 另外写入一个 VS Code 工作区文件，包含整个
集合——这是此命令唯一执行的写入操作。

## 工作集：重新打开你一起工作的文件夹

与上述所有内容分开：大多数人每次会话都打开相同的几
个文件夹——规划仓库加两三个代码仓库。
**工作集** 就是这一点的个人、命名视图，用一个
命令在你的工具中重新打开。

```
  workset "platform"                 openspec workset open platform
  ├── team-plans   ~/openspec/team-plans         │
  ├── api-server   ~/src/api-server              ▼
  └── web-app      ~/src/web-app       全部在你的工具中打开
```

```bash
openspec workset create platform \
  --member ~/openspec/team-plans --member ~/src/api-server \
  --tool code
openspec workset list
```

```
platform  (在 VS Code 中打开)
  team-plans  /Users/you/openspec/team-plans
  api-server  /Users/you/src/api-server
```

`openspec workset open platform` 然后启动保存的工具：编辑器
（VS Code、Cursor）用一个窗口打开每个成员并返回。第一个
成员是主要的。任何时候都可以用 `--tool <id>` 覆盖工具。

工作集故意*不是*共享状态。它们存在于你的机器上，
永远不会被提交，并且不对工作做任何声明——它们只记录
你喜欢一起打开什么。移除一个永远不会触及成员
文件夹。新工具是配置，而非代码：任何通过
工作区文件或每个文件夹附加标志启动的工具都可以添加在全局
配置（`openspec config edit`）中的 `openers` 键下。

## 命令如何决定在哪里执行

每个普通命令以相同方式解析其根，按此顺序：

```
1. --store <id>          你显式指定了                → 那个 store
2. 最近的 openspec/      这里有一个真正的规划根        → 这个仓库
   (从 cwd 向上遍历)
3. store: 指针           config.yaml 声明了一个 store    → 那个 store
4. defaultStore          全局配置设置了机器            → 那个 store
                         默认
5. 以上都不是             这台机器上注册了 store?          → 报错并给出
                                                         选择提示
                         没有注册 store?                  → 当前目录
                                                         (经典行为)
```

`Using OpenSpec root:` 这一行（以及 `--json` 输出中的 `root` 块）
告诉你处于哪种情况。

## 已知限制

- **测试版形状。** 此页面上的所有内容在版本之间都可能变化——
  名称、标志、文件格式、JSON 键。
- **每台机器每个 store id 一个检出。** 在同一 id 下注册第二个检出会失败，并提示先 `store unregister`。
- **永远不会同步——这是设计上的。** OpenSpec 不会克隆、拉取或推送。
  过时的检出显示过时的规格，直到*你*拉取；引用从磁盘上的任何内容实时索引。
- **空规划文件夹可能不存在。** 新 store 可能在 Git 中还没有
n  `openspec/changes/`、`openspec/specs/` 或 `openspec/changes/archive/`。
  这在测试版期间是被接受的；一旦正常
  命令为它们创建文件，这些文件夹就会出现。
- **指针仓库保持指针。** 一个仅在 `openspec/config.yaml` 中声明了
  `store: <id>` 的仅配置仓库被视为外部化
  规划，而非要注册的本地 store 根。如果你有意想将该仓库转换为本地 store 根，请先移除 `store:` 行。
- **一些命令保持原地。** `templates` 和已弃用的名词形式（`openspec change show`，...）仅在当前
  目录上执行——没有 `--store`。`schemas` 遵循规范的根选择
  优先级并接受 `--store <id>`，同时保持其成功的 JSON 数组
  形状不变。
- **每台机器的状态是每台机器的。** Store 注册表和工作集
  是本地设置。关于你的机器布局没有任何内容
n  会被提交到共享规划中。
- **工作集有两种启动方式。** 一个无法通过工作区文件或每个文件夹附加标志启动的工具不能作为 opener 添加。
- **Agent JSON 有已知的驼峰大小写分割**（store 系列键是
  snake_case，工作流系列是 camelCase）。文档记载于
  [agent contract](../agent-contract.md)；统一它已推迟到
  版本化发布。

## 东西在哪里

| 内容 | 位置 | 共享? |
|---|---|---|
| Store 的规划 | `<store>/openspec/` (specs, changes) | 是 — 提交并推送它 |
| Store 的身份 | `<store>/.openspec-store/store.yaml` | 是 — 与 store 一起提交 |
| Store 注册表 | `<data dir>/openspec/stores/registry.yaml` | 否 — 仅限本机 |
| 工作集 | `<data dir>/openspec/worksets/` | 否 — 仅限本机 |

`<data dir>` 在 macOS 和 Linux 上是 `~/.local/share/openspec`（或
`$XDG_DATA_HOME/openspec` 当设置时），在 Windows 上是 `%LOCALAPPDATA%\openspec`。

## 参考

此页面每个命令的精确标志和 JSON 形状：
[CLI 参考](../cli.md)（Store、Doctor、工作上下文、个人
工作集）和 [agent contract](../agent-contract.md)。

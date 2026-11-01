# 安装

## 先决条件

- **Node.js 20.19.0 或更高版本** — 检查你的版本：`node --version`

## 用你的 AI 助手安装

不想手动操作？将下面的提示粘贴到任何可以运行 shell 命令的编程助手中 — Claude Code、Codex、Cursor、Gemini CLI、Copilot 以及其余[支持的工具](supported-tools.md)。它会安装 CLI、初始化此项目并报告实际发生了什么。

下面的手动步骤是真相的来源 — 提示只是为你运行它们。如果你的助手停下来并交回一些东西，这是设计如此：在需要特权时它会询问，并且从不编辑你的 shell 启动文件。用[包管理器](#包管理器)和[故障排除](troubleshooting.md)自己完成这些部分。

```text
在此项目中安装 OpenSpec 并为我设置。按顺序遵循以下步骤，
并在步骤告诉你停止的地方停止。

1. 运行时。运行 `node --version`。OpenSpec 需要 Node.js 20.19.0 或更高版本。如果
   Node 缺失或版本较旧，说明情况并停止 — 不要安装 Node、切换
   版本或重新配置我的版本管理器。

2. 安装。使用 PATH 上已有的任何包管理器，优先使用 npm：
     npm install -g @fission-ai/openspec@latest
     pnpm add -g @fission-ai/openspec@latest
     bun add -g @fission-ai/openspec@latest
     yarn global add @fission-ai/openspec@latest   （仅限 Yarn 1.x）
   不要根据此项目的 lockfile 选择 — 全局安装与
   此仓库自己的依赖项如何安装无关。如果这四个
   都不可用，停止并告诉我 — 不要即兴安装。（如果我在 Nix 上，
   指向 OpenSpec 安装文档的 Nix 部分。）
   在运行之前显示确切的命令并让我确认；这会安装
   项目外部的软件，我可能希望不同的包管理器来
   管理它。
   如果安装需要 sudo 或管理员权限、因权限错误失败、
   或报告其全局 bin 目录缺失或未配置，请再次询问我。永远不要编辑我的 shell 启动文件（.bashrc、.zshrc、.profile、
   fish、PowerShell 配置文件），也永远不要运行为我编辑它们的设置命令 — 显示更改并让我自己进行。

3. PATH。运行 `openspec --version`。如果命令找不到，可能只是
   缺少这个 shell：告诉我包管理器安装在哪里以及如何
   将该目录添加到 PATH（针对我的 shell 和操作系统），然后停止直到我
   确认。如果它打印的版本比安装刚刚
   报告的旧，PATH 上较早的副本正在覆盖它 — 告诉我两个版本
   而不是继续。如果我使用版本管理器，请说明而不是
   绕过它编辑 PATH：使用 nvm 或 fnm 时，CLI 绑定到安装时
   活动的 Node 版本，而使用 asdf 或 volta 时，可能需要重新生成 shim。

4. 初始化。问我使用哪个 AI 编程工具，并将每个工具映射到来自
   `openspec init --help` 的 id（Copilot 是 `github-copilot`，Zoo Code 是
   `roocode`）。`--tools` 接受逗号分隔的列表，所以列出所有工具。
   `openspec init --tools <ids>` 会自动删除旧版 OpenSpec 的
   残留文件，无需询问 — 包括主目录中的 `opsx-*.md` 提示文件（Codex 将它们保存在 ~/.codex/prompts 中）。在运行之前，查找这些内容：`.../commands/openspec/` 文件夹、文件如 CLAUDE.md 或 AGENTS.md 中的 OpenSpec 标记块，以及主目录中的 `opsx-*.md` 提示。列出你发现的任何内容并等待我的许可；如果没有发现，说明情况并继续
   无需询问。现有的 `openspec/` 文件夹不是问题 — init 会刷新它并保留我的规格说明和变更。
   也确认我在正确的文件夹中：init 会在任何地方创建 `openspec/`，包括 monorepo 包内部。
   然后运行：openspec init --tools <ids>

5. 报告。不要假设应该存在什么 — 告诉我 init 实际打印了什么：
   创建了多少技能和/或命令以及它们在哪里、配置文件行、
   任何"需要设置"的说明，以及需要重启或重新加载的内容。某些工具仅支持技能，正确创建零个命令文件，因此缺少命令本身不是失败。如果 init 说没有生成任何内容，传达它建议的修复而不是重试。最后告诉我如何在我的工具中调用 OpenSpec，并从 init 创建的文件中获取确切的拼写而不是其摘要行：每个工具的标点符号不同（/opsx:propose 在某些工具中，/opsx-propose 在其他工具中，Amazon Q 中为 @opsx-propose），获得技能而非命令的工具通过技能名称调用（/openspec-propose、Codex 中的 $openspec-propose、Kimi Code 中的 /skill:openspec-propose）。
```

提示中没有特定于供应商的内容：它是普通指令加上此页面记录的相同命令。它在 macOS、Linux 和 Windows 上工作，当步骤需要你的许可时，它会故意停止而不是即兴发挥。你的助手需要能够运行 shell 命令 — 少数 IDE 集成不能。

## 包管理器

### npm

```bash
npm install -g @fission-ai/openspec@latest
```

### pnpm

```bash
pnpm add -g @fission-ai/openspec@latest
```

### yarn

```bash
yarn global add @fission-ai/openspec@latest
```

Yarn 2 及更高版本（Berry）删除了 `global` 命令。在这些版本上，使用 npm、pnpm 或 bun 安装 OpenSpec — 全局 CLI 不需要与你的项目的包管理器共享。

### deno

Deno 有时在解析 @latest 标签时会出现问题，但我们可以先指定版本安装。
如果发生这种情况，你可以尝试将 @latest 标签替换为版本，如 `@^1.3.1`

```bash
deno install --global \
  --allow-read --allow-write --allow-env --allow-sys=cpus,homedir --allow-net=edge.openspec.dev \
  npm:@fission-ai/openspec@latest
# 或
deno install --global \
  --allow-read --allow-write --allow-env --allow-sys=cpus,homedir --allow-net=edge.openspec.dev \
  npm:@fission-ai/openspec@^1.3.1
```

注意：如果你的子命令启动外部工具，如配置编辑、反馈或工作区打开，你可能需要范围化的 --allow-run=<program>。

### bun

Bun 可以全局安装 OpenSpec，但 OpenSpec 目前在 Node.js 上运行。
你仍然需要在 `PATH` 上可用 Node.js 20.19.0 或更高版本。

```bash
bun add -g @fission-ai/openspec@latest
```

## Nix

无需安装即可直接运行 OpenSpec：

```bash
nix run github:Fission-AI/OpenSpec -- init
```

或安装到你的配置文件：

```bash
nix profile install github:Fission-AI/OpenSpec
```

或在 `flake.nix` 中添加到你的开发环境：

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    openspec.url = "github:Fission-AI/OpenSpec";
  };

  outputs = { nixpkgs, openspec, ... }: {
    devShells.x86_64-linux.default = nixpkgs.legacyPackages.x86_64-linux.mkShell {
      buildInputs = [ openspec.packages.x86_64-linux.default ];
    };
  };
}
```

## 验证安装

```bash
openspec --version
```

## 更新

升级包，然后刷新每个项目的生成文件：

```bash
npm install -g @fission-ai/openspec@latest   # 或 pnpm/yarn/bun 等效命令
openspec update                              # 在每个项目中运行
```

`openspec update` 重新生成你已配置工具的技能和命令文件，因此你的斜杠命令与安装的版本保持同步。它还会检查是否已发布更新的 CLI 并提供升级，因为升级是使新工作流可用的首要条件 — 请参阅[CLI 参考](cli.md#openspec-update)。

## 卸载

没有 `openspec uninstall` 命令，因为 OpenSpec 只是一个全局包加上你项目中的一些文件。删除它只是几个手动步骤，而且这里没有任何内容接触你的源代码。

**1. 删除全局包：**

```bash
npm uninstall -g @fission-ai/openspec   # 或：pnpm rm -g / yarn global remove / bun rm -g
```

**2. 从项目中移除 OpenSpec（可选）。**如果你不再需要其规格说明和变更，请删除 `openspec/` 目录：

```bash
rm -rf openspec/
```

在这样做之前请三思：`openspec/specs/` 和 `openspec/changes/archive/` 是你的系统如何行为以及为什么更改的记录。如果你可能想要这段历史，即使在卸载后也要保留该文件夹（或将其保留在 git 中）。

**3. 删除生成的 AI 工具文件（可选）。**OpenSpec 将技能和命令文件写入每个工具的目录，如 `.claude/skills/`、`.cursor/commands/` 等。删除你配置的工具的 `openspec-*` 技能和 `opsx-*` 命令。每个工具的确切路径列在[支持的工具](supported-tools.md)中。

如果你还有 `CLAUDE.md` 或 `AGENTS.md` 等文件中的 OpenSpec 标记块，请手动删除它们；这些文件中你自己的内容由你自己保留。

## 下一步

安装后，在你的项目中初始化 OpenSpec：

```bash
cd your-project
openspec init
```

请参阅[开始使用](getting-started.md)了解完整的演练。

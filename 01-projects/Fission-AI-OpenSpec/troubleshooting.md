# 故障排除

具体问题的具体修复。每个条目命名症状，用一句话解释可能的原因，然后给你修复方法。如果你的问题不在此处，[FAQ](faq.md) 可能会有所帮助，[Discord](https://discord.gg/YctCnvvshC) 肯定会有。

## 安装和设置

### `openspec: command not found`

CLI 没有安装，或者你的 shell 找不到它。全局安装并检查：

```bash
npm install -g @fission-ai/openspec@latest
openspec --version
```

如果已安装但仍然找不到，你的全局 npm bin 目录可能不在你的 `PATH` 中。运行 `npm prefix -g` 查看全局包的位置：在 macOS 和 Linux 上，二进制文件在该目录的 `bin/` 中，在 Windows 上它们直接位于其中。确保该路径在你的 `PATH` 中。（`npm bin -g` 已在 npm 9 中移除。）

如果你使用了 [AI 辅助安装](installation.md#install-with-your-ai-assistant)，这是预期的交接点：该提示告诉你的助手向你展示 `PATH` 更改，而不是自己编辑你的 shell 启动文件。

### "Requires Node.js 20.19.0 or higher"

OpenSpec 在 Node 20.19.0+ 上运行。检查你的版本并在需要时升级：

```bash
node --version
```

如果你使用 bun 安装 OpenSpec，请注意 OpenSpec 仍然 *运行在* Node 上，所以无论安装方式如何，你的 `PATH` 上都需要 Node 20.19.0+。参见 [安装](installation.md)。

### `openspec init` 没有配置我的 AI 工具

Init 询问要设置哪些工具。如果你跳过了某个工具或想添加另一个，只需重新运行它，或使用非交互式形式：

```bash
openspec init --tools claude,cursor
```

完整的工具 ID 列表在 [支持的工具](supported-tools.md) 中。使用 `--tools all` 设置所有内容，`--tools none` 跳过工具设置。

## 命令不显示

如果 `/opsx:propose`（或你工具的等效命令）没有出现或什么都不做，按此列表排查。它们按最快检查的顺序排列。

1. **你可能在错误的地方。** 斜杠命令放在你的 AI 助手的聊天中，不是你的终端。如果你在 shell 中输入了 `/opsx:propose`，那就是问题所在。参见 [命令如何工作](how-commands-work.md)。

2. **重新生成文件。** 从你的项目根目录：

   ```bash
   openspec update
   ```

   这会重写你已配置工具的每个技能和命令文件。

   指令文件来自 *已安装* 的 CLI，因此过时的 CLI 会报告一切最新，而从未写入更新的工作流。`openspec update` 现在会检查并提示升级 — 如果看到提示就接受。

3. **重启你的助手。** 大多数工具在启动时扫描技能和命令。一个新的窗口通常就能解决问题。

4. **确认文件存在。** 对于 Claude Code，检查 `.claude/skills/` 是否包含 `openspec-*` 文件夹。其他工具使用自己的目录，全部列在 [支持的工具](supported-tools.md) 中。

5. **确认你在此项目上初始化过。** 技能是按项目写入的。如果你克隆了仓库或切换了文件夹，在那里运行 `openspec init`（或 `openspec update`）。

6. **确认你的工具支持命令文件。** Codex、CodeArts、ForgeCode、Hermes、Kimi Code、Mistral Vibe、Zed Agent 和共享的 `.agents` 目标不会生成 `opsx-*` 命令文件；它们使用基于技能的调用，因此 `/opsx` 永远不会为它们自动完成。在 Codex 中输入 `$openspec-propose`，在 Kimi Code 中输入 `/skill:openspec-propose`，在其余工具中输入 `/openspec-propose`。共享的 `.agents` 目标是厂商中立的，因此 `/openspec-propose` 是常见形式而不是保证 — 如果你的助手不响应它，请检查它自己的文档了解如何调用技能。Amazon Q 确实会生成命令文件，但将它们加载到提示库中而不是斜杠菜单中 — 在那里输入 `@opsx-propose`，而不是 `/opsx`。每个工具的形式都列在 [如何调用](supported-tools.md#how-to-invoke) 中。

## 处理变更

### "Change not found"

命令无法判断你指的是哪个变更。显式命名它，或检查存在什么：

```bash
openspec list                    # 查看活跃变更
/opsx:apply add-dark-mode        # 在聊天中命名变更
```

还要确认你在正确的项目目录中。

### "No artifacts ready"

每个产物要么已经创建，要么正在等待依赖关系。查看什么被阻塞了：

```bash
openspec status --change <name>
```

然后先创建缺失的依赖关系。记住顺序：proposal 启用 specs 和 design；specs 和 design 一起启用 tasks。

### `openspec validate` 报告警告或错误

验证检查你的 specs 和变更的结构问题。阅读消息：它会命名文件和问题。

```bash
openspec validate <name>           # 验证一个项目
openspec validate --all            # 验证所有内容
openspec validate --all --strict   # 更严格的检查，适合 CI
openspec validate --archived       # 如果归档的变更有未勾选的任务则失败
```

常见原因是缺少必需的部分（例如没有场景的 spec）或格式错误的 delta 标题。修复文件并重新运行。[CLI 参考](cli.md#openspec-validate) 记录了输出格式。

有一条消息值得单独说明：

```text
MODIFIED "<requirement>" omits scenario(s) the current spec still has: "<scenario>"
```

`MODIFIED` 需求替换整个需求块，所以它必须携带变更中所有幸存的场景，不仅仅是编辑过的场景。将命名场景从 `openspec/specs/<capability-path>/spec.md` 复制回 delta 中，保留路径中的任何域目录。这通常出现在旧变更上，在别人的变更向同一需求添加了场景之后 — 归档拒绝该变更，验证现在会提前告诉你。归档拒绝该变更，无论哪种方式。

### AI 创建了不完整或错误的产物

AI 没有足够的上下文。几个杠杆可以帮助：

- 在 `openspec/config.yaml` 中添加项目上下文，以便你的栈和约定被注入到每个请求中。参见 [自定义配置](customization.md#project-configuration)。
- 为特定产物添加 `rules:` 指导，例如 specs。
- 提出时给出更详细的描述。
- 使用扩展的 `/opsx:continue` 一次创建一个产物并审查每个产物，而不是让 `/opsx:ff` 一次性全部创建。

### 归档无法完成，或警告任务未完成

归档不会 *阻塞* 未完成的任务，但它会警告你，因为归档通常意味着工作已完成。如果任务是有意保留的（你归档了一个部分变更），请继续。否则先完成任务。归档还会提示同步你的 delta specs 到主 specs，如果你还没有同步的话；除非你有理由不这么做，否则同意。

### "User force closed the prompt with 0 null"

某个东西运行了 `openspec archive`，但没有任何东西可以回答问题 — AI 代理从工具调用它，CI 作业，或任何 stdin 已关闭的 shell。归档会问最多三个确认，无法回答的一个会失败并显示原始消息。

传递 `--yes` 以提前回答它们：

```bash
openspec archive <change-name> --yes
```

保留你已经在传递的任何标志 — `--skip-specs` 和 `--no-validate` 会改变归档的行为，所以裸 `--yes` 重新运行是不一样的命令。如果你打算从列表中选择，显式传递变更名称：选择器也需要回答。当前版本会为你命名该标志并打印一个你可以粘贴的 `Fix:` 行。如果你将 archive 的输出重定向到文件或被工具捕获 *并* 确实传递了答案（`printf 'y\n' | openspec archive …`），旧版本会在绘制提示时向捕获中写入终端转义码 — 在某些环境中足以严重膨胀文件。当前版本在 stdout 不是终端时将确认提示读取为纯文本，而无参数 `openspec archive`（否则将绘制交互式变更选择器）要求在 stdout 不是终端时提前传递变更名称，而不是将菜单渲染到捕获中。无论哪种方式，重定向和代理运行都保持干净；传递 `--yes`（带变更名称）完全跳过提示。

## 配置

### 我的 `config.yaml` 没有被应用

三个常见原因：

1. **文件名错误。** 必须是 `openspec/config.yaml`，不能是 `.yml`。
2. **无效的 YAML。** 通过任何 YAML 验证器运行；CLI 也会报告带有行号的语法错误。
3. **你预期需要重启。** 不需要。配置更改立即生效。

### "Unknown artifact ID in rules: X"

`rules:` 下的键与你的模式的任何产物都不匹配。对于默认的 `spec-driven` 模式，有效的 ID 是 `proposal`、`specs`、`design`、`tasks`。查看任何模式的 ID：

```bash
openspec schemas --json
```

### "Context too large"

`context:` 字段限制在 50KB，这是故意的，因为它被注入到每个请求中。总结它，或链接到更长的文档。精简的上下文也会产生更好、更快的结果。

### "Schema not found"

你引用的模式名称不存在。列出可用的并检查拼写：

```bash
openspec schemas                    # 列出可用模式
openspec schema which <name>        # 查看模式从哪解析
openspec schema init <name>         # 创建自定义模式
```

参见 [自定义配置](customization.md#custom-schemas)。

## 从旧工作流迁移

### "Legacy files detected in non-interactive mode"

你在 CI 或非交互式 shell 中，OpenSpec 发现了需要清理的旧文件但无法提示你。自动批准：

```bash
openspec init --force
```

对于 Codex，OpenSpec 可能会检测到全局 Codex 提示目录中的旧托管提示文件。该清理仅限于 OpenSpec 允许列表中的旧版 Codex 提示文件名，并且只有在替换 `.agents/skills/openspec-*` 技能存在后才会移除非交互式 `openspec init`。非交互式 `openspec update` 除非传递 `--force`，否则不会清理旧版残留。

### 迁移后命令没有出现

重启你的 IDE。技能在启动时检测。如果仍然没有出现，运行 `openspec update` 并检查 [支持的工具](supported-tools.md) 中的文件位置。

### 我的旧 `project.md` 没有被迁移

这是故意的。OpenSpec 永远不会自动删除 `project.md`，因为它可能包含你写的上下文。将有用部分移到 `config.yaml` 的 `context:` 部分，然后自己删除它。[迁移指南](migration-guide.md#migrating-projectmd-to-configyaml) 引导你完成此操作，包括一个你可以交给 AI 来执行提炼的提示。

## 仍然卡住？

- **Discord：** [discord.gg/YctCnvvshC](https://discord.gg/YctCnvvshC)
- **GitHub Issues：** [github.com/Fission-AI/OpenSpec/issues](https://github.com/Fission-AI/OpenSpec/issues)
- **从你的终端：** `openspec feedback "what went wrong"` 为你打开一个 issue。

当你报告问题时，包括你的 OpenSpec 版本（`openspec --version`）、Node 版本（`node --version`）、你的 AI 工具，以及确切的命令和输出。这会让帮助更快。

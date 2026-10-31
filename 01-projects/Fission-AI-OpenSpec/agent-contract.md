# OpenSpec Agent 契约

`openspec` CLI 的机器可读接口，已针对 `src/` 进行验证（巅峰审计，2026-06-11）。以下每个形状都是从发出代码中记录下来的。

## 1. 一般约定

- **每次调用一个 JSON 文档。** 在 `--json` 模式下，stdout 恰好携带一个 JSON 文档（2 空格缩进美化打印）。人类可读文本、进度条和 store 横幅输出到 stderr。
- **Store 横幅。** 在人类模式下，选中的 store 根会打印 `Using OpenSpec root: <id> (<path>)` 到 stderr。在 JSON 模式下从不打印。
- **键名大小写取决于表面**（见已知不一致）：store/doctor/context 负载使用 `snake_case`；工作流负载（`status`、`instructions`、`new change`、`validate`、`list`）使用 `camelCase`，除了嵌入的 `root` 对象，它始终使用 `store_id`。
- **可选键被省略，而非 null**，在大多数负载中（例如 `root.store_id`、`member.path`）。使用显式 `null` 的例外情况在每个形状中单独标注（store doctor `git.*`、失败负载）。

## 2. 诊断信封

一个信封形状被每个机器可读诊断（`StoreDiagnostic`）共享：

```json
{
  "severity": "error" | "warning" | "info",
  "code": "snake_case_string",
  "message": "human sentence",
  "target": "dotted.surface (可选)",
  "fix": "one actionable sentence/command (可选)"
}
```

诊断出现在两个位置：**状态数组**（顶层或每项的 `status: StoreDiagnostic[]`，用于健康发现）和**抛出的错误**（命令失败时转换为单元素 `status` 数组）。

## 3. 根选择和 `RootOutput`

所有根解析命令（`list`、`show`、`validate`、`status`、`instructions`、`instructions apply`、`instructions archive`、`new change`、`archive`、`doctor`、`context`、`schemas`）使用一个优先级解析一个 OpenSpec 根：

1. `--store <id>` → 注册 store 的根（`source: "store"`）。
2. 否则，最近的带有 `openspec/` 的祖先：规划形状 → `source: "nearest"`（`store:` 指针被忽略并带有 stderr 警告）；仅配置目录带有有效的 `store:` 指针 → 该 store，`source: "declared"`。
3. 无最近根 + 设置了全局 `defaultStore`（`openspec config set defaultStore <id>`）→ 该 store，`source: "global_default"`；过时的 id 失败并带有底层 store 错误和命名 `openspec config unset defaultStore` 的 `fix`。
4. 无最近根，无默认值 + 存在已注册 store → 错误 `no_root_with_registered_stores`。
5. 无根，无默认值，无 store：命令可能将 cwd 视为 `source: "implicit"`；`doctor`、`context`、`list` 和大批量 `validate` 反而失败并带有 `no_openspec_root`。`list` 为带有 `openspec/project.md` 的遗留项目保留隐式后备。

成功的 JSON 负载通常嵌入根；成功的 `schemas --json`
故意保留 §4.13 中记录兼容性裸数组：

```json
"root": { "path": "/abs/path", "source": "store" | "declared" | "global_default" | "nearest" | "implicit", "store_id": "id (仅在 store 选中时)" }
```

**根失败契约**：在 JSON 模式下，解析失败打印 `{ ...commandNullShape, "status": [diagnostic] }` 到 stdout 并以 1 退出。

## 4. 命令 JSON 形状

### 4.1 `list --json`
`{ "changes": [ { "name", "completedTasks", "totalTasks", "lastModified", "status": "no-tasks"|"complete"|"in-progress", "nested"?: ["<area>/<name>", ...] } ], "warnings"?: [ { "code", "name", "nested", "message" } ], "root": RootOutput }` — 注意每项变更的 `status` 在此是一个字符串枚举。`--specs`: `{ "specs": [ { "id", "requirementCount" } ], "root" }`。

`warnings`（空时省略）报告 `changes/` 下不是变更的目录。今天唯一的代码是 `nested_change_directory`：一个包裹变更目录的命名空间文件夹，OpenSpec 无法寻址它，因为变更始终是 `changes/` 下的直接目录。相同条目在列出的变更上携带 `nested`，其 `status` 因此没有意义。不要将此条目视为变更；报告消息并保留这些目录。

### 4.2 `show <item> --json`
变更：`{ "id", "title", "deltaCount", "deltas": [...], "root" }`。规格：`{ "id", "title", "overview", "requirementCount", "requirements": [...], "metadata": { "version", "format", "sourcePath"? }, "root" }`。一个需求，无论是在规格中还是在变更 delta 的 `requirement`/`requirements` 中，都是 `{ "name", "text", "scenarios": [ { "name", "rawText" } ] }`。需求的 `name` 是其标题去掉 `Requirement:` 和末尾的 `#` 序列，存档时 MODIFIED/REMOVED 条目精确匹配的 `name`。场景的 `name` 是其四级标题去掉 `Scenario:` 和末尾的 `#` 序列，MODIFIED 场景丢失检查比较的 `name`。

### 4.3 `validate --json`
`{ "items": [ { "id", "type": "change"|"spec", "valid", "issues": [ { "level", "path", "message", "line"?, "column"? } ], "durationMs" } ], "summary": { "totals": {items,passed,failed}, "byType": {...} }, "version": "1.0", "root" }`。任何项失败时退出 1。

### 4.4 `status --json`
`{ "changeName", "schemaName", "planningHome"?: { "kind", "root", "changesDir", "defaultSchema" }, "changeRoot", "artifactPaths": { "<id>": {outputPath, resolvedOutputPath, existingOutputPaths} }, "nextSteps": ["..."], "actionContext": { "mode": "repo-local", "sourceOfTruth": "repo", "planningArtifacts", "linkedContext", "allowedEditRoots", "requiresAffectedAreaSelection", "constraints" }, "isPlanningComplete", "isComplete", "applyRequires", "artifacts": [ {id, outputPath, status: "done"|"skipped"|"ready"|"blocked", requires, missingDeps?} ], "root" }`。对于 store 选中的根，`allowedEditRoots` 是当前路径上最近的项目是仅配置根且其 `store:` 指针命名该 store 时的 `[<declaring project>, <store>]`，否则是 `[<store>]`（包括全局 `defaultStore`），并带有约束告诉 Agent 询问要编辑哪个仓库。OpenSpec 不会将 store 的任务路由到仓库，因此声明的项目是当前项目，而非变更触及的每个仓库。`isPlanningComplete` 意味着每个非跳过规划产物存在；跳过的产物算作满足，无需创建。它不意味着实现任务已完成。`isComplete` 保留为兼容性别名，值相同。每个产物的 `requires` 是其直接依赖 id（对每个状态都出现，因此即使产物为 `done` 时，传递所需的集合也是可计算的）；`missingDeps` 仅在 `blocked` 时出现。`artifacts` 数组按依赖顺序排列，schema 的 `artifacts:` 声明顺序在同时就绪的产物之间打破平局（从不按字母顺序），因此第一个 `ready` 条目就是要写的下一个产物；`missingDeps` 使用相同顺序。`"skipped"` 标记一个产物，其 `generates` 路径在变更的 `specs/` 下，且该变更的 `.openspec.yaml` 声明了 `skip_specs: true`；它满足依赖但不能被创建。无活跃变更：`{ "changes": [], "message", "root" }`，退出 0。

`--all`（批量，与 `--change` 互斥——组合它们是错误并带有 `{ "changes": [], "root": null, "status": [d] }` 空形状）：`{ "changes": [ <每项变更的状态对象，无每项根>, ... ], "root" }`，按变更名称排序。加载失败的变更贡献 `{ "changeName", "status": [d] }` 代替；扫描继续，保留完整信封，并在文本和 JSON 模式下都以 1 退出。无效的 `--schema` 使整个调用失败并带有空形状，即使没有变更存在。

### 4.5 `instructions <artifact> --json`
`{ "changeName", "artifactId", "schemaName", "changeDir", "planningHome"?, "outputPath", "resolvedOutputPath", "existingOutputPaths", "description", "instruction"?, "context"?, "rules"?, "references"?: ReferenceIndexEntry[], "skipped"?, "warning"?, "template", "dependencies": [{id,done,path,description,skipped?}], "unlocks", "root" }`。`unlocks` 列出此产物使其就绪的产物，按 schema 的声明顺序（`status` 推荐它们的相同顺序）。`"skipped": true`（带有 `"warning"`）在变更声明 `skip_specs: true` 且此产物被跳过时出现——不要创建它的文件。带有 `skipped: true` 的依赖条目无需文件即被满足——不要尝试读取其路径。

`ReferenceIndexEntry`：`{ "store_id", "root"?, "specs"?: [{id,summary}], "fetch"?, "status": [] }` — 已解析条目携带 root/specs/fetch；未解析条目携带 store_id + warning 状态。索引上限为 50KB（`reference_index_truncated`）。

### 4.6 `instructions apply --json`
`{ "changeName", "changeDir", "schemaName", "contextFiles": { "<artifactId>": ["/abs", ...] }, "progress": {total,complete,remaining}, "tasks": [{id,description,done}], "state": "blocked"|"all_done"|"ready", "missingArtifacts"?, "missingPrerequisites"?, "warnings"?, "instruction", "references"?, "context"?, "operationGuidance"?, "root" }`。`missingArtifacts` 是 apply 阻塞的内容（schema 的 `apply.requires`）；`missingPrerequisites` 是在 apply 可以运行之前仍需构建的一切，按构建顺序——那些 requires 的传递闭包，因此它可能是更长的列表。`warnings` 列出变更本身的非阻塞问题——今天，一个准备好实现但无 delta 规格且无 `skip_specs: true` 的变更，`openspec validate` 会拒绝的状态。两个可选根字段（`context`、`operationGuidance`）在每次调用时从选中的根读取。`context` 是一个必需的提示级输入，其相关项目事实、约定和约束必须被应用；`operationGuidance` 是建议性输入，其条目仅在适用且与内置工作流兼容时才被遵循。两者都与状态、任务、进度、上下文文件和内置指令分开。

### 4.7 `instructions archive --json`
`{ "changeName", "context"?, "operationGuidance"?, "root" }`。要求在已解析的仓库/store 根中有一个有效的 `--change`，并使用与 apply 相同的 required-context/advisory-guidance 语义。这是一个只读的运行时输入表面：它不返回静态归档工作流、检查或合并 delta 规格、写入主规格，或移动变更。

### 4.8 `new change <name> --json`
成功：`{ "change": { "id", "path", "metadataPath", "schema" }, "root" }`。失败：`{ "change": null, "status": [d] }`，退出 1。

### 4.9 `archive <name> --json`
成功：`{ "archive": { "change", "archivedAs": "YYYY-MM-DD-name", "path", "specsUpdated", "totals"?, "warnings"? }, "root" }`。失败：`{ "archive": null, "root"?, "status": [d] }`，退出 1。`specsUpdated` 仅在至少一个规格文件被写入或停用时为真（一个能力，其最后一个需求被变更移除的，其规格会被删除，这需要变更的 `.openspec.yaml` 中有 `retire_capabilities: true`；每次停用都在 `warnings` 中命名，并仅在规格存在于调用者的检出中时提供可粘贴的 Git 恢复命令）；已同步的变更以全零总计归档，跳过项列在 `warnings` 中。JSON 模式严格非交互式：每个提示点变成 `archive_*` 代码。

- **`archive: null`**：命令失败。这不保证文件未更改。
- **`archive_retirement_cleanup_failed`**：变更已归档，但停用备份验证或清理失败。列出的备份路径可能已更改或消失。消息也可能报告失败的后备复制清理留下的暂存源。清理前检查当前归档和所有报告的恢复路径。保留任何需要的内容。重试归档不会清理这些路径。
- **`archive_error`**：后备诊断无法识别文件是否已更改。重试前检查变更、归档和受影响的规格。

### 4.10 `doctor --json`
`{ "root": { "path", "source", "store_id"?, "healthy", "status": [] }, "store": { "id", "metadata": {present,valid,remote?}, "origin_url"?, "drift"?: {ahead,behind}, "status": [] } | null, "references": [...], "status": [] }`。`drift`（仅对带有上游追踪引用的 git-backed store 检出存在）是 ahead/behind 计数，针对最后获取的上游，而非实时远程。任何严重程度的健康发现退出 0。失败负载：`{ "root": null, "store": null, "references": [], "status": [d] }`，退出 1。

### 4.11 `context --json`
`{ "root": { "path", "source", "store_id"?, "role": "openspec_root" }, "members": [ { "role": "referenced_store", "id", "path"?, "remote"?, "fetch"?, "status": [] } ], "status": [] }`。AVAILABLE = path 存在 AND status 为空。`--code-workspace <path>` 写入 `{folders:[{name,path}]}`（仅可用引用 store，`ref:` 前缀）；在 JSON 模式下，写入在打印前运行，因此 stdout 恰好持有一个文档，即使在写入失败时。失败：`{ "root": null, "members": [], "status": [d] }`，退出 1。

### 4.12 `store ... --json`
setup/register：`{ "store": {id, root, metadata_path?}, "registry": {path, registered, already_registered}, "git": {is_repository, initialized, committed}, "created_files": [], "status": [] }`。unregister/remove：`{ "store", "registry": {path, removed}, "files": {deleted, deleted_path, left_on_disk}, "status": [] }`。list：`{ "stores": [{id, root}], "status": [] }`。doctor：`{ "stores": [ { id, root, metadata_path?, openspec_root: {...healthy, status}, metadata: {present, valid, id?, remote}, git: {is_repository, has_commits, has_uncommitted_changes, has_remote, origin_url}, status } ], "status": [] }`（`null` = 未知/未探测）。健康发现退出 0；失败退出 1 并带有匹配空形状。提示取消退出 130。

### 4.13 `schemas --json` / `templates --json`
`schemas`：成功保留裸数组 `[ {name, description, artifacts, source} ]`；它解析规范根选择优先级并接受 `--store <id>`。根选择失败：`{ "schemas": [], "root": null, "status": [d] }`，退出 1。`templates`：键控对象 `{ "<artifactId>": {path, source} }`，仍基于 cwd，无根/status 键。

## 5. 退出码契约

| 情况 | 退出码 | Stdout |
|---|---|---|
| 成功，包括健康发现 (doctor/context/store doctor) | 0 | 负载 |
| `--json` 模式下的命令失败 | 1 | 一个带有 `status: [d]` 和命令空形状的 JSON 文档 |
| `validate` 有失败项 | 1 | 完整报告 |
| 提示取消 (store 组，人类模式) | 130 | 仅 stderr |

## 6. 诊断代码目录

### 解析
`no_openspec_root`, `no_root_with_registered_stores`, `no_registered_stores`, `unknown_store`, `store_identity_mismatch`, `unhealthy_store_root`, `store_path_not_supported`, `invalid_store_pointer`, `initiative_option_removed`, `areas_option_removed`；透传：`invalid_store_id`, `invalid_store_registry`, `invalid_store_metadata`。

### OpenSpec 根健康 (错误，无修复)
`openspec_store_root_missing`, `openspec_store_root_not_directory`, `openspec_root_missing`, `openspec_root_not_directory`, `openspec_config_missing`, `openspec_config_not_file`, `openspec_specs_not_directory`, `openspec_changes_not_directory`, `openspec_archive_not_directory`。在 stores 测试版期间，`openspec/specs/`、`openspec/changes/` 和 `openspec/changes/archive/` 在健康根中可能不存在；它们仅当存在但不是目录时才是健康错误。

### Store 注册表/身份/状态
`invalid_store_id`, `invalid_store_registry`, `invalid_store_metadata`, `store_registry_busy`, `store_not_found`, `no_store_registry`, `store_registry_changed`, `store_metadata_missing`, `store_metadata_id_mismatch`, `store_metadata_invalid`, `store_id_conflict`, `store_path_conflict`, `store_already_registered` (info)。

### Store 设置/注册/移除
`store_setup_id_required`, `store_setup_path_required`, `store_setup_path_not_directory`, `store_setup_inside_git_repo`, `store_setup_non_empty_directory`, `store_setup_cancelled`, `store_path_required`, `store_path_missing`, `store_path_not_directory`, `store_root_pointer_declared`, `store_register_root_unhealthy`, `store_register_identity_confirmation_required`, `store_register_cancelled`, `store_remote_empty`, `store_remote_requires_hand_edit`, `store_remove_confirmation_required`, `store_remove_cancelled`, `store_remove_path_not_directory`, `store_remove_metadata_missing`, `store_remove_contains_registered_store`, `store_root_missing` (remove 中的警告，doctor 中的错误), `store_root_not_directory`。

### Store git
`store_git_init_failed`, `store_git_identity_missing`, `store_git_commit_failed`, `store_git_no_commits` (warning), `store_clone_fragile_directories` (warning), `store_remote_divergence` (info, doctor), `store_checkout_drift` (info, doctor)。

### 引用 (warning)
`reference_invalid_id`, `reference_registry_unreadable`, `reference_unresolved`, `reference_root_unhealthy`, `reference_index_truncated`。

### 关系 (warning; doctor; context 只保留注册表的)
`relationship_registry_unreadable`, `root_pointer_ignored`, `root_pointer_invalid`, `pointer_declarations_inert`。

### 归档 (JSON 模式)
`archive_change_name_required`, `archive_change_not_found`, `archive_change_symlink`, `archive_validation_failed`, `archive_confirmation_required`, `archive_tasks_incomplete`, `archive_spec_update_failed`, `archive_spec_validation_failed`, `archive_target_exists`, `archive_retirement_cleanup_failed`, `archive_error`。

### 上下文写入
`context_file_exists`, `context_output_dir_missing`。

### 后备
`doctor_failed`, `context_failed`, `store_error`, `change_error`, `archive_error`。

## 已知不一致

由巅峰审计记录；已发布键重命名是推迟到本次发布之后的产品决策：

1. ~~在 `--json` 模式下，几个失败路径只打印 stderr 而没有 JSON 文档。~~ 在巅峰 gauntlet 回合中修复：`show`/`validate` 未知和模糊项发出 `{status:[{code: unknown_item | ambiguous_item, ...}]}`；`status`/`instructions`/`list`/`show`/`validate` 中的抛出错误通过 JSON 感知失败辅助器路由（命令的空形状 + `status`）；`store <unknown subcommand> --json` 发出 `{status:[{code: unknown_store_subcommand}]}`；`list` 在解析失败时携带其 `{changes|specs: [], root: null}` 空形状。
2. `store_root_missing` 以两种严重程度发出（remove 中的警告，store doctor 中的错误）——上下文相关，如上所述。
3. snake_case（store 系列）vs camelCase（工作流系列）键大小写；`root.store_id` 在所有地方都是 snake_case。
4. src 中存在四个并行信封类型声明；归档诊断从不携带 `target`。
5. `list --json` 将 `status` 键作为每项变更的字符串枚举复用。
6. 只有 `validate` 输出携带 `version` 字段。
7. `templates` 忽略根选择（基于 cwd，无 `--store`）。
8. 已弃用的名词形式（`change`/`spec` 子命令）发出无 `root`/`status` 的无信封负载。

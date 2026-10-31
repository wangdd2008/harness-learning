# 多语言指南

配置 OpenSpec 以生成英语以外的语言产物。

## 快速设置

对于新项目，在初始化期间设置语言：

```bash
openspec init --language "Portuguese (pt-BR)"
```

这会将语言指令写入 `openspec/config.yaml`。如果项目已经有配置，直接编辑其 `context` 字段以保留现有项目指导。

你也可以手动配置相同的行为：

将语言指令添加到你的 `openspec/config.yaml`：

```yaml
schema: spec-driven

context: |
  Language: Portuguese (pt-BR)
  All artifacts must be written in Brazilian Portuguese.
  Keep OpenSpec structural headings and SHALL/MUST keywords in English.

  # 你的其他项目上下文在下面...
  Tech stack: TypeScript, React, Node.js
```

就是这样。所有生成的产物现在都会是葡萄牙语。

OpenSpec 的文档结构和规范性 `SHALL`/`MUST` 关键字保持英文，因为验证依赖它们。周围的需求和场景文本可以使用你选择的语言。

## 语言示例

### 葡萄牙语（巴西）

```yaml
context: |
  Language: Portuguese (pt-BR)
  All artifacts must be written in Brazilian Portuguese.
```

### 西班牙语

```yaml
context: |
  Idioma: Español
  Todos los artefactos deben escribirse en español.
```

### 中文（简体）

```yaml
context: |
  语言：中文（简体）
  所有产出物必须用简体中文撰写。
```

### 日语

```yaml
context: |
  言語：日本語
  すべての成果物は日本語で作成してください。
```

### 法语

```yaml
context: |
  Langue : Français
  Tous les artefacts doivent être rédigés en français.
```

### 德语

```yaml
context: |
  Sprache: Deutsch
  Alle Artefakte müssen auf Deutsch verfasst werden.
```

## 技巧

### 处理技术术语

决定如何处理技术术语：

```yaml
context: |
  Language: Japanese
  Write in Japanese, but:
  - Keep technical terms like "API", "REST", "GraphQL" in English
  - Code examples and file paths remain in English
```

### 与其他上下文结合

语言设置与你的其他项目上下文一起工作：

```yaml
schema: spec-driven

context: |
  Language: Portuguese (pt-BR)
  All artifacts must be written in Brazilian Portuguese.

  Tech stack: TypeScript, React 18, Node.js 20
  Database: PostgreSQL with Prisma ORM
```

## 验证

要验证你的语言配置是否在工作：

```bash
# 检查指令 - 应该显示你的语言上下文
openspec instructions proposal --change my-change

# 输出会包含你的语言上下文
```

## 相关文档

- [自定义配置指南](./customization.md) - 项目配置选项
- [工作流指南](./workflows.md) - 完整工作流文档

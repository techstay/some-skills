# Skill 编写指南

基于 Anthropic 官方 skill 示例（algorithmic-art、docx）总结的编写经验。

---

## 核心原则

1. **只写 AI 不知道的领域知识** — 不写废话，不写通用能力
2. **实用导向** — 每一行都要对"AI 执行任务"有实际帮助
3. **渐进披露** — SKILL.md 放核心规则和导航，详细参考放 references

---

## 文件结构

```
skill-name/
├── SKILL.md
└── references/
    ├── high-freq-1.md
    ├── high-freq-2.md
    ├── mid-freq.md
    └── low-freq.md
```

**关键**：references 可按**使用频率**或**功能模块**拆分。按频率拆分是推荐做法（常用内容单独成小文件，低频内容合并），但按功能模块拆分也是可接受的，选择最适合该技能的方式即可。

---

## SKILL.md 的结构模板

```markdown
---
name: skill-name
description: "一段话描述技能用途和触发条件。这个字段决定了 skill 何时被加载。"
license: MIT
---

# 技能名称

一句话说明这个技能做什么。

## 快速参考

| 你要做什么 | 该怎么做                           |
| ---------- | ---------------------------------- |
| 场景 A     | 加载 `references/xxx.md`，执行步骤 |
| 场景 B     | 加载 `references/yyy.md`，执行步骤 |

---

## 关键工作流规则

### ⚠️ 最容易出错的地方（用 CRITICAL/⚠️ 标记）

列出最关键的 1-2 个规则，用 ❌/✅ 对比格式展示。

**避免：**

- ❌ 常见错误 A
- ❌ 常见错误 B

**遵循：**

- ✅ 正确做法 A
- ✅ 正确做法 B

---

## Reference 文件 — 按需加载

只加载当前任务所需的文件。**不要一次全部加载。**

| 文件 | 内容 | 加载时机 |
| ---- | ---- | -------- |

---

## 常见错误

| ❌ 错误写法 | ✅ 正确写法 | 原因 |
| ----------- | ----------- | ---- |
```

---

## Frontmatter 编写要点

`name` 和 `description` 是 frontmatter 中最重要的两个字段。Claude **仅凭 description** 决定是否加载技能——如果 description 写得不好，再好的指令也不会被触发。

### name

- 用小写字母和连字符（如 `obsidian-kanban`）
- 限制：**≤ 64 字符**

### description

description 需要具体、"pushy"（主动），让 Claude 明确知道"这是技能的活，不是我自己能搞定的"。

**好的 description 包含以下要素：**

1. **做什么** — 一句话概括核心功能
2. **什么时候触发** — 列出具体场景和用户会说的关键词
3. **输入类型** — 如 "当用户上传 CSV/Excel 时"、"当用户提到看板/卡片/列时"
4. **静默匹配** — 考虑用户没有明确提到技能名称的情况

**示例对比：**

```yaml
# ❌ 太模糊 — Claude 不知道何时触发
name: kanban-helper
description: 帮助管理看板

# ✅ 具体明确 — 列出触发条件、关键词、输入类型
name: obsidian-kanban
description: >
  在 Obsidian 中创建和管理基于 Markdown 的可视化看板。
  当用户需要在 Obsidian 中创建看板、添加/编辑卡片和列、
  设置日期标签、归档卡片、配置看板选项、或结合 Tasks 插件
  管理任务时使用此技能。
```

**限制：** description ≤ 1024 字符。优先写入直接影响触发的信息。

---

## 编写风格

### 用强调标记突出关键信息

- `⚠️` + 加粗标题 — 最容易出错的规则
- `CRITICAL`、`IMPORTANT` — 关键步骤的提醒
- ❌ / ✅ — 正反对比，比纯文字描述更直观
- **加粗** — 行内关键词

### 先规则后示例

每条规则先说"做什么"，再说"怎么做"。示例放在规则之后，不是替代规则。

### 用表格代替列表

快速参考、常见错误、reference 索引等内容，用表格比用 bullet 列表更紧凑、更易扫读。

### 避免冗余

- 同一个知识点只在一处讲清楚
- 如果"快速参考"已经覆盖了某块内容，正文不需要再重复展开
- "常见错误"表和"关键规则"不要重复同一条

---

## 反面模式（避免这些）

| 反面模式                   | 问题         | 正确做法                        |
| -------------------------- | ------------ | ------------------------------- |
| 触发场景和快速参考内容重叠 | 冗余         | 触发条件只写在 description 字段 |
| 关键限制和常见错误表重复   | 同一条写两遍 | 合并到一处，优先用 ❌/✅ 表格   |
| references 一次性全部加载  | 浪费 token   | 明确标注"不要一次全部加载"      |
| 纯文字描述错误             | 不够直观     | 用 ❌/✅ 对比表格展示           |

---

## 参考来源

- [Anthropic algorithmic-art skill](https://github.com/anthropics/skills/blob/main/skills/algorithmic-art/SKILL.md)
- [Anthropic docx skill](https://github.com/anthropics/skills/blob/main/skills/docx/SKILL.md)

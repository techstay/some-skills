# Tasks 核心语法参考

任务行的基本格式：

```
- [状态符号] 任务描述 [元数据...]
```

支持的列表前缀：`-`、`*`、`+`、`1.`、`2)`

## 日期 Emoji

日期格式统一为 `YYYY-MM-DD`，**不支持时间**。

| Emoji | 类型 | 含义 | 示例 |
|-------|------|------|------|
| 📅 | Due Date | 截止日期（必须完成的最后期限） | `- [ ] 提交报告 📅 2026-04-01` |
| ⏳ | Scheduled Date | 计划日期（打算什么时候做） | `- [ ] 写方案 ⏳ 2026-04-03` |
| 🛫 | Start Date | 开始日期（最早可以开始的时间） | `- [ ] 准备材料 🛫 2026-04-01` |
| ➕ | Created Date | 创建日期（设置中开启后自动添加） | `- [ ] 新任务 ➕ 2026-03-30` |
| ✅ | Done Date | 完成日期（完成任务时自动添加） | `- [x] 已完成 ✅ 2026-03-30` |
| ❌ | Cancelled Date | 取消日期（取消任务时自动添加） | `- [-] 已取消 ❌ 2026-03-30` |

**日期查询属性**：`task.due`、`task.scheduled`、`task.start`、`task.created`、`task.done`、`task.cancelled`

**万能日期过滤器 `happens`**：匹配以上所有日期类型中的任意一个。

## 优先级 Emoji

优先级从高到低：

| Emoji | 级别 | priorityNumber |
|-------|------|----------------|
| 🔺 | highest | 0 |
| ⏫ | high | 1 |
| 🔼 | medium | 2 |
| （无） | none（默认，介于 medium 和 low 之间） | 3 |
| 🔽 | low | 4 |
| ⏬ | lowest | 5 |

示例：`- [ ] 紧急修复 🔺 📅 2026-03-31`

未设置优先级的任务（none）比 low 更高，鼓励只给真正重要的任务设优先级。

## 标签

在任务行中任意位置使用 `#标签`：

```markdown
- [ ] 整理书房 📅 2026-04-05 #home #chores
```

**规则**：
- 标签和块链接**必须放在日期、优先级等元数据之后**，否则解析中断
- 可包含字母、数字、`_`、`-`、`/`
- Tasks 可以识别纯数字标签（如 `#1234`），Obsidian 原生不能
- Frontmatter 中的标签也会被读取（Tasks 7.7.0+）

## 重复任务

使用 `🔁` + 重复规则，**必须搭配至少一个日期**：

```markdown
- [ ] 倒垃圾 🔁 every Sunday 📅 2026-04-05
- [ ] 写周报 🔁 every weekday ⏳ 2026-03-31
- [ ] 月度总结 🔁 every month on the last Friday 📅 2026-04-30
```

完成后自动创建下一个实例，原任务保留完成记录。

### 重复规则语法

所有规则以 `every` 开头：

| 规则 | 含义 |
|------|------|
| `every day` | 每天 |
| `every 3 days` | 每 3 天 |
| `every weekday` | 每个工作日（周一至周五） |
| `every week` | 每周（基于日期对应的星期几） |
| `every week on Sunday` | 每周日 |
| `every 2 weeks` | 每两周 |
| `every month` | 每月（基于日期对应的天数） |
| `every month on the 1st` | 每月 1 号 |
| `every month on the last` | 每月最后一天 |
| `every month on the last Friday` | 每月最后一个周五 |
| `every quarter` | 每季度 |
| `every year` | 每年 |

### 基于完成日期的重复

添加 `when done` 后缀，使下次重复基于完成日期而非原始日期：

```markdown
- [ ] 扫地 🔁 every week when done ⏳ 2026-04-05
```

### 重复任务注意事项

- 完成后会移除 `id` 和 `dependsOn` 字段
- 不要在每日笔记（Daily Note）中创建重复任务
- 重复时可选移除计划日期（设置中配置）

## 完成时行为 (On Completion)

Tasks 7.8.0+ 支持。使用 `🏁` + 操作标识符来控制任务完成后的行为。

```markdown
- [ ] 这个任务完成后保留原样 🏁 keep
- [ ] 这个任务完成后自动删除 🏁 delete
- [ ] 每日重复 + 完成后删除已完成实例 🔁 every day when done 📅 2026-04-01 🏁 delete
```

| 操作 | 行为 |
|------|------|
| `keep` | **（默认）** 完成后保留任务，不做额外处理 |
| `delete` | 完成后自动从笔记中删除该任务行 |

**使用场景**：搭配重复任务使用 `🏁 delete` 最常见——已完成实例自动清理，只保留新生成的待办实例。

**⚠️ 警告**：不要在含嵌套子项的任务上使用 `🏁 delete`，否则子项会变成代码块破坏列表结构。

Dataview 格式语法：`[onCompletion:: delete]`

# Tasks 任务依赖参考

功能自 Tasks 6.1.0 引入。仅支持**完成到开始（Finish-to-Start）**依赖。

## 核心字段

### id（任务标识符）

唯一标识一个任务。建议在整个 vault 中保持唯一。

- 允许字符：字母（大小写）、数字、`_`、`-`
- 示例：`1234`、`task-alpha`、`do_this_first`

语法：`🆔 id值`

```markdown
- [ ] 先完成这个 🆔 task-alpha 📅 2026-04-01
- [ ] 然后做这个 ⛔ depends on task-alpha 📅 2026-04-05
```

### dependsOn（依赖关系）

指定当前任务依赖的其他任务的 id。多个依赖用逗号分隔。

语法：`⛔ depends on id1, id2`

```markdown
- [ ] 步骤一 🆔 step1 📅 2026-04-01
- [ ] 步骤二 🆔 step2 ⛔ depends on step1 📅 2026-04-03
- [ ] 步骤三 ⛔ depends on step1, step2 📅 2026-04-05
```

## 依赖概念

| 术语 | 含义 |
|------|------|
| **Blocking** | 未完成且被其他未完成任务依赖的任务（阻塞者） |
| **Blocked** | 未完成且其依赖任务中有未完成的任务（被阻塞者） |

## 依赖相关查询

| 指令 | 含义 |
|------|------|
| `has id` | 任务有 id 字段 |
| `no id` | 任务没有 id |
| `has depends on` | 任务有依赖 |
| `no depends on` | 任务没有依赖 |
| `is blocked` | 任务被阻塞（依赖中有未完成项） |
| `is not blocked` | 任务未被阻塞（可以执行） |
| `is blocking` | 任务正在阻塞其他任务 |

常用查询组合：

```tasks
# 查找当前可以做的任务
not done
is not blocked
sort by priority
```

```tasks
# 查找瓶颈任务
not done
is blocking
```

## 已知限制

- 一次性添加 ≥4 个依赖可能导致错误
- 无法从任务直接跳转到其依赖任务
- 重复任务完成后，新实例的 `id` 和 `dependsOn` 会被清除
- 紧迫性（urgency）评分不考虑依赖关系
- 需避免循环依赖（A→B→A）

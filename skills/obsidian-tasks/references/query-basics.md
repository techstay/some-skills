# Tasks 查询语法参考（基础）

在 `.md` 文件中插入 `tasks` 代码块来查询和展示任务：

````markdown
```tasks
not done
due before tomorrow
sort by due
group by filename
```
````

## 过滤器 (Filters)

### 状态过滤

| 指令 | 含义 |
|------|------|
| `not done` | 未完成任务（TODO, IN_PROGRESS, ON_HOLD） |
| `done` | 已完成任务（DONE, CANCELLED, NON_TASK） |

### 日期过滤

日期字段：`due`、`scheduled`、`start`、`created`、`done`、`cancelled`、`happens`（匹配所有日期）

比较词：`before`、`after`、`on`、`in`

| 指令 | 含义 |
|------|------|
| `due before 2026-04-01` | 截止日期在指定日期之前 |
| `due after tomorrow` | 截止日期在明天之后 |
| `due on 2026-04-01` | 截止日期为指定日期 |
| `scheduled in next week` | 计划日期在下周 |
| `happens before this month` | 任意日期在本月之前 |
| `has due date` / `no due date` | 是否有截止日期 |
| `has start date` / `no start date` | 是否有开始日期 |

**相对日期关键词**：`today`、`tomorrow`、`yesterday`、`next week`、`last week`、`this week`、`next month`、`last month`、`this month`、`next year`、`last year`、`this year`

### 优先级过滤

| 指令 | 含义 |
|------|------|
| `priority is above medium` | 优先级高于 medium（含 highest, high） |
| `priority is below high` | 优先级低于 high（含 medium, none, low, lowest） |
| `priority is highest` / `high` / `medium` / `low` / `lowest` / `none` | 精确匹配优先级 |

### 文件位置过滤

| 指令 | 含义 |
|------|------|
| `path includes "Projects"` | 文件路径包含指定文本 |
| `path does not include "Archive"` | 路径不包含 |
| `folder includes "Daily"` | 文件夹名包含 |
| `filename includes "Daily"` | 文件名包含 |
| `heading includes "Meeting"` | 任务上方的标题包含 |
| `root includes "Projects"` | 仓库根目录下的顶级文件夹名包含 |

支持变量：`{{query.file.path}}`、`{{query.file.folder}}`、`{{query.file.filename}}`

### 描述和标签过滤

| 指令 | 含义 |
|------|------|
| `description includes "紧急"` | 描述包含文本 |
| `description does not include "test"` | 描述不包含 |
| `has tags` / `no tags` | 是否有标签 |
| `tags include #work` | 包含指定标签 |
| `tags do not include #personal` | 不包含指定标签 |

### 重复任务过滤

| 指令 | 含义 |
|------|------|
| `is recurring` / `is not recurring` | 是否为重复任务 |

### 逻辑组合

```
(filter1) AND (filter2)
(filter1) OR (filter2)
NOT (filter1)
(filter1) AND NOT (filter2)
```

示例：`(due before tomorrow) AND NOT (tags include #someday)`

### 数量限制

| 指令 | 含义 |
|------|------|
| `limit 10` / `limit to 10 tasks` | 最多显示 10 个任务 |
| `limit groups to 5 tasks` | 每个分组最多 5 个任务 |
| `exclude sub-items` | 排除子任务 |

## 排序 (Sorting)

`sort by <字段> [reverse]`

| 字段 | 含义 |
|------|------|
| `status` | 按状态排序 |
| `due` | 按截止日期 |
| `scheduled` | 按计划日期 |
| `start` | 按开始日期 |
| `done` | 按完成日期 |
| `created` | 按创建日期 |
| `priority` | 按优先级（高→低） |
| `urgency` | 按紧迫度评分（综合多个因素） |
| `description` | 按描述文本（字母序） |
| `path` / `filename` / `folder` | 按文件路径 |
| `heading` | 按标题 |
| `tags` | 按标签 |
| `random` | 随机排序 |

示例：`sort by priority`、`sort by due reverse`（日期倒序，最近的在前）

## 分组 (Grouping)

`group by <字段>`

| 字段 | 含义 |
|------|------|
| `status` | 按状态分组 |
| `due` / `scheduled` / `start` / `done` | 按日期分组 |
| `priority` | 按优先级分组 |
| `path` / `filename` / `folder` | 按文件路径分组 |
| `heading` | 按标题分组 |
| `tags` | 按标签分组 |
| `backlink` | 按反向链接分组 |
| `recurrence` | 按重复规则分组 |
| `root` | 按顶级文件夹分组 |
| `happens` | 按任意日期分组 |

## 布局/显示指令

| 指令 | 含义 |
|------|------|
| `short mode` | 紧凑视图（只显示描述+截止日期+优先级） |
| `full mode` | 完整视图（所有元数据） |
| `hide due date` | 隐藏截止日期 |
| `hide scheduled date` | 隐藏计划日期 |
| `hide start date` | 隐藏开始日期 |
| `hide done date` | 隐藏完成日期 |
| `hide priority` | 隐藏优先级 |
| `hide tags` | 隐藏标签 |
| `hide edit button` | 隐藏编辑按钮 |
| `hide postpone button` | 隐藏推迟按钮 |
| `show tree` | 显示任务层级结构（缩进） |
| `show urgency` | 显示紧迫度评分 |

## 查询注释

在查询中使用 `#` 添加注释：

```tasks
# 只显示本周到期的紧急任务
not done
priority is above none
due in this week
```

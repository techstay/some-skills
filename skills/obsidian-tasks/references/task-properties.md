# Task 属性完整参考

以下属性可在 `filter by function`、`sort by function`、`group by function` 中通过 `task.` 访问。

## 状态属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `task.isDone` | `boolean` | 是否已完成 |
| `task.status.name` | `string` | 状态名称（如 'Todo'） |
| `task.status.type` | `string` | 状态类型（'TODO'/'DONE'/'IN_PROGRESS'/'ON_HOLD'/'CANCELLED'/'NON_TASK'） |
| `task.status.symbol` | `string` | 状态符号（如 ' '、'x'） |
| `task.status.nextSymbol` | `string` | 下一个状态符号 |
| `task.status.typeGroupText` | `string` | 用于分组排序的格式化文本（含 `%%序号%%`） |

## 日期属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `task.due` | `TasksDate` | 截止日期 |
| `task.scheduled` | `TasksDate` | 计划日期 |
| `task.start` | `TasksDate` | 开始日期 |
| `task.done` | `TasksDate` | 完成日期 |
| `task.created` | `TasksDate` | 创建日期 |
| `task.cancelled` | `TasksDate` | 取消日期（Tasks 5.5.0+） |
| `task.happens` | `TasksDate` | `due`、`scheduled`、`start` 中最早的一个 |

**TasksDate 对象**可用方法：

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `.moment` | `Moment` | 原始 Moment.js 对象，可调用所有 moment 方法 |
| `.formatAsDate()` | `string` | `'2026-04-01'` |
| `.formatAsDateAndTime()` | `string` | 日期+时间字符串 |
| `.format('格式')` | `string` | 自定义格式（[Moment.js 格式字符](https://momentjs.com/docs/#/displaying/format/)） |
| `.toISOString()` | `string` | ISO 格式字符串 |
| `.isValid` | `boolean` | 日期是否有效 |
| `.category.name` | `string` | 日期分类（如 'Future'、'Past'） |
| `.category.groupText` | `string` | 用于分组的分类文本 |
| `.fromNow.name` | `string` | 相对时间描述（如 'in 22 days'） |
| `.fromNow.groupText` | `string` | 用于分组的相对时间文本 |

格式化方法可接受可选的 `fallBackText` 参数：`task.due.formatAsDate("无日期")`

## 优先级属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `task.priorityNumber` | `number` | 优先级数字（0=最高, 5=最低） |
| `task.priorityName` | `string` | 优先级名称（'highest'/'high'/'medium'/'none'/'low'/'lowest'） |
| `task.priorityNameGroupText` | `string` | 用于分组的优先级文本 |

## 描述与标签

| 属性 | 类型 | 说明 |
|------|------|------|
| `task.description` | `string` | 任务描述（含标签） |
| `task.descriptionWithoutTags` | `string` | 任务描述（不含标签） |
| `task.tags` | `string[]` | 标签数组 |

## 依赖属性（Tasks 6.1.0+）

| 属性 | 类型 | 说明 |
|------|------|------|
| `task.id` | `string` | 任务 ID |
| `task.dependsOn` | `string[]` | 依赖的任务 ID 列表 |
| `task.isBlocked(query.allTasks)` | `boolean` | 是否被阻塞 |
| `task.isBlocking(query.allTasks)` | `boolean` | 是否阻塞其他任务 |

## 其他属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `task.urgency` | `number` | 紧迫度评分 |
| `task.isRecurring` | `boolean` | 是否为重复任务 |
| `task.recurrenceRule` | `string` | 重复规则字符串 |
| `task.onCompletion` | `string` | 完成时操作（'keep'/'delete'，Tasks 7.8.0+） |
| `task.originalMarkdown` | `string` | 原始 Markdown 文本 |
| `task.lineNumber` | `number` | 行号（从 0 开始） |
| `task.listMarker` | `string` | 列表标记符号（如 '-'） |
| `task.hasHeading` | `boolean` | 任务上方是否有标题 |
| `task.heading` | `string` | 任务上方的标题内容 |

## 文件属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `task.file.path` | `string` | 文件路径（含扩展名） |
| `task.file.pathWithoutExtension` | `string` | 文件路径（不含扩展名） |
| `task.file.root` | `string` | 仓库根目录下的顶级文件夹 |
| `task.file.folder` | `string` | 文件夹路径 |
| `task.file.filename` | `string` | 文件名（含扩展名） |
| `task.file.filenameWithoutExtension` | `string` | 文件名（不含扩展名） |
| `task.outlinks` | `Link[]` | 任务描述中的出站链接（Tasks 7.21.0+） |
| `task.file.outlinksInProperties` | `Link[]` | 文件属性中的出站链接 |
| `task.file.outlinksInBody` | `Link[]` | 文件正文中的出站链接 |
| `task.file.outlinks` | `Link[]` | 文件中所有出站链接 |

## Obsidian Properties（Tasks 7.7.0+）

通过文件 frontmatter 中的属性进行过滤和排序：

```tasks
filter by function task.file.hasProperty("status")
filter by function task.file.property("status") === "进行中"
sort by function task.file.property("priority") || 0
```

| 方法 | 返回类型 | 说明 |
|------|----------|------|
| `task.file.hasProperty('属性名')` | `boolean` | 检查文件是否有该属性 |
| `task.file.property('属性名')` | 各种类型 | 获取属性值，支持文本/数字/日期/列表/链接/复选框/嵌套对象 |

**示例**：frontmatter 中定义了 `project: "Alpha"`，则：
```
filter by function task.file.property("project") === "Alpha"
```

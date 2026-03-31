# Tasks 高级查询参考

## 自定义脚本函数

使用 JavaScript 函数实现自定义的过滤、排序和分组逻辑。

### filter by function

```tasks
filter by function task.description.includes("紧急")
filter by function task.due && task.due.isAfter(moment("2026-04-01"))
filter by function task.tags.length > 2
filter by function !task.isDone
```

### sort by function

```tasks
sort by function task.urgency
sort by function task.description.length
sort by function task.tags.length
```

返回数值进行排序，负数表示倒序。

### group by function

```tasks
group by function task.path.split("/")[0]
group by function task.tags[0] || "无标签"
```

返回字符串作为分组标题。

**Task 属性完整参考** → 加载 `references/task-properties.md`

## 正则过滤

### 标签正则

```tasks
tag regex matches /work|office/
tag regex does not match /^#context\//
```

### 描述正则

```tasks
description regex matches /紧急|重要/
description regex does not match /^[A-Z]/
```

## 全局查询忽略

`ignore global query` — 忽略在插件设置中配置的全局查询过滤器。

```tasks
ignore global query
path includes "Archive"
```

## 解释查询结果

`explain` — 在查询结果前显示调试信息，解释每个过滤器的匹配情况。

```tasks
explain
not done
due before tomorrow
```

## 预设查询 (Presets)

在插件设置中配置预设查询后，可在代码块中快速调用：

```tasks
preset this_file
```

`this_file` 是预设名称，使用在设置中定义的名称。

## 紧迫度 (Urgency)

紧迫度是一个综合评分，由以下因素计算：

| 因素 | 说明 | 分数范围 |
|------|------|----------|
| Due Date（截止日期） | **影响最大**，今天到期=8.8，提前/推后递变 | 0 ~ 12 |
| Priority（优先级） | 最高=9.0，高=6.0，中=3.9，无=1.95，低=0.0，最低=-1.8 | -1.8 ~ 9.0 |
| Scheduled Date（计划日期） | 今天或更早=5.0，否则=0.0 | 0 / 5.0 |
| Start Date（开始日期） | 明天或更晚=-3.0，否则=0.0 | -3.0 / 0.0 |

**注意事项**：
- 已完成任务紧迫度始终为 0
- 紧迫度不考虑任务状态和依赖关系
- 分数固定为 1.95 通常意味着元数据顺序错误导致解析失败

使用 `show urgency` 显示评分，`sort by urgency` 按紧迫度排序。

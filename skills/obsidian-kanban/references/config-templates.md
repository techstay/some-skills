# 常见配置模板

## 每日任务看板

适合每日任务管理，新任务置顶，日期链接到每日笔记。

```json
{
  "kanban-plugin": "basic",
  "show-checkboxes": true,
  "show-item-count": true,
  "new-card-insertion-method": "prepend",
  "date-trigger": "@",
  "date-format": "YYYY-MM-DD",
  "show-relative-date": true,
  "link-date-to-daily-note": true,
  "move-tags": "bottom",
  "move-task-metadata": true,
  "max-archive-size": 30,
  "archive-with-date": true
}
```

## 项目跟踪看板

适合项目管理，支持标签颜色、列折叠、较宽列显示更多信息。

```json
{
  "kanban-plugin": "basic",
  "show-checkboxes": true,
  "show-item-count": true,
  "list-collapse": true,
  "new-card-insertion-method": "append",
  "lane-width": 320,
  "date-format": "YYYY-MM-DD",
  "move-tags": "bottom",
  "tag-action": "search-board",
  "tag-colors": {
    "紧急": "#ff6b6b",
    "高优先级": "#ffa500",
    "低优先级": "#4ecdc4"
  },
  "move-task-metadata": true,
  "metadata-keys": ["assignee", "estimate"],
  "max-archive-size": 200,
  "archive-with-date": true
}
```

## 知识管理 MOC 看板

适合知识整理和内容管理，不需要复选框，重点展示元数据。

```json
{
  "kanban-plugin": "basic",
  "show-checkboxes": false,
  "show-item-count": true,
  "list-collapse": true,
  "new-card-insertion-method": "append",
  "lane-width": 280,
  "tag-action": "search-vault",
  "move-tags": "bottom",
  "metadata-keys": ["category", "author", "status"]
}
```

## 极简看板

最简配置，适合快速上手。

```json
{
  "kanban-plugin": "basic",
  "show-checkboxes": true,
  "show-item-count": false,
  "new-card-insertion-method": "append"
}
```

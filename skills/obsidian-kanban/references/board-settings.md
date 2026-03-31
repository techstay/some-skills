# Board Settings 完整参考

通过看板右上角 ⚙️ 按钮进入设置面板，或直接在 Markdown 文件中编辑 `%% kanban:settings %%` JSON 注释块。每个设置项均有「重置到默认」按钮。

> **提示**：设置同时支持全局默认（插件设置）和局部覆盖（单个看板文件内的 `%% kanban:settings %%` 块）。文件内设置优先于全局设置。

---

## 卡片显示

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `show-checkboxes` | bool | `true` | 卡片是否显示勾选复选框 |
| `show-item-count` | bool | `false` | 列标题旁是否显示卡片数量 |
| `hide-tags-in-title` | bool | `false` | 是否在卡片标题中隐藏标签 |
| `hide-dates-in-title` | bool | `false` | 是否在卡片标题中隐藏日期 |
| `new-card-insertion-method` | string | `"bottom"` | 新卡片插入位置：`"prepend"`（顶部）/ `"prepend-compact"`（顶部紧凑）/ `"append"`（底部） |
| `new-line-trigger` | string | `"enter"` | 卡片内新建行触发键：`"enter"` 或 `"shift-enter"` |

## 列布局

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `list-collapse` | bool | `false` | 是否允许折叠/展开列 |
| `hide-card-count` | bool | `false` | 隐藏列标题中的卡片数量（与 show-item-count 互斥） |
| `lane-width` | number | `272` | 列宽度（像素） |
| `full-list-lane-width` | bool | `false` | 列表视图中列是否展开到全宽 |

## 日期与时间

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `date-trigger` | string | `"@"` | 日期选择器触发字符 |
| `time-trigger` | string | `"@@"` | 时间选择器触发字符 |
| `date-format` | string | `"YYYY-MM-DD"` | 日期保存格式（moment.js 语法） |
| `time-format` | string | `"HH:mm"` | 时间显示格式 |
| `show-relative-date` | bool | `false` | 显示相对日期（如"3天后"）而非绝对日期 |
| `link-date-to-daily-note` | bool | `false` | 日期链接到每日笔记（需启用 Obsidian 日记核心插件） |

## 完成标记

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `complete-trigger` | string | `"✅"` | 标记完成的触发字符 |
| `complete-trigger-time` | string | `"✅ "` | 带时间戳的完成触发字符 |

## 归档

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `max-archive-size` | number | `-1` | 归档最大保留条数（`-1` = 无限） |
| `archive-with-date` | bool | `true` | 归档时是否自动添加完成日期 |
| `archive-date-time-format` | string | `"YYYY-MM-DD HH:mm"` | 归档日期时间格式 |

## 元数据显示

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `inline-metadata-position` | string | `"inline"` | 元数据显示位置：`"inline"`（行内）/ `"bottom"`（底部） |
| `move-task-metadata` | bool | `false` | 将 Tasks 插件元数据（📅🔁⏫等）移至卡片底部显示 |
| `metadata-keys` | array | `[]` | 显示链接笔记 frontmatter 中的哪些键值，如 `["category", "status", "priority"]` |

## 标签

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `move-tags` | string | `"in-card"` | 标签位置：`"in-card"`（在卡片正文中）/ `"bottom"`（在卡片底部） |
| `tag-action` | string | `"search-board"` | 点击标签时的行为：`"search-board"`（搜索当前看板）/ `"search-vault"`（搜索整个 vault） |
| `tag-colors` | object | `{}` | 标签颜色映射，格式：`{"标签名": "#颜色值"}` |
| `hide-tags-in-title` | bool | `false` | 是否在卡片标题中隐藏标签 |

## 笔记创建

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `note-template` | string | - | 从卡片创建笔记时使用的模板文件路径 |
| `note-folder` | string | - | 新笔记默认保存的文件夹路径 |

## 看板头部按钮

| 设置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `show-board-header-buttons` | bool | `true` | 是否显示看板头部操作按钮（搜索、设置、视图切换等） |

---

## 完整 JSON 示例

### 基础配置

```json
{
  "kanban-plugin": "basic",
  "show-checkboxes": true,
  "show-item-count": true,
  "new-card-insertion-method": "append",
  "lane-width": 272,
  "date-trigger": "@",
  "time-trigger": "@@",
  "date-format": "YYYY-MM-DD",
  "complete-trigger": "✅"
}
```

### 完整配置

```json
{
  "kanban-plugin": "basic",
  "show-checkboxes": true,
  "show-item-count": true,
  "list-collapse": true,
  "new-card-insertion-method": "append",
  "new-line-trigger": "enter",
  "lane-width": 300,
  "full-list-lane-width": false,
  "date-trigger": "@",
  "time-trigger": "@@",
  "date-format": "YYYY-MM-DD",
  "time-format": "HH:mm",
  "show-relative-date": true,
  "link-date-to-daily-note": true,
  "hide-dates-in-title": false,
  "hide-tags-in-title": false,
  "move-tags": "bottom",
  "tag-action": "search-board",
  "tag-colors": {
    "紧急": "#ff6b6b",
    "高优先级": "#ffa500",
    "低优先级": "#4ecdc4"
  },
  "move-task-metadata": true,
  "inline-metadata-position": "bottom",
  "metadata-keys": ["category", "status"],
  "max-archive-size": 50,
  "archive-with-date": true,
  "archive-date-time-format": "YYYY-MM-DD HH:mm",
  "complete-trigger": "✅",
  "show-board-header-buttons": true
}
```

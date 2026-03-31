# Kanban 与 Tasks 插件配合

## 卡片内使用 Tasks 语法

Kanban 卡片完全支持 Tasks 插件的 Emoji 元数据：

```markdown
- [ ] 写周报 📅 2026-04-05 🔼 #工作
- [ ] 每日复盘 🔁 every day 📅 2026-04-01
- [ ] 完善项目文档 ⏫ 🛫 2026-04-01 📅 2026-04-10
```

### Tasks Emoji 速查

| Emoji | 含义 | 示例 |
|-------|------|------|
| `📅` | 截止日期（Due） | `📅 2026-04-05` |
| `🛫` | 开始日期（Start） | `🛫 2026-04-01` |
| `⏳` | 计划日期（Scheduled） | `⏳ 2026-04-03` |
| `✅` | 完成日期（Done） | `✅ 2026-04-01` |
| `🔁` | 重复规则（Recurring） | `🔁 every week` |
| `⏫` | 高优先级 | — |
| `🔼` | 中优先级 | — |
| `🔽` | 低优先级 | — |

## Tasks 元数据显示控制

| 设置项 | 说明 |
|--------|------|
| `move-task-metadata` | 开启后，Tasks 的 Emoji 元数据显示在卡片底部而非正文中，保持卡片标题简洁 |
| `inline-metadata-position` | 控制内联元数据的显示位置：`"inline"`（行内）/ `"bottom"`（底部） |

## ⚠️ 关键限制：重复任务触发

**Kanban 内勾选复选框不会触发 Tasks 的重复任务逻辑。**

| 操作位置 | Tasks 重复逻辑是否触发 |
|----------|----------------------|
| Tasks 查询视图打勾 | ✅ 自动生成下一条 |
| Markdown 编辑模式打勾 | ✅ 自动生成下一条 |
| Kanban 看板中勾选 | ❌ 不会触发 |

### 原因

Tasks 插件监听的是 Markdown 编辑器中的文本变更事件，而 Kanban 的勾选操作直接修改 DOM 和内部状态，不经过编辑器的文本变更流程。

## 替代方案

### 1. 双视图操作

- 用 Tasks 查询视图做实际的打勾和重复任务生成
- Kanban 做可视化展示和拖拽管理
- 两者读取同一份 Markdown 数据，保持同步

### 2. 手动切换触发

- 在 Kanban 中勾选完成后
- 切换到 Markdown 编辑视图（Source Mode）
- 手动修改 `- [ ]` 为 `- [x]` 触发 Tasks 重复逻辑
- 切回 Kanban 视图查看更新

### 3. Templater 自动重建

使用 Templater 定时脚本，每天自动重建看板中的重复任务卡片：

```javascript
<%*
const tasks = ["每日复盘", "晨间日记", "运动打卡"];
const today = tp.date.now("YYYY-MM-DD");
tasks.forEach(task => {
  tR += `- [ ] ${task} 📅 ${today}\n`;
});
%>
```

### 4. 永久提醒卡片

- 把重复任务当作提醒卡片放在看板中
- 不勾选，仅作为视觉提醒
- 每天手动删除昨天的，添加今天的
- 或使用 Dataview 动态生成

### 5. 第三方状态联动插件

如 Kanban Status Updater 可在卡片移动时自动更新笔记属性，配合 Tasks 实现状态同步。

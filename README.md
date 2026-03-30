# some-skills

一些可能有用的技能（Skills），用于扩展 AI 大模型的能力。

## 📁 技能列表

### obsidian-tasks

Obsidian Tasks 插件技能 —— 在 Obsidian vault 的 Markdown 文件中创建、编辑和管理任务。

**功能覆盖：**

- 创建和编辑任务（含日期、优先级、标签、重复规则等元数据）
- 编写任务查询代码块（`tasks` 代码块）
- 任务状态管理（内置状态和自定义状态）
- 任务依赖关系（id / dependsOn）
- 高级查询（脚本函数、正则过滤、预设查询）

**文件结构：**

```
skills/obsidian-tasks/
├── SKILL.md                          # 主指令文件
└── references/
    ├── syntax-core.md                # 高频：任务语法、日期、优先级、标签、重复任务
    ├── query-basics.md               # 高频：常用查询指令（filter/sort/group/layout）
    ├── statuses.md                   # 中频：状态系统、自定义状态
    ├── dependencies.md               # 低频：任务依赖
    ├── query-advanced.md             # 低频：脚本函数、正则、预设、explain
    └── limitations.md                # 低频：限制与注意事项
```

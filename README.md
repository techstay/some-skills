# 🛠️ some-skills

<p>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=techstay.some-skills&left_color=555&right_color=e74c3c&left_text=visitors" alt="visitors" />
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License: MIT" /></a>
  <a href="https://github.com/techstay/some-skills"><img src="https://img.shields.io/badge/GitHub-repo-181717?style=flat-square&logo=github" alt="GitHub" /></a>
  <img src="https://img.shields.io/badge/Made%20with-%E2%9D%A4-red?style=flat-square" alt="Made with love" />
</p>

一些可能有用的技能（Skills），用于扩展 AI 大模型的能力。

<!--Quote starts-->
<details>
<summary><b>💡 每日灵感</b></summary>

<img src="https://quotes-github-readme.vercel.app/api?type=horizontal&theme=light" alt="Random Quote" />

</details>
<!--Quote ends-->

## 🚀 安装技能

本仓库的技能可以通过 `npx skills` CLI 工具安装到各种 AI 编码代理中（支持 OpenCode、Claude Code、Cursor、Codex 等 40+ 代理）。

### 快速安装

```bash
# 安装所有技能到项目
npx skills add techstay/some-skills

# 安装到全局
npx skills add techstay/some-skills -g

# 安装指定技能
npx skills add techstay/some-skills --skill obsidian-tasks --skill web-search

# 安装到指定代理
npx skills add techstay/some-skills -a opencode -a claude-code

# 查看可用技能（不安装）
npx skills add techstay/some-skills --list
```

### 更多命令

| 命令 | 说明 |
|------|------|
| `npx skills list` | 列出已安装的技能 |
| `npx skills find [query]` | 搜索技能 |
| `npx skills remove [skills]` | 移除已安装的技能 |
| `npx skills check` | 检查技能更新 |
| `npx skills update` | 更新所有已安装技能 |

> 了解更多：[vercel-labs/skills](https://github.com/vercel-labs/skills)

## 📁 技能列表

### ✅ obsidian-tasks

Obsidian Tasks 插件技能 —— 在 Obsidian vault 的 Markdown 文件中创建、编辑和管理任务。

**功能覆盖：**

- 创建和编辑任务（含日期、优先级、标签、重复规则等元数据）
- 编写任务查询代码块（`tasks` 代码块）
- 任务状态管理（内置状态和自定义状态）
- 任务依赖关系（id / dependsOn）
- 高级查询（脚本函数、正则过滤、预设查询）

### 🔍 web-search

网络搜索技能 —— 支持多后端（Tavily、Exa、Ollama）的网络检索，返回 YAML 格式结果。

### 📊 obsidian-kanban

Obsidian Kanban 插件技能 —— 在 Obsidian vault 中创建和管理基于 Markdown 的可视化看板。

**功能覆盖：**

- 创建和编辑看板（列、卡片、日期、标签、关联笔记）
- 完整的 Board Settings 配置参考
- 归档系统与列独立设置
- 与 Tasks 插件配合（含重复任务限制说明）
- 常见配置模板（每日看板、项目跟踪、知识管理等）
- FAQ 与故障排查指南

## ⭐ Star History

<a href="https://www.star-history.com/?repos=techstay%2Fsome-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=techstay/some-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=techstay/some-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=techstay/some-skills&type=date&legend=top-left" />
 </picture>
</a>

# some-skills

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

### web-search

网络搜索技能 —— 使用多种搜索后端（Tavily、Exa、Ollama）执行网络检索，返回带引用的 YAML 格式结果。

**功能覆盖：**

- 使用 Tavily / Exa / Ollama 进行网络搜索
- 结果以 YAML 格式输出，节省 token
- 支持新闻、金融等主题过滤（Tavily）
- 可通过 `--max-results` 控制结果数量

**文件结构：**

```
skills/web-search/
├── SKILL.md                          # 主指令文件
└── scripts/
    ├── web_search.py                 # 多后端搜索 CLI
    └── .env                          # API 密钥配置
```

## ⭐ Star History

<a href="https://www.star-history.com/?repos=techstay%2Fsome-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/image?repos=techstay/some-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/image?repos=techstay/some-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/image?repos=techstay/some-skills&type=date&legend=top-left" />
 </picture>
</a>

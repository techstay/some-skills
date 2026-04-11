---
name: marimo
description: >
  Create and manage reactive Python notebooks in Marimo. Use when creating notebooks,
  adding UI input components, writing SQL queries, deploying as apps, or learning
  about Marimo's reactive execution model.
  Keywords: marimo notebook, reactive notebook, Python notebook, UI components, SQL cell, app deployment.
license: MIT
version: "0.23.1"
---

# Marimo Skill

Marimo is an open-source reactive Python notebook that reimagines traditional Jupyter notebooks as reproducible, interactive, and shareable Python programs.

## Quick Reference

| What you want to do | How to do it |
|---------------------|--------------|
| Create a new notebook | Run `marimo edit` or `marimo edit notebook.py` |
| Add UI input components | Load `references/ui-inputs.md`, use `mo.ui.*` components |
| Write SQL queries | Load `references/sql-data.md`, create a SQL cell |
| Deploy as a web app | Load `references/apps-deployment.md`, run `marimo run notebook.py` |
| Understand reactive execution | Load `references/core-concepts.md`, learn the DAG execution model |
| View CLI commands | Load `references/cli-commands.md` |

---

## Key Workflow Rules

### ⚠️ Most Common Pitfalls

#### Mutations Are Not Tracked

**Avoid:**

- ❌ Defining a variable in one cell and mutating it in another
- ❌ Using `list.append()`, `df['col'] = values`, and similar mutation operations

**Follow:**

- ✅ Complete all mutations in the same cell where the variable is defined
- ✅ Create new variables instead of mutating old ones (`new_list = old_list + [item]`)
- ✅ Use a pure functional style for data processing

#### Global Variable Names Must Be Unique

**Avoid:**

- ❌ Defining a global variable with the same name in multiple cells
- ❌ Imported module names conflicting with variable names

**Follow:**

- ✅ Define each global variable in exactly one cell
- ✅ Use underscore prefix for local variables (`_temp_var`)
- ✅ Wrap temporary variables inside functions

---

## Reference Files — Load On Demand

**Do not load all at once. Only load the files needed for the current task.**

| File | Content | When to load |
|------|---------|-------------|
| `references/core-concepts.md` | Reactive execution model, DAG, variable rules | When you need to understand how Marimo works |
| `references/ui-inputs.md` | Detailed usage of all UI input components | When you need to add interactive controls |
| `references/sql-data.md` | SQL cells, database connections, data processing | When you need to use SQL queries |
| `references/apps-deployment.md` | App deployment, layout options, grid/slides | When you need to deploy as a web app |
| `references/cli-commands.md` | All CLI commands and options | When you need to check command-line usage |

---

## Common Mistakes

| ❌ Wrong | ✅ Right | Reason |
|----------|----------|--------|
| `df['new_col'] = values` in another cell | Complete in the same cell | Mutations are not tracked |
| `my_list.append(x)` in another cell | Create new list: `my_list + [x]` | Mutations are not tracked |
| Define `x = ...` in multiple cells | Define each variable in only one cell | Violates uniqueness rule |
| Use global variables to pass intermediate results | Wrap in functions or use return values | Avoids hidden dependencies |

---

## Quick Examples

### Basic Notebook Structure

```python
# Cell 1: Imports
import marimo as mo
import pandas as pd

# Cell 2: Data preparation
data = {"x": [1, 2, 3], "y": [4, 5, 6]}
df = pd.DataFrame(data)

# Cell 3: Add interactivity
slider = mo.ui.slider(1, 10, value=5)
slider

# Cell 4: Reactive computation
filtered_df = df[df["x"] < slider.value]
filtered_df
```

### Running Notebooks

```bash
# Edit mode
marimo edit notebook.py

# Run as app
marimo run notebook.py

# Convert to script execution
python notebook.py
```

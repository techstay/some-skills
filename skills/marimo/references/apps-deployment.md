# Marimo App Deployment & Layout

Marimo can run any notebook as an interactive web app. The `marimo run` command lays out the notebook as an app and starts a web server to host it.

## Running Apps

### Basic Commands

```bash
# Run a single notebook as an app
marimo run notebook.py

# Specify port
marimo run notebook.py --port 8080

# Host setting (0.0.0.0 allows external access)
marimo run notebook.py --host 0.0.0.0
```

### Running Multiple Notebooks (Gallery)

```bash
# Run an entire folder as an app gallery
marimo run folder/

# Run multiple specified files
marimo run notebook_a.py notebook_b.py folder/

# Watch mode (for development, auto-refreshes gallery index)
marimo run folder/ --watch
```

The gallery displays a page with one card per notebook. Cards can use notebook OpenGraph metadata to show titles, descriptions, and thumbnails.

---

## App Layouts

### Vertical Layout (Default)

The default layout is vertical: cell outputs are concatenated vertically, code is hidden.

```bash
marimo run notebook.py
```

Features:
- All outputs are arranged vertically in cell order
- Code is hidden by default (configurable to show)
- Use `mo.hstack`, `mo.vstack`, and other functions for complex programmatic layouts

### Grid Layout

Use a drag-and-drop grid editor to arrange the app interface.

**How to enable:**

In the app preview of `marimo edit`, enable the grid editor via the dropdown menu.

**How to use:**

1. In edit mode, click the "Preview" button to see the app layout
2. Select "Grid layout" from the dropdown
3. Drag outputs onto the grid
4. Resize and reposition

Features:
- Visual drag-and-drop interface
- No layout code needed
- Layout is saved in the `layouts/` folder

### Slides Layout

Present content in a slides-like experience.

**How to enable:**

Select "Slides layout" from the dropdown in the app preview.

Features:
- Slide order is determined by cell order in the notebook
- Drag-and-drop reordering is not supported
- All outputs shown, code hidden
- Supports PDF export

**PDF export command:**

```bash
marimo export pdf notebook.py --as=slides --raster-server=live
```

---

## Layout Functions

Use Marimo's layout functions to programmatically organize outputs in code.

### Basic Layouts

#### `mo.hstack(items, justify="start", align="center", gap=0)`
Horizontal stack

```python
mo.hstack([
    mo.ui.button(label="Left"),
    mo.ui.button(label="Center"),
    mo.ui.button(label="Right")
], justify="center", gap=1)
```

Parameters:
- `justify`: `"start"`, `"center"`, `"end"`, `"between"`, `"around"`, `"evenly"`
- `align`: `"start"`, `"center"`, `"end"`, `"stretch"`
- `gap`: spacing size (number, 0-4)

#### `mo.vstack(items, justify="start", align="stretch", gap=0)`
Vertical stack

```python
mo.vstack([
    mo.md("# Title"),
    mo.ui.text(label="Input:"),
    mo.ui.button(label="Submit")
], gap=2)
```

#### `mo.hstack([...], gap=1)` and `mo.vstack([...], gap=1)`

Shorthand for creating spaced layouts:

```python
# Horizontal arrangement, gap 1
mo.hstack([component1, component2, component3], gap=1)

# Vertical arrangement, gap 2
mo.vstack([header, content, footer], gap=2)
```

### Alignment & Distribution

#### Horizontal Alignment

```python
# Left-aligned (default)
mo.hstack([a, b, c], justify="start")

# Center-aligned
mo.hstack([a, b, c], justify="center")

# Right-aligned
mo.hstack([a, b, c], justify="end")

# Space between
mo.hstack([a, b, c], justify="between")

# Evenly distributed
mo.hstack([a, b, c], justify="around")
mo.hstack([a, b, c], justify="evenly")
```

#### Vertical Alignment

```python
# Top-aligned
mo.hstack([a, b, c], align="start")

# Center-aligned
mo.hstack([a, b, c], align="center")

# Bottom-aligned
mo.hstack([a, b, c], align="end")

# Stretch to fill
mo.hstack([a, b, c], align="stretch")
```

### Advanced Layouts

#### `mo.accordion(items)`
Accordion collapsible panels

```python
mo.accordion({
    "Section 1": mo.md("Content for section 1"),
    "Section 2": mo.md("Content for section 2"),
    "Section 3": mo.md("Content for section 3")
})
```

#### `mo.tabs(tabs, value=None)`
Tabs

```python
mo.tabs({
    "Plot": mo.ui.plotly(fig),
    "Data": mo.ui.dataframe(df),
    "Summary": mo.md(summary_text)
})
```

#### `mo.sidebar(content)`
Sidebar

```python
mo.sidebar([
    mo.md("## Menu"),
    mo.ui.button(label="Home"),
    mo.ui.button(label="Settings"),
    mo.ui.button(label="About")
])
```

#### `mo.callout(content, kind="info")`
Callout box

```python
mo.callout("This is an important note!", kind="info")
mo.callout("Warning: This action cannot be undone.", kind="warn")
mo.callout("Success! Your changes have been saved.", kind="success")
mo.callout("Error: Failed to save file.", kind="error")
```

### Responsive Layout

#### Condition-Based Display

```python
show_details = mo.ui.switch(label="Show details")
show_details
```

```python
# Conditional display based on switch value
content = [mo.md("## Summary")]

if show_details.value:
    content.append(mo.ui.dataframe(df))
    content.append(mo.ui.plotly(fig))

mo.vstack(content)
```

#### Dynamic Layout

```python
# Dynamically create layout based on data
items = [mo.ui.button(label=f"Button {i}") for i in range(5)]

# Choose layout based on count
if len(items) <= 3:
    layout = mo.hstack(items, gap=1)
else:
    layout = mo.vstack(items, gap=1)

layout
```

---

## Layout Persistence

### Layouts Folder

Marimo saves layout metadata in a `layouts/` folder:

```
my_notebook/
├── notebook.py
└── layouts/
    └── notebook.json
```

**Important**:
- Include the `layouts/` folder when sharing or deploying notebooks
- Check the `layouts/` folder into version control
- Deleting `layouts/` will lose custom layouts

### Layout Configuration

```python
# Set layout options in the notebook
import marimo as mo

# Configure app width
mo.app_config({
    "app_width": "medium",  # "narrow", "medium", "full"
    "layout": "vertical"    # "vertical", "grid", "slides"
})
```

---

## Deployment Checklist

### Pre-Deployment Checks

- [ ] All dependencies listed in `requirements.txt`
- [ ] Sensitive information uses environment variables
- [ ] Data file paths are relative or use environment variables
- [ ] `layouts/` folder is included in deployment
- [ ] App tested locally with `marimo run`

### Environment Variables

```python
import os

# Read configuration from environment variables
DATABASE_URL = os.environ.get("DATABASE_URL")
API_KEY = os.environ.get("API_KEY")
```

### Docker Deployment Example

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["marimo", "run", "app.py", "--host", "0.0.0.0", "--port", "8080"]
```

# Marimo CLI Command Reference

Marimo provides a rich command-line interface (CLI) for creating, editing, running, and deploying notebooks.

## Installation & Basics

### Installing Marimo

```bash
# Basic install
pip install marimo

# With recommended dependencies (SQL, AI completions, etc.)
pip install "marimo[recommended]"

# SQL support only
pip install "marimo[sql]"

# Using uv
uv add marimo
uv add "marimo[recommended]"

# Using conda
conda install -c conda-forge marimo
```

### Verifying Installation

```bash
# Check version
marimo --version

# View help
marimo --help
```

---

## Core Commands

### `marimo edit` - Edit / Create Notebooks

Launch the Marimo editor to create or edit notebooks.

```bash
# Create a new notebook (auto-assigned port)
marimo edit

# Specify a port
marimo edit --port 8080

# Edit a specific file
marimo edit notebook.py

# Specify host (allow external access)
marimo edit --host 0.0.0.0

# Headless mode (don't auto-open browser)
marimo edit --headless

# Specify browser
marimo edit --browser firefox
```

**Common options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--port` | Server port | Random available port |
| `--host` | Host address | `127.0.0.1` |
| `--headless` | Don't auto-open browser | `False` |
| `--browser` | Specify browser | System default |
| `--no-token` | Disable CSRF token | - |
| `--token` | Custom CSRF token | - |

### `marimo run` - Run Apps

Run a notebook as an interactive web app.

```bash
# Run a single notebook
marimo run notebook.py

# Specify port
marimo run notebook.py --port 8080

# Allow external access
marimo run notebook.py --host 0.0.0.0

# Run an entire folder (gallery mode)
marimo run folder/

# Run multiple specified files
marimo run notebook_a.py notebook_b.py

# Watch mode (for development)
marimo run folder/ --watch

# Silent mode
marimo run notebook.py --silent
```

**Common options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--port` | Server port | `8080` |
| `--host` | Host address | `127.0.0.1` |
| `--watch` | Watch for file changes | `False` |
| `--base-url` | Base URL path | `/` |
| `--silent` | Reduce log output | `False` |

### `marimo export` - Export

Export notebooks to various formats.

```bash
# Export as HTML
marimo export html notebook.py

# Export as HTML with code included
marimo export html notebook.py --include-code

# Export as runnable HTML (embeds Python runtime)
marimo export html notebook.py --self-contained

# Export as Markdown
marimo export markdown notebook.py

# Export as plain Python script
marimo export python notebook.py

# Export as Jupyter notebook
marimo export ipynb notebook.py

# Export as PDF (requires extra dependencies)
marimo export pdf notebook.py

# Export as slides PDF
marimo export pdf notebook.py --as=slides --raster-server=live

# Specify output filename
marimo export html notebook.py -o output.html

# Output to stdout
marimo export python notebook.py -o -
```

**Export options:**

| Format | Command | Notes |
|--------|---------|-------|
| HTML | `export html` | Static or interactive HTML |
| Markdown | `export markdown` | Markdown format |
| Python | `export python` | Plain Python script |
| Jupyter | `export ipynb` | Jupyter notebook |
| PDF | `export pdf` | Requires Playwright |

**HTML export options:**

| Option | Description |
|--------|-------------|
| `--include-code` | Include code |
| `--self-contained` | Self-contained (embeds runtime) |
| `--no-iframe` | Don't use iframe |
| `--title` | Custom title |

### `marimo convert` - Convert

Convert Jupyter notebooks to Marimo format.

```bash
# Convert Jupyter notebook to Marimo
marimo convert notebook.ipynb > notebook.py

# Batch convert
marimo convert *.ipynb

# Use web interface to convert
# Visit https://marimo.io/convert
```

### `marimo tutorial` - Tutorials

Run built-in tutorials.

```bash
# List all tutorials
marimo tutorial --help

# Run the intro tutorial
marimo tutorial intro

# Run the UI components tutorial
marimo tutorial ui

# Run the SQL tutorial
marimo tutorial sql

# Run the data visualization tutorial
marimo tutorial plots

# Run the layout tutorial
marimo tutorial layout

# And more...
```

---

## Configuration Commands

### `marimo config` - Configuration Management

```bash
# View current configuration
marimo config show

# Set a configuration item
marimo config set key value

# Get a configuration item
marimo config get key

# Remove a configuration item
marimo config remove key

# Reset all configuration
marimo config reset
```

---

## Environment Variables

Marimo supports the following environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `MARIMO_HOST` | Default host | `0.0.0.0` |
| `MARIMO_PORT` | Default port | `8080` |
| `MARIMO_BROWSER` | Default browser | `firefox` |
| `MARIMO_TOKEN` | CSRF token | `secret-token` |
| `MARIMO_SQL_OUTPUT_TYPE` | Default SQL output type | `native` |
| `MARIMO_APP_WIDTH` | Default app width | `medium` |

---

## Configuration Files

### pyproject.toml Configuration

```toml
[tool.marimo]
# SQL configuration
sql_output_type = "native"
sql_linter = true

# Runtime configuration
[tool.marimo.runtime]
auto_run = true
auto_run_on_cell_execution = true

# Data source configuration
[tool.marimo.datasources]
auto_discover_schemas = true
auto_discover_tables = "auto"
auto_discover_columns = "auto"

# Editor configuration
[tool.marimo.editor]
app_width = "medium"  # "narrow", "medium", "full"
```

---

## Full Examples

### Development Workflow

```bash
# 1. Create a new notebook
marimo edit my_app.py

# 2. After editing, test in app mode
marimo run my_app.py

# 3. Export as HTML to share
marimo export html my_app.py -o my_app.html --include-code

# 4. Deploy to server
marimo run my_app.py --host 0.0.0.0 --port 8080
```

### CI/CD Integration

```yaml
# .github/workflows/deploy.yml
name: Deploy Marimo App

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install marimo -r requirements.txt
      
      - name: Export HTML
        run: |
          marimo export html app.py -o dist/index.html
      
      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

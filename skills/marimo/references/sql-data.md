# Marimo SQL and Data Processing

Marimo has native SQL support, allowing you to mix Python and SQL to query dataframes, databases, and data warehouses.

## Installing Dependencies

```bash
# Basic install (uses DuckDB)
pip install "marimo[sql]"

# Or with uv
uv add "marimo[sql]"

# Or with conda
conda install -c conda-forge marimo duckdb polars
```

---

## Creating a SQL Cell

There are three ways to create a SQL cell:

1. **Right-click** the "+" button next to a cell and select "SQL cell"
2. Convert an empty cell to SQL via the cell context menu
3. Click the SQL button that appears at the bottom of the notebook

A created SQL cell looks like this:

```sql
SELECT * FROM my_table LIMIT 10
```

Under the hood, this is syntactic sugar for a Python f-string:

```python
output_df = mo.sql(f"SELECT * FROM my_table LIMIT {max_rows}")
```

---

## Querying Local DataFrames

You can reference Python dataframes directly in SQL:

```python
import pandas as pd
import marimo as mo

# Create a dataframe
df = pd.DataFrame({
    "name": ["Alice", "Bob", "Charlie"],
    "age": [25, 30, 35],
    "city": ["NYC", "LA", "Chicago"]
})
```

```sql
-- Directly reference the df variable
SELECT * FROM df WHERE age > 25
```

If a table with the same name exists in the database, the database table takes precedence.

---

## Output Variables

Define output variables in SQL cells to use results in other cells:

```sql
-- Define output variable filtered_data
filtered_data = SELECT * FROM df WHERE age > 25
```

```python
# Use the result in a Python cell
print(filtered_data.value)

# The result is a Polars or Pandas DataFrame
import matplotlib.pyplot as plt
plt.hist(filtered_data.value['age'])
```

**Note**: Using an underscore prefix (e.g. `_df`) makes the variable private, inaccessible from other cells.

---

## Querying Files and APIs

Marimo's SQL is based on DuckDB, which can directly query many data sources:

### Query CSV Files

```sql
SELECT * FROM read_csv('path/to/file.csv')
```

### Query Parquet Files

```sql
SELECT * FROM read_parquet('path/to/file.parquet')
```

### Query JSON Files

```sql
SELECT * FROM read_json('path/to/file.json')
```

### Query HTTP APIs

```sql
SELECT * FROM read_csv_auto('https://api.example.com/data.csv')
```

### Query S3 Storage

```sql
SELECT * FROM read_parquet('s3://my-bucket/data.parquet')
```

---

## Connecting to Databases

### Via UI

Click the "Add database connection" button in the notebook, supports:
- PostgreSQL
- MySQL
- SQLite
- DuckDB
- Snowflake
- BigQuery

### Via Code

Create connection engines using various libraries:

**SQLAlchemy:**

```python
import sqlalchemy

# Create an in-memory SQLite database
engine = sqlalchemy.create_engine("sqlite:///:memory:")
```

**SQLModel:**

```python
import sqlmodel

engine = sqlmodel.create_engine("sqlite:///:memory:")
```

**Ibis:**

```python
import ibis

engine = ibis.connect("sqlite:///:memory:")
```

**DuckDB:**

```python
import duckdb

conn = duckdb.connect("file.db")
```

After creating the engine, select it in the SQL cell's connection dropdown.

---

## SQL Output Types

Marimo supports different SQL query output types, useful when working with large datasets.

### Configuring Output Type

Set the output type in the top-right of the app configuration:

| Option | Description |
|--------|-------------|
| `native` | Uses DuckDB native lazy relations (recommended for best performance) |
| `lazy-polars` | Returns a lazy Polars DataFrame |
| `polars` | Returns an eager Polars DataFrame |
| `pandas` | Returns a Pandas DataFrame |
| `auto` | Auto-selects based on installed packages |

### Recommended Settings

- **Large datasets**: Use `native` to avoid loading the entire result into memory
- **Python processing needed**: Use `polars` or `pandas`
- **Chained SQL**: Use `native` for easier SQL cell chaining

---

## SQL Utilities

### SQL Linter

Automatically checks SQL code with better autocompletion and error highlighting.

Disable in `pyproject.toml`:

```toml
[tool.marimo]
sql_linter = false
```

### SQL Formatting

Click the paint roller icon in the bottom-right of a SQL cell to auto-format SQL code.

### SQL Mode

For in-memory DuckDB, Marimo provides a validation mode that validates SQL as you write.

---

## Full Example

### Interactive SQL Query Tool

```python
import marimo as mo
import pandas as pd

# Load data
@mo.cache
def load_data():
    return pd.read_csv("sales_data.csv")

df = load_data()

# Create query controls
controls = mo.vstack([
    mo.md("## SQL Query Builder"),
    mo.hstack([
        mo.ui.dropdown(df.columns.tolist(), label="Select column"),
        mo.ui.dropdown(["=", ">", "<", ">=", "<=", "!="], label="Operator", value="="),
        mo.ui.text(label="Value")
    ]),
    mo.ui.button(label="Execute Query", on_click=lambda: None)
])
controls
```

```sql
-- Dynamically generated query
{% raw %}
{% set col = controls[1][0].value %}
{% set op = controls[1][1].value %}
{% set val = controls[1][2].value %}

SELECT * FROM df WHERE {{ col }} {{ op }} '{{ val }}' LIMIT 100
{% endraw %}
```

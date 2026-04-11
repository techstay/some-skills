# Marimo Core Concepts

## Reactive Execution Model

Marimo uses a **reactive execution model**, which is one of the biggest differences from Jupyter.

### How It Works

1. **Static Analysis**: Marimo analyzes each cell without executing code to determine:
   - **References**: global variables that the cell reads but does not define
   - **Definitions**: global variables that the cell defines

2. **Build DAG**: Based on reference and definition relationships, Marimo builds a Directed Acyclic Graph (DAG)

3. **Reactive Execution**: When a cell runs, all cells that reference its defined variables automatically re-run

```
Cell A: x = 1          (defines x)
   ↓
Cell B: y = x + 1      (references x, defines y)
   ↓
Cell C: print(y)       (references y)
```

When Cell A changes, Cell B and Cell C automatically re-execute.

### Execution Order

- Cell execution order is determined by variable relationships, not by position on the page
- This is similar to how spreadsheets behave
- You can place helper functions at the bottom of the notebook and they will work logically

### Deleting Cells Deletes Variables

**Key feature**: In Marimo, **deleting a cell removes its global variables from program memory**.

- Cells that reference those variables will automatically re-run and become invalidated
- This eliminates the hidden state problem common in traditional notebooks

---

## Variable Rules

### 1. Mutations Are Not Tracked

Marimo **does not track variable mutations**.

**❌ Wrong:**

```python
# Cell 1
my_list = [1, 2, 3]

# Cell 2
my_list.append(4)  # This will not trigger Cell 1 to re-run
```

**✅ Right:**

```python
# Cell 1
my_list = [1, 2, 3]

# Cell 2
new_list = my_list + [4]  # Create a new variable
```

**Why?**

- Reliably tracking mutations in Python is impossible
- Reacting to mutations could cause unexpected cell re-runs

### 2. Global Variable Names Must Be Unique

**Each global variable can only be defined in one cell.**

**❌ Wrong:**

```python
# Cell 1
x = 1

# Cell 2
x = 2  # Error! x is already defined in Cell 1
```

**✅ Right:**

```python
# Cell 1
x = 1

# Cell 2
y = 2  # Use a different variable name
```

**Why?**

- This ensures Marimo can maintain consistency between code and output
- Encourages reducing the number of global variables

---

## Creating Temporary Variables

### Use Underscore Prefix

Variables starting with an underscore (e.g. `_temp`) are "local" to the cell:

- Other cells cannot read them
- Multiple cells can reuse the same local variable name

```python
# Cell 1
_temp = expensive_computation()  # Only visible in Cell 1
result1 = _temp + 1

# Cell 2
_temp = another_computation()  # Can reuse _temp
result2 = _temp * 2
```

### Wrap in Functions

If you want most variables in a cell to be temporary, wrap the code in a function:

```python
def _():
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot([1, 2])
    return ax

_()
```

Here `plt`, `fig`, and `ax` are not added to global variables.

---

## Configuring Run Mode

### Runtime Configuration

Through the notebook settings menu, you can configure how Marimo runs cells:

| Option | Description |
|--------|-------------|
| Auto-run on startup | Whether to auto-run all cells when opening the notebook |
| Auto-run on execution | Whether to auto-run dependent cells after modifying a cell |
| Module auto-reload | Whether to auto-reload when imported modules change |

### Disabling Cells

Sometimes you want to edit part of a notebook without triggering automatic execution of dependent cells:

- **Disable cell**: Right-click a cell and select "Disable"
- Disabled cells and their dependent cells will not run
- When re-enabled, Marimo will auto-run the cell if ancestor cells have run

---

## Best Practices

### ✅ Do

1. **Create new variables instead of mutating old ones**
   ```python
   # Good
   new_list = old_list + [item]
   
   # Bad
   old_list.append(item)
   ```

2. **Complete all mutations in the cell where the variable is defined**
   ```python
   # Cell 1
   df = pd.DataFrame({"a": [1, 2]})
   df["b"] = [3, 4]  # Mutate in the same cell
   ```

3. **Use local variables to reduce global variable count**
   ```python
   _temp = compute()  # _ prefix = local variable
   result = _temp + 1
   ```

4. **Wrap complex logic in functions**
   ```python
   def _():
       # Complex computation
       return result
   _()
   ```

### ❌ Don't

1. **Don't mutate the same variable across different cells**
2. **Don't use the `global` keyword**
3. **Don't rely on cell execution order** (rely on variable relationships instead)
4. **Don't create too many global variables**

---

## Troubleshooting

### Problem: Cells Not Auto-Running

**Possible causes:**
1. Runtime configuration is set to "lazy" mode
2. Cell is disabled
3. Variable relationships are not correctly established

**Solution:**
- Check runtime configuration in the settings menu
- Confirm the cell is not disabled
- Check that variable names are spelled correctly

### Problem: Incorrect Variable Values

**Possible causes:**
1. Hidden state (should already be prevented by Marimo)
2. Cell execution order is unexpected

**Solution:**
- Use "Runtime > Restart and run all cells"
- Check variable dependency relationships
- Ensure no variable is defined with the same name in multiple cells

### Problem: Slow Performance

**Solution:**
- Enable lazy mode (mark as stale instead of auto-running)
- Use `mo.stop()` to conditionally stop execution
- See the [Expensive Notebooks guide](https://docs.marimo.io/guides/expensive_notebooks/)

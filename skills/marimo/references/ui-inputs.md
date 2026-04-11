# Marimo UI Input Components

Marimo provides a rich set of interactive UI components for building powerful notebooks and apps. All components live under the `marimo.ui` namespace.

## Basic Usage

Three steps to using UI components:

1. **Import**: `import marimo as mo`
2. **Create**: Assign the component to a global variable
3. **Display**: Output the component at the end of a cell

```python
import marimo as mo

# Create a slider
slider = mo.ui.slider(1, 100, value=50)
slider
```

## Accessing Component Values

Access a component's value via the `.value` attribute:

```python
# Use the component value in another cell
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x * slider.value / 10)

plt.plot(x, y)
plt.title(f"Frequency: {slider.value}")
plt.show()
```

When the user interacts with a component, `.value` updates automatically, and all cells referencing that component re-run automatically.

---

## Input Components

### Text Input

#### `mo.ui.text(label=None, value="")`
Single-line text input

```python
name = mo.ui.text("Enter your name:", value="Alice")
name
```

#### `mo.ui.text_area(label=None, value="", rows=4)`
Multi-line text input

```python
bio = mo.ui.text_area("Tell us about yourself:", rows=6)
bio
```

#### `mo.ui.code_editor(language="python", value="")`
Code editor

```python
code = mo.ui.code_editor(language="python", value="print('Hello World')")
code
```

### Numeric Input

#### `mo.ui.number(start, stop, value=None, label=None)`
Number input box

```python
age = mo.ui.number(0, 150, value=25, label="Age:")
age
```

#### `mo.ui.slider(start, stop, value=None, step=None, label=None)`
Slider

```python
slider = mo.ui.slider(0, 100, value=50, step=5, label="Value:")
slider
```

#### `mo.ui.range_slider(start, stop, value=None, label=None)`
Range slider (select an interval)

```python
range_slider = mo.ui.range_slider(0, 100, value=(20, 80), label="Range:")
range_slider
```

### Selection Inputs

#### `mo.ui.dropdown(options, value=None, label=None)`
Dropdown select

```python
color = mo.ui.dropdown(
    ["red", "green", "blue", "yellow"],
    value="blue",
    label="Favorite color:"
)
color
```

#### `mo.ui.radio(options, value=None, label=None)`
Radio button group

```python
size = mo.ui.radio(["small", "medium", "large"], value="medium", label="Size:")
size
```

#### `mo.ui.multiselect(options, value=None, label=None)`
Multi-select dropdown

```python
toppings = mo.ui.multiselect(
    ["cheese", "pepperoni", "mushrooms", "onions"],
    value=["cheese"],
    label="Pizza toppings:"
)
toppings
```

#### `mo.ui.checkbox(value=False, label=None)`
Checkbox

```python
agree = mo.ui.checkbox(value=False, label="I agree to the terms")
agree
```

#### `mo.ui.switch(value=False, label=None)`
Switch (toggle button)

```python
dark_mode = mo.ui.switch(value=False, label="Dark mode")
dark_mode
```

### Date & Time Inputs

#### `mo.ui.date(value=None, label=None)`
Date picker

```python
birth_date = mo.ui.date(value="1990-01-01", label="Birth date:")
birth_date
```

#### `mo.ui.datetime(value=None, label=None)`
Datetime picker

```python
appointment = mo.ui.datetime(label="Appointment:")
appointment
```

#### `mo.ui.date_range(start=None, end=None, label=None)`
Date range picker

```python
trip_dates = mo.ui.date_range(label="Trip dates:")
trip_dates
```

---

## Advanced Components

### File Upload

#### `mo.ui.file(label=None, multiple=False)`
File upload component

```python
uploaded_file = mo.ui.file(label="Upload a file:", multiple=False)
uploaded_file
```

Access the uploaded file:

```python
# Get file content
if uploaded_file.value:
    content = uploaded_file.value[0].contents
    filename = uploaded_file.value[0].name
```

#### `mo.ui.file_browser(start_path=".", label=None)`
File browser

```python
selected_file = mo.ui.file_browser(start_path="./data", label="Select file:")
selected_file
```

### Buttons

#### `mo.ui.button(label="Click me", on_click=None)`
Regular button

```python
click_count = mo.ui.state(0)

def on_click():
    click_count.value += 1

button = mo.ui.button(label=f"Clicked {click_count.value} times", on_click=on_click)
button
```

#### `mo.ui.run_button(label="Run")`
Run button (triggers cell re-execution)

```python
run_btn = mo.ui.run_button(label="Refresh data")
run_btn
```

#### `mo.ui.refresh(label="Refresh", seconds=None)`
Auto-refresh button / timer

```python
# Manual refresh button
refresh_btn = mo.ui.refresh(label="Update")

# Auto-refresh every 5 seconds
auto_refresh = mo.ui.refresh(seconds=5)
auto_refresh
```

### Data Structure Editing

#### `mo.ui.array(elements, label=None)`
Array editor

```python
arr = mo.ui.array([mo.ui.number(0, 100) for _ in range(3)], label="Values:")
arr
```

#### `mo.ui.dictionary(value, label=None)`
Dictionary editor

```python
dict_editor = mo.ui.dictionary(
    {"name": mo.ui.text("Name"), "age": mo.ui.number(0, 150)},
    label="Person:"
)
dict_editor
```

#### `mo.ui.matrix(shape, value=None, label=None)`
Matrix / vector editor

```python
matrix = mo.ui.matrix((3, 3), label="Matrix:")
matrix
```

### Forms

#### `mo.ui.form(children, on_submit=None)`
Form component (batch submit multiple inputs)

```python
name_input = mo.ui.text(label="Name:")
age_input = mo.ui.number(0, 150, label="Age:")
email_input = mo.ui.text(label="Email:")

form = mo.ui.form([name_input, age_input, email_input], label="Submit")
form
```

Access form values:

```python
if form.value:
    print(f"Name: {form.value['Name:']}")
    print(f"Age: {form.value['Age:']}")
```

### Tabs

#### `mo.ui.tabs(tabs, value=None)`
Tabs component

```python
tabs = mo.ui.tabs({
    "Tab 1": mo.ui.text("Content for tab 1"),
    "Tab 2": mo.ui.text("Content for tab 2"),
    "Tab 3": mo.ui.text("Content for tab 3")
})
tabs
```

Get the currently selected tab:

```python
print(tabs.value)  # Outputs the currently selected tab name
```

---

## Data Display Components

### DataFrame

#### `mo.ui.dataframe(df, selection=None)`
Interactive dataframe viewer

```python
df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
table = mo.ui.dataframe(df, selection="multi")
table
```

### Table

#### `mo.ui.table(data, pagination=10)`
Table component

```python
data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]
table = mo.ui.table(data, pagination=5)
table
```

### Data Explorer

#### `mo.ui.data_explorer(df)`
Data explorer (auto-analyzes data)

```python
df = pd.DataFrame({"A": [1, 2, 3, 4, 5], "B": [5, 4, 3, 2, 1]})
explorer = mo.ui.data_explorer(df)
explorer
```

---

## Integration Components

### Chart Integrations

#### `mo.ui.altair_chart(chart)`
Interactive Altair chart

```python
import altair as alt

chart = alt.Chart(df).mark_point().encode(x='A', y='B')
interactive_chart = mo.ui.altair_chart(chart)
interactive_chart
```

#### `mo.ui.plotly(fig)`
Interactive Plotly chart

```python
import plotly.express as px

fig = px.scatter(df, x="A", y="B")
interactive_plot = mo.ui.plotly(fig)
interactive_plot
```

#### `mo.ui.matplotlib(fig)`
Reactive Matplotlib chart

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 2])
mo.ui.matplotlib(fig)
```

### Chat Interface

#### `mo.ui.chat(messages=None, on_send=None)`
Chat interface component

```python
def on_send(message):
    return f"Echo: {message}"

chat = mo.ui.chat(on_send=on_send)
chat
```

### Custom Widget

#### `mo.ui.anywidget(widget)`
Custom widget using anywidget

```python
import anywidget
import traitlets

class CounterWidget(anywidget.AnyWidget):
    _esm = """
    export function render({ model, el }) {
      let count = () => model.get("count");
      let btn = document.createElement("button");
      btn.innerHTML = `Count is ${count()}`;
      btn.addEventListener("click", () => {
        model.set("count", count() + 1);
        model.save_changes();
      });
      el.appendChild(btn);
    }
    """
    count = traitlets.Int(0).tag(sync=True)

counter = mo.ui.anywidget(CounterWidget())
counter
```

---

## Best Practices

### Component Composition Patterns

Combine multiple components into more complex interfaces:

```python
import marimo as mo

# Create form components
name = mo.ui.text(label="Name")
age = mo.ui.number(0, 150, label="Age")
email = mo.ui.text(label="Email")
submit = mo.ui.button(label="Submit")

# Compose into a form interface
form = mo.vstack([
    mo.md("## User Registration"),
    name,
    age,
    email,
    submit
])
form
```

### Conditional Display

Show content conditionally based on component values:

```python
toggle = mo.ui.switch(label="Show advanced options")
toggle
```

```python
# Show different content based on switch value
if toggle.value:
    mo.vstack([
        mo.ui.number(label="Advanced param 1"),
        mo.ui.number(label="Advanced param 2")
    ])
else:
    mo.md("Basic mode enabled")
```

### State Management

Use `mo.ui.state()` for complex state management:

```python
# Create state
counter = mo.ui.state(0)

def increment():
    counter.value += 1

button = mo.ui.button(label=f"Count: {counter.value}", on_click=increment)
button
```

---

## Full Example

### Interactive Data Explorer

```python
import marimo as mo
import pandas as pd
import matplotlib.pyplot as plt

# Load data
@mo.cache

def load_data():
    return pd.read_csv("data.csv")

df = load_data()

# Create interactive controls
filters = mo.vstack([
    mo.md("## Data Explorer"),
    mo.hstack([
        mo.ui.dropdown(df.columns.tolist(), label="X axis"),
        mo.ui.dropdown(df.columns.tolist(), label="Y axis")
    ]),
    mo.ui.range_slider(0, len(df), label="Row range"),
    mo.ui.checkbox(label="Show trend line")
])
filters
```

```python
# Generate chart based on control values
x_col = filters[1][0].value
y_col = filters[1][1].value
row_range = filters[2].value
show_trend = filters[3].value

filtered_df = df.iloc[row_range[0]:row_range[1]]

fig, ax = plt.subplots()
ax.scatter(filtered_df[x_col], filtered_df[y_col])

if show_trend:
    z = np.polyfit(filtered_df[x_col], filtered_df[y_col], 1)
    p = np.poly1d(z)
    ax.plot(filtered_df[x_col], p(filtered_df[x_col]), "r--")

ax.set_xlabel(x_col)
ax.set_ylabel(y_col)
mo.ui.matplotlib(fig)
```

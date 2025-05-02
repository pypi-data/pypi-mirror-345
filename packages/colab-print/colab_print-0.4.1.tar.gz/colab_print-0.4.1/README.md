# Colab Print

[![PyPI version](https://img.shields.io/pypi/v/colab-print.svg)](https://pypi.org/project/colab-print/)
[![Python versions](https://img.shields.io/pypi/pyversions/colab-print.svg)](https://pypi.org/project/colab-print/)
[![License](https://img.shields.io/github/license/alaamer12/colab-print.svg)](https://github.com/alaamer12/colab-print/blob/main/LICENSE)

**Colab Print** is a Python library that enhances the display capabilities of Jupyter and Google Colab notebooks, providing beautiful, customizable HTML outputs for text, lists, dictionaries, tables, pandas DataFrames, and progress bars.

## Features

- 🎨 **Rich Text Styling** - Display text with predefined styles or custom CSS
- 📊 **Beautiful DataFrame Display** - Present pandas DataFrames with extensive styling options
- 📑 **Customizable Tables** - Create HTML tables with headers, rows, and custom styling
- 📜 **Formatted Lists** - Display Python lists and tuples as ordered or unordered HTML lists
- 📖 **Readable Dictionaries** - Render dictionaries as structured definition lists
- 🎭 **Extensible Themes** - Use built-in themes or create your own custom styles
- 📏 **Smart Row/Column Limiting** - Automatically display large DataFrames with sensible limits
- 🔍 **Cell Highlighting** - Highlight specific rows, columns, or individual cells in tables and DataFrames
- 📊 **Progress Tracking** - Display elegant progress bars with tqdm compatibility
- 🔄 **Graceful Fallbacks** - Works even outside Jupyter/IPython environments
- 🧩 **Structured Data Detection** - Automatic handling of nested structures, matrices, and array-like objects

## Installation

```bash
pip install colab-print
```

## Quick Start

```python
from colab_print import Printer, header, success, progress
import pandas as pd
import time

# Create a printer with default styles
printer = Printer()

# Use pre-configured styling functions
header("Colab Print Demo")
success("Library loaded successfully!")

# Display styled text
printer.display("Hello, World!", style="highlight")

# Display a list with nested elements (automatically detected and styled)
my_list = ['apple', 'banana', ['nested', 'item'], 'cherry', {'key': 'value'}]
printer.display_list(my_list, ordered=True, style="info")

# Show a progress bar
for i in progress(range(10), desc="Processing"):
    time.sleep(0.2)  # Simulate work

# Display a dictionary
my_dict = {
    'name': 'Alice', 
    'age': 30, 
    'address': {'street': '123 Main St', 'city': 'Anytown'}
}
printer.display_dict(my_dict, style="success")

# Display a simple table
headers = ["Name", "Age", "City"]
rows = [
    ["Alice", 28, "New York"],
    ["Bob", 34, "London"],
    ["Charlie", 22, "Paris"]
]
printer.display_table(headers, rows, style="default")

# Display a pandas DataFrame with styling
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [28, 34, 22],
    'City': ['New York', 'London', 'Paris']
})
printer.display_df(df, 
                  highlight_cols=['Name'],
                  highlight_cells={(0, 'Age'): "background-color: #FFEB3B;"},
                  caption="Sample DataFrame")
```

## Styling & Shortcut Functions

### Predefined Style Shortcuts

Colab Print provides convenient shortcut functions with pre-configured styling:

```python
from colab_print import (
    header, title, subtitle, section_divider, subheader,
    code, card, quote, badge, data_highlight, footer,
    highlight, info, success, warning, error, muted, primary, secondary,
    dfd, table, list_, dict_, progress
)

# Display styled text with a single function call
header("Main Section")
title("Document Title")
subtitle("Supporting information")
success("Operation completed!")
warning("Proceed with caution")
error("An error occurred")
code("print('Hello World')")

# Display different content types with shortcuts
table(headers, rows)
list_(my_list, ordered=True)
dict_(my_dict)
dfd(df, highlight_cols=["Name"])
```

### Predefined Styles

- `default` - Clean, professional styling
- `highlight` - Stand-out text with emphasis
- `info` - Informational blue text
- `success` - Positive green message
- `warning` - Attention-grabbing yellow alert
- `error` - Critical red message
- `muted` - Subtle gray text
- `primary` - Primary blue-themed text
- `secondary` - Secondary purple-themed text
- `code` - Code-like display with monospace font
- `card` - Card-like container with shadow
- `quote` - Styled blockquote
- `notice` - Attention-drawing notice
- `badge` - Compact badge-style display

### Custom Styling

You can add your own styles:

```python
printer = Printer()
printer.add_style("custom", "color: purple; font-size: 20px; font-weight: bold;")
printer.display("Custom styled text", style="custom")
```

## Display Methods

- `printer.display(text, style="default", **inline_styles)`: Displays styled text.
- `printer.display_list(items, ordered=False, style="default", item_style=None, **inline_styles)`: Displays lists/tuples.
- `printer.display_dict(data, style="default", key_style=None, value_style=None, **inline_styles)`: Displays dictionaries.
- `printer.display_table(headers, rows, style="default", **table_options)`: Displays basic tables.
- `printer.display_df(df, style="default", **df_options)`: Displays pandas DataFrames with many options.
- `printer.display_progress(total, desc="", style="default", **progress_options)`: Displays a progress bar.

## Progress Tracking

Colab Print offers powerful progress tracking with tqdm compatibility:

```python
from colab_print import progress, Printer
import time

# Simple progress bar using iterable
for i in progress(range(100), desc="Processing"):
    time.sleep(0.01)  # Do some work

# Manual progress
printer = Printer()
progress_id = printer.display_progress(total=50, desc="Manual progress")
for i in range(50):
    time.sleep(0.05)  # Do some work
    printer.update_progress(progress_id, i+1)

# Progress with customization
for i in progress(range(100), 
                 desc="Custom progress", 
                 color="#9C27B0", 
                 height="25px",
                 style="card"):
    time.sleep(0.01)

# Undetermined progress (loading indicator)
progress_id = printer.display_progress(total=None, desc="Loading...", animated=True)
time.sleep(3)  # Do some work with unknown completion time
```

## DataFrame Display Options

The `display_df` method supports numerous customization options:

```python
printer.display_df(df,
                  style='default',           # Base style
                  max_rows=20,               # Max rows to display
                  max_cols=10,               # Max columns to display
                  precision=2,               # Decimal precision for floats
                  header_style="...",        # Custom header styling
                  odd_row_style="...",       # Custom odd row styling
                  even_row_style="...",      # Custom even row styling
                  index=True,                # Show index
                  width="100%",              # Table width
                  caption="My DataFrame",    # Table caption
                  highlight_cols=["col1"],   # Highlight columns
                  highlight_rows=[0, 2],     # Highlight rows
                  highlight_cells={(0,0): "..."}, # Highlight specific cells
                  font_size="14px",          # Custom font size for all cells
                  text_align="center")       # Text alignment for all cells
```

## Advanced List Display

Colab Print automatically detects and optimally displays complex data structures:

```python
from colab_print import list_
import numpy as np
import pandas as pd

# Nested lists are visualized with hierarchical styling
nested_list = [1, 2, [3, 4, [5, 6]], 7]
list_(nested_list)

# Matrices are displayed as tables automatically
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
list_(matrix)

# NumPy arrays are handled seamlessly
np_array = np.array([[1, 2, 3], [4, 5, 6]])
list_(np_array)

# Pandas data structures work too
series = pd.Series([1, 2, 3, 4])
list_(series)

# Control display format manually if needed
list_(matrix, matrix_mode=False)  # Force list display for a matrix
```

## Advanced Usage

### Creating Custom Themes

```python
custom_themes = {
    'dark': 'color: white; background-color: #333; font-size: 16px;',
    'fancy': 'color: #8A2BE2; font-family: "Brush Script MT", cursive; font-size: 20px;'
}

printer = Printer(additional_styles=custom_themes)
printer.display("Dark theme", style="dark")
printer.display("Fancy theme", style="fancy")
```

### Creating Reusable Display Functions

```python
# Create a function with predefined styling
my_header = printer.create_styled_display("header", color="#FF5722", font_size="24px")

# Use it multiple times with consistent styling
my_header("First Section")
my_header("Second Section")

# Still allows overrides at call time
my_header("Special Section", color="#9C27B0")
```

### Handling Non-Notebook Environments

The library gracefully handles non-IPython environments by printing fallback text representations:

```python
# This will work in regular Python scripts
printer.display_list([1, 2, 3])
printer.display_dict({'a': 1})
printer.display_df(df)
```

## Exception Handling

Colab Print includes a comprehensive exception hierarchy for robust error handling:

```python
from colab_print import (
    ColabPrintError,        # Base exception
    StyleNotFoundError,     # When a style isn't found
    DataFrameError,         # DataFrame-related issues
    InvalidParameterError,  # Parameter validation failures
    HTMLRenderingError      # HTML rendering problems
)

try:
    printer.display("Some text", style="non_existent_style")
except StyleNotFoundError as e:
    print(f"Style error: {e}")
```

## Full Examples

For a comprehensive demonstration of all features, please see the example script:

[example.py](https://github.com/alaamer12/colab-print/blob/main/example.py)

This script covers:
- Text, List, Dictionary, Table, and DataFrame display
- Using built-in styles and inline styles
- Adding custom styles
- Creating a Printer instance with custom themes
- Highlighting options for DataFrames
- Progress bar usage and customization
- Advanced list and nested structure display
- Exception handling
- Fallback behavior notes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

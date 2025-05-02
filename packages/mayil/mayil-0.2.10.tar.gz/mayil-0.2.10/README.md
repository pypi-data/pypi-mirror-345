# Mayil

A beautiful HTML email generator for Python that makes creating professional, responsive emails a breeze.

[Homepage](https://mayil.vercel.app/)

## Installation

```bash
pip install mayil
```

## Quick Start

```python
import mayil as my
import pandas as pd



# Add content
my.title("Welcome to Our Newsletter", center=True)
my.header("Latest Updates")
my.text("Stay informed with our latest news and updates.")
my.metric("Active Users", "1,234", color="#88C0D0")
my.sticky_note("Important Notice", "Please read this carefully.", color="blue")

# Add a table
df = pd.DataFrame({
    'Name': ['John', 'Jane'],
    'Score': ['95', '85']
})
my.dataframe(df, align='center')

# Get the HTML content
html_content = my.body
```

## Features

- 🎨 Beautiful, responsive email templates
- 📊 Data visualization with tables and metrics
- 🎯 Conditional formatting for tables
- 📝 Rich text formatting
- 📱 Mobile-friendly design
- 🔗 Easy hyperlink support
- 📐 Flexible layout options with columns
- 📈 Interactive Plotly charts support

## API Reference

### Basic Components

#### Title
```python
my.title("Welcome", center=True)
```
Adds a large title to the email. Optionally center it.

#### Header
```python
my.header("Section Title")
```
Adds a section header.

#### Subheader
```python
my.subheader("Subsection Title")
```
Adds a subsection header.

#### Text
```python
my.text("Your paragraph text", justify=True)
```
Adds a paragraph of text. Optionally justify the text.

#### Metric
```python
my.metric("Active Users", "1,234", color="#88C0D0")
```
Displays a metric with label and value. Customize the value color.

#### Sticky Note
```python
my.sticky_note("Important", "Read this carefully", color="blue")
```
Adds a sticky note component. Colors: yellow, green, blue, red, white, violet, orange, darkgreen.

#### Divider
```python
my.divider()
```
Adds a light grey dotted divider line.

### Layout Components

#### Columns
```python
cols = my.columns(3)
with cols[0]:
    my.metric("Metric 1", "100")
with cols[1]:
    my.metric("Metric 2", "200")
```
Creates a multi-column layout (max 4 columns).

### Table Components

#### DataFrame
```python
df = pd.DataFrame({
    'Name': ['John', 'Jane'],
    'Score': ['95', '85']
})
my.dataframe(df, align='center')
```
Adds a styled DataFrame to the email.

#### Formatted Table (ftable)
```python
conditions = {
    'Score': [
        (lambda x: x < '90', '#ffb3ba'),  # Pastel red
        (lambda x: x >= '90', '#baffc9')  # Pastel green
    ],
    'Status': [
        (lambda x: x.lower() == 'active', '#bae1ff'),  # Pastel blue
        (lambda x: x.lower() == 'inactive', '#ffdfba')  # Pastel orange
    ]
}
my.ftable(df, cell_colors=conditions, align='center')
```
Adds a table with conditional formatting based on column values.

### Data Visualization

#### Plotly Chart
```python
import plotly.express as px

# Create a sample plotly figure
df = pd.DataFrame({
    'Date': pd.date_range('2024-01-01', '2024-01-10'),
    'Value': [10, 15, 13, 17, 19, 16, 14, 18, 20, 22]
})
fig = px.line(df, x='Date', y='Value', title='Trend Analysis')

# Add the plotly chart to the email
my.plotly_chart(fig)
```
Adds an interactive Plotly chart to the email. The chart will be rendered as an HTML component that can be interacted with in email clients that support HTML content.

### Links

#### Hyperlink
```python
my.hyperlink("Visit our website", "https://example.com")
```
Adds a clickable link to the email.

## Advanced Usage

### Creating Multiple Instances

```python
from mayil import Mayil

# Create a new instance
custom_instance = Mayil()
custom_instance.header("Custom Header")
```

### Table Formatting Options

The `ftable` method supports three types of conditional formatting:

1. `conditions`: Applies formatting to both cell background and text
2. `cell_colors`: Applies formatting only to cell background
3. `text_colors`: Applies formatting only to text

Each condition is defined as a tuple of (lambda function, color) where:
- The lambda function should return a boolean
- The color can be any valid CSS color (hex, rgb, named colors)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


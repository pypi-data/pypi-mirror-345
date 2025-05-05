# 🧠 SheryAnalysis - Advanced EDA Library

## 📦 Overview
A powerful, user-friendly Python library for exploratory data analysis that makes it easy to analyze DataFrames, identify column types, handle missing values intelligently, and gain insights from your data — all with minimal code.

```python
import pandas as pd
from sheryanalysis import analyze

df = pd.read_csv("your_data.csv")
analyze(df)  # Get instant insights about your data
```

## 🌟 Key Features

- **Smart Data Analysis**: Automatically detect column types and provide meaningful statistics
- **Advanced Missing Value Handling**: Multiple imputation strategies including KNN and regression
- **Configurable Verbosity**: Control the level of detail in output
- **Comprehensive Error Handling**: Clear error messages and graceful fallbacks
- **Type Hints & Documentation**: Well-documented API with examples

---

## 📊 Core Functionality

### 1. Basic Analysis

```python
from sheryanalysis import analyze

# Basic analysis with default verbosity
results = analyze(df)

# Control output detail level (0=minimal, 1=normal, 2=verbose)
analyze(df, verbosity=2)  # Detailed output
analyze(df, verbosity=0)  # Minimal output

# Override column classification
custom_types = {
    'categorical': ['country', 'product'],
    'numerical': ['price', 'quantity'],
    'datetime': ['order_date'],
    'text': ['description']
}
analyze(df, column_types=custom_types)
```

#### What You Get:
- DataFrame shape and dimensions
- Column names and data types
- Null value summary
- Intelligent column classification:
  - 🔠 Categorical columns
  - 🔢 Numerical columns
  - 📅 Datetime columns
  - 📝 Text columns

### 2. Value Count Analysis

```python
# Top N value counts for all columns
analyze.value_count(df, n=5)

# Value counts for a single column
analyze.value_count(df['category'])

# Value counts for categorical columns only
analyze.value_count_category(df)
```

### 3. Column-Specific Analysis

```python
# Get detailed statistics for a specific column
stats = analyze.get_column_analysis(df, 'age')
```

#### Statistics Provided:
- Basic info (data type, null count, unique values)
- For numerical columns: min, max, mean, median, std dev, skewness
- Outlier detection using IQR method
- Top values and their frequencies

---

## 🧩 Missing Value Handling

### 1. Single Column Imputation

```python
# Auto-select best imputation method
analyze.fill_nulls(df, 'age')

# Specify imputation method
analyze.fill_nulls(df, 'category', method='mode')
analyze.fill_nulls(df, 'age', method='median')
analyze.fill_nulls(df, 'status', method='constant', value='Unknown')

# Advanced methods
analyze.fill_nulls(df, 'income', method='knn')
analyze.fill_nulls(df, 'expenses', method='regression')

# Return a copy instead of modifying in-place
df_filled = analyze.fill_nulls(df, 'age', inplace=False)
```

### 2. Multi-Column Imputation

```python
# Fill all columns with auto-selected methods
analyze.fill_nulls_all(df)

# Specify methods for specific columns
methods = {
    'age': 'median',
    'category': 'mode',
    'status': 'constant'
}
analyze.fill_nulls_all(df, methods=methods)

# Skip columns with too many nulls
analyze.fill_nulls_all(df, drop_threshold=0.3)  # Skip if >30% nulls
```

### 3. Direct Imputer Access

```python
from sheryanalysis import Imputer

# Create an imputer with custom verbosity
imputer = Imputer(df, verbosity=1)

# Use the imputer directly
imputer.fill_nulls('age', method='knn')
imputer.fill_nulls_all(methods={'income': 'regression'})
```

---

## �️ Advanced Usage

### Controlling Verbosity

All functions accept a `verbosity` parameter to control output detail:

```python
# 0 = Minimal output (warnings and errors only)
# 1 = Normal output (default)
# 2 = Verbose output (detailed information)
analyze(df, verbosity=2)
analyze.fill_nulls_all(df, verbosity=0)
```

### Categorical Column Detection

Control how categorical columns are detected:

```python
# Adjust the uniqueness threshold (default is 0.05 or 5%)
analyze(df, threshold=0.1)  # Consider columns with ≤10% unique values as categorical
```

---

## 🔜 Coming Soon

- **Data Visualization**: Automatic plots for distributions, correlations, and missing values
- **Report Generation**: Export analysis to HTML, PDF, or Markdown
- **Data Preprocessing**: Feature scaling, encoding, and other preprocessing functions
- **Statistical Tests**: Common statistical tests for data analysis
- **Command-Line Interface**: Run analyses from the command line

---

## 📦 Installation

```bash
pip install sheryanalysis
```

## 🧪 Requirements

- Python 3.7+
- pandas >= 1.0.0
- numpy >= 1.18.0
- scikit-learn >= 0.22.0

---

## � Examples

### Quick Start

```python
import pandas as pd
from sheryanalysis import analyze

# Load your data
df = pd.read_csv("data.csv")

# Get basic insights
analyze(df)

# Handle missing values
analyze.fill_nulls_all(df)

# Check the results
analyze(df)
```

### Complete Workflow

```python
import pandas as pd
from sheryanalysis import analyze, Imputer

# Load data
df = pd.read_csv("data.csv")

# Initial analysis
analyze(df, verbosity=2)

# Examine specific columns
analyze.get_column_analysis(df, 'age')
analyze.value_count(df['category'])

# Handle missing values with custom strategies
methods = {
    'age': 'median',
    'income': 'regression',
    'category': 'mode',
    'status': 'constant'
}
analyze.fill_nulls_all(df, methods=methods)

# Final analysis
analyze(df)
```

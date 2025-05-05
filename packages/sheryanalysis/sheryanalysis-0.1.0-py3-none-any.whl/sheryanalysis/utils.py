"""
Utility functions for sheryanalysis.
Contains helper functions for data analysis and manipulation.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union, Any
from datetime import datetime
import re

def detect_column_types(df: pd.DataFrame, 
                        threshold: float = 0.05, 
                        datetime_format: Optional[str] = None) -> Dict[str, List[str]]:
    """
    Detect column types in a DataFrame.
    
    This function categorizes columns into:
    - categorical: Columns with low cardinality relative to row count
    - numerical: Columns with numeric data types and high cardinality
    - datetime: Columns containing datetime values
    - text: Columns with string data and high cardinality
    
    Args:
        df: The pandas DataFrame to analyze
        threshold: Uniqueness ratio threshold for categorical columns
        datetime_format: Optional datetime format string for detection
        
    Returns:
        Dict with column types as keys and lists of column names as values
    """
    total_rows = len(df)
    column_types = {
        'categorical': [],
        'numerical': [],
        'datetime': [],
        'text': []
    }
    
    for col in df.columns:
        # Skip columns with all null values
        if df[col].isnull().all():
            continue
            
        # Check for datetime columns
        if _is_datetime_column(df[col], datetime_format):
            column_types['datetime'].append(col)
            continue
            
        # Check data type
        if pd.api.types.is_numeric_dtype(df[col]):
            # Calculate uniqueness ratio
            unique_vals = df[col].nunique()
            unique_ratio = unique_vals / total_rows
            
            if unique_ratio <= threshold:
                column_types['categorical'].append(col)
            else:
                column_types['numerical'].append(col)
        else:
            # For non-numeric columns
            unique_vals = df[col].nunique()
            unique_ratio = unique_vals / total_rows
            
            if unique_ratio <= threshold:
                column_types['categorical'].append(col)
            else:
                # High cardinality string columns are likely text data
                column_types['text'].append(col)
    
    return column_types

def _is_datetime_column(series: pd.Series, datetime_format: Optional[str] = None) -> bool:
    """
    Check if a series contains datetime values.
    
    Args:
        series: The pandas Series to check
        datetime_format: Optional datetime format string
        
    Returns:
        bool: True if the series contains datetime values
    """
    # If already datetime type
    if pd.api.types.is_datetime64_dtype(series):
        return True
        
    # If numeric, probably not datetime
    if pd.api.types.is_numeric_dtype(series):
        return False
        
    # Sample non-null values for testing
    sample = series.dropna().head(5)
    if len(sample) == 0:
        return False
        
    # Try to convert to datetime
    try:
        if datetime_format:
            # Try with specified format
            pd.to_datetime(sample, format=datetime_format)
        else:
            # Try automatic inference
            pd.to_datetime(sample)
        return True
    except:
        return False

def get_column_stats(df: pd.DataFrame, column: str) -> Dict[str, Any]:
    """
    Get detailed statistics for a specific column.
    
    Args:
        df: The pandas DataFrame
        column: The column name
        
    Returns:
        Dict containing statistics for the column
    """
    stats = {}
    
    # Basic stats
    stats['name'] = column
    stats['dtype'] = str(df[column].dtype)
    stats['count'] = len(df[column])
    stats['null_count'] = df[column].isnull().sum()
    stats['null_percentage'] = (stats['null_count'] / stats['count']) * 100
    stats['unique_count'] = df[column].nunique()
    stats['unique_percentage'] = (stats['unique_count'] / stats['count']) * 100
    
    # Type-specific stats
    if pd.api.types.is_numeric_dtype(df[column]):
        stats['min'] = df[column].min()
        stats['max'] = df[column].max()
        stats['mean'] = df[column].mean()
        stats['median'] = df[column].median()
        stats['std'] = df[column].std()
        stats['skewness'] = df[column].skew()
        stats['kurtosis'] = df[column].kurtosis()
        
        # Check for outliers using IQR method
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        outlier_count = ((df[column] < (Q1 - 1.5 * IQR)) | (df[column] > (Q3 + 1.5 * IQR))).sum()
        stats['outlier_count'] = outlier_count
        stats['outlier_percentage'] = (outlier_count / stats['count']) * 100
    
    # For categorical columns, get value counts
    if stats['unique_count'] <= 20:  # Only for columns with reasonable number of categories
        value_counts = df[column].value_counts().head(10).to_dict()
        stats['top_values'] = value_counts
    
    return stats

def suggest_imputation_method(df: pd.DataFrame, column: str) -> Tuple[str, Any]:
    """
    Suggest an appropriate imputation method for a column.
    
    Args:
        df: The pandas DataFrame
        column: The column name
        
    Returns:
        Tuple of (method_name, imputation_value)
    """
    # Check if column exists
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    # If no nulls, no imputation needed
    if df[column].isnull().sum() == 0:
        return ("none", None)
    
    # For categorical/object columns
    if df[column].dtype == 'object' or df[column].nunique() < 10:
        # Use mode for categorical data
        if df[column].mode().empty:
            return ("constant", "MISSING")
        else:
            return ("mode", df[column].mode().iloc[0])
    
    # For numeric columns
    elif pd.api.types.is_numeric_dtype(df[column]):
        # Check skewness
        skewness = df[column].skew()
        
        # For highly skewed data, use median
        if abs(skewness) > 1:
            return ("median", df[column].median())
        # For normally distributed data, use mean
        else:
            return ("mean", df[column].mean())
    
    # For datetime columns
    elif pd.api.types.is_datetime64_dtype(df[column]):
        # Use median date
        return ("median", df[column].median())
    
    # Default fallback
    return ("mode", df[column].mode().iloc[0] if not df[column].mode().empty else "MISSING")

"""
Main analyzer module for sheryanalysis.
Provides functions for exploratory data analysis.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union, Any, Callable
import warnings
from .logger import get_logger
from .utils import detect_column_types, get_column_stats
from .imputer import Imputer

def analyze(df: pd.DataFrame,
           threshold: float = 0.05,
           verbosity: int = 1,
           column_types: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
    """
    Perform basic analysis on a pandas DataFrame.

    This function analyzes the DataFrame and prints a summary report including:
    - Basic information (shape, columns)
    - Data types
    - Null values
    - Column classification (categorical, numerical, datetime, text)

    Args:
        df: The pandas DataFrame to analyze
        threshold: Uniqueness ratio threshold for categorical columns
        verbosity: Verbosity level (0=minimal, 1=normal, 2=verbose)
        column_types: Optional manual column type classification

    Returns:
        Dict containing analysis results

    Examples:
        >>> import pandas as pd
        >>> from sheryanalysis import analyze
        >>> df = pd.read_csv("data.csv")
        >>> analyze(df)
    """
    # Input validation
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Please pass a pandas DataFrame")

    # Initialize logger
    logger = get_logger(verbosity)

    # Create results dictionary
    results = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'null_counts': df.isnull().sum().to_dict(),
        'total_rows': len(df)
    }

    # Detect column types
    if column_types is None:
        results['column_types'] = detect_column_types(df, threshold)
    else:
        results['column_types'] = column_types

    # Print report based on verbosity
    if verbosity >= 1:
        logger.info("\n🔍 Basic Analysis Report")
        logger.info("-" * 60)
        logger.info(f"📏 Shape: {results['shape']}")
        logger.info(f"🧱 Columns: {results['columns']}")

        if verbosity >= 2:
            logger.info(f"\n🧪 Data Types:\n{df.dtypes}")
            logger.info(f"\n🧼 Null Values:\n{df.isnull().sum()}")
        else:
            # Simplified output for normal verbosity
            null_cols = [col for col, count in results['null_counts'].items() if count > 0]
            if null_cols:
                logger.info(f"\n🧼 Columns with nulls: {null_cols}")
            else:
                logger.info("\n✅ No null values found")

        # Print column classifications
        for col_type, cols in results['column_types'].items():
            if cols:
                emoji = {
                    'categorical': '🔠',
                    'numerical': '🔢',
                    'datetime': '📅',
                    'text': '📝'
                }.get(col_type, '📋')

                logger.info(f"\n{emoji} {col_type.capitalize()} Columns: {cols}")

    # Save for use in other functions
    analyze._results = results

    return results


def value_count(data: Union[pd.DataFrame, pd.Series],
               n: int = 3,
               verbosity: int = 1) -> Dict[str, Dict[Any, int]]:
    """
    Show value counts for DataFrame columns or a Series.

    Args:
        data: The pandas DataFrame or Series to analyze
        n: Number of top values to show
        verbosity: Verbosity level (0=minimal, 1=normal, 2=verbose)

    Returns:
        Dict containing value counts for each column

    Examples:
        >>> import pandas as pd
        >>> from sheryanalysis import analyze
        >>> df = pd.read_csv("data.csv")
        >>> analyze.value_count(df)
        >>> # Or for a single column:
        >>> analyze.value_count(df['column_name'])
    """
    logger = get_logger(verbosity)
    results = {}

    if verbosity >= 1:
        logger.info(f"\n🔁 Value Counts (Top {n}):")

    try:
        if isinstance(data, pd.Series):
            # For a single Series
            col_name = data.name or "Series"
            value_counts = data.value_counts().head(n).to_dict()
            results[col_name] = value_counts

            if verbosity >= 1:
                logger.info(f"\n▶️ {col_name}")
                for val, count in value_counts.items():
                    logger.info(f"{val}: {count}")

        elif isinstance(data, pd.DataFrame):
            # For a DataFrame
            for col in data.columns:
                try:
                    value_counts = data[col].value_counts().head(n).to_dict()
                    results[col] = value_counts

                    if verbosity >= 1:
                        logger.info(f"\n▶️ {col}")
                        for val, count in value_counts.items():
                            logger.info(f"{val}: {count}")

                except Exception as e:
                    results[col] = {"error": str(e)}
                    if verbosity >= 1:
                        logger.warning(f"⛔ Cannot compute value counts for '{col}': {str(e)}")
        else:
            raise ValueError("Please pass a pandas DataFrame or Series")

    except Exception as e:
        logger.error(f"Error computing value counts: {str(e)}")

    return results


def value_count_category(df: pd.DataFrame,
                        threshold: float = 0.05,
                        verbosity: int = 1,
                        column_types: Optional[Dict[str, List[str]]] = None) -> Dict[str, Dict[Any, int]]:
    """
    Show value counts for categorical columns in a DataFrame.

    Args:
        df: The pandas DataFrame to analyze
        threshold: Uniqueness ratio threshold for categorical columns
        verbosity: Verbosity level (0=minimal, 1=normal, 2=verbose)
        column_types: Optional manual column type classification

    Returns:
        Dict containing value counts for categorical columns

    Examples:
        >>> import pandas as pd
        >>> from sheryanalysis import analyze
        >>> df = pd.read_csv("data.csv")
        >>> analyze.value_count_category(df)
    """
    logger = get_logger(verbosity)
    results = {}

    if not isinstance(df, pd.DataFrame):
        logger.error("⛔ Please pass a pandas DataFrame")
        return results

    # Get categorical columns
    if column_types is None:
        col_types = detect_column_types(df, threshold)
        cat_cols = col_types['categorical']
    else:
        cat_cols = column_types.get('categorical', [])

    if not cat_cols:
        logger.warning("⚠️ No categorical columns found based on uniqueness threshold.")
        return results

    if verbosity >= 1:
        logger.info("\n📊 Value Counts of Categorical Columns:")

    # Get value counts for each categorical column
    for col in cat_cols:
        try:
            value_counts = df[col].value_counts().to_dict()
            results[col] = value_counts

            if verbosity >= 1:
                logger.info(f"\n▶️ {col}")
                for val, count in value_counts.items():
                    logger.info(f"{val}: {count}")

        except Exception as e:
            results[col] = {"error": str(e)}
            if verbosity >= 1:
                logger.warning(f"⛔ Cannot compute value counts for '{col}': {str(e)}")

    return results


def fill_nulls(df: pd.DataFrame,
              column: str,
              method: Optional[str] = None,
              value: Optional[Any] = None,
              inplace: bool = True,
              verbosity: int = 1) -> Optional[pd.DataFrame]:
    """
    Fill null values in a specific column with an appropriate strategy.

    Args:
        df: The pandas DataFrame to modify
        column: The column name to fill nulls in
        method: The imputation method ('mean', 'median', 'mode', 'constant', 'knn', 'regression')
               If None, an appropriate method will be suggested based on the data
        value: The value to use for imputation (only used with 'constant' method)
        inplace: Whether to modify the DataFrame in place
        verbosity: Verbosity level (0=minimal, 1=normal, 2=verbose)

    Returns:
        Modified DataFrame if inplace=False, None otherwise

    Examples:
        >>> import pandas as pd
        >>> from sheryanalysis import analyze
        >>> df = pd.read_csv("data.csv")
        >>> # Fill nulls in a column using an automatically selected method
        >>> analyze.fill_nulls(df, 'age')
        >>> # Fill nulls with a specific method
        >>> analyze.fill_nulls(df, 'category', method='mode')
        >>> # Fill nulls with a constant value
        >>> analyze.fill_nulls(df, 'status', method='constant', value='Unknown')
    """
    imputer = Imputer(df, verbosity=verbosity)
    return imputer.fill_nulls(column, method=method, value=value, inplace=inplace)


def fill_nulls_all(df: pd.DataFrame,
                  drop_threshold: float = 0.2,
                  methods: Optional[Dict[str, str]] = None,
                  inplace: bool = True,
                  verbosity: int = 1) -> Optional[pd.DataFrame]:
    """
    Fill null values in all columns of the DataFrame.

    Args:
        df: The pandas DataFrame to modify
        drop_threshold: Columns with more nulls than this ratio will be skipped with a warning
        methods: Dictionary mapping column names to imputation methods
        inplace: Whether to modify the DataFrame in place
        verbosity: Verbosity level (0=minimal, 1=normal, 2=verbose)

    Returns:
        Modified DataFrame if inplace=False, None otherwise

    Examples:
        >>> import pandas as pd
        >>> from sheryanalysis import analyze
        >>> df = pd.read_csv("data.csv")
        >>> # Fill all nulls using automatically selected methods
        >>> analyze.fill_nulls_all(df)
        >>> # Fill nulls with specific methods for some columns
        >>> methods = {'age': 'median', 'category': 'mode', 'status': 'constant'}
        >>> analyze.fill_nulls_all(df, methods=methods)
    """
    imputer = Imputer(df, verbosity=verbosity)
    return imputer.fill_nulls_all(drop_threshold=drop_threshold, methods=methods, inplace=inplace)


def get_column_analysis(df: pd.DataFrame,
                       column: str,
                       verbosity: int = 1) -> Dict[str, Any]:
    """
    Get detailed analysis for a specific column.

    Args:
        df: The pandas DataFrame
        column: The column name to analyze
        verbosity: Verbosity level (0=minimal, 1=normal, 2=verbose)

    Returns:
        Dict containing detailed statistics for the column

    Examples:
        >>> import pandas as pd
        >>> from sheryanalysis import analyze
        >>> df = pd.read_csv("data.csv")
        >>> stats = analyze.get_column_analysis(df, 'age')
    """
    logger = get_logger(verbosity)

    if column not in df.columns:
        logger.error(f"Column '{column}' not found in DataFrame")
        return {}

    try:
        stats = get_column_stats(df, column)

        if verbosity >= 1:
            logger.info(f"\n📊 Column Analysis: {column}")
            logger.info("-" * 60)
            logger.info(f"Data Type: {stats['dtype']}")
            logger.info(f"Null Count: {stats['null_count']} ({stats['null_percentage']:.2f}%)")
            logger.info(f"Unique Values: {stats['unique_count']} ({stats['unique_percentage']:.2f}%)")

            if 'min' in stats:
                logger.info(f"Min: {stats['min']}")
                logger.info(f"Max: {stats['max']}")
                logger.info(f"Mean: {stats['mean']}")
                logger.info(f"Median: {stats['median']}")
                logger.info(f"Std Dev: {stats['std']}")
                logger.info(f"Skewness: {stats['skewness']}")

                if 'outlier_count' in stats:
                    logger.info(f"Outliers: {stats['outlier_count']} ({stats['outlier_percentage']:.2f}%)")

            if 'top_values' in stats:
                logger.info("\nTop Values:")
                for val, count in stats['top_values'].items():
                    logger.info(f"  {val}: {count}")

        return stats

    except Exception as e:
        logger.error(f"Error analyzing column '{column}': {str(e)}")
        return {"error": str(e)}


# Attach functions to analyze
analyze.value_count = value_count
analyze.value_count_category = value_count_category
analyze.fill_nulls = fill_nulls
analyze.fill_nulls_all = fill_nulls_all
analyze.get_column_analysis = get_column_analysis

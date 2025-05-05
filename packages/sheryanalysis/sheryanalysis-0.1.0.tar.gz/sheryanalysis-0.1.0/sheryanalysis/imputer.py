"""
Imputation module for sheryanalysis.
Provides methods for handling missing values in DataFrames.
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union, Any, Callable
from sklearn.impute import KNNImputer, SimpleImputer
from .logger import get_logger
from .utils import suggest_imputation_method

class Imputer:
    """
    Class for handling missing values in DataFrames with various strategies.
    
    Attributes:
        logger: The logger instance
        df: The pandas DataFrame to work with
        verbosity: Verbosity level for logging
    """
    
    def __init__(self, df: pd.DataFrame, verbosity: int = 1):
        """
        Initialize the Imputer with a DataFrame.
        
        Args:
            df: The pandas DataFrame to work with
            verbosity: Verbosity level for logging (0=minimal, 1=normal, 2=verbose)
        """
        self.logger = get_logger(verbosity)
        self.df = df.copy()
        self.verbosity = verbosity
        
    def fill_nulls(self, column: str, 
                  method: Optional[str] = None, 
                  value: Optional[Any] = None, 
                  inplace: bool = True) -> Optional[pd.DataFrame]:
        """
        Fill null values in a specific column.
        
        Args:
            column: The column name to fill nulls in
            method: The imputation method ('mean', 'median', 'mode', 'constant', 'knn', 'regression')
                   If None, an appropriate method will be suggested based on the data
            value: The value to use for imputation (only used with 'constant' method)
            inplace: Whether to modify the DataFrame in place
            
        Returns:
            Modified DataFrame if inplace=False, None otherwise
        """
        # Check if column exists
        if column not in self.df.columns:
            self.logger.error(f"Column '{column}' not found in DataFrame")
            return self.df.copy() if not inplace else None
        
        # Check if there are nulls to fill
        null_count = self.df[column].isnull().sum()
        if null_count == 0:
            self.logger.info(f"No nulls in column '{column}'")
            return self.df.copy() if not inplace else None
        
        # Get working dataframe
        df_work = self.df if inplace else self.df.copy()
        
        # If method not specified, suggest one
        if method is None:
            method, suggested_value = suggest_imputation_method(df_work, column)
            if method == "none":
                return df_work if not inplace else None
            
            if value is None:
                value = suggested_value
                
            self.logger.info(f"Suggested imputation method for '{column}': {method.upper()} = {value}")
        
        # Apply the imputation method
        try:
            if method.lower() == 'mean':
                df_work[column].fillna(df_work[column].mean(), inplace=True)
                self.logger.info(f"Filled nulls in '{column}' using MEAN = {df_work[column].mean()}")
                
            elif method.lower() == 'median':
                df_work[column].fillna(df_work[column].median(), inplace=True)
                self.logger.info(f"Filled nulls in '{column}' using MEDIAN = {df_work[column].median()}")
                
            elif method.lower() == 'mode':
                mode_value = df_work[column].mode().iloc[0] if not df_work[column].mode().empty else np.nan
                df_work[column].fillna(mode_value, inplace=True)
                self.logger.info(f"Filled nulls in '{column}' using MODE = {mode_value}")
                
            elif method.lower() == 'constant':
                if value is None:
                    raise ValueError("Value must be provided for 'constant' method")
                df_work[column].fillna(value, inplace=True)
                self.logger.info(f"Filled nulls in '{column}' using CONSTANT = {value}")
                
            elif method.lower() == 'knn':
                self._fill_with_knn(df_work, column)
                self.logger.info(f"Filled nulls in '{column}' using KNN imputation")
                
            elif method.lower() == 'regression':
                self._fill_with_regression(df_work, column)
                self.logger.info(f"Filled nulls in '{column}' using regression imputation")
                
            else:
                raise ValueError(f"Unknown imputation method: {method}")
                
        except Exception as e:
            self.logger.error(f"Error filling nulls in '{column}': {str(e)}")
            if not inplace:
                return self.df.copy()
        
        return df_work if not inplace else None
    
    def fill_nulls_all(self, 
                      drop_threshold: float = 0.2, 
                      methods: Optional[Dict[str, str]] = None,
                      inplace: bool = True) -> Optional[pd.DataFrame]:
        """
        Fill null values in all columns of the DataFrame.
        
        Args:
            drop_threshold: Columns with more nulls than this ratio will be skipped with a warning
            methods: Dictionary mapping column names to imputation methods
            inplace: Whether to modify the DataFrame in place
            
        Returns:
            Modified DataFrame if inplace=False, None otherwise
        """
        # Get working dataframe
        df_work = self.df if inplace else self.df.copy()
        
        # Get columns with nulls
        total_rows = len(df_work)
        nulls = df_work.isnull().sum()
        cols_with_nulls = nulls[nulls > 0].index.tolist()
        
        if not cols_with_nulls:
            self.logger.info("No null values found in DataFrame")
            return df_work if not inplace else None
        
        self.logger.info(f"Filling nulls in {len(cols_with_nulls)} columns")
        
        # Process each column
        for column in cols_with_nulls:
            missing_ratio = nulls[column] / total_rows
            
            # Skip columns with too many nulls
            if missing_ratio > drop_threshold:
                self.logger.warning(f"Column '{column}' has {missing_ratio:.2%} missing values. Consider dropping it.")
                continue
            
            # Get method for this column
            method = None if methods is None else methods.get(column)
            
            # Fill nulls in this column
            self.fill_nulls(column, method=method, inplace=True)
        
        return df_work if not inplace else None
    
    def _fill_with_knn(self, df: pd.DataFrame, target_column: str, n_neighbors: int = 5) -> None:
        """
        Fill nulls using KNN imputation.
        
        Args:
            df: The DataFrame to modify
            target_column: The column to impute
            n_neighbors: Number of neighbors to use for KNN
        """
        try:
            # Select only numeric columns for KNN
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if target_column not in numeric_cols:
                self.logger.warning(f"KNN imputation only works with numeric columns. '{target_column}' is not numeric.")
                # Fallback to simpler method
                method, value = suggest_imputation_method(df, target_column)
                df[target_column].fillna(value, inplace=True)
                return
            
            # Remove columns with all nulls
            numeric_cols = [col for col in numeric_cols if not df[col].isnull().all()]
            
            if len(numeric_cols) < 2:
                self.logger.warning("Not enough numeric columns for KNN imputation. Falling back to simpler method.")
                method, value = suggest_imputation_method(df, target_column)
                df[target_column].fillna(value, inplace=True)
                return
            
            # Create a subset with only numeric columns
            df_numeric = df[numeric_cols].copy()
            
            # Initialize and fit the KNN imputer
            imputer = KNNImputer(n_neighbors=n_neighbors)
            imputed_values = imputer.fit_transform(df_numeric)
            
            # Create a DataFrame with the imputed values
            imputed_df = pd.DataFrame(imputed_values, columns=numeric_cols, index=df.index)
            
            # Update only the target column
            df[target_column] = imputed_df[target_column]
            
        except Exception as e:
            self.logger.error(f"Error in KNN imputation: {str(e)}")
            self.logger.info("Falling back to simpler imputation method")
            method, value = suggest_imputation_method(df, target_column)
            df[target_column].fillna(value, inplace=True)
    
    def _fill_with_regression(self, df: pd.DataFrame, target_column: str) -> None:
        """
        Fill nulls using regression imputation.
        
        Args:
            df: The DataFrame to modify
            target_column: The column to impute
        """
        try:
            from sklearn.linear_model import LinearRegression
            
            # Select only numeric columns for regression
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if target_column not in numeric_cols:
                self.logger.warning(f"Regression imputation only works with numeric columns. '{target_column}' is not numeric.")
                # Fallback to simpler method
                method, value = suggest_imputation_method(df, target_column)
                df[target_column].fillna(value, inplace=True)
                return
            
            # Remove the target column from predictors
            predictor_cols = [col for col in numeric_cols if col != target_column]
            
            # Remove columns with all nulls
            predictor_cols = [col for col in predictor_cols if not df[col].isnull().all()]
            
            if len(predictor_cols) < 1:
                self.logger.warning("Not enough numeric columns for regression imputation. Falling back to simpler method.")
                method, value = suggest_imputation_method(df, target_column)
                df[target_column].fillna(value, inplace=True)
                return
            
            # Split data into rows with and without nulls in target column
            df_train = df.loc[df[target_column].notnull(), predictor_cols + [target_column]]
            df_predict = df.loc[df[target_column].isnull(), predictor_cols]
            
            if len(df_train) < 10:
                self.logger.warning("Not enough training data for regression imputation. Falling back to simpler method.")
                method, value = suggest_imputation_method(df, target_column)
                df[target_column].fillna(value, inplace=True)
                return
            
            # Handle nulls in predictor columns for both training and prediction sets
            for col in predictor_cols:
                if df_train[col].isnull().any() or df_predict[col].isnull().any():
                    # Use median for simplicity
                    median_val = df[col].median()
                    df_train[col].fillna(median_val, inplace=True)
                    df_predict[col].fillna(median_val, inplace=True)
            
            # Train regression model
            X_train = df_train[predictor_cols]
            y_train = df_train[target_column]
            
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            # Predict missing values
            if not df_predict.empty:
                X_predict = df_predict[predictor_cols]
                predictions = model.predict(X_predict)
                
                # Update the original dataframe with predictions
                df.loc[df[target_column].isnull(), target_column] = predictions
            
        except Exception as e:
            self.logger.error(f"Error in regression imputation: {str(e)}")
            self.logger.info("Falling back to simpler imputation method")
            method, value = suggest_imputation_method(df, target_column)
            df[target_column].fillna(value, inplace=True)

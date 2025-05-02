"""
Missing value handler module for handling missing values in data.
"""

import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer, KNNImputer
from cleanfusion.utils.logger import Logger

class MissingValueHandler:
    """
    Class for handling missing values in data.
    
    Features:
    - Multiple strategies for numerical data: mean, median, mode, constant, KNN
    - Multiple strategies for categorical data: most_frequent, constant
    - Specialized handling for time series data
    """
    
    def __init__(self):
        """Initialize the MissingValueHandler."""
        self.logger = Logger()
        self._numerical_imputers = {}
        self._categorical_imputers = {}
    
    def handle_numerical_missing(self, series, method='mean', fill_value=0):
        """
        Handle missing values in numerical data.
        
        Parameters
        ----------
        series : pandas.Series
            The numerical series with missing values.
        
        method : str, default='mean'
            Method to use for imputation: 'mean', 'median', 'mode', 'constant', 'knn'
        
        fill_value : float, default=0
            Value to use when method='constant'
        
        Returns
        -------
        pandas.Series
            The series with imputed values.
        """
        if series.name not in self._numerical_imputers:
            if method == 'mean':
                imputer = SimpleImputer(strategy='mean')
            elif method == 'median':
                imputer = SimpleImputer(strategy='median')
            elif method == 'mode':
                imputer = SimpleImputer(strategy='most_frequent')
            elif method == 'constant':
                imputer = SimpleImputer(strategy='constant', fill_value=fill_value)
            elif method == 'knn':
                try:
                    imputer = KNNImputer(n_neighbors=5)
                except Exception as e:
                    self.logger.warning(f"KNN imputation failed: {e}. Falling back to median.")
                    imputer = SimpleImputer(strategy='median')
            else:
                self.logger.warning(f"Unknown method: {method}. Using mean instead.")
                imputer = SimpleImputer(strategy='mean')
            
            # Reshape for sklearn imputers
            values = series.values.reshape(-1, 1)
            imputer.fit(values)
            self._numerical_imputers[series.name] = imputer
        else:
            imputer = self._numerical_imputers[series.name]
        
        # Get masks for tracking
        missing_mask = series.isna()
        num_missing = missing_mask.sum()
        
        if num_missing > 0:
            # Perform imputation
            values = series.values.reshape(-1, 1)
            imputed_values = imputer.transform(values).flatten()
            
            self.logger.info(f"Imputed {num_missing} missing values in column '{series.name}' using {method} method")
            return pd.Series(imputed_values, index=series.index, name=series.name)
        
        return series
    
    def handle_categorical_missing(self, series, method='most_frequent', fill_value='unknown'):
        """
        Handle missing values in categorical data.
        
        Parameters
        ----------
        series : pandas.Series
            The categorical series with missing values.
        
        method : str, default='most_frequent'
            Method to use for imputation: 'most_frequent', 'constant'
        
        fill_value : str, default='unknown'
            Value to use when method='constant'
        
        Returns
        -------
        pandas.Series
            The series with imputed values.
        """
        if series.name not in self._categorical_imputers:
            if method == 'most_frequent':
                imputer = SimpleImputer(strategy='most_frequent')
            elif method == 'constant':
                imputer = SimpleImputer(strategy='constant', fill_value=fill_value)
            else:
                self.logger.warning(f"Unknown method: {method}. Using most_frequent instead.")
                imputer = SimpleImputer(strategy='most_frequent')
            
            # Reshape for sklearn imputers
            values = series.astype(str).values.reshape(-1, 1)
            imputer.fit(values)
            self._categorical_imputers[series.name] = imputer
        else:
            imputer = self._categorical_imputers[series.name]
        
        # Get masks for tracking
        missing_mask = series.isna() 
        num_missing = missing_mask.sum()
        
        if num_missing > 0:
            # Perform imputation
            values = series.astype(str).values.reshape(-1, 1)
            imputed_values = imputer.transform(values).flatten()
            
            self.logger.info(f"Imputed {num_missing} missing values in column '{series.name}' using {method} method")
            return pd.Series(imputed_values, index=series.index, name=series.name)
        
        return series
    
    def drop_missing(self, df, threshold=0.5, columns=None):
        """
        Drop rows or columns with too many missing values.
        
        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame to process.
        
        threshold : float, default=0.5
            The threshold of missing values ratio above which to drop.
        
        columns : list, default=None
            Specific columns to check. If None, check all columns.
        
        Returns
        -------
        pandas.DataFrame
            The DataFrame with rows/columns dropped.
        """
        original_shape = df.shape
        
        if columns is None:
            columns = df.columns
        
        # Calculate missing ratio for each column
        missing_ratio = df[columns].isna().mean()
        cols_to_drop = missing_ratio[missing_ratio > threshold].index.tolist()
        
        if cols_to_drop:
            self.logger.info(f"Dropping {len(cols_to_drop)} columns with over {threshold*100}% missing values")
            df = df.drop(columns=cols_to_drop)
        
        # Drop rows with too many missing values
        rows_before = len(df)
        df = df.dropna(thresh=int((1-threshold) * len(df.columns)))
        rows_dropped = rows_before - len(df)
        
        if rows_dropped > 0:
            self.logger.info(f"Dropped {rows_dropped} rows with over {threshold*100}% missing values")
        
        self.logger.info(f"Original shape: {original_shape}, New shape: {df.shape}")
        return df
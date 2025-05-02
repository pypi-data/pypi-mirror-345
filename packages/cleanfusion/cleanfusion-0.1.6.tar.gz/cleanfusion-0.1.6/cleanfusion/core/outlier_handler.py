"""
Outlier handler module for detecting and handling outliers in data.
"""

import pandas as pd
import numpy as np
from scipy import stats
from cleanfusion.utils.logger import Logger

class OutlierHandler:
    """
    Class for detecting and handling outliers in data.
    
    Features:
    - Z-score based outlier detection
    - IQR (Interquartile Range) based outlier detection
    - Multiple handling strategies: clip, remove, impute
    """
    
    def __init__(self, data=None):
        """
        Initialize the OutlierHandler.
        
        Parameters
        ----------
        data : pandas.DataFrame, default=None
            The DataFrame to analyze for outliers.
        """
        self.data = data.copy() if data is not None else None
        self.logger = Logger()
        self.outlier_indices = {}
    
    def detect_outliers_zscore(self, column, threshold=3.0):
        """
        Detect outliers in a column using Z-score method.
        
        Parameters
        ----------
        column : str
            The column name to check for outliers.
        
        threshold : float, default=3.0
            Z-score threshold above which values are considered outliers.
        
        Returns
        -------
        pandas.Series
            Boolean series with True for outliers.
        """
        if self.data is None:
            raise ValueError("No data provided. Set data in constructor or use detect_outliers_zscore_series.")
        
        series = self.data[column]
        return self.detect_outliers_zscore_series(series, threshold)
    
    def detect_outliers_zscore_series(self, series, threshold=3.0):
        """
        Detect outliers in a series using Z-score method.
        
        Parameters
        ----------
        series : pandas.Series
            The series to check for outliers.
        
        threshold : float, default=3.0
            Z-score threshold above which values are considered outliers.
        
        Returns
        -------
        pandas.Series
            Boolean series with True for outliers.
        """
        z_scores = np.abs(stats.zscore(series.dropna()))
        # Create a boolean series with the same index as the original
        outlier_mask = pd.Series(False, index=series.index)
        # Mark outliers where z-score exceeds threshold
        outlier_mask.loc[series.dropna().index] = z_scores > threshold
        
        num_outliers = outlier_mask.sum()
        if num_outliers > 0:
            self.logger.info(f"Detected {num_outliers} outliers in column '{series.name}' using Z-score method")
            if series.name:
                self.outlier_indices[series.name] = outlier_mask
        
        return outlier_mask
    
    def detect_outliers_iqr(self, column, multiplier=1.5):
        """
        Detect outliers in a column using IQR method.
        
        Parameters
        ----------
        column : str
            The column name to check for outliers.
        
        multiplier : float, default=1.5
            The multiplier for IQR to determine outlier boundaries.
        
        Returns
        -------
        pandas.Series
            Boolean series with True for outliers.
        """
        if self.data is None:
            raise ValueError("No data provided. Set data in constructor or use detect_outliers_iqr_series.")
        
        series = self.data[column]
        return self.detect_outliers_iqr_series(series, multiplier)
    
    def detect_outliers_iqr_series(self, series, multiplier=1.5):
        """
        Detect outliers in a series using IQR method.
        
        Parameters
        ----------
        series : pandas.Series
            The series to check for outliers.
        
        multiplier : float, default=1.5
            The multiplier for IQR to determine outlier boundaries.
        
        Returns
        -------
        pandas.Series
            Boolean series with True for outliers.
        """
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outlier_mask = (series < lower_bound) | (series > upper_bound)
        
        num_outliers = outlier_mask.sum()
        if num_outliers > 0:
            self.logger.info(f"Detected {num_outliers} outliers in column '{series.name}' using IQR method")
            if series.name:
                self.outlier_indices[series.name] = outlier_mask
        
        return outlier_mask
    
    def handle_outliers_zscore(self, column, threshold=3.0, method='clip'):
        """
        Handle outliers in a column using Z-score method.
        
        Parameters
        ----------
        column : str
            The column name to handle outliers for.
        
        threshold : float, default=3.0
            Z-score threshold above which values are considered outliers.
        
        method : str, default='clip'
            Method to handle outliers: 'clip', 'remove', or 'impute'.
        
        Returns
        -------
        pandas.DataFrame
            The DataFrame with handled outliers.
        """
        outlier_mask = self.detect_outliers_zscore(column, threshold)
        return self._handle_outliers(column, outlier_mask, method)
    
    def handle_outliers_iqr(self, column, multiplier=1.5, method='clip'):
        """
        Handle outliers in a column using IQR method.
        
        Parameters
        ----------
        column : str
            The column name to handle outliers for.
        
        multiplier : float, default=1.5
            The multiplier for IQR to determine outlier boundaries.
        
        method : str, default='clip'
            Method to handle outliers: 'clip', 'remove', or 'impute'.
        
        Returns
        -------
        pandas.DataFrame
            The DataFrame with handled outliers.
        """
        outlier_mask = self.detect_outliers_iqr(column, multiplier)
        return self._handle_outliers(column, outlier_mask, method)
    
    def _handle_outliers(self, column, outlier_mask, method):
        """
        Internal method to handle outliers based on a mask.
        
        Parameters
        ----------
        column : str
            The column name to handle outliers for.
        
        outlier_mask : pandas.Series
            Boolean series with True for outliers.
        
        method : str
            Method to handle outliers: 'clip', 'remove', or 'impute'.
        
        Returns
        -------
        pandas.DataFrame
            The DataFrame with handled outliers.
        """
        if not outlier_mask.any():
            return self.data
        
        data_copy = self.data.copy()
        
        if method == 'remove':
            # Remove rows with outliers
            data_copy = data_copy[~outlier_mask]
            self.logger.info(f"Removed {outlier_mask.sum()} outliers from column '{column}'")
            
        elif method == 'clip':
            # Clip outliers to the acceptable range
            series = data_copy[column]
            
            # Get the acceptable range
            if column in self.outlier_indices:
                non_outlier_values = series[~outlier_mask]
                if len(non_outlier_values) > 0:
                    lower_bound = non_outlier_values.min()
                    upper_bound = non_outlier_values.max()
                    
                    # Clip the values
                    data_copy.loc[outlier_mask, column] = series[outlier_mask].clip(lower_bound, upper_bound)
                    self.logger.info(f"Clipped {outlier_mask.sum()} outliers in column '{column}'")
            
        elif method == 'impute':
            # Impute outliers with median of non-outliers
            series = data_copy[column]
            non_outlier_values = series[~outlier_mask]
            
            if len(non_outlier_values) > 0:
                median_value = non_outlier_values.median()
                data_copy.loc[outlier_mask, column] = median_value
                self.logger.info(f"Imputed {outlier_mask.sum()} outliers in column '{column}' with median value {median_value}")
        
        else:
            self.logger.warning(f"Unknown method: {method}. No action taken.")
        
        return data_copy
    
    def get_outlier_summary(self):
        """
        Get a summary of detected outliers.
        
        Returns
        -------
        dict
            Dictionary with column names as keys and outlier counts as values.
        """
        summary = {}
        
        for column, mask in self.outlier_indices.items():
            summary[column] = {
                'count': mask.sum(),
                'percentage': 100 * mask.sum() / len(mask) if len(mask) > 0 else 0
            }
        
        return summary
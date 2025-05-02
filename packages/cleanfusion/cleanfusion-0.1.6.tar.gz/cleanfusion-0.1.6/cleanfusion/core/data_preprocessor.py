"""
Data preprocessor module for handling various data cleaning tasks.
"""

import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.base import BaseEstimator, TransformerMixin
import os

from cleanfusion.core.missing_value_handler import MissingValueHandler
from cleanfusion.core.outlier_handler import OutlierHandler
from cleanfusion.text.text_cleaner import TextCleaner
from cleanfusion.text.text_vectorizer import TextVectorizer
from cleanfusion.utils.logger import Logger
from cleanfusion.file_handlers.csv_handler import CSVHandler
from cleanfusion.file_handlers.txt_handler import TXTHandler
from cleanfusion.file_handlers.docx_handler import DOCXHandler
from cleanfusion.file_handlers.pdf_handler import PDFHandler


class DataPreprocessor(BaseEstimator, TransformerMixin):
    """
    A comprehensive data preprocessing class that handles various data cleaning tasks.
    
    This class provides a unified interface for handling missing values, outliers,
    text preprocessing, and more.
    
    Parameters
    ----------
    numerical_strategy : str, default='mean'
        Strategy for handling missing values in numerical columns.
        Options: 'mean', 'median', 'knn'
    
    categorical_strategy : str, default='most_frequent'
        Strategy for handling missing values in categorical columns.
        Options: 'most_frequent', 'constant'
    
    outlier_threshold : float, default=3.0
        Threshold for z-score based outlier detection.
    
    text_vectorizer : str, default='tfidf'
        Method for vectorizing text data.
        Options: 'tfidf', 'count', 'bert'
    """
    
    def __init__(self, numerical_strategy='mean', categorical_strategy='most_frequent', 
                 outlier_threshold=3, text_vectorizer='tfidf'):
        self.numerical_strategy = numerical_strategy
        self.categorical_strategy = categorical_strategy
        self.outlier_threshold = outlier_threshold
        self.text_vectorizer = text_vectorizer
        self.logger = Logger()
        
        # Initialize handlers
        self.missing_handler = MissingValueHandler()
        self.text_cleaner = TextCleaner()
        self.text_vectorizer = TextVectorizer()
        
    def fit(self, X, y=None):
        """
        Fit the preprocessor to the data.
        
        Parameters
        ----------
        X : pandas.DataFrame
            The input data to be transformed.
        
        y : array-like, default=None
            Target values (ignored).
        
        Returns
        -------
        self : object
            Returns self.
        """
        return self
    
    def transform(self, X):
        """
        Transform the data.
        
        Parameters
        ----------
        X : pandas.DataFrame
            The input data to be transformed.
        
        Returns
        -------
        X_transformed : pandas.DataFrame
            The transformed data.
        """
        self.logger.info("Starting data preprocessing...")
        
        # Create a copy to avoid modifying the original DataFrame
        X_transformed = X.copy()
        
        # Handle missing values
        X_transformed = self._handle_missing_values(X_transformed)
        
        # Handle outliers
        X_transformed = self._handle_outliers(X_transformed)
        
        # Handle text preprocessing
        X_transformed = self._preprocess_text(X_transformed)
        
        self.logger.info("Data preprocessing completed successfully.")
        return X_transformed
    
    def _handle_missing_values(self, df):
        """Handle missing values in the DataFrame."""
        self.logger.info("Handling missing values...")
        
        # Separate numerical and categorical columns
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        # Handle numerical missing values
        for col in numerical_cols:
            if df[col].isnull().sum() > 0:
                df[col] = self.missing_handler.handle_numerical_missing(df[col], method=self.numerical_strategy)
        
        # Handle categorical missing values
        for col in categorical_cols:
            if df[col].isnull().sum() > 0:
                df[col] = self.missing_handler.handle_categorical_missing(df[col])
        
        return df
    
    def _handle_outliers(self, df):
        """Handle outliers in the DataFrame."""
        self.logger.info("Handling outliers...")
        
        outlier_handler = OutlierHandler(df)
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
        
        for col in numerical_cols:
            outlier_handler.handle_outliers_iqr(col)
        
        return outlier_handler.data  # Return the DataFrame with handled outliers
    
    def _preprocess_text(self, df):
        """Preprocess text columns in the DataFrame."""
        # Identify text columns (simple heuristic: object columns with high uniqueness and length)
        text_columns = []
        for col in df.select_dtypes(include=['object']).columns:
            # Skip if column has too few values
            if len(df[col].dropna()) < 5:
                continue
            
            # Check if it's likely a text column (based on average length and uniqueness)
            avg_length = df[col].astype(str).apply(len).mean()
            uniqueness_ratio = df[col].nunique() / len(df[col].dropna())
            
            if avg_length > 20 or uniqueness_ratio > 0.5:
                text_columns.append(col)
                self.logger.info(f"Column '{col}' identified as text data.")
        
        # Clean text columns
        for col in text_columns:
            df[col] = df[col].astype(str).apply(self.text_cleaner.clean_text)
            self.logger.info(f"Text preprocessing applied to column '{col}'.")
        
        return df
    
    def clean_file(self, file_path, output_path=None):
        """
        Clean a file based on its extension.
        
        Parameters
        ----------
        file_path : str
            Path to the input file.
        
        output_path : str, default=None
            Path to save the cleaned data. If None, a default path will be used.
        
        Returns
        -------
        result : object
            The cleaned data, format depends on the input file type.
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if not output_path:
            base_name = os.path.basename(file_path)
            base_name_no_ext = os.path.splitext(base_name)[0]
            output_path = f"cleaned_{base_name_no_ext}{file_ext}"
        
        self.logger.info(f"Processing file: {file_path}")
        
        # Handle different file types
        if file_ext == '.csv':
            handler = CSVHandler()
            df = handler.read_file(file_path)
            cleaned_df = self.transform(df)
            handler.write_file(cleaned_df, output_path)
            return cleaned_df
        
        elif file_ext == '.txt':
            handler = TXTHandler()
            text_data = handler.read_file(file_path)
            cleaned_text = self.text_cleaner.clean_text(text_data)
            handler.write_file(cleaned_text, output_path)
            return cleaned_text
        
        elif file_ext == '.docx':
            handler = DOCXHandler()
            text_data = handler.read_file(file_path)
            cleaned_text = self.text_cleaner.clean_text(text_data)
            handler.write_file(cleaned_text, output_path)
            return cleaned_text
        
        elif file_ext == '.pdf':
            handler = PDFHandler()
            text_data = handler.read_file(file_path)
            cleaned_text = self.text_cleaner.clean_text(text_data)
            handler.write_file(cleaned_text, output_path)
            return cleaned_text
        
        else:
            raise ValueError(f"Unsupported file extension: {file_ext}")
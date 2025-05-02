"""
Categorical encoder module for encoding categorical variables in data.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from cleanfusion.utils.logger import Logger

class CategoricalEncoder:
    """
    Class for encoding categorical variables in data.
    
    Features:
    - Label encoding (simple numerical mapping)
    - One-hot encoding (binary representation)
    - Ordinal encoding (with custom ordering)
    - Binary encoding (efficient alternative to one-hot)
    - Target encoding (using target variable)
    
    Parameters
    ----------
    method : str, default='label'
        Encoding method: 'label', 'onehot', 'ordinal', 'binary', or 'target'
    """
    
    def __init__(self, method='label'):
        """
        Initialize the CategoricalEncoder.
        
        Parameters
        ----------
        method : str, default='label'
            Encoding method: 'label', 'onehot', 'ordinal', 'binary', or 'target'
        """
        self.method = method
        self.logger = Logger()
        self.encoders = {}
        self.ordinal_mappings = {}
        self.target_mappings = {}
        
    def fit(self, df, columns=None, ordinal_mappings=None, target_column=None):
        """
        Fit the encoder to the data.
        
        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame containing categorical columns to encode
        columns : list, default=None
            List of columns to encode. If None, all object and category columns are used.
        ordinal_mappings : dict, default=None
            Dictionary mapping column names to ordered category lists for ordinal encoding.
            Example: {'size': ['small', 'medium', 'large']}
        target_column : str, default=None
            Target column name for target encoding
            
        Returns
        -------
        self : object
            Returns self.
        """
        # Determine columns to encode if not specified
        if columns is None:
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        self.logger.info(f"Fitting categorical encoder for {len(columns)} columns using {self.method} method")
        
        # Store ordinal mappings if provided
        if ordinal_mappings:
            self.ordinal_mappings = ordinal_mappings
            
        # Fit encoders based on the method
        if self.method == 'label':
            for col in columns:
                encoder = LabelEncoder()
                encoder.fit(df[col].astype(str).fillna('missing'))
                self.encoders[col] = encoder
                self.logger.info(f"Fitted label encoder for column '{col}' with {len(encoder.classes_)} classes")
                
        elif self.method == 'onehot':
            for col in columns:
                encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
                encoder.fit(df[[col]].astype(str).fillna('missing'))
                self.encoders[col] = encoder
                self.logger.info(f"Fitted one-hot encoder for column '{col}' with {len(encoder.categories_[0])} categories")
                
        elif self.method == 'ordinal':
            for col in columns:
                if col in self.ordinal_mappings:
                    # Use provided ordering
                    mapping = {category: i for i, category in enumerate(self.ordinal_mappings[col])}
                    self.encoders[col] = mapping
                    self.logger.info(f"Created ordinal mapping for column '{col}' with {len(mapping)} ordered categories")
                else:
                    # Default to label encoding if no mapping provided
                    encoder = LabelEncoder()
                    encoder.fit(df[col].astype(str).fillna('missing'))
                    self.encoders[col] = encoder
                    self.logger.info(f"No ordinal mapping provided for '{col}', using label encoder with {len(encoder.classes_)} classes")
                    
        elif self.method == 'binary':
            for col in columns:
                # For binary encoding, we just store unique values
                unique_values = df[col].astype(str).fillna('missing').unique()
                self.encoders[col] = {val: i for i, val in enumerate(unique_values)}
                self.logger.info(f"Created binary encoding mapping for column '{col}' with {len(unique_values)} categories")
                
        elif self.method == 'target':
            if target_column is None:
                raise ValueError("Target column must be specified for target encoding")
                
            for col in columns:
                if col != target_column:
                    # Calculate mean target value for each category
                    target_means = df.groupby(col)[target_column].mean().to_dict()
                    self.target_mappings[col] = target_means
                    self.logger.info(f"Created target encoding mapping for column '{col}' with {len(target_means)} categories")
        
        return self
    
    def transform(self, df, drop_original=True):
        """
        Transform categorical columns in the DataFrame.
        
        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame to transform
        drop_original : bool, default=True
            Whether to drop the original columns after encoding
            
        Returns
        -------
        pandas.DataFrame
            The transformed DataFrame
        """
        if not self.encoders and self.method != 'target':
            self.logger.warning("No encoders fitted. Call fit() first.")
            return df
            
        if self.method == 'target' and not self.target_mappings:
            self.logger.warning("No target mappings fitted. Call fit() first.")
            return df
            
        result_df = df.copy()
        
        self.logger.info(f"Transforming categorical columns using {self.method} encoding")
        
        if self.method == 'label':
            for col, encoder in self.encoders.items():
                if col in result_df.columns:
                    # Transform column
                    result_df[f"{col}_encoded"] = encoder.transform(result_df[col].astype(str).fillna('missing'))
                    self.logger.info(f"Transformed column '{col}' using label encoding")
                    
                    # Drop original if requested
                    if drop_original:
                        result_df = result_df.drop(columns=[col])
                        
        elif self.method == 'onehot':
            for col, encoder in self.encoders.items():
                if col in result_df.columns:
                    # Transform column
                    encoded = encoder.transform(result_df[[col]].astype(str).fillna('missing'))
                    
                    # Create new columns with proper names
                    feature_names = [f"{col}_{cat}" for cat in encoder.categories_[0]]
                    encoded_df = pd.DataFrame(encoded, columns=feature_names, index=result_df.index)
                    
                    # Add encoded columns to result
                    result_df = pd.concat([result_df, encoded_df], axis=1)
                    self.logger.info(f"Transformed column '{col}' using one-hot encoding into {len(feature_names)} columns")
                    
                    # Drop original if requested
                    if drop_original:
                        result_df = result_df.drop(columns=[col])
                        
        elif self.method == 'ordinal':
            for col, encoder in self.encoders.items():
                if col in result_df.columns:
                    if isinstance(encoder, dict):
                        # Use mapping dictionary for ordinal encoding
                        result_df[f"{col}_encoded"] = result_df[col].map(encoder)
                        # Fill missing values with -1 or the next available number
                        if result_df[f"{col}_encoded"].isna().any():
                            next_val = max(encoder.values()) + 1 if encoder else 0
                            result_df[f"{col}_encoded"] = result_df[f"{col}_encoded"].fillna(next_val)
                    else:
                        # Use label encoder
                        result_df[f"{col}_encoded"] = encoder.transform(result_df[col].astype(str).fillna('missing'))
                        
                    self.logger.info(f"Transformed column '{col}' using ordinal encoding")
                    
                    # Drop original if requested
                    if drop_original:
                        result_df = result_df.drop(columns=[col])
                        
        elif self.method == 'binary':
            for col, mapping in self.encoders.items():
                if col in result_df.columns:
                    # Get integer codes
                    result_df[f"{col}_code"] = result_df[col].map(mapping)
                    
                    # Convert to binary representation
                    max_val = max(mapping.values())
                    num_bits = int(np.log2(max_val)) + 1
                    
                    # Create binary columns
                    for bit in range(num_bits):
                        result_df[f"{col}_bit{bit}"] = ((result_df[f"{col}_code"] >> bit) & 1).astype(int)
                    
                    self.logger.info(f"Transformed column '{col}' using binary encoding into {num_bits} columns")
                    
                    # Drop intermediate and original columns
                    result_df = result_df.drop(columns=[f"{col}_code"])
                    if drop_original:
                        result_df = result_df.drop(columns=[col])
                        
        elif self.method == 'target':
            for col, mapping in self.target_mappings.items():
                if col in result_df.columns:
                    # Map categories to target means
                    result_df[f"{col}_target_encoded"] = result_df[col].map(mapping)
                    
                    # Handle missing values
                    global_mean = np.mean(list(mapping.values()))
                    result_df[f"{col}_target_encoded"] = result_df[f"{col}_target_encoded"].fillna(global_mean)
                    
                    self.logger.info(f"Transformed column '{col}' using target encoding")
                    
                    # Drop original if requested
                    if drop_original:
                        result_df = result_df.drop(columns=[col])
        
        return result_df
    
    def fit_transform(self, df, columns=None, ordinal_mappings=None, target_column=None, drop_original=True):
        """
        Fit the encoder and transform the data in one step.
        
        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame to transform
        columns : list, default=None
            List of columns to encode. If None, all object and category columns are used.
        ordinal_mappings : dict, default=None
            Dictionary mapping column names to ordered category lists for ordinal encoding
        target_column : str, default=None
            Target column name for target encoding
        drop_original : bool, default=True
            Whether to drop the original columns after encoding
            
        Returns
        -------
        pandas.DataFrame
            The transformed DataFrame
        """
        self.fit(df, columns, ordinal_mappings, target_column)
        return self.transform(df, drop_original)
    
    def encode_with_custom_order(self, df, column, ordered_categories, drop_original=True):
        """
        Encode a single column with a custom ordering.
        
        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame containing the column to encode
        column : str
            The column name to encode
        ordered_categories : list
            List of categories in the desired order
        drop_original : bool, default=True
            Whether to drop the original column after encoding
            
        Returns
        -------
        pandas.DataFrame
            The DataFrame with the encoded column
        """
        result_df = df.copy()
        
        # Create mapping from categories to ordinal values
        mapping = {category: i for i, category in enumerate(ordered_categories)}
        
        # Apply mapping
        result_df[f"{column}_encoded"] = result_df[column].map(mapping)
        
        # Handle values not in the mapping
        if result_df[f"{column}_encoded"].isna().any():
            next_val = len(ordered_categories)
            missing_categories = result_df[result_df[f"{column}_encoded"].isna()][column].unique()
            self.logger.warning(f"Found {len(missing_categories)} categories in column '{column}' not in the provided ordering")
            
            # Assign new values to missing categories
            for cat in missing_categories:
                if pd.notna(cat):
                    mapping[cat] = next_val
                    next_val += 1
            
            # Apply updated mapping
            result_df[f"{column}_encoded"] = result_df[column].map(mapping)
            
            # Still handle any NaN values
            result_df[f"{column}_encoded"] = result_df[f"{column}_encoded"].fillna(-1)
        
        self.logger.info(f"Encoded column '{column}' with custom ordering")
        
        # Drop original if requested
        if drop_original:
            result_df = result_df.drop(columns=[column])
            
        return result_df
    
    def get_mapping(self, column):
        """
        Get the mapping for a specific column.
        
        Parameters
        ----------
        column : str
            The column name
            
        Returns
        -------
        dict or list
            The mapping used for encoding the column
        """
        if self.method == 'label' or (self.method == 'ordinal' and not isinstance(self.encoders.get(column), dict)):
            if column in self.encoders:
                classes = self.encoders[column].classes_
                return {cls: idx for idx, cls in enumerate(classes)}
        elif self.method == 'onehot':
            if column in self.encoders:
                categories = self.encoders[column].categories_[0]
                return {cat: i for i, cat in enumerate(categories)}
        elif self.method == 'ordinal' and isinstance(self.encoders.get(column), dict):
            return self.encoders[column]
        elif self.method == 'binary':
            return self.encoders.get(column)
        elif self.method == 'target':
            return self.target_mappings.get(column)
            
        return None

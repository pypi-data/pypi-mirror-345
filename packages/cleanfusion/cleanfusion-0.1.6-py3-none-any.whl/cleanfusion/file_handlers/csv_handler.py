"""
CSV file handler module for reading and writing CSV files.
"""

import pandas as pd
from cleanfusion.utils.logger import Logger

class CSVHandler:
    """
    Handler for CSV files.
    """
    
    def __init__(self):
        """Initialize the CSV handler."""
        self.logger = Logger()
    
    def read_file(self, file_path, **kwargs):
        """
        Read a CSV file into a pandas DataFrame.
        
        Parameters
        ----------
        file_path : str
            Path to the CSV file.
        
        **kwargs : dict
            Additional arguments to pass to pandas.read_csv.
        
        Returns
        -------
        pandas.DataFrame
            The data from the CSV file.
        """
        try:
            self.logger.info(f"Reading CSV file: {file_path}")
            df = pd.read_csv(file_path, **kwargs)
            self.logger.info(f"Successfully read CSV with shape: {df.shape}")
            return df
        except Exception as e:
            self.logger.error(f"Error reading CSV file: {e}")
            raise
    
    def write_file(self, df, file_path, **kwargs):
        """
        Write a pandas DataFrame to a CSV file.
        
        Parameters
        ----------
        df : pandas.DataFrame
            The DataFrame to write.
        
        file_path : str
            Path to the output CSV file.
        
        **kwargs : dict
            Additional arguments to pass to pandas.DataFrame.to_csv.
        
        Returns
        -------
        str
            The path to the written file.
        """
        try:
            self.logger.info(f"Writing CSV file: {file_path}")
            df.to_csv(file_path, index=False, **kwargs)
            self.logger.info(f"Successfully wrote DataFrame with shape {df.shape} to CSV")
            return file_path
        except Exception as e:
            self.logger.error(f"Error writing CSV file: {e}")
            raise
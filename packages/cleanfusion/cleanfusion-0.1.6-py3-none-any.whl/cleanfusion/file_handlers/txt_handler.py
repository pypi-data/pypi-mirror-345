"""
TXT file handler module for reading and writing text files.
"""

import os
from cleanfusion.utils.logger import Logger

class TXTHandler:
    """
    Handler for plain text files.
    """
    
    def __init__(self):
        """Initialize the TXT handler."""
        self.logger = Logger()
    
    def read_file(self, file_path, encoding='utf-8'):
        """
        Read a text file.
        
        Parameters
        ----------
        file_path : str
            Path to the text file.
        
        encoding : str, default='utf-8'
            The encoding of the text file.
        
        Returns
        -------
        str
            The content of the text file.
        """
        try:
            self.logger.info(f"Reading text file: {file_path}")
            with open(file_path, 'r', encoding=encoding) as file:
                text = file.read()
            self.logger.info(f"Successfully read text file: {len(text)} characters")
            return text
        except Exception as e:
            self.logger.error(f"Error reading text file: {e}")
            raise
    
    def write_file(self, text, file_path, encoding='utf-8'):
        """
        Write text to a file.
        
        Parameters
        ----------
        text : str
            The text to write.
        
        file_path : str
            Path to the output text file.
        
        encoding : str, default='utf-8'
            The encoding for the output file.
        
        Returns
        -------
        str
            The path to the written file.
        """
        try:
            self.logger.info(f"Writing text file: {file_path}")
            with open(file_path, 'w', encoding=encoding) as file:
                file.write(text)
            self.logger.info(f"Successfully wrote text file: {len(text)} characters")
            return file_path
        except Exception as e:
            self.logger.error(f"Error writing text file: {e}")
            raise
    
    def read_lines(self, file_path, encoding='utf-8'):
        """
        Read a text file and return lines as a list.
        
        Parameters
        ----------
        file_path : str
            Path to the text file.
        
        encoding : str, default='utf-8'
            The encoding of the text file.
        
        Returns
        -------
        list
            The lines of the text file.
        """
        try:
            self.logger.info(f"Reading lines from text file: {file_path}")
            with open(file_path, 'r', encoding=encoding) as file:
                lines = file.readlines()
            self.logger.info(f"Successfully read {len(lines)} lines from text file")
            return lines
        except Exception as e:
            self.logger.error(f"Error reading lines from text file: {e}")
            raise
    
    def write_lines(self, lines, file_path, encoding='utf-8'):
        """
        Write lines to a text file.
        
        Parameters
        ----------
        lines : list
            The lines to write.
        
        file_path : str
            Path to the output text file.
        
        encoding : str, default='utf-8'
            The encoding for the output file.
        
        Returns
        -------
        str
            The path to the written file.
        """
        try:
            self.logger.info(f"Writing lines to text file: {file_path}")
            with open(file_path, 'w', encoding=encoding) as file:
                file.writelines(lines)
            self.logger.info(f"Successfully wrote {len(lines)} lines to text file")
            return file_path
        except Exception as e:
            self.logger.error(f"Error writing lines to text file: {e}")
            raise
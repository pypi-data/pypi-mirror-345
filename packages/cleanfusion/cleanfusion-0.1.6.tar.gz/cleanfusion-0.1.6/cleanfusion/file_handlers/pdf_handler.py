"""
PDF file handler module for reading and extracting text from PDF files.
"""
import PyPDF2
import os
import re
from cleanfusion.utils.logger import Logger
import pdfplumber

class PDFHandler:
    """
    Handler for PDF files.
    """
    
    def __init__(self):
        """Initialize the PDF handler."""
        self.logger = Logger()
    
    def read_file(self, file_path):
        """
        Extract text from a PDF file.
        
        Parameters
        ----------
        file_path : str
            Path to the PDF file.
        
        Returns
        -------
        str
            The extracted text from the PDF.
        """
        try:
            self.logger.info(f"Reading PDF file: {file_path}")
            
            try:
                
                # Extract text with PyPDF2
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ''
                    for page in reader.pages:
                        text += page.extract_text() + '\n\n'
                self.logger.info(f"Successfully extracted text from PDF with PyPDF2")
                
            except ImportError:
                self.logger.warning("PyPDF2 not installed. Attempting to use pdfplumber...")
                try:
                    
                    with pdfplumber.open(file_path) as pdf:
                        text = ''
                        for page in pdf.pages:
                            text += page.extract_text() + '\n\n'
                    self.logger.info(f"Successfully extracted text from PDF with pdfplumber")
                except ImportError:
                    self.logger.error("Neither PyPDF2 nor pdfplumber is installed. Please install one of them.")
                    raise ImportError("PDF extraction requires PyPDF2 or pdfplumber. Please install one of them.")
            
            return text
            
        except Exception as e:
            self.logger.error(f"Error reading PDF file: {e}")
            raise
    
    def write_file(self, text, file_path):
        """
        Write extracted text to a file.
        
        Parameters
        ----------
        text : str
            The text to write.
        
        file_path : str
            Path to the output file.
        
        Returns
        -------
        str
            The path to the written file.
        """
        try:
            self.logger.info(f"Writing extracted text to: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(text)
            self.logger.info(f"Successfully wrote extracted text to file")
            return file_path
        except Exception as e:
            self.logger.error(f"Error writing file: {e}")
            raise
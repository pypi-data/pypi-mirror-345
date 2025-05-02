"""
CleanFusion: A comprehensive data cleaning and preprocessing library.

This package provides tools for cleaning and preprocessing various types of data,
including CSV, TXT, DOCX, and PDF files.
"""

from cleanfusion.core.data_preprocessor import DataPreprocessor
from cleanfusion.core.data_assessment import DataAssessment

# Convenient shorthand for common use cases
from cleanfusion.core.data_preprocessor import DataPreprocessor as DataCleaner

__version__ = "0.1.0"
__author__ = "Hriday Thaker"
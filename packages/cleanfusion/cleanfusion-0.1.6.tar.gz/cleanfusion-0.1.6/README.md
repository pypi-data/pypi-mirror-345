# CleanFusion: A Comprehensive Data Cleaning Library

## Overview

CleanFusion is a powerful Python library designed to streamline and automate data cleaning tasks. Built with flexibility and ease-of-use in mind, it provides a comprehensive suite of tools for data assessment, preprocessing, and transformation. Whether you're dealing with missing values, outliers, inconsistent text data, or need to extract information from various file formats, CleanFusion offers an integrated solution for all your data cleaning needs.

## Authors

- [Himanshu Chopade](https://github.com/himanshuchopade97)
- [Hriday Thaker](https://github.com/thakerhriday)
- [Aryan Bachute](https://github.com/Aryanfour5)
- [Gautam Rajhans](https://github.com/capricode-ui)

## Features

### Core Functionality

- **Data Assessment**: Comprehensive analysis of data quality issues including missing values, outliers, data type inconsistencies, duplicates, and distribution analysis
- **Missing Value Handling**: Multiple strategies for imputing missing data (mean, median, mode, KNN, constant values)
- **Outlier Detection and Treatment**: Z-score and IQR-based methods with configurable thresholds and handling strategies
- **Decision Engine**: Intelligent recommendations for data cleaning strategies based on data characteristics
- **Categorical Data Encoding**: Various encoding techniques (label, one-hot, ordinal, binary, target encoding)

### Text Processing

- **Text Cleaning**: Lowercasing, punctuation removal, stopword removal, lemmatization, and negation handling
- **Text Vectorization**: Convert text to numerical features using TF-IDF, count vectorization, or BERT embeddings

### File Handling

- **Multiple Format Support**: Process CSV, TXT, DOCX, and PDF files
- **Seamless Conversion**: Extract and clean text from various document formats

## Installation

```bash
pip install cleanfusion
```

## Requirements

- Python 3.7+
- pandas
- numpy
- scikit-learn
- nltk
- PyPDF2
- pdfplumber (optional, for enhanced PDF extraction)
- sentence-transformers (optional, for BERT embeddings)

## Quick Start

### Command Line Interface


CleanFusion provides a convenient command-line interface for common data cleaning tasks:

```
cleanfusion  --help
```
Replace file names and column names as needed for your use case.
```

# Assess data quality
cleanfusion assess data.csv --output assessment_report.txt

# Get cleaning recommendations
cleanfusion recommend data.csv --output recommendations.txt

# Clean a data file
cleanfusion clean data.csv --numerical median --categorical most_frequent --output cleaned_data.csv

# Clean text data
cleanfusion text document.txt --lowercase --remove-punctuation --remove-stopwords --output cleaned_text.txt

# Vectorize text data
cleanfusion vectorize document.txt --method tfidf --output vectors.csv

# Encode categorical data (one-hot encoding for specific columns)
cleanfusion encode data.csv --method onehot --columns Category,Region --output encoded_data.csv

# Label encoding
cleanfusion encode data.csv --method label --output encoded_data.csv

# Target encoding (with a target variable)
cleanfusion encode data.csv --method target --target TargetColumn --output target_encoded.csv

# Clean a DOCX file
cleanfusion clean document.docx --output cleaned_document.docx

# Clean a PDF file
cleanfusion clean document.pdf --output extracted_text.txt
```

**Tip:**  
For details and all options for any command, run:

```
cleanfusion  <command> --help
```

### Python API

```python
# Data assessment
from cleanfusion.core.data_assessment import DataAssessment

assessment = DataAssessment()
results = assessment.assess(df)
report = assessment.generate_report(output_path="report.txt")

# Data cleaning
from cleanfusion.core.data_preprocessor import DataPreprocessor

preprocessor = DataPreprocessor(
    numerical_strategy="median",
    categorical_strategy="most_frequent",
    outlier_threshold=2.5
)
cleaned_df = preprocessor.transform(df)

# Text processing
from cleanfusion.text.text_cleaner import TextCleaner
from cleanfusion.text.text_vectorizer import TextVectorizer

cleaner = TextCleaner(remove_stopwords=True, lemmatize=True)
cleaned_text = cleaner.clean_text(text)

vectorizer = TextVectorizer(method="tfidf")
vectors = vectorizer.vectorize(texts)

# Categorical encoding
from cleanfusion.text.categorical_encoder import CategoricalEncoder

encoder = CategoricalEncoder(method="onehot")
encoded_df = encoder.fit_transform(df, columns=["Category", "Region"])
```

## Detailed Usage

### Data Assessment

The `DataAssessment` class provides comprehensive analysis of data quality:

```python
from cleanfusion.core.data_assessment import DataAssessment

assessment = DataAssessment()
results = assessment.assess(df)

# Access specific assessment results
missing_values = results["missing_values"]
outliers = results["outliers"]
correlations = results["correlations"]
distributions = results["distributions"]

# Generate a comprehensive report
report = assessment.generate_report(output_path="assessment_report.txt")
```

### Decision Engine

The `DecisionEngine` provides intelligent recommendations for data cleaning:

```python
from cleanfusion.core.decision_engine import DecisionEngine

engine = DecisionEngine()
recommendations = engine.analyze(df)

# Get specific recommendations
missing_value_recs = recommendations["missing_values"]
outlier_recs = recommendations["outliers"]
feature_selection_recs = recommendations["feature_selection"]
text_cleaning_recs = recommendations["text_cleaning"]

# Generate a human-readable report
report = engine.get_recommendation_report()
```

### Missing Value Handling

```python
from cleanfusion.core.missing_value_handler import MissingValueHandler

handler = MissingValueHandler()

# Handle missing values in numerical columns
df["numeric_column"] = handler.handle_numerical_missing(df["numeric_column"], method="median")

# Handle missing values in categorical columns
df["category_column"] = handler.handle_categorical_missing(df["category_column"], method="most_frequent")

# Drop rows or columns with too many missing values
df = handler.drop_missing(df, threshold=0.5)
```

### Outlier Detection and Handling

```python
from cleanfusion.core.outlier_handler import OutlierHandler

handler = OutlierHandler(df)

# Detect outliers
z_outliers = handler.detect_outliers_zscore("column_name", threshold=3.0)
iqr_outliers = handler.detect_outliers_iqr("column_name", multiplier=1.5)

# Handle outliers
df = handler.handle_outliers_zscore("column_name", method="clip")
df = handler.handle_outliers_iqr("column_name", method="remove")

# Get summary of detected outliers
summary = handler.get_outlier_summary()
```

### Text Processing

```python
from cleanfusion.text.text_cleaner import TextCleaner

cleaner = TextCleaner(
    remove_stopwords=True,
    lemmatize=True,
    handle_negation=True,
    preserve_structure=False
)

cleaned_text = cleaner.clean_text(
    text,
    lowercase=True,
    remove_punctuation=True
)
```

### Text Vectorization

```python
from cleanfusion.text.text_vectorizer import TextVectorizer

vectorizer = TextVectorizer(method="tfidf")  # Options: "tfidf", "count", "bert"
vectors = vectorizer.vectorize(texts, return_array=True)

# Get feature names
feature_names = vectorizer.get_features()
```

### Categorical Encoding

```python
from cleanfusion.text.categorical_encoder import CategoricalEncoder

# Label encoding
encoder = CategoricalEncoder(method="label")
encoded_df = encoder.fit_transform(df, columns=["Category", "Region"])

# One-hot encoding
encoder = CategoricalEncoder(method="onehot")
encoded_df = encoder.fit_transform(df, columns=["Category"])

# Ordinal encoding with custom ordering
ordinal_mappings = {"Size": ["Small", "Medium", "Large"]}
encoder = CategoricalEncoder(method="ordinal")
encoded_df = encoder.fit_transform(df, columns=["Size"], ordinal_mappings=ordinal_mappings)

# Target encoding
encoder = CategoricalEncoder(method="target")
encoded_df = encoder.fit_transform(df, columns=["Category"], target_column="Target")
```

### File Handling

```python
# CSV files
from cleanfusion.file_handlers.csv_handler import CSVHandler
handler = CSVHandler()
df = handler.read_file("data.csv")
handler.write_file(df, "output.csv")

# Text files
from cleanfusion.file_handlers.txt_handler import TXTHandler
handler = TXTHandler()
text = handler.read_file("document.txt")
handler.write_file(text, "output.txt")

# PDF files
from cleanfusion.file_handlers.pdf_handler import PDFHandler
handler = PDFHandler()
text = handler.read_file("document.pdf")
handler.write_file(text, "extracted_text.txt")

# DOCX files
from cleanfusion.file_handlers.docx_handler import DOCXHandler
handler = DOCXHandler()
text = handler.read_file("document.docx")
handler.write_file(text, "extracted_text.txt")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The scikit-learn team for their excellent machine learning library
- The NLTK project for natural language processing tools
- All contributors who have helped improve this library

![PyPI - Downloads](https://img.shields.io/pypi/dm/cleanfusion?label=Downloads&color=brightgreen)

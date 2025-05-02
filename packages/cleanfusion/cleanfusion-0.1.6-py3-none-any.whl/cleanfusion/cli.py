"""
Command-line interface for the CleanFusion data cleaning library.
"""

import argparse
import os
import pandas as pd
import sys
from pathlib import Path

from cleanfusion.core.data_preprocessor import DataPreprocessor
from cleanfusion.core.data_assessment import DataAssessment
from cleanfusion.core.decision_engine import DecisionEngine
from cleanfusion.file_handlers.csv_handler import CSVHandler
from cleanfusion.utils.logger import Logger
from cleanfusion.text.text_cleaner import TextCleaner
from cleanfusion.text.text_vectorizer import TextVectorizer

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="CleanFusion - A comprehensive data cleaning library",
        fromfile_prefix_chars="@"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean a data file")
    clean_parser.add_argument("file", help="Path to the file to clean")
    clean_parser.add_argument("--output", "-o", help="Output file path")
    clean_parser.add_argument("--numerical", choices=["mean", "median", "knn"], default="mean",
                             help="Strategy for handling missing numerical values")
    clean_parser.add_argument("--categorical", choices=["most_frequent", "constant"], default="most_frequent",
                             help="Strategy for handling missing categorical values")
    clean_parser.add_argument("--outlier-threshold", type=float, default=3.0,
                             help="Threshold for outlier detection")
    clean_parser.add_argument("--text-vectorizer", choices=["tfidf", "count", "bert"], default="tfidf",
                             help="Method for vectorizing text data")
    
    # Assess command
    assess_parser = subparsers.add_parser("assess", help="Assess data quality")
    assess_parser.add_argument("file", help="Path to the file to assess")
    assess_parser.add_argument("--output", "-o", help="Output report file path")
    
    # Recommend command
    recommend_parser = subparsers.add_parser("recommend", help="Get cleaning recommendations")
    recommend_parser.add_argument("file", help="Path to the file to analyze")
    recommend_parser.add_argument("--output", "-o", help="Output recommendation file path")
    
    # Text cleaning command
    text_parser = subparsers.add_parser("text", help="Clean text data")
    text_parser.add_argument("file", help="Path to the text file to clean")
    text_parser.add_argument("--output", "-o", help="Output file path")
    text_parser.add_argument("--lowercase", action="store_true", help="Convert text to lowercase")
    text_parser.add_argument("--remove-punctuation", action="store_true", help="Remove punctuation")
    text_parser.add_argument("--remove-stopwords", action="store_true", help="Remove stopwords")
    text_parser.add_argument("--lemmatize", action="store_true", help="Lemmatize words")
    text_parser.add_argument("--handle-negation", action="store_true", help="Handle negation (e.g., not good -> not_good)")
    
    # Vectorize command
    vectorize_parser = subparsers.add_parser("vectorize", help="Vectorize text data")
    vectorize_parser.add_argument("file", help="Path to the text file to vectorize")
    vectorize_parser.add_argument("--output", "-o", help="Output file path")
    vectorize_parser.add_argument("--method", choices=["tfidf", "count", "bert"], default="tfidf",
                                help="Vectorization method")
    
    # Add a new subparser for encoding
    encode_parser = subparsers.add_parser("encode", help="Encode categorical data in a CSV file")
    encode_parser.add_argument("file", help="Path to the CSV file")
    encode_parser.add_argument("--output", "-o", help="Output file path")
    encode_parser.add_argument("--method", choices=["label", "onehot", "ordinal", "binary", "target"], 
                            default="label", help="Encoding method")
    encode_parser.add_argument("--columns", help="Comma-separated list of columns to encode")
    encode_parser.add_argument("--target", help="Target column for target encoding")
    encode_parser.add_argument("--keep-original", action="store_true", 
                            help="Keep original columns after encoding")

    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize logger
    logger = Logger()
    
    # Execute the appropriate command
    if args.command == "clean":
        clean_file(args)
    elif args.command == "assess":
        assess_file(args)
    elif args.command == "recommend":
        recommend_file(args)
    elif args.command == "text":
        clean_text_file(args)
    elif args.command == "vectorize":
        vectorize_text_file(args)
    elif args.command == "encode":
        encode_categorical_data(args)

    else:
        parser.print_help()
        return 1
    
    return 0

def clean_file(args):
    """Clean a data file using DataPreprocessor."""
    logger = Logger()
    logger.info(f"Cleaning file: {args.file}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        return 1
    
    # Create preprocessor with specified parameters
    preprocessor = DataPreprocessor(
        numerical_strategy=args.numerical,
        categorical_strategy=args.categorical,
        outlier_threshold=args.outlier_threshold,
        text_vectorizer=args.text_vectorizer
    )
    
    try:
        # Clean the file
        output_path = args.output if args.output else None
        preprocessor.clean_file(args.file, output_path)
        
        if output_path:
            logger.info(f"Cleaned data saved to: {output_path}")
        else:
            logger.info("Cleaning completed successfully")
            
    except Exception as e:
        logger.error(f"Error cleaning file: {e}")
        return 1
    
    return 0

def assess_file(args):
    """Assess data quality using DataAssessment."""
    logger = Logger()
    logger.info(f"Assessing file: {args.file}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        return 1
    
    try:
        # Read the file
        file_ext = os.path.splitext(args.file)[1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(args.file)
        else:
            logger.error(f"Unsupported file format for assessment: {file_ext}")
            return 1
        
        # Create assessment
        assessment = DataAssessment()
        assessment.assess(df)
        
        # Generate report
        report = assessment.generate_report()
        
        # Save or print report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Assessment report saved to: {args.output}")
        else:
            print(report)
            
    except Exception as e:
        logger.error(f"Error assessing file: {e}")
        return 1
    
    return 0

def recommend_file(args):
    """Generate cleaning recommendations using DecisionEngine."""
    logger = Logger()
    logger.info(f"Analyzing file for recommendations: {args.file}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        return 1
    
    try:
        # Read the file
        file_ext = os.path.splitext(args.file)[1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(args.file)
        else:
            logger.error(f"Unsupported file format for recommendations: {file_ext}")
            return 1
        
        # Create decision engine
        engine = DecisionEngine()
        engine.analyze(df)
        
        # Generate recommendation report
        report = engine.get_recommendation_report()
        
        # Save or print report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Recommendation report saved to: {args.output}")
        else:
            print(report)
            
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return 1
    
    return 0

def clean_text_file(args):
    """Clean a text file using TextCleaner."""
    logger = Logger()
    logger.info(f"Cleaning text file: {args.file}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        return 1
    
    try:
        # Read the file
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Create text cleaner
        cleaner = TextCleaner()
        
        # Set options based on arguments
        options = {
            'lowercase': args.lowercase,
            'remove_punctuation': args.remove_punctuation,
            'remove_stopwords': args.remove_stopwords,
            'lemmatize': args.lemmatize,
            'handle_negation': args.handle_negation
        }
        
        # Clean the text
        cleaned_text = cleaner.clean_text(text, **options)
        
        # Save or print cleaned text
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            logger.info(f"Cleaned text saved to: {args.output}")
        else:
            print(cleaned_text)
            
    except Exception as e:
        logger.error(f"Error cleaning text: {e}")
        return 1
    
    return 0

def vectorize_text_file(args):
    """Vectorize a text file using TextVectorizer."""
    logger = Logger()
    logger.info(f"Vectorizing text file: {args.file}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        return 1
    
    try:
        # Read the file
        with open(args.file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Split text into lines or paragraphs
        texts = [t.strip() for t in text.split('\n') if t.strip()]
        
        # Create vectorizer
        vectorizer = TextVectorizer(method=args.method)
        
        # Vectorize the text
        vectors = vectorizer.vectorize(texts, return_array=True)
        
        # Save or print vectors
        if args.output:
            # Save as CSV
            pd.DataFrame(vectors).to_csv(args.output, index=False)
            logger.info(f"Vectorized text saved to: {args.output}")
        else:
            # Print shape and sample
            print(f"Vectorized shape: {vectors.shape}")
            print(f"Sample (first 5 rows, up to 10 features):")
            print(vectors[:5, :min(10, vectors.shape[1])])
            
    except Exception as e:
        logger.error(f"Error vectorizing text: {e}")
        return 1
    
    return 0

def encode_categorical_data(args):
    """Encode categorical data in a CSV file."""
    logger = Logger()
    logger.info(f"Encoding categorical data in file: {args.file}")
    
    # Check if file exists
    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        return 1
    
    try:
        # Read the CSV file
        handler = CSVHandler()
        df = handler.read_file(args.file)
        
        # Parse columns to encode
        columns = args.columns.split(',') if args.columns else None
        
        # Create encoder
        from cleanfusion.text.categorical_encoder import CategoricalEncoder
        encoder = CategoricalEncoder(method=args.method)
        
        # Encode the data
        encoded_df = encoder.fit_transform(
            df, 
            columns=columns,
            target_column=args.target,
            drop_original=not args.keep_original
        )
        
        # Save the encoded data
        output_path = args.output if args.output else None
        if not output_path:
            base_name = os.path.basename(args.file)
            base_name_no_ext = os.path.splitext(base_name)[0]
            output_path = f"encoded_{base_name_no_ext}.csv"
        
        handler.write_file(encoded_df, output_path)
        logger.info(f"Encoded data saved to: {output_path}")
        
    except Exception as e:
        logger.error(f"Error encoding categorical data: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

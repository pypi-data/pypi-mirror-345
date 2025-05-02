"""
Data assessment module for analyzing and reporting data quality issues.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from cleanfusion.utils.logger import Logger
from cleanfusion.core.outlier_handler import OutlierHandler

class DataAssessment:
    """
    Class for assessing data quality and identifying issues.
    
    Features:
    - Missing value analysis
    - Outlier detection
    - Data type consistency checks
    - Duplicate detection
    - Distribution analysis
    - Correlation analysis
    """
    
    def __init__(self, data=None):
        """
        Initialize the DataAssessment.
        
        Parameters
        ----------
        data : pandas.DataFrame, default=None
            The DataFrame to assess.
        """
        self.data = data
        self.logger = Logger()
        self.assessment_results = {}
        
        if data is not None:
            self.assess(data)
    
    def assess(self, data):
        """
        Run a comprehensive assessment on the data.
        
        Parameters
        ----------
        data : pandas.DataFrame
            The DataFrame to assess.
        
        Returns
        -------
        dict
            Dictionary containing assessment results.
        """
        self.data = data
        self.logger.info(f"Starting data assessment on DataFrame with shape {data.shape}")
        
        # Run all assessments
        self._assess_missing_values()
        self._assess_duplicates()
        self._assess_data_types()
        self._assess_outliers()
        self._assess_correlations()
        self._assess_distributions()
        
        return self.assessment_results
    
    def _assess_missing_values(self):
        """Assess missing values in the data."""
        if self.data is None:
            self.logger.warning("No data available for missing value assessment")
            return
            
        # Calculate missing value statistics
        missing_counts = self.data.isnull().sum()
        missing_percent = 100 * missing_counts / len(self.data)
        
        # Create a summary DataFrame
        missing_summary = pd.DataFrame({
            'missing_count': missing_counts,
            'missing_percent': missing_percent
        })
        
        # Add to results
        self.assessment_results['missing_values'] = {
            'summary': missing_summary,
            'total_missing_cells': missing_counts.sum(),
            'total_missing_percent': 100 * missing_counts.sum() / (self.data.shape[0] * self.data.shape[1]),
            'columns_with_missing': missing_counts[missing_counts > 0].index.tolist()
        }
        
        self.logger.info(f"Found {missing_counts.sum()} missing values across {len(missing_counts[missing_counts > 0])} columns")
    
    def _assess_duplicates(self):
        """Assess duplicate rows in the data."""
        if self.data is None:
            self.logger.warning("No data available for duplicate assessment")
            return
            
        # Check for duplicates
        duplicate_count = self.data.duplicated().sum()
        duplicate_percent = 100 * duplicate_count / len(self.data)
        
        # Add to results
        self.assessment_results['duplicates'] = {
            'count': duplicate_count,
            'percent': duplicate_percent
        }
        
        if duplicate_count > 0:
            self.logger.info(f"Found {duplicate_count} duplicate rows ({duplicate_percent:.2f}%)")
    
    def _assess_data_types(self):
        """Assess data types and their consistency."""
        if self.data is None:
            self.logger.warning("No data available for data type assessment")
            return
            
        # Get data types
        dtypes = self.data.dtypes
        
        # Check for mixed data types within columns
        mixed_type_columns = []
        for column in self.data.columns:
            # Skip non-object columns
            if dtypes[column] != 'object':
                continue
                
            # Check if column contains mixed types
            try:
                unique_types = self.data[column].dropna().apply(type).unique()
                if len(unique_types) > 1:
                    mixed_type_columns.append({
                        'column': column,
                        'types': [t.__name__ for t in unique_types]
                    })
            except Exception as e:
                self.logger.warning(f"Error checking types in column '{column}': {e}")
        
        # Add to results
        self.assessment_results['data_types'] = {
            'dtypes': dtypes.to_dict(),
            'mixed_type_columns': mixed_type_columns
        }
        
        if mixed_type_columns:
            self.logger.info(f"Found {len(mixed_type_columns)} columns with mixed data types")
    
    def _assess_outliers(self):
        """Assess outliers in numerical columns."""
        if self.data is None:
            self.logger.warning("No data available for outlier assessment")
            return
            
        # Initialize outlier handler
        outlier_handler = OutlierHandler(self.data)
        
        # Detect outliers in numerical columns
        outlier_results = {}
        for column in self.data.select_dtypes(include=['int64', 'float64']).columns:
            # Detect outliers using both methods
            z_outliers = outlier_handler.detect_outliers_zscore(column)
            iqr_outliers = outlier_handler.detect_outliers_iqr(column)
            
            outlier_results[column] = {
                'z_score': {
                    'count': z_outliers.sum(),
                    'percent': 100 * z_outliers.sum() / len(z_outliers)
                },
                'iqr': {
                    'count': iqr_outliers.sum(),
                    'percent': 100 * iqr_outliers.sum() / len(iqr_outliers)
                }
            }
        
        # Add to results
        self.assessment_results['outliers'] = outlier_results
        
        # Log summary
        total_outliers = sum(result['z_score']['count'] for result in outlier_results.values())
        self.logger.info(f"Found {total_outliers} potential outliers across {len(outlier_results)} numerical columns")
    
    def _assess_correlations(self):
        """Assess correlations between numerical columns."""
        if self.data is None:
            self.logger.warning("No data available for correlation assessment")
            return
            
        try:
            # Get numerical columns
            numerical_data = self.data.select_dtypes(include=['int64', 'float64'])
            
            if numerical_data.shape[1] < 2:
                self.logger.info("Not enough numerical columns for correlation analysis")
                return
                
            # Calculate correlation matrix
            corr_matrix = numerical_data.corr()
            
            # Find highly correlated pairs
            high_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    col1 = corr_matrix.columns[i]
                    col2 = corr_matrix.columns[j]
                    corr_value = corr_matrix.iloc[i, j]
                    
                    if abs(corr_value) > 0.7:  # Threshold for high correlation
                        high_correlations.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': corr_value
                        })
            
            # Add to results
            self.assessment_results['correlations'] = {
                'correlation_matrix': corr_matrix.to_dict(),
                'high_correlations': high_correlations
            }
            
            if high_correlations:
                self.logger.info(f"Found {len(high_correlations)} highly correlated column pairs")
                
        except Exception as e:
            self.logger.warning(f"Error during correlation assessment: {e}")
    
    def _assess_distributions(self):
        """Assess distributions of numerical columns."""
        if self.data is None:
            self.logger.warning("No data available for distribution assessment")
            return
            
        # Get numerical columns
        numerical_data = self.data.select_dtypes(include=['int64', 'float64'])
        
        # Calculate distribution statistics
        distribution_stats = {}
        for column in numerical_data.columns:
            series = numerical_data[column].dropna()
            
            if len(series) == 0:
                continue
                
            stats = {
                'mean': series.mean(),
                'median': series.median(),
                'std': series.std(),
                'min': series.min(),
                'max': series.max(),
                'skewness': series.skew(),
                'kurtosis': series.kurt(),
                'range': series.max() - series.min()
            }
            
            # Detect distribution type (normal, uniform, etc.)
            # This is a simple heuristic and could be improved
            if abs(stats['skewness']) < 0.5 and abs(stats['kurtosis']) < 1:
                stats['distribution_type'] = 'likely_normal'
            elif abs(stats['skewness']) > 1:
                stats['distribution_type'] = 'skewed'
            else:
                stats['distribution_type'] = 'unknown'
                
            distribution_stats[column] = stats
        
        # Add to results
        self.assessment_results['distributions'] = distribution_stats
        
        self.logger.info(f"Analyzed distributions for {len(distribution_stats)} numerical columns")
    
    def generate_report(self, output_path=None):
        """
        Generate a comprehensive data quality report.
        
        Parameters
        ----------
        output_path : str, default=None
            Path to save the report. If None, returns the report as a string.
        
        Returns
        -------
        str or None
            The report as a string if output_path is None, otherwise None.
        """
        if not self.assessment_results:
            self.logger.warning("No assessment results available. Run assess() first.")
            return "No assessment results available. Run assess() first."
        
        # Build report
        report = []
        report.append("# Data Quality Assessment Report")
        report.append(f"\n## Dataset Overview")
        report.append(f"- Number of rows: {self.data.shape[0]}")
        report.append(f"- Number of columns: {self.data.shape[1]}")
        
        # Missing values
        if 'missing_values' in self.assessment_results:
            missing = self.assessment_results['missing_values']
            report.append("\n## Missing Values")
            report.append(f"- Total missing cells: {missing['total_missing_cells']} ({missing['total_missing_percent']:.2f}%)")
            report.append(f"- Columns with missing values: {len(missing['columns_with_missing'])}")
            
            # Top 5 columns with most missing values
            top_missing = missing['summary'].sort_values('missing_count', ascending=False).head(5)
            if not top_missing.empty:
                report.append("\n### Top 5 Columns with Missing Values")
                for idx, row in top_missing.iterrows():
                    report.append(f"- {idx}: {row['missing_count']} values ({row['missing_percent']:.2f}%)")
        
        # Duplicates
        if 'duplicates' in self.assessment_results:
            duplicates = self.assessment_results['duplicates']
            report.append("\n## Duplicate Rows")
            report.append(f"- Duplicate rows: {duplicates['count']} ({duplicates['percent']:.2f}%)")
        
        # Data types
        if 'data_types' in self.assessment_results:
            dtypes = self.assessment_results['data_types']
            report.append("\n## Data Types")
            report.append("### Column Data Types")
            for col, dtype in dtypes['dtypes'].items():
                report.append(f"- {col}: {dtype}")
            
            if dtypes['mixed_type_columns']:
                report.append("\n### Columns with Mixed Data Types")
                for col_info in dtypes['mixed_type_columns']:
                    report.append(f"- {col_info['column']}: {', '.join(col_info['types'])}")
        
        # Outliers
        if 'outliers' in self.assessment_results:
            outliers = self.assessment_results['outliers']
            report.append("\n## Outliers")
            for column, methods in outliers.items():
                z_count = methods['z_score']['count']
                iqr_count = methods['iqr']['count']
                if z_count > 0 or iqr_count > 0:
                    report.append(f"- {column}:")
                    report.append(f"  - Z-score method: {z_count} outliers ({methods['z_score']['percent']:.2f}%)")
                    report.append(f"  - IQR method: {iqr_count} outliers ({methods['iqr']['percent']:.2f}%)")
        
        # Correlations
        if 'correlations' in self.assessment_results and 'high_correlations' in self.assessment_results['correlations']:
            high_corrs = self.assessment_results['correlations']['high_correlations']
            if high_corrs:
                report.append("\n## High Correlations")
                for corr in high_corrs:
                    report.append(f"- {corr['column1']} and {corr['column2']}: {corr['correlation']:.3f}")
        
        # Distributions
        if 'distributions' in self.assessment_results:
            distributions = self.assessment_results['distributions']
            report.append("\n## Distributions")
            for column, stats in distributions.items():
                report.append(f"\n### {column}")
                report.append(f"- Distribution type: {stats.get('distribution_type', 'unknown')}")
                report.append(f"- Mean: {stats['mean']:.3f}")
                report.append(f"- Median: {stats['median']:.3f}")
                report.append(f"- Standard deviation: {stats['std']:.3f}")
                report.append(f"- Skewness: {stats['skewness']:.3f}")
                report.append(f"- Range: {stats['min']:.3f} to {stats['max']:.3f}")
        
        # Join report sections
        full_report = "\n".join(report)
        
        # Save to file if path provided
# Save to file if path provided
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(full_report)
                self.logger.info(f"Report saved to {output_path}")
            except Exception as e:
                self.logger.error(f"Error saving report: {e}")

        # Always return the report string
        return full_report

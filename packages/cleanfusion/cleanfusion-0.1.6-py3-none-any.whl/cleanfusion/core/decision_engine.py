"""
Decision engine module for making intelligent decisions about data cleaning.
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from cleanfusion.utils.logger import Logger
from cleanfusion.core.data_assessment import DataAssessment

class DecisionEngine:
    """
    Class for making intelligent decisions about data cleaning strategies.
    
    Features:
    - Auto-detection of data types
    - Recommendation of cleaning strategies
    - Data quality scoring
    - Optimization of cleaning pipelines
    """
    
    def __init__(self, data=None):
        """
        Initialize the DecisionEngine.
        
        Parameters
        ----------
        data : pandas.DataFrame, default=None
            The DataFrame to analyze.
        """
        self.data = data
        self.logger = Logger()
        self.assessment = None
        self.recommendations = {}
        
        if data is not None:
            self.analyze(data)
    
    def analyze(self, data):
        """
        Analyze the data and generate recommendations.
        
        Parameters
        ----------
        data : pandas.DataFrame
            The DataFrame to analyze.
        
        Returns
        -------
        dict
            Dictionary containing recommendations.
        """
        self.data = data
        self.logger.info(f"Starting analysis for decision recommendations")
        
        # Run assessment
        self.assessment = DataAssessment()
        assessment_results = self.assessment.assess(data)
        
        # Generate recommendations based on assessment
        self._recommend_missing_value_strategies()
        self._recommend_outlier_strategies()
        self._recommend_feature_selection()
        self._recommend_text_cleaning()
        
        return self.recommendations
    
    def _recommend_missing_value_strategies(self):
        """Generate recommendations for handling missing values."""
        if not self.assessment or 'missing_values' not in self.assessment.assessment_results:
            self.logger.warning("No missing value assessment available")
            return
        
        missing_values = self.assessment.assessment_results['missing_values']
        recommendations = {}
        
        for column in missing_values['columns_with_missing']:
            # Get column info
            missing_percent = missing_values['summary'].loc[column, 'missing_percent']
            is_numeric = pd.api.types.is_numeric_dtype(self.data[column])
            is_categorical = pd.api.types.is_categorical_dtype(self.data[column]) or (
                pd.api.types.is_object_dtype(self.data[column]) and self.data[column].nunique() < 20
            )
            
            # Make recommendations based on missing percentage and column type
            if missing_percent > 75:
                recommendations[column] = {
                    'action': 'drop_column',
                    'reason': f"Column has {missing_percent:.1f}% missing values, too high to reliably impute."
                }
            elif missing_percent > 50:
                recommendations[column] = {
                    'action': 'consider_dropping',
                    'reason': f"Column has {missing_percent:.1f}% missing values, consider removing."
                }
            elif is_numeric:
                # Check for timeseries data
                is_timeseries = False
                if 'datetime' in str(self.data.columns).lower() or 'date' in str(self.data.columns).lower():
                    is_timeseries = True
                
                if is_timeseries:
                    recommendations[column] = {
                        'action': 'interpolate',
                        'method': 'time',
                        'reason': "Numeric column in timeseries data, interpolation is appropriate."
                    }
                elif missing_percent <= 5:
                    recommendations[column] = {
                        'action': 'impute',
                        'method': 'mean',
                        'reason': "Low percentage of missing values in numeric column."
                    }
                elif missing_percent <= 15:
                    recommendations[column] = {
                        'action': 'impute',
                        'method': 'median',
                        'reason': "Moderate missing values in numeric column, median less sensitive to outliers."
                    }
                else:
                    recommendations[column] = {
                        'action': 'impute',
                        'method': 'knn',
                        'reason': "Higher percentage of missing values, KNN may capture patterns better."
                    }
            elif is_categorical:
                if missing_percent <= 10:
                    recommendations[column] = {
                        'action': 'impute',
                        'method': 'most_frequent',
                        'reason': "Low percentage of missing values in categorical column."
                    }
                else:
                    recommendations[column] = {
                        'action': 'impute',
                        'method': 'new_category',
                        'reason': "Higher percentage of missing values, creating a new 'Unknown' category."
                    }
            else:
                # Assume text or other complex type
                recommendations[column] = {
                    'action': 'impute',
                    'method': 'empty_string',
                    'reason': "Complex column type, replacing with empty string or placeholder."
                }
        
        self.recommendations['missing_values'] = recommendations
    
    def _recommend_outlier_strategies(self):
        """Generate recommendations for handling outliers."""
        if not self.assessment or 'outliers' not in self.assessment.assessment_results:
            self.logger.warning("No outlier assessment available")
            return
        
        outliers = self.assessment.assessment_results['outliers']
        recommendations = {}
        
        for column, methods in outliers.items():
            z_percent = methods['z_score']['percent']
            iqr_percent = methods['iqr']['percent']
            
            # Use the more conservative estimate
            outlier_percent = min(z_percent, iqr_percent)
            
            # Check if column is likely a natural distribution with expected outliers
            if 'distributions' in self.assessment.assessment_results:
                dist = self.assessment.assessment_results['distributions'].get(column, {})
                is_normal = dist.get('distribution_type') == 'likely_normal'
                is_skewed = dist.get('distribution_type') == 'skewed'
                skewness = dist.get('skewness', 0)
            else:
                is_normal = False
                is_skewed = False
                skewness = 0
            
            # Generate recommendations
            if outlier_percent <= 1:
                # Few outliers, could be errors
                recommendations[column] = {
                    'action': 'clip',
                    'reason': f"Small percentage of outliers ({outlier_percent:.1f}%), likely data errors."
                }
            elif outlier_percent <= 5:
                if is_normal:
                    recommendations[column] = {
                        'action': 'keep',
                        'reason': f"Moderate outliers ({outlier_percent:.1f}%) in normally distributed data, likely valid values."
                    }
                else:
                    recommendations[column] = {
                        'action': 'winsorize',
                        'percentile': 95,
                        'reason': f"Moderate outliers ({outlier_percent:.1f}%), winsorizing to reduce impact."
                    }
            elif is_skewed and abs(skewness) > 1:
                recommendations[column] = {
                    'action': 'transform',
                    'method': 'log' if skewness > 0 else 'sqrt',
                    'reason': f"Skewed distribution (skewness={skewness:.2f}) with outliers, transformation recommended."
                }
            else:
                recommendations[column] = {
                    'action': 'robust_scaling',
                    'reason': f"Significant outliers ({outlier_percent:.1f}%), robust scaling recommended."
                }
        
        self.recommendations['outliers'] = recommendations
    
    def _recommend_feature_selection(self):
        """Generate recommendations for feature selection."""
        # Check for correlations
        if self.assessment and 'correlations' in self.assessment.assessment_results:
            correlations = self.assessment.assessment_results['correlations']
            high_corrs = correlations.get('high_correlations', [])
            
            if high_corrs:
                # Group correlations by columns
                column_correlations = defaultdict(list)
                for corr in high_corrs:
                    column_correlations[corr['column1']].append((corr['column2'], corr['correlation']))
                    column_correlations[corr['column2']].append((corr['column1'], corr['correlation']))
                
                # Find columns with most correlations (potential for removal)
                recommendations = {}
                for column, corrs in column_correlations.items():
                    if len(corrs) >= 2:  # If correlated with multiple columns
                        recommendations[column] = {
                            'action': 'consider_removing',
                            'correlated_with': [c[0] for c in corrs],
                            'correlation_values': [c[1] for c in corrs],
                            'reason': f"Highly correlated with {len(corrs)} other columns, potential redundancy."
                        }
                
                self.recommendations['feature_selection'] = recommendations
    
    def _recommend_text_cleaning(self):
        """Generate recommendations for text cleaning."""
        if not self.data is not None:
            return
            
        # Identify potential text columns
        text_columns = []
        for column in self.data.select_dtypes(include=['object']):
            series = self.data[column].dropna()
            if len(series) == 0:
                continue
                
            # Check if it's likely a text column (based on average length and uniqueness)
            avg_length = series.astype(str).apply(len).mean()
            uniqueness_ratio = series.nunique() / len(series)
            
            if avg_length > 20 or uniqueness_ratio > 0.5:
                text_columns.append(column)
        
        if text_columns:
            recommendations = {}
            for column in text_columns:
                # Sample some values to check characteristics
                sample = self.data[column].dropna().sample(min(5, len(self.data[column].dropna()))).astype(str)
                
                has_punctuation = any(any(c in s for c in ',.;:!?') for s in sample)
                has_uppercase = any(any(c.isupper() for c in s) for s in sample)
                has_numbers = any(any(c.isdigit() for c in s) for s in sample)
                
                cleaning_steps = []
                
                # Always recommend lowercasing for consistency
                cleaning_steps.append('lowercase')
                
                # If it has punctuation, recommend cleaning
                if has_punctuation:
                    cleaning_steps.append('remove_punctuation')
                
                # If it likely contains sentences, recommend stopword removal
                if avg_length > 50:
                    cleaning_steps.append('remove_stopwords')
                    cleaning_steps.append('lemmatization')
                
                # If it has numbers, check if they should be kept
                if has_numbers:
                    cleaning_steps.append('consider_removing_numbers')
                
                recommendations[column] = {
                    'action': 'text_cleaning',
                    'steps': cleaning_steps,
                    'reason': f"Text column with avg length {avg_length:.1f}, recommended preprocessing steps."
                }
            
            self.recommendations['text_cleaning'] = recommendations
    
    def get_recommendation_report(self):
        """
        Generate a human-readable report of recommendations.
        
        Returns
        -------
        str
            The recommendation report.
        """
        if not self.recommendations:
            return "No recommendations available. Run analyze() first."
        
        report = []
        report.append("# Data Cleaning Recommendations")
        
        # Missing values
        if 'missing_values' in self.recommendations:
            report.append("\n## Missing Value Recommendations")
            for column, rec in self.recommendations['missing_values'].items():
                report.append(f"\n### Column: {column}")
                report.append(f"- Recommended action: {rec['action']}")
                if 'method' in rec:
                    report.append(f"- Method: {rec['method']}")
                report.append(f"- Reason: {rec['reason']}")
        
        # Outliers
        if 'outliers' in self.recommendations:
            report.append("\n## Outlier Recommendations")
            for column, rec in self.recommendations['outliers'].items():
                report.append(f"\n### Column: {column}")
                report.append(f"- Recommended action: {rec['action']}")
                if 'method' in rec:
                    report.append(f"- Method: {rec['method']}")
                if 'percentile' in rec:
                    report.append(f"- Percentile: {rec['percentile']}")
                report.append(f"- Reason: {rec['reason']}")
        
        # Feature selection
        if 'feature_selection' in self.recommendations:
            report.append("\n## Feature Selection Recommendations")
            for column, rec in self.recommendations['feature_selection'].items():
                report.append(f"\n### Column: {column}")
                report.append(f"- Recommended action: {rec['action']}")
                report.append(f"- Correlated with: {', '.join(rec['correlated_with'])}")
                report.append(f"- Reason: {rec['reason']}")
        
        # Text cleaning
        if 'text_cleaning' in self.recommendations:
            report.append("\n## Text Cleaning Recommendations")
            for column, rec in self.recommendations['text_cleaning'].items():
                report.append(f"\n### Column: {column}")
                report.append(f"- Recommended cleaning steps:")
                for step in rec['steps']:
                    report.append(f"  - {step}")
                report.append(f"- Reason: {rec['reason']}")
        
        return "\n".join(report)
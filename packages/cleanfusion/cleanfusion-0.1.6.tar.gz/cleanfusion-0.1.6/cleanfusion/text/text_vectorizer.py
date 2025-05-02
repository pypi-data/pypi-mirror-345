"""
Text vectorization module for converting text to numerical features.
"""

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import pandas as pd
import numpy as np
from cleanfusion.utils.logger import Logger

class TextVectorizer:
    """
    Class for vectorizing text data using various techniques.
    
    Features:
    - TF-IDF vectorization
    - Count vectorization
    - Optional sentence transformer embeddings (when dependencies are installed)
    """
    
    def __init__(self, method='tfidf'):
        """
        Initialize the TextVectorizer.
        
        Parameters
        ----------
        method : str, default='tfidf'
            Vectorization method: 'tfidf', 'count', or 'bert'.
        """
        self.method = method
        self.logger = Logger()
        self.vectorizer = None
    
    def vectorize(self, texts, return_array=False):
        """
        Vectorize a collection of texts.
        
        Parameters
        ----------
        texts : list of str or pandas.Series
            The texts to vectorize.
        
        return_array : bool, default=False
            Whether to return a numpy array instead of a sparse matrix.
        
        Returns
        -------
        vectors : scipy.sparse.csr_matrix or numpy.ndarray
            The vectorized texts.
        """
        # Handle pandas Series
        if isinstance(texts, pd.Series):
            texts = texts.fillna("").tolist()
        
        # Handle None/NaN values
        texts = [t if t else "" for t in texts]
        
        # Use different vectorization methods
        if self.method == 'tfidf':
            self.vectorizer = TfidfVectorizer(max_features=5000)
            vectors = self.vectorizer.fit_transform(texts)
            
        elif self.method == 'count':
            self.vectorizer = CountVectorizer(max_features=5000)
            vectors = self.vectorizer.fit_transform(texts)
            
        elif self.method == 'bert':
            try:
                from sentence_transformers import SentenceTransformer
                model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                vectors = model.encode(texts)
                return vectors  # Always returns numpy array
                
            except ImportError:
                self.logger.warning("Sentence Transformers not installed. Falling back to TF-IDF.")
                self.vectorizer = TfidfVectorizer(max_features=5000)
                vectors = self.vectorizer.fit_transform(texts)
        
        else:
            raise ValueError(f"Unknown vectorization method: {self.method}")
        
        # Convert to array if requested
        if return_array and hasattr(vectors, 'toarray'):
            return vectors.toarray()
        
        return vectors
    
    def get_features(self):
        """
        Get the feature names from the vectorizer.
        
        Returns
        -------
        list of str
            The feature names.
        """
        if hasattr(self.vectorizer, 'get_feature_names_out'):
            return self.vectorizer.get_feature_names_out()
        elif hasattr(self.vectorizer, 'get_feature_names'):
            return self.vectorizer.get_feature_names()
        else:
            return None
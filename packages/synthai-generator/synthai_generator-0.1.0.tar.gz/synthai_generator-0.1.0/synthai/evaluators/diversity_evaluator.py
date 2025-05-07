"""
Evaluator for measuring diversity in synthetic data.
"""
import logging
from typing import Dict, List, Any, Union, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

try:
    from sklearn.metrics import pairwise_distances
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from synthai.core.base import BaseEvaluator

logger = logging.getLogger(__name__)


class DiversityEvaluator(BaseEvaluator):
    """Evaluator for measuring diversity in synthetic data."""
    
    def __init__(self, metric: str = "cosine", **kwargs):
        """Initialize the diversity evaluator.
        
        Args:
            metric: Distance metric to use for diversity calculation.
                Options: 'cosine', 'euclidean', 'manhattan', etc.
            **kwargs: Additional parameters for the distance metric.
        """
        super().__init__(**kwargs)
        
        if not HAS_SKLEARN:
            raise ImportError(
                "scikit-learn package is required for DiversityEvaluator. "
                "Please install it with `pip install scikit-learn`."
            )
        
        self.metric = metric
        self.kwargs = kwargs
    
    def _preprocess_text_data(self, data: List[str]) -> np.ndarray:
        """Preprocess text data for diversity analysis.
        
        Args:
            data: List of text strings.
            
        Returns:
            NumPy array of TF-IDF features.
        """
        vectorizer = TfidfVectorizer(
            max_features=1000,
            min_df=2,
            stop_words="english",
            **self.kwargs.get("tfidf_params", {})
        )
        
        try:
            features = vectorizer.fit_transform(data)
            return features
        except Exception as e:
            logger.warning(f"Error in text preprocessing: {str(e)}")
            # Fallback to simple bag of words if TF-IDF fails
            from collections import Counter
            word_counts = [Counter(text.split()) for text in data]
            all_words = sorted(set().union(*word_counts))
            features = np.zeros((len(data), len(all_words)))
            
            for i, counts in enumerate(word_counts):
                for j, word in enumerate(all_words):
                    features[i, j] = counts.get(word, 0)
                    
            return features
    
    def _preprocess_tabular_data(self, data: pd.DataFrame) -> np.ndarray:
        """Preprocess tabular data for diversity analysis.
        
        Args:
            data: DataFrame of tabular data.
            
        Returns:
            NumPy array of preprocessed features.
        """
        # Handle categorical features
        categorical_cols = data.select_dtypes(include=["object", "category"]).columns
        numerical_cols = data.select_dtypes(include=["number"]).columns
        
        processed_data = data.copy()
        
        # One-hot encode categorical columns
        if not categorical_cols.empty:
            processed_data = pd.get_dummies(processed_data, columns=categorical_cols, dtype=float)
            
        # Scale numerical columns
        if not numerical_cols.empty:
            scaler = StandardScaler()
            processed_data[numerical_cols] = scaler.fit_transform(processed_data[numerical_cols])
            
        return processed_data.values
    
    def _calculate_diversity_score(self, features: np.ndarray) -> Dict[str, float]:
        """Calculate diversity metrics from feature matrix.
        
        Args:
            features: Feature matrix of data points.
            
        Returns:
            Dictionary of diversity metrics.
        """
        if features.shape[0] <= 1:
            return {
                "diversity_score": 0.0,
                "avg_pairwise_distance": 0.0,
                "min_pairwise_distance": 0.0,
                "max_pairwise_distance": 0.0,
                "std_pairwise_distance": 0.0
            }
        
        # Calculate pairwise distances
        distances = pairwise_distances(features, metric=self.metric)
        
        # Extract upper triangle (excluding diagonal)
        triu_indices = np.triu_indices(distances.shape[0], k=1)
        pairwise_distances_array = distances[triu_indices]
        
        # Calculate diversity metrics
        avg_distance = np.mean(pairwise_distances_array)
        min_distance = np.min(pairwise_distances_array)
        max_distance = np.max(pairwise_distances_array)
        std_distance = np.std(pairwise_distances_array)
        
        # Normalize diversity score to 0-1 range
        # Higher values mean more diverse data
        if self.metric == "cosine":
            # For cosine distances, normalize to 0-1
            diversity_score = avg_distance
        else:
            # For other metrics, normalize using min-max
            diversity_score = avg_distance / max_distance if max_distance > 0 else 0.0
        
        return {
            "diversity_score": float(diversity_score),
            "avg_pairwise_distance": float(avg_distance),
            "min_pairwise_distance": float(min_distance),
            "max_pairwise_distance": float(max_distance),
            "std_pairwise_distance": float(std_distance)
        }
    
    def evaluate(self, data: Union[List[str], pd.DataFrame]) -> Dict[str, float]:
        """Evaluate diversity of synthetic data.
        
        Args:
            data: Synthetic data to evaluate, either as list of strings or DataFrame.
            
        Returns:
            Dictionary of diversity metrics.
        """
        if isinstance(data, list) and all(isinstance(item, str) for item in data):
            # Text data
            features = self._preprocess_text_data(data)
        elif isinstance(data, pd.DataFrame):
            # Tabular data
            features = self._preprocess_tabular_data(data)
        else:
            raise ValueError("Unsupported data format. Expected list of strings or DataFrame.")
        
        return self._calculate_diversity_score(features)
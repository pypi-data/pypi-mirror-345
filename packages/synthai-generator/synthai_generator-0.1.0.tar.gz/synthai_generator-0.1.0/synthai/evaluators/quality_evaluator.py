"""
Evaluator for measuring quality in synthetic data.
"""
import logging
from typing import Dict, List, Any, Union, Optional
import numpy as np
import pandas as pd
from collections import Counter

try:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import IsolationForest
    from sklearn.metrics import silhouette_score
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

from synthai.core.base import BaseEvaluator

logger = logging.getLogger(__name__)


class QualityEvaluator(BaseEvaluator):
    """Evaluator for measuring quality metrics of synthetic data."""
    
    def __init__(
        self, 
        metrics: List[str] = None,
        reference_data: Optional[Union[pd.DataFrame, List[str]]] = None,
        **kwargs
    ):
        """Initialize the quality evaluator.
        
        Args:
            metrics: List of quality metrics to calculate. If None, all metrics are calculated.
                Options for text: 'coherence', 'fluency', 'bias', 'toxicity'
                Options for tabular: 'outliers', 'completeness', 'consistency'
            reference_data: Reference data to compare synthetic data against (for distributional similarity).
            **kwargs: Additional parameters for specific metrics.
        """
        super().__init__(**kwargs)
        
        if metrics is None:
            # Default metrics
            self.metrics = {
                "text": ["coherence", "fluency"],
                "tabular": ["outliers", "completeness", "consistency"]
            }
        else:
            text_metrics = [m for m in metrics if m in ["coherence", "fluency", "bias", "toxicity"]]
            tabular_metrics = [m for m in metrics if m in ["outliers", "completeness", "consistency"]]
            self.metrics = {
                "text": text_metrics,
                "tabular": tabular_metrics
            }
            
        self.reference_data = reference_data
        
        # Only initialize NLP models if text metrics are requested
        self.nlp_models = {}
        if self.metrics["text"] and HAS_TRANSFORMERS:
            if "coherence" in self.metrics["text"] or "fluency" in self.metrics["text"]:
                try:
                    model_name = kwargs.get("fluency_model", "distilbert-base-uncased")
                    self.nlp_models["fluency"] = {
                        "tokenizer": AutoTokenizer.from_pretrained(model_name),
                        "model": None  # Lazy loading to save resources
                    }
                except Exception as e:
                    logger.warning(f"Failed to load fluency model: {str(e)}")
    
    def _evaluate_text_coherence(self, texts: List[str]) -> float:
        """Evaluate coherence of text data.
        
        Args:
            texts: List of text strings.
            
        Returns:
            Coherence score from 0 to 1.
        """
        if not HAS_TRANSFORMERS:
            logger.warning("Transformers package not available. Using simpler coherence metric.")
            # Simple heuristic: sentence count, word count ratios
            coherence_scores = []
            
            for text in texts:
                sentences = text.split('. ')
                if len(sentences) <= 1:
                    coherence_scores.append(0.5)  # Neutral score for single sentences
                    continue
                
                # Count words per sentence
                word_counts = [len(s.split()) for s in sentences]
                
                # Variance in sentence length (lower is better)
                variance = np.var(word_counts) / (np.mean(word_counts) + 1e-10)
                normalized_variance = min(1.0, max(0.0, 1.0 - (variance / 10.0)))
                
                # Sentence transition words (simple approximation)
                transition_words = ['however', 'therefore', 'thus', 'consequently', 
                                  'furthermore', 'moreover', 'nevertheless', 'in addition',
                                  'finally', 'in conclusion']
                
                transition_count = sum(1 for word in transition_words 
                                     if any(word in s.lower() for s in sentences))
                transition_score = min(1.0, transition_count / max(1, len(sentences) - 1))
                
                coherence_scores.append(0.5 * normalized_variance + 0.5 * transition_score)
            
            return float(np.mean(coherence_scores))
        
        # More sophisticated approach using perplexity from language model
        # This is a placeholder for more advanced implementations
        return 0.75  # Placeholder value
    
    def _evaluate_text_fluency(self, texts: List[str]) -> float:
        """Evaluate fluency of text data.
        
        Args:
            texts: List of text strings.
            
        Returns:
            Fluency score from 0 to 1.
        """
        if not HAS_TRANSFORMERS:
            logger.warning("Transformers package not available. Using simpler fluency metric.")
            # Simple heuristics: grammar indicators
            fluency_scores = []
            
            for text in texts:
                words = text.split()
                if not words:
                    fluency_scores.append(0)
                    continue
                
                # Check for repeated words (lower is better)
                word_counts = Counter(words)
                repetition_ratio = 1.0 - (len(word_counts) / len(words))
                
                # Check average word length (extremely short/long words may indicate issues)
                avg_word_len = np.mean([len(w) for w in words])
                word_len_score = min(1.0, max(0.0, 1.0 - abs((avg_word_len - 5.0) / 5.0)))
                
                # Check for sentence fragments and punctuation
                has_period = '.' in text
                sentence_count = text.count('. ') + text.count('! ') + text.count('? ')
                expected_sentences = max(1, len(text) / 100)
                sentence_ratio = min(1.0, sentence_count / expected_sentences)
                
                fluency_scores.append(0.4 * (1 - repetition_ratio) + 
                                     0.4 * word_len_score + 
                                     0.2 * (has_period * sentence_ratio))
            
            return float(np.mean(fluency_scores))
            
        # Use language model for more accurate fluency assessment
        # This is a placeholder for more advanced implementations
        return 0.8  # Placeholder value
    
    def _evaluate_tabular_outliers(self, data: pd.DataFrame) -> float:
        """Evaluate outlier ratio in tabular data.
        
        Args:
            data: DataFrame of tabular data.
            
        Returns:
            Outlier quality score from 0 to 1.
        """
        if not HAS_SKLEARN or len(data) < 10:
            logger.warning("Sklearn not available or insufficient data. Using simple outlier check.")
            # Simple outlier detection using z-score
            outlier_scores = []
            
            numeric_cols = data.select_dtypes(include=['number']).columns
            for col in numeric_cols:
                values = data[col].values
                if len(values) <= 1:
                    continue
                    
                mean, std = np.mean(values), np.std(values)
                if std == 0:
                    continue
                    
                z_scores = np.abs((values - mean) / std)
                outlier_ratio = np.mean(z_scores > 3)
                outlier_scores.append(1.0 - min(1.0, outlier_ratio * 10))
            
            return float(np.mean(outlier_scores)) if outlier_scores else 0.5
        
        # Use Isolation Forest for outlier detection
        numeric_data = data.select_dtypes(include=['number'])
        if numeric_data.empty:
            return 0.5  # Neutral score if no numeric data
            
        try:
            # Scale the data
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            
            # Fit Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            outliers = iso_forest.fit_predict(scaled_data)
            
            # Calculate ratio of inliers
            inlier_ratio = np.mean(outliers == 1)
            
            # Score is higher when more data points are inliers
            return float(inlier_ratio)
        except Exception as e:
            logger.warning(f"Error in outlier detection: {str(e)}")
            return 0.5
    
    def _evaluate_tabular_completeness(self, data: pd.DataFrame) -> float:
        """Evaluate completeness/missingness of tabular data.
        
        Args:
            data: DataFrame of tabular data.
            
        Returns:
            Completeness score from 0 to 1.
        """
        # Check for missing values
        missing_ratio = data.isnull().mean().mean()
        completeness = 1.0 - missing_ratio
        
        return float(completeness)
    
    def _evaluate_tabular_consistency(self, data: pd.DataFrame) -> float:
        """Evaluate internal consistency of tabular data.
        
        Args:
            data: DataFrame of tabular data.
            
        Returns:
            Consistency score from 0 to 1.
        """
        # This is a placeholder for more advanced consistency checking
        # For instance, checking that:
        # - Dates are in logical order
        # - Categorical values match allowed values
        # - Numeric values are within expected ranges
        
        # Simple check: are there any completely constant columns?
        constant_cols = 0
        for col in data.columns:
            if data[col].nunique() == 1:
                constant_cols += 1
                
        constant_ratio = constant_cols / max(1, len(data.columns))
        consistency_score = max(0, 1.0 - constant_ratio)
        
        # If we have a reference data, compare distributions
        if self.reference_data is not None and isinstance(self.reference_data, pd.DataFrame):
            # Check for shared columns
            shared_cols = set(data.columns).intersection(set(self.reference_data.columns))
            if shared_cols:
                dist_scores = []
                
                for col in shared_cols:
                    if data[col].dtype != self.reference_data[col].dtype:
                        continue
                        
                    if pd.api.types.is_numeric_dtype(data[col]):
                        # Compare means and stds for numeric columns
                        syn_mean, syn_std = data[col].mean(), data[col].std()
                        ref_mean, ref_std = self.reference_data[col].mean(), self.reference_data[col].std()
                        
                        if ref_std == 0 or syn_std == 0:
                            continue
                            
                        mean_diff = abs(syn_mean - ref_mean) / max(1e-10, ref_mean)
                        std_diff = abs(syn_std - ref_std) / max(1e-10, ref_std)
                        
                        col_score = 1.0 - min(1.0, (mean_diff + std_diff) / 2)
                        dist_scores.append(col_score)
                    else:
                        # Compare distributions for categorical columns
                        syn_counts = data[col].value_counts(normalize=True).to_dict()
                        ref_counts = self.reference_data[col].value_counts(normalize=True).to_dict()
                        
                        # Calculate Jensen-Shannon distance
                        all_cats = set(syn_counts.keys()).union(set(ref_counts.keys()))
                        syn_dist = np.array([syn_counts.get(cat, 0) for cat in all_cats])
                        ref_dist = np.array([ref_counts.get(cat, 0) for cat in all_cats])
                        
                        # Normalize
                        syn_dist = syn_dist / np.sum(syn_dist)
                        ref_dist = ref_dist / np.sum(ref_dist)
                        
                        # Calculate distance
                        m_dist = (syn_dist + ref_dist) / 2
                        js_dist = 0.5 * (np.sum(syn_dist * np.log(syn_dist / m_dist + 1e-10)) +
                                        np.sum(ref_dist * np.log(ref_dist / m_dist + 1e-10)))
                        
                        col_score = 1.0 - min(1.0, js_dist)
                        dist_scores.append(col_score)
                
                if dist_scores:
                    # Combine with basic consistency score
                    return float(0.5 * consistency_score + 0.5 * np.mean(dist_scores))
        
        return float(consistency_score)
    
    def evaluate(self, data: Union[List[str], pd.DataFrame]) -> Dict[str, float]:
        """Evaluate quality of synthetic data.
        
        Args:
            data: Synthetic data to evaluate, either as list of strings or DataFrame.
            
        Returns:
            Dictionary of quality metrics.
        """
        results = {}
        
        if isinstance(data, list) and all(isinstance(item, str) for item in data):
            # Text data
            if "coherence" in self.metrics["text"]:
                results["coherence"] = self._evaluate_text_coherence(data)
                
            if "fluency" in self.metrics["text"]:
                results["fluency"] = self._evaluate_text_fluency(data)
                
            # Calculate average quality score
            text_scores = [v for k, v in results.items() if k in self.metrics["text"]]
            if text_scores:
                results["quality_score"] = float(np.mean(text_scores))
            else:
                results["quality_score"] = 0.5  # Neutral score
                
        elif isinstance(data, pd.DataFrame):
            # Tabular data
            if "outliers" in self.metrics["tabular"]:
                results["outliers_score"] = self._evaluate_tabular_outliers(data)
                
            if "completeness" in self.metrics["tabular"]:
                results["completeness"] = self._evaluate_tabular_completeness(data)
                
            if "consistency" in self.metrics["tabular"]:
                results["consistency"] = self._evaluate_tabular_consistency(data)
                
            # Calculate average quality score
            tabular_scores = [v for k, v in results.items()]
            if tabular_scores:
                results["quality_score"] = float(np.mean(tabular_scores))
            else:
                results["quality_score"] = 0.5  # Neutral score
        else:
            raise ValueError("Unsupported data format. Expected list of strings or DataFrame.")
        
        return results
"""
Base classes for synthetic data generation.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import pandas as pd
import numpy as np

from synthai.core.config import GenerationConfig


class BaseGenerator(ABC):
    """Abstract base class for all synthetic data generators."""
    
    def __init__(self, model_name: str = None, **kwargs):
        """Initialize generator.
        
        Args:
            model_name: Name or path of the model to use.
            **kwargs: Additional generator-specific parameters.
        """
        self.model_name = model_name
        self.model = None
        self.kwargs = kwargs
        
    @abstractmethod
    def load_model(self) -> Any:
        """Load and return the generation model."""
        pass
    
    @abstractmethod
    def generate(self, config: GenerationConfig) -> Union[pd.DataFrame, List[str], np.ndarray]:
        """Generate synthetic data based on provided configuration.
        
        Args:
            config: Configuration for data generation.
        
        Returns:
            Generated synthetic data as DataFrame, list, or numpy array.
        """
        pass
    
    @abstractmethod
    def enhance_diversity(self, data: Any, diversity_factor: float) -> Any:
        """Enhance diversity in the generated data.
        
        Args:
            data: Generated data.
            diversity_factor: Factor controlling diversity enhancement (0-1).
            
        Returns:
            Data with enhanced diversity.
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Any) -> bool:
        """Validate generated data.
        
        Args:
            data: Generated data to validate.
            
        Returns:
            True if data is valid, False otherwise.
        """
        pass


class BaseEvaluator(ABC):
    """Abstract base class for synthetic data evaluators."""
    
    def __init__(self, **kwargs):
        """Initialize evaluator."""
        self.kwargs = kwargs
    
    @abstractmethod
    def evaluate(self, data: Any) -> Dict[str, float]:
        """Evaluate synthetic data quality.
        
        Args:
            data: Generated synthetic data to evaluate.
            
        Returns:
            Dictionary of evaluation metrics.
        """
        pass
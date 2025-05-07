"""
Main synthetic data generator implementation.
"""
import os
import json
import logging
import random
from typing import Dict, List, Any, Optional, Union, Type
import pandas as pd
import numpy as np
from string import Formatter

from synthai.core.base import BaseGenerator
from synthai.core.config import GenerationConfig

logger = logging.getLogger(__name__)


class SyntheticDataGenerator:
    """Main class for generating synthetic data using various generator types."""
    
    def __init__(
        self, 
        generator_type: Optional[BaseGenerator] = None, 
        domain: str = "generic",
        seed: Optional[int] = None
    ):
        """Initialize the synthetic data generator.
        
        Args:
            generator_type: Instance of a generator class derived from BaseGenerator.
            domain: Domain of the synthetic data (e.g., 'customer_reviews', 'medical_notes').
            seed: Random seed for reproducibility.
        """
        self.generator = generator_type
        self.domain = domain
        
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            self.seed = seed
        else:
            self.seed = None
    
    def generate(
        self, 
        num_samples: int = 100,
        prompt_template: str = "", 
        parameters: Optional[Dict[str, List[str]]] = None,
        max_length: int = 256,
        temperature: float = 0.7,
        diversity_factor: float = 0.8,
        **kwargs
    ) -> Union[pd.DataFrame, List[str]]:
        """Generate synthetic data.
        
        Args:
            num_samples: Number of data samples to generate.
            prompt_template: Template string for generation with placeholders for parameters.
            parameters: Dictionary mapping parameter names to possible values.
            max_length: Maximum length of generated text.
            temperature: Controls randomness in generation.
            diversity_factor: Controls how diverse the generated samples should be.
            **kwargs: Additional generation parameters.
            
        Returns:
            Generated synthetic data as DataFrame or list.
        """
        if self.generator is None:
            raise ValueError("No generator specified. Please provide a generator when initializing.")
            
        if parameters is None:
            parameters = {}
            
        # Get all field names from the prompt template
        field_names = [fname for _, fname, _, _ in Formatter().parse(prompt_template) if fname]
        
        # Ensure all field names in the prompt template are in the parameters
        missing_params = [f for f in field_names if f not in parameters]
        if missing_params:
            raise ValueError(f"Missing parameters in prompt template: {missing_params}")
        
        # Create configuration
        config = GenerationConfig(
            num_samples=num_samples,
            domain=self.domain,
            prompt_template=prompt_template,
            parameters=parameters,
            max_length=max_length,
            temperature=temperature,
            diversity_factor=diversity_factor,
            seed=self.seed,
            metadata=kwargs
        )
        
        # Generate data
        logger.info(f"Generating {num_samples} synthetic samples for domain: {self.domain}")
        data = self.generator.generate(config)
        
        return data
        
    def save_data(
        self, 
        data: Union[pd.DataFrame, List[str], np.ndarray],
        output_path: str,
        format: str = None
    ) -> None:
        """Save generated data to file.
        
        Args:
            data: Generated data to save.
            output_path: Path to save the data.
            format: Format to save data in. If None, will be inferred from output_path extension.
        """
        if format is None:
            _, ext = os.path.splitext(output_path)
            format = ext.lstrip('.').lower()
            
        directory = os.path.dirname(output_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        if isinstance(data, pd.DataFrame):
            if format == 'csv':
                data.to_csv(output_path, index=False)
            elif format == 'json':
                data.to_json(output_path, orient='records')
            elif format == 'parquet':
                data.to_parquet(output_path, index=False)
            else:
                data.to_csv(output_path, index=False)
        elif isinstance(data, list) and all(isinstance(item, str) for item in data):
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(f"{item}\n")
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        elif isinstance(data, np.ndarray):
            np.save(output_path, data)
        else:
            raise TypeError(f"Unsupported data type for saving: {type(data)}")
            
        logger.info(f"Data saved to {output_path}")
        
    def load_data(self, input_path: str) -> Union[pd.DataFrame, List[str], np.ndarray]:
        """Load synthetic data from file.
        
        Args:
            input_path: Path to load data from.
            
        Returns:
            Loaded synthetic data.
        """
        _, ext = os.path.splitext(input_path)
        format = ext.lstrip('.').lower()
        
        if format == 'csv':
            return pd.read_csv(input_path)
        elif format == 'json':
            return pd.read_json(input_path, orient='records')
        elif format == 'parquet':
            return pd.read_parquet(input_path)
        elif format == 'npy':
            return np.load(input_path)
        elif format in ('txt', 'text'):
            with open(input_path, 'r', encoding='utf-8') as f:
                return f.read().splitlines()
        else:
            raise ValueError(f"Unsupported file format: {format}")
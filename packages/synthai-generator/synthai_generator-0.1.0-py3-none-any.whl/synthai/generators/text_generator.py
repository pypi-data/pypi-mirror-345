"""
Text-based synthetic data generator implementation using language models.
"""
import random
import logging
from typing import List, Dict, Any, Union, Optional
import pandas as pd
import numpy as np

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

from synthai.core.base import BaseGenerator
from synthai.core.config import GenerationConfig

logger = logging.getLogger(__name__)


class TextGenerator(BaseGenerator):
    """Text generator using Hugging Face transformers."""
    
    def __init__(
        self, 
        model: str = "distilgpt2",
        device: str = None,
        **kwargs
    ):
        """Initialize text generator.
        
        Args:
            model: Model name or path from Hugging Face.
            device: Device to run inference on ('cpu', 'cuda', None for auto-detection).
            **kwargs: Additional model-specific parameters.
        """
        super().__init__(model_name=model, **kwargs)
        
        if not HAS_TRANSFORMERS:
            raise ImportError(
                "Transformers package is required for TextGenerator. "
                "Please install it with `pip install transformers`."
            )
        
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        self.tokenizer = None
        self.model = None
        
    def load_model(self) -> Any:
        """Load the language model and tokenizer."""
        logger.info(f"Loading model: {self.model_name}")
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
        
        self.tokenizer = tokenizer
        self.model = model
        return model
    
    def _fill_template(self, template: str, parameters: Dict[str, List[str]]) -> str:
        """Fill a template with randomly selected parameters.
        
        Args:
            template: Template string with {parameter} placeholders.
            parameters: Dictionary of parameter names and possible values.
            
        Returns:
            Filled template string.
        """
        param_values = {}
        for param_name, values in parameters.items():
            param_values[param_name] = random.choice(values)
            
        return template.format(**param_values)
    
    def generate(self, config: GenerationConfig) -> List[str]:
        """Generate synthetic text data.
        
        Args:
            config: Configuration for data generation.
            
        Returns:
            List of generated text samples.
        """
        if self.model is None:
            self.load_model()
            
        # Set seed for reproducibility if provided
        if config.seed is not None:
            set_seed(config.seed)
            
        generated_texts = []
        prompt_parameters = pd.DataFrame({
            k: np.random.choice(v, config.num_samples) 
            for k, v in config.parameters.items()
        }) if config.parameters else None
        
        for i in range(config.num_samples):
            # Create prompt by filling template with parameters
            if prompt_parameters is not None:
                param_values = {k: prompt_parameters.iloc[i][k] for k in prompt_parameters.columns}
                prompt = config.prompt_template.format(**param_values)
            else:
                prompt = config.prompt_template
                
            # Tokenize prompt
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate text
            outputs = self.model.generate(
                **inputs,
                max_length=config.max_length,
                temperature=config.temperature,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                num_return_sequences=1,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            # Decode and append result
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the original prompt from the output if it appears at the beginning
            if prompt and generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
                
            generated_texts.append(generated_text)
            
        # Enhance diversity if requested
        if config.diversity_factor > 0:
            generated_texts = self.enhance_diversity(generated_texts, config.diversity_factor)
            
        return generated_texts
    
    def enhance_diversity(self, texts: List[str], diversity_factor: float) -> List[str]:
        """Enhance diversity in generated texts.
        
        Uses techniques to reduce repetition and increase semantic diversity.
        
        Args:
            texts: List of generated texts.
            diversity_factor: Factor to control diversity enhancement (0-1).
            
        Returns:
            Texts with enhanced diversity.
        """
        if diversity_factor <= 0:
            return texts
            
        # This is a simple implementation that could be expanded with more
        # sophisticated techniques in a production version
        enhanced_texts = []
        unique_texts = set()
        
        for text in texts:
            if text in unique_texts and random.random() < diversity_factor:
                # Generate a new text with higher temperature
                if self.model is not None:
                    inputs = self.tokenizer(text.split()[:5], return_tensors="pt").to(self.device)
                    outputs = self.model.generate(
                        **inputs,
                        max_length=len(text.split()) + 10,
                        temperature=min(1.0, 0.8 + diversity_factor * 0.4),
                        do_sample=True,
                        top_k=40,
                        top_p=0.98,
                        num_return_sequences=1
                    )
                    new_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                    enhanced_texts.append(new_text)
                    unique_texts.add(new_text)
            else:
                enhanced_texts.append(text)
                unique_texts.add(text)
                
        return enhanced_texts
    
    def validate_data(self, texts: List[str]) -> bool:
        """Validate generated texts.
        
        Args:
            texts: List of generated texts.
            
        Returns:
            True if texts are valid, False otherwise.
        """
        if not texts:
            return False
            
        # Check for empty texts
        if any(not text.strip() for text in texts):
            return False
            
        # Additional validation could be implemented here
        return True
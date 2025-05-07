"""
Configuration classes for synthetic data generation.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any


@dataclass
class GenerationConfig:
    """Configuration class for synthetic data generation.
    
    Attributes:
        num_samples: Number of data samples to generate.
        domain: Domain of the synthetic data (e.g., 'customer_reviews', 'medical_notes').
        prompt_template: Template string for generation with placeholders for parameters.
        parameters: Dictionary mapping parameter names to possible values.
        max_length: Maximum length of generated text (for text generation).
        temperature: Controls randomness in generation (higher = more random).
        diversity_factor: Controls how diverse the generated samples should be (0-1).
        seed: Random seed for reproducibility.
        metadata: Optional additional configuration parameters.
    """
    num_samples: int = 100
    domain: str = "generic"
    prompt_template: str = ""
    parameters: Dict[str, List[str]] = field(default_factory=dict)
    max_length: int = 256
    temperature: float = 0.7
    diversity_factor: float = 0.8
    seed: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.num_samples <= 0:
            raise ValueError("num_samples must be greater than 0")
        
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError("temperature must be between 0 and 1")
        
        if self.diversity_factor < 0 or self.diversity_factor > 1:
            raise ValueError("diversity_factor must be between 0 and 1")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "num_samples": self.num_samples,
            "domain": self.domain,
            "prompt_template": self.prompt_template,
            "parameters": self.parameters,
            "max_length": self.max_length,
            "temperature": self.temperature,
            "diversity_factor": self.diversity_factor,
            "seed": self.seed,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'GenerationConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)
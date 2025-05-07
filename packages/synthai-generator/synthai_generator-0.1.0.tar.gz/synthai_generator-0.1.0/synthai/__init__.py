"""
SynthAI: A framework for generating synthetic data using LLMs with techniques to ensure diversity and reduce bias.
"""

__version__ = "0.1.0"

from synthai.core.generator import SyntheticDataGenerator
from synthai.core.config import GenerationConfig

__all__ = [
    "SyntheticDataGenerator",
    "GenerationConfig"
]
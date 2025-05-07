# SynthAI: Synthetic Data Generation Framework

[![PyPI version](https://img.shields.io/pypi/v/synthai.svg)](https://pypi.org/project/synthai/)
[![Python Version](https://img.shields.io/pypi/pyversions/synthai.svg)](https://pypi.org/project/synthai/)
[![License](https://img.shields.io/github/license/biswanathroul/synthai.svg)](https://github.com/biswanathroul/synthai/blob/main/LICENSE)

SynthAI is a lightweight framework for generating high-quality synthetic data using LLMs with techniques to ensure diversity and reduce bias.

## Features

- 🤖 **LLM-Powered Generation**: Create realistic synthetic data using language models
- 🧩 **Domain Adapters**: Specialized components for different data domains (text, tabular, time-series)
- 🔄 **Diversity Enhancement**: Built-in techniques to increase diversity in generated data
- ⚖️ **Bias Reduction**: Methods to detect and mitigate bias in synthetic datasets
- 📊 **Quality Evaluation**: Tools to measure the quality and utility of generated data
- 🚀 **Resource Efficiency**: Optimized to work with lighter models and minimal compute requirements

## Installation

```bash
pip install synthai
```

## Quick Start

```python
from synthai import SyntheticDataGenerator
from synthai.generators import TextGenerator
from synthai.evaluators import DiversityEvaluator

# Initialize a generator
generator = SyntheticDataGenerator(
    generator_type=TextGenerator(model="distilgpt2"),
    domain="customer_reviews"
)

# Generate synthetic data
synthetic_data = generator.generate(
    num_samples=100,
    prompt_template="Write a {sentiment} review for a {product_type}",
    parameters={
        "sentiment": ["positive", "negative", "neutral"],
        "product_type": ["smartphone", "laptop", "headphones"]
    }
)

# Evaluate diversity of the generated data
evaluator = DiversityEvaluator()
diversity_score = evaluator.evaluate(synthetic_data)
print(f"Diversity score: {diversity_score}")

# Save the generated data
generator.save_data(synthetic_data, "synthetic_reviews.csv")
```

## Documentation

For full documentation, visit [synthai.readthedocs.io](https://synthai.readthedocs.io).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- **Biswanath Roul** - [GitHub](https://github.com/biswanathroul)

## Acknowledgments

Special thanks to the open-source community and the advancements in LLM technology that make this library possible.
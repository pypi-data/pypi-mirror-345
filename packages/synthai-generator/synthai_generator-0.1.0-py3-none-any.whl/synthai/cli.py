#!/usr/bin/env python
"""
Command Line Interface for SynthAI.

This module provides a command-line interface for generating synthetic data using SynthAI.
"""

import argparse
import json
import os
import sys
import logging
from typing import Dict, Any, Optional
import pandas as pd

# Fix imports to use direct module paths
from synthai.core.generator import SyntheticDataGenerator
from synthai.core.config import GenerationConfig
from synthai.generators.text_generator import TextGenerator
from synthai.generators.tabular_generator import TabularGenerator
from synthai.evaluators.diversity_evaluator import DiversityEvaluator
from synthai.evaluators.quality_evaluator import QualityEvaluator
from synthai.utils import setup_logging

logger = logging.getLogger("synthai.cli")


def parse_args():
    """Parse command line arguments.
    
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="SynthAI - Generate synthetic data using LLMs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--mode", 
        type=str, 
        choices=["text", "tabular"], 
        default="text",
        help="Generation mode: text or tabular data"
    )
    
    parser.add_argument(
        "--model", 
        type=str, 
        default="distilgpt2",
        help="Model to use for generation. Use 'synthetic' for non-LLM tabular generation."
    )
    
    parser.add_argument(
        "--num-samples", 
        type=int, 
        default=10,
        help="Number of samples to generate"
    )
    
    parser.add_argument(
        "--prompt-template", 
        type=str, 
        default="",
        help="Template string for text generation with {placeholders}"
    )
    
    parser.add_argument(
        "--parameters", 
        type=str, 
        default="{}",
        help="JSON string or path to JSON file with parameter values for prompt template"
    )
    
    parser.add_argument(
        "--schema", 
        type=str, 
        default="{}",
        help="JSON string or path to JSON file with schema for tabular data"
    )
    
    parser.add_argument(
        "--diversity", 
        type=float, 
        default=0.7,
        help="Diversity factor for generation (0-1)"
    )
    
    parser.add_argument(
        "--temperature", 
        type=float, 
        default=0.8,
        help="Temperature for LLM generation (0-1)"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        default="synthetic_data",
        help="Output file path without extension"
    )
    
    parser.add_argument(
        "--format", 
        type=str,
        choices=["csv", "json", "txt", "parquet"], 
        default="csv",
        help="Output file format"
    )
    
    parser.add_argument(
        "--evaluate", 
        action="store_true",
        help="Evaluate the generated data"
    )
    
    parser.add_argument(
        "--seed", 
        type=int, 
        default=None,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def load_json_config(config_str: str) -> Dict[str, Any]:
    """Load JSON configuration from string or file.
    
    Args:
        config_str: JSON string or path to JSON file.
        
    Returns:
        Parsed JSON as dictionary.
    """
    if os.path.isfile(config_str):
        with open(config_str, "r") as f:
            return json.load(f)
    else:
        try:
            return json.loads(config_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {config_str}")
            return {}


def generate_text(args) -> pd.DataFrame:
    """Generate text data based on command line arguments.
    
    Args:
        args: Parsed command line arguments.
        
    Returns:
        DataFrame with generated data.
    """
    # Load parameters for prompt template
    parameters = load_json_config(args.parameters)
    
    # Initialize generator
    text_generator = TextGenerator(model=args.model)
    
    generator = SyntheticDataGenerator(
        generator_type=text_generator,
        domain="cli_generated",
        seed=args.seed
    )
    
    # Generate text data
    texts = generator.generate(
        num_samples=args.num_samples,
        prompt_template=args.prompt_template,
        parameters=parameters,
        temperature=args.temperature,
        diversity_factor=args.diversity
    )
    
    # Create DataFrame
    df = pd.DataFrame({
        "text": texts,
        "length": [len(text) for text in texts]
    })
    
    return df


def generate_tabular(args) -> pd.DataFrame:
    """Generate tabular data based on command line arguments.
    
    Args:
        args: Parsed command line arguments.
        
    Returns:
        DataFrame with generated data.
    """
    # Load schema for tabular data
    schema = load_json_config(args.schema)
    
    if not schema:
        logger.error("Schema is required for tabular data generation")
        sys.exit(1)
    
    # Initialize generator
    tabular_generator = TabularGenerator(model=args.model, schema=schema)
    
    generator = SyntheticDataGenerator(
        generator_type=tabular_generator,
        domain="cli_generated",
        seed=args.seed
    )
    
    # Generate tabular data
    df = generator.generate(
        num_samples=args.num_samples,
        temperature=args.temperature,
        diversity_factor=args.diversity
    )
    
    return df


def evaluate_data(data, mode: str) -> Dict[str, float]:
    """Evaluate the quality and diversity of generated data.
    
    Args:
        data: Generated data (DataFrame or list of texts).
        mode: Generation mode ("text" or "tabular").
        
    Returns:
        Dictionary with evaluation metrics.
    """
    results = {}
    
    # Evaluate diversity
    diversity_evaluator = DiversityEvaluator()
    diversity_metrics = diversity_evaluator.evaluate(data)
    
    # Evaluate quality
    quality_metrics = {}
    if mode == "text":
        quality_evaluator = QualityEvaluator(metrics=["coherence", "fluency"])
        if isinstance(data, pd.DataFrame) and "text" in data.columns:
            quality_metrics = quality_evaluator.evaluate(data["text"].tolist())
        else:
            quality_metrics = quality_evaluator.evaluate(data)
    else:  # tabular
        quality_evaluator = QualityEvaluator(
            metrics=["outliers", "completeness", "consistency"]
        )
        quality_metrics = quality_evaluator.evaluate(data)
    
    # Combine results
    results.update(diversity_metrics)
    results.update(quality_metrics)
    
    return results


def main():
    """Main entry point for CLI."""
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=log_level)
    
    logger.info(f"Starting SynthAI in {args.mode} mode")
    
    try:
        # Generate data based on mode
        if args.mode == "text":
            data = generate_text(args)
        else:  # tabular
            data = generate_tabular(args)
        
        logger.info(f"Successfully generated {len(data)} samples")
        
        # Evaluate if requested
        if args.evaluate:
            logger.info("Evaluating generated data...")
            metrics = evaluate_data(data, args.mode)
            
            logger.info("Evaluation results:")
            for metric, value in metrics.items():
                logger.info(f"{metric}: {value:.4f}")
        
        # Save the data
        output_path = f"{args.output}.{args.format}"
        
        if args.format == "txt" and args.mode == "text":
            # Save as plain text file
            if isinstance(data, pd.DataFrame) and "text" in data.columns:
                with open(output_path, "w") as f:
                    for text in data["text"]:
                        f.write(f"{text}\n\n")
            else:
                with open(output_path, "w") as f:
                    for text in data:
                        f.write(f"{text}\n\n")
        else:
            # Save as specified format
            if args.format == "csv":
                data.to_csv(output_path, index=False)
            elif args.format == "json":
                data.to_json(output_path, orient="records", indent=2)
            elif args.format == "parquet":
                try:
                    data.to_parquet(output_path, index=False)
                except Exception as e:
                    logger.error(f"Failed to save as parquet: {str(e)}")
                    data.to_csv(f"{args.output}.csv", index=False)
                    logger.info(f"Saved as CSV instead: {args.output}.csv")
        
        logger.info(f"Data saved to {output_path}")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
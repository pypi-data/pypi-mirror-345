"""
Tabular data generator implementation with schema validation.
"""
import random
import string
import logging
from typing import Dict, List, Any, Union, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

from synthai.core.base import BaseGenerator
from synthai.core.config import GenerationConfig

logger = logging.getLogger(__name__)


class TabularGenerator(BaseGenerator):
    """Tabular data generator with schema validation."""
    
    def __init__(
        self, 
        model: str = "synthetic",
        schema: Dict[str, Dict[str, Any]] = None,
        **kwargs
    ):
        """Initialize tabular generator.
        
        Args:
            model: "synthetic" for pure synthetic generation or model name for LLM-based generation.
            schema: Dictionary defining the schema for tabular data.
                Each key is a column name and value is a dictionary of column properties.
                Supported column types: "int", "float", "str", "date", "bool", "category".
                Example: {"age": {"type": "int", "range": (18, 65)}}
            **kwargs: Additional generator-specific parameters.
        """
        super().__init__(model_name=model, **kwargs)
        
        self.schema = schema or {}
        self.model = None
        self.tokenizer = None
        
        # Initialize the LLM if requested (not "synthetic" mode)
        if model != "synthetic" and HAS_TRANSFORMERS:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model)
            except Exception as e:
                logger.warning(f"Failed to load tokenizer: {str(e)}. Falling back to synthetic mode.")
                self.model_name = "synthetic"
    
    def load_model(self) -> Any:
        """Load the generation model if using LLM-based generation."""
        if self.model_name == "synthetic":
            return None
            
        if not HAS_TRANSFORMERS:
            raise ImportError(
                "Transformers package is required for LLM-based generation. "
                "Please install it with `pip install transformers`."
            )
            
        logger.info(f"Loading model: {self.model_name}")
        model = AutoModelForCausalLM.from_pretrained(self.model_name).to(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        
        self.model = model
        return model
    
    def _generate_int_value(self, props: Dict[str, Any]) -> int:
        """Generate an integer value based on schema properties.
        
        Args:
            props: Properties for the integer column.
            
        Returns:
            Generated integer value.
        """
        min_val, max_val = props.get("range", (0, 100))
        distribution = props.get("distribution", "uniform")
        
        if distribution == "uniform":
            return random.randint(min_val, max_val)
        elif distribution == "normal":
            mean = (min_val + max_val) / 2
            std_dev = (max_val - min_val) / 6  # +/- 3 std covers ~99.7%
            value = int(round(random.gauss(mean, std_dev)))
            # Keep value within range
            return max(min_val, min(max_val, value))
        else:
            return random.randint(min_val, max_val)
    
    def _generate_float_value(self, props: Dict[str, Any]) -> float:
        """Generate a float value based on schema properties.
        
        Args:
            props: Properties for the float column.
            
        Returns:
            Generated float value.
        """
        min_val, max_val = props.get("range", (0.0, 1.0))
        distribution = props.get("distribution", "uniform")
        decimals = props.get("decimals", 2)
        
        if distribution == "uniform":
            value = random.uniform(min_val, max_val)
        elif distribution == "normal":
            mean = (min_val + max_val) / 2
            std_dev = (max_val - min_val) / 6
            value = random.gauss(mean, std_dev)
            # Keep value within range
            value = max(min_val, min(max_val, value))
        else:
            value = random.uniform(min_val, max_val)
            
        return round(value, decimals)
    
    def _generate_str_value(self, props: Dict[str, Any], idx: int) -> str:
        """Generate a string value based on schema properties.
        
        Args:
            props: Properties for the string column.
            idx: Index of the current row being generated.
            
        Returns:
            Generated string value.
        """
        templates = props.get("templates", [])
        min_length = props.get("min_length", 5)
        max_length = props.get("max_length", 10)
        
        # Use template if provided
        if templates:
            template = random.choice(templates)
            return template.format(i=idx)
            
        # Generate random string
        length = random.randint(min_length, max_length)
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _generate_date_value(self, props: Dict[str, Any]) -> pd.Timestamp:
        """Generate a date value based on schema properties.
        
        Args:
            props: Properties for the date column.
            
        Returns:
            Generated date value.
        """
        start_date, end_date = props.get(
            "range", 
            (pd.Timestamp("2020-01-01"), pd.Timestamp("2023-12-31"))
        )
        
        if isinstance(start_date, str):
            start_date = pd.Timestamp(start_date)
        if isinstance(end_date, str):
            end_date = pd.Timestamp(end_date)
            
        # Convert to datetime for calculation
        start_dt = datetime.combine(start_date.date(), datetime.min.time())
        end_dt = datetime.combine(end_date.date(), datetime.min.time())
        
        # Calculate the range in days
        delta_days = (end_dt - start_dt).days
        
        # Generate a random number of days to add
        random_days = random.randint(0, max(0, delta_days))
        
        # Create the new date
        random_date = start_dt + timedelta(days=random_days)
        
        return pd.Timestamp(random_date)
    
    def _generate_bool_value(self, props: Dict[str, Any]) -> bool:
        """Generate a boolean value based on schema properties.
        
        Args:
            props: Properties for the boolean column.
            
        Returns:
            Generated boolean value.
        """
        # Probability of True (default 50%)
        p_true = props.get("p_true", 0.5)
        return random.random() < p_true
    
    def _generate_category_value(self, props: Dict[str, Any]) -> str:
        """Generate a categorical value based on schema properties.
        
        Args:
            props: Properties for the categorical column.
            
        Returns:
            Generated categorical value.
        """
        categories = props.get("categories", [])
        weights = props.get("weights", None)
        
        if not categories:
            return None
            
        if weights and len(weights) == len(categories):
            return random.choices(categories, weights=weights, k=1)[0]
        else:
            return random.choice(categories)
    
    def _generate_synthetic_row(self, idx: int) -> Dict[str, Any]:
        """Generate a single row of synthetic data based on the schema.
        
        Args:
            idx: Index of the current row.
            
        Returns:
            Dictionary of column name to generated value.
        """
        row = {}
        
        for col_name, props in self.schema.items():
            col_type = props.get("type", "str").lower()
            
            try:
                if col_type == "int":
                    row[col_name] = self._generate_int_value(props)
                elif col_type == "float":
                    row[col_name] = self._generate_float_value(props)
                elif col_type == "str":
                    row[col_name] = self._generate_str_value(props, idx)
                elif col_type == "date":
                    row[col_name] = self._generate_date_value(props)
                elif col_type == "bool":
                    row[col_name] = self._generate_bool_value(props)
                elif col_type == "category":
                    row[col_name] = self._generate_category_value(props)
                else:
                    logger.warning(f"Unsupported column type: {col_type}. Generating as string.")
                    row[col_name] = self._generate_str_value({}, idx)
            except Exception as e:
                logger.warning(f"Error generating value for {col_name}: {str(e)}")
                row[col_name] = None
                
        return row
    
    def _generate_llm_row(self, prompt: str) -> Dict[str, Any]:
        """Generate a single row of tabular data using LLM.
        
        Args:
            prompt: Prompt to use for LLM generation.
            
        Returns:
            Dictionary of column name to generated value.
        """
        if not self.model:
            self.load_model()
            
        if not self.model:
            logger.warning("LLM model not available, falling back to synthetic generation.")
            return self._generate_synthetic_row(0)
            
        # Generate JSON-like structure from LLM
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        outputs = self.model.generate(
            **inputs,
            max_length=500,
            temperature=0.7,
            do_sample=True,
            top_p=0.95,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract the JSON part (very simple parsing)
        try:
            import json
            
            # Find JSON-like structure
            start = generated_text.find("{")
            end = generated_text.rfind("}")
            
            if start >= 0 and end > start:
                json_str = generated_text[start:end+1]
                row = json.loads(json_str)
                
                # Validate and fix types based on schema
                for col_name, props in self.schema.items():
                    if col_name not in row:
                        # Fill missing values with synthetic data
                        col_type = props.get("type", "str").lower()
                        if col_type == "int":
                            row[col_name] = self._generate_int_value(props)
                        elif col_type == "float":
                            row[col_name] = self._generate_float_value(props)
                        elif col_type == "date":
                            row[col_name] = self._generate_date_value(props)
                        elif col_type == "bool":
                            row[col_name] = self._generate_bool_value(props)
                        elif col_type == "category":
                            row[col_name] = self._generate_category_value(props)
                        else:
                            row[col_name] = self._generate_str_value(props, 0)
                
                return row
        except Exception as e:
            logger.warning(f"Error parsing LLM output: {str(e)}")
        
        # Fallback to synthetic generation
        return self._generate_synthetic_row(0)
    
    def _create_llm_prompt(self) -> str:
        """Create a prompt for the LLM to generate tabular data.
        
        Returns:
            Prompt string for LLM.
        """
        prompt = "Generate a realistic data record in JSON format with the following schema:\n"
        
        for col_name, props in self.schema.items():
            col_type = props.get("type", "str").lower()
            prompt += f"- {col_name}: {col_type}"
            
            if col_type == "int":
                min_val, max_val = props.get("range", (0, 100))
                prompt += f" between {min_val} and {max_val}"
            elif col_type == "float":
                min_val, max_val = props.get("range", (0.0, 1.0))
                prompt += f" between {min_val} and {max_val}"
            elif col_type == "date":
                start_date, end_date = props.get(
                    "range", 
                    (pd.Timestamp("2020-01-01"), pd.Timestamp("2023-12-31"))
                )
                prompt += f" between {start_date} and {end_date}"
            elif col_type == "category":
                categories = props.get("categories", [])
                if categories:
                    prompt += f" from {categories}"
                    
            prompt += "\n"
            
        prompt += "\nReturn only a valid JSON object without explanation."
        return prompt
    
    def generate(self, config: GenerationConfig) -> pd.DataFrame:
        """Generate synthetic tabular data.
        
        Args:
            config: Configuration for data generation.
        
        Returns:
            DataFrame with generated data.
        """
        if not self.schema:
            raise ValueError("Schema is required for tabular data generation.")
            
        # Set seed for reproducibility if provided
        if config.seed is not None:
            random.seed(config.seed)
            np.random.seed(config.seed)
            if HAS_TRANSFORMERS:
                set_seed(config.seed)
                
        # Use LLM-based or pure synthetic generation
        rows = []
        
        if self.model_name != "synthetic" and HAS_TRANSFORMERS:
            # LLM-based generation
            prompt = self._create_llm_prompt()
            
            for i in range(config.num_samples):
                row = self._generate_llm_row(prompt)
                rows.append(row)
        else:
            # Pure synthetic generation
            for i in range(config.num_samples):
                row = self._generate_synthetic_row(i)
                rows.append(row)
                
        # Create DataFrame
        df = pd.DataFrame(rows)
        
        # Enhance diversity if requested
        if config.diversity_factor > 0:
            df = self.enhance_diversity(df, config.diversity_factor)
            
        return df
    
    def enhance_diversity(self, data: pd.DataFrame, diversity_factor: float) -> pd.DataFrame:
        """Enhance diversity in generated tabular data.
        
        Args:
            data: DataFrame of generated data.
            diversity_factor: Factor to control diversity enhancement (0-1).
            
        Returns:
            DataFrame with enhanced diversity.
        """
        if diversity_factor <= 0:
            return data
            
        enhanced_data = data.copy()
        
        # For categorical columns, possibly shift distribution
        for col_name, props in self.schema.items():
            col_type = props.get("type", "").lower()
            
            # Apply diversity enhancement to relevant columns
            if col_type == "category":
                categories = props.get("categories", [])
                if not categories:
                    continue
                    
                weights = props.get("weights", None)
                
                # If column has weights, modify them to increase diversity
                if weights and len(weights) == len(categories):
                    # Make weights more uniform (less skewed)
                    modified_weights = []
                    for w in weights:
                        # Move weight closer to 1/len(categories)
                        avg_weight = 1.0 / len(categories)
                        modified_w = w * (1 - diversity_factor) + avg_weight * diversity_factor
                        modified_weights.append(modified_w)
                    
                    # Normalize weights to sum to 1
                    total = sum(modified_weights)
                    modified_weights = [w / total for w in modified_weights]
                    
                    # Re-sample some values with modified distribution
                    resample_idx = np.random.choice(
                        len(enhanced_data),
                        size=int(len(enhanced_data) * diversity_factor),
                        replace=False
                    )
                    
                    for idx in resample_idx:
                        enhanced_data.at[idx, col_name] = np.random.choice(
                            categories, p=modified_weights
                        )
            
            # For numeric columns, introduce some variation
            elif col_type in ["int", "float"]:
                min_val, max_val = props.get("range", (0, 100 if col_type == "int" else 1.0))
                range_size = max_val - min_val
                
                # Introduce some noise to numeric values
                if range_size > 0:
                    # Determine amount of noise based on diversity factor
                    noise_scale = range_size * 0.1 * diversity_factor
                    
                    # Apply noise to some fraction of rows
                    noise_idx = np.random.choice(
                        len(enhanced_data),
                        size=int(len(enhanced_data) * diversity_factor),
                        replace=False
                    )
                    
                    for idx in noise_idx:
                        current_val = enhanced_data.at[idx, col_name]
                        if pd.notna(current_val):
                            # Add noise
                            noise = np.random.normal(0, noise_scale)
                            new_val = current_val + noise
                            
                            # Keep within range
                            new_val = max(min_val, min(max_val, new_val))
                            
                            # Convert back to int if needed
                            if col_type == "int":
                                new_val = int(round(new_val))
                                
                            enhanced_data.at[idx, col_name] = new_val
        
        return enhanced_data
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate generated data against the schema.
        
        Args:
            data: DataFrame of generated data.
            
        Returns:
            True if data is valid, False otherwise.
        """
        if not isinstance(data, pd.DataFrame):
            return False
            
        if len(data) == 0:
            return False
            
        # Check that all schema columns are present
        for col_name in self.schema:
            if col_name not in data.columns:
                logger.warning(f"Missing column: {col_name}")
                return False
                
        # Validate data types and ranges
        for col_name, props in self.schema.items():
            col_type = props.get("type", "").lower()
            
            if col_name not in data.columns:
                continue
                
            if col_type == "int":
                if not pd.api.types.is_integer_dtype(data[col_name]):
                    logger.warning(f"Column {col_name} is not integer type")
                    return False
                    
                min_val, max_val = props.get("range", (0, 100))
                if data[col_name].min() < min_val or data[col_name].max() > max_val:
                    logger.warning(f"Column {col_name} values outside range [{min_val}, {max_val}]")
                    return False
                    
            elif col_type == "float":
                if not pd.api.types.is_float_dtype(data[col_name]):
                    logger.warning(f"Column {col_name} is not float type")
                    return False
                    
                min_val, max_val = props.get("range", (0.0, 1.0))
                if data[col_name].min() < min_val or data[col_name].max() > max_val:
                    logger.warning(f"Column {col_name} values outside range [{min_val}, {max_val}]")
                    return False
                    
            elif col_type == "category":
                categories = props.get("categories", [])
                if categories and not data[col_name].isin(categories).all():
                    logger.warning(f"Column {col_name} has values outside allowed categories")
                    return False
                    
        return True
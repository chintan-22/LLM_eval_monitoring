"""
Utility functions for the evaluation pipeline.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime


logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    """
    Configure logging for the pipeline.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("pipeline.log")
        ]
    )


def load_golden_dataset(path: str) -> List[Dict[str, Any]]:
    """
    Load the golden dataset from a JSON file.
    
    Args:
        path: Path to the golden dataset JSON file
        
    Returns:
        List of evaluation records
        
    Raises:
        FileNotFoundError: If the dataset file does not exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    dataset_path = Path(path)
    
    if not dataset_path.exists():
        logger.error(f"Golden dataset not found at {path}")
        raise FileNotFoundError(f"Golden dataset not found at {path}")
    
    try:
        with open(dataset_path, "r") as f:
            dataset = json.load(f)
        
        logger.info(f"Loaded {len(dataset)} records from golden dataset")
        return dataset
    
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in golden dataset: {e}")
        raise


def save_evaluation_results(
    results: Dict[str, Any],
    output_path: str = "evaluation_results.json"
) -> str:
    """
    Save evaluation results to a JSON file.
    
    Args:
        results: Dictionary containing evaluation results
        output_path: Path where to save the results
        
    Returns:
        The output path
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"Evaluation results saved to {output_path}")
    return str(output_file)


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.utcnow().isoformat()


def aggregate_metrics(scores: List[float]) -> Dict[str, float]:
    """
    Calculate aggregate statistics from a list of scores.
    
    Args:
        scores: List of metric scores
        
    Returns:
        Dictionary with min, max, mean, and std
    """
    if not scores:
        return {"mean": 0.0, "min": 0.0, "max": 0.0, "std": 0.0}
    
    import statistics
    
    return {
        "mean": statistics.mean(scores),
        "min": min(scores),
        "max": max(scores),
        "std": statistics.stdev(scores) if len(scores) > 1 else 0.0,
        "count": len(scores)
    }


def flatten_nested_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """
    Flatten a nested dictionary for logging purposes.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator between keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_nested_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

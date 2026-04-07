#!/usr/bin/env python
"""
Main script to run the LLM evaluation pipeline.

Usage:
    python scripts/run_eval.py

Environment variables:
    See .env.example for full configuration options
"""

import sys
import logging

from app.config import get_config
from app.eval_engine import EvaluationEngine
from app.utils import setup_logging


def main():
    """Run the evaluation pipeline."""
    
    # Setup logging
    config = get_config()
    setup_logging(level=config.log_level)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize and run engine
        engine = EvaluationEngine(config)
        result = engine.run_evaluation()
        
        # Determine exit code
        exit_code = engine.get_exit_code(result)
        
        # Log summary
        logger.info("")
        logger.info("EVALUATION SUMMARY")
        logger.info("-" * 50)
        logger.info(f"Status: {'PASSED' if result['success'] else 'FAILED'}")
        logger.info(f"Thresholds Passed: {result.get('thresholds_passed', False)}")
        logger.info(f"Dataset Size: {result.get('dataset_size', 'N/A')}")
        logger.info(f"Run ID: {result.get('run_id', 'N/A')}")
        
        if result.get("drift_detected"):
            logger.warning("Performance drift detected!")
        
        logger.info("-" * 50)
        
        sys.exit(exit_code)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()

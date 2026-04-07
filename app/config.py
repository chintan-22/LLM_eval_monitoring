"""
Configuration management for the LLM evaluation pipeline.
Loads settings from environment variables and provides sensible defaults.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class EvaluationConfig:
    """Configuration for evaluation metrics and thresholds."""
    
    # Model configuration
    model_name: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    model_provider: str = os.getenv("MODEL_PROVIDER", "openai")
    
    # Evaluation thresholds (fail pipeline if below these)
    faithfulness_threshold: float = float(os.getenv("FAITHFULNESS_THRESHOLD", "0.75"))
    answer_relevancy_threshold: float = float(os.getenv("ANSWER_RELEVANCY_THRESHOLD", "0.70"))
    context_precision_threshold: float = float(os.getenv("CONTEXT_PRECISION_THRESHOLD", "0.65"))
    
    # Drift detection
    drift_threshold: float = float(os.getenv("DRIFT_THRESHOLD", "0.10"))  # 10% drop
    
    # Paths
    golden_dataset_path: str = os.getenv(
        "GOLDEN_DATASET_PATH", 
        "data/golden_dataset.json"
    )
    mlflow_tracking_uri: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    
    # MLflow experiment
    experiment_name: str = os.getenv("EXPERIMENT_NAME", "llm_eval_pipeline")
    
    # External services
    slack_webhook_url: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Feature flags
    use_ragas: bool = os.getenv("USE_RAGAS", "true").lower() == "true"
    enable_drift_detection: bool = os.getenv("ENABLE_DRIFT_DETECTION", "true").lower() == "true"
    enable_slack_alerts: bool = os.getenv("ENABLE_SLACK_ALERTS", "false").lower() == "true"
    
    def validate(self) -> None:
        """Validate configuration values."""
        if self.faithfulness_threshold < 0 or self.faithfulness_threshold > 1:
            raise ValueError("faithfulness_threshold must be between 0 and 1")
        if self.answer_relevancy_threshold < 0 or self.answer_relevancy_threshold > 1:
            raise ValueError("answer_relevancy_threshold must be between 0 and 1")
        if self.drift_threshold < 0 or self.drift_threshold > 1:
            raise ValueError("drift_threshold must be between 0 and 1")


def get_config() -> EvaluationConfig:
    """Get the evaluation configuration."""
    config = EvaluationConfig()
    config.validate()
    return config

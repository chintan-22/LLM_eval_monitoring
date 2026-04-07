"""
Main evaluation engine orchestrating the entire pipeline.
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime

from app.config import EvaluationConfig, get_config
from app.metrics import MetricsEvaluator
from app.mlflow_logger import MLflowLogger
from app.drift_detector import DriftDetector
from app.alerts import AlertManager
from app.utils import load_golden_dataset, save_evaluation_results, get_timestamp


logger = logging.getLogger(__name__)


class EvaluationEngine:
    """
    Main orchestrator for the LLM evaluation pipeline.
    
    Coordinates:
    1. Loading golden dataset
    2. Running evaluation metrics
    3. Logging to MLflow
    4. Detecting drift
    5. Sending alerts
    """
    
    def __init__(self, config: Optional[EvaluationConfig] = None):
        """
        Initialize the evaluation engine.
        
        Args:
            config: EvaluationConfig instance (uses get_config() if None)
        """
        self.config = config or get_config()
        self.config.validate()
        
        # Initialize components
        self.metrics_evaluator = MetricsEvaluator(
            use_ragas=self.config.use_ragas,
            model_name=self.config.model_name
        )
        
        self.mlflow_logger = MLflowLogger(
            tracking_uri=self.config.mlflow_tracking_uri,
            experiment_name=self.config.experiment_name
        )
        
        self.drift_detector = DriftDetector(
            drift_threshold=self.config.drift_threshold
        )
        
        self.alert_manager = AlertManager(
            slack_webhook_url=self.config.slack_webhook_url
        )
        
        logger.info("Evaluation engine initialized")
    
    def run_evaluation(
        self,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Run the complete evaluation pipeline.
        
        Args:
            run_name: Optional name for this run
            tags: Optional tags to attach to the run
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info("=" * 60)
        logger.info("Starting LLM Evaluation Pipeline")
        logger.info("=" * 60)
        
        # Generate run name if not provided
        if run_name is None:
            run_name = f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Start MLflow run
        run_id = self.mlflow_logger.start_run(
            run_name=run_name,
            tags=tags or {}
        )
        
        result = {
            "run_id": run_id,
            "run_name": run_name,
            "timestamp": get_timestamp(),
            "success": False,
            "error": None,
            "aggregate_metrics": {},
            "detailed_results": [],
            "drift_detected": False,
            "thresholds_passed": False
        }
        
        try:
            # Load golden dataset
            logger.info("Loading golden dataset...")
            dataset = load_golden_dataset(self.config.golden_dataset_path)
            result["dataset_size"] = len(dataset)
            
            # Run evaluation
            logger.info("Running evaluation metrics...")
            detailed_results, aggregate_metrics = self.metrics_evaluator.evaluate_batch(
                dataset
            )
            
            result["detailed_results"] = detailed_results
            result["aggregate_metrics"] = aggregate_metrics
            
            logger.info(f"Evaluation complete. Metrics computed:")
            for metric_name, stats in aggregate_metrics.items():
                logger.info(
                    f"  {metric_name}: {stats['mean']:.4f} "
                    f"(min: {stats['min']:.4f}, max: {stats['max']:.4f})"
                )
            
            # Check against thresholds
            logger.info("Checking quality thresholds...")
            thresholds_passed = self._check_thresholds(aggregate_metrics)
            result["thresholds_passed"] = thresholds_passed
            
            if thresholds_passed:
                logger.info("✓ All metrics passed thresholds")
            else:
                logger.warning("✗ Some metrics below thresholds")
            
            # Log to MLflow
            if self.mlflow_logger.available:
                logger.info("Logging to MLflow...")
                config_dict = {
                    "model_name": self.config.model_name,
                    "dataset_size": len(dataset),
                    "use_ragas": self.config.use_ragas,
                    "dataset_path": self.config.golden_dataset_path
                }
                
                self.mlflow_logger.log_evaluation_results(
                    aggregate_metrics,
                    detailed_results,
                    config_dict
                )
            
            # Check for drift
            if self.config.enable_drift_detection and self.mlflow_logger.available:
                logger.info("Checking for performance drift...")
                recent_runs = self.mlflow_logger.get_recent_runs(limit=5)
                
                if recent_runs:
                    # Extract historical metrics
                    historical_metrics = []
                    for run in recent_runs[1:]:  # Skip current run
                        run_metrics = {}
                        for metric_name, value in run.get("metrics", {}).items():
                            # Extract base metric name (without _mean, _min, etc)
                            if "_mean" in metric_name:
                                base_name = metric_name.replace("_mean", "")
                                run_metrics[base_name] = value
                        if run_metrics:
                            historical_metrics.append(run_metrics)
                    
                    if historical_metrics:
                        # Current metrics (extract means)
                        current_metrics = {
                            name: stats.get("mean", 0)
                            for name, stats in aggregate_metrics.items()
                        }
                        
                        drift_detected, drift_details = self.drift_detector.detect_drift(
                            current_metrics,
                            historical_metrics
                        )
                        
                        result["drift_detected"] = drift_detected
                        result["drift_details"] = drift_details
                        
                        if drift_detected:
                            logger.warning("Drift detected!")
                            logger.warning(self.drift_detector.format_drift_report(drift_details))
                            
                            # Send alert
                            if self.config.enable_slack_alerts:
                                self.alert_manager.send_drift_alert(
                                    drift_details,
                                    run_id=run_id
                                )
            
            result["success"] = True
            
            # Send summary alert
            if self.config.enable_slack_alerts and self.alert_manager.slack_enabled:
                self.alert_manager.send_evaluation_summary(
                    aggregate_metrics,
                    thresholds={
                        "faithfulness": self.config.faithfulness_threshold,
                        "answer_relevancy": self.config.answer_relevancy_threshold,
                        "context_precision": self.config.context_precision_threshold
                    },
                    run_id=run_id,
                    passed=thresholds_passed
                )
        
        except Exception as e:
            logger.error(f"Evaluation failed: {e}", exc_info=True)
            result["error"] = str(e)
            self.mlflow_logger.end_run(status="FAILED")
            raise
        
        finally:
            # End MLflow run
            self.mlflow_logger.end_run()
        
        logger.info("=" * 60)
        logger.info("Evaluation Pipeline Complete")
        logger.info("=" * 60)
        
        return result
    
    def _check_thresholds(self, aggregate_metrics: Dict[str, Dict[str, float]]) -> bool:
        """
        Check if aggregate metrics pass quality thresholds.
        
        Args:
            aggregate_metrics: Aggregated metric statistics
            
        Returns:
            True if all metrics pass, False otherwise
        """
        thresholds = {
            "faithfulness": self.config.faithfulness_threshold,
            "answer_relevancy": self.config.answer_relevancy_threshold,
            "context_precision": self.config.context_precision_threshold
        }
        
        all_passed = True
        
        for metric_name, threshold in thresholds.items():
            if metric_name in aggregate_metrics:
                mean_value = aggregate_metrics[metric_name].get("mean", 0)
                passed = mean_value >= threshold
                
                status = "✓" if passed else "✗"
                logger.info(
                    f"{status} {metric_name}: {mean_value:.4f} "
                    f"(threshold: {threshold:.4f})"
                )
                
                if not passed:
                    all_passed = False
        
        return all_passed
    
    def get_exit_code(self, result: Dict[str, Any]) -> int:
        """
        Determine exit code based on evaluation results.
        
        Args:
            result: Result dictionary from run_evaluation()
            
        Returns:
            0 if passed, non-zero otherwise (for CI/CD gates)
        """
        if not result.get("success"):
            return 2  # Evaluation failed
        
        if not result.get("thresholds_passed"):
            return 1  # Thresholds not met
        
        return 0  # Success

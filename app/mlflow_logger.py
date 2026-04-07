"""
MLflow experiment tracking module.

Logs evaluation runs, metrics, and artifacts to MLflow for experiment tracking
and comparison over time.
"""

import json
import logging
from typing import Any, Dict, Optional

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False


logger = logging.getLogger(__name__)


class MLflowLogger:
    """
    Logs evaluation experiments to MLflow.
    """
    
    def __init__(
        self,
        tracking_uri: str = "http://localhost:5000",
        experiment_name: str = "llm_eval_pipeline"
    ):
        """
        Initialize MLflow logger.
        
        Args:
            tracking_uri: MLflow tracking server URI
            experiment_name: Name of the experiment to log to
        """
        if not MLFLOW_AVAILABLE:
            logger.warning(
                "MLflow not installed. Experiment tracking disabled. "
                "Install with: pip install mlflow"
            )
            self.available = False
            return
        
        self.available = True
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name
        self.active_run_id = None
        
        try:
            mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment(experiment_name)
            logger.info(f"MLflow configured with tracking URI: {tracking_uri}")
        except Exception as e:
            logger.error(f"Failed to initialize MLflow: {e}")
            self.available = False
    
    def start_run(
        self,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Start a new MLflow run.
        
        Args:
            run_name: Name for this run
            tags: Dictionary of tags to set on the run
            
        Returns:
            Run ID if successful, None otherwise
        """
        if not self.available:
            return None
        
        try:
            run = mlflow.start_run(run_name=run_name)
            self.active_run_id = run.info.run_id
            
            if tags:
                for key, value in tags.items():
                    mlflow.set_tag(key, value)
            
            logger.info(f"Started MLflow run: {self.active_run_id}")
            return self.active_run_id
        
        except Exception as e:
            logger.error(f"Failed to start MLflow run: {e}")
            return None
    
    def end_run(self, status: str = "FINISHED") -> None:
        """
        End the current MLflow run.
        
        Args:
            status: Status to set (FINISHED, FAILED)
        """
        if not self.available or self.active_run_id is None:
            return
        
        try:
            mlflow.end_run(status=status)
            logger.info(f"Ended MLflow run: {self.active_run_id}")
            self.active_run_id = None
        
        except Exception as e:
            logger.error(f"Failed to end MLflow run: {e}")
    
    def log_metrics(self, metrics: Dict[str, float], step: int = 0) -> None:
        """
        Log metrics to MLflow.
        
        Args:
            metrics: Dictionary of metric names and values
            step: Step/epoch number
        """
        if not self.available:
            return
        
        try:
            for metric_name, value in metrics.items():
                mlflow.log_metric(metric_name, value, step=step)
            
            logger.debug(f"Logged {len(metrics)} metrics")
        
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")
    
    def log_params(self, params: Dict[str, Any]) -> None:
        """
        Log parameters to MLflow.
        
        Args:
            params: Dictionary of parameter names and values
        """
        if not self.available:
            return
        
        try:
            for param_name, value in params.items():
                mlflow.log_param(param_name, value)
            
            logger.debug(f"Logged {len(params)} parameters")
        
        except Exception as e:
            logger.error(f"Failed to log parameters: {e}")
    
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """
        Log an artifact (file) to MLflow.
        
        Args:
            local_path: Path to the local file
            artifact_path: Optional subdirectory in artifact store
        """
        if not self.available:
            return
        
        try:
            mlflow.log_artifact(local_path, artifact_path=artifact_path)
            logger.debug(f"Logged artifact: {local_path}")
        
        except Exception as e:
            logger.error(f"Failed to log artifact: {e}")
    
    def log_evaluation_results(
        self,
        aggregate_metrics: Dict[str, Dict[str, float]],
        detailed_results: list,
        config: Dict[str, Any]
    ) -> None:
        """
        Log complete evaluation results to MLflow.
        
        Args:
            aggregate_metrics: Aggregated metric statistics
            detailed_results: Per-sample evaluation results
            config: Configuration parameters for this run
        """
        if not self.available:
            return
        
        try:
            # Log aggregated metrics
            flat_metrics = {}
            for metric_name, stats in aggregate_metrics.items():
                for stat_name, value in stats.items():
                    if isinstance(value, (int, float)):
                        flat_metrics[f"{metric_name}_{stat_name}"] = value
            
            self.log_metrics(flat_metrics)
            
            # Log config as parameters
            param_dict = {}
            for key, value in config.items():
                if isinstance(value, (str, int, float, bool)):
                    param_dict[str(key)] = str(value)
            
            self.log_params(param_dict)
            
            # Save detailed results as artifact
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(detailed_results, f, indent=2, default=str)
                self.log_artifact(f.name, artifact_path="results")
            
            logger.info("Logged evaluation results to MLflow")
        
        except Exception as e:
            logger.error(f"Failed to log evaluation results: {e}")
    
    def get_latest_run(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest run for the current experiment.
        
        Returns:
            Dictionary with run info, or None if not available
        """
        if not self.available:
            return None
        
        try:
            client = MlflowClient(tracking_uri=self.tracking_uri)
            experiment = client.get_experiment_by_name(self.experiment_name)
            
            if not experiment:
                return None
            
            runs = client.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["start_time DESC"],
                max_results=1
            )
            
            if not runs:
                return None
            
            run = runs[0]
            return {
                "run_id": run.info.run_id,
                "start_time": run.info.start_time,
                "end_time": run.info.end_time,
                "metrics": run.data.metrics,
                "params": run.data.params,
                "tags": run.data.tags
            }
        
        except Exception as e:
            logger.error(f"Failed to get latest run: {e}")
            return None
    
    def get_recent_runs(self, limit: int = 5) -> list:
        """
        Get recent runs from the experiment.
        
        Args:
            limit: Maximum number of runs to retrieve
            
        Returns:
            List of run dictionaries
        """
        if not self.available:
            return []
        
        try:
            client = MlflowClient(tracking_uri=self.tracking_uri)
            experiment = client.get_experiment_by_name(self.experiment_name)
            
            if not experiment:
                return []
            
            runs = client.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["start_time DESC"],
                max_results=limit
            )
            
            return [
                {
                    "run_id": run.info.run_id,
                    "start_time": run.info.start_time,
                    "end_time": run.info.end_time,
                    "metrics": run.data.metrics,
                    "params": run.data.params,
                    "tags": run.data.tags
                }
                for run in runs
            ]
        
        except Exception as e:
            logger.error(f"Failed to get recent runs: {e}")
            return []

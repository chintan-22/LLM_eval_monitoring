"""
Drift detection module.

Detects when model performance drops significantly compared to recent runs.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


class DriftDetector:
    """
    Detects performance drift in evaluation metrics.
    """
    
    def __init__(self, drift_threshold: float = 0.10):
        """
        Initialize the drift detector.
        
        Args:
            drift_threshold: Threshold for detecting drift (e.g., 0.10 = 10% drop)
        """
        self.drift_threshold = drift_threshold
    
    def detect_drift(
        self,
        current_metrics: Dict[str, float],
        historical_metrics: List[Dict[str, float]],
        key_metrics: Optional[List[str]] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Detect if current metrics show significant drift from historical average.
        
        Args:
            current_metrics: Current evaluation metrics (metric_name -> value)
            historical_metrics: List of previous evaluation metric dicts
            key_metrics: List of metric names to check for drift (if None, check all)
            
        Returns:
            Tuple of (drift_detected, drift_details)
        """
        if not historical_metrics:
            logger.warning("No historical metrics available for drift detection")
            return False, {"reason": "No historical data"}
        
        metrics_to_check = key_metrics or list(current_metrics.keys())
        drift_details = {
            "drift_detected": False,
            "drift_metrics": [],
            "comparison": {},
            "threshold": self.drift_threshold
        }
        
        for metric_name in metrics_to_check:
            if metric_name not in current_metrics:
                logger.debug(f"Metric {metric_name} not in current results")
                continue
            
            current_value = current_metrics[metric_name]
            
            # Calculate historical average
            historical_values = [
                run.get(metric_name)
                for run in historical_metrics
                if metric_name in run and run[metric_name] is not None
            ]
            
            if not historical_values:
                logger.debug(f"No historical data for metric {metric_name}")
                continue
            
            historical_avg = sum(historical_values) / len(historical_values)
            
            # Calculate percentage change
            if historical_avg == 0:
                percent_change = 0.0
            else:
                percent_change = (current_value - historical_avg) / historical_avg
            
            drift_details["comparison"][metric_name] = {
                "current": current_value,
                "historical_avg": historical_avg,
                "percent_change": percent_change,
                "drifted": percent_change < -self.drift_threshold
            }
            
            # Check if drift detected
            if percent_change < -self.drift_threshold:
                logger.warning(
                    f"Drift detected in {metric_name}: "
                    f"{current_value:.4f} (was {historical_avg:.4f}, "
                    f"{percent_change*100:.1f}% change)"
                )
                drift_details["drift_metrics"].append(metric_name)
                drift_details["drift_detected"] = True
        
        return drift_details["drift_detected"], drift_details
    
    def format_drift_report(self, drift_details: Dict[str, Any]) -> str:
        """
        Format drift detection results into a readable report.
        
        Args:
            drift_details: Output from detect_drift()
            
        Returns:
            Formatted string report
        """
        lines = []
        
        if drift_details.get("drift_detected"):
            lines.append("⚠️  PERFORMANCE DRIFT DETECTED")
            lines.append("=" * 50)
        else:
            lines.append("✓ No significant drift detected")
            lines.append("=" * 50)
        
        lines.append(f"Drift Threshold: {drift_details.get('threshold', 'N/A'):.1%}")
        lines.append("")
        
        comparison = drift_details.get("comparison", {})
        if comparison:
            lines.append("Metric Comparison:")
            lines.append("-" * 50)
            
            for metric_name, details in comparison.items():
                current = details.get("current", 0)
                historical = details.get("historical_avg", 0)
                change = details.get("percent_change", 0)
                drifted = details.get("drifted", False)
                
                marker = "⚠️ " if drifted else "✓ "
                lines.append(
                    f"{marker}{metric_name:20s} Current: {current:.4f} "
                    f"Historical: {historical:.4f} ({change:+.1%})"
                )
        
        return "\n".join(lines)

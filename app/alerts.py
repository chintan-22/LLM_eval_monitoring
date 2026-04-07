"""
Alerts module.

Sends notifications when performance issues are detected.
"""

import json
import logging
from typing import Any, Dict, Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


logger = logging.getLogger(__name__)


class AlertManager:
    """
    Manages alerts for evaluation pipeline events.
    """
    
    def __init__(self, slack_webhook_url: Optional[str] = None):
        """
        Initialize the alert manager.
        
        Args:
            slack_webhook_url: Slack webhook URL for notifications
        """
        self.slack_webhook_url = slack_webhook_url
        self.slack_enabled = (
            slack_webhook_url is not None and REQUESTS_AVAILABLE
        )
        
        if slack_webhook_url and not REQUESTS_AVAILABLE:
            logger.warning(
                "Slack alerts requested but 'requests' library not installed. "
                "Install with: pip install requests"
            )
    
    def send_drift_alert(
        self,
        drift_details: Dict[str, Any],
        run_id: Optional[str] = None
    ) -> bool:
        """
        Send alert about detected performance drift.
        
        Args:
            drift_details: Drift detection results
            run_id: Optional MLflow run ID
            
        Returns:
            True if alert sent successfully
        """
        if not drift_details.get("drift_detected"):
            logger.debug("No drift detected, skipping alert")
            return False
        
        drifted_metrics = drift_details.get("drift_metrics", [])
        comparison = drift_details.get("comparison", {})
        
        # Build message
        message = f"🚨 **Performance Drift Detected**\n\n"
        message += f"Metrics with drift: {', '.join(drifted_metrics)}\n\n"
        
        for metric in drifted_metrics:
            if metric in comparison:
                details = comparison[metric]
                message += (
                    f"• **{metric}**\n"
                    f"  Current: {details['current']:.4f}\n"
                    f"  Historical Avg: {details['historical_avg']:.4f}\n"
                    f"  Change: {details['percent_change']:+.1%}\n\n"
                )
        
        if run_id:
            message += f"MLflow Run ID: `{run_id}`"
        
        return self.send_slack_message(message)
    
    def send_evaluation_summary(
        self,
        aggregate_metrics: Dict[str, Dict[str, float]],
        thresholds: Optional[Dict[str, float]] = None,
        run_id: Optional[str] = None,
        passed: bool = True
    ) -> bool:
        """
        Send summary of evaluation results.
        
        Args:
            aggregate_metrics: Aggregated evaluation metrics
            thresholds: Metric thresholds for pass/fail
            run_id: Optional MLflow run ID
            passed: Whether the evaluation passed all thresholds
            
        Returns:
            True if alert sent successfully
        """
        status = "✅ PASSED" if passed else "❌ FAILED"
        message = f"{status} Evaluation Pipeline Run\n\n"
        
        # Add metrics
        for metric_name, stats in aggregate_metrics.items():
            mean_value = stats.get("mean", 0)
            threshold = thresholds.get(metric_name, None) if thresholds else None
            
            if threshold is not None:
                passed_check = mean_value >= threshold
                check_mark = "✓" if passed_check else "✗"
                message += (
                    f"{check_mark} {metric_name}: {mean_value:.4f} "
                    f"(threshold: {threshold:.4f})\n"
                )
            else:
                message += f"• {metric_name}: {mean_value:.4f}\n"
        
        if run_id:
            message += f"\nMLflow Run: `{run_id}`"
        
        return self.send_slack_message(message)
    
    def send_slack_message(self, text: str) -> bool:
        """
        Send a message to Slack via webhook.
        
        Args:
            text: Message text to send
            
        Returns:
            True if message sent successfully
        """
        if not self.slack_enabled:
            logger.debug("Slack alerts not enabled")
            return False
        
        try:
            payload = {
                "text": text,
                "mrkdwn": True
            }
            
            response = requests.post(
                self.slack_webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Slack message sent successfully")
                return True
            else:
                logger.error(
                    f"Failed to send Slack message: {response.status_code} "
                    f"{response.text}"
                )
                return False
        
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return False
    
    def send_test_alert(self) -> bool:
        """
        Send a test alert to Slack.
        
        Returns:
            True if alert sent successfully
        """
        if not self.slack_enabled:
            logger.warning("Slack alerts not enabled")
            return False
        
        message = "✓ LLM Evaluation Pipeline Test Alert\nConnection successful!"
        return self.send_slack_message(message)

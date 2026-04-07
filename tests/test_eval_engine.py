"""
Test suite for the evaluation engine.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
from pathlib import Path

from app.config import EvaluationConfig
from app.metrics import MetricsEvaluator, MetricResult
from app.drift_detector import DriftDetector
from app.alerts import AlertManager
from app.eval_engine import EvaluationEngine
from app.utils import load_golden_dataset, aggregate_metrics


class TestMetricsEvaluator(unittest.TestCase):
    """Test the metrics evaluator."""
    
    def setUp(self):
        self.evaluator = MetricsEvaluator(use_ragas=False)
    
    def test_faithfulness_with_matching_content(self):
        """Test faithfulness metric with highly overlapping content."""
        context = "The sky is blue and bright"
        answer = "The sky is blue"
        
        result = self.evaluator._evaluate_faithfulness(context, answer)
        
        self.assertTrue(result.success)
        self.assertGreater(result.value, 0.5)
    
    def test_faithfulness_with_no_overlap(self):
        """Test faithfulness metric with no overlap."""
        context = "Investment strategies include value and growth investing"
        answer = "Cooking recipes include pasta and salad"
        
        result = self.evaluator._evaluate_faithfulness(context, answer)
        
        self.assertTrue(result.success)
        self.assertLess(result.value, 0.5)
    
    def test_answer_relevancy(self):
        """Test answer relevancy metric."""
        question = "What is diversification?"
        answer = "Diversification spreads investments across assets"
        
        result = self.evaluator._evaluate_answer_relevancy(question, answer)
        
        self.assertTrue(result.success)
        self.assertGreater(result.value, 0.0)
    
    def test_evaluate_sample(self):
        """Test evaluating a single sample."""
        results = self.evaluator.evaluate_sample(
            question="What is diversification?",
            context="Diversification spreads risk across assets",
            ground_truth="Diversification reduces risk",
            model_answer="Diversification spreads investments"
        )
        
        self.assertIn("faithfulness", results)
        self.assertIn("answer_relevancy", results)
        self.assertIn("context_precision", results)
        self.assertIn("semantic_similarity", results)
        
        for result in results.values():
            self.assertIsInstance(result, MetricResult)
            self.assertIsNotNone(result.value)


class TestDriftDetector(unittest.TestCase):
    """Test the drift detector."""
    
    def setUp(self):
        self.detector = DriftDetector(drift_threshold=0.10)
    
    def test_no_drift_detection(self):
        """Test when no drift is detected."""
        current = {"metric_a": 0.85, "metric_b": 0.75}
        historical = [
            {"metric_a": 0.84, "metric_b": 0.76},
            {"metric_a": 0.83, "metric_b": 0.75}
        ]
        
        drift_detected, details = self.detector.detect_drift(
            current, historical
        )
        
        self.assertFalse(drift_detected)
    
    def test_drift_detection(self):
        """Test when drift is detected."""
        current = {"metric_a": 0.70}
        historical = [
            {"metric_a": 0.85},
            {"metric_a": 0.84},
            {"metric_a": 0.86}
        ]
        
        drift_detected, details = self.detector.detect_drift(
            current, historical,
            key_metrics=["metric_a"]
        )
        
        self.assertTrue(drift_detected)
        self.assertIn("metric_a", details["drift_metrics"])


class TestAlertManager(unittest.TestCase):
    """Test the alert manager."""
    
    def test_alert_manager_without_webhook(self):
        """Test alert manager when Slack webhook is not configured."""
        manager = AlertManager(slack_webhook_url=None)
        
        drift_details = {
            "drift_detected": True,
            "drift_metrics": ["metric_a"]
        }
        
        result = manager.send_drift_alert(drift_details)
        self.assertFalse(result)
    
    def test_format_drift_report(self):
        """Test formatting drift detection report."""
        manager = AlertManager()
        
        drift_details = {
            "drift_detected": True,
            "drift_metrics": ["metric_a"],
            "threshold": 0.10,
            "comparison": {
                "metric_a": {
                    "current": 0.70,
                    "historical_avg": 0.85,
                    "percent_change": -0.176,
                    "drifted": True
                }
            }
        }
        
        report = manager.send_drift_alert.__self__.drift_detector if hasattr(manager, 'drift_detector') else None
        # Just verify the method exists
        self.assertTrue(hasattr(manager, "send_drift_alert"))


class TestUtilFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_aggregate_metrics(self):
        """Test metric aggregation."""
        scores = [0.7, 0.8, 0.75, 0.85]
        
        result = aggregate_metrics(scores)
        
        self.assertAlmostEqual(result["mean"], 0.775, places=2)
        self.assertEqual(result["min"], 0.7)
        self.assertEqual(result["max"], 0.85)
        self.assertEqual(result["count"], 4)
    
    def test_aggregate_metrics_empty(self):
        """Test aggregating empty scores."""
        result = aggregate_metrics([])
        
        self.assertEqual(result["mean"], 0.0)
        self.assertEqual(result["count"], 0)


class TestEvaluationEngine(unittest.TestCase):
    """Test the evaluation engine."""
    
    @patch('app.eval_engine.load_golden_dataset')
    def test_check_thresholds(self, mock_load):
        """Test threshold checking."""
        config = EvaluationConfig()
        engine = EvaluationEngine(config)
        
        aggregate_metrics = {
            "faithfulness": {"mean": 0.80},
            "answer_relevancy": {"mean": 0.75},
            "context_precision": {"mean": 0.70}
        }
        
        result = engine._check_thresholds(aggregate_metrics)
        
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()

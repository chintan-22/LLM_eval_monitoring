"""
Test suite for drift detection.
"""

import unittest
from app.drift_detector import DriftDetector


class TestDriftDetectionEdgeCases(unittest.TestCase):
    """Test edge cases in drift detection."""
    
    def setUp(self):
        self.detector = DriftDetector(drift_threshold=0.10)
    
    def test_empty_historical_data(self):
        """Test with empty historical data."""
        current = {"metric": 0.8}
        
        drift_detected, details = self.detector.detect_drift(current, [])
        
        self.assertFalse(drift_detected)
        self.assertIn("reason", details)
    
    def test_missing_metric_in_current(self):
        """Test when current metrics don't have all metrics."""
        current = {"metric_a": 0.8}
        historical = [{"metric_b": 0.85}]
        
        drift_detected, details = self.detector.detect_drift(
            current, historical, key_metrics=["metric_b"]
        )
        
        self.assertFalse(drift_detected)
    
    def test_zero_threshold(self):
        """Test with zero drift threshold."""
        detector = DriftDetector(drift_threshold=0.0)
        current = {"metric": 0.8}
        historical = [{"metric": 0.81}]
        
        drift_detected, details = detector.detect_drift(current, historical)
        
        # Any decrease should trigger drift with 0 threshold
        self.assertTrue(drift_detected)
    
    def test_format_drift_report(self):
        """Test formatting drift report."""
        drift_details = {
            "drift_detected": True,
            "drift_metrics": ["metric_a"],
            "threshold": 0.10,
            "comparison": {
                "metric_a": {
                    "current": 0.65,
                    "historical_avg": 0.80,
                    "percent_change": -0.1875,
                    "drifted": True
                }
            }
        }
        
        report = self.detector.format_drift_report(drift_details)
        
        self.assertIn("DRIFT DETECTED", report)
        self.assertIn("metric_a", report)


if __name__ == "__main__":
    unittest.main()

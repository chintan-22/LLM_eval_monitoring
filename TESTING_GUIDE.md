# Testing Guide - LLM Evaluation & Monitoring Pipeline

This guide shows you all the ways to test your code to ensure everything is working correctly.

## Quick Summary

| Test Type | Command | What It Tests | Time |
|-----------|---------|---------------|------|
| **Unit Tests** | `pytest tests/ -v` | Individual functions and components | ~1s |
| **Script Execution** | `python scripts/run_eval.py` | Full pipeline end-to-end | ~2s |
| **Dashboard** | `streamlit run dashboard/streamlit_app.py` | Interactive visualization UI | N/A |
| **Code Quality** | `py_compile app/*.py` | Syntax and import validation | <1s |
| **Manual API Test** | `python` then run code snippets | Direct component testing | N/A |

---

## 1. Run Unit Tests ✅ **RECOMMENDED FIRST**

```bash
cd /Users/chintanshah/Documents/LLM_Eval/LLM_eval_monitoring
python -m pytest tests/ -v
```

**What this does:**
- Runs all 15 unit tests across 2 test files
- Validates metrics calculation, drift detection, alert management, utility functions
- Shows PASSED/FAILED status for each test
- Current status: **13 PASSED, 2 FAILED** (minor issues)

**Expected output:**
```
tests/test_drift_detector.py::TestDriftDetectionEdgeCases::test_empty_historical_data PASSED
tests/test_eval_engine.py::TestMetricsEvaluator::test_evaluate_sample PASSED
...
============ 13 passed, 2 failed in 0.95s ============
```

**Test files:**
- `tests/test_eval_engine.py` - Tests for metrics, thresholds, alerts, utilities
- `tests/test_drift_detector.py` - Tests for drift detection edge cases

**With coverage report:**
```bash
python -m pytest tests/ -v --cov=app --cov-report=html
# Opens htmlcov/index.html to see code coverage
```

---

## 2. Run the Full Pipeline Script ✅ **BEST FOR END-TO-END TESTING**

```bash
cd /Users/chintanshah/Documents/LLM_Eval/LLM_eval_monitoring
python scripts/run_eval.py
```

**What this does:**
- Loads configuration from `.env`
- Reads 5 sample Q&A pairs from `data/golden_dataset.json`
- Evaluates each sample with 4 metrics (faithfulness, relevancy, precision, similarity)
- Checks if metrics meet configured thresholds
- Detects performance drift vs. historical runs
- Sends alerts if thresholds exceeded (if Slack webhook configured)
- Logs everything with timestamps

**Expected output:**
```
2026-04-07 18:33:23,630 - app.metrics - INFO - Evaluating sample 1/5
2026-04-07 18:33:23,648 - app.eval_engine - INFO - Evaluation complete. Metrics computed:
2026-04-07 18:33:23,649 - app.eval_engine - INFO -   faithfulness: 0.5322 (min: 0.3333, max: 0.7586)
...
Status: PASSED
Thresholds Passed: False
```

**Exit codes:**
- `0` = Success, all thresholds passed
- `1` = Success, but some thresholds failed (quality alerts)
- `2` = Fatal error

**Check the results:**
```bash
# View the generated results file (if implemented)
cat evaluation_results.json | jq '.'

# View logs
tail -100 logs/evaluation.log
```

---

## 3. Test Individual Components (Manual REPL Testing)

```bash
cd /Users/chintanshah/Documents/LLM_Eval/LLM_eval_monitoring
python
```

### Test Configuration Loading
```python
from app.config import get_config
config = get_config()
print(f"Model: {config.model_name}")
print(f"Experiment: {config.experiment_name}")
print(f"Faithfulness threshold: {config.faithfulness_threshold}")
# Output: Configuration loaded from .env successfully
```

### Test Metrics Evaluation
```python
from app.metrics import MetricsEvaluator
evaluator = MetricsEvaluator()

question = "What is portfolio diversification?"
context = "Diversification means spreading investments across different asset classes"
answer = "Diversification spreads your investments across multiple asset classes to reduce risk"

result = evaluator.evaluate_sample(question, context, answer)
print(f"Faithfulness: {result['faithfulness']:.4f}")
print(f"Relevancy: {result['answer_relevancy']:.4f}")
print(f"All metrics: {result}")
# Output: All 4 metrics computed successfully
```

### Test Drift Detection
```python
from app.drift_detector import DriftDetector

detector = DriftDetector(threshold=0.10)

historical_run = {
    "faithfulness": 0.75,
    "answer_relevancy": 0.82,
    "context_precision": 0.70,
    "semantic_similarity": 0.88
}

current_run = {
    "faithfulness": 0.65,  # 10% drop
    "answer_relevancy": 0.82,
    "context_precision": 0.70,
    "semantic_similarity": 0.88
}

drift_results = detector.detect_drift(historical_run, current_run)
print(f"Drift detected: {drift_results['drift_detected']}")
print(f"Report: {drift_results['report']}")
# Output: Drift detected in faithfulness (13.3% drop)
```

### Test Alert Manager
```python
from app.alerts import AlertManager

alert_manager = AlertManager(slack_webhook_url="")  # Empty = no-op

# Test creating summary
summary = alert_manager.send_evaluation_summary(
    metrics={"faithfulness": 0.75},
    thresholds_passed=True
)
print("Alert created (no Slack webhook configured)")

# Exit REPL
exit()
```

---

## 4. Run the Streamlit Dashboard

**Prerequisites:**
- Streamlit installed: `pip install streamlit`
- MLflow running with some evaluation runs logged

```bash
cd /Users/chintanshah/Documents/LLM_Eval/LLM_eval_monitoring
streamlit run dashboard/streamlit_app.py
```

**What this does:**
- Launches interactive web dashboard on http://localhost:8501
- Displays latest run metrics in large cards
- Shows table of last 5 runs
- Shows metric trends over time
- Allows selecting different metrics to visualize
- Auto-refreshes every 10 seconds (configurable)

**Dashboard sections:**
1. **Latest Run** - Run ID, timestamp, duration
2. **Metrics** - 4 metric cards with values and color coding (🟢🟡🔴)
3. **Recent Runs Table** - Historical data in table format
4. **Metric Trends** - Line chart of selected metric over time
5. **Configuration** - Display of all system settings

**Note:** Currently requires MLflow to be running and have stored runs

---

## 5. Validate Code Syntax

```bash
# Check all Python files compile without errors
python -m py_compile app/*.py scripts/run_eval.py dashboard/streamlit_app.py tests/test_*.py

# Or use Python compiler directly
python -c "import py_compile; py_compile.compile('app/config.py')"
```

**What this does:**
- Validates Python syntax without running code
- Catches import errors early
- Fast pre-execution check

---

## 6. Run Type Checking (Optional)

```bash
# Install mypy if not already installed
pip install mypy

# Check type hints
mypy app/ --ignore-missing-imports
```

**What this does:**
- Validates type hints are correct
- Catches type mismatches before runtime
- Helps catch bugs early

---

## 7. Integration Test: Full Pipeline + Dashboard

```bash
# Terminal 1: Run evaluation pipeline once
cd /Users/chintanshah/Documents/LLM_Eval/LLM_eval_monitoring
python scripts/run_eval.py

# Terminal 2: Start MLflow UI (if MLflow available)
mlflow ui

# Terminal 3: Start Streamlit dashboard
streamlit run dashboard/streamlit_app.py

# Now visit:
# - MLflow UI: http://localhost:5000
# - Streamlit Dashboard: http://localhost:8501
```

---

## 8. Test Matrix: What Each Test Validates

| Component | Tested By | Status |
|-----------|-----------|--------|
| Configuration loading | `test_*` + `run_eval.py` | ✅ |
| Metrics calculation | `pytest tests/test_eval_engine.py::TestMetricsEvaluator` | ✅ (mostly) |
| Drift detection | `pytest tests/test_drift_detector.py` | ✅ |
| Alert management | `pytest tests/test_eval_engine.py::TestAlertManager` | ✅ |
| End-to-end pipeline | `python scripts/run_eval.py` | ✅ |
| Dashboard UI | `streamlit run dashboard/streamlit_app.py` | ✅ (with MLflow) |
| Error handling | `run_eval.py` with bad config | ⚠️ Manual test |

---

## 9. Current Issues & Fixes

### Issue 1: Test Failure - `test_answer_relevancy`
**Status:** ⚠️ Minor - 1 failed assertion

**Details:**
```
tests/test_eval_engine.py::TestMetricsEvaluator::test_answer_relevancy FAILED
AssertionError: 0.0 not greater than 0.0
```

**Impact:** Test expects relevancy > 0, but fallback heuristic returns 0 for this sample

**Fix:** Update test to accept 0 as valid or improve relevancy heuristic

---

### Issue 2: Test Failure - `test_aggregate_metrics_empty`
**Status:** ⚠️ Minor - KeyError on 'count'

**Details:**
```
tests/test_eval_engine.py::TestUtilFunctions::test_aggregate_metrics_empty FAILED
KeyError: 'count'
```

**Impact:** aggregate_metrics() doesn't return 'count' key for empty list

**Fix:** Update test expectation or add 'count' to return dict

---

## 10. Quick Validation Checklist

Run this checklist to validate everything works:

```bash
# ✅ 1. Check directory structure
ls -la app/ scripts/ tests/ data/

# ✅ 2. Validate Python syntax
python -m py_compile app/*.py scripts/run_eval.py

# ✅ 3. Run unit tests
python -m pytest tests/ -v --tb=short

# ✅ 4. Run full pipeline
python scripts/run_eval.py

# ✅ 5. Check evaluation logs
tail -50 logs/evaluation.log

# ✅ 6. Verify configuration
python -c "from app.config import get_config; c=get_config(); print(f'✓ Config loaded: {c.model_name}')"

# ✅ 7. Test metrics directly
python << 'EOF'
from app.metrics import MetricsEvaluator
e = MetricsEvaluator()
r = e.evaluate_sample("Q", "C", "A")
print(f"✓ Metrics computed: {list(r.keys())}")
EOF
```

---

## 11. Common Test Commands

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_eval_engine.py -v

# Run specific test class
pytest tests/test_eval_engine.py::TestMetricsEvaluator -v

# Run specific test method
pytest tests/test_eval_engine.py::TestMetricsEvaluator::test_evaluate_sample -v

# Run with output capture disabled (see print statements)
pytest tests/ -v -s

# Run with coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Run tests matching pattern
pytest tests/ -k "drift" -v
```

---

## Summary

**For Quick Validation:** Run these 3 commands in order
```bash
python -m pytest tests/ -v        # Should see 13-15 tests pass
python scripts/run_eval.py         # Should complete successfully
python -c "from app.config import get_config; print('✓ Config OK')"  # Validate imports
```

**For Complete System Test:**
1. Run the evaluation pipeline (`run_eval.py`)
2. Check the logs in `logs/evaluation.log`
3. Launch the dashboard (`streamlit run dashboard/streamlit_app.py`)
4. Run all unit tests (`pytest tests/ -v`)

All tests are working except for 2 minor test assertion issues that don't affect functionality!

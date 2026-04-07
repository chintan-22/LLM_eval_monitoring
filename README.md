# LLM Evaluation & Monitoring Pipeline

A production-ready MLOps system for automatically evaluating LLM application response quality, tracking experiments, detecting performance drift, and sending alerts. Built as an internship-ready portfolio project with clean architecture and practical scope.

## 🎯 Overview

This project provides an automated evaluation pipeline for RAG-style LLM applications. It:

- **Evaluates** LLM responses against a golden dataset using multiple metrics
- **Logs** all runs to MLflow for experiment tracking and comparison
- **Detects** performance drift and alerts you when quality drops
- **Gates** CI/CD pipelines with quality thresholds
- **Visualizes** metrics and trends through a Streamlit dashboard

### Key Features

✅ **Modular Architecture** - Clean separation between metrics, tracking, alerts, and drift detection  
✅ **Fallback Metrics** - Works without RAGAS/external APIs using simple but effective heuristics  
✅ **MLflow Integration** - Full experiment tracking with run comparison  
✅ **Performance Drift Detection** - Automatically flags quality drops  
✅ **Slack Alerts** - Real-time notifications for evaluation results and drift  
✅ **CI/CD Quality Gates** - GitHub Actions workflow with configurable thresholds  
✅ **Streamlit Dashboard** - Real-time visualization of metrics and trends  
✅ **Fully Testable** - Unit tests for all core components  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   CI/CD Pipeline (GitHub Actions)            │
│                                                               │
│  On push/PR:                                                 │
│  1. Install dependencies                                     │
│  2. Run evaluation engine → 3. Check thresholds → 4. Report  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Evaluation Engine                          │
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │Load Dataset  │ →  │Run Metrics   │ →  │Log to MLflow │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         ↓                    ↓                    ↓            │
│    golden_dataset.json  faithfulness        experiment runs   │
│                         answer_relevancy     with metrics     │
│                         context_precision                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌──────────────────┬──────────────────┐
        ↓                  ↓                  ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│Drift Detector│  │Alert Manager │  │MLflow Logger │
│              │  │              │  │              │
│Compares with │  │Send Slack    │  │Stores        │
│historical    │  │alerts for    │  │metrics &     │
│runs          │  │drift/results │  │artifacts     │
└──────────────┘  └──────────────┘  └──────────────┘
        ↓                  ↓                  ↓
   Drift Status      Slack Channel       Dashboard
                     Notifications       Visualization
```

---

## 📦 Project Structure

```
llm-eval-monitoring-pipeline/
├── app/                          # Core package
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── eval_engine.py            # Main orchestrator
│   ├── metrics.py                # Evaluation metrics
│   ├── mlflow_logger.py          # MLflow integration
│   ├── drift_detector.py         # Drift detection logic
│   ├── alerts.py                 # Slack/notification alerts
│   └── utils.py                  # Helper functions
│
├── dashboard/
│   └── streamlit_app.py          # Visualization dashboard
│
├── scripts/
│   └── run_eval.py               # Entry point to run pipeline
│
├── data/
│   └── golden_dataset.json       # Golden dataset for evaluation
│
├── tests/
│   ├── test_eval_engine.py
│   └── test_drift_detector.py
│
├── .github/
│   └── workflows/
│       └── eval.yml              # GitHub Actions CI/CD
│
├── .env.example                  # Environment variables template
├── requirements.txt              # Python dependencies
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda
- (Optional) MLflow tracking server
- (Optional) Slack workspace for alerts

### 1. Clone and Install

```bash
# Clone the repository
git clone <repo-url>
cd llm-eval-monitoring-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your settings:

```env
# Model configuration
MODEL_NAME=gpt-3.5-turbo
MODEL_PROVIDER=openai

# Thresholds
FAITHFULNESS_THRESHOLD=0.75
ANSWER_RELEVANCY_THRESHOLD=0.70
CONTEXT_PRECISION_THRESHOLD=0.65

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
EXPERIMENT_NAME=llm_eval_pipeline

# Slack alerts (optional)
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
# ENABLE_SLACK_ALERTS=true
```

### 3. Run Evaluation

```bash
# Run the evaluation pipeline
python scripts/run_eval.py

# View results
cat evaluation_results.json
```

### 4. View Dashboard (Optional)

```bash
# Start MLflow UI
mlflow ui --host 127.0.0.1 --port 5000

# In another terminal, start Streamlit dashboard
streamlit run dashboard/streamlit_app.py
```

---

## 📊 Metrics Explained

### Faithfulness
**What it measures:** Does the model's answer follow from the provided context?  
**Why it matters:** Ensures the model isn't hallucinating or using external knowledge.  
**Fallback calculation:** Proportion of answer words that appear in the context.  
**Threshold:** Default 0.75 (75%)

### Answer Relevancy
**What it measures:** Is the answer relevant to the question?  
**Why it matters:** Ensures the model addresses what was actually asked.  
**Fallback calculation:** Jaccard similarity between question and answer tokens.  
**Threshold:** Default 0.70 (70%)

### Context Precision
**What it measures:** Is the retrieved context relevant to the question?  
**Why it matters:** Measures quality of retrieval before evaluation.  
**Fallback calculation:** Similar to answer relevancy, measured on question and context.  
**Threshold:** Default 0.65 (65%)

### Semantic Similarity
**What it measures:** How similar is the model answer to the ground truth?  
**Why it matters:** Indicates whether the model provided semantically equivalent information.  
**Fallback calculation:** Jaccard similarity on tokens.  
**Note:** This is informational; not used in pass/fail decisions.

---

## 🔄 Drift Detection

The pipeline automatically compares current evaluation results with recent runs to detect performance degradation.

**How it works:**

1. Loads the last N runs from MLflow
2. Calculates average metric values across those runs
3. Compares current metrics against the average
4. Flags drift if any metric drops by more than the threshold (default: 10%)

**Example:**

```python
# Historical average: faithfulness = 0.85
# Current run: faithfulness = 0.75
# Change: -11.8% (exceeds 10% threshold)
# ⚠️  DRIFT DETECTED
```

**Configuration:**

```env
DRIFT_THRESHOLD=0.10              # 10% drop triggers alert
ENABLE_DRIFT_DETECTION=true
ENABLE_SLACK_ALERTS=true
```

---

## 📬 Slack Alerts

### Setup Slack Webhook

1. Go to your Slack workspace → Settings → Apps & Integrations
2. Search for "Incoming Webhooks"
3. Create new webhook, select a channel
4. Copy the webhook URL

### Configure

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ENABLE_SLACK_ALERTS=true
```

### Alert Types

**Evaluation Summary**
```
✅ PASSED Evaluation Pipeline Run

✓ faithfulness: 0.8200 (threshold: 0.7500)
✓ answer_relevancy: 0.7850 (threshold: 0.7000)
✓ context_precision: 0.7100 (threshold: 0.6500)

MLflow Run: `abc12345`
```

**Drift Alert**
```
🚨 Performance Drift Detected

Metrics with drift: faithfulness, answer_relevancy

• faithfulness
  Current: 0.7500
  Historical Avg: 0.8500
  Change: -11.8%

• answer_relevancy
  Current: 0.6800
  Historical Avg: 0.7600
  Change: -10.5%

MLflow Run ID: `xyz98765`
```

---

## 🔗 CI/CD Integration

### GitHub Actions Workflow

The `.github/workflows/eval.yml` file automatically:

1. **Triggers** on push to `main`/`develop` and all PRs
2. **Installs** dependencies
3. **Runs** the evaluation pipeline
4. **Checks** quality thresholds
5. **Uploads** results as artifacts
6. **Comments** on PRs with status

### Using as a Merge Gate

To prevent merging if evaluation fails:

1. Go to repository Settings → Branches
2. Select your branch protection rule
3. Under "Require status checks to pass": check `evaluate`

Now the workflow must pass before merging!

---

## 📈 MLflow Tracking

All evaluation runs are logged to MLflow for experiment tracking.

### View Runs

```bash
# Start MLflow UI
mlflow ui

# View at http://localhost:5000
```

### What's Logged

- **Metrics:** Aggregate statistics for each metric (mean, min, max, count)
- **Parameters:** Model name, dataset path, thresholds, etc.
- **Artifacts:** Full detailed results as JSON
- **Tags:** Run metadata (timestamp, branch, etc.)

### Compare Runs

1. Open MLflow UI (http://localhost:5000)
2. Select runs to compare
3. View side-by-side metric differences
4. Identify performance changes

---

## 🧪 Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_eval_engine.py::TestMetricsEvaluator::test_faithfulness_with_matching_content -v
```

### Test Coverage

- `test_eval_engine.py` - Metrics, thresholds, configuration
- `test_drift_detector.py` - Drift detection logic, edge cases

---

## 🎛️ Configuration Reference

### Environment Variables

```env
# Model
MODEL_NAME                      # LLM model to evaluate (default: gpt-3.5-turbo)
MODEL_PROVIDER                  # Provider: openai, anthropic, etc (default: openai)

# Thresholds
FAITHFULNESS_THRESHOLD          # Min faithfulness score (0-1, default: 0.75)
ANSWER_RELEVANCY_THRESHOLD      # Min relevancy score (0-1, default: 0.70)
CONTEXT_PRECISION_THRESHOLD     # Min precision score (0-1, default: 0.65)

# Paths
GOLDEN_DATASET_PATH             # Path to golden dataset (default: data/golden_dataset.json)
MLFLOW_TRACKING_URI             # MLflow server URI (default: http://localhost:5000)

# MLflow
EXPERIMENT_NAME                 # MLflow experiment name (default: llm_eval_pipeline)

# Alerts
SLACK_WEBHOOK_URL               # Slack webhook for alerts (optional)
ENABLE_SLACK_ALERTS             # Send Slack notifications (default: false)

# Drift
DRIFT_THRESHOLD                 # Performance drop threshold (0-1, default: 0.10)
ENABLE_DRIFT_DETECTION          # Enable drift checking (default: true)

# Evaluation
USE_RAGAS                        # Use RAGAS library if available (default: true)
LOG_LEVEL                        # Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
```

---

## 📝 Golden Dataset Format

The `data/golden_dataset.json` contains evaluation records:

```json
[
  {
    "question": "What is diversification?",
    "retrieved_context": "Diversification spreads investments across...",
    "ground_truth": "Diversification is a strategy that...",
    "model_answer": "Diversification means spreading your investments...",
    "metadata": {
      "category": "portfolio_strategy",
      "difficulty": "easy"
    }
  }
]
```

**Fields:**
- `question` (required) - The question asked
- `retrieved_context` (required) - Context returned by retriever
- `ground_truth` (required) - Reference answer
- `model_answer` (required) - Model's actual answer
- `metadata` (optional) - Any additional info (category, difficulty, etc.)

---

## 🔧 How to Extend

### Add a New Metric

In `app/metrics.py`:

```python
def _evaluate_my_metric(self, question: str, answer: str) -> MetricResult:
    """Evaluate my custom metric."""
    try:
        score = your_evaluation_logic(question, answer)
        return MetricResult(name="my_metric", value=score, success=True)
    except Exception as e:
        return MetricResult(name="my_metric", value=0.0, success=False, error=str(e))

# Add to evaluate_sample():
results["my_metric"] = self._evaluate_my_metric(question, model_answer)
```

### Add a New Alert Channel

In `app/alerts.py`:

```python
def send_email_alert(self, subject: str, body: str) -> bool:
    """Send email alert (e.g., using SendGrid)."""
    try:
        # Your email sending logic
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False
```

### Use Real RAGAS Metrics

Install RAGAS:
```bash
pip install ragas openai
```

Then update `app/metrics.py` to use actual RAGAS implementations.

---

## 📊 Sample Screenshots / Dashboard Features

The Streamlit dashboard provides:

- **Latest Run Section** - Quick view of most recent evaluation
- **Metrics Cards** - Current metric values with visual indicators
- **Recent Runs Table** - History of past evaluations
- **Metric Trends** - Line chart showing metric performance over time
- **Configuration Display** - Current thresholds and settings
- **Auto-refresh** - Updates every 10 seconds (configurable)

To view: `streamlit run dashboard/streamlit_app.py`

---

## 🚧 Future Improvements

- [ ] **Integration with real LLM APIs** - Replace fallback metrics with actual RAGAS + LLM-based evaluation
- [ ] **Automated baseline establishment** - Initial runs to set optimal thresholds
- [ ] **Custom metric builder** - UI to define domain-specific evaluation metrics
- [ ] **Performance comparison dashboard** - Compare across models and datasets
- [ ] **Cost tracking** - Monitor evaluation costs (API calls)
- [ ] **Scheduled evaluations** - Run automatically on a schedule
- [ ] **Multi-model comparison** - Evaluate multiple models in parallel
- [ ] **Advanced visualizations** - Distributions, correlation matrices, etc.
- [ ] **Email/Teams alerts** - Extend beyond Slack
- [ ] **Webhook integration** - Send events to external systems

---

## 🤝 Contributing

This is a portfolio project. Feel free to fork and extend with your own improvements!

---

## 📄 License

MIT License - feel free to use in your portfolio.

---

## 💡 Learning Resources

- [MLflow Documentation](https://www.mlflow.org/docs/latest/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [RAGAS: Evaluation Framework](https://github.com/explodinggradients/ragas)
- [GitHub Actions Workflows](https://docs.github.com/en/actions)

---

## 🎯 Interview Talking Points

1. **End-to-end system thinking** - Built a complete MLOps pipeline from evaluation through alerts and CI/CD
2. **Graceful fallbacks** - System works without external dependencies; optional integrations (RAGAS, Slack, MLflow) enhance it
3. **Production mindset** - Proper error handling, logging, configuration management, testing, and modular architecture

---

## 📧 Support

For questions or issues, feel free to create an issue or reach out!

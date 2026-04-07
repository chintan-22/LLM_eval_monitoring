# Getting Started Guide

This guide walks you through setting up and running the LLM Evaluation & Monitoring Pipeline locally.

## Prerequisites

- **Python 3.8+** - Check with `python --version`
- **pip** or **conda** - Python package manager
- **Git** - For version control
- **(Optional) MLflow** - For experiment tracking
- **(Optional) Slack** - For alert notifications

## Step 1: Initial Setup

### Clone the Repository

```bash
git clone <repository-url>
cd llm-eval-monitoring-pipeline
```

### Create Virtual Environment

```bash
# Using venv (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 2: Configure Environment

### Copy Environment Template

```bash
cp .env.example .env
```

### Edit `.env` File

Open `.env` in your editor and update values:

```env
# Required - but has sensible defaults
MODEL_NAME=gpt-3.5-turbo
FAITHFULNESS_THRESHOLD=0.75
ANSWER_RELEVANCY_THRESHOLD=0.70

# Optional - for MLflow integration
MLFLOW_TRACKING_URI=http://localhost:5000

# Optional - for Slack alerts
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
# ENABLE_SLACK_ALERTS=true
```

## Step 3: Prepare Golden Dataset

The project includes a sample golden dataset at `data/golden_dataset.json` with 5 investment-related Q&A pairs.

**To add your own data:**

1. Create evaluation records in JSON format
2. Each record must have:
   - `question` - The query
   - `retrieved_context` - Retrieved context
   - `ground_truth` - Reference answer
   - `model_answer` - Model's response
   - `metadata` (optional) - Any additional info

**Example:**

```json
[
  {
    "question": "Your question here?",
    "retrieved_context": "Context retrieved by RAG system...",
    "ground_truth": "Expected correct answer...",
    "model_answer": "Model's actual answer...",
    "metadata": {
      "category": "topic",
      "difficulty": "easy"
    }
  }
]
```

3. Save to `data/golden_dataset.json` or update `GOLDEN_DATASET_PATH` in `.env`

## Step 4: Run Evaluation

### Quick Start (Minimal)

```bash
python scripts/run_eval.py
```

This will:
- Load the golden dataset
- Run all evaluation metrics
- Check quality thresholds
- Save results to `evaluation_results.json`
- Exit with appropriate status code

**Example output:**

```
============================================================
Starting LLM Evaluation Pipeline
============================================================
Loading golden dataset...
Loaded 5 records from golden dataset
Running evaluation metrics...
Evaluating sample 1/5
Evaluating sample 2/5
...
Evaluation complete. Metrics computed:
  faithfulness: 0.5322 (min: 0.3333, max: 0.7586)
  answer_relevancy: 0.0615 (min: 0.0312, max: 0.1034)
  ...
============================================================
Evaluation Pipeline Complete
============================================================
```

## Step 5: View Results

### View Evaluation Results

```bash
cat evaluation_results.json
```

### View Metrics in Dashboard (Optional)

**First, start MLflow:**

```bash
mlflow ui
```

Navigate to `http://localhost:5000` in your browser.

**Then, in another terminal, start Streamlit dashboard:**

```bash
streamlit run dashboard/streamlit_app.py
```

Navigate to `http://localhost:8501` in your browser.

## Step 6: Set Up Slack Alerts (Optional)

### Create Slack Webhook

1. Go to your Slack workspace → Settings
2. Search for "Incoming Webhooks" or go to Apps & Integrations
3. Create a new webhook
4. Select the channel where alerts should be posted
5. Copy the webhook URL

### Configure Webhook

Edit `.env`:

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX
ENABLE_SLACK_ALERTS=true
```

### Test Alert

```bash
python3 << 'EOF'
from app.alerts import AlertManager
from app.config import get_config

config = get_config()
manager = AlertManager(slack_webhook_url=config.slack_webhook_url)
manager.send_test_alert()
EOF
```

## Step 7: Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# View coverage
open htmlcov/index.html
```

## Step 8: Set Up CI/CD (Optional)

The project includes a GitHub Actions workflow that automatically runs evaluation on every push and PR.

**No setup needed!** The `.github/workflows/eval.yml` file is already configured.

**What happens automatically:**
- On every push to `main` or `develop`
- On every pull request
- Install dependencies
- Run evaluation
- Check thresholds
- Upload results as artifacts
- Comment on PRs with status

**To use as a merge gate:**

1. Go to repository Settings → Branches
2. Find "Branch protection rules"
3. Enable "Require status checks to pass" → check `evaluate`
4. Now PRs won't merge unless evaluation passes

## Advanced Configuration

### Adjust Thresholds

Edit `.env` to change quality gates:

```env
FAITHFULNESS_THRESHOLD=0.80        # Stricter
ANSWER_RELEVANCY_THRESHOLD=0.75
CONTEXT_PRECISION_THRESHOLD=0.70
DRIFT_THRESHOLD=0.15               # Allow 15% drift instead of 10%
```

### Use RAGAS Library (Advanced)

Install RAGAS:

```bash
pip install ragas openai
```

Then in `.env`:

```env
USE_RAGAS=true
```

The system will automatically use RAGAS metrics when available.

### Change Log Level

```env
LOG_LEVEL=DEBUG    # Verbose logging
LOG_LEVEL=INFO     # Standard
LOG_LEVEL=WARNING  # Only warnings and errors
```

## Troubleshooting

### Issue: "Golden dataset not found"

**Solution:** 
- Check `GOLDEN_DATASET_PATH` in `.env`
- Ensure `data/golden_dataset.json` exists
- Use absolute path if relative path doesn't work

### Issue: "ModuleNotFoundError" when running evaluation

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: MLflow UI not connecting

**Solution:**
```bash
# Check if MLflow is running
mlflow ui --host 127.0.0.1 --port 5000

# Check MLFLOW_TRACKING_URI in .env matches
MLFLOW_TRACKING_URI=http://localhost:5000
```

### Issue: Slack webhooks not working

**Solution:**
- Verify webhook URL in `.env` is correct
- Check `ENABLE_SLACK_ALERTS=true`
- Run test: `python3 -c "from app.alerts import AlertManager; AlertManager('<webhook-url>').send_test_alert()"`

## Next Steps

1. **Replace Golden Dataset** - Add your own Q&A pairs in `data/golden_dataset.json`
2. **Implement Real Metrics** - Install RAGAS and configure actual LLM-based evaluation
3. **Monitor Production** - Set up continuous evaluation in your CI/CD
4. **Extend Alerts** - Add email, Teams, or custom notification channels
5. **Compare Models** - Run multiple models and compare results in MLflow

## File Structure Reminder

```
├── app/                    # Core package
│   ├── eval_engine.py     # Main orchestrator
│   ├── metrics.py         # Evaluation metrics
│   ├── config.py          # Configuration
│   ├── mlflow_logger.py   # Experiment tracking
│   ├── drift_detector.py  # Performance drift detection
│   └── alerts.py          # Slack notifications
├── scripts/
│   └── run_eval.py        # Entry point
├── dashboard/
│   └── streamlit_app.py   # Visualization
├── data/
│   └── golden_dataset.json # Your evaluation data
├── tests/                  # Unit tests
├── .github/workflows/
│   └── eval.yml           # CI/CD automation
└── .env.example           # Configuration template
```

## Support & Questions

- Check `README.md` for full documentation
- Review test files for usage examples
- Examine module docstrings for API reference

Happy evaluating! 🚀

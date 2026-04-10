# Setup Guide for New Users

This guide explains what changes someone needs to make to use this LLM Evaluation & Monitoring Pipeline in their own environment.

## TL;DR - Quick Setup (5 minutes)

```bash
# 1. Clone or download the project
git clone https://github.com/chintan-22/LLM_eval_monitoring.git
cd LLM_eval_monitoring

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your settings (see below)

# 5. Run the pipeline
python scripts/run_eval.py
```

---

## Step-by-Step Configuration

### 1. Clone the Repository

```bash
git clone https://github.com/chintan-22/LLM_eval_monitoring.git
cd LLM_eval_monitoring
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Why:** Isolates project dependencies from system Python.

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**What gets installed:**
- `python-dotenv` - Load configuration from .env
- `pytest` - For running tests
- `streamlit` (optional) - For dashboard
- `mlflow` (optional) - For experiment tracking
- `ragas` (optional) - For advanced metrics
- `requests` (optional) - For Slack alerts

### 4. Create and Configure `.env` File

**Copy the template:**
```bash
cp .env.example .env
```

**Edit `.env` with your settings:**

```bash
# Open in your editor
nano .env    # or vim, vscode, etc.
```

---

## Required Configuration Changes

### A. Model Configuration

```env
# Which LLM model to evaluate
MODEL_NAME=gpt-3.5-turbo
MODEL_PROVIDER=openai

# Alternative options:
# MODEL_NAME=claude-3-sonnet
# MODEL_PROVIDER=anthropic
# 
# MODEL_NAME=llama2
# MODEL_PROVIDER=huggingface
```

**Change this to:** Your LLM model name and provider

---

### B. Quality Thresholds

```env
# Minimum acceptable scores (0.0 to 1.0)
FAITHFULNESS_THRESHOLD=0.75
ANSWER_RELEVANCY_THRESHOLD=0.70
CONTEXT_PRECISION_THRESHOLD=0.65
SEMANTIC_SIMILARITY_THRESHOLD=0.60

# Minimum dataset size for evaluation
MIN_DATASET_SIZE=5
```

**Change these to:** Your quality standards
- Higher = stricter evaluation
- Lower = more lenient
- Example: For critical applications, use 0.85+
- Example: For experimental use, use 0.50+

---

### C. Drift Detection Settings

```env
# Enable/disable drift detection
ENABLE_DRIFT_DETECTION=true

# How much change is acceptable before alert (0.10 = 10%)
DRIFT_THRESHOLD=0.10

# Compare against N previous runs
DRIFT_WINDOW_SIZE=5
```

**Change these to:**
- `ENABLE_DRIFT_DETECTION=false` if you don't want drift monitoring
- `DRIFT_THRESHOLD=0.05` for stricter change detection
- `DRIFT_THRESHOLD=0.20` for more lenient change detection

---

### D. Logging Configuration

```env
# Log level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Log file location
LOG_FILE=logs/evaluation.log
```

**Change to:**
- `DEBUG` for detailed logging (development)
- `INFO` for standard logging (production)
- `WARNING` for minimal logging (minimal noise)

---

### E. MLflow Experiment Tracking (Optional)

```env
# MLflow tracking server URI
MLFLOW_TRACKING_URI=http://localhost:5000

# Experiment name for organizing runs
EXPERIMENT_NAME=llm-evaluation-main

# Use MLflow for logging
USE_MLFLOW=true
```

**To use MLflow:**
1. Install: `pip install mlflow`
2. Start server: `mlflow ui`
3. Set `MLFLOW_TRACKING_URI=http://localhost:5000`
4. Access dashboard: http://localhost:5000

**To disable MLflow:**
- Set `USE_MLFLOW=false` (system will still work)

---

### F. Slack Notifications (Optional)

```env
# Your Slack webhook URL (for alerts)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Whether to send Slack alerts
ENABLE_SLACK_ALERTS=true

# Slack channel (optional, can be set in webhook)
SLACK_CHANNEL=#evaluation-alerts
```

**To set up Slack:**
1. Go to https://api.slack.com/apps
2. Create new app → "From scratch"
3. Name: "LLM Evaluation Alerts"
4. Enable "Incoming Webhooks"
5. "Add New Webhook to Workspace"
6. Copy the webhook URL to `.env`

**To disable Slack:**
- Leave `SLACK_WEBHOOK_URL` empty or set `ENABLE_SLACK_ALERTS=false`

---

### G. RAGAS Advanced Metrics (Optional)

```env
# Use RAGAS for advanced LLM-based evaluation
USE_RAGAS=true

# RAGAS requires API access (uses LLM for evaluation)
RAGAS_MODEL=gpt-3.5-turbo
```

**To use RAGAS:**
1. Install: `pip install ragas`
2. Set `USE_RAGAS=true`
3. System will use it automatically

**Without RAGAS (default):**
- System uses lightweight heuristic metrics
- No external API calls needed
- Works without API keys

---

## Required Code Changes

### 1. Update Golden Dataset

**File:** `data/golden_dataset.json`

**Current structure:**
```json
[
  {
    "question": "...",
    "retrieved_context": "...",
    "ground_truth": "...",
    "model_answer": "...",
    "metadata": {
      "category": "...",
      "difficulty": "..."
    }
  }
]
```

**What to change:**
- Replace the investment Q&A samples with your domain data
- Update `question` - What you're asking the LLM
- Update `retrieved_context` - Relevant information retrieved from knowledge base
- Update `ground_truth` - Expected/ideal answer
- Update `model_answer` - Actual answer from your LLM
- Update `metadata.category` - Your domain categories
- Update `metadata.difficulty` - Your difficulty levels

**Example for Healthcare Domain:**
```json
{
  "question": "What is the recommended dosage for ibuprofen?",
  "retrieved_context": "Ibuprofen is a nonsteroidal anti-inflammatory drug (NSAID). Standard dosage for adults...",
  "ground_truth": "The recommended dose for adults is 200-400mg every 4-6 hours, not to exceed 1200mg daily without doctor supervision.",
  "model_answer": "Adults can take 200-400mg every 4 to 6 hours, with a maximum of 1200mg per day.",
  "metadata": {
    "category": "medications",
    "difficulty": "easy"
  }
}
```

---

### 2. Update Threshold Configurations

**File:** `app/config.py` (if you need to change defaults)

```python
# Current defaults:
FAITHFULNESS_THRESHOLD: float = 0.75
ANSWER_RELEVANCY_THRESHOLD: float = 0.70
CONTEXT_PRECISION_THRESHOLD: float = 0.65
SEMANTIC_SIMILARITY_THRESHOLD: float = 0.60
```

**To change defaults:**
1. Edit `.env` file (recommended) - easier
2. OR edit `app/config.py` lines 20-25

---

### 3. Custom Metrics (Advanced)

**File:** `app/metrics.py`

To add your own metrics:

```python
# Find the MetricsEvaluator class
class MetricsEvaluator:
    
    # Add new method for custom metric
    def _evaluate_custom_metric(self, question: str, answer: str) -> float:
        """
        Your custom metric logic here.
        Should return a value between 0.0 and 1.0
        """
        score = your_scoring_logic(question, answer)
        return score
    
    # Add it to evaluate_sample() method
    def evaluate_sample(self, question, retrieved_context, ground_truth, model_answer):
        result = {
            # ... existing metrics ...
            "custom_metric": self._evaluate_custom_metric(question, model_answer),
        }
        return result
```

---

### 4. Custom Alerts (Advanced)

**File:** `app/alerts.py`

To add custom notifications (email, Teams, Discord, etc.):

```python
class AlertManager:
    
    def send_email_alert(self, metrics, thresholds_passed):
        """Send email alert"""
        # Your email logic
        pass
    
    def send_to_monitoring_system(self, metrics):
        """Send to your monitoring system"""
        # Your system logic
        pass
```

---

### 5. Custom Drift Detection (Advanced)

**File:** `app/drift_detector.py`

The current implementation compares to previous runs. To customize:

```python
class DriftDetector:
    # Modify detect_drift() method to:
    # - Compare to baseline instead of history
    # - Use different statistical tests
    # - Add anomaly detection
```

---

## Optional Customizations

### Add Custom Dataset Loading

**File:** `app/utils.py`

```python
def load_custom_dataset(source: str):
    """Load from your database or API"""
    # Instead of JSON file:
    if source == "database":
        # Load from your database
        pass
    elif source == "api":
        # Load from your API
        pass
```

---

### Add Custom Logging

**File:** `app/utils.py` - `setup_logging()` function

```python
# Add custom handlers:
# - Send to cloud logging (CloudWatch, Datadog, etc.)
# - Database logging
# - Custom formatting
```

---

### Add Custom Dashboard

**File:** `dashboard/streamlit_app.py`

```python
# Customize the dashboard:
# - Add your own charts
# - Change layout
# - Add new metrics visualizations
# - Add export functionality
```

---

## Testing After Setup

```bash
# 1. Run unit tests
python -m pytest tests/ -v

# 2. Run full pipeline
python scripts/run_eval.py

# 3. Check logs
tail -50 logs/evaluation.log

# 4. Launch dashboard (if MLflow running)
streamlit run dashboard/streamlit_app.py
```

---

## Common Setup Issues & Solutions

### Issue 1: `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Make sure you're in project root
cd /path/to/LLM_eval_monitoring

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Run from project root
python scripts/run_eval.py
```

---

### Issue 2: `.env` file not found

**Solution:**
```bash
# Create from template
cp .env.example .env

# Edit it
nano .env
```

---

### Issue 3: `RAGAS not installed` warning

**Solution (if you want RAGAS):**
```bash
pip install ragas
```

**Or (if you don't care):**
- Just ignore the warning - fallback metrics work fine

---

### Issue 4: MLflow connection error

**Solution:**
```bash
# Start MLflow server
mlflow ui

# Or disable MLflow in .env
USE_MLFLOW=false
```

---

### Issue 5: Slack alerts not working

**Solution:**
- Verify webhook URL is correct in `.env`
- Check Slack workspace allows webhooks
- Verify `ENABLE_SLACK_ALERTS=true`

---

## File Structure After Setup

```
LLM_eval_monitoring/
├── app/                          # Core application (don't change structure)
│   ├── __init__.py
│   ├── config.py                 # ← EDIT: Defaults only
│   ├── metrics.py                # ← EDIT: Add custom metrics
│   ├── eval_engine.py
│   ├── drift_detector.py         # ← EDIT: Custom drift logic
│   ├── alerts.py                 # ← EDIT: Add alert types
│   ├── mlflow_logger.py
│   └── utils.py                  # ← EDIT: Custom loading
│
├── data/
│   └── golden_dataset.json       # ← MUST EDIT: Your Q&A data
│
├── scripts/
│   └── run_eval.py               # Run this to start
│
├── dashboard/
│   └── streamlit_app.py          # ← EDIT: Custom dashboard
│
├── tests/                        # ← EDIT: Add tests for custom metrics
│
├── .env                          # ← MUST CREATE: Your configuration
├── .env.example                  # Reference template
├── requirements.txt              # Dependencies
│
├── README.md
├── SETUP.md
└── TESTING_GUIDE.md
```

---

## Summary: Changes Required vs Optional

### 🔴 MUST CHANGE (Required)
1. ✅ Create `.env` file from `.env.example`
2. ✅ Replace `data/golden_dataset.json` with your Q&A data
3. ✅ Update MODEL_NAME and threshold values in `.env`

### 🟡 SHOULD CHANGE (Recommended)
1. Update quality thresholds for your use case
2. Configure MLflow tracking (for experiment management)
3. Set up Slack webhooks (for notifications)
4. Customize log level based on your needs

### 🟢 NICE TO HAVE (Optional)
1. Add custom metrics in `app/metrics.py`
2. Customize dashboard in `dashboard/streamlit_app.py`
3. Add custom drift detection logic
4. Build custom dataset loaders

---

## Next Steps

1. ✅ Follow "TL;DR - Quick Setup" above
2. ✅ Edit `.env` with your configuration
3. ✅ Replace golden dataset with your data
4. ✅ Run `python scripts/run_eval.py`
5. ✅ Check logs and results
6. 🟢 (Optional) Customize for your needs

---

## Getting Help

- **Detailed Testing:** See `TESTING_GUIDE.md`
- **Project Overview:** See `README.md`
- **Quick Commands:** See `QUICK_TEST_COMMANDS.md`
- **Project Structure:** See `PROJECT_MAP.md`

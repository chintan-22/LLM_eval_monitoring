# Changes Other Users Need to Make

Quick reference for what someone needs to change when using this codebase.

---

## 🔴 MUST CHANGE (3 Critical Steps)

### 1. Create `.env` Configuration File

**Location:** Project root directory
**Time:** 2 minutes

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env  # or open in your editor
```

**Critical values to change:**
```env
MODEL_NAME=your-model-name              # e.g., gpt-3.5-turbo, claude-3, llama2
MODEL_PROVIDER=your-provider            # e.g., openai, anthropic, huggingface
FAITHFULNESS_THRESHOLD=0.75             # Change to your quality standard
ANSWER_RELEVANCY_THRESHOLD=0.70         # Change to your quality standard  
CONTEXT_PRECISION_THRESHOLD=0.65        # Change to your quality standard
SEMANTIC_SIMILARITY_THRESHOLD=0.60      # Change to your quality standard
```

---

### 2. Replace Golden Dataset

**Location:** `data/golden_dataset.json`
**Time:** 5-10 minutes

**Current data:** 5 investment/finance Q&A pairs

**You need to:**
- Replace with YOUR domain's Q&A pairs
- Keep the JSON structure the same
- Include at least 5 examples
- Update all 4 fields: `question`, `retrieved_context`, `ground_truth`, `model_answer`

**Example replacement:**

```json
[
  {
    "question": "YOUR QUESTION HERE",
    "retrieved_context": "CONTEXT/INFO FROM YOUR KNOWLEDGE BASE",
    "ground_truth": "EXPECTED/IDEAL ANSWER",
    "model_answer": "ACTUAL ANSWER FROM YOUR LLM",
    "metadata": {
      "category": "your_category",
      "difficulty": "easy/medium/hard"
    }
  }
]
```

**Domain examples:**
- **Healthcare:** Medical Q&A, symptoms, treatments
- **Finance:** Investment, trading, portfolio questions
- **Legal:** Contract Q&A, compliance questions
- **Customer Service:** FAQ, troubleshooting
- **Technical:** API docs, code examples

---

### 3. Update Quality Thresholds (Optional but Recommended)

**Location:** `.env` file
**Time:** 1 minute

**Change these based on your quality requirements:**

```env
# Strict (for critical applications)
FAITHFULNESS_THRESHOLD=0.85
ANSWER_RELEVANCY_THRESHOLD=0.85
CONTEXT_PRECISION_THRESHOLD=0.80
SEMANTIC_SIMILARITY_THRESHOLD=0.80

# Balanced (recommended default)
FAITHFULNESS_THRESHOLD=0.75
ANSWER_RELEVANCY_THRESHOLD=0.70
CONTEXT_PRECISION_THRESHOLD=0.65
SEMANTIC_SIMILARITY_THRESHOLD=0.60

# Lenient (for experimental/development)
FAITHFULNESS_THRESHOLD=0.50
ANSWER_RELEVANCY_THRESHOLD=0.50
CONTEXT_PRECISION_THRESHOLD=0.50
SEMANTIC_SIMILARITY_THRESHOLD=0.50
```

---

## 🟡 SHOULD CHANGE (Configuration & Integrations)

### Optional: Configure MLflow Tracking

**For:** Experiment history and comparison
**Time:** 5 minutes

```env
ENABLE_MLFLOW=true
MLFLOW_TRACKING_URI=http://localhost:5000
EXPERIMENT_NAME=my-llm-evaluation

# Then start MLflow server:
# mlflow ui
# Access at: http://localhost:5000
```

---

### Optional: Setup Slack Alerts

**For:** Get notifications when quality drops
**Time:** 5 minutes

```bash
# 1. Go to https://api.slack.com/apps
# 2. Create new app → "From scratch"
# 3. Name: "LLM Evaluation Alerts"
# 4. In left menu: "Incoming Webhooks" → ON
# 5. "Add New Webhook to Workspace"
# 6. Copy the URL to .env:
```

```env
ENABLE_SLACK_ALERTS=true
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#evaluation-alerts
```

---

### Optional: Enable Advanced Metrics

**For:** Better evaluation using LLM-based metrics
**Time:** 2 minutes

```bash
# Install RAGAS
pip install ragas

# Enable in .env
USE_RAGAS=true
```

---

### Optional: Change Logging Level

**For:** Control verbosity of logs
**Time:** 1 minute

```env
LOG_LEVEL=INFO          # Standard (recommended)
# OR
LOG_LEVEL=DEBUG         # Very detailed (development)
# OR
LOG_LEVEL=WARNING       # Minimal (production)
```

---

### Optional: Adjust Drift Detection

**For:** Monitor if model performance is degrading
**Time:** 1 minute

```env
ENABLE_DRIFT_DETECTION=true
DRIFT_THRESHOLD=0.10        # Alert if >10% drop
DRIFT_WINDOW_SIZE=5         # Compare to last 5 runs
```

---

## 🟢 NICE TO HAVE (Advanced Customizations)

### Add Custom Metrics

**File:** `app/metrics.py`
**Time:** 20-30 minutes

```python
# Add method to MetricsEvaluator class:
def _evaluate_custom_metric(self, question: str, answer: str) -> float:
    """Your custom scoring logic"""
    # Calculate your metric
    score = your_scoring_function(question, answer)
    return score  # Return 0.0 to 1.0

# Add to evaluate_sample():
def evaluate_sample(self, ...):
    return {
        # existing metrics...
        "custom_metric": self._evaluate_custom_metric(question, model_answer),
    }
```

---

### Customize Dashboard

**File:** `dashboard/streamlit_app.py`
**Time:** 30-60 minutes

```python
# Add your own visualizations, charts, tables
# Customize layout
# Add export functionality
# Add custom filters
```

---

### Custom Drift Detection

**File:** `app/drift_detector.py`
**Time:** 20-30 minutes

```python
# Modify detect_drift() to:
# - Compare to baseline vs history
# - Use different statistical methods
# - Add anomaly detection
# - Custom thresholds per metric
```

---

### Custom Alert Types

**File:** `app/alerts.py`
**Time:** 20-30 minutes

Add notifications to:
- Email
- PagerDuty
- Teams
- Discord
- DataDog
- Your monitoring system

---

## Summary Table

| Change | Required? | Time | File | Difficulty |
|--------|-----------|------|------|------------|
| Create `.env` | ✅ YES | 2 min | .env | Easy |
| Replace dataset | ✅ YES | 5-10 min | data/golden_dataset.json | Easy |
| Update thresholds | 🟡 MAYBE | 1 min | .env | Easy |
| MLflow setup | 🟢 NO | 5 min | .env + mlflow | Easy |
| Slack alerts | 🟢 NO | 5 min | .env + Slack API | Easy |
| Custom metrics | 🟢 NO | 30 min | app/metrics.py | Medium |
| Dashboard customization | 🟢 NO | 60 min | dashboard/streamlit_app.py | Medium |
| Drift detection | 🟢 NO | 30 min | app/drift_detector.py | Hard |
| Alert customization | 🟢 NO | 30 min | app/alerts.py | Hard |

---

## Files You Should vs Shouldn't Edit

### ✅ SAFE TO EDIT

```
✓ .env                              (configuration)
✓ data/golden_dataset.json          (your Q&A data)
✓ app/metrics.py                    (add custom metrics)
✓ app/alerts.py                     (add custom alerts)
✓ app/drift_detector.py             (custom drift logic)
✓ app/utils.py                      (custom loading)
✓ dashboard/streamlit_app.py        (customize UI)
✓ tests/                            (add tests)
```

### ⚠️ EDIT WITH CAUTION

```
⚠️ app/config.py                    (only if changing defaults, .env is better)
⚠️ app/eval_engine.py               (core logic, might break things)
⚠️ app/mlflow_logger.py             (optional, works as-is)
⚠️ scripts/run_eval.py              (should work as-is)
```

### ❌ DON'T EDIT

```
✗ app/__init__.py
✗ requirements.txt                  (unless adding new libraries)
✗ .github/workflows/eval.yml        (unless customizing CI/CD)
✗ README.md, TESTING_GUIDE.md, etc  (documentation)
```

---

## Absolute Minimum Setup (Start Here!)

**To get running in 5 minutes:**

```bash
# 1. Create .env
cp .env.example .env

# 2. Edit ONE line
MODEL_NAME=your-model

# 3. Edit data file
# Replace investment Q&A with YOUR Q&A in data/golden_dataset.json

# 4. Run it
python scripts/run_eval.py

# Done! 🎉
```

---

## Recommended Full Setup (30 minutes)

1. ✅ Create `.env` with your model and thresholds
2. ✅ Replace `data/golden_dataset.json` with your Q&A
3. 🟡 Setup MLflow for tracking
4. 🟡 Setup Slack for alerts
5. ✅ Run and verify: `python scripts/run_eval.py`
6. ✅ Check logs: `tail logs/evaluation.log`

---

## After Setup: What's Next?

- **Run tests:** `python -m pytest tests/ -v`
- **Check logs:** `tail -50 logs/evaluation.log`
- **View results:** `cat evaluation_results.json | jq '.'`
- **Start dashboard:** `streamlit run dashboard/streamlit_app.py`
- **Customize:** Add custom metrics, alerts, drift logic

---

## Getting Help

- **Setup issues?** → See `NEW_USER_SETUP.md`
- **Want a checklist?** → See `SETUP_CHECKLIST.md`
- **Need to test?** → See `TESTING_GUIDE.md`
- **How does it work?** → See `README.md` and `PROJECT_MAP.md`
- **Quick commands?** → See `QUICK_TEST_COMMANDS.md`

---

## TL;DR for Impatient People

```bash
cp .env.example .env
# Edit .env: change MODEL_NAME and thresholds
# Edit data/golden_dataset.json: put YOUR data
python scripts/run_eval.py
# Done!
```

That's it! Everything else is optional.

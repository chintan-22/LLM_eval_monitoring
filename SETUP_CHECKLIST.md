# New User Configuration Checklist

Use this checklist when setting up the project in a new environment.

## Pre-Setup Checklist

- [ ] Python 3.8+ installed
- [ ] Git installed (if cloning)
- [ ] Terminal/Command prompt ready
- [ ] Text editor available (VS Code, nano, vim, etc.)

---

## Installation & Setup (10 minutes)

### Step 1: Get the Code
```bash
[ ] git clone https://github.com/chintan-22/LLM_eval_monitoring.git
[ ] cd LLM_eval_monitoring
```

### Step 2: Create Virtual Environment
```bash
[ ] python3 -m venv venv
[ ] source venv/bin/activate  # macOS/Linux
    OR
[ ] venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies
```bash
[ ] pip install --upgrade pip
[ ] pip install -r requirements.txt
```

### Step 4: Create Configuration File
```bash
[ ] cp .env.example .env
[ ] nano .env  (or open in your editor)
```

---

## Critical Configuration Changes

### ✅ REQUIRED - Must Do These

**In `.env` file:**

```
[1] Model Configuration
  [ ] MODEL_NAME = your LLM model (e.g., "gpt-3.5-turbo")
  [ ] MODEL_PROVIDER = provider (e.g., "openai")

[2] Data Configuration
  [ ] DATA_PATH = path to your dataset (usually: data/golden_dataset.json)
  [ ] DATASET_FORMAT = json (or your format)

[3] Quality Thresholds
  [ ] FAITHFULNESS_THRESHOLD = your min score (0.0-1.0)
  [ ] ANSWER_RELEVANCY_THRESHOLD = your min score
  [ ] CONTEXT_PRECISION_THRESHOLD = your min score
  [ ] SEMANTIC_SIMILARITY_THRESHOLD = your min score
```

**Replace your data:**

```
[ ] Open: data/golden_dataset.json
[ ] Replace investment Q&A examples with YOUR questions
[ ] Keep JSON structure same
[ ] Test with at least 5 examples
```

---

### 🟡 RECOMMENDED - Should Do These

**In `.env` file:**

```
[4] MLflow (Experiment Tracking)
  [ ] ENABLE_MLFLOW = true/false
  [ ] MLFLOW_TRACKING_URI = http://localhost:5000
  [ ] EXPERIMENT_NAME = descriptive name

[5] Logging
  [ ] LOG_LEVEL = INFO (or DEBUG/WARNING)
  [ ] LOG_FILE = logs/evaluation.log

[6] Drift Detection
  [ ] ENABLE_DRIFT_DETECTION = true/false
  [ ] DRIFT_THRESHOLD = 0.10 (adjust to your tolerance)
```

**Setup integrations:**

```
[ ] MLflow: pip install mlflow (optional)
[ ] Slack webhook: Create at api.slack.com (optional)
[ ] RAGAS: pip install ragas (optional)
```

---

### 🟢 OPTIONAL - Nice to Have

```
[ ] Advanced customizations in app/*.py files
[ ] Custom metrics in app/metrics.py
[ ] Dashboard customization in dashboard/streamlit_app.py
[ ] Custom drift detection logic
```

---

## Verification Checklist (After Setup)

### Run These Tests

```bash
[ ] 1. Check config loads:
      python -c "from app.config import get_config; print('✓')"

[ ] 2. Check data loads:
      python -c "from app.utils import load_golden_dataset; d=load_golden_dataset('data/golden_dataset.json'); print(f'✓ {len(d)} samples')"

[ ] 3. Run full pipeline:
      python scripts/run_eval.py

[ ] 4. Run unit tests:
      python -m pytest tests/ -v

[ ] 5. Check logs exist:
      ls -la logs/
```

### Expected Results

```
✅ Config loads without errors
✅ Dataset has your Q&A pairs
✅ Pipeline runs and shows metrics
✅ Unit tests pass (13-15/15)
✅ Log file created with timestamps
```

---

## Quick Reference: What to Change

| File/Component | Required? | Changes Needed |
|---|---|---|
| `.env` | ✅ YES | Model name, thresholds, API keys |
| `data/golden_dataset.json` | ✅ YES | Replace with your Q&A data |
| `app/config.py` | 🟡 MAYBE | Only if changing defaults |
| `app/metrics.py` | 🟢 NO | Only if adding custom metrics |
| `app/alerts.py` | 🟢 NO | Only if custom notifications |
| `app/drift_detector.py` | 🟢 NO | Only if custom drift logic |
| `dashboard/streamlit_app.py` | 🟢 NO | Only if customizing dashboard |
| Everything else | ⚫ NO | Don't change |

---

## Configuration File (.env) Template

**Minimal Setup (Just Copy & Edit):**

```env
# MUST CHANGE
MODEL_NAME=gpt-3.5-turbo
MODEL_PROVIDER=openai
FAITHFULNESS_THRESHOLD=0.75
ANSWER_RELEVANCY_THRESHOLD=0.70
CONTEXT_PRECISION_THRESHOLD=0.65
SEMANTIC_SIMILARITY_THRESHOLD=0.60

# OPTIONAL
ENABLE_MLflow=true
MLFLOW_TRACKING_URI=http://localhost:5000
EXPERIMENT_NAME=llm-evaluation
LOG_LEVEL=INFO
ENABLE_DRIFT_DETECTION=true
DRIFT_THRESHOLD=0.10
SLACK_WEBHOOK_URL=
USE_RAGAS=false
```

---

## Common First-Time Issues

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | Make sure venv is activated and pip install -r requirements.txt ran |
| `.env` file not found | Run: `cp .env.example .env` |
| Data not loading | Check `data/golden_dataset.json` exists and has valid JSON |
| Tests failing | Run from project root, make sure venv activated |
| Metrics all 0.0 | Normal! Fallback heuristics are conservative |
| MLflow connection error | Start MLflow with: `mlflow ui` |
| Slack alerts not working | Verify webhook URL and `ENABLE_SLACK_ALERTS=true` |

---

## First Run Commands

```bash
# 1. Activate environment (if not already)
source venv/bin/activate

# 2. Run full pipeline
python scripts/run_eval.py

# 3. Check results
tail -50 logs/evaluation.log

# 4. (Optional) See metrics on dashboard
streamlit run dashboard/streamlit_app.py
```

---

## Success Criteria

You're done when:
- ✅ `.env` created with your configuration
- ✅ `data/golden_dataset.json` has your Q&A pairs
- ✅ `python scripts/run_eval.py` runs without errors
- ✅ Metrics are computed for all samples
- ✅ Thresholds are checked
- ✅ Logs are generated

---

## After Setup: Next Steps

1. **For Understanding the System:**
   - Read `README.md`
   - Read `PROJECT_MAP.md`
   - Read `SUMMARY.md`

2. **For Detailed Testing:**
   - See `TESTING_GUIDE.md`
   - See `QUICK_TEST_COMMANDS.md`

3. **For Customization:**
   - See `NEW_USER_SETUP.md` → "Custom Metrics" section
   - Modify files in `app/` as needed

4. **For Integration:**
   - Set up MLflow for tracking
   - Configure Slack for alerts
   - Integrate with CI/CD pipeline

5. **For Deployment:**
   - Push to GitHub
   - Set up GitHub Actions workflow
   - Deploy to production environment

---

## Support Resources

- **GitHub Issues:** Report bugs or ask questions
- **README.md:** Project overview
- **PROJECT_MAP.md:** Detailed file structure
- **TESTING_GUIDE.md:** How to test everything
- **QUICK_TEST_COMMANDS.md:** Copy-paste commands

---

**Estimated Time to Setup: 10-15 minutes**

**Questions? Start with NEW_USER_SETUP.md for detailed explanations!**

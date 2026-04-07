# Project Navigation Map

Quick guide to understanding the codebase structure and finding what you need.

---

## 🗺️ File Structure Explained

```
llm-eval-monitoring-pipeline/
│
├── 📚 DOCUMENTATION (Start here)
│   ├── README.md           ← Project overview & features
│   ├── SETUP.md            ← Step-by-step setup instructions
│   ├── SUMMARY.md          ← Status & what's included
│   ├── INTERVIEW_GUIDE.md  ← Q&As + talking points
│   ├── RESUME_BULLETS.md   ← Polished achievement statements
│   └── PROJECT_MAP.md      ← This file
│
├── 🔧 CORE APPLICATION (app/)
│   ├── __init__.py         ← Package initialization
│   ├── config.py           ← Configuration from env vars
│   ├── eval_engine.py      ← Main orchestrator (START HERE)
│   ├── metrics.py          ← Evaluation metrics
│   ├── mlflow_logger.py    ← MLflow integration
│   ├── drift_detector.py   ← Drift detection
│   ├── alerts.py           ← Slack alerts
│   └── utils.py            ← Helper functions
│
├── 🚀 SCRIPTS (scripts/)
│   └── run_eval.py         ← Entry point to run pipeline
│
├── 📊 DASHBOARD (dashboard/)
│   └── streamlit_app.py    ← Live metrics dashboard
│
├── 📥 DATA (data/)
│   └── golden_dataset.json ← Sample evaluation dataset
│
├── 🧪 TESTS (tests/)
│   ├── test_eval_engine.py ← Core functionality tests
│   └── test_drift_detector.py ← Drift detection tests
│
├── 🔄 CI/CD (.github/workflows/)
│   └── eval.yml            ← GitHub Actions automation
│
├── ⚙️ CONFIGURATION
│   ├── .env.example        ← Configuration template
│   ├── .gitignore          ← Git ignore rules
│   └── requirements.txt    ← Python dependencies
```

---

## 🧭 Navigation Guide by Task

### "I want to understand the project"
1. Start → `README.md` (5 min read)
2. Then → `SUMMARY.md` (status check)
3. Deep dive → `app/eval_engine.py` (main orchestrator)

### "I want to set it up locally"
1. Read → `SETUP.md` (step-by-step)
2. Follow → 7-step installation
3. Run → `python scripts/run_eval.py`

### "I want to understand the code"
1. Entry point → `scripts/run_eval.py`
2. Orchestrator → `app/eval_engine.py`
3. Components:
   - Metrics → `app/metrics.py`
   - Tracking → `app/mlflow_logger.py`
   - Drift → `app/drift_detector.py`
   - Alerts → `app/alerts.py`

### "I want to modify something"
| Component | File | Complexity |
|-----------|------|------------|
| Add metric | `app/metrics.py` | ⭐⭐ |
| Adjust threshold | `app/config.py` | ⭐ |
| Add alert channel | `app/alerts.py` | ⭐⭐ |
| Custom dataset | `data/golden_dataset.json` | ⭐ |
| Change dashboard | `dashboard/streamlit_app.py` | ⭐⭐⭐ |

### "I want to extend to production"
1. Implement real metrics in `app/metrics.py` (replace fallbacks)
2. Set up MLflow server (currently uses local)
3. Configure Slack webhook in `.env`
4. Add your golden dataset to `data/golden_dataset.json`
5. Deploy via GitHub Actions (already configured)

### "I want to prepare for interviews"
1. Read → `INTERVIEW_GUIDE.md` (expect these questions)
2. Study → `RESUME_BULLETS.md` (polish your talking points)
3. Practice → Show code structure + run demo

---

## 🔍 File Deep Dives

### Core Modules Explained

#### `app/config.py` (~60 lines)
**Purpose:** Configuration management  
**Key class:** `EvaluationConfig`  
**What it does:**
- Loads settings from environment variables
- Provides type-safe configuration object
- Validates values on startup

**When to edit:** If adding new configurable settings

---

#### `app/metrics.py` (~350 lines)
**Purpose:** Evaluation metrics computation  
**Key class:** `MetricsEvaluator`  
**What it does:**
- Computes 4 metrics per sample
- Supports RAGAS if available
- Falls back to heuristics if not
- Aggregates batch results

**Metrics:**
1. Faithfulness - Answer grounded in context
2. Answer Relevancy - Answer addresses question
3. Context Precision - Context relevant to question
4. Semantic Similarity - Answer similar to ground truth

**When to edit:** To add new metrics or improve heuristics

---

#### `app/eval_engine.py` (~250 lines)
**Purpose:** Main orchestrator  
**Key class:** `EvaluationEngine`  
**What it does:**
- Loads golden dataset
- Runs metrics on all samples
- Checks thresholds
- Logs to MLflow
- Detects drift
- Sends alerts
- Returns results + exit code

**When to edit:** To change pipeline orchestration logic

---

#### `app/mlflow_logger.py` (~250 lines)
**Purpose:** MLflow integration  
**Key class:** `MLflowLogger`  
**What it does:**
- Connects to MLflow server
- Logs metrics and parameters
- Saves artifacts (detailed results)
- Retrieves recent runs
- Optional (works without MLflow)

**When to edit:** To add custom MLflow functionality

---

#### `app/drift_detector.py` (~120 lines)
**Purpose:** Performance drift detection  
**Key class:** `DriftDetector`  
**What it does:**
- Compares current vs. historical metrics
- Detects drops exceeding threshold
- Formats drift reports
- Configurable threshold (default 10%)

**When to edit:** To change drift detection algorithm

---

#### `app/alerts.py` (~150 lines)
**Purpose:** Notifications  
**Key class:** `AlertManager`  
**What it does:**
- Sends Slack messages via webhook
- Sends evaluation summaries
- Sends drift alerts
- Optional (fails gracefully)

**When to edit:** To add email/Teams/other alert channels

---

#### `app/utils.py` (~150 lines)
**Purpose:** Helper functions  
**Key functions:**
- `load_golden_dataset()` - Load JSON dataset
- `save_evaluation_results()` - Save results
- `setup_logging()` - Configure logging
- `aggregate_metrics()` - Calculate statistics

**When to edit:** When adding utility functions

---

### Scripts

#### `scripts/run_eval.py` (~50 lines)
**Purpose:** Entry point  
**What it does:**
1. Loads configuration
2. Sets up logging
3. Initializes EvaluationEngine
4. Runs evaluation
5. Exits with proper code (0/1/2)

**To run:** `python scripts/run_eval.py`

---

### Dashboard

#### `dashboard/streamlit_app.py` (~200 lines)
**Purpose:** Metrics visualization  
**Sections:**
- Latest run metrics
- Recent runs table
- Metric trends chart
- Configuration display
- Auto-refresh every 10 seconds

**To run:** `streamlit run dashboard/streamlit_app.py`

---

### Tests

#### `tests/test_eval_engine.py` (~150 lines)
**Coverage:**
- Metrics evaluation
- Threshold checking
- Configuration
- Utilities

**To run:** `pytest tests/test_eval_engine.py -v`

---

#### `tests/test_drift_detector.py` (~80 lines)
**Coverage:**
- Drift detection
- Edge cases (no history, missing metrics)
- Report formatting

**To run:** `pytest tests/test_drift_detector.py -v`

---

## 🔗 Data Flow

```
┌─────────────────────────┐
│ scripts/run_eval.py     │
│ (Entry point)           │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ app/config.py           │
│ (Load configuration)    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ app/eval_engine.py      │
│ (Main orchestrator)     │
└────────┬────────────┬───────────┬────────────────┐
         ↓            ↓           ↓                ↓
    ┌────────┐  ┌──────────┐  ┌────────┐  ┌─────────────┐
    │metrics │  │mlflow    │  │drift   │  │alerts       │
    │.py     │  │_logger   │  │detector│  │.py          │
    │        │  │.py       │  │.py     │  │             │
    └────────┘  └──────────┘  └────────┘  └─────────────┘
         ↓            ↓           ↓                ↓
    [Scores]  [MLflow logs] [Drift?]       [Slack msg]
         ↓            ↓           ↓                ↓
    ┌──────────────────────────────────────────────────┐
    │ Evaluation Results                               │
    │ - Metrics computed                               │
    │ - Thresholds checked                             │
    │ - Logged to MLflow                               │
    │ - Drift detected?                                │
    │ - Alerts sent?                                   │
    └──────────────────────────────────────────────────┘
             ↓
    ┌──────────────────────────────────────────────────┐
    │ Exit Code (0=pass, 1=fail, 2=error)             │
    └──────────────────────────────────────────────────┘
```

---

## 🎯 Common Edits

### Add a new metric
1. Open `app/metrics.py`
2. Add method `_evaluate_my_metric()`
3. Add to `evaluate_sample()` results
4. Run tests to verify

### Change thresholds
1. Edit `.env`
2. Modify `FAITHFULNESS_THRESHOLD`, etc.
3. Run `python scripts/run_eval.py`

### Use real RAGAS metrics
1. `pip install ragas openai`
2. Update `app/metrics.py` to use actual RAGAS
3. Configure `.env` with API keys
4. Update `USE_RAGAS=true`

### Add email alerts
1. Install email library (e.g., `pip install sendgrid`)
2. Add method to `app/alerts.py`
3. Call from `eval_engine.py`
4. Test and deploy

### Deploy to production
1. Use GitHub Actions (already configured)
2. Ensure `.env` variables are set as secrets
3. Monitor MLflow for run history
4. Set up Slack for alerts

---

## 📞 Reference Table

| Need | File | Line Count |
|------|------|-----------|
| Understand flow | `eval_engine.py` | 250 |
| Compute metrics | `metrics.py` | 350 |
| Track experiments | `mlflow_logger.py` | 250 |
| Detect drift | `drift_detector.py` | 120 |
| Send alerts | `alerts.py` | 150 |
| Configure | `config.py` | 60 |
| Visualize | `streamlit_app.py` | 200 |
| Run pipeline | `run_eval.py` | 50 |

---

## 🚀 Quick Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Run
python scripts/run_eval.py

# Test
pytest tests/ -v

# Dashboard
streamlit run dashboard/streamlit_app.py

# MLflow
mlflow ui
```

---

## 💡 Tips for Navigation

1. **Start with files in order of size:** Small files are easier to understand first
   - `run_eval.py` (50 lines)
   - `config.py` (60 lines)
   - `drift_detector.py` (120 lines)
   - Then larger files

2. **Follow imports:** If file X imports from file Y, understand Y first

3. **Run tests first:** Tests show usage examples
   ```bash
   pytest tests/ -v
   ```

4. **Use IDE features:**
   - Go to definition (Cmd+click in VS Code)
   - Find all references (Ctrl+K, Ctrl+R)
   - Follow the flow visually

---

## 📚 Documentation Cross-Reference

| Question | Read |
|----------|------|
| How to set up? | SETUP.md |
| How to run? | README.md (Quick Start) |
| What's in the code? | SUMMARY.md |
| How to talk about it? | INTERVIEW_GUIDE.md |
| What to put on resume? | RESUME_BULLETS.md |
| File structure? | This file (PROJECT_MAP.md) |

---

**Last Updated:** 2026-04-07  
**Status:** Complete and ready to explore! 🎉

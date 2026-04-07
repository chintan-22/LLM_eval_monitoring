# ⚡ Quick Start (5 Minutes)

**Get the pipeline running in under 5 minutes.**

## Step 1: Setup Environment (1 min)

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy configuration
cp .env.example .env
```

## Step 2: Run Evaluation (1 min)

```bash
python scripts/run_eval.py
```

**Expected output:**
```
============================================================
Starting LLM Evaluation Pipeline
============================================================
Loading golden dataset...
Loaded 5 records from golden dataset
Running evaluation metrics...
Evaluating sample 1/5
...
Evaluation complete. Metrics computed:
  faithfulness: 0.5322 (min: 0.3333, max: 0.7586)
  answer_relevancy: 0.0615 (min: 0.0312, max: 0.1034)
  context_precision: 0.0434 (min: 0.0233, max: 0.0714)
  semantic_similarity: 0.3647 (min: 0.2250, max: 0.5333)
...
============================================================
Evaluation Pipeline Complete
============================================================
```

## Step 3: View Results (1 min)

```bash
cat evaluation_results.json
```

You'll see:
- All 5 samples evaluated
- 4 metrics per sample
- Aggregate statistics
- Pass/fail status

## Step 4: Run Tests (1 min)

```bash
pytest tests/ -v
```

## Step 5: View Dashboard (1 min)

```bash
# Terminal 1: Start MLflow
mlflow ui

# Terminal 2: Start Streamlit
streamlit run dashboard/streamlit_app.py
```

Visit:
- MLflow: http://localhost:5000
- Dashboard: http://localhost:8501

---

## ✅ You're Done!

The pipeline is now:
- ✅ Installed
- ✅ Configured
- ✅ Running
- ✅ Tested
- ✅ Visualized

## Next Steps

### To Understand the Code
→ Read `PROJECT_MAP.md` (10 min)

### To Prepare for Interviews  
→ Read `INTERVIEW_GUIDE.md` (20 min)

### To Deploy to Production
→ Read `SETUP.md` → Production section (15 min)

### To Customize
1. Edit `data/golden_dataset.json` - Add your Q&A pairs
2. Edit `.env` - Change thresholds
3. Edit `app/metrics.py` - Add new metrics
4. Run again: `python scripts/run_eval.py`

---

**See README.md for full documentation**

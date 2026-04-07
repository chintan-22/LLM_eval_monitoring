"""
Streamlit dashboard for visualizing evaluation pipeline metrics and trends.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

from app.config import get_config
from app.mlflow_logger import MLflowLogger


# Page config
st.set_page_config(
    page_title="LLM Evaluation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .status-pass {
        color: #28a745;
        font-weight: bold;
    }
    .status-fail {
        color: #dc3545;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_mlflow_logger():
    """Get MLflow logger instance (cached)."""
    config = get_config()
    return MLflowLogger(
        tracking_uri=config.mlflow_tracking_uri,
        experiment_name=config.experiment_name
    )


def format_metrics_dataframe(runs: list) -> pd.DataFrame:
    """Convert MLflow runs to a pandas DataFrame for display."""
    data = []
    
    for run in runs:
        row = {
            "Run ID": run["run_id"][:8],
            "Start Time": datetime.fromtimestamp(run["start_time"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Add metrics
        for metric_name, value in run.get("metrics", {}).items():
            if "_mean" in metric_name:
                base_name = metric_name.replace("_mean", "").replace("_", " ").title()
                row[base_name] = f"{value:.4f}"
        
        data.append(row)
    
    return pd.DataFrame(data)


def main():
    """Main dashboard application."""
    
    # Header
    st.title("📊 LLM Evaluation & Monitoring Pipeline")
    st.markdown("Real-time monitoring of LLM response quality and performance trends")
    
    # Sidebar
    st.sidebar.title("Configuration")
    config = get_config()
    st.sidebar.write(f"**Model:** {config.model_name}")
    st.sidebar.write(f"**Experiment:** {config.experiment_name}")
    
    refresh_interval = st.sidebar.slider(
        "Refresh Interval (seconds)",
        min_value=5,
        max_value=60,
        value=10
    )
    
    # Get MLflow data
    mlflow_logger = get_mlflow_logger()
    
    if not mlflow_logger.available:
        st.error("❌ MLflow not available. Please ensure MLflow is installed and tracking server is running.")
        st.stop()
    
    # Fetch recent runs
    recent_runs = mlflow_logger.get_recent_runs(limit=10)
    
    if not recent_runs:
        st.warning("⚠️ No evaluation runs found. Run the evaluation pipeline first.")
        st.stop()
    
    # Latest run section
    st.header("📈 Latest Run")
    
    latest_run = recent_runs[0]
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Run ID",
            value=latest_run["run_id"][:8]
        )
    
    with col2:
        start_time = datetime.fromtimestamp(latest_run["start_time"] / 1000)
        st.metric(
            label="Started",
            value=start_time.strftime("%H:%M:%S")
        )
    
    with col3:
        end_time = datetime.fromtimestamp(latest_run["end_time"] / 1000) if latest_run.get("end_time") else None
        duration = (end_time - start_time).total_seconds() if end_time else 0
        st.metric(
            label="Duration",
            value=f"{duration:.1f}s"
        )
    
    # Metrics display
    st.subheader("Metrics")
    
    metrics_cols = st.columns(4)
    metric_names = []
    
    for metric_name, value in latest_run.get("metrics", {}).items():
        if "_mean" in metric_name:
            base_name = metric_name.replace("_mean", "").replace("_", " ").title()
            metric_names.append((base_name, value))
    
    for idx, (name, value) in enumerate(metric_names):
        with metrics_cols[idx % 4]:
            color = "🟢" if value >= 0.7 else "🟡" if value >= 0.5 else "🔴"
            st.metric(label=name, value=f"{value:.4f}", delta=f"{value*100:.1f}%")
    
    # Recent runs table
    st.header("📋 Recent Runs")
    
    runs_df = format_metrics_dataframe(recent_runs[:5])
    st.dataframe(runs_df, use_container_width=True, hide_index=True)
    
    # Metric trends
    st.header("📊 Metric Trends")
    
    # Extract metric names and values over time
    metric_names_set = set()
    for run in recent_runs:
        for metric_name in run.get("metrics", {}).keys():
            if "_mean" in metric_name:
                metric_names_set.add(metric_name.replace("_mean", ""))
    
    if metric_names_set:
        selected_metric = st.selectbox(
            "Select metric to view trend",
            list(metric_names_set)
        )
        
        # Build trend data
        trend_data = {
            "Run": [],
            "Value": [],
            "Timestamp": []
        }
        
        for idx, run in enumerate(recent_runs[::-1]):  # Reverse for chronological order
            metric_key = f"{selected_metric}_mean"
            if metric_key in run.get("metrics", {}):
                trend_data["Run"].append(idx + 1)
                trend_data["Value"].append(run["metrics"][metric_key])
                start_time = datetime.fromtimestamp(run["start_time"] / 1000)
                trend_data["Timestamp"].append(start_time)
        
        if trend_data["Value"]:
            trend_df = pd.DataFrame(trend_data)
            st.line_chart(trend_df.set_index("Run")["Value"])
        else:
            st.info(f"No data available for {selected_metric}")
    
    # Configuration display
    st.header("⚙️ Configuration")
    
    config_cols = st.columns(3)
    
    with config_cols[0]:
        st.write(f"**Model:** {config.model_name}")
        st.write(f"**Provider:** {config.model_provider}")
    
    with config_cols[1]:
        st.write(f"**Faithfulness Threshold:** {config.faithfulness_threshold}")
        st.write(f"**Relevancy Threshold:** {config.answer_relevancy_threshold}")
    
    with config_cols[2]:
        st.write(f"**Drift Threshold:** {config.drift_threshold:.1%}")
        st.write(f"**Drift Detection:** {'Enabled' if config.enable_drift_detection else 'Disabled'}")
    
    # Auto-refresh
    st.markdown("---")
    import time
    time.sleep(refresh_interval)
    st.rerun()


if __name__ == "__main__":
    main()

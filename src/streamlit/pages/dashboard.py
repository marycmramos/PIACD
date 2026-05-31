import streamlit as st
import pandas as pd
import plotly.express as px
import html
import os
import json
import base64

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

PALETTE_LIGHT = ["#83BCD4", "#A4D1E0", "#B1DEE0", "#DEF7D2", "#8EE8B7"]
PALETTE_DARK = ["#1A3A4A", "#1F4D5C", "#1E5A5C", "#1A4228", "#0F5C38"]

if not st.session_state.get("user"):
    st.warning("Please log in to access the dashboard.")
    st.switch_page("CES.py")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.stApp {
    background: linear-gradient(270deg, #e8f6fa, #eefaf6, #f4fdf0, #f0fdf8);
    background-size: 600% 600%;
    animation: gradientBG 18s ease infinite;
    color: #1a3a4a;
}
.card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    padding: 20px;
    border-radius: 18px;
    margin-bottom: 20px;
    box-shadow: 0 8px 25px rgba(131, 188, 212, 0.15);
}
div[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.75);
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 4px 15px rgba(131, 188, 212, 0.12);
    border: 1px solid rgba(164, 209, 224, 0.35);
}
[data-testid="stMetricLabel"] {
    color: #1a3a4a !important;
}
[data-testid="stMetricValue"] {
    color: #1E5A5C !important;
}
h1, h2, h3 {
    font-weight: 600;
    color: #1a3a4a;
    letter-spacing: -0.3px;
}
[data-testid="stHeader"] {
    background: transparent;
}
.logo-container {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0 0 0;
}
.logo-container img.logo {
    height: 56px;
    object-fit: contain;
}
.logo-container img.nome {
    height: 36px;
    object-fit: contain;
}
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(164, 209, 224, 0.3);
}
</style>
""", unsafe_allow_html=True)


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


logo_path = "src/utils/LOGO_claro.png"
nome_path = "src/utils/NOME_claro.png"

if os.path.exists(logo_path) and os.path.exists(nome_path):
    logo_b64 = img_to_base64(logo_path)
    nome_b64 = img_to_base64(nome_path)
    st.markdown(f"""
        <div class="logo-container">
            <img class="logo" src="data:image/png;base64,{logo_b64}" alt="logo">
            <img class="nome" src="data:image/png;base64,{nome_b64}" alt="nome">
        </div>
    """, unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(255, 255, 255, 0.5)",
    plot_bgcolor="rgba(255, 255, 255, 0.3)",
    font=dict(color="#1a3a4a", family="Poppins"),
)


@st.cache_data
def load_best_params():
    path = os.path.join(ROOT_DIR, "data", "models", "best_params.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


@st.cache_data
def load_predictions():
    path = os.path.join(ROOT_DIR, "data", "results", "full_predictions.json")
    if not os.path.exists(path):
        st.warning("File not found.")
        return pd.DataFrame()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        if df.empty:
            st.error(
                "Empty dataset after merge. Please check timestamps"
                " between features and predictions."
            )
            st.stop()
        df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.tz_localize(None)
        return df
    except Exception as e:
        st.error(f"Error reading JSON: {e}")
        return pd.DataFrame()


@st.cache_data
def load_weather():
    path = os.path.join(ROOT_DIR, "data", "processed", "features.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df.rename(columns={"timestamp": "Timestamp"}, inplace=True)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.tz_localize(None)
    return df[["Timestamp", "temperature"]]


@st.cache_data
def load_merged_data():
    pred_path = os.path.join(ROOT_DIR, "data", "results", "test_predictions.json")
    feat_path = os.path.join(ROOT_DIR, "data", "features.csv")
    if not os.path.exists(pred_path) or not os.path.exists(feat_path):
        return pd.DataFrame()
    try:
        with open(pred_path, "r", encoding="utf-8") as f:
            pred = pd.DataFrame(json.load(f))
        features = pd.read_csv(feat_path)
        pred["Timestamp"] = pd.to_datetime(pred["Timestamp"]).dt.tz_localize(None)
        features["Timestamp"] = pd.to_datetime(features["Timestamp"])
        return pd.merge(features, pred, on="Timestamp", how="left")
    except Exception as e:
        st.error(f"Error in merge: {e}")
        return pd.DataFrame()


best = load_best_params()
df = load_predictions()
weather = load_weather()
if not weather.empty and not df.empty:
    df = df.merge(weather, on="Timestamp", how="left")
username_safe = html.escape(st.session_state['user']['username'])

st.markdown('<div class="title">Energy Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown(f"<div class='small'>Active Session: <b>{username_safe}</b></div>", unsafe_allow_html=True)
st.write("---")


# System Overview
st.subheader("System Overview")

if not df.empty:
    demand_col = "Actual Demand (MW)"
    demand_peak = df[demand_col].max()
    demand_avg = df[demand_col].mean()
    demand_min = df[demand_col].min()
    latest_ts = df["Timestamp"].max()

    temp_col = next(
        (c for c in df.columns if "temp" in c.lower() or "temperature" in c.lower()), None
    )
    temp_value = f"{df[temp_col].mean():.1f} °C" if temp_col else "N/D"

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Average Demand",      f"{demand_avg/1000:.1f} MW")
    c2.metric("Peak Demand",         f"{demand_peak/1000:.0f} MW")
    c3.metric("Minimum Demand",      f"{demand_min/1000:.0f} MW")
    c4.metric("Average Temperature", temp_value)
    c5.metric("Latest Update",       latest_ts.strftime("%m-%d %H:%M"))
else:
    st.info("No data available.")

st.write("---")


# Climate Impact
if not df.empty and "Temperature" in df.columns:
    st.subheader("Climate Impact on Demand")
    fig = px.scatter(
        df,
        x="Temperature",
        y="Actual Demand (MW)",
        trendline="ols",
        opacity=0.6,
        color_discrete_sequence=["#1A3A4A"],
    )
    fig.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)


# Demand by Hour
if not df.empty:
    st.subheader("Demand by Hour of Day")
    df["Hour"] = df["Timestamp"].dt.hour
    hourly = df.groupby("Hour")["Actual Demand (MW)"].mean().reset_index()
    fig = px.bar(
        hourly,
        x="Hour",
        y="Actual Demand (MW)",
        color="Actual Demand (MW)",
        color_continuous_scale=["#A4D1E0", "#1F4D5C"],
    )
    fig.update_layout(xaxis=dict(dtick=1), coloraxis_showscale=False, **CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

# Seasonal Comparison
if not df.empty and "Timestamp" in df.columns:
    st.subheader("Seasonal Demand Comparison")
    df["Month"] = df["Timestamp"].dt.month

    def get_season(m):
        if m in [12, 1, 2]:
            return "Winter"
        elif m in [3, 4, 5]:
            return "Spring"
        elif m in [6, 7, 8]:
            return "Summer"
        else:
            return "Autumn"

    df["Season"] = df["Month"].apply(get_season)
    seasonal = df.groupby("Season")["Actual Demand (MW)"].mean().reindex(
        ["Winter", "Spring", "Summer", "Autumn"]
    ).reset_index()

    season_colors = {
        "Winter": "#1A3A4A",
        "Spring": "#0F5C38",
        "Summer": "#64BB8B",
        "Autumn": "#306A7E",
    }

    fig = px.bar(
        seasonal,
        x="Season",
        y="Actual Demand (MW)",
        color="Season",
        color_discrete_map=season_colors,
    )
    fig.update_layout(showlegend=False, **CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

st.write("---")


# Last 24h
st.subheader("Last 24h - Real vs Prevision")

if not df.empty and best:
    pred_col = "Predicted RF" if best["best_model"] == "random_forest" else "Predicted LR"
    last_24h = df.sort_values("Timestamp").tail(24)
    fig_24h = px.line(
        last_24h,
        x="Timestamp",
        y=["Actual Demand (MW)", pred_col],
        labels={"value": "MW", "variable": "Série"},
        color_discrete_sequence=["#1A3A4A", "#8EE8B7"],
    )
    fig_24h.update_traces(selector={"name": "Actual Demand (MW)"}, line=dict(width=2.5))
    fig_24h.update_traces(selector={"name": pred_col}, line=dict(width=2.5))
    fig_24h.update_layout(hovermode="x unified", **CHART_LAYOUT)
    st.plotly_chart(fig_24h, use_container_width=True)
    st.caption(
        f"Using the best model found by the grid search: **{best['best_model']}**.",
        help="To explore other periods and models, go to the **Predictions** page.",
    )
else:
    st.info("No prediction data available.")


# Best Model Metrics
if best:
    best_model_key = best["best_model"]
    m = best[best_model_key]
    params = m["params"]

    c1, c2, c3 = st.columns(3)
    c1.metric("MAE",  f"{m['mae']:.2f} MW")
    c2.metric("RMSE", f"{m['rmse']:.2f} MW")
    c3.metric("R²",   f"{m['r2']:.4f}")

    with st.expander("Model Parameters"):
        if best_model_key == "random_forest":
            param_labels = {
                "n_estimators":      ("Number of Trees",    params.get("n_estimators")),
                "max_depth":         ("Max Depth",          params.get("max_depth", "No limit")),
                "min_samples_split": ("Min. Samples Split", params.get("min_samples_split")),
                "min_samples_leaf":  ("Min. Samples Leaf",  params.get("min_samples_leaf")),
                "bootstrap":         (
                    "Bootstrap",
                    "Yes" if params.get("bootstrap", True) else "No"
                ),
            }
        else:
            param_labels = {
                "fit_intercept": (
                    "Fit Intercept",
                    "Yes" if params.get("fit_intercept", True) else "No"
                ),
                "positive": (
                    "Positive",
                    "Yes" if params.get("positive", False) else "No"
                ),
            }
        cols = st.columns(len(param_labels))
        for col, (_, (label, value)) in zip(cols, param_labels.items()):
            col.metric(label, value)
else:
    st.info(
        "Grid search yet to be executed. "
        "Go to the **Model Training** page "
        "to run the search and find the best model."
    )

st.write("---")


# Model Comparison
if best:
    st.subheader("Model Performance Comparison")
    comp_df = pd.DataFrame({
        "Model": ["Linear Regression", "Random Forest"],
        "MAE":   [best["linear_regression"]["mae"],  best["random_forest"]["mae"]],
        "RMSE":  [best["linear_regression"]["rmse"], best["random_forest"]["rmse"]],
    })
    fig = px.bar(
        comp_df,
        x="Model",
        y=["MAE", "RMSE"],
        barmode="group",
        color_discrete_sequence=["#1F7561", "#53A08E"]
    )
    fig.update_layout(**CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

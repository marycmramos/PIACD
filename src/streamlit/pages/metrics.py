import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import glob
import base64

st.set_page_config(page_title="Metrics", layout="wide")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

if not st.session_state.get("user"):
    st.warning("Please log in to access the metrics.")
    st.switch_page("pages/1_Login.py")


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

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

[data-testid="stAppViewContainer"],
[data-testid="stMainBlockContainer"] {
    background: transparent;
}

div[data-testid="metric-container"] {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 15px rgba(131, 188, 212, 0.12);
    border: 1px solid rgba(164, 209, 224, 0.35);
    transition: transform 0.2s ease;
}
div[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
}
[data-testid="stMetricLabel"] { color: #1a3a4a !important; }
[data-testid="stMetricValue"] { color: #1E5A5C !important; }

section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(164, 209, 224, 0.3);
}

h1, h2, h3 {
    font-weight: 600;
    color: #1a3a4a;
    letter-spacing: -0.3px;
}

[data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.6);
    border-radius: 12px;
}

/* TABS */
button[data-baseweb="tab"] {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    color: #1F4D5C !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #1A3A4A !important;
    border-bottom-color: #1E5A5C !important;
}
[data-baseweb="tab-highlight"] { background-color: #1E5A5C !important; }
[data-baseweb="tab-border"]    { background-color: rgba(164, 209, 224, 0.4) !important; }

/* TITLE WITH LOGO */
.title-with-logo {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 0.5rem;
    margin-top: 0.5rem;
}
.title-with-logo img {
    height: 52px;
    object-fit: contain;
}
.title-with-logo h1 {
    margin: 0;
    font-size: 2.6rem;
    font-weight: 800;
    color: #1a3a4a;
    letter-spacing: -0.5px;
}

/* BUTTON */
.stButton > button {
    background: linear-gradient(135deg, #1F4D5C, #1E5A5C) !important;
    color: white !important;
    border-radius: 12px;
    height: 3em;
    font-weight: 600;
    font-family: 'Poppins', sans-serif;
    border: none;
    transition: 0.3s;
}
.stButton > button:hover {
    transform: scale(1.02);
    background: linear-gradient(135deg, #1A3A4A, #1F4D5C) !important;
}
</style>
""", unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(255, 255, 255, 0.5)",
    plot_bgcolor="rgba(255, 255, 255, 0.3)",
    font=dict(color="#1a3a4a", family="Poppins"),
)

# Paleta consistente com o resto da app
COLOR_DARK = "#1A3A4A"
COLOR_MID = "#1E5A5C"
COLOR_LIGHT = "#A4D1E0"
COLOR_SCALE = [[0, "#A4D1E0"], [1, "#1F4D5C"]]

# Logo
logo_path = os.path.join(ROOT_DIR, "src", "utils", "LOGO_claro.png")
logo_b64 = None
if os.path.exists(logo_path):
    logo_b64 = img_to_base64(logo_path)

# Título
if logo_b64:
    st.markdown(f"""
        <div class="title-with-logo">
            <img src="data:image/png;base64,{logo_b64}" alt="logo">
            <h1>Metrics</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='font-size:2.6rem; font-weight:800;'>Metrics</h1>", unsafe_allow_html=True)


# Data loaders
@st.cache_data
def load_latest_results():
    path = os.path.join(ROOT_DIR, "data", "results")
    files = glob.glob(os.path.join(path, "results_*.json"))
    if not files:
        return None
    latest = max(files, key=os.path.getctime)
    with open(latest, "r") as f:
        return json.load(f)


@st.cache_data
def load_latest_residuals():
    path = os.path.join(ROOT_DIR, "data", "results")
    files = glob.glob(os.path.join(path, "residuals_*.json"))
    if not files:
        return pd.DataFrame()
    latest = max(files, key=os.path.getctime)
    return pd.read_json(latest)


@st.cache_data
def load_performance_log():
    path = os.path.join(ROOT_DIR, "logs", "performance.log")
    if not os.path.exists(path):
        return []
    entries = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                parts = line.split(" - ", 1)
                timestamp = parts[0].strip()
                message = parts[1].strip()
                label, duration = message.rsplit(":", 1)
                seconds = float(duration.strip().replace(" seconds", ""))
                entries.append({
                    "Timestamp": timestamp,
                    "Componente": label.strip(),
                    "Duração (s)": seconds
                })
            except Exception:
                continue
    return entries


results = load_latest_results()
residuals_df = load_latest_residuals()
perf_entries = load_performance_log()

if not results:
    st.warning("No results available. Run the training pipeline to generate metrics.")
    st.stop()


# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Models",
    "Residuals",
    "Overfitting",
    "Features",
    "Performance",
])


# =============================
# TAB 1 - MODELOS
# =============================
with tab1:
    st.subheader("Model Comparison")

    comparison_data = {
        "Model": ["Naive Baseline (lag 1h)", "Linear Regression", "Random Forest"],
        "MAE (MW)": [
            results["baseline"]["mae"],
            results["linear_regression"]["mae"],
            results["random_forest"]["mae"],
        ],
        "RMSE (MW)": [
            results["baseline"]["rmse"],
            results["linear_regression"]["rmse"],
            results["random_forest"]["rmse"],
        ],
        "R²": [
            results["baseline"]["r2"],
            results["linear_regression"]["r2"],
            results["random_forest"]["r2"],
        ],
        "Improvement in MAE vs Baseline": [
            "-",
            f"{results['improvement_vs_baseline']['lr']:+.2f} MW",
            f"{results['improvement_vs_baseline']['rf']:+.2f} MW",
        ],
    }

    df_comparison = pd.DataFrame(comparison_data)
    best_mae_idx = df_comparison["MAE (MW)"].iloc[1:].idxmin()

    def highlight_best(row):
        if row.name == best_mae_idx:
            return ["background-color: rgba(30,90,92,0.15); font-weight: bold;"] * len(row)
        return [""] * len(row)

    st.dataframe(
        df_comparison.style
        .format({"MAE (MW)": "{:.2f}", "RMSE (MW)": "{:.2f}", "R²": "{:.4f}"},
                subset=["MAE (MW)", "RMSE (MW)", "R²"])
        .apply(highlight_best, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    models = ["Naive Baseline", "Linear Regression", "Random Forest"]
    mae_vals = [results["baseline"]["mae"], results["linear_regression"]["mae"], results["random_forest"]["mae"]]
    rmse_vals = [results["baseline"]["rmse"], results["linear_regression"]["rmse"], results["random_forest"]["rmse"]]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="MAE",  x=models, y=mae_vals,  marker_color=COLOR_DARK))
    fig_bar.add_trace(go.Bar(name="RMSE", x=models, y=rmse_vals, marker_color=COLOR_MID))
    fig_bar.update_layout(barmode="group", yaxis_title="MW",
                          legend=dict(orientation="h", y=1.1), **CHART_LAYOUT)
    st.plotly_chart(fig_bar, use_container_width=True)


# =============================
# TAB 2 - RESÍDUOS
# =============================
with tab2:
    st.subheader("Residual Analysis (Random Forest)")

    if not residuals_df.empty:
        ra = results.get("residual_analysis", {})

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Mean",   f"{ra.get('mean', 0):.2f} MW")
        c2.metric("Std Dev", f"{ra.get('std',  0):.2f} MW")
        c3.metric("Minimum",  f"{ra.get('min',  0):.2f} MW")
        c4.metric("Maximum",  f"{ra.get('max',  0):.2f} MW")

        col1, col2 = st.columns(2)

        with col1:
            res_values, res_bins = pd.cut(
                residuals_df["residual"],
                bins=40,
                retbins=True,
                labels=False
            )
            res_counts = res_values.value_counts().sort_index()
            res_centers = [(res_bins[i] + res_bins[i + 1]) / 2 for i in range(len(res_bins) - 1)]
            res_counts_list = [res_counts.get(i, 0) for i in range(len(res_centers))]

            fig_hist = go.Figure(go.Bar(
                x=res_centers,
                y=res_counts_list,
                marker=dict(
                    color=res_counts_list,
                    colorscale=COLOR_SCALE,
                    showscale=False,
                ),
            ))
            fig_hist.add_vline(x=0, line_dash="dash", line_color="#83BCD4")
            fig_hist.update_layout(
                xaxis_title="Residual (MW)",
                yaxis_title="count",
                **CHART_LAYOUT
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            fig_scatter = px.scatter(residuals_df, x="predicted", y="residual",
                                     color_discrete_sequence=[COLOR_MID], opacity=0.5)
            fig_scatter.add_hline(y=0, line_dash="dash", line_color="#83BCD4")
            fig_scatter.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No residual data available.")


# =============================
# TAB 3 - OVERFITTING
# =============================
with tab3:
    st.subheader("Overfitting Analysis (Random Forest)")

    ov = results.get("overfitting_analysis", {})

    if ov:
        train_m = ov.get("train", {})
        test_m = ov.get("test", {})

        df_ov = pd.DataFrame({
            "Set":  ["Train", "Test"],
            "MAE (MW)":  [train_m.get("mae"),  test_m.get("mae")],
            "RMSE (MW)": [train_m.get("rmse"), test_m.get("rmse")],
            "R²":        [train_m.get("r2"),   test_m.get("r2")],
        })

        st.dataframe(
            df_ov.style.format({"MAE (MW)": "{:.2f}", "RMSE (MW)": "{:.2f}", "R²": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )

        fig_ov = go.Figure()
        fig_ov.add_trace(go.Bar(name="Train", x=["MAE", "RMSE"],
                                y=[train_m.get("mae"), train_m.get("rmse")],
                                marker_color=COLOR_DARK))
        fig_ov.add_trace(go.Bar(name="Test",  x=["MAE", "RMSE"],
                                y=[test_m.get("mae"),  test_m.get("rmse")],
                                marker_color=COLOR_MID))
        fig_ov.update_layout(barmode="group", **CHART_LAYOUT)
        st.plotly_chart(fig_ov, use_container_width=True)

        mae_diff = test_m.get("mae", 0) - train_m.get("mae", 0)
        if mae_diff > 500:
            st.warning(f"Difference in MAE: {mae_diff:.2f} MW - possible overfitting.")
        else:
            st.success(f"Difference in MAE: {mae_diff:.2f} MW - model generalizes well.")
    else:
        st.info("No overfitting data available.")


# =============================
# TAB 4 - FEATURE IMPORTANCE
# =============================
with tab4:
    st.subheader("Feature Importance (Random Forest)")

    fi = results.get("feature_importance", {})

    if fi:
        df_fi = (pd.DataFrame(fi.items(), columns=["Feature", "Relevance"])
                 .sort_values("Relevance", ascending=True)
                 .tail(20))

        fig_fi = px.bar(df_fi, x="Relevance", y="Feature", orientation="h",
                        color="Relevance", color_continuous_scale=COLOR_SCALE)
        fig_fi.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_fi, use_container_width=True)
    else:
        st.info("No feature importance data available.")


# =============================
# TAB 5 - PERFORMANCE
# =============================
with tab5:
    st.subheader("Execution Time of Components")

    if perf_entries:
        df_perf = pd.DataFrame(perf_entries)
        df_latest = df_perf.drop_duplicates(subset="Componente", keep="last")

        df_latest = df_latest.rename(columns={
            "Componente": "Component",
            "Duração (s)": "Duration (s)"
        })

        fig_perf = px.bar(
            df_latest.sort_values("Duration (s)", ascending=True),
            x="Duration (s)", y="Component", orientation="h",
            color="Duration (s)", color_continuous_scale=COLOR_SCALE
        )
        fig_perf.update_layout(**CHART_LAYOUT)
        st.plotly_chart(fig_perf, use_container_width=True)

        with st.expander("View complete log"):
            df_display = df_perf.rename(columns={
                "Componente": "Component",
                "Duração (s)": "Duration (s)"
            })
            st.dataframe(df_display.sort_values("Timestamp", ascending=False),
                         use_container_width=True, hide_index=True)
    else:
        st.info("No performance data available.")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import joblib
import math
import base64
from datetime import datetime, time


def get_project_root():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    while not os.path.exists(os.path.join(current_dir, "data")):
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            return os.path.abspath(os.path.dirname(__file__))
        current_dir = parent_dir
    return current_dir


ROOT_DIR = get_project_root()
MODELS_DIR = os.path.join(ROOT_DIR, "data", "models")

if not st.session_state.get("user"):
    st.warning("Please log in to access the predictions.", icon=":material/lock:")
    st.switch_page("CES.py")


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

/* PREDICTION CARD */
.prediction-card {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(15px);
    padding: 30px;
    border-radius: 20px;
    border: 1px solid rgba(164, 209, 224, 0.35);
    text-align: center;
    box-shadow: 0 8px 25px rgba(131, 188, 212, 0.15);
}
.result-value {
    font-size: 3rem;
    font-weight: 800;
    color: #1A3A4A;
}

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

/* SLIDERS - cor do thumb e fill */
div[data-baseweb="slider"] div[role="slider"] {
    background-color: #1E5A5C !important;
    border-color: #1E5A5C !important;
}
div[data-baseweb="slider"] div[class*="Track"] > div:first-child {
    background-color: #1E5A5C !important;
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


# Logo apenas para o título
logo_path = os.path.join(ROOT_DIR, "src", "utils", "LOGO_claro.png")

logo_b64 = None
if os.path.exists(logo_path):
    logo_b64 = img_to_base64(logo_path)


CHART_LAYOUT = dict(
    paper_bgcolor="rgba(255, 255, 255, 0.5)",
    plot_bgcolor="rgba(255, 255, 255, 0.3)",
    font=dict(color="#1a3a4a", family="Poppins"),
)


# Data loaders
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
        df["Timestamp"] = pd.to_datetime(df["Timestamp"]).dt.tz_localize(None)
        return df
    except Exception as e:
        st.error(f"Error reading JSON: {e}")
        return pd.DataFrame()


@st.cache_data
def load_best_params():
    path = os.path.join(ROOT_DIR, "data", "models", "best_params.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


@st.cache_resource
def load_model(model_name):
    file_name = "rf_model.pkl" if model_name == "Random Forest" else "lr_model.pkl"
    path = os.path.join(MODELS_DIR, file_name)
    if os.path.exists(path):
        return joblib.load(path)
    return None


@st.cache_resource
def load_training_columns():
    path = os.path.join(MODELS_DIR, "X_train.pkl")
    if os.path.exists(path):
        return joblib.load(path).columns.tolist()
    return None


# Header
df = load_predictions()
best = load_best_params()

if logo_b64:
    st.markdown(f"""
        <div class="title-with-logo">
            <img src="data:image/png;base64,{logo_b64}" alt="logo">
            <h1>Predictions</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<h1 style='font-size:2.6rem; font-weight:800;'>Predictions</h1>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("Filtros")

model_choice = st.sidebar.selectbox(
    "Modelo",
    ["Random Forest", "Linear Regression"],
    index=0 if (best and best["best_model"] == "random_forest") else 1
)

pred_col = "Predicted RF" if model_choice == "Random Forest" else "Predicted LR"
key = "random_forest" if model_choice == "Random Forest" else "linear_regression"

if not df.empty:
    min_date = df["Timestamp"].min().date()
    max_date = df["Timestamp"].max().date()
    date_range = st.sidebar.date_input(
        "Período", value=(min_date, max_date),
        min_value=min_date, max_value=max_date
    )
    if len(date_range) == 2:
        start = pd.to_datetime(date_range[0])
        end = pd.to_datetime(date_range[1])
        df_filtered = df[(df["Timestamp"] >= start) & (df["Timestamp"] <= end)]
    else:
        df_filtered = df.copy()
else:
    df_filtered = pd.DataFrame()


# Tabs
tab_hist, tab_realtime = st.tabs([
    "Historic",
    "Real-time Prediction",
])


# =============================
# TAB 1 - HISTÓRICO
# =============================
with tab_hist:

    if df_filtered.empty:
        st.warning("No prediction data available.")
        st.stop()

    if best and key in best:
        m = best[key]
        st.subheader(f"Performance - {model_choice}")
        c1, c2, c3 = st.columns(3)
        c1.metric("MAE",  f"{m['mae']:.2f} MW")
        c2.metric("RMSE", f"{m['rmse']:.2f} MW")
        c3.metric("R²",   f"{m['r2']:.4f}")
        st.write("---")

    st.subheader("Real vs Prediction")
    fig = px.line(
        df_filtered,
        x="Timestamp",
        y=["Actual Demand (MW)", pred_col],
        labels={"value": "MW", "variable": ""},
        color_discrete_sequence=["#1A3A4A", "#5CB1A1"],
    )
    fig.update_traces(selector={"name": "Actual Demand (MW)"}, line=dict(width=2.5))
    fig.update_traces(selector={"name": pred_col}, line=dict(width=2.5))
    fig.update_layout(hovermode="x unified", **CHART_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    # Histograma com gradiente baseado no count
    st.subheader("Distribution of Actual Demand")
    hist_values, hist_bins = pd.cut(
        df_filtered["Actual Demand (MW)"],
        bins=30,
        retbins=True,
        labels=False
    )
    bin_counts = hist_values.value_counts().sort_index()
    bin_centers = [(hist_bins[i] + hist_bins[i + 1]) / 2 for i in range(len(hist_bins) - 1)]
    counts_list = [bin_counts.get(i, 0) for i in range(len(bin_centers))]

    fig2 = go.Figure(go.Bar(
        x=bin_centers,
        y=counts_list,
        marker=dict(
            color=counts_list,
            colorscale=[[0, "#A4D1E0"], [1, "#1F4D5C"]],
            showscale=False,
        ),
    ))
    fig2.update_layout(
        xaxis_title="Actual Demand (MW)",
        yaxis_title="count",
        **CHART_LAYOUT
    )
    st.plotly_chart(fig2, use_container_width=True)


# ===============================
# TAB 2 - PREVISÃO EM TEMPO REAL
# ===============================
with tab_realtime:

    st.write("Configure the energy and climate scenario to obtain an intelligent prediction.")

    # Inputs
    st.subheader("Scenario Settings")

    selected_model = st.selectbox(
        "Select the Model",
        ["Random Forest", "Linear Regression"],
        key="rt_model"
    )

    st.markdown("### Energy Context")
    carga_base = st.slider(
        "Reference Load (MW)",
        min_value=35000.0, max_value=70000.0, value=50000.0, step=100.0,
        help="Define the base level of consumption for the scenario."
    )

    st.markdown("### Climate Variables")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        temp = st.slider("Current Temperature (°C)",   min_value=-10.0, max_value=50.0,  value=20.0, step=0.5)
        temp_min = st.slider("Daily Minimum Temperature (°C)", min_value=-10.0, max_value=45.0,  value=15.0, step=0.5)
        precip = st.slider("Total Precipitation (mm)",  min_value=0.0,   max_value=200.0, value=0.0,  step=0.1)
    with col_t2:
        wind = st.slider("Wind Speed (km/h)",              min_value=0.0,   max_value=150.0,  value=15.0,  step=0.5)
        temp_max = st.slider("Daily Maximum Temperature (°C)", min_value=-10.0, max_value=50.0,   value=25.0,  step=0.5)
        solar = st.slider("Solar Radiation (W/m²)",     min_value=0.0,   max_value=1200.0, value=200.0, step=10.0)

    st.markdown("### Temporal Context")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        data_selecionada = st.date_input("Simulation Date", value=datetime.today())
    with col_d2:
        hora_selecionada = st.time_input("Hour of the Day", value=time(12, 30))

    st.write("")
    predict_btn = st.button(
        "Calculate Prediction",
        use_container_width=True,
        icon=":material/rocket_launch:"
    )

    # Resultado
    st.write("---")
    st.subheader("Results")

    if predict_btn:
        rt_model = load_model(selected_model)
        expected_cols = load_training_columns()

        if rt_model is None:
            st.error(f"Error: The model '{selected_model}' was not found.")
        elif expected_cols is None:
            st.error("Error: Could not load the model structure (X_train.pkl).")
        else:
            try:
                day_of_week = data_selecionada.weekday()
                month = data_selecionada.month
                is_weekend = 1 if day_of_week >= 5 else 0
                hour_decimal = hora_selecionada.hour + (hora_selecionada.minute / 60.0)

                hour_sin = math.sin(2 * math.pi * hour_decimal / 24)
                hour_cos = math.cos(2 * math.pi * hour_decimal / 24)
                dow_sin = math.sin(2 * math.pi * day_of_week / 7)
                dow_cos = math.cos(2 * math.pi * day_of_week / 7)

                temp_range = temp_max - temp_min
                is_day = 1 if 6 <= hour_decimal <= 19 else 0
                temp_x_hour = temp * hour_decimal
                heatwave = 1 if temp_max >= 35 else 0
                cold = 1 if temp_min <= 5 else 0

                features_dict = {
                    "convective_precipitation": precip,
                    "total_precipitation":      precip,
                    "solar_radiation":          solar,
                    "temperature":              temp,
                    "temp_max":                 temp_max,
                    "temp_min":                 temp_min,
                    "wind_speed":               wind,
                    "hour":                     hour_decimal,
                    "day_of_week":              day_of_week,
                    "month":                    month,
                    "is_weekend":               is_weekend,
                    "hour_sin":                 hour_sin,
                    "hour_cos":                 hour_cos,
                    "dow_sin":                  dow_sin,
                    "dow_cos":                  dow_cos,
                    "lag_1h":                   carga_base,
                    "lag_24h":                  carga_base,
                    "lag_168h":                 carga_base,
                    "rolling_load_24h":         carga_base,
                    "rolling_temp_24h":         20.0,
                    "temp_range":               temp_range,
                    "heatwave":                 heatwave,
                    "cold":                     cold,
                    "temp_anomaly":             0,
                    "is_day":                   is_day,
                    "load_diff":                0.0,
                    "temp_x_hour":              temp_x_hour,
                }

                input_df = pd.DataFrame(0.0, index=[0], columns=expected_cols)
                for col in expected_cols:
                    if col in features_dict:
                        input_df.at[0, col] = features_dict[col]

                prediction = rt_model.predict(input_df)[0]

                st.markdown(f"""
                    <div class="prediction-card">
                        <p style="margin-bottom:0; color:#1F4D5C;">
                            Estimated Demand ({selected_model})
                        </p>
                        <div class="result-value">
                            {prediction:.2f}
                            <span style="font-size:1.2rem; color:#1E5A5C;">MW</span>
                        </div>
                        <hr style="border: 0.5px solid rgba(164,209,224,0.5);">
                        <p style="font-size:0.9rem; color:#1F4D5C;">
                            Prediction based on the reference load of {carga_base:,.0f} MW.
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                st.write("")
                if prediction > (carga_base * 1.2):
                    st.warning("Alert: Significant increase in demand detected compared to the reference.")
                elif prediction < (carga_base * 0.8):
                    st.info("Info: Notable reduction in demand compared to the reference load.")
                else:
                    st.success("Demand within expected operational levels.")

                st.write("---")
                st.markdown("### Daily Load Curve")
                st.write("Expected evolution of the grid over 24 hours under these weather conditions.")

                simulacao_horas = []
                simulacao_preds = []

                for h in range(24):
                    feat_sim = features_dict.copy()
                    feat_sim["hour"] = float(h)
                    feat_sim["hour_sin"] = math.sin(2 * math.pi * h / 24)
                    feat_sim["hour_cos"] = math.cos(2 * math.pi * h / 24)
                    feat_sim["is_day"] = 1 if 6 <= h <= 19 else 0
                    feat_sim["temp_x_hour"] = temp * h

                    input_sim_df = pd.DataFrame(0.0, index=[0], columns=expected_cols)
                    for col in expected_cols:
                        if col in feat_sim:
                            input_sim_df.at[0, col] = feat_sim[col]

                    simulacao_horas.append(f"{h:02d}:00")
                    simulacao_preds.append(rt_model.predict(input_sim_df)[0])

                df_grafico = pd.DataFrame({
                    "Hour": simulacao_horas,
                    "Estimated Demand (MW)": simulacao_preds,
                })

                fig_rt = px.line(
                    df_grafico,
                    x="Hour",
                    y="Estimated Demand (MW)",
                    markers=True,
                    color_discrete_sequence=["#1A3A4A"],
                )
                fig_rt.add_hline(
                    y=carga_base,
                    line_dash="dash",
                    line_color="#83BCD4",
                    annotation_text=" Reference",
                    annotation_position="bottom right"
                )
                hora_int = int(hour_decimal)
                fig_rt.add_scatter(
                    x=[f"{hora_int:02d}:00"],
                    y=[simulacao_preds[hora_int]],
                    mode="markers",
                    marker=dict(color="#8EE8B7", size=14),
                    name="Selected Hour"
                )
                fig_rt.update_layout(
                    hovermode="x unified",
                    margin=dict(l=0, r=0, t=30, b=0),
                    showlegend=False,
                    **CHART_LAYOUT
                )
                st.plotly_chart(fig_rt, use_container_width=True)

            except Exception as e:
                st.error("Error processing the prediction.")
                st.write(f"Detail: `{e}`")
    else:
        st.info("Configure the parameters above and click **Calculate Prediction** to see the result.")

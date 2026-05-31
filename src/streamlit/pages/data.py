import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

st.set_page_config(page_title="Data Explorer", layout="wide")


# Auth
if not st.session_state.get("user"):
    st.warning("Please login first to access the data explorer.")
    st.switch_page("pages/1_Login.py")


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# CSS
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
</style>
""", unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(255, 255, 255, 0.5)",
    plot_bgcolor="rgba(255, 255, 255, 0.3)",
    font=dict(color="#1a3a4a", family="Poppins"),
)

COLOR_DARK = "#1A3A4A"
COLOR_MID = "#1E5A5C"
COLOR_LIGHT = "#A4D1E0"
COLOR_ACCENT = "#83BCD4"


# Logo
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
logo_path = os.path.join(ROOT_DIR, "src", "utils", "LOGO_claro.png")
logo_b64 = None
if os.path.exists(logo_path):
    logo_b64 = img_to_base64(logo_path)

if logo_b64:
    st.markdown(f"""
        <div class="title-with-logo">
            <img src="data:image/png;base64,{logo_b64}" alt="logo">
            <h1>Data Explorer</h1>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(
        "<h1 style='font-size:2.6rem; font-weight:800;'>Data Explorer</h1>",
        unsafe_allow_html=True
    )


# Data
@st.cache_data
def load_data():
    file_path = os.path.join(ROOT_DIR, "data", "processed", "features.csv")
    df = pd.read_csv(file_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading features.csv: {e}")
    st.stop()


# Sidebar
st.sidebar.header("Climate Variable")

climate_variables = {
    "Temperature":     "temperature",
    "Solar Radiation": "solar_radiation",
    "Wind Speed":      "wind_speed",
    "Precipitation":   "total_precipitation",
}

selected_label = st.sidebar.selectbox("Choose a climate variable:", list(climate_variables.keys()))
selected_feature = climate_variables[selected_label]

st.sidebar.divider()
st.sidebar.header("Time Filter")

start_date = st.sidebar.date_input("Start Date", df["timestamp"].min().date())
end_date = st.sidebar.date_input("End Date",   df["timestamp"].max().date())

mask = (df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)
df_filtered = df.loc[mask]


# Tabs
tab1, tab2, tab3 = st.tabs([
    "Time Series",
    "Relationship Analysis",
    "Alerts",
])


# =============================
# TAB 1 - TIME SERIES
# =============================
with tab1:

    st.write(
        "Select variables in the sidebar to analyse their impact on electricity"
        " consumption and decide which ones to use in the model."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Energy Load")
        fig_load = px.line(
            df_filtered, x="timestamp", y="load",
            color_discrete_sequence=[COLOR_DARK],
        )
        fig_load.update_layout(
            height=400, xaxis_title="Date", yaxis_title="Load (MW)",
            margin=dict(t=20), **CHART_LAYOUT
        )
        st.plotly_chart(fig_load, use_container_width=True)

    with col2:
        st.markdown(f"### {selected_label}")
        fig_feature = px.line(
            df_filtered, x="timestamp", y=selected_feature,
            color_discrete_sequence=[COLOR_ACCENT],
        )
        fig_feature.update_layout(
            height=400, xaxis_title="Date", yaxis_title=selected_label,
            margin=dict(t=20), **CHART_LAYOUT
        )
        st.plotly_chart(fig_feature, use_container_width=True)

    st.subheader("Interpretation")

    interpretations = {
        "temperature": (
            "Electricity demand is significantly higher during colder periods "
            "and decreases as temperatures rise. This pattern suggests that "
            "heating systems play a major role in energy consumption in Germany."
        ),
        "solar_radiation": (
            "Higher solar radiation levels generally occur during summer months, "
            "when electricity demand tends to be lower. This inverse relationship "
            "reflects reduced heating needs during warmer and brighter periods."
        ),
        "wind_speed": (
            "Wind speed exhibits a volatile pattern throughout the year, with more "
            "pronounced peaks during winter months. This behavior can be beneficial "
            "for the energy system, as higher wind availability tends to coincide "
            "with periods of increased electricity demand."
        ),
        "total_precipitation": (
            "Precipitation does not display a clear direct relationship with "
            "electricity demand, although extreme weather conditions may still "
            "indirectly affect consumption behavior."
        ),
    }
    st.info(interpretations[selected_feature])


# =============================
# TAB 2 - RELATIONSHIP ANALYSIS
# =============================
with tab2:

    # Correlation Analysis
    correlation = df_filtered[selected_feature].corr(df_filtered["load"])

    if abs(correlation) > 0.7:
        corr_label = "Strong correlation"
    elif abs(correlation) > 0.4:
        corr_label = "Moderate correlation"
    elif abs(correlation) > 0.2:
        corr_label = "Weak correlation"
    else:
        corr_label = "Very weak correlation"

    direction = "positive" if correlation > 0 else "negative"

    st.markdown(f"""
        <div style="background:rgba(255,255,255,0.75); backdrop-filter:blur(10px);
            padding:28px 36px; border-radius:18px; margin-bottom:1.5rem;
            box-shadow:0 4px 15px rgba(131,188,212,0.12);
            border:1px solid rgba(164,209,224,0.35);
            display:flex; align-items:center; gap:48px;
            font-family:'Poppins', sans-serif;">
            <div style="text-align:center; min-width:140px;">
                <div style="font-size:0.8rem; color:#1F4D5C; font-weight:600;
                    letter-spacing:0.05em; text-transform:uppercase; margin-bottom:6px;
                    font-family:'Poppins', sans-serif;">
                    Correlation Coefficient
                </div>
                <div style="font-size:3.2rem; font-weight:800; color:#1A3A4A;
                    letter-spacing:-2px; line-height:1; font-family:'Poppins', sans-serif;">
                    {correlation:.3f}
                </div>
            </div>
            <div style="flex:1; border-left:2px solid rgba(164,209,224,0.5); padding-left:36px;">
                <div style="font-size:1rem; color:#1A3A4A; line-height:1.7;
                    font-family:'Poppins', sans-serif;">
                    <strong>{selected_label}</strong> shows a
                    <strong>{corr_label.lower()} {direction} relationship</strong>
                    with electricity demand.
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.write("---")

    # Scatter
    st.subheader(f"Relationship Between {selected_label} and Energy Load")

    scatter_interpretations = {
        "temperature": (
            "Each point represents one hour of data. The trend line shows that as temperature "
            "drops, energy demand rises - confirming that heating is the dominant driver of "
            "consumption in Germany. The spread of points reflects daily and seasonal variation "
            "beyond temperature alone."
        ),
        "solar_radiation": (
            "Higher solar radiation correlates with lower electricity demand, since bright "
            "periods coincide with warmer months when heating needs are reduced. The wide "
            "spread indicates that radiation alone does not fully explain demand - other "
            "factors like temperature and time of day also play a role."
        ),
        "wind_speed": (
            "Wind speed shows a weak relationship with energy demand. While higher winds "
            "tend to occur in winter (when demand is higher), the correlation is not strong "
            "enough to use wind speed as a standalone predictor. It may still add value "
            "as a secondary feature in the model."
        ),
        "total_precipitation": (
            "Precipitation has little direct influence on electricity demand, as shown by "
            "the nearly flat trend line. Extreme rainfall events may cause localized spikes, "
            "but overall this variable contributes minimally to explaining consumption patterns."
        ),
    }

    fig_scatter = px.scatter(
        df_filtered, x=selected_feature, y="load",
        opacity=0.5, trendline="ols",
        color_discrete_sequence=[COLOR_MID],
    )
    fig_scatter.update_layout(
        height=500, xaxis_title=selected_label, yaxis_title="Energy Load (MW)",
        margin=dict(t=20), **CHART_LAYOUT
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.info(scatter_interpretations[selected_feature])


# =============================
# TAB 3 - ALERTS
# =============================
with tab3:
    st.subheader("Climate & Energy Monitoring")
    st.markdown("##### Adjust Alert Thresholds")

    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1:
        high_load_threshold = st.selectbox("Energy Demand (MW)", [60000, 65000, 70000], index=2)
    with t_col2:
        cold_threshold = st.selectbox("Extreme Cold (ºC)", [-5.0, 0.0, 5.0], index=1)
    with t_col3:
        wind_threshold = st.selectbox("High Wind (m/s)", [4.0, 5.0, 6.0], index=1)
    with t_col4:
        rain_threshold = st.selectbox("Extreme Rain (mm)", [0.3, 0.4, 0.5], index=1)

    st.write("")

    high_load = df_filtered[df_filtered["load"] > high_load_threshold]
    extreme_cold = df_filtered[df_filtered["temperature"] < cold_threshold]
    high_wind = df_filtered[df_filtered["wind_speed"] > wind_threshold]
    heavy_rain = df_filtered[df_filtered["total_precipitation"] > rain_threshold]

    ICON_BOLT = (
        '<svg width="20" height="20" fill="none" stroke="currentColor"'
        ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
        ' viewBox="0 0 24 24">'
        '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
    )
    ICON_TEMP = (
        '<svg width="20" height="20" fill="none" stroke="currentColor"'
        ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
        ' viewBox="0 0 24 24">'
        '<path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>'
    )
    ICON_WIND = (
        '<svg width="20" height="20" fill="none" stroke="currentColor"'
        ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
        ' viewBox="0 0 24 24">'
        '<path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2'
        'm15.73-8.27A2.5 2.5 0 1 1 19.5 12H2"/></svg>'
    )
    ICON_RAIN = (
        '<svg width="20" height="20" fill="none" stroke="currentColor"'
        ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
        ' viewBox="0 0 24 24">'
        '<line x1="16" y1="13" x2="16" y2="21"/>'
        '<line x1="8" y1="13" x2="8" y2="21"/>'
        '<line x1="12" y1="15" x2="12" y2="23"/>'
        '<path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/></svg>'
    )

    def alert_card(icon, icon_color, title, count, subtitle, description):
        return (
            f'<div style="background: rgba(255,255,255,0.6);'
            f'backdrop-filter: blur(16px);-webkit-backdrop-filter: blur(16px);'
            f'padding: 24px 28px;border-radius: 20px;margin-bottom: 20px;'
            f'border: 1px solid rgba(255,255,255,0.7);'
            f'box-shadow: 0 8px 32px rgba(131,188,212,0.15),'
            f'0 0 0 1px rgba(164,209,224,0.2),'
            f'inset 0 1px 0 rgba(255,255,255,0.8);'
            f'font-family: \'Poppins\', sans-serif;">'
            f'<div style="display:flex; align-items:center;'
            f'gap:10px; margin-bottom:14px;">'
            f'<span style="color:{icon_color};'
            f'display:flex; align-items:center;">{icon}</span>'
            f'<h3 style="margin:0; color:#1A3A4A;font-size:1rem; font-weight:700;'
            f'font-family:\'Poppins\', sans-serif;">{title}</h3>'
            f'</div>'
            f'<div style="font-size:2.4rem; font-weight:800; color:#1A3A4A;'
            f'letter-spacing:-1px; line-height:1; margin-bottom:6px;'
            f'font-family:\'Poppins\', sans-serif;">'
            f'{count}'
            f'<span style="font-size:14px; color:#1E5A5C; font-weight:500;'
            f'letter-spacing:0;">'
            f'&nbsp;hours &nbsp;(~{count // 24} days)'
            f'</span>'
            f'</div>'
            f'<p style="margin:6px 0 4px 0; color:#1F4D5C; font-weight:600;'
            f'font-size:0.9rem;font-family:\'Poppins\', sans-serif;">{subtitle}</p>'
            f'<p style="margin:0; color:#1F4D5C; font-size:13px; line-height:1.6;'
            f'font-family:\'Poppins\', sans-serif;">{description}</p>'
            f'</div>'
        )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(alert_card(
            ICON_BOLT, COLOR_DARK,
            "High Energy Demand", len(high_load),
            f"Exceeded the {high_load_threshold:,} MW threshold.",
            "Represents periods of grid stress, historically aligning with maximum"
            " winter heating requirements."
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(alert_card(
            ICON_TEMP, COLOR_ACCENT,
            "Extreme Cold Conditions", len(extreme_cold),
            f"Registered temperatures below {cold_threshold}ºC.",
            "Directly correlates with peak load events. These freezing"
            " periods dictate the baseline for thermal capacity needs."
        ), unsafe_allow_html=True)

    with col1:
        st.markdown(alert_card(
            ICON_WIND, COLOR_MID,
            "High Wind Availability", len(high_wind),
            f"Recorded wind speeds above {wind_threshold} m/s.",
            "High potential for wind power generation, crucial for offsetting"
            " peak winter demand and reducing fossil reliance."
        ), unsafe_allow_html=True)

    with col2:
        st.markdown(alert_card(
            ICON_RAIN, COLOR_LIGHT,
            "Extreme Precipitation", len(heavy_rain),
            f"Experienced rainfall exceeding {rain_threshold} mm/h.",
            "Indicates localized severe weather events, which may pose operational"
            " risks to physical grid infrastructure."
        ), unsafe_allow_html=True)

    st.write("---")

    total_alerts = len(high_load) + len(extreme_cold) + len(high_wind) + len(heavy_rain)

    if total_alerts > 0:
        st.info(
            "The monitoring system detected relevant climate and energy events "
            "based on your custom thresholds."
        )
    else:
        st.success(
            "No significant climate or energy anomalies were detected "
            "above the defined thresholds."
        )

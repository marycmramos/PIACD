import streamlit as st
import os
import base64

st.set_page_config(
    page_title="Climate Energy Analytics",
    layout="wide"
)


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Round');

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

/* HERO LOGO */
.hero-logo-wrapper {
    display: flex;
    justify-content: center;
    padding-top: 3.5rem;
    padding-bottom: 1.5rem;
}
.hero-logo-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    background: rgba(255, 255, 255, 0.45);
    backdrop-filter: blur(12px);
    border-radius: 24px;
    padding: 2rem 3.5rem;
    box-shadow: 0 6px 24px rgba(131, 188, 212, 0.18);
    border: 1px solid rgba(164, 209, 224, 0.35);
}
.hero-logo-box img.hero-logo {
    height: 110px;
    object-fit: contain;
}
.hero-logo-box img.hero-nome {
    height: 60px;
    object-fit: contain;
}

/* HERO */
.hero-container {
    padding-bottom: 2rem;
}
.subtitle {
    font-size: 1.2rem;
    color: #1F4D5C;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: 400;
}

/* DESCRIPTION CARD */
.description-card {
    max-width: 950px;
    margin: auto;
    background: rgba(255, 255, 255, 0.7);
    padding: 2.5rem;
    border-radius: 22px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(131, 188, 212, 0.15);
    border: 1px solid rgba(164, 209, 224, 0.3);
    margin-bottom: 2.5rem;
}
.description {
    text-align: center;
    font-size: 1.05rem;
    line-height: 1.9;
    color: #1a3a4a;
    margin: 0;
}

/* BUTTON */
.stButton > button {
    background: linear-gradient(135deg, #1F4D5C, #1E5A5C);
    color: white !important;
    border-radius: 12px;
    height: 3.2em;
    border: none;
    font-weight: 600;
    font-size: 1rem;
    font-family: 'Poppins', sans-serif;
    transition: 0.3s;
}
.stButton > button:hover {
    transform: scale(1.03);
    background: linear-gradient(135deg, #1A3A4A, #1F4D5C);
}

/* SECTION TITLES */
.section-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #1A3A4A;
    margin-top: 3rem;
    margin-bottom: 1.5rem;
    text-align: center;
    letter-spacing: -0.5px;
}

/* FEATURE CARDS */
.feature-card {
    background: rgba(255, 255, 255, 0.7);
    padding: 1.8rem;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(131, 188, 212, 0.12);
    border: 1px solid rgba(164, 209, 224, 0.3);
    min-height: 220px;
    transition: transform 0.2s ease;
}
.feature-card:hover {
    transform: translateY(-3px);
}
.feature-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: #1A3A4A;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.feature-title .material-icons-round {
    font-size: 1.5rem;
    color: #1E5A5C;
    background: rgba(142, 232, 183, 0.25);
    border-radius: 10px;
    padding: 6px;
}
.feature-text {
    color: #1F4D5C;
    line-height: 1.75;
    font-size: 0.97rem;
}

/* WORKFLOW */
.workflow-card {
    background: rgba(255, 255, 255, 0.7);
    padding: 2rem;
    border-radius: 18px;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(131, 188, 212, 0.12);
    border: 1px solid rgba(164, 209, 224, 0.3);
    text-align: center;
    margin-top: 1rem;
}
.workflow-step {
    font-size: 1.05rem;
    font-weight: 600;
    color: #1E5A5C;
}
.workflow-arrow {
    color: #83BCD4;
    font-weight: 300;
}
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(164, 209, 224, 0.3);
}

/* FOOTER */
.footer {
    text-align: center;
    margin-top: 5rem;
    margin-bottom: 1rem;
    color: #1F4D5C;
    font-size: 0.88rem;
    opacity: 0.8;
}
</style>
""", unsafe_allow_html=True)


# Hero: Logo + Nome centrados com caixa
logo_path = "src/utils/LOGO_claro.png"
nome_path = "src/utils/NOME_claro.png"

if os.path.exists(logo_path) and os.path.exists(nome_path):
    logo_b64 = img_to_base64(logo_path)
    nome_b64 = img_to_base64(nome_path)
    st.markdown(f"""
        <div class="hero-logo-wrapper">
            <div class="hero-logo-box">
                <img class="hero-logo" src="data:image/png;base64,{logo_b64}" alt="logo">
                <img class="hero-nome" src="data:image/png;base64,{nome_b64}" alt="nome">
            </div>
        </div>
    """, unsafe_allow_html=True)


# Hero
st.markdown('<div class="hero-container">', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">AI-powered climate and electricity demand analysis</div>',
    unsafe_allow_html=True
)

st.markdown("""
<div class="description-card">
    <p class="description">
        Climate Energy Analytics is a platform designed to explore how climate
        conditions influence electricity demand patterns in Germany.
        <br><br>
        Using real-world climate and energy datasets, the system combines
        data processing, machine learning, and predictive analytics to support
        the study of energy consumption behavior and climate-driven demand forecasting.
    </p>
</div>
""", unsafe_allow_html=True)

left, center, right = st.columns([2, 1, 2])
with center:
    if st.button("Get Started", use_container_width=True):
        st.switch_page("pages/login.py")

st.markdown('</div>', unsafe_allow_html=True)


# Features
st.markdown('<div class="section-title">Core Features</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">
            <span class="material-icons-round">cloud</span>
            Climate Data Integration
        </div>
        <div class="feature-text">
        Integration of ERA5 climate datasets including temperature,
        solar radiation, and wind speed variables used to analyze
        climate influence on energy demand.
        </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">
            <span class="material-icons-round">bolt</span>
            Energy Demand Analytics
        </div>
        <div class="feature-text">
        Analysis of hourly electricity demand patterns using
        ENTSO-E energy consumption datasets for Germany,
        enabling temporal and seasonal demand exploration.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

col3, col4 = st.columns(2)
with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">
            <span class="material-icons-round">psychology</span>
            Machine Learning Models
        </div>
        <div class="feature-text">
        Predictive models designed to estimate electricity demand
        based on historical energy usage and climate-related features.
        </div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-title">
            <span class="material-icons-round">lock</span>
            Secure Access
        </div>
        <div class="feature-text">
        Authentication-protected environment that restricts access
        to prediction, model execution, and analytical functionalities.
        </div>
    </div>
    """, unsafe_allow_html=True)


# Workflow
st.markdown('<div class="section-title">System Workflow</div>', unsafe_allow_html=True)

st.markdown("""
<div class="workflow-card">
    <span class="workflow-step">Data Collection</span>
    <span class="workflow-arrow"> &nbsp;→&nbsp; </span>
    <span class="workflow-step">Processing</span>
    <span class="workflow-arrow"> &nbsp;→&nbsp; </span>
    <span class="workflow-step">Feature Engineering</span>
    <span class="workflow-arrow"> &nbsp;→&nbsp; </span>
    <span class="workflow-step">Modeling</span>
    <span class="workflow-arrow"> &nbsp;→&nbsp; </span>
    <span class="workflow-step">Prediction</span>
</div>
""", unsafe_allow_html=True)


# Footer
st.markdown("""
<div class="footer">
    PIACD 2025/2026 • Climate-Driven Energy Demand Analytics System
    <br>
    Department of Informatics Engineering
</div>
""", unsafe_allow_html=True)

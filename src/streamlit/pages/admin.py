import base64
import hashlib
import html
import json
import os
import subprocess
import sys

import pandas as pd
import streamlit as st

_THIS_FILE = os.path.abspath(globals().get("__file__", __file__))
_STREAMLIT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(_THIS_FILE), "..")
)
_SRC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(_THIS_FILE), "..", "..")
)
_ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(_THIS_FILE), "..", "..", "..")
)

for _p in [_STREAMLIT_DIR, _SRC_DIR, _ROOT_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from utils.user_manager import (
    add_user,
    change_role,
    delete_user,
    load_users,
)

st.set_page_config(page_title="Admin - WattCast", layout="wide")

ROOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..")
)
SRC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

CONFIG_PATH = os.path.join(
    ROOT_DIR,
    "src",
    "utils",
    "model_config.json",
)

LOG_DIR = os.path.join(ROOT_DIR, "logs")

if not st.session_state.get("user"):
    st.warning("Please, log in.")
    st.switch_page("pages/1_Login.py")

if st.session_state["user"].get("role") != "admin":
    st.error("Access denied. This page is only for administrators.")
    st.stop()


# Helpers
def img_to_base64(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode()


# CSS
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

html,
body,
[class*="css"] {
    font-family: 'Poppins', sans-serif;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp {
    background: linear-gradient(
        270deg,
        #e8f6fa,
        #eefaf6,
        #f4fdf0,
        #f0fdf8
    );
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

[data-testid="stMetricLabel"] {
    color: #1a3a4a !important;
}

[data-testid="stMetricValue"] {
    color: #1E5A5C !important;
}

section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.5);
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(164, 209, 224, 0.3);
}

h1,
h2,
h3 {
    font-weight: 600;
    color: #1a3a4a;
    letter-spacing: -0.3px;
}

[data-testid="stDataFrame"] {
    background: rgba(255, 255, 255, 0.6);
    border-radius: 12px;
}

button[data-baseweb="tab"] {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    color: #1F4D5C !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #1A3A4A !important;
    border-bottom-color: #1E5A5C !important;
}

[data-baseweb="tab-highlight"] {
    background-color: #1E5A5C !important;
}

[data-baseweb="tab-border"] {
    background-color: rgba(164, 209, 224, 0.4) !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextInputRootElement"] input {
    background-color: #ffffff !important;
    color: #1a3a4a !important;
    border-radius: 10px !important;
    border: 1px solid rgba(30, 90, 92, 0.35) !important;
}

div[data-testid="stTextInput"] > div {
    background-color: #ffffff !important;
    border-radius: 10px !important;
}

div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stCheckbox"] label,
div[data-testid="stRadio"] > label {
    color: #1A3A4A !important;
    font-weight: 600 !important;
}

div[data-testid="stSelectbox"] > div > div {
    background-color: rgba(255, 255, 255, 0.85) !important;
    color: #1a3a4a !important;
    border-radius: 10px !important;
    border: 1px solid rgba(30, 90, 92, 0.35) !important;
}

div[data-testid="stNumberInput"] input {
    background-color: #ffffff !important;
    color: #1a3a4a !important;
    border-radius: 10px !important;
    border: 1px solid rgba(30, 90, 92, 0.35) !important;
}

div[data-testid="stCheckbox"] label,
div[data-testid="stCheckbox"] label * {
    color: #1a3a4a !important;
}

div[data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.75) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(30, 90, 92, 0.2) !important;
    padding: 20px !important;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    border: none;
    color: white !important;
    background: #1A3A4A !important;
    font-family: 'Poppins', sans-serif !important;
}

.stButton > button:hover {
    background: #1E5A5C !important;
}

div[data-testid="stForm"] button {
    background: #1A3A4A !important;
    color: white !important;
}

div[data-testid="stForm"] button:disabled {
    background: rgba(30, 90, 92, 0.3) !important;
    color: #1A3A4A !important;
    opacity: 0.6 !important;
}

[data-baseweb="menu"] {
    background-color: #ffffff !important;
}

[data-baseweb="menu"] li {
    color: #1a3a4a !important;
}

[data-baseweb="menu"] li:hover {
    background-color: rgba(30, 90, 92, 0.1) !important;
}

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

.small {
    color: #1F4D5C;
    font-size: 0.95rem;
}

.step-status-pending {
    color: #9ca3af;
    font-size: 0.85rem;
    font-weight: 600;
}

.step-status-running {
    color: #f59e0b;
    font-size: 0.85rem;
    font-weight: 600;
}

.step-status-done {
    color: #1E5A5C;
    font-size: 0.85rem;
    font-weight: 600;
}

.step-status-error {
    color: #ef4444;
    font-size: 0.85rem;
    font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)

# Design tokens
COLOR_DARK = "#1A3A4A"
COLOR_MID = "#1E5A5C"
COLOR_LIGHT = "#A4D1E0"
COLOR_ACCENT = "#83BCD4"

CARD_LR = "#a1dfcd"
CARD_RF = "#A4D1E0"
CARD_BASE = "#83BCD4"
CARD_OK = "#1E5A5C"
CARD_WARN = "#f59e0b"
CARD_ERR = "#ef4444"

# Icons
ICON_LR = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
<path stroke-linecap="round" stroke-linejoin="round"
d="M3 17l6-6 4 4 8-8"/>
</svg>
"""

ICON_RF = ICON_LR
ICON_BASE = ICON_LR

ICON_OK = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
<path stroke-linecap="round" stroke-linejoin="round"
d="M5 13l4 4L19 7"/>
</svg>
"""

ICON_USER = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
<path stroke-linecap="round" stroke-linejoin="round"
d="M12 12a5 5 0 100-10 5 5 0 000 10zm0 2c-4 0-7 2-7 5h14c0-3-3-5-7-5z"/>
</svg>
"""

ICON_PIPE = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
<path stroke-linecap="round" stroke-linejoin="round"
d="M4 7h16M4 12h16M4 17h16"/>
</svg>
"""

ICON_WARN = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
<path stroke-linecap="round" stroke-linejoin="round"
d="M12 9v4m0 4h.01M10.29 3.86L1.82 18A2 2 0 003.53 21h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
</svg>
"""

ICON_ERR = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
<path stroke-linecap="round" stroke-linejoin="round"
d="M6 18L18 6M6 6l12 12"/>
</svg>
"""

ICON_BEST = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
<path stroke-linecap="round" stroke-linejoin="round"
d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
</svg>
"""

ICON_STEP = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
<circle cx="12" cy="12" r="10"/>
<polyline points="12 6 12 12 16 14"/>
</svg>
"""


# -------------------------------------
def alert_card(
    icon, icon_color, title, main_value, subtitle, description,
    min_height="230px", value_size="2rem"
):
    main_value_html = (
        f'<div style="font-size:{value_size};font-weight:800;color:#1A3A4A;'
        f'letter-spacing:-1px;line-height:1.1;margin-bottom:8px;'
        f'font-family:\'Poppins\',sans-serif;">{main_value}</div>'
        if main_value else ""
    )
    subtitle_html = (
        f'<p style="margin:4px 0 4px 0;color:#1F4D5C;font-weight:600;'
        f'font-size:0.9rem;font-family:\'Poppins\',sans-serif;">{subtitle}</p>'
        if subtitle else ""
    )
    return (
        f'<div style="background:rgba(255,255,255,0.6);min-height:{min_height};'
        f'display:flex;flex-direction:column;justify-content:flex-start;'
        f'backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);'
        f'padding:24px 28px;border-radius:20px;margin-bottom:16px;'
        f'border:1px solid rgba(255,255,255,0.7);'
        f'box-shadow:0 8px 32px rgba(131,188,212,0.15),'
        f'0 0 0 1px rgba(164,209,224,0.2),inset 0 1px 0 rgba(255,255,255,0.8);'
        f'font-family:\'Poppins\',sans-serif;color:#1a3a4a;">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">'
        f'<span style="color:{icon_color};display:flex;align-items:center;">{icon}</span>'
        f'<h3 style="margin:0;color:#1A3A4A;font-size:1rem;font-weight:700;'
        f'font-family:\'Poppins\',sans-serif;">{title}</h3>'
        f'</div>'
        f'{main_value_html}'
        f'{subtitle_html}'
        f'<p style="margin:0;color:#1F4D5C;font-size:13px;line-height:1.6;'
        f'font-family:\'Poppins\',sans-serif;">{description}</p>'
        f'</div>'
    )


def user_card(icon, icon_color, title, badge_text, badge_bg, badge_color, description=""):
    """Card de utilizador, estilo Data Explorer.

    FIX: description span is now placed correctly inside the flex container,
    and the HTML structure is self-contained so no closing tags leak as visible text.
    """
    desc_html = (
        f'<span style="font-size:0.78rem; color:#64748b; margin-left:8px;">'
        f'{description}</span>'
        if description else ""
    )
    return (
        f'<div style="background: rgba(255,255,255,0.6);'
        f'backdrop-filter: blur(16px);-webkit-backdrop-filter: blur(16px);'
        f'padding: 18px 24px;border-radius: 20px;margin-bottom: 16px;'
        f'border: 1px solid rgba(255,255,255,0.7);'
        f'box-shadow: 0 8px 32px rgba(131,188,212,0.15),'
        f'0 0 0 1px rgba(164,209,224,0.2),inset 0 1px 0 rgba(255,255,255,0.8);'
        f'font-family: \'Poppins\', sans-serif;color: #1a3a4a;'
        f'display: flex;align-items: center;gap: 12px;flex-wrap: nowrap;">'
        f'<span style="color:{icon_color}; display:flex; align-items:center;">{icon}</span>'
        f'<span style="font-weight:700; font-size:0.95rem; flex:1;">{title}</span>'
        f'<span style="background:{badge_bg}; color:{badge_color}; padding:3px 12px;'
        f'border-radius:20px; font-size:0.78rem; font-weight:700;">{badge_text}</span>'
        f'{desc_html}</div>'
    )


def pipeline_step_card(icon, icon_color, title, subtitle, status_html_str, min_height="300px"):
    """Card de etapa de pipeline, estilo Data Explorer."""
    return (
        f'<div style="background: rgba(255,255,255,0.6);min-height: {min_height};'
        f'display:flex;flex-direction:column;justify-content:space-between;'
        f'backdrop-filter: blur(16px);-webkit-backdrop-filter: blur(16px);'
        f'padding: 24px 28px;border-radius: 20px;margin-bottom: 16px;'
        f'border: 1px solid rgba(255,255,255,0.7);'
        f'box-shadow: 0 8px 32px rgba(131,188,212,0.15),'
        f'0 0 0 1px rgba(164,209,224,0.2),inset 0 1px 0 rgba(255,255,255,0.8);'
        f'font-family: \'Poppins\', sans-serif;color: #1a3a4a;">'
        f'<div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">'
        f'<span style="color:{icon_color}; display:flex; align-items:center;">{icon}</span>'
        f'<h3 style="margin:0; color:#1A3A4A; font-size:1rem; font-weight:700;'
        f'font-family:\'Poppins\',sans-serif;">{title}</h3>'
        f'</div>'
        f'<p style="margin:0 0 8px 0; color:#1F4D5C; font-size:13px; line-height:1.5;'
        f'font-family:\'Poppins\',sans-serif;">{subtitle}</p>'
        f'<div>Status: {status_html_str}</div>'
        f'</div>'
    )


def status_html(status):
    labels = {
        "pending": ("Pending", "step-status-pending"),
        "running": ("Running...", "step-status-running"),
        "done": ("Done", "step-status-done"),
        "error": ("Error", "step-status-error"),
    }
    label, cls = labels.get(status, ("Pending", "step-status-pending"))
    return f'<span class="{cls}">{label}</span>'


# Logo
logo_path = os.path.join(ROOT_DIR, "src", "utils", "LOGO_claro.png")
logo_b64 = None
if os.path.exists(logo_path):
    logo_b64 = img_to_base64(logo_path)

col1, col2 = st.columns([8, 2])
username_safe = html.escape(st.session_state["user"]["username"])

with col1:
    if logo_b64:
        st.markdown(f"""
            <div class="title-with-logo">
                <img src="data:image/png;base64,{logo_b64}" alt="logo">
                <h1>Admin Panel</h1>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            "<h1 style='font-size:2.6rem; font-weight:800;'>Admin Panel</h1>",
            unsafe_allow_html=True
        )
    st.markdown(
        f"<div class='small'>Active Session: <b>{username_safe}</b> · Admin</div>",
        unsafe_allow_html=True
    )

with col2:
    st.empty()


# Helpers de dados
EXPERIMENTS_PATH = os.path.join(ROOT_DIR, "data", "experiments", "experiments.json")
RESULTS_DIR = os.path.join(ROOT_DIR, "data", "results")


def load_experiments():
    if not os.path.exists(EXPERIMENTS_PATH):
        return []
    with open(EXPERIMENTS_PATH, "r") as f:
        return json.load(f)


def load_result(run_id):
    path = os.path.join(RESULTS_DIR, f"results_{run_id}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def get_config_hash(config):
    lr_hash = hashlib.sha256(
        json.dumps(config.get("linear_regression", {}), sort_keys=True).encode()
    ).hexdigest()
    rf_hash = hashlib.sha256(
        json.dumps(config.get("random_forest", {}), sort_keys=True).encode()
    ).hexdigest()
    return {"lr": lr_hash, "rf": rf_hash}


def render_metrics_cards(exp, result):
    col_b, col_lr, col_rf = st.columns(3)
    with col_b:
        st.markdown(alert_card(
            ICON_BASE, COLOR_ACCENT,
            "Baseline",
            f"{exp['baseline_mae']:.1f} MW",
            "Naive prediction (lag_1h)",
            "Reference value for comparison with the trained models."
        ), unsafe_allow_html=True)
    with col_lr:
        lr = result.get("linear_regression", {}) if result else {}
        st.markdown(alert_card(
            ICON_LR, CARD_LR,
            "Linear Regression",
            f"MAE: {exp['lr_mae']:.1f} MW",
            f"Run: {exp['timestamp'][:10]}",
            f"RMSE: {lr.get('rmse', 0):.1f} MW &nbsp;·&nbsp; R²: {lr.get('r2', 0):.4f}"
        ), unsafe_allow_html=True)
    with col_rf:
        rf = result.get("random_forest", {}) if result else {}
        st.markdown(alert_card(
            ICON_RF, COLOR_MID,
            "Random Forest",
            f"MAE: {exp['rf_mae']:.1f} MW",
            f"Run: {exp['timestamp'][:10]}",
            f"RMSE: {rf.get('rmse', 0):.1f} MW &nbsp;·&nbsp; R²: {rf.get('r2', 0):.4f}"
        ), unsafe_allow_html=True)


def run_pipeline_block(mode=None, include_ingestion=False, include_gridsearch=False):
    try:
        args = [sys.executable, "-m", "src.pipeline.full_pipeline"]
        if mode == "ingestion":
            args.append("--only-ingestion")
        elif mode == "processing":
            args.append("--only-processing")
        elif mode == "modeling":
            args.append("--only-modeling")
            if include_gridsearch:
                args.append("--grid-search")
        elif include_ingestion:
            args.append("--ingestion")

        if mode != "modeling" and include_gridsearch:
            args.append("--grid-search")

        result = subprocess.run(
            args, capture_output=True, text=True,
            cwd=ROOT_DIR, env={**os.environ, "PYTHONPATH": ROOT_DIR}
        )
        if result.returncode != 0:
            st.error("Pipeline failed")
            if result.stderr:
                st.markdown("**Error Details:**")
                st.code(result.stderr)
            return False
        st.success("Pipeline completed successfully!")
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False


def run_modeling_pipeline():
    result = subprocess.run(
        [sys.executable, "-m", "src.pipeline.full_pipeline", "--only-modeling"],
        capture_output=True, text=True,
        cwd=ROOT_DIR, env={**os.environ, "PYTHONPATH": ROOT_DIR}
    )
    return result.returncode == 0, result.stderr


# Tabs
tab1, tab2, tab3 = st.tabs([
    "Manage Users",
    "Configure Models",
    "Run Pipeline",
])


# ======================
# TAB 1 - MANAGE USERS
# ======================
with tab1:
    st.subheader("Manage Users")

    data = load_users()
    users = data.get("users", [])

    if not users:
        st.info("No users registered.")
    else:
        for user in users:
            uname = html.escape(user["username"])
            role = user.get("role", "user")
            badge = "Admin" if role == "admin" else "User"
            border_color = CARD_WARN if role == "admin" else CARD_OK
            badge_bg = "#fef3c7" if role == "admin" else "#d1fae5"
            badge_color = "#92400e" if role == "admin" else "#065f46"
            icon_color = CARD_WARN if role == "admin" else COLOR_MID

            c1, c2, c3 = st.columns([4, 2, 2])
            with c1:
                st.markdown(
                    user_card(
                        ICON_USER, icon_color,
                        uname, badge, badge_bg, badge_color,
                        "(you)" if uname == username_safe else ""
                    ),
                    unsafe_allow_html=True
                )
            with c2:
                st.write("")
                if uname != username_safe:
                    new_role = "user" if role == "admin" else "admin"
                    label = "Make User" if role == "admin" else "Make Admin"
                    if st.button(label, key=f"role_{uname}", use_container_width=True):
                        ok, msg = change_role(user["username"], new_role)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            with c3:
                st.write("")
                if uname != username_safe:
                    if st.button("Delete", key=f"del_{uname}", use_container_width=True):
                        ok, msg = delete_user(user["username"])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    st.write("---")
    st.subheader("Add User")

    col_a, col_b = st.columns(2)
    with col_a:
        new_username = st.text_input("Username", key="form_username")
        new_password = st.text_input("Password", type="password", key="form_password")
    with col_b:
        new_role_select = st.selectbox("Role", ["user", "admin"], key="form_role")
        st.write("")
        st.write("")
        if st.button("Create User", use_container_width=True, type="primary"):
            if not new_username or not new_password:
                st.warning("Please fill in all fields.")
            elif len(new_password) < 8:
                st.warning("Password must be at least 8 characters long.")
            else:
                ok, msg = add_user(new_username, new_password, role=new_role_select)
                if ok:
                    st.success(msg)
                    st.session_state["user_created"] = True
                else:
                    st.error(msg)

    if st.session_state.get("user_created"):
        st.session_state["user_created"] = False
        st.rerun()


# ============================
# TAB 2 - CONFIGURE MODELS
# ============================
with tab2:

    experiments = load_experiments()

    st.subheader("Configure Models")

    if not os.path.exists(CONFIG_PATH):
        st.error(f"Configuration file not found: {CONFIG_PATH}")
    else:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

        modelo_selecionado = st.radio(
            "Select the model to configure",
            ["Linear Regression", "Random Forest"],
            horizontal=True
        )
        st.write("")

        # Linear Regression
        if modelo_selecionado == "Linear Regression":
            st.markdown(alert_card(
                ICON_LR, CARD_LR,
                "Linear Regression",
                "Parameters",
                "Configuration of the linear regression model",
                "Adjust the parameters below and click <b>Save and Train</b> to retrain the model."
            ), unsafe_allow_html=True)

            with st.form("lr_form"):
                lr = config.get("linear_regression", {})
                lr_fit_intercept = st.checkbox(
                    "fit_intercept", value=lr.get("fit_intercept", True)
                )
                lr_positive = st.checkbox(
                    "positive", value=lr.get("positive", False)
                )
                submitted = st.form_submit_button(
                    "Save and Train", use_container_width=True
                )

                if submitted:
                    new_lr_config = {
                        "fit_intercept": lr_fit_intercept,
                        "positive": lr_positive,
                    }
                    new_config = {**config, "linear_regression": new_lr_config}
                    new_hash = get_config_hash(new_config)
                    existing_exp = next((
                        e for e in experiments
                        if isinstance(e.get("config_hash"), dict)
                        and e["config_hash"].get("lr") == new_hash["lr"]
                    ), None)

                    if existing_exp:
                        st.warning(
                            f"This configuration has already been trained in run "
                            f"{existing_exp['run_id'][:15]} "
                            f"({existing_exp['timestamp'][:10]})."
                        )
                        exp_result = load_result(existing_exp["run_id"])
                        if exp_result:
                            lr_r = exp_result.get("linear_regression", {})
                            st.markdown(alert_card(
                                ICON_LR, CARD_LR,
                                "Linear Regression - Configuration already trained",
                                f"MAE: {existing_exp['lr_mae']:.1f} MW",
                                f"Run: {existing_exp['timestamp'][:10]}",
                                f"RMSE: {lr_r.get('rmse', 0):.1f} MW &nbsp;·&nbsp;"
                                f" R²: {lr_r.get('r2', 0):.4f}"
                            ), unsafe_allow_html=True)
                    else:
                        with open(CONFIG_PATH, "w") as f:
                            json.dump(new_config, f, indent=4)
                        with st.spinner("Training models..."):
                            success, stderr = run_modeling_pipeline()
                        if success:
                            st.success("Training completed.")
                            experiments = load_experiments()
                            latest = experiments[-1]
                            latest_result = load_result(latest["run_id"])
                            lr_m = (
                                latest_result.get("linear_regression", {})
                                if latest_result else {}
                            )
                            diff = latest["baseline_mae"] - latest["lr_mae"]
                            col_r1, col_r2, col_r3 = st.columns(3)
                            with col_r1:
                                st.markdown(alert_card(
                                    ICON_LR, CARD_LR,
                                    "Linear Regression",
                                    f"MAE: {latest['lr_mae']:.1f} MW",
                                    f"Run: {latest['timestamp'][:10]}",
                                    f"RMSE: {lr_m.get('rmse', 0):.1f} MW &nbsp;·&nbsp;"
                                    f" R²: {lr_m.get('r2', 0):.4f}"
                                ), unsafe_allow_html=True)
                            with col_r2:
                                st.markdown(alert_card(
                                    ICON_BASE, COLOR_ACCENT,
                                    "Baseline",
                                    f"{latest['baseline_mae']:.1f} MW",
                                    "Naive forecast (lag_1h)",
                                    "Reference value for comparison."
                                ), unsafe_allow_html=True)
                            with col_r3:
                                st.markdown(alert_card(
                                    ICON_OK, CARD_OK,
                                    "Improvement vs Baseline",
                                    f"-{diff:.1f} MW",
                                    "Error Reduction",
                                    f"Improvement of {diff / latest['baseline_mae'] * 100:.1f}%"
                                    f" vs baseline."
                                ), unsafe_allow_html=True)
                        else:
                            st.error("Error in training.")
                            st.code(stderr)

        # Random Forest
        else:
            st.markdown(alert_card(
                ICON_RF, COLOR_MID,
                "Random Forest",
                "Parameters",
                "Random forest model configuration",
                "Adjust the parameters below and click <b>Save and Train</b> to retrain the model."
            ), unsafe_allow_html=True)

            with st.form("rf_form"):
                rf = config.get("random_forest", {})
                col_f1, col_f2 = st.columns(2)
                with col_f1:
                    rf_n_estimators = st.number_input(
                        "n_estimators", min_value=10, max_value=1000,
                        value=rf.get("n_estimators", 100), step=10
                    )
                    rf_max_depth = st.number_input(
                        "max_depth", min_value=1, max_value=100,
                        value=rf.get("max_depth", 10), step=1
                    )
                    rf_random_state = st.number_input(
                        "random_state", min_value=0, max_value=9999,
                        value=rf.get("random_state", 42), step=1
                    )
                with col_f2:
                    rf_min_samples_split = st.number_input(
                        "min_samples_split", min_value=2, max_value=20,
                        value=rf.get("min_samples_split", 2), step=1
                    )
                    rf_min_samples_leaf = st.number_input(
                        "min_samples_leaf", min_value=1, max_value=20,
                        value=rf.get("min_samples_leaf", 1), step=1
                    )
                submitted = st.form_submit_button(
                    "Save and Train", use_container_width=True
                )

                if submitted:
                    new_rf_config = {
                        "n_estimators": int(rf_n_estimators),
                        "max_depth": int(rf_max_depth),
                        "min_samples_split": int(rf_min_samples_split),
                        "min_samples_leaf": int(rf_min_samples_leaf),
                        "random_state": int(rf_random_state),
                    }
                    new_config = {**config, "random_forest": new_rf_config}
                    new_hash = get_config_hash(new_config)
                    existing_exp = next((
                        e for e in experiments
                        if isinstance(e.get("config_hash"), dict)
                        and e["config_hash"].get("rf") == new_hash["rf"]
                    ), None)

                    if existing_exp:
                        st.warning(
                            f"Esta configuração já foi treinada no run "
                            f"{existing_exp['run_id'][:15]} "
                            f"({existing_exp['timestamp'][:10]})."
                        )
                        exp_result = load_result(existing_exp["run_id"])
                        if exp_result:
                            rf_r = exp_result.get("random_forest", {})
                            st.markdown(alert_card(
                                ICON_RF, COLOR_MID,
                                "Random Forest - Existing Run",
                                f"MAE: {existing_exp['rf_mae']:.1f} MW",
                                f"Run: {existing_exp['timestamp'][:10]}",
                                f"RMSE: {rf_r.get('rmse', 0):.1f} MW &nbsp;·&nbsp;"
                                f" R²: {rf_r.get('r2', 0):.4f}"
                            ), unsafe_allow_html=True)
                    else:
                        with open(CONFIG_PATH, "w") as f:
                            json.dump(new_config, f, indent=4)
                        with st.spinner("Training models..."):
                            success, stderr = run_modeling_pipeline()
                        if success:
                            st.success("Training completed.")
                            experiments = load_experiments()
                            latest = experiments[-1]
                            latest_result = load_result(latest["run_id"])
                            rf_m = (
                                latest_result.get("random_forest", {})
                                if latest_result else {}
                            )
                            diff = latest["baseline_mae"] - latest["rf_mae"]
                            col_r1, col_r2, col_r3 = st.columns(3)
                            with col_r1:
                                st.markdown(alert_card(
                                    ICON_RF, COLOR_MID,
                                    "Random Forest",
                                    f"MAE: {latest['rf_mae']:.1f} MW",
                                    f"Run: {latest['timestamp'][:10]}",
                                    f"RMSE: {rf_m.get('rmse', 0):.1f} MW &nbsp;·&nbsp;"
                                    f" R²: {rf_m.get('r2', 0):.4f}"
                                ), unsafe_allow_html=True)
                            with col_r2:
                                st.markdown(alert_card(
                                    ICON_BASE, COLOR_ACCENT,
                                    "Baseline",
                                    f"{latest['baseline_mae']:.1f} MW",
                                    "Naive forecast (lag_1h)",
                                    "Reference value for comparison."
                                ), unsafe_allow_html=True)
                            with col_r3:
                                st.markdown(alert_card(
                                    ICON_OK, CARD_OK,
                                    "Improvement vs Baseline",
                                    f"-{diff:.1f} MW",
                                    "Error Reduction",
                                    f"Improvement of {diff / latest['baseline_mae'] * 100:.1f}%"
                                    f" vs baseline."
                                ), unsafe_allow_html=True)
                        else:
                            st.error("Error in training.")
                            st.code(stderr)

    st.write("---")

    # Desempenho atual
    st.subheader("Current Performance")
    if experiments:
        latest = experiments[-1]
        render_metrics_cards(latest, load_result(latest["run_id"]))
    else:
        st.info("No experiments found. Run the pipeline first.")

    st.write("---")

    # Histórico
    st.subheader("History of Experiments")
    if not experiments:
        st.info("No experiments registered.")
    else:
        n_show = st.slider(
            "Number of runs to show", min_value=5, max_value=20, value=5, step=5
        )
        recent = list(reversed(experiments))[:n_show]
        df_exp = pd.DataFrame([{
            "Data": e["timestamp"][:10],
            "Hora": e["timestamp"][11:16],
            "Baseline MAE": f"{e['baseline_mae']:.1f}",
            "LR MAE": f"{e['lr_mae']:.1f}",
            "RF MAE": f"{e['rf_mae']:.1f}",
            "Best Model": (
                "Random Forest"
                if e["best_model"] == "random_forest"
                else "Linear Regression"
            ),
        } for e in recent])
        st.dataframe(df_exp, use_container_width=True, hide_index=True)

        st.write("")
        run_labels_hist = [
            f"{e['timestamp'][:10]} ({e['timestamp'][11:16]})" for e in recent
        ]
        run_ids_hist = [e["run_id"] for e in recent]
        sel_detail = st.selectbox(
            "Ver detalhes do run", run_labels_hist, key="detail_select"
        )
        detail_run_id = run_ids_hist[run_labels_hist.index(sel_detail)]
        detail_result = load_result(detail_run_id)
        detail_exp = next(e for e in experiments if e["run_id"] == detail_run_id)

        if detail_result:
            cfg = detail_result.get("config", {})
            lr_cfg = cfg.get("linear_regression", {})
            rf_cfg = cfg.get("random_forest", {})
            lr_m = detail_result.get("linear_regression", {})
            rf_m = detail_result.get("random_forest", {})
            best_label = (
                "Random Forest"
                if detail_exp["best_model"] == "random_forest"
                else "Linear Regression"
            )

            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.markdown(alert_card(
                    ICON_LR, CARD_LR,
                    "Parâmetros - Linear Regression",
                    "",
                    "",
                    f"<b>fit_intercept:</b> {lr_cfg.get('fit_intercept', '-')}<br>"
                    f"<b>positive:</b> {lr_cfg.get('positive', '-')}",
                    min_height="260px"
                ), unsafe_allow_html=True)
            with col_d2:
                st.markdown(alert_card(
                    ICON_RF, COLOR_MID,
                    "Parâmetros - Random Forest",
                    "",
                    "",
                    f"<b>n_estimators:</b> {rf_cfg.get('n_estimators', '-')}<br>"
                    f"<b>max_depth:</b> {rf_cfg.get('max_depth', '-')}<br>"
                    f"<b>min_samples_split:</b> {rf_cfg.get('min_samples_split', '-')}<br>"
                    f"<b>min_samples_leaf:</b> {rf_cfg.get('min_samples_leaf', '-')}<br>"
                    f"<b>random_state:</b> {rf_cfg.get('random_state', '-')}",
                    min_height="260px"
                ), unsafe_allow_html=True)
            with col_d3:
                st.markdown(alert_card(
                    ICON_BEST, CARD_OK,
                    "Métricas do Run",
                    f"Melhor: {best_label}",
                    "Baseline vs Modelos",
                    f"<b>Baseline</b> - MAE: {detail_exp['baseline_mae']:.1f} MW<br><br>"
                    f"<b>LR</b> - MAE: {detail_exp['lr_mae']:.1f} · "
                    f"RMSE: {lr_m.get('rmse', 0):.1f} · R²: {lr_m.get('r2', 0):.4f}<br>"
                    f"<b>RF</b> - MAE: {detail_exp['rf_mae']:.1f} · "
                    f"RMSE: {rf_m.get('rmse', 0):.1f} · R²: {rf_m.get('r2', 0):.4f}",
                    min_height="260px",
                    value_size="1.3rem"
                ), unsafe_allow_html=True)

    st.write("---")

    # Comparar Runs
    st.subheader("Compare Runs")
    if len(experiments) < 2:
        st.info("You need at least 2 runs to compare.")
    else:
        run_ids = [e["run_id"] for e in experiments]
        run_labels = [
            f"{e['timestamp'][:10]} ({e['timestamp'][11:16]})"
            for e in experiments
        ]
        col_a, col_b = st.columns(2)
        with col_a:
            sel_a = st.selectbox("Run A", run_labels, index=0, key="compare_a")
        with col_b:
            sel_b = st.selectbox(
                "Run B", run_labels, index=min(1, len(run_labels) - 1), key="compare_b"
            )
        run_id_a = run_ids[run_labels.index(sel_a)]
        run_id_b = run_ids[run_labels.index(sel_b)]
        result_a = load_result(run_id_a)
        result_b = load_result(run_id_b)
        exp_a = next(e for e in experiments if e["run_id"] == run_id_a)
        exp_b = next(e for e in experiments if e["run_id"] == run_id_b)

        if result_a and result_b:
            col_ra, col_rb = st.columns(2)
            for col, exp, result, label, icon_color, icon in [
                (col_ra, exp_a, result_a, "Run A", CARD_LR, ICON_LR),
                (col_rb, exp_b, result_b, "Run B", COLOR_MID, ICON_RF),
            ]:
                rf = result["random_forest"]
                lr = result["linear_regression"]
                best = (
                    "Random Forest"
                    if exp["best_model"] == "random_forest"
                    else "Linear Regression"
                )
                with col:
                    st.markdown(alert_card(
                        icon, icon_color,
                        f"{label} - {exp['run_id'][:15]}",
                        f"Melhor: {best}",
                        exp["timestamp"][:10],
                        f"<b>Baseline MAE:</b> {exp['baseline_mae']:.1f} MW<br><br>"
                        f"<b>Linear Regression</b> - MAE: {exp['lr_mae']:.1f} · "
                        f"RMSE: {lr['rmse']:.1f} · R²: {lr['r2']:.4f}<br>"
                        f"<b>Random Forest</b> - MAE: {exp['rf_mae']:.1f} · "
                        f"RMSE: {rf['rmse']:.1f} · R²: {rf['r2']:.4f}"
                    ), unsafe_allow_html=True)
        else:
            st.markdown(alert_card(
                ICON_ERR, CARD_ERR,
                "Dados em falta",
                "",
                "Ficheiros de resultados não encontrados",
                "Apenas runs com <b>results_*.json</b> em <b>data/results/</b>"
                " podem ser comparados."
            ), unsafe_allow_html=True)


# ==========================
# TAB 3 - CORRER PIPELINE
# ==========================
with tab3:

    if "pipeline_initialized" not in st.session_state:
        for key in ["step_ingestion", "step_processing", "step_modeling", "step_all"]:
            st.session_state[key] = "pending"
        st.session_state["pipeline_initialized"] = True

    st.subheader("Run Pipeline")

    energy_file = os.path.exists(
        os.path.join(ROOT_DIR, "data/raw/energy/load_DE_2025.csv")
    )
    features_path = os.path.join(ROOT_DIR, "data/processed/features.csv")
    features_file = os.path.exists(features_path) and os.path.getsize(features_path) > 0

    # Pipeline completa
    st.markdown(pipeline_step_card(
        ICON_PIPE, CARD_LR,
        "Pipeline Completed",
        "Run all steps sequentially - ingestion, processing, and modeling.",
        status_html(st.session_state["step_all"]),
        min_height="180px"
    ), unsafe_allow_html=True)

    include_ingestion = st.checkbox("Include Data Ingestion")
    if include_ingestion:
        st.warning("Data ingestion may take around 1h30.")

    if st.button("Run Complete Pipeline", key="run_full_pipeline"):
        st.session_state["step_all"] = "running"
        with st.spinner("Running complete pipeline..."):
            success = run_pipeline_block(include_ingestion=include_ingestion)
        if success:
            st.session_state["step_all"] = "done"
            if include_ingestion:
                st.session_state["step_ingestion"] = "done"
            st.session_state["step_processing"] = "done"
            st.session_state["step_modeling"] = "done"
        else:
            st.session_state["step_all"] = "error"
        st.rerun()

    st.write("---")

    # Controlo individual
    st.markdown("#### Controlo Individual")
    st.caption("Run each step separately, in this order.")
    st.write("")

    col_s1, col_arr1, col_s2, col_arr2, col_s3 = st.columns(
        [1, 0.15, 1, 0.15, 1],
        vertical_alignment="top"
    )

    with col_s1:
        st.markdown(pipeline_step_card(
            ICON_STEP, COLOR_MID,
            "Data Ingestion",
            "Obtains energy data from the external source. May take around ~1h30.",
            status_html(st.session_state["step_ingestion"])
        ), unsafe_allow_html=True)
        st.markdown("<div style='height:36px;'></div>", unsafe_allow_html=True)
        if st.button("Run", key="btn_ingestion", use_container_width=True):
            st.session_state["step_ingestion"] = "running"
            with st.spinner("Running data ingestion..."):
                success = run_pipeline_block(mode="ingestion")
            st.session_state["step_ingestion"] = "done" if success else "error"
            st.rerun()

    with col_arr1:
        st.markdown(
            f"<div style='text-align:center; font-size:2rem; "
            f"padding-top:60px; color:{COLOR_MID};'>→</div>",
            unsafe_allow_html=True
        )

    with col_s2:
        st.markdown(pipeline_step_card(
            ICON_STEP, COLOR_MID,
            "Data Processing",
            "Cleaning of raw data and creation of features for modeling.",
            status_html(st.session_state["step_processing"])
        ), unsafe_allow_html=True)
        st.markdown("<div style='height:36px;'></div>", unsafe_allow_html=True)
        if st.button("Run", key="btn_processing", use_container_width=True):
            if not energy_file:
                st.error("Ensure the energy file exists first.")
            else:
                st.session_state["step_processing"] = "running"
                with st.spinner("Processing data..."):
                    success = run_pipeline_block(mode="processing")
                st.session_state["step_processing"] = "done" if success else "error"
                st.rerun()

    with col_arr2:
        st.markdown(
            f"<div style='text-align:center; font-size:2rem; "
            f"padding-top:60px; color:{COLOR_MID};'>→</div>",
            unsafe_allow_html=True
        )

    with col_s3:
        st.markdown(pipeline_step_card(
            ICON_STEP, COLOR_MID,
            "Modeling",
            "Training of prediction models with the generated features.",
            status_html(st.session_state["step_modeling"])
        ), unsafe_allow_html=True)
        run_grid_search_option = st.checkbox(
            "Run Grid Search",
            help="Takes quite a while but optimizes the hyperparameters."
        )
        if st.button("Run", key="btn_modeling", use_container_width=True):
            if not features_file:
                st.error("Run the processing step first to generate features.csv.")
            else:
                st.session_state["step_modeling"] = "running"
                with st.spinner("Training models..."):
                    success = run_pipeline_block(
                        mode="modeling",
                        include_gridsearch=run_grid_search_option
                    )
                st.session_state["step_modeling"] = "done" if success else "error"
                st.rerun()

    # Logs
    st.write("---")
    with st.expander("View System Logs", expanded=True):
        log_files = {
            "Reliability Log": os.path.join(LOG_DIR, "reliability.log"),
            "Performance Log": os.path.join(LOG_DIR, "performance.log"),
        }
        selected_log = st.selectbox("Select the log", list(log_files.keys()))
        log_path = log_files[selected_log]

        if os.path.exists(log_path):
            if "log_lines" not in st.session_state:
                st.session_state["log_lines"] = 200
            num_lines = st.slider(
                "Number of lines", min_value=20, max_value=1000,
                value=st.session_state["log_lines"], step=20, key="log_slider"
            )
            st.session_state["log_lines"] = num_lines
            st.button("Update Logs")
            with open(log_path, "r", encoding="cp1252", errors="ignore") as f:
                lines = f.readlines()
            st.code("".join(lines[-num_lines:]), language="text")
        else:
            st.info("Log still does not exist.")

import sys
import os
import streamlit as st

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Climate Energy System",
    layout="wide",
)

# =========================
# SESSION
# =========================

if "user" not in st.session_state:
    st.session_state.user = None

# =========================
# PAGES
# =========================

home = st.Page(
    "pages/home.py",
    title="Home",
    default=True
)

login = st.Page(
    "pages/login.py",
    title="Login"
)

dashboard = st.Page(
    "pages/dashboard.py",
    title="Dashboard"
)

predict = st.Page(
    "pages/predict.py",
    title="Predict"
)

metrics = st.Page(
    "pages/metrics.py",
    title="Metrics"
)

data = st.Page(
    "pages/data.py",
    title="Data"
)

admin = st.Page(
    "pages/admin.py",
    title="Admin"
)

logout = st.Page(
    "pages/logout.py",
    title="Logout"
)

# =========================
# NAVIGATION
# =========================

if st.session_state.user is None:
    pg = st.navigation({
        "Welcome": [home, login]
    })

else:
    pages = {
        "Analytics": [dashboard, predict, metrics, data],
    }

    # ADMIN ONLY - aparece antes do Account
    if st.session_state.user["role"] == "admin":
        pages["Admin"] = [admin]

    pages["Account"] = [logout]

    pg = st.navigation(pages)

# RUN PAGE
pg.run()

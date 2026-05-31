import streamlit as st
import sys
import os
import base64
from dotenv import load_dotenv
from src.utils.user_manager import authenticate, add_user

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

load_dotenv()

st.set_page_config(page_title="Login", layout="centered")

st.session_state.setdefault("user", None)

if st.session_state.get("user"):
    st.switch_page("pages/Home.py")


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

[data-testid="stMainBlockContainer"] > div:first-child {
    max-width: 460px;
    margin: 5vh auto 0 auto;
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(14px);
    padding: 40px;
    border-radius: 24px;
    box-shadow: 0 10px 30px rgba(131, 188, 212, 0.18);
    border: 1px solid rgba(164, 209, 224, 0.3);
}

/* LOGO BOX */
.login-logo-wrapper {
    display: flex;
    justify-content: center;
    margin-bottom: 1.5rem;
}
.login-logo-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    background: rgba(255, 255, 255, 0.45);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 1.4rem 2.5rem;
    box-shadow: 0 4px 16px rgba(131, 188, 212, 0.15);
    border: 1px solid rgba(164, 209, 224, 0.3);
}
.login-logo-box img.login-logo {
    height: 70px;
    object-fit: contain;
}
.login-logo-box img.login-nome {
    height: 38px;
    object-fit: contain;
}

.subtitle {
    color: #1F4D5C;
    margin-bottom: 1.5rem;
    text-align: center;
    font-size: 1rem;
    font-weight: 400;
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
[data-baseweb="tab-highlight"] {
    background-color: #1E5A5C !important;
}
[data-baseweb="tab-border"] {
    background-color: rgba(164, 209, 224, 0.4) !important;
}

/* BOTÃO LOGIN - azul escuro */
div[data-testid="stForm"] .stButton > button {
    background: linear-gradient(135deg, #1F4D5C, #1E5A5C) !important;
    color: white !important;
    border-radius: 12px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    font-weight: 600;
    font-family: 'Poppins', sans-serif;
    border: none;
    transition: 0.3s;
}
div[data-testid="stForm"] .stButton > button:hover {
    transform: scale(1.02);
    background: linear-gradient(135deg, #1A3A4A, #1F4D5C) !important;
}

/* BOTÃO CREATE ACCOUNT - verde escuro */
div[data-testid="stVerticalBlock"] .stButton > button {
    background: linear-gradient(135deg, #1A4228, #0F5C38) !important;
    color: white !important;
    border-radius: 12px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    font-weight: 600;
    font-family: 'Poppins', sans-serif;
    border: none;
    transition: 0.3s;
}
div[data-testid="stVerticalBlock"] .stButton > button:hover {
    transform: scale(1.02);
    background: linear-gradient(135deg, #0F5C38, #1A4228) !important;
}

input {
    border-radius: 10px !important;
}

[data-testid="stSidebar"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none;
}
#MainMenu, header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# Logo
logo_path = "src/utils/LOGO_claro.png"
nome_path = "src/utils/NOME_claro.png"

if os.path.exists(logo_path) and os.path.exists(nome_path):
    logo_b64 = img_to_base64(logo_path)
    nome_b64 = img_to_base64(nome_path)
    st.markdown(f"""
        <div class="login-logo-wrapper">
            <div class="login-logo-box">
                <img class="login-logo" src="data:image/png;base64,{logo_b64}" alt="logo">
                <img class="login-nome" src="data:image/png;base64,{nome_b64}" alt="nome">
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="subtitle">Login or create an account</div>', unsafe_allow_html=True)


# Tabs
tab1, tab2 = st.tabs(["Login", "Sign Up"])

with tab1:
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if not username or not password:
            st.warning("Fill in both fields.")
        else:
            user = authenticate(username, password)
            if user:
                st.session_state["user"] = user
                st.switch_page("pages/Home.py")
            else:
                st.error("Invalid credentials.")


with tab2:
    with st.form("signup_form"):
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password",  type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="reg_pass2")
        admin_token = st.text_input("Admin Token (opcional)", type="password", key="reg_token")
        submitted2 = st.form_submit_button("Create Account", use_container_width=True)

    if submitted2:
        if not new_user or not new_pass or not confirm_pass:
            st.warning("Fill in all fields.")
        elif len(new_pass) < 8:
            st.warning("Password must be at least 8 characters long.")
        elif new_pass != confirm_pass:
            st.warning("Passwords do not match.")
        else:
            ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")
            if admin_token and admin_token == ADMIN_TOKEN:
                role = "admin"
            elif admin_token and admin_token != ADMIN_TOKEN:
                st.error("Invalid admin token.")
                st.stop()
            else:
                role = "user"

            success, msg = add_user(new_user, new_pass, role=role)
            if success:
                st.success(f"Account {'admin ' if role == 'admin' else ''}created successfully! Please log in.")
            else:
                st.error(msg)

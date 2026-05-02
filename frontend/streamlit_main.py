"""
Enhanced Streamlit UI for AI Healthcare Assistant
Multi-page application with symptom analysis, doctor finder, appointments, and chat
"""
import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from typing import Optional
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.translation import LocalizationManager, get_translation_service

# Page Configuration
st.set_page_config(
    page_title="AI Healthcare Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.user_name = ""
    st.session_state.language = "EN"
    st.session_state.symptoms = []
    st.session_state.diagnoses = []
    st.session_state.selected_doctor = None
    st.session_state.appointment_id = None
    st.session_state.chat_mode = None

# API Configuration
API_BASE_URL = "http://127.0.0.1:8003/api/v1"
TRANSLATION_SERVICE = get_translation_service()


def get_localized_text(key: str) -> str:
    """Get localized UI text"""
    return LocalizationManager.get_localized_string(key, st.session_state.language)


# ============== SIDEBAR ==============

with st.sidebar:
    st.image("🏥", width=50)
    st.title("AI Healthcare Assistant")
    
    # Language Selection
    st.subheader("⚙️ Settings")
    language = st.selectbox(
        "🌐 Language / भाषा / भाषा",
        options=["EN (English)", "HI (हिंदी)", "MR (मराठी)"],
        index=0
    )
    
    lang_code_map = {"EN (English)": "EN", "HI (हिंदी)": "HI", "MR (मराठी)": "MR"}
    st.session_state.language = lang_code_map.get(language, "EN")
    
    # User Info
    st.divider()
    st.subheader("👤 Profile")
    
    if st.session_state.user_id:
        st.write(f"**{get_localized_text('welcome')}**")
        st.write(f"ID: {st.session_state.user_id[:8]}...")
        
        if st.button("🚪 Logout"):
            st.session_state.user_id = None
            st.rerun()
    else:
        user_id = st.text_input("Enter your ID (7-8 digits):")
        if st.button("Login"):
            if len(user_id) in [7, 8] and user_id.isdigit():
                st.session_state.user_id = user_id
                st.rerun()
            else:
                st.error("Invalid ID format")
    
    st.divider()
    
    # Medical Disclaimer
    with st.expander("⚠️ Medical Disclaimer"):
        st.warning(LocalizationManager.get_localized_string("medical_disclaimer", st.session_state.language))


# ============== MAIN CONTENT ==============

# Navigation
page = st.navigation([
    st.Page("pages/1_home.py", title="🏠 Home"),
    st.Page("pages/2_symptom_checker.py", title="🔍 Symptom Checker"),
    st.Page("pages/3_doctor_finder.py", title="👨‍⚕️ Find Doctor"),
    st.Page("pages/4_appointments.py", title="📅 My Appointments"),
    st.Page("pages/5_chat.py", title="💬 Chat with Doctor"),
])

page.run()

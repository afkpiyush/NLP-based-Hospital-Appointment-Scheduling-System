"""
Page 1: Home
Main landing page with overview and quick actions
"""
import streamlit as st
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(page_title="AI Healthcare Assistant", layout="wide")

from login_utils import initialize_session_state, show_login_form

# Initialize session state
initialize_session_state()

# Show login form if not logged in
if not st.session_state.user_id:
    st.title("🏥 AI Healthcare Assistant")
    st.markdown("""Welcome to your AI-powered healthcare assistant. This platform helps you:
    - Analyze symptoms with AI
    - Find nearby doctors
    - Book appointments
    - Chat with healthcare professionals
    """)
    show_login_form()
    st.stop()

st.title("🏥 Welcome to AI Healthcare Assistant")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 Symptom Checker")
    st.write("""
    Describe your symptoms and let our AI analyze them:
    - Extract symptoms from natural language
    - Predict possible conditions
    - Recommend appropriate specialists
    """)
    if st.button("Start Symptom Check", key="symptom_btn"):
        st.switch_page("pages/2_symptom_checker.py")

with col2:
    st.subheader("👨‍⚕️ Find a Doctor")
    st.write("""
    Find specialized doctors near you:
    - Search by specialization
    - View doctor profiles and ratings
    - Check availability and book appointments
    """)
    if st.button("Search Doctors", key="doctor_btn"):
        st.switch_page("pages/3_doctor_finder.py")

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("📅 My Appointments")
    st.write("""
    Manage your appointments:
    - View booked appointments
    - Reschedule or cancel
    - Get appointment reminders
    """)
    if st.button("View Appointments", key="apt_btn"):
        st.switch_page("pages/4_appointments.py")

with col4:
    st.subheader("💬 Doctor Chat")
    st.write("""
    Chat with healthcare professionals:
    - General consultation without appointment
    - Real-time messaging after appointments
    - Share medical history
    - Get follow-up advice
    """)
    if st.button("Open Chat", key="chat_btn"):
        st.switch_page("pages/5_chat.py")

st.divider()

st.info("""
**How It Works:**

**Option 1: Quick Consultation (No Appointment Needed)**
1. Login with your ID
2. Go to Chat with Doctor
3. Select "General Consultation"
4. Start chatting with healthcare professionals

**Option 2: Full Medical Workflow**
1. Describe your symptoms in natural language
2. AI analyzes and predicts possible conditions
3. Get recommended specialists
4. Find and book appointment with nearby doctor
5. Chat with your doctor post-appointment
""")

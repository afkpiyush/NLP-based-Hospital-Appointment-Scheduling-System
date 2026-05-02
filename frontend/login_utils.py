"""
Login utilities for authentication across pages
"""
import streamlit as st


def initialize_session_state():
    """Initialize all required session state variables"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
        st.session_state.user_name = ""
        st.session_state.language = "EN"
        st.session_state.symptoms = []
        st.session_state.diagnoses = []
        st.session_state.selected_doctor = None
        st.session_state.appointment_id = None
        st.session_state.chat_mode = None


def show_login_form():
    """Display login form and handle authentication"""
    st.markdown("---")
    st.subheader("👤 Login Required")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_id = st.text_input(
            "Enter your ID (7-8 digits):",
            placeholder="e.g., 1234567",
            key="login_user_id"
        )
    
    with col2:
        st.write("")  # Spacing
        login_button = st.button("Login", type="primary", use_container_width=True)
    
    if login_button:
        if user_id and len(user_id) in [7, 8] and user_id.isdigit():
            st.session_state.user_id = user_id
            st.success(f"✅ Logged in as {user_id}")
            st.rerun()
        elif user_id:
            st.error("❌ Invalid ID format. Please enter 7-8 digits.")
        else:
            st.error("❌ Please enter your ID.")
    
    st.info("Don't have an ID? Use any 7-8 digit number for testing (e.g., 1234567)")
    st.markdown("---")


def require_login(page_title: str = ""):
    """Require user to be logged in, show login form if not"""
    initialize_session_state()
    
    if not st.session_state.user_id:
        st.warning(f"⚠️ Please login to access {page_title}")
        show_login_form()
        st.stop()

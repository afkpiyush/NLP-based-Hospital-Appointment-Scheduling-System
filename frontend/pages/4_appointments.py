"""
Page 4: My Appointments
View, reschedule, and cancel appointments
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from login_utils import require_login, initialize_session_state

st.set_page_config(page_title="My Appointments", layout="wide")

# Require login with form
require_login("My Appointments")

st.title("📅 My Appointments")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Upcoming", "✅ Completed", "❌ Cancelled"])

with tab1:
    st.subheader("Upcoming Appointments")
    
    with st.spinner("Loading appointments..."):
        try:
            response = requests.get(
                f"http://127.0.0.1:8003/api/v1/users/{st.session_state.user_id}/appointments",
                params={"status": "BOOKED"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                appointments = data.get("appointments", [])
                
                if appointments:
                    for apt in appointments:
                        with st.container(border=True):
                            col1, col2, col3 = st.columns([2, 1, 1])
                            
                            with col1:
                                st.write(f"**Date:** {apt.get('appointment_date', '')}")
                                st.write(f"**Doctor:** Dr. {apt.get('doctor_id', '')}")
                                st.write(f"**Reason:** {apt.get('reason_for_visit', '')}")
                            
                            with col2:
                                st.metric("Status", apt.get('status', 'UNKNOWN'), delta=None)
                            
                            with col3:
                                if st.button("💬 Chat", key=f"chat_{apt.get('appointment_id')}"):
                                    st.session_state.appointment_id = apt.get('appointment_id')
                                    st.switch_page("pages/5_chat.py")
                else:
                    st.info("No upcoming appointments. Book one now!")
                    
            else:
                st.error("Error loading appointments")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab2:
    st.subheader("Completed Appointments")
    st.info("No completed appointments yet")

with tab3:
    st.subheader("Cancelled Appointments")
    st.info("No cancelled appointments yet")

st.divider()

# Book New Appointment
if st.button("🆕 Book New Appointment", type="primary", use_container_width=True):
    st.switch_page("pages/3_doctor_finder.py")

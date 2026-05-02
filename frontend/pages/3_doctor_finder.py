"""
Page 3: Doctor Finder
Find nearby doctors, view availability, and book appointments
"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from login_utils import require_login, initialize_session_state

st.set_page_config(page_title="Find Doctor", layout="wide")

# Require login with form
require_login("Find Doctor")

st.title("👨‍⚕️ Find a Doctor")

# Search Filters
col1, col2, col3, col4 = st.columns(4)

with col1:
    specialization = st.text_input("Specialization:", placeholder="e.g., Cardiologist")

with col2:
    latitude = st.number_input("Latitude:", format="%.4f", value=19.0760)

with col3:
    longitude = st.number_input("Longitude:", format="%.4f", value=72.8777)

with col4:
    distance = st.slider("Max Distance (km):", 1, 100, 25)

# Search Button
if st.button("🔍 Search Doctors", type="primary", use_container_width=True):
    if not specialization.strip():
        st.error("Please enter specialization")
    else:
        with st.spinner("Searching for doctors..."):
            try:
                response = requests.get(
                    f"http://127.0.0.1:8003/api/v1/doctors/search",
                    params={
                        "specialization": specialization,
                        "latitude": latitude,
                        "longitude": longitude,
                        "max_distance_km": distance
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    doctors = data.get("doctors", [])
                    
                    if doctors:
                        st.success(f"Found {len(doctors)} doctors")
                        
                        # Display doctors
                        for doctor in doctors:
                            with st.container(border=True):
                                col1, col2, col3 = st.columns([2, 1, 1])
                                
                                with col1:
                                    st.subheader(f"Dr. {doctor.get('name', 'Unknown')}")
                                    st.write(f"**Specialization:** {doctor.get('specialization', '')}")
                                    st.write(f"**Experience:** {doctor.get('experience_years', 0)} years")
                                    st.write(f"**Consultation Fee:** ₹{doctor.get('consultation_fee', 0)}")
                                
                                with col2:
                                    rating = doctor.get('rating', 0)
                                    st.metric("Rating", f"{rating:.1f}/5.0", delta=None)
                                
                                with col3:
                                    if st.button("📅 View Slots", key=doctor.get('doctor_id')):
                                        st.session_state.selected_doctor = doctor
                                        st.switch_page("pages/4_booking.py")
                    else:
                        st.info("No doctors found matching your criteria. Try different filters.")
                        
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")

st.divider()

# Quick Doctor Suggestions
st.subheader("💡 Suggested Specialists for Your Symptoms")

if st.session_state.symptoms:
    suggested = ["General Physician", "Internal Medicine"]
    for spec in suggested:
        if st.button(f"Search for {spec}", key=f"quick_{spec}"):
            st.rerun()
else:
    st.info("Complete symptom analysis first to get personalized recommendations")

"""
Page 2: Symptom Checker
AI-powered symptom analysis with natural language input
"""
import streamlit as st
import requests
import json
from datetime import datetime
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from login_utils import require_login, initialize_session_state

st.set_page_config(page_title="Symptom Checker", layout="wide")

# Require login with form
require_login("Symptom Checker")

st.title("🔍 Symptom Checker")

st.write("Describe your symptoms in detail and let AI analyze them.")

# Input Section
col1, col2 = st.columns([3, 1])

with col1:
    symptom_input = st.text_area(
        "Describe your symptoms:",
        placeholder="Example: I have been experiencing a high fever (39.5°C) for 2 days, along with severe headache and body aches. I also have a dry cough...",
        height=150,
        label_visibility="collapsed"
    )

with col2:
    input_language = st.selectbox(
        "Language:",
        options=["EN", "HI", "MR"],
        index=["EN", "HI", "MR"].index(st.session_state.language)
    )

if st.button("🔄 Analyze Symptoms", type="primary", use_container_width=True):
    if not symptom_input.strip():
        st.error("Please describe your symptoms")
    else:
        with st.spinner("Analyzing your symptoms..."):
            try:
                # Call API
                response = requests.post(
                    f"{st.session_state.api_url}/symptoms/analyze",
                    json={
                        "patient_description": symptom_input,
                        "language": input_language,
                        "user_id": st.session_state.user_id
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.symptoms = data.get("symptoms", [])
                    st.success("✅ Symptoms analyzed successfully!")
                    
                    # Display Results
                    st.divider()
                    st.subheader("📋 Analysis Results")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Symptoms Identified",
                            len(st.session_state.symptoms),
                            delta=None
                        )
                    
                    with col2:
                        st.metric(
                            "Analysis Confidence",
                            f"{data.get('analysis_confidence', 0)*100:.0f}%",
                            delta=None
                        )
                    
                    with col3:
                        urgency = "🟢 Normal" if not data.get("needs_urgent_care") else "🔴 Urgent"
                        st.metric("Urgency Level", urgency, delta=None)
                    
                    # Detailed Symptoms Table
                    st.subheader("🩺 Extracted Symptoms")
                    symptoms_df = []
                    for symptom in st.session_state.symptoms:
                        symptoms_df.append({
                            "Symptom": symptom.get("name", ""),
                            "Severity": symptom.get("severity", ""),
                            "Duration": symptom.get("duration_days", "N/A")
                        })
                    
                    if symptoms_df:
                        st.dataframe(symptoms_df, use_container_width=True)
                    
                    # Next Steps
                    st.divider()
                    st.subheader("📈 Next Steps")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("🔬 Get AI Diagnosis"):
                            st.switch_page("pages/2_diagnosis.py")
                    
                    with col2:
                        if st.button("👨‍⚕️ Find Specialist"):
                            st.switch_page("pages/3_doctor_finder.py")
                    
                    with col3:
                        if st.button("🏥 Emergency Services"):
                            st.info("Please call your local emergency number or visit nearest hospital")
                    
                else:
                    st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                    
            except requests.exceptions.Timeout:
                st.error("Request timeout. Please try again.")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Additional Features
st.divider()
st.subheader("💡 Tips for Better Analysis")

tips = [
    "Be specific about symptoms (location, intensity, timing)",
    "Mention how long you've had the symptoms",
    "Include any recent exposure or travel",
    "Describe any associated symptoms",
    "Mention existing medical conditions"
]

for i, tip in enumerate(tips, 1):
    st.write(f"{i}. {tip}")

# Disclaimer
st.warning("""
⚠️ **Medical Disclaimer**: This analysis is AI-generated for informational purposes only
and is NOT a medical diagnosis. Please consult a qualified healthcare professional
for accurate diagnosis and treatment.
""")

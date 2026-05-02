"""
Page 5: Doctor Chat
Real-time messaging with doctors post-appointment
"""
import streamlit as st
import requests
import asyncio
import json
from datetime import datetime
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(page_title="Chat with Doctor", layout="wide")

from login_utils import require_login, initialize_session_state

# Require login with form
require_login("Chat with Doctor")

st.title("💬 Chat with Doctor")

# Initialize chat mode if not set
if "chat_mode" not in st.session_state:
    st.session_state.chat_mode = None

# Chat mode selection
col1, col2 = st.columns(2)
with col1:
    if st.button("📋 Chat about Appointment", use_container_width=True):
        st.session_state.chat_mode = "appointment"
        st.rerun()

with col2:
    if st.button("🆘 General Consultation", use_container_width=True):
        st.session_state.chat_mode = "general"
        st.rerun()

if not st.session_state.chat_mode:
    st.info("Select a chat option above to get started")
    st.stop()

# Get appointment details if in appointment mode
appointment = {}
if st.session_state.chat_mode == "appointment":
    if not st.session_state.appointment_id:
        st.info("Please select an appointment first")
        if st.button("Go to Appointments"):
            st.switch_page("pages/4_appointments.py")
        st.stop()
    
    try:
        apt_response = requests.get(
            f"http://127.0.0.1:8003/api/v1/appointments/{st.session_state.appointment_id}",
            timeout=30
        )
        appointment = apt_response.json()
    except:
        appointment = {}

# Header
col1, col2 = st.columns([2, 1])

with col1:
    if st.session_state.chat_mode == "appointment":
        st.subheader(f"Chat with Dr. {appointment.get('doctor_id', 'Doctor')}")
        st.write(f"Appointment: {appointment.get('appointment_date', 'N/A')}")
    else:
        st.subheader("General Consultation Chat")
        st.write("Ask a healthcare professional a question")

with col2:
    if st.button("🔄 Refresh", key="refresh_chat"):
        st.rerun()

st.divider()

# Determine chat ID
if st.session_state.chat_mode == "appointment":
    chat_id = st.session_state.appointment_id
else:
    chat_id = f"general_{st.session_state.user_id}"

# Chat Messages Container
messages_placeholder = st.container()

# Get chat history
try:
    with st.spinner("Loading chat history..."):
        response = requests.get(
            f"http://127.0.0.1:8003/api/v1/chats/{chat_id}/history",
            timeout=30
        )
        
        if response.status_code == 200:
            chat_data = response.json()
            messages = chat_data.get("messages", [])
            
            with messages_placeholder:
                for msg in messages:
                    sender = msg.get("sender_type", "")
                    content = msg.get("content", "")
                    timestamp = msg.get("timestamp", "")
                    
                    if sender == "USER":
                        with st.chat_message("user"):
                            st.write(content)
                            st.caption(timestamp)
                    else:
                        with st.chat_message("assistant"):
                            st.write(content)
                            st.caption(timestamp)
except:
    with messages_placeholder:
        st.info("No messages yet. Start the conversation!")

st.divider()

# Message Input
col1, col2 = st.columns([4, 1])

with col1:
    message_input = st.text_area(
        "Type your message:",
        placeholder="Ask doctor a question or share information...",
        height=100,
        label_visibility="collapsed"
    )

with col2:
    if st.button("📤 Send", type="primary", use_container_width=True):
        if message_input.strip():
            with st.spinner("Sending..."):
                try:
                    response = requests.post(
                        f"http://127.0.0.1:8003/api/v1/chats/{chat_id}/send",
                        json={
                            "content": message_input,
                            "language": st.session_state.language
                        },
                        params={
                            "user_id": st.session_state.user_id,
                            "user_type": "USER"
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        st.success("✅ Message sent!")
                        st.rerun()
                    else:
                        st.error("Failed to send message")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please type a message")

# Chat Guidelines
with st.expander("📌 Chat Guidelines"):
    st.write("""
    - Be clear and concise in your messages
    - Provide relevant medical information
    - Don't share sensitive personal details
    - For emergencies, call 911 instead
    - Wait for doctor's response before sending another message
    """)

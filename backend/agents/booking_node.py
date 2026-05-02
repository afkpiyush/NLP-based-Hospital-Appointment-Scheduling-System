"""
Booking Agent Node
Handles appointment booking, rescheduling, and cancellation
"""
from langgraph.types import Command
from langchain_core.messages import AIMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.agents import create_agent, tool
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class BookingOutput(BaseModel):
    """Booking operation output"""
    success: bool
    message: str
    appointment_id: Optional[str] = None
    confirmation_details: Optional[str] = None


@tool
def book_appointment(
    user_id: str,
    doctor_id: str,
    appointment_date: str,
    reason_for_visit: str = ""
) -> str:
    """
    Book a new appointment for a user with a doctor
    """
    from ..database.crud import AppointmentCRUD, DoctorCRUD
    
    try:
        # Validate date format
        dt_obj = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
        
        # Create appointment
        appointment_data = {
            "user_id": user_id,
            "doctor_id": doctor_id,
            "appointment_date": dt_obj,
            "reason_for_visit": reason_for_visit,
            "status": "BOOKED"
        }
        
        appointment_id = AppointmentCRUD.create_appointment(appointment_data)
        
        # Update doctor availability
        DoctorCRUD.mark_slot_booked(
            doctor_id,
            str(dt_obj.date()),
            str(dt_obj.time()),
            user_id
        )
        
        return f"Successfully booked appointment (ID: {appointment_id}) for {appointment_date}"
    except Exception as e:
        return f"Error booking appointment: {str(e)}"


@tool
def cancel_appointment(appointment_id: str) -> str:
    """
    Cancel an existing appointment
    """
    from ..database.crud import AppointmentCRUD
    
    try:
        success = AppointmentCRUD.cancel_appointment(appointment_id)
        if success:
            return "Appointment cancelled successfully"
        return "Appointment not found or already cancelled"
    except Exception as e:
        return f"Error cancelling appointment: {str(e)}"


def booking_node(llm_model):
    """
    Booking Agent
    - Manages the appointment lifecycle
    - Interacts with database to store records
    - Confirms details with user
    """
    
    def node(state):
        system_prompt = """
        You are an appointment booking specialist for a healthcare platform.
        
        Your role is to:
        1. Process appointment booking requests
        2. Handle cancellations and rescheduling
        3. Confirm all details (doctor, date, time) before finalizing
        4. Provide clear confirmation messages
        
        Important Guidelines:
        - Always verify user_id and doctor_id are present
        - Ensure date/time is in a valid format (ISO 8601)
        - Be professional and helpful
        - If information is missing, ask the user clearly
        
        Tools Available:
        - book_appointment: Create new appointment record
        - cancel_appointment: Remove/cancel an existing appointment
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ])
        
        agent = create_agent(
            model=llm_model,
            tools=[book_appointment, cancel_appointment],
            prompt=prompt,
        )
        
        result = agent.invoke(state)
        
        final_message = result.get("messages", [])
        if final_message:
            last_message = final_message[-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            response_text = "Booking process completed."
            
        return Command(
            update={
                "messages": state["messages"] + [AIMessage(content=response_text)],
                "current_reasoning": "Booking operation processed"
            },
            goto="supervisor"
        )
    
    return node

from typing import Literal, Any, List, Optional, Dict
from typing_extensions import TypedDict, Annotated
from langgraph.graph.message import add_messages

class Router(TypedDict):
    next: Literal[
        "symptom_analysis",
        "medical_reasoning", 
        "specialist_recommendation",
        "location_availability",
        "booking_node",
        "chat_node",
        "information_node",
        "FINISH"
    ]
    reasoning: str

class AgentState(TypedDict):
    """Extended agent state with new fields for healthcare system"""
    
    # Core messaging
    messages: Annotated[list[Any], add_messages]
    
    # User identification
    id_number: int
    user_id: Optional[str]
    
    # Routing
    next: str
    query: str
    current_reasoning: str
    
    # Symptom analysis
    symptoms_extracted: Optional[List[str]]
    symptom_severity: Optional[Dict[str, str]]
    
    # Medical reasoning
    predicted_diseases: Optional[List[Dict[str, Any]]]
    needs_emergency: Optional[bool]
    
    # Specialist recommendation
    recommended_specialists: Optional[List[str]]
    primary_specialist: Optional[str]
    specialist_justifications: Optional[Dict[str, str]]
    
    # Location & availability
    user_latitude: Optional[float]
    user_longitude: Optional[float]
    available_doctors: Optional[List[Dict[str, Any]]]
    selected_doctor_id: Optional[str]
    selected_appointment_slot: Optional[Dict[str, str]]
    
    # Appointment
    appointment_id: Optional[str]
    appointment_date: Optional[str]
    
    # Chat
    chat_id: Optional[str]
    language_preference: Optional[str]
    
    # Tracking
    step_count: int
    max_steps: int
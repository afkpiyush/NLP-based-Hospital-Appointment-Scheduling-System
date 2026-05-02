"""
Location & Availability Agent Node
Finds doctors, checks availability, suggests appointment slots
"""
from langgraph.types import Command
from langchain_core.messages import AIMessage
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.agents import create_agent, tool
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime, timedelta
import math


class AvailableSlot(BaseModel):
    """Available appointment slot"""
    doctor_id: str
    doctor_name: str
    date: str
    time: str
    distance_km: float
    consultation_fee: float


class DoctorWithAvailability(BaseModel):
    """Doctor with availability information"""
    doctor_id: str
    name: str
    specialization: str
    experience_years: int
    rating: float
    distance_km: float
    consultation_fee: float
    available_slots: List[AvailableSlot]


class LocationAvailabilityOutput(BaseModel):
    """Location availability output"""
    doctors_found: List[DoctorWithAvailability]
    nearest_doctor: str = Field(..., description="Nearest doctor with availability")
    recommended_slots: List[AvailableSlot] = Field(..., description="Top recommended time slots")


# Tools for location and availability
@tool
def find_nearby_doctors(
    specialization: str,
    latitude: float,
    longitude: float,
    max_distance_km: float = 50
) -> str:
    """
    Find doctors by specialization near given location
    Returns JSON string with doctor information
    """
    from ..database.crud import DoctorCRUD
    
    try:
        doctors = DoctorCRUD.search_doctors_by_specialization(
            specialization, latitude, longitude, max_distance_km
        )
        
        # Calculate distances
        results = []
        for doc in doctors:
            if "clinic_location" in doc:
                doc_lat = doc["clinic_location"].get("latitude", 0)
                doc_lon = doc["clinic_location"].get("longitude", 0)
                distance = _calculate_distance(latitude, longitude, doc_lat, doc_lon)
                
                results.append({
                    "doctor_id": doc.get("doctor_id"),
                    "name": doc.get("name"),
                    "specialization": doc.get("specialization"),
                    "experience": doc.get("experience_years"),
                    "rating": doc.get("rating"),
                    "distance_km": round(distance, 2),
                    "consultation_fee": doc.get("consultation_fee"),
                    "languages": doc.get("languages_spoken", ["EN"])
                })
        
        return str(results[:10])  # Top 10 nearby doctors
    except Exception as e:
        return f"Error finding doctors: {str(e)}"


@tool
def check_doctor_availability(doctor_id: str, date: str = None) -> str:
    """
    Check available time slots for a doctor
    If date not specified, checks next 7 days
    Returns JSON string with available slots
    """
    from ..database.crud import DoctorCRUD
    
    try:
        doctor = DoctorCRUD.get_doctor(doctor_id)
        if not doctor:
            return "Doctor not found"
        
        available_slots = []
        if "availability_slots" in doctor:
            for slot in doctor["availability_slots"]:
                if slot.get("is_available"):
                    available_slots.append({
                        "date": slot.get("date"),
                        "start_time": slot.get("start_time"),
                        "end_time": slot.get("end_time")
                    })
        
        return str(available_slots)
    except Exception as e:
        return f"Error checking availability: {str(e)}"


@tool
def suggest_best_slots(
    available_slots: List[Dict],
    user_preference: str = "morning"
) -> str:
    """
    AI-based slot suggestion based on user preference
    Preferences: morning (6-12), afternoon (12-18), evening (18-23)
    Returns top 3 recommended slots
    """
    try:
        preference_map = {
            "morning": (6, 12),
            "afternoon": (12, 18),
            "evening": (18, 23)
        }
        
        time_range = preference_map.get(user_preference, (6, 23))
        preferred_slots = []
        
        for slot in available_slots:
            if slot.get("start_time"):
                hour = int(slot["start_time"].split(":")[0])
                if time_range[0] <= hour < time_range[1]:
                    preferred_slots.append(slot)
        
        # Sort by date and time
        preferred_slots.sort(key=lambda x: (x.get("date"), x.get("start_time")))
        
        return str(preferred_slots[:3])
    except Exception as e:
        return f"Error suggesting slots: {str(e)}"


def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def location_availability_node(llm_model):
    """
    Location & Availability Agent
    - Finds doctors based on specialization and location
    - Checks availability
    - Suggests best time slots
    - Returns sortable doctor list
    """
    
    def node(state):
        system_prompt = """
        You are a doctor finder and appointment scheduling assistant.
        
        Your role is to:
        1. Find nearby doctors based on specialization and location
        2. Check their availability
        3. Suggest best appointment slots based on user preference
        4. Present options in a clear, actionable format
        
        Guidelines:
        - Prioritize doctors with higher ratings
        - Consider distance and travel time
        - Suggest slots that are soonest available
        - Include consultation fees in recommendations
        - Be transparent about qualifications and experience
        
        Tools Available:
        - find_nearby_doctors: Find doctors by specialization near location
        - check_doctor_availability: Check specific doctor's availability
        - suggest_best_slots: Get AI-recommended time slots
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{messages}"),
        ])
        
        # Create agent with tools
        agent = create_agent(
            model=llm_model,
            tools=[
                find_nearby_doctors,
                check_doctor_availability,
                suggest_best_slots
            ],
            prompt=prompt,
        )
        
        result = agent.invoke(state)
        
        # Process result
        final_message = result.get("messages", [])
        if final_message:
            last_message = final_message[-1]
            response_text = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            response_text = "No doctors found in your area. Please try a different search."
        
        # Add booking option
        response_text += """

🔍 DOCTOR FINDER RESULTS

To proceed with booking:
1. Click on your preferred doctor
2. Select desired appointment slot
3. Confirm appointment

Or type 'book' to confirm selection.
        """
        
        # Log interaction
        from backend.database.crud import InteractionLogCRUD
        try:
            InteractionLogCRUD.log_interaction({
                "user_id": state.get("user_id", "unknown"),
                "interaction_type": "LOCATION_AVAILABILITY"
            })
        except:
            pass
        
        return Command(
            update={
                "messages": state["messages"] + [AIMessage(content=response_text)],
                "current_reasoning": "Location & Availability search completed"
            },
            goto="supervisor"
        )
    
    return node

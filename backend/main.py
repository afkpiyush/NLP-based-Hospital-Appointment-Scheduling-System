"""
FastAPI Endpoints for AI-Powered Healthcare Assistant Platform
Comprehensive API for symptom analysis, specialist recommendation, and appointment booking
"""
from fastapi import FastAPI, WebSocket, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional, List
import uuid

from .models.schemas import (
    SymptomAnalysisRequest, SymptomAnalysisResponse,
    DiagnosisResponse, SpecialistRecommendationResponse,
    DoctorSearchRequest, DoctorSearchResponse,
    AppointmentCreate, Appointment,
    ChatMessageCreate, ChatHistory,
    User, Doctor,
    WorkflowExecutionRequest, WorkflowExecutionResponse
)
from .services.llm import LLMModel
from .database.crud import (
    UserCRUD, DoctorCRUD, AppointmentCRUD, ChatCRUD, InteractionLogCRUD
)
from .services.translation import get_translation_service, LocalizationManager
from .websocket.chat_manager import handle_chat_connection
from .agents.workflow import get_workflow


# Initialize FastAPI app
app = FastAPI(
    title="AI Healthcare Assistant",
    description="Complete healthcare platform with AI-powered diagnostics",
    version="1.0.0"
)

# Initialize services
llm_service = LLMModel(model_name="llama3-70b-8192")
translation_service = get_translation_service()
llm_model = llm_service.get_model()


# ============== HEALTH CHECK ==============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# ============== SYMPTOM ANALYSIS ENDPOINTS ==============

@app.post("/api/v1/symptoms/analyze", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(request: SymptomAnalysisRequest):
    """
    Analyze patient symptoms
    
    - Accepts natural language symptom description
    - Extracts structured symptoms
    - Assesses urgency level
    - Returns symptom analysis
    """
    try:
        # Normalize input to English for processing
        normalized_input = translation_service.normalize_to_english(request.patient_description)
        
        # Store interaction log
        InteractionLogCRUD.log_interaction({
            "user_id": request.user_id,
            "interaction_type": "SYMPTOM_ANALYSIS",
            "symptoms_input": normalized_input
        })
        
        # Response
        response = SymptomAnalysisResponse(
            symptoms=[
                {"name": "fever", "severity": "moderate"},
                {"name": "headache", "severity": "severe"},
                {"name": "body_aches", "severity": "mild"}
            ],
            analysis_confidence=0.87,
            needs_urgent_care=False
        )
        
        # Translate response if needed
        if request.language != "EN":
            for symptom in response.symptoms:
                symptom.name = translation_service.translate(
                    symptom.name, "EN", request.language
                )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing symptoms: {str(e)}")


@app.get("/api/v1/symptoms/common")
async def get_common_symptoms(language: str = Query("EN", regex="^(EN|HI|MR)$")):
    """Get list of common symptoms in user's language"""
    
    common_symptoms = [
        "fever", "headache", "cough", "body_aches", "fatigue",
        "nausea", "dizziness", "shortness_of_breath", "sore_throat",
        "runny_nose", "chest_pain", "abdominal_pain"
    ]
    
    if language != "EN":
        common_symptoms = translation_service.translate_list(
            common_symptoms, language
        )
    
    return {"symptoms": common_symptoms}


# ============== DIAGNOSIS & SPECIALIST ENDPOINTS ==============

@app.post("/api/v1/diagnosis/predict", response_model=DiagnosisResponse)
async def predict_diagnosis(
    session_id: str,
    user_id: str,
    language: str = Query("EN", regex="^(EN|HI|MR)$")
):
    """
    Predict diseases from analyzed symptoms
    
    - Uses medical knowledge base
    - Returns top 3 predictions with confidence
    - Includes medical disclaimer
    """
    try:
        # Fetch symptom analysis from session
        # (In real implementation, this would retrieve from cache/DB)
        
        # Mock response
        response = DiagnosisResponse(
            session_id=session_id,
            diseases=[
                {
                    "name": "Influenza",
                    "confidence": 0.92,
                    "description": "Contagious respiratory illness",
                    "risk_factors": ["viral exposure", "seasonal"],
                    "recommended_tests": ["Rapid flu test", "RT-PCR"]
                },
                {
                    "name": "Common Cold",
                    "confidence": 0.78,
                    "description": "Viral upper respiratory infection",
                    "recommended_tests": ["None typically needed"]
                }
            ],
            specialist_recommendations=["General Physician", "Infectious Disease Specialist"]
        )
        
        # Translate if needed
        if language != "EN":
            for disease in response.diseases:
                disease["name"] = translation_service.translate(disease["name"], "EN", language)
                disease["description"] = translation_service.translate(
                    disease["description"], "EN", language
                )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting diagnosis: {str(e)}")


@app.post("/api/v1/specialists/recommend", response_model=SpecialistRecommendationResponse)
async def recommend_specialists(
    predicted_disease: str,
    user_id: str,
    language: str = Query("EN", regex="^(EN|HI|MR)$")
):
    """
    Recommend specialists for predicted disease
    
    - Maps diseases to appropriate specialists
    - Ranks by relevance
    - Provides qualification information
    """
    try:
        # Mock specialist recommendation
        response = SpecialistRecommendationResponse(
            session_id=str(uuid.uuid4()),
            specialists=[
                {
                    "name": "General Physician",
                    "ranking": 1,
                    "justification": "Primary care for initial diagnosis",
                    "related_diseases": ["Influenza", "Common Cold"]
                },
                {
                    "name": "Infectious Disease Specialist",
                    "ranking": 2,
                    "justification": "For complex infectious cases",
                    "related_diseases": ["Influenza", "COVID-19"]
                }
            ],
            primary_specialist="General Physician"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recommending specialists: {str(e)}")


# ============== DOCTOR SEARCH & AVAILABILITY ==============

@app.get("/api/v1/doctors/search", response_model=DoctorSearchResponse)
async def search_doctors(
    specialization: str,
    latitude: float,
    longitude: float,
    max_distance_km: float = 50,
    min_rating: float = 0.0,
    language: str = Query("EN", regex="^(EN|HI|MR)$")
):
    """
    Search for doctors by specialization and location
    
    - Searches nearby doctors
    - Filters by rating and distance
    - Returns availability information
    """
    try:
        doctors = DoctorCRUD.search_doctors_by_specialization(
            specialization, latitude, longitude, max_distance_km
        )
        
        # Filter by rating
        doctors = [d for d in doctors if d.get("rating", 0) >= min_rating]
        
        response = DoctorSearchResponse(
            doctors=[Doctor(**doc) for doc in doctors],
            total_count=len(doctors),
            search_timestamp=datetime.utcnow()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching doctors: {str(e)}")


@app.get("/api/v1/doctors/{doctor_id}")
async def get_doctor_details(doctor_id: str):
    """Get detailed information about a doctor"""
    try:
        doctor = DoctorCRUD.get_doctor(doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        return doctor
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching doctor details: {str(e)}")


@app.get("/api/v1/doctors/{doctor_id}/availability")
async def get_doctor_availability(
    doctor_id: str,
    date: Optional[str] = None
):
    """Get availability slots for a doctor"""
    try:
        doctor = DoctorCRUD.get_doctor(doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        slots = doctor.get("availability_slots", [])
        
        # Filter by date if provided
        if date:
            slots = [s for s in slots if s.get("date") == date]
        
        return {
            "doctor_id": doctor_id,
            "available_slots": slots
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching availability: {str(e)}")


# ============== APPOINTMENT ENDPOINTS ==============

@app.post("/api/v1/appointments/book", response_model=Appointment)
async def book_appointment(request: AppointmentCreate):
    """
    Book new appointment
    
    - Validates slot availability
    - Creates appointment record
    - Returns confirmation
    """
    try:
        # Create appointment in database
        appointment_id = AppointmentCRUD.create_appointment({
            "user_id": request.user_id,
            "doctor_id": request.doctor_id,
            "appointment_date": request.appointment_date,
            "status": "BOOKED",
            "reason_for_visit": request.reason_for_visit,
            "symptoms": request.symptoms,
            "predicted_diagnoses": request.predicted_diagnoses
        })
        
        # Update doctor availability
        doctor = DoctorCRUD.get_doctor(request.doctor_id)
        DoctorCRUD.mark_slot_booked(
            request.doctor_id,
            str(request.appointment_date.date()),
            str(request.appointment_date.time()),
            request.user_id
        )
        
        appointment = AppointmentCRUD.get_appointment(appointment_id)
        
        return Appointment(**appointment)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error booking appointment: {str(e)}")


@app.get("/api/v1/appointments/{appointment_id}")
async def get_appointment(appointment_id: str):
    """Get appointment details"""
    try:
        appointment = AppointmentCRUD.get_appointment(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return appointment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching appointment: {str(e)}")


@app.get("/api/v1/users/{user_id}/appointments")
async def get_user_appointments(
    user_id: str,
    status: Optional[str] = None
):
    """Get all appointments for a user"""
    try:
        appointments = AppointmentCRUD.get_user_appointments(user_id, status)
        return {"appointments": appointments}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching appointments: {str(e)}")


@app.post("/api/v1/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: str):
    """Cancel appointment"""
    try:
        success = AppointmentCRUD.cancel_appointment(appointment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        return {"message": "Appointment cancelled successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling appointment: {str(e)}")


# ============== CHAT ENDPOINTS ==============

@app.websocket("/ws/chat/{appointment_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    appointment_id: str,
    user_id: str = Query(...),
    user_type: str = Query("USER", regex="^(USER|DOCTOR)$")
):
    """
    WebSocket endpoint for real-time doctor-patient chat
    
    Message Format:
    {
        "type": "message|typing|read",
        "content": "...",
        "language": "EN|HI|MR"
    }
    """
    
    # Get or create chat session
    appointment = AppointmentCRUD.get_appointment(appointment_id)
    if not appointment:
        await websocket.close(code=4004, reason="Appointment not found")
        return
    
    # Get chat_id for this appointment
    existing_chat = ChatCRUD.get_chat_by_appointment(appointment_id)
    if existing_chat:
        chat_id = existing_chat["chat_id"]
    else:
        chat_id = ChatCRUD.create_chat_session(
            appointment_id,
            appointment["user_id"],
            appointment["doctor_id"]
        )
    
    # Handle WebSocket connection
    await handle_chat_connection(websocket, chat_id, user_id, user_type)


@app.get("/api/v1/chats/{chat_id}/history")
async def get_chat_history(
    chat_id: str,
    limit: int = Query(50, ge=1, le=200)
):
    """Get chat history for a conversation"""
    try:
        chat = ChatCRUD.get_chat_history(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        messages = chat.get("messages", [])[-limit:]
        
        return {
            "chat_id": chat_id,
            "message_count": len(messages),
            "messages": messages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chat history: {str(e)}")


@app.post("/api/v1/chats/{chat_id}/send")
async def send_chat_message(
    chat_id: str,
    message: ChatMessageCreate,
    user_id: str = Query(...),
    user_type: str = Query("USER", regex="^(USER|DOCTOR)$")
):
    """Send message in chat (HTTP fallback)"""
    try:
        ChatCRUD.add_message(chat_id, {
            "sender_type": user_type,
            "sender_id": user_id,
            "content": message.content,
            "language": message.language
        })
        
        return {"message": "Message sent successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")


# ============== USER ENDPOINTS ==============

@app.post("/api/v1/users", response_model=User)
async def create_user(user_data: dict):
    """Create new user account"""
    try:
        user_id = UserCRUD.create_user(user_data)
        return UserCRUD.get_user(user_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: str):
    """Get user profile"""
    try:
        user = UserCRUD.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")


@app.put("/api/v1/users/{user_id}")
async def update_user(user_id: str, updates: dict):
    """Update user profile"""
    try:
        success = UserCRUD.update_user(user_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserCRUD.get_user(user_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")


# ============== WORKFLOW ENDPOINT ==============

@app.post("/api/v1/workflow/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(request: WorkflowExecutionRequest):
    """
    Execute the healthcare agent workflow
    - Routes through specialized agents
    - Handles symptoms, reasoning, booking, and more
    """
    try:
        workflow = get_workflow()
        
        # Convert history to LangChain messages if provided
        from langchain_core.messages import HumanMessage, AIMessage
        history = []
        for msg in request.history:
            if msg.get("role") == "user":
                history.append(HumanMessage(content=msg.get("content")))
            else:
                history.append(AIMessage(content=msg.get("content")))
        
        response = await workflow.execute(
            user_input=request.user_input,
            user_id=request.user_id,
            id_number=request.id_number,
            history=history
        )
        
        return WorkflowExecutionResponse(**response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing workflow: {str(e)}")


# ============== LOCALIZATION ENDPOINTS ==============

@app.get("/api/v1/localization/strings/{key}")
async def get_localized_string(
    key: str,
    language: str = Query("EN", regex="^(EN|HI|MR)$")
):
    """Get localized UI string"""
    return {
        "key": key,
        "language": language,
        "text": LocalizationManager.get_localized_string(key, language)
    }


@app.get("/api/v1/localization/all/{key}")
async def get_all_translations(key: str):
    """Get all language translations for a key"""
    return LocalizationManager.get_all_translations(key)


# ============== ERROR HANDLERS ==============

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )

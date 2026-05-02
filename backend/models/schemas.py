"""
Pydantic models for API request/response validation
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, field_validator
import uuid


# ============== USER MODELS ==============

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(..., pattern="^(M|F|Other)$")
    language_preference: str = Field(default="EN", pattern="^(EN|HI|MR)$")


class UserLocation(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    city: str
    state: str


class UserCreate(UserBase):
    location: UserLocation
    medical_history: Optional[List[str]] = []
    allergies: Optional[List[str]] = []


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    language_preference: Optional[str] = Field(None, pattern="^(EN|HI|MR)$")
    location: Optional[UserLocation] = None
    medical_history: Optional[List[str]] = None
    allergies: Optional[List[str]] = None


class User(UserBase):
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    location: UserLocation
    medical_history: List[str]
    allergies: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True


# ============== DOCTOR MODELS ==============

class ClinicLocation(BaseModel):
    latitude: float
    longitude: float
    address: str
    city: str


class TimeSlot(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end_time: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    is_available: bool = True
    booked_by: Optional[str] = None


class DoctorBase(BaseModel):
    name: str
    specialization: str
    qualifications: List[str]
    experience_years: int = Field(..., ge=0, le=70)
    consultation_fee: float = Field(..., gt=0)
    languages_spoken: List[str] = ["EN"]


class DoctorCreate(DoctorBase):
    clinic_location: ClinicLocation
    availability_slots: Optional[List[TimeSlot]] = []


class Doctor(DoctorBase):
    doctor_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    clinic_location: ClinicLocation
    rating: float = Field(default=0.0, ge=0, le=5)
    availability_slots: List[TimeSlot]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


# ============== SYMPTOM & DIAGNOSIS MODELS ==============

class Symptom(BaseModel):
    name: str
    severity: str = Field(..., pattern="^(mild|moderate|severe)$")
    duration_days: Optional[int] = None
    description: Optional[str] = None


class Disease(BaseModel):
    name: str
    confidence: float = Field(..., ge=0, le=1)
    description: str
    risk_factors: Optional[List[str]] = []


class SymptomAnalysisRequest(BaseModel):
    patient_description: str
    language: str = Field(default="EN", pattern="^(EN|HI|MR)$")
    user_id: str


class SymptomAnalysisResponse(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symptoms: List[Symptom]
    analysis_confidence: float
    needs_urgent_care: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DiagnosisResponse(BaseModel):
    session_id: str
    diseases: List[Disease]
    specialist_recommendations: List[str]
    disclaimer: str = "This is an AI-generated analysis and NOT a medical diagnosis. Please consult with a qualified healthcare professional."
    severity_alert: Optional[str] = None


# ============== SPECIALIST MODELS ==============

class SpecialistRecommendation(BaseModel):
    name: str
    ranking: int
    justification: str
    related_diseases: List[str]


class SpecialistRecommendationResponse(BaseModel):
    session_id: str
    specialists: List[SpecialistRecommendation]
    primary_specialist: str


# ============== APPOINTMENT MODELS ==============

class AppointmentCreate(BaseModel):
    user_id: str
    doctor_id: str
    appointment_date: datetime
    reason_for_visit: str
    symptoms: Optional[List[str]] = []
    predicted_diagnoses: Optional[List[Dict[str, Any]]] = []


class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    reason_for_visit: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(BOOKED|COMPLETED|CANCELLED|NO_SHOW)$")
    doctor_notes: Optional[str] = None


class Appointment(BaseModel):
    appointment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    doctor_id: str
    appointment_date: datetime
    status: str = "BOOKED"
    reason_for_visit: str
    symptoms: List[str] = []
    predicted_diagnoses: List[Disease] = []
    doctor_notes: Optional[str] = None
    prescription: Optional[str] = None
    consultation_fee: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============== CHAT MODELS ==============

class ChatMessage(BaseModel):
    sender_type: str = Field(..., pattern="^(USER|DOCTOR)$")
    sender_id: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    is_moderated: bool = False
    language: str = "EN"


class ChatMessageCreate(BaseModel):
    content: str
    language: str = Field(default="EN", pattern="^(EN|HI|MR)$")


class ChatHistory(BaseModel):
    chat_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    appointment_id: str
    user_id: str
    doctor_id: str
    messages: List[ChatMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        from_attributes = True


# ============== MEDICAL INTERACTION LOG MODELS ==============

class MedicalInteractionLog(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    interaction_type: str = Field(..., pattern="^(SYMPTOM_ANALYSIS|DIAGNOSIS|BOOKING|CHAT)$")
    symptoms_input: Optional[str] = None
    diseases_predicted: List[str] = []
    specialist_recommended: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


# ============== API RESPONSE MODELS ==============

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== SEARCH & FILTER MODELS ==============

class DoctorSearchRequest(BaseModel):
    specialization: str
    latitude: float
    longitude: float
    max_distance_km: float = 50.0
    min_rating: float = Field(default=0.0, ge=0, le=5)
    sort_by: str = Field(default="distance", pattern="^(distance|rating|fee)$")


class DoctorSearchResponse(BaseModel):
    doctors: List[Doctor]
    total_count: int
    search_timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============== VALIDATORS ==============

class DateValidator:
    @staticmethod
    def validate_appointment_date(date: datetime) -> bool:
        """Ensure appointment is in future"""
        return date > datetime.utcnow()
    
    @staticmethod
    def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> bool:
        """Validate date string format"""
        try:
            datetime.strptime(date_str, format)
            return True
        except ValueError:
# ============== WORKFLOW MODELS ==============

class WorkflowExecutionRequest(BaseModel):
    user_input: str
    user_id: str
    id_number: int = 0
    history: Optional[List[Dict[str, str]]] = []

class WorkflowExecutionResponse(BaseModel):
    messages: List[Dict[str, str]]
    current_reasoning: str
    next_node: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# AI-Powered Healthcare Assistant Platform - Complete Architecture

## System Overview

An intelligent healthcare platform that uses multi-agent LLM architecture to:
1. Analyze patient symptoms → predict diseases → recommend specialists
2. Find available doctors → automatically suggest appointments
3. Support multilingual conversations (English, Hindi, Marathi)
4. Enable real-time doctor-patient chat post-appointment
5. Maintain persistent data in database (MongoDB/PostgreSQL)

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  Streamlit UI Components:                                        │
│  ├─ Home Page                                                   │
│  ├─ Symptom Input (text/voice)                                  │
│  ├─ Diagnosis & Recommendation Display                          │
│  ├─ Doctor Search & Booking                                     │
│  ├─ Chat Interface (WebSocket)                                  │
│  └─ Multilingual Toggle (EN/HI/MR)                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FastAPI)                        │
├─────────────────────────────────────────────────────────────────┤
│  REST Endpoints:                                                 │
│  ├─ POST /api/v1/symptoms/analyze                               │
│  ├─ POST /api/v1/specialists/recommend                          │
│  ├─ GET /api/v1/doctors/search                                  │
│  ├─ POST /api/v1/appointments/book                              │
│  ├─ GET /api/v1/appointments/{id}                               │
│  └─ WebSocket /ws/chat/{appointment_id}                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              TRANSLATION LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│  ├─ Language Detection                                           │
│  ├─ Text Translation (Input Normalization)                       │
│  └─ Output Localization (EN/HI/MR)                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           MULTI-AGENT ORCHESTRATION (LangGraph)                 │
├─────────────────────────────────────────────────────────────────┤
│  Supervisor Agent                                                │
│  ├─ Symptom Analysis Agent                                       │
│  ├─ Medical Reasoning Agent                                      │
│  ├─ Specialist Recommendation Agent                              │
│  ├─ Location & Availability Agent                                │
│  ├─ Booking Agent (Extended)                                     │
│  ├─ Information Node (Existing)                                  │
│  ├─ Booking Node (Existing)                                      │
│  └─ Chat Conversation Agent                                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              TOOLS & EXTERNAL SERVICES                          │
├─────────────────────────────────────────────────────────────────┤
│  ├─ Medical Knowledge Base (Vector DB / Chroma)                 │
│  ├─ Location Service (Google Maps API)                          │
│  ├─ LLM Service (GROQ / OpenAI)                                 │
│  ├─ Translation Service (Google Translate)                      │
│  └─ Chat Message Queue (Redis)                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  DATA PERSISTENCE LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  Primary Database (PostgreSQL or MongoDB):                       │
│  ├─ Users Collection                                             │
│  ├─ Doctors Collection                                           │
│  ├─ Appointments Collection                                      │
│  ├─ Chat History Collection                                      │
│  ├─ Medical Interactions Log                                     │
│  └─ Doctor Availability Slots                                    │
│                                                                   │
│  Cache Layer (Redis):                                            │
│  ├─ Session Management                                           │
│  ├─ Chat Message Queue                                           │
│  └─ Query Results Cache                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Design & Responsibilities

### 1. **Supervisor Agent** (Main Orchestrator)
- **Role**: Analyze user intent, route to appropriate agents
- **Input**: User query, language, user context
- **Output**: Routing decision + reasoning
- **Routing Options**:
  - `symptom_analysis` → If user describes symptoms
  - `specialist_recommendation` → If user asks for doctor recommendation
  - `location_availability` → If user wants to find doctors
  - `booking` → If user wants to book appointment
  - `chat` → If user continues conversation
  - `FINISH` → If query resolved

### 2. **Symptom Analysis Agent**
- **Role**: Extract symptoms from natural language
- **Tools**:
  - `extract_symptoms()` → Parse free text, identify symptoms
  - `validate_symptoms()` → Verify against medical ontology
  - `get_symptom_severity()` → Rate symptom severity (mild/moderate/severe)
- **Output**: Structured symptom list with severity

### 3. **Medical Reasoning Agent**
- **Role**: AI diagnosis using symptom → disease mapping
- **Tools**:
  - `predict_diseases()` → LLM + medical KB (top 3 with confidence)
  - `get_disease_info()` → Return disease details, symptoms, risk factors
  - `flag_critical()` → Alert if critical condition detected
- **Output**: List of possible diseases with confidence scores + disclaimer

### 4. **Specialist Recommendation Agent**
- **Role**: Map diseases → appropriate medical specialists
- **Tools**:
  - `map_disease_to_specialist()` → Disease → Specialist mapping
  - `get_specialist_info()` → Details about specialist qualifications
  - `rank_specialists()` → Priority ranking
- **Output**: Recommended specialists with reasoning

### 5. **Location & Availability Agent**
- **Role**: Find doctors, check availability, suggest time slots
- **Tools**:
  - `find_doctors_by_specialization()` → Location-based search
  - `check_doctor_availability()` → Get available time slots
  - `suggest_best_slots()` → ML-based slot recommendation
  - `get_travel_time()` → Distance to doctor clinic
- **Output**: List of doctors with available slots + recommendations

### 6. **Booking Agent** (Extended)
- **Role**: Execute appointment bookings, manage rescheduling/cancellation
- **Tools**:
  - `create_appointment()` (New)
  - `reschedule_appointment()` (Fixed + Enhanced)
  - `cancel_appointment()` (Existing)
  - `send_confirmation()` (New)
- **Output**: Booking confirmation, appointment details

### 7. **Chat Conversation Agent** (New)
- **Role**: Manage post-appointment doctor-patient messaging
- **Tools**:
  - `store_message()` → Persist chat in DB
  - `get_chat_history()` → Retrieve past messages
  - `moderate_content()` → Basic content moderation
  - `send_notification()` → Alert users of new messages
- **Output**: Message confirmation, chat history

### 8. **Information Node** (Existing - Enhanced)
- **Role**: General queries, FAQ, appointment information
- **Output**: Relevant information

---

## Data Models & Database Schema

### **Users Collection**
```python
{
    "_id": ObjectId,
    "user_id": str (UUID),
    "name": str,
    "email": str (unique),
    "phone": str,
    "age": int,
    "gender": str (M/F/Other),
    "language_preference": str (EN/HI/MR),
    "location": {
        "latitude": float,
        "longitude": float,
        "city": str,
        "state": str
    },
    "medical_history": [str],  # Past conditions
    "allergies": [str],
    "created_at": datetime,
    "last_login": datetime,
    "is_active": bool
}
```

### **Doctors Collection**
```python
{
    "_id": ObjectId,
    "doctor_id": str (UUID),
    "name": str,
    "specialization": str,
    "qualifications": [str],
    "experience_years": int,
    "clinic_location": {
        "latitude": float,
        "longitude": float,
        "address": str,
        "city": str
    },
    "rating": float (1-5),
    "consultation_fee": float,
    "languages_spoken": [str],
    "availability_slots": [
        {
            "date": date,
            "start_time": time,
            "end_time": time,
            "is_available": bool
        }
    ],
    "created_at": datetime
}
```

### **Appointments Collection**
```python
{
    "_id": ObjectId,
    "appointment_id": str (UUID),
    "user_id": str,
    "doctor_id": str,
    "appointment_date": datetime,
    "status": str (BOOKED/COMPLETED/CANCELLED/NO_SHOW),
    "reason_for_visit": str,
    "symptoms": [str],
    "predicted_diagnoses": [
        {
            "disease": str,
            "confidence": float
        }
    ],
    "doctor_notes": str,
    "prescription": str,
    "consultation_fee": float,
    "created_at": datetime,
    "completed_at": datetime,
    "cancelled_at": datetime
}
```

### **Chat History Collection**
```python
{
    "_id": ObjectId,
    "chat_id": str (UUID),
    "appointment_id": str,
    "user_id": str,
    "doctor_id": str,
    "messages": [
        {
            "sender_type": str (USER/DOCTOR),
            "sender_id": str,
            "content": str,
            "timestamp": datetime,
            "is_moderated": bool,
            "language": str
        }
    ],
    "created_at": datetime,
    "last_message_at": datetime,
    "is_active": bool
}
```

### **Medical Interactions Log Collection**
```python
{
    "_id": ObjectId,
    "log_id": str (UUID),
    "user_id": str,
    "interaction_type": str (SYMPTOM_ANALYSIS/DIAGNOSIS/BOOKING/CHAT),
    "symptoms_input": str,
    "diseases_predicted": [str],
    "specialist_recommended": str,
    "feedback": str,
    "created_at": datetime
}
```

### **Doctor Availability Slots Collection** (Alternative to CSV)
```python
{
    "_id": ObjectId,
    "doctor_id": str,
    "date": date,
    "time_slots": [
        {
            "start_time": time,
            "end_time": time,
            "is_available": bool,
            "booked_by": str (user_id or null)
        }
    ],
    "last_updated": datetime
}
```

---

## Folder Structure

```
doctor-healthcare-assistant/
│
├── main.py                              # Entry point
├── ARCHITECTURE.md                      # This file
├── requirements.txt                     # Dependencies
├── .env.example                         # Environment config template
│
├── frontend/
│   ├── streamlit_main.py               # Main Streamlit app
│   ├── pages/
│   │   ├── 1_home.py
│   │   ├── 2_symptom_checker.py
│   │   ├── 3_doctor_finder.py
│   │   ├── 4_appointments.py
│   │   ├── 5_chat.py
│   │   └── 6_settings.py
│   └── components/
│       ├── symptom_input.py
│       ├── diagnosis_display.py
│       ├── booking_form.py
│       ├── chat_interface.py
│       └── language_selector.py
│
├── backend/
│   ├── main.py                         # FastAPI app initialization
│   ├── config.py                       # Configuration
│   ├── requirements.txt
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── symptoms.py            # Symptom analysis endpoints
│   │   │   ├── specialists.py         # Specialist recommendation
│   │   │   ├── doctors.py             # Doctor search & availability
│   │   │   ├── appointments.py        # Appointment CRUD
│   │   │   ├── chat.py                # Chat endpoints
│   │   │   └── health.py              # Health check endpoint
│   │   └── dependencies.py            # Shared dependencies
│   │
│   ├── agents/                         # Multi-agent system (existing + new)
│   │   ├── __init__.py
│   │   ├── state.py                   # Extended state definitions
│   │   ├── supervisor.py              # Supervisor agent
│   │   ├── symptom_analysis_node.py   # New
│   │   ├── medical_reasoning_node.py  # New
│   │   ├── specialist_recommendation_node.py  # New
│   │   ├── location_availability_node.py     # New
│   │   ├── booking_node.py            # Extended
│   │   ├── chat_node.py               # New
│   │   ├── information_node.py        # Existing
│   │   ├── builder.py                 # Graph builder
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── symptom_tools.py       # New
│   │       ├── medical_tools.py       # New
│   │       ├── specialist_tools.py    # New
│   │       ├── location_tools.py      # New
│   │       ├── booking_tools.py       # Extended
│   │       ├── chat_tools.py          # New
│   │       └── availability_tools.py  # Existing
│   │
│   ├── models/                         # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py                    # Extended with new fields
│   │   ├── doctor.py                  # New
│   │   ├── appointment.py             # New/Extended
│   │   ├── chat.py                    # New
│   │   ├── symptom.py                 # New
│   │   └── diagnosis.py               # New
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py              # MongoDB/PostgreSQL connection
│   │   ├── models.py                  # ORM models (if using SQLAlchemy)
│   │   └── crud.py                    # CRUD operations
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm.py                     # LLM service (existing, enhanced)
│   │   ├── translation.py             # Multilingual translation
│   │   ├── location.py                # Location/Maps service
│   │   ├── email.py                   # Email notifications
│   │   ├── chat.py                    # Chat management
│   │   ├── medical_kb.py              # Medical knowledge base
│   │   └── cache.py                   # Redis cache
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py              # Data validation
│   │   ├── logger.py                  # Logging setup
│   │   ├── constants.py               # Constants
│   │   └── helpers.py                 # Helper functions
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py                    # Authentication
│   │
│   └── websocket/
│       ├── __init__.py
│       ├── chat_manager.py            # WebSocket chat management
│       └── connection_handler.py      # Connection handling
│
├── data/
│   ├── doctor_availability.csv        # Existing
│   ├── medical_knowledge_base.json    # New - disease/specialist mapping
│   ├── symptom_mappings.json          # New - symptom → disease
│   └── doctor_profiles.csv            # New - extended doctor data
│
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_api.py
│   ├── test_services.py
│   └── test_chat.py
│
└── docker/
    ├── Dockerfile
    ├── docker-compose.yml
    └── .dockerignore
```

---

## Execution Flow - Complete User Journey

### **Scenario: Patient with Symptoms**

```
1. USER INPUT (Streamlit UI)
   └─> Language: English
   └─> Symptom Input: "I have severe headache, fever, and body aches"

2. TRANSLATION LAYER
   └─> Detect language: English
   └─> (No translation needed)

3. SUPERVISOR AGENT
   └─> Analyze intent: "SYMPTOM_ANALYSIS"
   └─> Route to: Symptom Analysis Agent

4. SYMPTOM ANALYSIS AGENT
   └─> Extract: ["headache", "fever", "body_aches"]
   └─> Severity: ["severe", "moderate", "moderate"]
   └─> Return to Supervisor

5. SUPERVISOR (Routing Again)
   └─> Intent: "MEDICAL_REASONING"
   └─> Route to: Medical Reasoning Agent

6. MEDICAL REASONING AGENT
   └─> Using LLM + Medical KB:
   │   ├─ Disease 1: Influenza (92% confidence)
   │   ├─ Disease 2: COVID-19 (85% confidence)
   │   └─ Disease 3: Viral Fever (78% confidence)
   └─> ⚠️ Add Disclaimer
   └─> Return to Supervisor

7. SUPERVISOR (Routing Again)
   └─> Intent: "SPECIALIST_RECOMMENDATION"
   └─> Route to: Specialist Recommendation Agent

8. SPECIALIST RECOMMENDATION AGENT
   └─> Map diseases to specialists:
   │   ├─ Primary: General Physician / Internist
   │   ├─ Secondary: Infectious Disease Specialist
   │   └─ Tertiary: Emergency Medicine
   └─> Return to Supervisor

9. SUPERVISOR (Routing Again)
   └─> Intent: "AUTO_SUGGEST_BOOKING"
   └─> Route to: Location & Availability Agent

10. LOCATION & AVAILABILITY AGENT
    └─> Find doctors:
    │   ├─ Get user location (via permission)
    │   ├─ Search nearby General Physicians
    │   ├─ Fetch availability from DB
    │   └─ Suggest top 3 doctors + best slots
    └─> Return to Supervisor

11. SUPERVISOR
    └─> Intent: Check if user wants to book
    └─> Wait for user input (show options to user)

12. USER CONFIRMS BOOKING
    └─> Select: "Dr. Rajesh Kumar, 2:00 PM today"

13. BOOKING AGENT
    └─> Create appointment:
    │   ├─ Validate slot availability
    │   ├─ Create appointment record in DB
    │   ├─ Update doctor availability
    │   ├─ Send confirmation email
    │   └─> Store in Appointments collection
    └─> Return confirmation

14. SUPERVISOR
    └─> Intent: "FINISH"
    └─> End conversation

15. OUTPUT (Back to UI)
    └─> Show:
    │   ├─ Detected Symptoms
    │   ├─ Possible Diseases (with disclaimer)
    │   ├─ Recommended Specialist
    │   ├─ Suggested Doctors
    │   └─ Booking Confirmation
    └─> Enable Chat Option for post-appointment
```

---

## API Endpoints

### **Symptom Analysis**
```
POST /api/v1/symptoms/analyze
Body: {
  "patient_description": "string (text)",
  "language": "EN|HI|MR",
  "user_id": "string"
}
Response: {
  "symptoms": ["headache", "fever"],
  "severity": ["severe", "moderate"],
  "session_id": "string"
}
```

### **Specialist Recommendation**
```
POST /api/v1/specialists/recommend
Body: {
  "session_id": "string",
  "user_id": "string"
}
Response: {
  "diseases": [
    {"name": "Influenza", "confidence": 0.92},
    ...
  ],
  "specialists": [
    {"name": "General Physician", "ranking": 1},
    ...
  ],
  "disclaimer": "This is not medical diagnosis..."
}
```

### **Doctor Search & Availability**
```
GET /api/v1/doctors/search?specialization=General%20Physician&latitude=19.076&longitude=72.877
Response: {
  "doctors": [
    {
      "doctor_id": "string",
      "name": "string",
      "rating": 4.8,
      "distance_km": 2.5,
      "available_slots": [
        {"date": "2024-05-03", "time": "14:00"},
        ...
      ]
    },
    ...
  ]
}
```

### **Book Appointment**
```
POST /api/v1/appointments/book
Body: {
  "user_id": "string",
  "doctor_id": "string",
  "appointment_date": "2024-05-03T14:00:00",
  "reason_for_visit": "string"
}
Response: {
  "appointment_id": "string",
  "confirmation_message": "string",
  "booking_reference": "string"
}
```

### **WebSocket Chat**
```
WebSocket /ws/chat/{appointment_id}?user_id={user_id}

Message Format: {
  "type": "message|typing|read",
  "content": "string",
  "language": "EN|HI|MR"
}
```

---

## Security & Compliance

1. **HIPAA Compliance**: Encrypt sensitive medical data
2. **Data Privacy**: User consent for symptom analysis
3. **Authentication**: JWT tokens for API access
4. **Authorization**: Role-based access (patient/doctor/admin)
5. **Input Validation**: Sanitize all user inputs
6. **Rate Limiting**: Prevent abuse (e.g., 100 requests/hour)
7. **Content Moderation**: Flag inappropriate messages in chat
8. **Medical Disclaimer**: Always display for AI predictions

---

## Deployment Strategy

1. **Development**: Local Docker containers
2. **Staging**: Cloud VM (AWS EC2 / Google Cloud)
3. **Production**: Kubernetes cluster with:
   - Horizontal scaling for FastAPI
   - Redis cluster for cache
   - MongoDB Atlas for database
   - CDN for frontend assets

---

## Next Steps

1. ✅ Review and approve architecture
2. ⏳ Implement database models
3. ⏳ Create new agents
4. ⏳ Build API endpoints
5. ⏳ Develop frontend components
6. ⏳ Set up WebSocket chat
7. ⏳ Integrate translation service
8. ⏳ Testing & deployment

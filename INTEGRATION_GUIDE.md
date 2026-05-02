# Complete System Integration Guide

## 📚 Table of Contents
1. System Components
2. Data Flow
3. Agent Execution Flow
4. API Integration Points
5. Database Integration
6. Frontend-Backend Communication
7. Real-time Chat Integration
8. Multilingual Pipeline
9. Error Handling
10. Performance Optimization

---

## 🏗️ System Components

### Backend Components
```
backend/
├── main.py                      # FastAPI app initialization
├── config.py                    # Configuration management
├── agents/                      # Multi-agent system
│   ├── supervisor.py            # Main router
│   ├── symptom_analysis_node.py # Symptom extraction
│   ├── medical_reasoning_node.py# Disease prediction
│   ├── specialist_recommendation_node.py
│   ├── location_availability_node.py
│   ├── chat_node.py             # Post-appointment chat
│   ├── booking_node.py          # Appointment booking
│   ├── information_node.py      # General info
│   └── builder.py               # Graph construction
├── api/
│   └── v1/
│       ├── symptoms.py          # Symptom endpoints
│       ├── specialists.py       # Specialist endpoints
│       ├── doctors.py           # Doctor search endpoints
│       ├── appointments.py      # Appointment endpoints
│       ├── chat.py              # Chat endpoints
│       └── health.py            # Health check
├── database/
│   ├── connection.py            # DB connection manager
│   └── crud.py                  # Database operations
├── services/
│   ├── llm.py                   # LLM service
│   ├── translation.py           # Translation service
│   ├── location.py              # Location service
│   ├── cache.py                 # Caching layer
│   └── email.py                 # Email notifications
├── models/
│   └── schemas.py               # Pydantic models
├── websocket/
│   └── chat_manager.py          # WebSocket chat handler
└── utils/
    ├── validators.py            # Input validation
    ├── logger.py                # Logging setup
    └── constants.py             # Constants
```

### Frontend Components
```
frontend/
├── streamlit_main.py            # Main app
└── pages/
    ├── 1_home.py                # Landing page
    ├── 2_symptom_checker.py     # Symptom analysis UI
    ├── 3_doctor_finder.py       # Doctor search UI
    ├── 4_appointments.py        # Appointments UI
    └── 5_chat.py                # Chat UI
```

---

## 🔄 Complete Data Flow

### User Journey: Symptom → Diagnosis → Booking → Chat

```
1. USER INITIATES SYMPTOM CHECK
   ↓
   └─→ Streamlit: Patient enters symptoms
   └─→ Translation Service: Normalize to English
   └─→ API: POST /api/v1/symptoms/analyze

2. BACKEND PROCESSES SYMPTOMS
   ↓
   └─→ FastAPI Endpoint: Receives request
   └─→ Supervisor Agent: Routes to symptom_analysis
   └─→ Symptom Analysis Agent:
       ├─ Extract symptoms
       ├─ Assess severity
       ├─ Check for emergency
       └─ Return structured output
   └─→ Database: Log interaction
   └─→ Response sent back to frontend

3. FRONTEND DISPLAYS RESULTS
   ↓
   └─→ Streamlit: Show extracted symptoms
   └─→ User confirmation: Proceed to diagnosis?

4. AI DIAGNOSIS GENERATION
   ↓
   └─→ API: POST /api/v1/diagnosis/predict
   └─→ Supervisor: Route to medical_reasoning
   └─→ Medical Reasoning Agent:
       ├─ Analyze symptoms
       ├─ Query medical KB
       ├─ Predict diseases (top 3)
       ├─ Add confidence scores
       └─ Return with disclaimer
   └─→ Database: Log diagnosis results
   └─→ Response: Diseases + specialists

5. SPECIALIST RECOMMENDATION
   ↓
   └─→ Supervisor: Route to specialist_recommendation
   └─→ Specialist Agent:
       ├─ Map diseases to specialists
       ├─ Rank by relevance
       └─ Return recommendations

6. DOCTOR SEARCH & AVAILABILITY
   ↓
   └─→ API: GET /api/v1/doctors/search?specialization=...&latitude=...
   └─→ Supervisor: Route to location_availability
   └─→ Location Agent:
       ├─ Find nearby doctors
       ├─ Check availability
       ├─ Suggest best slots
       └─ Return doctor list
   └─→ Frontend: Display doctors

7. APPOINTMENT BOOKING
   ↓
   └─→ User selects doctor + time
   └─→ API: POST /api/v1/appointments/book
   └─→ Supervisor: Route to booking_node
   └─→ Booking Agent:
       ├─ Validate availability
       ├─ Create appointment record
       ├─ Update doctor availability
       ├─ Send confirmation email
       └─ Return appointment_id
   └─→ Database: Store appointment
   └─→ Frontend: Confirmation + appointment ID

8. POST-APPOINTMENT CHAT
   ↓
   └─→ User opens chat
   └─→ WebSocket Connection: /ws/chat/{appointment_id}
   └─→ Chat Manager: Establish connection
   └─→ Frontend: Display chat history
   └─→ User sends message
   └─→ API: Store in DB + broadcast to doctor
   └─→ Doctor receives + responds
   └─→ Message flows back to patient

9. MULTILINGUAL OUTPUT
   ↓
   └─→ At each step: Check language_preference
   └─→ Translation Service: Translate response
   └─→ Return in user's language
```

---

## 🤖 Agent Execution Flow (LangGraph)

### Graph Structure
```
                    START
                      ↓
             ┌─────────────────┐
             │   SUPERVISOR    │
             └────────┬────────┘
                      ↓
        ┌─────────────────────────────────┐
        ↓         ↓         ↓       ↓      ↓
     symptom  medical   specialist location booking
     analysis reasoning recommend  avail    & chat
        ↓         ↓         ↓       ↓      ↓
        └─────────────────────────────────┘
                      ↓
             ┌─────────────────┐
             │   SUPERVISOR    │ (Next routing)
             └────────┬────────┘
                      ↓
              (Loop until FINISH)
                      ↓
                    END
```

### Agent Routing Logic
```python
# Supervisor evaluation
if user_intent == "symptom_description":
    route = "symptom_analysis"
elif symptoms_present and need_diagnosis:
    route = "medical_reasoning"
elif diseases_predicted:
    route = "specialist_recommendation"
elif need_to_find_doctor:
    route = "location_availability"
elif user_ready_to_book:
    route = "booking_node"
elif post_appointment_chat:
    route = "chat_node"
else:
    route = "FINISH"
```

---

## 🔌 API Integration Points

### REST API Endpoints
```
SYMPTOM ANALYSIS
  POST /api/v1/symptoms/analyze
  ├─ Input: patient_description, language, user_id
  └─ Output: symptoms[], severity[], urgency_level

DIAGNOSIS PREDICTION
  POST /api/v1/diagnosis/predict
  ├─ Input: session_id, user_id, language
  └─ Output: diseases[], confidence_scores, disclaimer

SPECIALIST RECOMMENDATION
  POST /api/v1/specialists/recommend
  ├─ Input: predicted_disease, user_id, language
  └─ Output: specialists[], justifications, primary_specialist

DOCTOR SEARCH
  GET /api/v1/doctors/search
  ├─ Input: specialization, latitude, longitude, distance
  └─ Output: doctors[], ratings, availability

DOCTOR AVAILABILITY
  GET /api/v1/doctors/{doctor_id}/availability
  ├─ Input: doctor_id, date
  └─ Output: time_slots[], availability_status

APPOINTMENTS
  POST /api/v1/appointments/book
  ├─ Input: user_id, doctor_id, date, reason
  └─ Output: appointment_id, confirmation

CHAT
  WebSocket /ws/chat/{appointment_id}
  ├─ Input: user_id, user_type, message
  └─ Output: message, sender_info, timestamp
```

---

## 🗄️ Database Integration

### MongoDB Collections Structure
```javascript
// Users Collection
db.users.find({})
{
  _id: ObjectId,
  user_id: "uuid",
  name: "John Doe",
  email: "john@example.com",
  language_preference: "EN",
  location: {lat, lon, city},
  medical_history: ["condition1", "condition2"]
}

// Doctors Collection
db.doctors.find({})
{
  _id: ObjectId,
  doctor_id: "uuid",
  name: "Dr. Smith",
  specialization: "Cardiologist",
  clinic_location: {lat, lon, address},
  rating: 4.8,
  availability_slots: [{date, start_time, end_time, is_available}]
}

// Appointments Collection
db.appointments.find({})
{
  _id: ObjectId,
  appointment_id: "uuid",
  user_id: "uuid",
  doctor_id: "uuid",
  appointment_date: ISODate(),
  status: "BOOKED|COMPLETED|CANCELLED",
  symptoms: ["symptom1", "symptom2"],
  predicted_diagnoses: [{disease, confidence}]
}

// Chat History
db.chat_history.find({})
{
  _id: ObjectId,
  chat_id: "uuid",
  appointment_id: "uuid",
  messages: [
    {sender_type, sender_id, content, timestamp, language}
  ]
}

// Medical Interaction Logs
db.medical_interaction_logs.find({})
{
  _id: ObjectId,
  user_id: "uuid",
  interaction_type: "SYMPTOM_ANALYSIS|DIAGNOSIS|BOOKING",
  symptoms_input: "string",
  diseases_predicted: ["disease1"],
  specialist_recommended: "string"
}
```

### Query Optimization
```python
# Create indexes
db.users.createIndex({"email": 1}, {unique: true})
db.appointments.createIndex({"user_id": 1, "appointment_date": -1})
db.doctors.createIndex({"clinic_location": "2dsphere"})
db.chat_history.createIndex({"appointment_id": 1})
```

---

## 🌐 Frontend-Backend Communication

### Streamlit → FastAPI Flow
```python
# 1. User Input in Streamlit
symptom_text = st.text_area("Describe symptoms...")

# 2. HTTP Request to Backend
response = requests.post(
    "http://localhost:8003/api/v1/symptoms/analyze",
    json={
        "patient_description": symptom_text,
        "language": "EN",
        "user_id": session_state.user_id
    },
    timeout=30
)

# 3. Process Response
if response.status_code == 200:
    data = response.json()
    symptoms = data["symptoms"]
    # Display in Streamlit
    st.dataframe(symptoms)

# 4. User Action
if st.button("Continue to Diagnosis"):
    # Next API call...
```

### Session State Management
```python
st.session_state = {
    "user_id": "12345678",
    "user_name": "John Doe",
    "language": "EN",
    "symptoms": [...],
    "diagnoses": [...],
    "selected_doctor": {...},
    "appointment_id": "apt-uuid",
    "chat_id": "chat-uuid"
}
```

---

## 💬 Real-time Chat Integration

### WebSocket Connection Lifecycle
```python
# 1. User opens chat page
# 2. Streamlit initiates WebSocket connection
websocket_url = f"ws://localhost:8003/ws/chat/{appointment_id}"

# 3. Chat Manager accepts connection
# 4. Previous messages loaded via REST API
messages = requests.get(f"/api/v1/chats/{chat_id}/history")

# 5. User types and sends message
# 6. Message goes through WebSocket
# 7. Server broadcasts to doctor
# 8. Doctor's response comes back through WebSocket
# 9. Display in Streamlit

# 10. Connection closes when user leaves page
```

### Message Flow Diagram
```
Patient                    Server                    Doctor
  │                          │                          │
  ├──POST /send_message─────→│                          │
  │                          ├──Broadcast to Doctor────→│
  │                          │                          │
  │                          │←─Doctor types (ping)─────┤
  │                          │                          │
  │                          │←─Doctor sends message────┤
  │                          │                          │
  │←─WebSocket message───────┤                          │
  │                          │                          │
  ├─Read Receipt─────────────→│                          │
```

---

## 🌍 Multilingual Pipeline

### Language Flow
```
INPUT → DETECTION → NORMALIZATION → PROCESSING → OUTPUT

1. Input: "मुझे बुखार है"
2. Detection: Language = "HI"
3. Normalization: "मुझे बुखार है" → "I have fever" (English)
4. Processing: English text through agents
5. Output Translation: English result → User's language
6. Output: "आपको बुखार है..." (Hindi response)
```

### Translation Service Integration
```python
# In any agent or endpoint:
translation_service = get_translation_service()

# Detect user language
detected_lang = translation_service.detect_language(user_input)

# Normalize to English for processing
normalized = translation_service.normalize_to_english(user_input)

# Process (agents use English)
result = process_with_agents(normalized)

# Translate response back
if user_language != "EN":
    result = translation_service.translate(result, "EN", user_language)

return result
```

---

## 🚨 Error Handling

### Exception Hierarchy
```python
try:
    # API call
    response = requests.post(url, json=data, timeout=30)
    data = response.json()
except requests.exceptions.Timeout:
    # Handle timeout
    st.error("Request timeout. Please try again.")
except requests.exceptions.ConnectionError:
    # Handle connection error
    st.error("Cannot connect to server.")
except json.JSONDecodeError:
    # Handle invalid JSON
    st.error("Invalid response format.")
except Exception as e:
    # Handle unexpected error
    st.error(f"Error: {str(e)}")
```

### Error Recovery
```python
# Retry logic
max_retries = 3
for attempt in range(max_retries):
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

---

## ⚡ Performance Optimization

### Caching Strategy
```python
from functools import lru_cache

# Cache doctor searches
@lru_cache(maxsize=128)
def search_doctors_cached(specialization, latitude, longitude):
    return search_doctors(specialization, latitude, longitude)

# Redis caching for session data
def get_user_from_cache(user_id):
    cached = redis_client.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    # Fetch from DB, cache for 1 hour
    user = UserCRUD.get_user(user_id)
    redis_client.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user
```

### Database Query Optimization
```python
# Use indexes for frequent queries
db.appointments.createIndex({"user_id": 1, "appointment_date": -1})
db.doctors.createIndex({"specialization": 1, "clinic_location": "2dsphere"})

# Use projection to fetch only needed fields
appointments = db.appointments.find(
    {"user_id": user_id},
    {"_id": 0, "appointment_id": 1, "doctor_id": 1, "appointment_date": 1}
)

# Pagination for large result sets
doctors = db.doctors.find(query).skip(offset).limit(page_size)
```

### API Response Optimization
```python
# Compress responses
@app.middleware("http")
async def compress_response(request, call_next):
    response = await call_next(request)
    if len(response.body) > 1000:
        response.headers["Content-Encoding"] = "gzip"
    return response

# Response pagination
@app.get("/doctors")
async def list_doctors(page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    doctors = DoctorCRUD.get_doctors().skip(skip).limit(page_size)
    return {"doctors": doctors, "page": page, "total": total_count}
```

---

## 🧪 Integration Testing

### End-to-End Test
```python
def test_symptom_to_booking():
    # 1. Create user
    user = create_test_user()
    
    # 2. Analyze symptoms
    symptom_response = client.post("/api/v1/symptoms/analyze", 
        json={"patient_description": "...", "user_id": user["user_id"]})
    assert symptom_response.status_code == 200
    
    # 3. Get diagnosis
    diagnosis_response = client.post("/api/v1/diagnosis/predict",
        params={"session_id": symptom_response.json()["session_id"]})
    assert diagnosis_response.status_code == 200
    
    # 4. Get specialists
    specialist_response = client.post("/api/v1/specialists/recommend",
        json={"predicted_disease": diagnosis_response.json()["diseases"][0]})
    assert specialist_response.status_code == 200
    
    # 5. Search doctors
    doctors_response = client.get("/api/v1/doctors/search",
        params={"specialization": "Cardiologist", "latitude": 19.07, "longitude": 72.87})
    assert doctors_response.status_code == 200
    assert len(doctors_response.json()["doctors"]) > 0
    
    # 6. Book appointment
    doctor = doctors_response.json()["doctors"][0]
    booking_response = client.post("/api/v1/appointments/book",
        json={"user_id": user["user_id"], "doctor_id": doctor["doctor_id"]})
    assert booking_response.status_code == 200
    
    # 7. Verify appointment created
    appointment = booking_response.json()
    assert appointment["status"] == "BOOKED"
```

---

## 📊 Monitoring & Logging

### Logging Points
```python
# Log at each critical point
logger.info(f"User {user_id} started symptom analysis")
logger.info(f"Symptoms extracted: {symptoms}")
logger.info(f"Diseases predicted: {diseases}")
logger.info(f"Appointment booked: {appointment_id}")
logger.error(f"Error booking appointment: {error}")
logger.warning(f"Emergency symptoms detected: {emergency_symptoms}")
```

### Metrics
```python
# Track key metrics
- Symptom analysis requests/hour
- Successful diagnosis predictions
- Appointment booking success rate
- Chat message count
- API response time
- Database query time
- Error rates
```

---

This completes the comprehensive integration guide for the AI-Powered Healthcare Assistant Platform!

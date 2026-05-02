# Doctor-Patient Appointment Multi-Agent System

An intelligent appointment management system powered by LangGraph and multi-agent architecture that automates doctor-patient appointment booking, rescheduling, and information retrieval using natural language processing.

> **⚠️ Learning Project Disclaimer**  
> This project is built for **educational and learning purposes only**. It demonstrates the fundamentals of multi-agent systems using LangGraph. If you're interested in a production-ready, highly advanced version with enterprise features, I can develop a comprehensive system including:
> - **Database Integration** (PostgreSQL, MongoDB with proper schema design)
> - **Human-in-the-Loop** (approval workflows, escalation mechanisms)
> - **Advanced Authentication & Authorization** (OAuth2, JWT, role-based access)
> - **Observability & Monitoring** (OpenTelemetry, Prometheus, Grafana dashboards)
> - **Production Deployment** (Docker, Kubernetes, CI/CD pipelines)
> - **Scalability** (Load balancing, caching with Redis, message queues)
> - **Advanced AI Features** (RAG, memory persistence, conversation history)
> - **Testing Suite** (Unit, integration, end-to-end tests)
> - **API Rate Limiting & Security** (API gateway, encryption, audit logs)
> - **Multi-tenancy Support** (Organization management, data isolation)

## 🌟 Features

- **Natural Language Processing**: Interact with the system using conversational queries
- **Multi-Agent Architecture**: Supervisor, Information, and Booking agents coordinate to handle requests
- **Appointment Management**: 
  - Check doctor availability by name or specialization
  - Book new appointments
  - Reschedule existing appointments
  - Cancel appointments
- **Dual Interface**:
  - Streamlit web UI for user-friendly interaction
  - FastAPI backend for programmatic access
- **Intelligent Routing**: Supervisor agent intelligently routes queries to appropriate specialized agents

## 🏗️ Architecture

The system uses a **multi-agent** architecture built on LangGraph:

![Multi-Agent Architecture](./agent%20structure.png)

**Workflow:**
- The **Supervisor** receives user queries and routes them to specialized agents
- The **Information Node** handles availability checks and general queries
- The **Booking Node** manages appointment actions (book, reschedule, cancel)
- Agents can loop back to the supervisor for multi-step conversations
- The workflow terminates at the **end** node when the task is complete

### Agents

1. **Supervisor Agent**: Entry point that analyzes user queries and routes them to appropriate specialized agents
2. **Information Node**: Handles queries about doctor availability and appointment information
3. **Booking Node**: Manages appointment booking, rescheduling, and cancellation

### Tools

- `check_availability_by_doctor`: Check available time slots for a specific doctor
- `check_availability_by_specialization`: Find available doctors by medical specialization
- `set_appointment`: Book a new appointment
- `reschedule_appointment`: Modify existing appointment times
- `cancel_appointment`: Cancel scheduled appointments

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- GROQ API key (for LLM access)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd doctor-patient-appointment-multiagent-system
```

2. Install dependencies:
```bash
pip install langchain langchain-groq langgraph streamlit fastapi uvicorn pandas python-dotenv
```

3. Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
```

4. Ensure you have the `doctor_availability.csv` file in the root directory with appointment data

### Configuration

Update the LLM model in [services/llm.py](services/llm.py) if needed:
```python
llm_instance = LLMModel(model_name="llama3-70b-8192")
```

## 💻 Usage

### Option 1: Streamlit UI

1. Start the FastAPI backend:
```bash
cd endpoints
uvicorn agent:app --host 127.0.0.1 --port 8003
```

2. In a new terminal, launch the Streamlit interface:
```bash
streamlit run streamlit_ui.py
```

3. Access the UI at `http://localhost:8501`
   - Enter your ID number
   - Type your query (e.g., "I want to book an appointment with a cardiologist tomorrow at 10 AM")
   - Submit and receive intelligent responses

### Option 2: Direct Python Script

Run the main script:
```bash
python main.py
```

Modify the `initial_state` in [main.py](main.py) to test different queries.

### Option 3: API Endpoint

Send POST requests to `http://127.0.0.1:8003/execute`:

```python
import requests

response = requests.post(
    "http://127.0.0.1:8003/execute",
    json={
        "messages": "Can you check if a dentist is available tomorrow at 10 AM?",
        "id_number": 101
    }
)
print(response.json())
```

## 📁 Project Structure

```
doctor-patient-appointment-multiagent-system/
├── agents/
│   ├── booking_node.py          # Handles booking, rescheduling, cancellation
│   ├── builder.py               # Builds the agent graph
│   ├── information_node.py      # Handles availability queries
│   ├── state.py                 # Defines agent state schema
│   └── supervisor.py            # Supervisor agent routing logic
├── dummy-appointment-data/      # Sample data for testing
├── endpoints/
│   └── agent.py                 # FastAPI server endpoint
├── experiment/
│   └── experiment.ipynb         # Jupyter notebook for experiments
├── models/
│   ├── datetime.py              # Date/time models
│   ├── id.py                    # ID models
│   └── user.py                  # User query models
├── prompts/
│   └── prompt.py                # System prompts for agents
├── services/
│   └── llm.py                   # LLM service configuration
├── tools/
│   ├── cancel_appointment.py    # Appointment cancellation tool
│   ├── check_availability.py    # Availability checking tools
│   ├── reschedule_appointment.py # Rescheduling tool
│   └── set_appointment.py       # Appointment booking tool
├── main.py                      # Direct execution script
├── streamlit_ui.py              # Streamlit web interface
└── doctor_availability.csv      # Doctor availability database
```

## 🔧 Supported Specializations

- General Dentist
- Cosmetic Dentist
- Prosthodontist
- Pediatric Dentist
- Emergency Dentist
- Oral Surgeon
- Orthodontist

## 📝 Example Queries

- "I want to book an appointment with Dr. John Doe tomorrow at 2 PM"
- "Can you check if a cardiologist is available next Monday?"
- "I need to reschedule my appointment to next week"
- "Cancel my appointment scheduled for tomorrow"
- "Show me available dentists for this Friday afternoon"

## 🛠️ Technologies Used

- **LangGraph**: Multi-agent orchestration framework
- **LangChain**: LLM application framework
- **GROQ**: LLM API provider
- **FastAPI**: Backend API framework
- **Streamlit**: Web UI framework
- **Pandas**: Data manipulation for availability checking

## 🚀 Future Enhancements

This is a learning project showcasing multi-agent fundamentals. Potential enterprise features for a production system include:

### Infrastructure & Deployment
- 🐳 **Containerization**: Docker with multi-stage builds
- ☸️ **Orchestration**: Kubernetes deployment with auto-scaling
- 🔄 **CI/CD**: GitHub Actions/GitLab CI with automated testing
- 🌐 **Cloud Deployment**: AWS/Azure/GCP with infrastructure as code (Terraform)

### Data & Persistence
- 🗄️ **Database**: PostgreSQL/MongoDB with proper indexing and migrations
- 💾 **Caching Layer**: Redis for session management and performance
- 📊 **Data Warehousing**: Analytics and reporting capabilities
- 🔄 **Message Queues**: RabbitMQ/Kafka for asynchronous processing

### Security & Compliance
- 🔐 **Authentication**: OAuth2, JWT, multi-factor authentication
- 🛡️ **Authorization**: Role-based access control (RBAC)
- 🔒 **Data Encryption**: At-rest and in-transit encryption
- 📝 **Audit Logging**: Comprehensive activity tracking
- ⚖️ **Compliance**: HIPAA/GDPR compliance for healthcare data

### Observability & Monitoring
- 📊 **Metrics**: Prometheus with custom business metrics
- 📈 **Dashboards**: Grafana for real-time monitoring
- 🔍 **Distributed Tracing**: OpenTelemetry/Jaeger for request tracking
- 🚨 **Alerting**: PagerDuty/Slack integration for incidents
- 📝 **Structured Logging**: ELK stack (Elasticsearch, Logstash, Kibana)

### Advanced AI Features
- 🧠 **Memory Persistence**: Long-term conversation context
- 📚 **RAG Integration**: Knowledge base with vector databases
- 🤖 **Multi-model Support**: Fallback strategies and model routing
- 🔄 **Human-in-the-Loop**: Approval workflows for critical actions
- 🎯 **Personalization**: User preference learning and adaptation

### Performance & Scalability
- ⚡ **Load Balancing**: Horizontal scaling with load balancers
- 🚀 **API Gateway**: Rate limiting, throttling, request validation
- 📦 **Microservices**: Service mesh architecture
- 🔄 **Async Processing**: Background job processing
- 💨 **CDN Integration**: Static asset delivery

### Testing & Quality
- ✅ **Unit Tests**: Comprehensive test coverage (>80%)
- 🔗 **Integration Tests**: API and database testing
- 🎭 **End-to-End Tests**: Selenium/Playwright for UI testing
- 🧪 **Load Testing**: Performance benchmarking with k6/JMeter
- 🔍 **Code Quality**: SonarQube, linting, and static analysis

### User Experience
- 📱 **Mobile App**: React Native/Flutter mobile interface
- 🔔 **Notifications**: Email, SMS, push notifications
- 🌍 **Internationalization**: Multi-language support
- ♿ **Accessibility**: WCAG compliance
- 📧 **Email Templates**: Branded confirmation emails

**Interested in building the advanced version?** Feel free to reach out for collaboration or custom development!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

Built with LangGraph's multi-agent framework for intelligent task coordination and routing.

## 📞 Contact

Interested in collaborating or need a production-ready multi-agent system? Feel free to reach out!

- **Mobile**: +91 8002007238
- **Email**: [shubham07kumargupta@gmail.com](mailto:shubham07kumargupta@gmail.com)
- **LinkedIn**: [shubhamiitpatna](https://linkedin.com/in/shubhamiitpatna)
- **GitHub**: [@SHubhamanjk](https://github.com/SHubhamanjk)
- **Portfolio**: [shubham-exe.netlify.app](https://shubham-exe.netlify.app)

For enterprise solutions, custom development, or professional inquiries, please reach out via email or LinkedIn.
"# NLP-based-Hospital-Appointment-Scheduling-System" 

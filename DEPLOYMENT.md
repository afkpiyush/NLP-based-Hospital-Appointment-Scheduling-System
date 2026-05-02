# AI-Powered Healthcare Assistant - Complete Deployment Guide

## 🚀 Quick Start (Development)

### Prerequisites
- Python 3.8+
- MongoDB or PostgreSQL
- Redis (optional, for caching)
- GROQ API key (for LLM)

### Installation Steps

#### 1. Clone and Setup
```bash
cd doctor-healthcare-assistant
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

#### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

#### 4. Start Services

**Terminal 1 - FastAPI Backend:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Terminal 2 - Streamlit Frontend:**
```bash
streamlit run frontend/streamlit_main.py --server.port=8501
```

#### 5. Access Application
- **Streamlit UI:** http://localhost:8501
- **API Docs:** http://localhost:8003/docs
- **API Swagger:** http://localhost:8003/swagger-ui.html

---

## 🗄️ Database Setup

### MongoDB Setup (Recommended)

**Local Installation:**
```bash
# Install MongoDB
# Linux: sudo apt-get install -y mongodb
# macOS: brew install mongodb-community
# Windows: Download from https://www.mongodb.com/try/download/community

# Start MongoDB
mongod

# Verify connection
mongo
```

**Cloud Setup (MongoDB Atlas):**
```
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create cluster and database
3. Copy connection string to MONGODB_URL in .env
```

### PostgreSQL Setup

```bash
# Install PostgreSQL
# Linux: sudo apt-get install postgresql postgresql-contrib
# macOS: brew install postgresql
# Windows: Download installer

# Create database
createdb healthcare_assistant

# Update credentials in .env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
```

---

## 🔧 Configuration

### API Keys Required

1. **GROQ API** (LLM):
   - Sign up: https://console.groq.com
   - Get API key: Settings → API Keys
   - Add to .env: `GROQ_API_KEY=...`

2. **Google Translate API** (Optional):
   - Enable in Google Cloud Console
   - Create service account
   - Add key to .env: `GOOGLE_TRANSLATE_API_KEY=...`

3. **Google Maps API** (Optional):
   - Create API key in Google Cloud Console
   - Add to .env: `GOOGLE_MAPS_API_KEY=...`

---

## 📊 Database Schema Initialization

### Auto-Migration (Recommended)
```python
from backend.database.connection import MongoDBClient

client = MongoDBClient()
db = client.get_database()

# Collections are created automatically on first insert
```

### Manual Collection Creation
```bash
# Connect to MongoDB
mongo healthcare_assistant

# Create indexes
db.users.createIndex({"email": 1}, {unique: true})
db.users.createIndex({"clinic_location": "2dsphere"})
db.doctors.createIndex({"specialization": 1})
db.doctors.createIndex({"clinic_location": "2dsphere"})
db.appointments.createIndex({"user_id": 1})
db.appointments.createIndex({"doctor_id": 1})
db.chat_history.createIndex({"appointment_id": 1})
```

---

## 🌐 Production Deployment

### Docker Containerization

**Dockerfile Example:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8003

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8003"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongo_data:/data/db

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8003:8003"
    environment:
      - MONGODB_URL=mongodb://root:password@mongodb:27017
      - REDIS_URL=redis://redis:6379
      - LLM_PROVIDER=groq
      - GROQ_API_KEY=${GROQ_API_KEY}
    depends_on:
      - mongodb
      - redis

  frontend:
    image: streamlit-frontend:latest
    ports:
      - "8501:8501"
    depends_on:
      - backend

volumes:
  mongo_data:
```

**Deploy with Docker Compose:**
```bash
docker-compose up -d
```

### Cloud Deployment (AWS Example)

**1. Prepare for EC2:**
```bash
# Create deployment package
zip -r deployment.zip . -x "*.git*" "venv/*" "__pycache__/*"
```

**2. Launch EC2 Instance:**
```bash
# Use Ubuntu 22.04 LTS
# Security Groups: Allow ports 8003, 8501, 27017 (if local DB)
```

**3. Setup on EC2:**
```bash
# SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv mongodb redis-server

# Deploy application
unzip deployment.zip
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Run with PM2 (process manager)
npm install -g pm2
pm2 start backend/main.py --name "api" --interpreter python
pm2 start "streamlit run frontend/streamlit_main.py" --name "ui"
pm2 save
```

### Using AWS AppRunner / Heroku

**Heroku Deployment:**
```bash
# Create Procfile
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
worker: streamlit run frontend/streamlit_main.py --server.port=8501

# Deploy
heroku login
heroku create your-app-name
git push heroku main
```

---

## 🧪 Testing

### Unit Tests
```bash
pytest tests/test_agents.py -v
pytest tests/test_api.py -v
pytest tests/test_services.py -v
```

### Integration Tests
```bash
pytest tests/test_integration.py -v
```

### API Testing
```bash
# Using curl
curl -X POST http://localhost:8003/api/v1/symptoms/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "patient_description": "I have fever and headache",
    "language": "EN",
    "user_id": "12345678"
  }'

# Using Postman
# Import: backend/postman_collection.json
```

---

## 📈 Monitoring & Maintenance

### Health Check
```bash
curl http://localhost:8003/health
```

### View Logs
```bash
# Docker logs
docker-compose logs -f backend

# Application logs
tail -f logs/app.log
```

### Database Backup
```bash
# MongoDB backup
mongodump --uri "mongodb://localhost:27017" --out backup/

# PostgreSQL backup
pg_dump healthcare_assistant > backup.sql
```

---

## 🔒 Security Checklist

- [ ] Change JWT_SECRET_KEY in production
- [ ] Enable HTTPS/SSL certificates
- [ ] Set CORS_ORIGINS to specific domains
- [ ] Enable database authentication
- [ ] Rotate API keys regularly
- [ ] Enable rate limiting
- [ ] Set up firewall rules
- [ ] Enable database encryption
- [ ] Configure backup strategy
- [ ] Setup monitoring & alerts

---

## 🆘 Troubleshooting

### MongoDB Connection Error
```bash
# Verify MongoDB is running
mongosh
# If error: start MongoDB service
sudo service mongod start
```

### Port Already in Use
```bash
# Find process using port 8003
lsof -i :8003
# Kill process
kill -9 <PID>
```

### LLM API Error
```
Error: GROQ_API_KEY not found
Solution: Set API key in .env and restart app
```

### Memory Issues
```
Solution: Increase available memory or use horizontal scaling
Docker: Set memory limits in docker-compose.yml
```

---

## 📚 API Documentation

Full API documentation available at:
- **Swagger UI:** http://localhost:8003/docs
- **ReDoc:** http://localhost:8003/redoc
- **OpenAPI JSON:** http://localhost:8003/openapi.json

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/new-feature`
2. Commit changes: `git commit -m "Add new feature"`
3. Push branch: `git push origin feature/new-feature`
4. Create Pull Request

---

## 📞 Support

- **Issues:** Create GitHub issue
- **Email:** support@healthcareassistant.com
- **Documentation:** https://docs.healthcareassistant.com

---

## 📄 License

This project is licensed under MIT License - see LICENSE file for details.

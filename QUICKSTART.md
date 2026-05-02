# ⚡ Quick Start Guide (5 Minutes to Running)

## Step 1: Install Dependencies (2 minutes)

```bash
# Navigate to project
cd c:\Users\piyus\Desktop\SE

# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate  # On Windows

# Install all packages
pip install -r backend/requirements.txt
```

## Step 2: Configure Environment (1 minute)

```bash
# Create .env file in project root
cp .env.example .env

# Edit .env - minimum required:
GROQ_API_KEY=your_groq_api_key_here
DATABASE_TYPE=mongodb
MONGODB_URL=mongodb://localhost:27017

# If using local MongoDB, it will create database automatically
```

## Step 3: Start Services (1 minute)

**Terminal 1 - Backend API:**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

**Terminal 2 - Frontend UI:**
```bash
cd frontend
streamlit run streamlit_main.py
```

## Step 4: Test the Application (1 minute)

### Access Points
- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8003/docs
- **Health Check**: http://localhost:8003/health

### Test Workflow
1. Open http://localhost:8501
2. Select language (EN/HI/MR)
3. Go to "Symptom Checker"
4. Enter: "I have fever and headache"
5. Click "Analyze Symptoms"
6. See AI results

---

## 🎯 First-Time Setup Checklist

### Before You Start
- [ ] Python 3.8+ installed: `python --version`
- [ ] MongoDB running (OR set `DATABASE_TYPE=memory` for testing)
- [ ] GROQ API key obtained from https://console.groq.com

### First Run
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip list | grep fastapi`
- [ ] .env file created with API keys
- [ ] Both services started

### Verification
- [ ] Backend responds: `curl http://localhost:8003/health`
- [ ] Frontend loads: Browser at http://localhost:8501
- [ ] API docs accessible: http://localhost:8003/docs

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find what's using port 8003
netstat -ano | findstr :8003

# Kill the process
taskkill /PID <PID> /F

# Restart
uvicorn main:app --port 8003
```

### ModuleNotFoundError
```bash
# Ensure virtual environment is activated
which python  # Should show venv path

# Reinstall requirements
pip install -r backend/requirements.txt --force-reinstall
```

### Database Connection Error
```bash
# Option 1: Use in-memory database for testing
echo "DATABASE_TYPE=memory" >> .env

# Option 2: Start MongoDB
mongod

# Option 3: Use MongoDB Atlas (cloud)
# Update MONGODB_URL in .env to MongoDB Atlas connection string
```

### GROQ API Error
```bash
# Verify API key is correct
echo $env:GROQ_API_KEY  # Windows: echo %GROQ_API_KEY%

# Get new key: https://console.groq.com
# Update .env with new key
# Restart backend
```

---

## 📝 Quick Test Commands

### Test Backend Endpoints

```bash
# Health check
curl http://localhost:8003/health

# Symptom analysis
curl -X POST http://localhost:8003/api/v1/symptoms/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "patient_description": "I have fever and cough",
    "language": "EN",
    "user_id": "test-user-1"
  }'

# Search doctors
curl "http://localhost:8003/api/v1/doctors/search?specialization=General%20Physician&latitude=19.07&longitude=72.87&distance=10"
```

### Test Frontend
1. Open http://localhost:8501
2. Try each page:
   - Home (Overview)
   - Symptom Checker (Test AI)
   - Doctor Finder (Search)
   - Appointments (History)
   - Chat (Messaging)

---

## 🚀 Next Steps

### After First Run (Day 1)
- [ ] Explore API documentation at http://localhost:8003/docs
- [ ] Test all 5 Streamlit pages
- [ ] Review ARCHITECTURE.md for system overview
- [ ] Check INTEGRATION_GUIDE.md for integration details

### After Testing (Week 1)
- [ ] Set up proper MongoDB/PostgreSQL
- [ ] Configure email notifications
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring
- [ ] Deploy to staging

### For Production (Week 2-4)
- [ ] Configure Redis caching
- [ ] Set up database backups
- [ ] Enable rate limiting
- [ ] Configure CI/CD
- [ ] Deploy to production

---

## 📚 Important Files to Know

```
project/
├── backend/
│   ├── main.py              ← FastAPI app starts here
│   ├── config.py            ← Configuration settings
│   ├── requirements.txt      ← Python dependencies
│   ├── agents/              ← AI agents
│   ├── database/            ← Database operations
│   └── websocket/           ← Real-time chat
│
├── frontend/
│   ├── streamlit_main.py    ← Streamlit app starts here
│   └── pages/               ← UI pages
│
├── .env.example             ← Copy to .env
├── ARCHITECTURE.md          ← System design
├── INTEGRATION_GUIDE.md     ← Integration details
└── DEPLOYMENT.md            ← Deployment guide
```

---

## 💡 Quick Tips

### Enable Hot Reload
Backend automatically reloads with `--reload` flag. Just save and refresh browser.

### View Logs
```bash
# Backend logs appear in terminal running uvicorn
# Frontend logs appear in terminal running streamlit
```

### Change Language
In Streamlit UI, use language selector in sidebar to switch EN/HI/MR

### Test With Different Symptoms
Try these to see different AI responses:
- "fever, cough, sore throat" → Common Cold
- "chest pain, difficulty breathing" → Urgent care
- "headache, body pain" → Influenza
- "constipation, stomach pain" → Gastritis

---

## 🔒 Security Notes

For development only:
- JWT_SECRET_KEY in .env is public (change for production)
- CORS allows all origins (restrict for production)
- Debug mode is ON (disable for production)
- No rate limiting enabled (enable for production)

See DEPLOYMENT.md for production security checklist.

---

## 📞 Support Quick Links

| Issue | Solution |
|-------|----------|
| Port 8003 in use | See "Port Already in Use" above |
| ModuleNotFoundError | Activate venv, reinstall requirements |
| API returns 500 | Check .env configuration |
| Frontend won't load | Verify backend is running on 8003 |
| Chat not working | Check WebSocket URL in config |
| Language not working | Verify Google Translate API key (optional) |

---

## ⏱️ Time Breakdown

- **Installation**: 2 minutes
- **Configuration**: 1 minute
- **Starting services**: 1 minute
- **First test**: 1 minute
- **Total**: ~5 minutes

---

## 🎯 Success Criteria

You're ready when:
✅ Backend API responds at http://localhost:8003/health
✅ Frontend loads at http://localhost:8501
✅ Symptom checker returns results
✅ API documentation visible at http://localhost:8003/docs

---

## 📖 Read Next

1. **IMPLEMENTATION_SUMMARY.md** - Overview of everything built
2. **ARCHITECTURE.md** - Deep dive into system design
3. **INTEGRATION_GUIDE.md** - How components work together
4. **DEPLOYMENT.md** - Deploy to production

---

**You're all set! 🎉**

Have questions? Check the documentation files or the docstrings in the source code.

**Start with http://localhost:8501 and enjoy! 🚀**

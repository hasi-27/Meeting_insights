# Quick Reference - AI Meeting Insights Dashboard

## 🚀 Start Development (60 seconds)

```bash
# Terminal 1 - Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add GEMINI_API_KEY to .env
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev

# Open browser
http://localhost:5173
```

---

## 📂 Key File Locations

| What | Where |
|------|-------|
| FastAPI app | `backend/app/main.py` |
| API routes | `backend/app/api/endpoints.py` |
| Services | `backend/app/services/` |
| Models | `backend/app/models.py` |
| React app | `frontend/src/App.jsx` |
| Components | `frontend/src/components/` |
| Styles | `frontend/src/App.css` |
| Configuration | `backend/.env`, `frontend/.env` |

---

## 🔧 Environment Setup

### Backend `.env` Required
```
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
```

### Frontend `.env` Optional
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📊 Processing Pipeline

```
Upload File
    → Validate format/size
    → Save to uploads/
    → Start async processing
    → Return meeting_id
    
Poll Status
    → Transcription (Gemini audio)
    → Diarization (pyannote)
    → Merge transcript + speakers
    → LLM analysis (Gemini)
    → Calculate stats
    → Return results
```

---

## 🛠 Common Commands

### Backend
```bash
# Run development server
uvicorn app.main:app --reload

# Check health
curl http://localhost:8000/api/health

# Upload test file
curl -F "file=@test.mp3" http://localhost:8000/api/meetings/upload
```

### Frontend
```bash
# Development server
npm run dev

# Production build
npm run build

# Preview build
npm run preview
```

---

## 🏗 Architecture

```
Frontend (React + Vite)
        ↓ HTTP/API
Backend (FastAPI)
        ↓ Async
Services
  - Gemini audio (transcription)
  - pyannote (diarization)
  - Gemini (LLM)
  - Stats calculation
```

---

## 📦 Main Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Backend framework |
| `uvicorn` | ASGI server |
| `pydantic` | Data validation |
| `google-genai` | Gemini API client |
| `pyannote.audio` | Speaker ID |
| `react` | Frontend UI |
| `vite` | Frontend build |
| `recharts` | Charts |

---

## 🐛 Debugging

### Check Backend Logs
```bash
# Terminal with running uvicorn shows:
# - Request logs
# - Processing status
# - Errors
```

### Check Frontend Logs
```bash
# Browser console (F12)
# - API errors
# - Component errors
# - Network issues
```

### Test API
```bash
# Health check
curl http://localhost:8000/api/health

# Get meeting
curl http://localhost:8000/api/meetings/{meeting_id}
```

---

## ✅ Testing Workflow

1. **Start Services**
   ```bash
   # Backend + Frontend running
   ```

2. **Upload File**
   - Go to http://localhost:5173
   - Drag/drop or select audio file
   - Click "Upload & Analyze"

3. **Monitor Processing**
   - Watch processing loader
   - Check backend logs
   - Verify status polling

4. **Review Results**
   - Check overview cards
   - Read summary
   - Review decisions
   - Check action items
   - Search transcript

---

## 🔐 Security Notes

- ✅ Keep `.env` files out of git
- ✅ Never commit API keys
- ✅ Use environment variables
- ✅ Validate all inputs
- ✅ Sanitize error messages
- ✅ Use HTTPS in production

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Full documentation (2000+ lines) |
| `SETUP.md` | Setup and troubleshooting |
| `DEPLOYMENT.md` | Production deployment |
| `PROJECT_COMPLETION_SUMMARY.md` | Project overview |
| `QuickReference.md` | This file |

---

## 🚀 Deployment

### Docker
```bash
docker-compose up -d
```

### Cloud (Choose One)
- AWS: Elastic Beanstalk, ECS, Lambda
- Google: Cloud Run, App Engine
- Azure: Container Instances, App Service
- Heroku: Simple git push

See `DEPLOYMENT.md` for details.

---

## 🎯 Project Structure Quick View

```
backend/
  app/
    api/endpoints.py          ← All routes
    services/                 ← Business logic
    utils/                    ← Helpers
    config.py                 ← Settings
    models.py                 ← Schemas
    main.py                   ← Entry point

frontend/
  src/
    components/               ← React components
    pages/                    ← Page components
    services/api.js           ← API client
    App.jsx                   ← Main component
    main.jsx                  ← Entry point

Documentation:
  README.md                   ← Full guide
  SETUP.md                    ← Setup steps
  DEPLOYMENT.md               ← Deployment
```

---

## 💡 Tips & Tricks

### Development Speed
- Use `--reload` flag for auto-restart
- Hot reload works automatically in Vite
- Check logs frequently
- Use browser DevTools (F12)

### Debugging
- Add `print()` statements in Python
- Use `console.log()` in React
- Check backend terminal output
- Use browser network tab

### Testing
- Start with small audio files (< 1 MB)
- Use sample_data/ directory
- Try different audio qualities
- Test error scenarios

---

## ⚡ Performance Tips

### Backend
- Use a Gemini Flash model for speed and quality
- Enable GPU if available
- Cache frequent results
- Use async/await for I/O

### Frontend
- Lazy load components
- Optimize images
- Use React.memo for components
- Implement pagination for long lists

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 8000 in use | `lsof -i :8000` then kill process |
| Port 5173 in use | `npm run dev` uses different port |
| Dependencies fail | Delete `node_modules`, run `npm install` |
| API key error | Check `.env` file exists and has key |
| Blank dashboard | Check browser console (F12) for errors |
| Processing stuck | Check backend logs, may be transcribing |

---

## 📱 Responsive Design

Dashboard works on:
- ✅ Desktop (1920px+)
- ✅ Laptop (1366px)
- ✅ Tablet (768px+)
- ✅ Mobile (375px+)

Use browser developer tools to test different sizes.

---

## 🔗 Links

- Gemini API: https://ai.google.dev/gemini-api/docs
- FastAPI Docs: http://localhost:8000/docs
- React Docs: https://react.dev
- Tailwind CSS: https://tailwindcss.com

---

## 📞 Getting Help

1. **Check README.md** - Comprehensive documentation
2. **Check SETUP.md** - Troubleshooting section
3. **Review code comments** - Docstrings throughout
4. **Check logs** - Backend and browser console
5. **Try test endpoint** - `/api/health` to verify API

---

**Last Updated**: August 31, 2026  
**Version**: 1.0.0

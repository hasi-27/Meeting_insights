# Getting Started - AI Meeting Insights Dashboard

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.9+
- Node.js 16+
- Gemini API Key
- ~2GB free disk space

### Step 1: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your values
# GEMINI_API_KEY=your-gemini-api-key-here
```

### Step 2: Frontend Setup

```bash
# Navigate to frontend (in another terminal)
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Default value should work: VITE_API_BASE_URL=http://localhost:8000
```

### Step 3: Start Services

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open browser to **http://localhost:5173**

---

## 📋 Complete Setup Instructions

### Backend Setup (Detailed)

#### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** First installation may take 10-15 minutes due to PyTorch and pyannote.audio dependencies.

#### 3. Configure Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with required values:

```
# REQUIRED - Get from Google AI Studio
GEMINI_API_KEY=your-gemini-api-key

# Gemini model used for transcription and analysis
GEMINI_MODEL=gemini-2.5-flash

# URLs for CORS
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# File upload limits
MAX_FILE_SIZE_MB=500

# Storage directories (will be created automatically)
UPLOAD_DIRECTORY=./uploads
TEMP_DIRECTORY=./temp
```

#### 4. Run Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Test health check:
```bash
curl http://localhost:8000/api/health
```

### Frontend Setup (Detailed)

#### 1. Install Dependencies

```bash
cd frontend
npm install
```

#### 2. Configure Environment

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

The default value should work:
```
VITE_API_BASE_URL=http://localhost:8000
```

#### 3. Run Development Server

```bash
npm run dev
```

Expected output:
```
  VITE v4.5.0  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

Open browser to **http://localhost:5173**

---

## 🔧 Environment Variables Guide

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Your Gemini API key |
| `GEMINI_MODEL` | Yes | gemini-2.5-flash | Gemini model to use |
| `BACKEND_URL` | No | http://localhost:8000 | Backend URL for CORS |
| `FRONTEND_URL` | No | http://localhost:5173 | Frontend URL for CORS |
| `MAX_FILE_SIZE_MB` | No | 500 | Max upload size in MB |
| `UPLOAD_DIRECTORY` | No | ./uploads | Where to store uploads |
| `TEMP_DIRECTORY` | No | ./temp | Temporary processing dir |
| `PROCESSING_TIMEOUT` | No | 3600 | Timeout in seconds |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | No | http://localhost:8000 | Backend API URL |

---

## 🧪 Testing the System

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/health

# Expected response:
# {"status":"ok","version":"1.0.0"}
```

### 2. Test File Upload

```bash
# Create a test audio file or use an existing one
curl -F "file=@test-meeting.mp3" http://localhost:8000/api/meetings/upload

# Expected response:
# {
#   "meeting_id": "550e8400-e29b-41d4-a716-446655440000",
#   "filename": "test-meeting.mp3",
#   "status": "processing"
# }
```

### 3. Check Meeting Status

```bash
curl http://localhost:8000/api/meetings/{meeting_id}

# Will show processing status and results when complete
```

### 4. Use Web UI

1. Go to http://localhost:5173
2. Drag and drop an audio file or click to select
3. Click "Upload & Analyze"
4. Wait for processing
5. View results in dashboard

---

## 🐛 Troubleshooting

### Backend Issues

#### "ModuleNotFoundError: No module named 'app'"

Make sure you're running from the backend directory:
```bash
cd backend
uvicorn app.main:app --reload
```

#### "ImportError: cannot import name 'Pipeline' from 'pyannote.audio'"

This means pyannote.audio didn't install correctly. Try reinstalling:
```bash
pip install --upgrade pyannote.audio
```

#### "GEMINI_API_KEY not found"

Ensure `.env` file exists and contains:
```
GEMINI_API_KEY=your-actual-key
```

#### "Connection refused" when uploading

Make sure backend is running on port 8000:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Issues

#### "Cannot find module 'react'" or similar

Reinstall dependencies:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### "VITE_API_BASE_URL is not defined"

Create `.env` file in frontend directory:
```bash
cd frontend
cp .env.example .env
```

#### Blank page or components not showing

Check browser console (F12) for errors. Common issues:
- Backend not running (check http://localhost:8000/api/health)
- CORS issues (check backend CORS configuration)
- Missing environment variables

### Processing Issues

#### "Unable to generate a reliable transcript"

Audio quality is poor. Try:
- Using higher quality audio
- Ensuring speakers speak clearly
- Reducing background noise

#### "Processing timeout"

Meeting is too long or system is slow. Gemini audio processing can take time for long recordings.

#### "Diarization model not available"

pyannote.audio model failed to load. You'll need:
1. Hugging Face account (free)
2. Accept model license on Hugging Face
3. Replace "hf_token_here" in `backend/app/services/diarization.py` with your token

Get your token from: https://huggingface.co/settings/tokens

---

## 📦 Production Deployment

### Docker Setup (Optional)

Create `Dockerfile` in root:

```dockerfile
# Backend
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t meeting-insights-backend .
docker run -p 8000:8000 --env-file .env meeting-insights-backend
```

### Environment Setup for Production

1. Use a real database (SQLite, PostgreSQL)
2. Enable HTTPS
3. Set appropriate CORS origins
4. Use secrets manager for API keys
5. Set up logging and monitoring
6. Configure rate limiting
7. Use environment-specific configs

---

## 📊 Project Structure Verification

After setup, verify your project looks like this:

```
meeting-insights-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── endpoints.py
│   │   ├── services/
│   │   │   ├── transcription.py
│   │   │   ├── diarization.py
│   │   │   ├── llm_analysis.py
│   │   │   ├── speaker_stats.py
│   │   │   └── file_handler.py
│   │   ├── utils/
│   │   │   ├── validation.py
│   │   │   ├── error_handler.py
│   │   │   └── helpers.py
│   │   ├── config.py
│   │   ├── models.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── .env
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── .env
│   └── .env.example
└── README.md
```

---

## ✅ Next Steps

1. **Upload a test meeting** to verify end-to-end flow
2. **Check logs** in backend terminal for any errors
3. **Review results** in dashboard UI
4. **Customize** components as needed
5. **Deploy** to production when ready

---

## 📚 Additional Resources

- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev)
- [Gemini Audio Understanding](https://ai.google.dev/gemini-api/docs/audio)
- [pyannote.audio Docs](https://github.com/pyannote/pyannote-audio)

---

**Need help?** Check the README.md for more details about the architecture and features.

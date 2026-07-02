# 🤖 Autonomous AI Interviewer

An intelligent AI-powered interview system that conducts conversational technical interviews, evaluates candidates in real-time, and generates comprehensive hiring reports. Features a conversational interface with voice support.

---

## 📋 Table of Contents

- [What This Project Does](#what-this-project-does)
- [Technologies Used](#technologies-used)
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [API Endpoints](#api-endpoints)
- [Architecture](#architecture)

---

## 🎯 What This Project Does

This system automates the entire technical interview process:

1. **Analyzes Resumes** - Upload a PDF/DOCX resume and AI extracts skills, experience, and projects
2. **Generates Personalized Questions** - Creates interview questions tailored to the candidate's background
3. **Conducts Conversational Interviews** - ChatGPT-style chat interface with voice or text input
4. **Evaluates Answers in Real-Time** - AI scores each answer across 5 dimensions instantly
5. **Provides Intelligent Follow-ups** - Generates probing questions based on answers
6. **Makes Hiring Decisions** - Produces comprehensive reports with hire/reject recommendations

---

## 💻 Technologies Used

### **Backend**
| Technology | Purpose | Version |
|-----------|---------|---------|
| **Python** | Core language | 3.11+ |
| **Flask** | REST API framework | 3.0.0 |
| **SQLAlchemy** | ORM for database | 2.0.23 |
| **PostgreSQL** | Primary database | 12+ |
| **Pydantic** | Data validation | 2.5.0 |

### **AI & Machine Learning**
| Technology | Purpose | Usage |
|-----------|---------|-------|
| **Google Gemini API** | LLM for analysis/evaluation | Resume parsing, question generation, answer evaluation |
| **OpenAI Whisper** | Speech-to-text | Voice answer transcription |
| **ChromaDB** | Vector database | Interview context & memory |
| **sentence-transformers** | Text embeddings | Semantic search (all-MiniLM-L6-v2) |

### **Frontend**
| Technology | Purpose | Usage |
|-----------|---------|-------|
| **Streamlit** | Web interface | Conversational chat UI |
| **gTTS** | Text-to-speech | Reading questions aloud |
| **streamlit-audiorec** | Audio recording | Voice answer capture |

### **Document Processing**
| Technology | Purpose | Usage |
|-----------|---------|-------|
| **PyMuPDF** | PDF parsing | Resume text extraction |
| **pdfplumber** | PDF fallback | Backup PDF parser |
| **python-docx** | DOCX parsing | Word document resumes |
| **ReportLab** | PDF generation | Interview report creation |

### **Development Tools**
- **Werkzeug** - WSGI utilities
- **python-dotenv** - Environment configuration
- **requests** - HTTP client (frontend to backend)

---

## ✨ Features

### 🎤 **Conversational Interview (ChatGPT-Style)**
- Natural chat interface with conversation bubbles
- Smooth transitions between questions ("Great answer! Let me ask...")
- Clear turn-taking indicators
- Real-time progress tracking
- Interview history in scrollable chat

### 🔊 **Audio Support**
- **Questions Read Aloud**: Automatic text-to-speech for questions
- **Voice Answers**: Record answers using microphone
- **Text Answers**: Type answers as alternative
- **Audio Toggle**: Turn audio on/off anytime

### 📄 **Resume Analysis**
- Supports PDF and DOCX formats
- Extracts: name, email, skills, experience, projects
- AI-powered skill classification
- Categories: Programming Languages, Frameworks, Databases, Tools, etc.

### 🎯 **Intelligent Question Generation**
- Personalized based on candidate's resume
- Multiple question types:
  - Technical (40%)
  - Project-based (20%)
  - Problem-solving (20%)
  - System design (10%)
  - Behavioral (10%)
- Difficulty levels: Easy, Medium, Hard
- 15 questions per interview

### 📊 **Multi-Dimensional Scoring**
Each answer scored on 5 dimensions (0-10):
- **Technical Score**: Technical correctness
- **Communication Score**: Clarity & articulation
- **Problem-Solving Score**: Analytical thinking
- **Confidence Score**: Conviction in answers
- **Depth Score**: Understanding depth

### 💡 **Smart Follow-up Questions**
- Context-aware probing questions
- Generated based on answer quality
- Explores weak areas or interesting points

### 🧠 **Interview Memory (Vector Database)**
- Stores interview context in ChromaDB
- Remembers previous Q&A for context
- Prevents repetitive questions
- Enables intelligent follow-ups

### 📈 **Real-Time Feedback**
- Immediate score after each answer
- Strengths highlighted
- Areas for improvement noted
- Overall interview progress shown

### 📑 **Comprehensive Reports**
- Overall performance score (0-100)
- Score breakdown by dimension
- Hiring recommendation:
  - Strong Hire (90-100)
  - Hire (75-89)
  - Borderline (60-74)
  - Reject (Below 60)
- Strengths and weaknesses summary
- Question-by-question analysis
- JSON and PDF formats

---

## 📁 Project Structure

```
autonomous_ai_interviewer/
│
├── app.py                          # Flask application entry point
├── config.py                       # Configuration settings
├── streamlit_app.py                # Streamlit frontend (ChatGPT-style UI)
├── init_db.py                      # Database initialization script
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (API keys, DB URL)
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── run_streamlit.bat              # Quick start script for Streamlit
│
├── database/
│   ├── db.py                      # Database connection & session management
│   └── models.py                  # SQLAlchemy models (7 tables)
│
├── routes/
│   ├── resume_routes.py           # POST /api/upload-resume
│   ├── interview_routes.py        # Interview endpoints (start, questions, evaluate)
│   └── report_routes.py           # Report generation endpoints
│
├── services/
│   ├── gemini_service.py          # Google Gemini API integration
│   ├── resume_parser.py           # Resume PDF/DOCX parsing
│   ├── skill_extractor.py         # AI skill extraction & classification
│   ├── interview_engine.py        # Main interview orchestration
│   ├── question_generator.py      # AI question generation
│   ├── answer_evaluator.py        # AI answer evaluation & scoring
│   ├── followup_generator.py      # AI follow-up question generation
│   ├── speech_to_text.py          # Whisper integration for voice
│   ├── vector_store.py            # ChromaDB for interview memory
│   ├── scoring_engine.py          # Scoring calculations & recommendations
│   └── report_generator.py        # PDF report generation
│
├── prompts/
│   ├── resume_analysis.txt        # Prompt for resume parsing
│   ├── skill_extraction.txt       # Prompt for skill classification
│   ├── question_generation.txt    # Prompt for question generation
│   ├── answer_evaluation.txt      # Prompt for answer evaluation
│   ├── followup_generation.txt    # Prompt for follow-up questions
│   ├── hiring_decision.txt        # Prompt for hiring recommendation
│   └── report_generation.txt      # Prompt for report summary
│
├── uploads/                       # Uploaded resume files
├── audio/                         # Recorded audio files
├── reports/                       # Generated PDF reports
├── chroma_db/                     # ChromaDB vector storage
├── logs/                          # Application logs
└── venv/                          # Virtual environment
```

---

## 🔧 Prerequisites

Before you begin, ensure you have:

- ✅ **Python 3.11 or higher** ([Download](https://www.python.org/downloads/))
- ✅ **PostgreSQL 12 or higher** ([Download](https://www.postgresql.org/download/))
- ✅ **Google Gemini API Key** ([Get Free Key](https://makersuite.google.com/app/apikey))
- ✅ **Git** (optional, for cloning)

---

## 🚀 Installation & Setup

### **Step 1: Clone or Download Project**

```bash
cd autonomous_ai_interviewer
```

---

### **Step 2: Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate
```

---

### **Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

**What gets installed:**
- Flask (backend framework)
- SQLAlchemy (database ORM)
- Google Gemini SDK
- Whisper (speech recognition)
- ChromaDB (vector database)
- Streamlit (frontend)
- Document parsers (PyMuPDF, pdfplumber, python-docx)
- ReportLab (PDF generation)
- gTTS (text-to-speech)
- And more...

---

### **Step 4: Set Up PostgreSQL Database**

#### **Create Database:**

```bash
# Open PostgreSQL command line
psql -U postgres

# Create database
CREATE DATABASE ai_interviewer;

# Exit
\q
```

#### **Or use pgAdmin:**
1. Open pgAdmin
2. Right-click "Databases" → "Create" → "Database"
3. Name: `ai_interviewer`
4. Click "Save"

---

### **Step 5: Configure Environment Variables**

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ai_interviewer

# Google Gemini API Key
GEMINI_API_KEY=your-gemini-api-key-here

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True
```

**How to get Gemini API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy and paste into `.env` file

---

### **Step 6: Initialize Database**

Run this to create all tables:

```bash
python init_db.py
```

**This creates 7 tables:**
- `candidates` - Candidate information
- `resumes` - Resume files and metadata
- `skills` - Extracted skills
- `interview_sessions` - Interview sessions
- `questions` - Interview questions
- `answers` - Candidate answers with scores
- `reports` - Interview reports

---

## ▶️ How to Run

### **Method 1: Using Streamlit Frontend (Recommended)**

#### **Terminal 1: Start Backend**
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run Flask backend
python app.py
```

You should see:
```
* Running on http://127.0.0.1:5000
```

#### **Terminal 2: Start Frontend**
```bash
# Activate virtual environment (in new terminal)
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run Streamlit
streamlit run streamlit_app.py
```

**Or use the batch file (Windows):**
```bash
run_streamlit.bat
```

Your browser will open to: `http://localhost:8501`

---

### **Method 2: Using API Directly**

Start only the backend:

```bash
python app.py
```

Then use tools like Postman, curl, or Python requests to call the API.

---

## 🌐 API Endpoints

### **Resume Upload**

```http
POST /api/upload-resume
Content-Type: multipart/form-data

file: [resume.pdf or resume.docx]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "candidate": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "experience_years": 5
    },
    "skills": [
      {"skill_name": "Python", "category": "Programming Languages"},
      {"skill_name": "React", "category": "Frameworks"}
    ]
  }
}
```

---

### **Start Interview**

```http
POST /api/start-interview
Content-Type: application/json

{
  "candidate_id": 1
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session": {"id": 1, "status": "in_progress"},
    "total_questions": 15,
    "first_question": {
      "id": 1,
      "question_text": "Explain decorators in Python",
      "difficulty": "medium"
    }
  }
}
```

---

### **Get Next Question**

```http
GET /api/next-question?session_id=1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "question": {
      "id": 2,
      "question_text": "What is your experience with React hooks?",
      "difficulty": "medium"
    },
    "has_more_questions": true
  }
}
```

---

### **Transcribe Audio (Voice Answer)**

```http
POST /api/transcribe
Content-Type: multipart/form-data

audio: [audio.wav]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transcript": "Decorators are a design pattern that allows..."
  }
}
```

---

### **Evaluate Answer**

```http
POST /api/evaluate-answer
Content-Type: application/json

{
  "question_id": 1,
  "transcript": "Decorators are a design pattern that allows..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "evaluation": {
      "technical_score": 8.5,
      "communication_score": 7.5,
      "problem_solving_score": 8.0,
      "confidence_score": 7.0,
      "depth_score": 8.5,
      "strengths": ["Clear explanation", "Good examples"],
      "weaknesses": ["Could mention closure concept"]
    },
    "followup_questions": [
      {
        "question_text": "Can you explain a practical use case?",
        "difficulty": "medium"
      }
    ]
  }
}
```

---

### **Get Interview Status**

```http
GET /api/interview-status/1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "progress": {
      "total_questions": 15,
      "answered_questions": 8,
      "remaining_questions": 7,
      "completion_percentage": 53.33
    }
  }
}
```

---

### **Get Report (JSON)**

```http
GET /api/report/1
```

**Response:**
```json
{
  "success": true,
  "data": {
    "report": {
      "performance_metrics": {
        "overall_score": 78.5,
        "technical_score": 80.0,
        "communication_score": 75.0,
        "problem_solving_score": 77.0,
        "confidence_score": 74.0,
        "depth_score": 76.5
      },
      "hiring_recommendation": {
        "recommendation": "hire",
        "confidence": "high",
        "summary": "Strong technical candidate with good communication skills",
        "strengths": [
          "Deep technical knowledge",
          "Clear communication",
          "Good problem-solving approach"
        ],
        "weaknesses": [
          "Limited system design experience",
          "Could improve confidence in explanations"
        ]
      }
    }
  }
}
```

---

### **Download Report (PDF)**

```http
GET /api/download-report/1
```

Returns a PDF file with comprehensive interview report.

---

## 🏗️ Architecture

### **System Flow:**

```
┌─────────────┐
│   Resume    │
│   Upload    │
└──────┬──────┘
       │
       v
┌─────────────┐      ┌──────────────┐
│   Gemini    │<─────│   Resume     │
│     API     │      │   Parser     │
└──────┬──────┘      └──────────────┘
       │
       v
┌─────────────┐      ┌──────────────┐
│   Skills    │──────>│  PostgreSQL  │
│ Extraction  │      │   Database   │
└─────────────┘      └──────────────┘
       │
       v
┌─────────────┐
│  Question   │
│ Generation  │
└──────┬──────┘
       │
       v
┌─────────────┐      ┌──────────────┐
│ Streamlit   │<─────>│    Flask     │
│  Frontend   │      │   Backend    │
└──────┬──────┘      └──────┬───────┘
       │                     │
       v                     v
┌─────────────┐      ┌──────────────┐
│   Voice     │      │   ChromaDB   │
│   Input     │      │   (Memory)   │
└──────┬──────┘      └──────────────┘
       │
       v
┌─────────────┐
│   Whisper   │
│  (STT API)  │
└──────┬──────┘
       │
       v
┌─────────────┐      ┌──────────────┐
│   Answer    │──────>│   Scoring    │
│ Evaluation  │      │    Engine    │
└─────────────┘      └──────┬───────┘
                             │
                             v
                      ┌──────────────┐
                      │   Report     │
                      │ Generation   │
                      └──────────────┘
```

### **Database Schema:**

```sql
candidates
  - id (PK)
  - name
  - email
  - experience_years

resumes
  - id (PK)
  - candidate_id (FK)
  - file_name
  - raw_text

skills
  - id (PK)
  - resume_id (FK)
  - skill_name
  - category

interview_sessions
  - id (PK)
  - candidate_id (FK)
  - status (in_progress, completed)
  - overall_score

questions
  - id (PK)
  - session_id (FK)
  - question_text
  - difficulty
  - question_type

answers
  - id (PK)
  - question_id (FK)
  - transcript
  - technical_score
  - communication_score
  - problem_solving_score
  - confidence_score
  - depth_score

reports
  - id (PK)
  - session_id (FK)
  - report_data (JSON)
  - pdf_path
```

---

## 📝 .gitignore

The project includes a `.gitignore` file that excludes:

```gitignore
# Virtual Environment
venv/
env/
ENV/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# Environment Variables
.env
.env.local

# Database
*.db
*.sqlite3

# Uploads & Generated Files
uploads/*
!uploads/.gitkeep
audio/*
!audio/.gitkeep
reports/*
!reports/.gitkeep
logs/*.log

# ChromaDB
chroma_db/*
!chroma_db/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Distribution
build/
dist/
*.egg-info/
```

---

## 🎓 Usage Guide

### **For Candidates:**

1. **Upload Resume**: Drag and drop your PDF/DOCX resume
2. **Start Interview**: Click "Start Interview" button
3. **Answer Questions**: Choose voice or text input
4. **Get Feedback**: See your score after each answer
5. **View Results**: Check comprehensive report when done

### **For Interviewers/Companies:**

1. Set up the system on your server
2. Candidates access via web browser
3. Review generated reports
4. Make hiring decisions based on AI recommendations

---

## 🐛 Troubleshooting

### **Backend won't start:**
- Check PostgreSQL is running
- Verify `.env` file has correct `DATABASE_URL`
- Ensure port 5000 is not in use

### **Gemini API errors:**
- Check API key in `.env`
- Verify internet connection
- Check API quota at Google AI Studio

### **Audio transcription not working:**
- Backend must be running
- Check microphone permissions in browser
- Fallback: use text input instead

### **Database errors:**
- Run `python init_db.py` again
- Check PostgreSQL connection
- Verify database name is `ai_interviewer`

---

## 📄 License

This project is for educational and portfolio demonstration purposes.

## 👤 Author

Created as a demonstration of AI engineering capabilities.

---

## 🚀 Quick Start Commands

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate environment
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python init_db.py

# 5. Start backend
python app.py

# 6. Start frontend (new terminal)
streamlit run streamlit_app.py
```

**Access at:** `http://localhost:8501`

---

**Happy Interviewing! 🎉**
# AI-Recruiter-Bot-

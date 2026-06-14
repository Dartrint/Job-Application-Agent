# 🤖 Job Application Multi-Agent System

A production-grade multi-agent AI system for optimizing job applications using **LangGraph** orchestration and **Groq** LLMs. Works with both CLI and interactive Streamlit web interface.

**Features:**
- 📋 **Job Analyzer** - Extracts requirements and skills from job postings
- 📊 **CV Optimizer** - Analyzes CV match and suggests improvements  
- 🎤 **Interview Prep** - Generates technical, behavioral, and system design questions
- ✍️ **Cover Letter Generator** - Creates personalized cover letter variations
- 🌐 **Web UI** - Interactive Streamlit interface for easy file uploads
- 📝 **CLI** - Command-line interface with JSON output

## 🚀 Quick Start (5 minutes)

### 1. Get Groq API Key (FREE - No Credit Card)

1. Visit https://console.groq.com/
2. Sign up and create API key (takes 2 minutes)
3. Keep your key safe

### 2. Setup

```bash
# Clone/navigate to project
cd job-application-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
cp .env.example .env
# Edit .env and add: GROQ_API_KEY=your_key_here
```

### 3. Run (Choose One)

**Option A: Web Interface (Recommended)**
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

**Option B: CLI with Sample Data**
```bash
python main.py --demo
```

**Option C: CLI with Your Files**
```bash
python main.py your_job_description.pdf your_cv.pdf
```
Supported formats: `.pdf`, `.docx`, `.txt`

## 📖 How to Use

### Web Interface (Streamlit)
1. Open http://localhost:8501
2. Toggle "Use Sample Data" or upload your files
3. Click "🚀 Analyze Application"
4. View results in tabs: Job Profile, CV Match, Interview Prep, Cover Letter
5. Download results as JSON

### CLI
```bash
# Run with sample data
python main.py --demo

# Run with files
python main.py job_description.txt resume.txt

# Show help
python main.py --help
```

Results are saved to `results.json` with all analysis.

## 📊 What You Get

### Job Profile Analysis
- Position, company, seniority level
- Required and nice-to-have skills
- Key responsibilities

### CV Match Score
- Match percentage (0-100%)
- Your matching skills
- Missing skills to improve
- Specific improvement suggestions

### Interview Preparation
- 5+ Technical Q&A
- 5+ Behavioral Q&A  
- 3+ System design questions
- Duration estimate
- Pro tips and tricks

### Cover Letter
- Primary tailored version
- 2+ variations for different styles
- HTML export option

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│    LangGraph State Machine              │
├─────────────────────────────────────┤
│ START                                   │
│   ↓                                      │
│ Job Analyzer                            │
│   ↓                                     │
│ CV Optimizer                             │
│   ↓                                     │
│ Interview Prep                          │
│   ↓                                     │
│ Cover Letter Generator                  │
│   ↓                                     │
│ Report Builder → Email (optional)      │
│   ↓                                     │
│  END                                    │
└─────────────────────────────────────┘
         ↓
    Groq API (Free)
    LLaMA 3.3 70B
```

## 🤖 Automation & Email Reports

After each analysis, the system can automatically save HTML/JSON reports to `reports/` and email them.

### 1. Configure email in `.env`

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password      # Gmail: use App Password
REPORT_EMAIL_TO=recipient@example.com
AUTO_SEND_REPORT=false               # set true to always email from CLI
```

### 2. Run automation CLI

```bash
# Analyze + save reports to reports/
python automation.py --demo

# Analyze + save reports + send email
python automation.py --demo --email

# Custom recipient
python automation.py examples/sample_job.txt examples/sample_cv.txt --email-to you@example.com
```

### 3. CLI / Web UI

```bash
python main.py --demo --email
streamlit run app.py   # enable "Send report to email" in sidebar when SMTP is configured
```

## 📁 Project Structure

```
job-application-agent/
├── app.py                      # Streamlit web UI
├── main.py                     # CLI entry point
├── automation.py               # Automation CLI (report + email)
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
├── README.md                  # This file
│
├── src/
│   ├── config.py              # Configuration
│   ├── state.py               # Pydantic models
│   ├── orchestrator.py        # LangGraph workflow
│   ├── automation.py          # Workflow + report + email pipeline
│   ├── sample_data.py         # Shared demo data
│   ├── agents/
│   │   ├── job_analyzer.py    # Parse job posting
│   │   ├── cv_optimizer.py    # Analyze CV match
│   │   ├── interview_prep.py  # Generate Q&A
│   │   └── cover_letter.py    # Generate letter
│   ├── templates/
│   │   └── report.html.j2     # HTML report template
│   ├── utils/
│   │   └── llm_utils.py       # LLM JSON parsing helpers
│   └── tools/
│       ├── file_processor.py  # PDF/DOCX handling
│       ├── report_builder.py  # HTML/JSON reports
│       └── email_sender.py    # SMTP delivery
│
└── tests/
    ├── conftest.py
    ├── test_enhanced.py
    └── test_automation.py
```

## 🧪 Testing

### Test the Workflow
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_enhanced.py -v

# Run CLI demo
python main.py --demo
```

### Manual Testing Checklist

**CLI:**
- ✅ Demo mode runs without errors
- ✅ Generates results.json
- ✅ All 4 agents complete successfully

**Web UI:**
- ✅ Streamlit app starts on http://localhost:8501
- ✅ Sample data loads correctly
- ✅ File upload works for PDF/DOCX/TXT
- ✅ Analysis produces all 4 components
- ✅ Results tabs display correctly
- ✅ JSON export works

**Output Quality:**
- ✅ Job analysis extracts required skills
- ✅ CV match score is reasonable (0-100%)
- ✅ Interview questions are relevant
- ✅ Cover letter is personalized

## ⚙️ Configuration

Edit `src/config.py` to customize:

```python
# LLM Model (fast and free)
GROQ_MODEL = "llama-3.3-70b-versatile"

# Response creativity (0.0=precise, 1.0=creative)
GROQ_TEMPERATURE = 0.7

# Timeout per agent (seconds)
AGENT_TIMEOUT = 30

# Total workflow timeout (seconds)
TOTAL_TIMEOUT = 300
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `GROQ_API_KEY not found` | Ensure `.env` file exists with your API key |
| `Failed to parse JSON response` | Try increasing GROQ_TEMPERATURE in config.py |
| `Slow responses` | Groq free tier has ~30 req/min limit. Wait 1-2 minutes. |
| `Memory errors on large files` | Trim CV/JD to relevant sections (max 10MB) |
| `Streamlit port already in use` | Run: `streamlit run app.py --server.port 8502` |
| `Unicode error in CLI output` | Set: `$env:PYTHONIOENCODING = 'utf-8'` (PowerShell) |

## 📊 Sample Output Format

```json
{
  "workflow_id": "4089c9f1-c008-4f2a-8c26-a0a212795e1e",
  "timestamp": "2026-06-03T23:11:47.478000",
  "status": {
    "job_analysis": "OK",
    "cv_analysis": "OK",
    "interview_prep": "OK",
    "cover_letter": "OK"
  },
  "job_profile": {
    "title": "Senior AI/ML Engineer",
    "company": "TechCorp AI",
    "seniority_level": "Senior",
    "required_skills": ["Python", "LangChain", "RAG", ...],
    "nice_to_have_skills": ["Open source", "Research", ...]
  },
  "cv_analysis": {
    "experience_years": 6,
    "improvement_score": 85,
    "matching_skills": ["Python", "LangChain", "RAG"],
    "missing_skills": ["Kubernetes"],
    "suggestions": ["Add Kubernetes experience", ...]
  },
  "interview_guide": {
    "technical_questions": [...],
    "behavioral_questions": [...],
    "system_design_questions": [...],
    "estimated_duration_minutes": 60,
    "tips_and_tricks": [...]
  },
  "cover_letter": {
    "primary_version": "Dear Hiring Manager...",
    "variations": [...]
  }
}
```




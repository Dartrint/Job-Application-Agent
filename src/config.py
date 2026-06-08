"""Job Application Agent System - Configuration Module"""

import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# Groq Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.7

# Application Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DEMO_MODE = os.getenv("DEMO_MODE", "True").lower() == "true"

# Timeouts
AGENT_TIMEOUT = 30
TOTAL_TIMEOUT = 300

# Model Parameters
MAX_TOKENS = 2048
TOP_P = 0.95

# Email / Automation
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
REPORT_EMAIL_FROM = os.getenv("REPORT_EMAIL_FROM", SMTP_USER)
REPORT_EMAIL_TO = os.getenv("REPORT_EMAIL_TO", "")
AUTO_SEND_REPORT = os.getenv("AUTO_SEND_REPORT", "false").lower() == "true"
EMAIL_ENABLED = bool(SMTP_HOST and SMTP_USER and SMTP_PASSWORD and REPORT_EMAIL_TO)


class AgentType(str, Enum):
    """Available agent types in the system"""
    JOB_ANALYZER = "job_analyzer"
    CV_OPTIMIZER = "cv_optimizer"
    INTERVIEW_PREP = "interview_prep"
    COVER_LETTER = "cover_letter"


if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY not found. Please set it in .env file or environment variables."
    )

"""Job Application Agent System"""

__version__ = "1.0.0"
__author__ = "AI Engineering Portfolio"

from src.config import GROQ_API_KEY, GROQ_MODEL
from src.state import ApplicationState, JobProfile, CVAnalysis, InterviewGuide, CoverLetterDraft

__all__ = [
    "ApplicationState",
    "JobProfile",
    "CVAnalysis",
    "InterviewGuide",
    "CoverLetterDraft",
]

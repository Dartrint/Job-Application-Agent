"""State models for LangGraph workflow using Pydantic"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class QuestionAnswer(BaseModel):
    """Structured Q&A format"""
    question: str
    suggested_answer: Optional[str] = None
    difficulty: Optional[str] = None
    why_asked: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)  # Key concepts to mention


class SystemDesignQuestion(BaseModel):
    """System design question format"""
    question: str
    approach: Optional[str] = None
    hints: list[str] = Field(default_factory=list)


class CoverLetterVariation(BaseModel):
    """Single cover letter variation"""
    content: str
    tone: Optional[str] = None


class JobProfile(BaseModel):
    """Structured job posting analysis"""
    title: str
    company: str
    seniority_level: str
    required_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    compensation_range: Optional[str] = None
    location: Optional[str] = None
    employment_type: str = "Full-time"
    raw_text: str = ""


class CVAnalysis(BaseModel):
    """CV analysis and suggestions"""
    experience_years: float
    key_skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    matching_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    improvement_score: float = Field(ge=0, le=100)


class InterviewGuide(BaseModel):
    """Interview preparation guide"""
    technical_questions: list[QuestionAnswer] = Field(default_factory=list)
    behavioral_questions: list[QuestionAnswer] = Field(default_factory=list)
    system_design_questions: list[SystemDesignQuestion] = Field(default_factory=list)
    tips_and_tricks: list[str] = Field(default_factory=list)
    estimated_duration_minutes: int = 60
    interview_format: Optional[str] = None  # technical, behavioral, or mixed
    company_research: Optional[str] = None  # Key things to know about company
    success_factors: list[str] = Field(default_factory=list)  # Top factors for success


class CoverLetterDraft(BaseModel):
    """Cover letter variations"""
    primary_version: str
    variations: list[CoverLetterVariation] = Field(default_factory=list)
    key_narratives: list[str] = Field(default_factory=list)


class ApplicationState(BaseModel):
    """Main state for the entire application workflow"""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )

    # Input documents
    job_description: str = ""
    cv_text: str = ""
    user_profile: dict = Field(default_factory=dict)  # Background info, achievements, etc.
    language: str = "en"  # Language for content generation: "en" or "vi"

    # Processing metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    workflow_id: str = ""

    # Agent outputs
    job_profile: Optional[JobProfile] = None
    cv_analysis: Optional[CVAnalysis] = None
    interview_guide: Optional[InterviewGuide] = None
    cover_letter: Optional[CoverLetterDraft] = None

    # Status tracking
    job_analysis_completed: bool = False
    cv_analysis_completed: bool = False
    interview_prep_completed: bool = False
    cover_letter_completed: bool = False

    # Error tracking
    errors: list[str] = Field(default_factory=list)

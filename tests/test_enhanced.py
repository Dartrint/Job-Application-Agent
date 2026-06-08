"""Enhanced comprehensive test suite with file processing and structured types"""

import pytest
import json
import tempfile
from pathlib import Path
from src.orchestrator import JobApplicationOrchestrator, format_results
from src.state import (
    ApplicationState,
    JobProfile,
    CVAnalysis,
    InterviewGuide,
    QuestionAnswer,
    SystemDesignQuestion,
    CoverLetterDraft,
)
from src.tools.file_processor import (
    validate_file_size,
    get_file_info,
    extract_text_from_file,
)


@pytest.fixture
def orchestrator():
    """Initialize orchestrator"""
    return JobApplicationOrchestrator()


@pytest.fixture
def sample_job():
    """Sample job description"""
    return """
Senior AI/ML Engineer - San Francisco

Company: TechCorp AI
Location: San Francisco, CA

About the role:
We're looking for a Senior AI/ML Engineer to join our core platform team.

Key Responsibilities:
- Design and implement machine learning pipelines using LangChain
- Develop and optimize RAG systems
- Build production LLM applications

Required Skills:
- 5+ years of ML/AI engineering
- Strong Python expertise
- Experience with LLMs
- Knowledge of LangChain and LangGraph
- Vector database experience
"""


@pytest.fixture
def sample_cv():
    """Sample CV"""
    return """
John Doe
San Francisco, CA | john.doe@email.com

PROFESSIONAL SUMMARY
Experienced AI/ML Engineer with 6+ years building production ML systems.

EXPERIENCE

Senior ML Engineer | DataSystems Inc. (2022 - Present)
- Led development of LLM-powered chatbot using LangChain
- Designed and implemented RAG system for knowledge base retrieval
- Architected ML pipeline processing 1M+ documents daily

ML Engineer | CloudAI Corp. (2020 - 2022)
- Built recommendation engine using collaborative filtering
- Implemented prompt engineering strategies
- Created vector database infrastructure

TECHNICAL SKILLS
Languages: Python, SQL, JavaScript
ML/AI: LangChain, LangGraph, TensorFlow, PyTorch
Databases: PostgreSQL, MongoDB, Pinecone, ChromaDB
Cloud: AWS, Docker, Kubernetes
"""


class TestStructuredTypes:
    """Test new structured Q&A types"""

    def test_question_answer_creation(self):
        """Test QuestionAnswer model creation"""
        q = QuestionAnswer(
            question="What is RAG?",
            suggested_answer="RAG stands for...",
            difficulty="medium",
            why_asked="To assess knowledge",
        )
        assert q.question == "What is RAG?"
        assert q.difficulty == "medium"

    def test_system_design_question_creation(self):
        """Test SystemDesignQuestion model creation"""
        q = SystemDesignQuestion(
            question="Design a recommendation system",
            approach="Use collaborative filtering...",
            hints=["Consider scalability", "Think about data storage"],
        )
        assert q.question == "Design a recommendation system"
        assert len(q.hints) == 2

    def test_interview_guide_with_proper_types(self):
        """Test InterviewGuide with proper question objects"""
        guide = InterviewGuide(
            technical_questions=[
                QuestionAnswer(question="Q1", suggested_answer="A1"),
                QuestionAnswer(question="Q2", suggested_answer="A2"),
            ],
            behavioral_questions=[
                QuestionAnswer(question="Tell about your experience", suggested_answer="I have..."),
            ],
            system_design_questions=[
                SystemDesignQuestion(question="Design X", approach="Use Y"),
            ],
            tips_and_tricks=["Tip 1", "Tip 2"],
        )
        assert len(guide.technical_questions) == 2
        assert guide.technical_questions[0].question == "Q1"
        assert len(guide.system_design_questions) == 1


class TestFileProcessing:
    """Test file processing utilities"""

    def test_validate_file_size_valid(self):
        """Test file size validation for valid size"""
        assert validate_file_size(5 * 1024 * 1024) is True

    def test_validate_file_size_invalid(self):
        """Test file size validation for invalid size"""
        assert validate_file_size(15 * 1024 * 1024) is False

    def test_get_file_info(self):
        """Test getting file information"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content")
            tmp_path = tmp.name

        info = get_file_info(tmp_path)
        assert "name" in info
        assert "type" in info
        assert "size_bytes" in info
        assert info["size_bytes"] == 12

    def test_extract_text_from_txt(self):
        """Test extracting text from TXT file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
            tmp.write("Sample job description\n")
            tmp.write("Required skills: Python, SQL")
            tmp_path = tmp.name

        text = extract_text_from_file(tmp_path, "txt")
        assert "Sample job description" in text
        assert "Python" in text


class TestInputValidation:
    """Test input validation"""

    def test_empty_job_description_raises_error(self, orchestrator, sample_cv):
        """Test that empty job description raises ValueError"""
        with pytest.raises(ValueError, match="Job description cannot be empty"):
            orchestrator.process_application_sync(
                job_description="",
                cv_text=sample_cv,
                user_profile={"industry": "AI/ML"},
            )

    def test_empty_cv_raises_error(self, orchestrator, sample_job):
        """Test that empty CV raises ValueError"""
        with pytest.raises(ValueError, match="CV text cannot be empty"):
            orchestrator.process_application_sync(
                job_description=sample_job,
                cv_text="",
                user_profile={"industry": "AI/ML"},
            )

    def test_whitespace_only_job_description(self, orchestrator, sample_cv):
        """Test that whitespace-only job description raises error"""
        with pytest.raises(ValueError):
            orchestrator.process_application_sync(
                job_description="   \n\t  ",
                cv_text=sample_cv,
                user_profile={"industry": "AI/ML"},
            )

    def test_valid_inputs_accepted(self, orchestrator, sample_job, sample_cv):
        """Test that valid inputs are accepted"""
        result = orchestrator.process_application_sync(
            job_description=sample_job,
            cv_text=sample_cv,
            user_profile={"industry": "AI/ML", "years_experience": 6},
        )
        assert result is not None
        assert not isinstance(result, ValueError)


class TestWorkflowExecution:
    """Test workflow execution"""

    def test_workflow_initialization(self, orchestrator):
        """Test that orchestrator initializes without errors"""
        assert orchestrator is not None
        assert hasattr(orchestrator, "process_application_sync")

    def test_full_workflow_sync(self, orchestrator, sample_job, sample_cv):
        """Test complete workflow execution"""
        result = orchestrator.process_application_sync(
            job_description=sample_job,
            cv_text=sample_cv,
            user_profile={"industry": "AI/ML", "years_experience": 6},
        )

        assert result is not None
        assert isinstance(result, ApplicationState)

    def test_interview_guide_has_proper_types(self, orchestrator, sample_job, sample_cv):
        """Test that interview guide uses proper types"""
        result = orchestrator.process_application_sync(
            job_description=sample_job,
            cv_text=sample_cv,
            user_profile={"industry": "AI/ML", "years_experience": 6},
        )

        if result.interview_guide and result.interview_guide.technical_questions:
            first_q = result.interview_guide.technical_questions[0]
            assert isinstance(first_q, QuestionAnswer)
            assert hasattr(first_q, "question")
            assert hasattr(first_q, "suggested_answer")


class TestJobProfile:
    """Test job profile extraction"""

    def test_job_profile_structure(self, orchestrator, sample_job, sample_cv):
        """Test job profile has required fields"""
        result = orchestrator.process_application_sync(
            job_description=sample_job,
            cv_text=sample_cv,
            user_profile={"industry": "AI/ML", "years_experience": 6},
        )

        profile = result.job_profile
        if profile:
            assert hasattr(profile, "title")
            assert hasattr(profile, "company")
            assert hasattr(profile, "required_skills")


class TestCVAnalysis:
    """Test CV analysis"""

    def test_cv_analysis_structure(self, orchestrator, sample_job, sample_cv):
        """Test CV analysis has required fields"""
        result = orchestrator.process_application_sync(
            job_description=sample_job,
            cv_text=sample_cv,
            user_profile={"industry": "AI/ML", "years_experience": 6},
        )

        analysis = result.cv_analysis
        if analysis:
            assert hasattr(analysis, "improvement_score")
            assert 0 <= analysis.improvement_score <= 100


class TestResultsFormatting:
    """Test results formatting"""

    def test_format_results_creates_json(self, orchestrator, sample_job, sample_cv):
        """Test that results can be formatted as JSON"""
        result = orchestrator.process_application_sync(
            job_description=sample_job,
            cv_text=sample_cv,
            user_profile={"industry": "AI/ML", "years_experience": 6},
        )

        formatted = format_results(result)
        assert isinstance(formatted, dict)

    def test_formatted_results_serializable(self, orchestrator, sample_job, sample_cv):
        """Test that formatted results are JSON serializable"""
        result = orchestrator.process_application_sync(
            job_description=sample_job,
            cv_text=sample_cv,
            user_profile={"industry": "AI/ML", "years_experience": 6},
        )

        formatted = format_results(result)
        # Should not raise an exception
        json_str = json.dumps(formatted, default=str)
        assert isinstance(json_str, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

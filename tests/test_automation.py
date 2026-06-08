"""Tests for report builder, LLM utils, and email automation"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.state import ApplicationState, JobProfile, CVAnalysis
from src.utils.llm_utils import normalize_string_list, normalize_tips, parse_llm_json
from src.tools.report_builder import build_html_report, save_report_files


class TestLlmUtils:
    def test_parse_llm_json_plain(self):
        data = parse_llm_json('{"title": "Engineer"}')
        assert data["title"] == "Engineer"

    def test_parse_llm_json_with_extra_text(self):
        data = parse_llm_json('Here is JSON:\n{"score": 90}\nDone')
        assert data["score"] == 90

    def test_normalize_string_list_mixed(self):
        items = ["Plain text", {"degree": "BS CS", "university": "Berkeley"}]
        result = normalize_string_list(items)
        assert result[0] == "Plain text"
        assert "BS CS" in result[1]

    def test_normalize_tips(self):
        tips = ["Tip one", {"tip": "Tip two"}]
        assert normalize_tips(tips) == ["Tip one", "Tip two"]


class TestReportBuilder:
    @pytest.fixture
    def sample_formatted(self):
        return {
            "workflow_id": "test-workflow",
            "status": {
                "job_analysis": "OK",
                "cv_analysis": "OK",
                "interview_prep": "OK",
                "cover_letter": "OK",
            },
            "errors": [],
            "job_profile": {
                "title": "Senior Engineer",
                "company": "TechCorp",
                "seniority_level": "Senior",
                "required_skills": ["Python"],
                "responsibilities": ["Build ML pipelines"],
            },
            "cv_analysis": {
                "improvement_score": 85,
                "experience_years": 5,
                "matching_skills": ["Python"],
                "missing_skills": [],
                "suggestions": ["Add metrics"],
            },
            "interview_guide": {
                "technical_questions": [
                    {"question": "What is RAG?", "suggested_answer": "Retrieval augmented generation"}
                ],
                "behavioral_questions": [],
                "system_design_questions": [],
                "tips_and_tricks": ["Review the job description"],
                "estimated_duration_minutes": 90,
                "interview_format": "mixed",
                "company_research": "AI-first company",
                "success_factors": ["Strong Python skills"],
            },
            "cover_letter": {
                "primary_version": "Dear Hiring Manager...",
                "variations": [],
                "key_narratives": ["ML experience"],
            },
        }

    def test_build_html_report(self, sample_formatted):
        html = build_html_report(sample_formatted)
        assert "Senior Engineer" in html
        assert "TechCorp" in html
        assert "85" in html

    def test_save_report_files(self, sample_formatted, tmp_path):
        paths = save_report_files(sample_formatted, output_dir=tmp_path)
        assert paths["html"].exists()
        assert paths["json"].exists()
        saved = json.loads(paths["json"].read_text(encoding="utf-8"))
        assert saved["workflow_id"] == "test-workflow"


class TestEmailSender:
    def test_send_report_email_mock(self, tmp_path):
        from src.tools import email_sender

        html_file = tmp_path / "report.html"
        html_file.write_text("<html><body>Report</body></html>", encoding="utf-8")

        with patch.object(email_sender, "EMAIL_ENABLED", True), patch.object(
            email_sender, "SMTP_HOST", "smtp.test.com"
        ), patch.object(email_sender, "SMTP_PORT", 587), patch.object(
            email_sender, "SMTP_USER", "user@test.com"
        ), patch.object(
            email_sender, "SMTP_PASSWORD", "secret"
        ), patch.object(
            email_sender, "REPORT_EMAIL_TO", "to@test.com"
        ), patch.object(
            email_sender, "REPORT_EMAIL_FROM", "user@test.com"
        ), patch.object(
            email_sender, "SMTP_USE_TLS", True
        ), patch(
            "src.tools.email_sender.smtplib.SMTP"
        ) as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            email_sender.send_report_email(
                html_body=html_file.read_text(encoding="utf-8"),
                subject="Test Report",
                attachments={"html": html_file},
            )

            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.sendmail.assert_called_once()

    def test_send_email_not_configured(self):
        from src.tools.email_sender import send_report_email

        with patch("src.tools.email_sender.EMAIL_ENABLED", False):
            with pytest.raises(ValueError, match="Email is not configured"):
                send_report_email("<p>test</p>", "Subject")

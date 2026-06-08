"""End-to-end automation: analyze, report, and email delivery"""

import logging
import time
from pathlib import Path

from src.orchestrator import JobApplicationOrchestrator, format_results
from src.sample_data import load_sample_data
from src.state import ApplicationState
from src.tools.email_sender import is_email_configured, send_report_email
from src.tools.file_processor import extract_text_from_file, validate_file_size
from src.tools.report_builder import save_report_files

logger = logging.getLogger(__name__)


class JobApplicationAutomation:
    """Runs the workflow and optionally delivers reports by email."""

    def __init__(self):
        self.orchestrator = JobApplicationOrchestrator()

    def run(
        self,
        job_description: str,
        cv_text: str,
        user_profile: dict | None = None,
        send_email: bool = False,
        email_to: str | None = None,
        output_dir: Path | None = None,
        save_reports: bool = True,
    ) -> dict:
        """
        Execute workflow, save reports, and optionally email results.

        Returns dict with keys: state, formatted, report_paths, email_sent, elapsed_seconds
        """
        start = time.time()
        state = self.orchestrator.process_application_sync(
            job_description=job_description,
            cv_text=cv_text,
            user_profile=user_profile or {},
        )
        formatted = format_results(state)
        report_paths = {}
        if save_reports:
            report_paths = save_report_files(formatted, state, output_dir=output_dir)

        email_sent = False
        if send_email:
            if not report_paths.get("html"):
                raise ValueError("Cannot send email without a saved HTML report")
            job_title = (state.job_profile.title if state.job_profile else "Job Application")
            company = (state.job_profile.company if state.job_profile else "Analysis")
            subject = f"Job Application Report — {job_title} @ {company}"
            html_body = report_paths["html"].read_text(encoding="utf-8")
            send_report_email(
                html_body=html_body,
                subject=subject,
                to_address=email_to,
                attachments=report_paths,
            )
            email_sent = True

        elapsed = time.time() - start
        return {
            "state": state,
            "formatted": formatted,
            "report_paths": report_paths,
            "email_sent": email_sent,
            "elapsed_seconds": elapsed,
        }

    @staticmethod
    def load_inputs_from_files(jd_path: str, cv_path: str) -> tuple[str, str]:
        """Load job description and CV text from supported file paths."""
        jd = Path(jd_path)
        cv = Path(cv_path)

        if not jd.exists():
            raise FileNotFoundError(f"Job description file not found: {jd_path}")
        if not cv.exists():
            raise FileNotFoundError(f"CV file not found: {cv_path}")

        for path in (jd, cv):
            if not validate_file_size(path.stat().st_size):
                raise ValueError(f"File too large (max 10MB): {path.name}")

        job_text = extract_text_from_file(str(jd), jd.suffix[1:].lower())
        cv_text = extract_text_from_file(str(cv), cv.suffix[1:].lower())
        return job_text, cv_text

    @staticmethod
    def load_demo_inputs() -> tuple[str, str]:
        return load_sample_data()

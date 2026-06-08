"""Main entry point for Job Application Agent"""

import json
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.automation import JobApplicationAutomation
from src.config import AUTO_SEND_REPORT, REPORT_EMAIL_TO
from src.sample_data import load_sample_data
from src.tools.email_sender import is_email_configured
from src.tools.file_processor import extract_text_from_file, validate_file_size

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def print_usage():
    """Print usage information"""
    print("""
Usage: python main.py [options]

Options:
  --demo                    Run with sample data (default)
  --help                    Show this help message
  --email                   Send HTML report to REPORT_EMAIL_TO after analysis
  --email-to ADDRESS        Override recipient email address
  --no-report               Skip saving report files to reports/
  <jd_file> <cv_file>       Process with external files
                            Supported formats: .pdf, .docx, .doc, .txt

Examples:
  python main.py --demo
  python main.py --demo --email
  python main.py job_description.pdf resume.pdf --email-to you@example.com
  python automation.py --demo --email
""")


def load_inputs_from_args() -> tuple[str, str, bool]:
    """Parse argv and return job text, cv text, and whether demo mode was used."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print_usage()
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        logger.info("Running in DEMO mode with sample data...")
        job, cv = load_sample_data()
        return job, cv, True

    file_args = [
        arg
        for arg in sys.argv[1:]
        if not arg.startswith("--") and arg not in ("--email",)
    ]

    if len(file_args) >= 2:
        jd_file, cv_file = file_args[0], file_args[1]
        try:
            logger.info(f"Loading Job Description from: {jd_file}")
            if not Path(jd_file).exists():
                raise FileNotFoundError(f"Job description file not found: {jd_file}")

            file_size = Path(jd_file).stat().st_size
            if not validate_file_size(file_size):
                raise ValueError(
                    f"Job description file too large (max 10MB): {file_size / (1024 * 1024):.2f}MB"
                )

            job_desc = extract_text_from_file(jd_file, Path(jd_file).suffix[1:].lower())
            logger.info(f"Loaded job description ({len(job_desc)} characters)")

            logger.info(f"Loading CV from: {cv_file}")
            if not Path(cv_file).exists():
                raise FileNotFoundError(f"CV file not found: {cv_file}")

            file_size = Path(cv_file).stat().st_size
            if not validate_file_size(file_size):
                raise ValueError(
                    f"CV file too large (max 10MB): {file_size / (1024 * 1024):.2f}MB"
                )

            cv_text = extract_text_from_file(cv_file, Path(cv_file).suffix[1:].lower())
            logger.info(f"Loaded CV ({len(cv_text)} characters)")
            return job_desc, cv_text, False

        except Exception as e:
            logger.error(f"File loading error: {str(e)}")
            logger.info("Falling back to sample data...")
            job, cv = load_sample_data()
            return job, cv, True

    logger.info("Using sample data for demonstration...")
    job, cv = load_sample_data()
    return job, cv, True


def parse_flags() -> tuple[bool, str | None, bool]:
    """Return send_email, email_to override, save_report flags."""
    send_email = "--email" in sys.argv or AUTO_SEND_REPORT
    email_to = None
    save_report = "--no-report" not in sys.argv

    for i, arg in enumerate(sys.argv):
        if arg == "--email-to" and i + 1 < len(sys.argv):
            email_to = sys.argv[i + 1]

    return send_email, email_to, save_report


def main():
    """Main execution function"""
    logger.info("=" * 80)
    logger.info("Job Application Multi-Agent System")
    logger.info("=" * 80)

    send_email, email_to, save_report = parse_flags()
    job_desc, cv_text, _ = load_inputs_from_args()

    if send_email and not is_email_configured() and not email_to:
        logger.error(
            "Email requested but SMTP is not configured. "
            "Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD, REPORT_EMAIL_TO in .env"
        )
        sys.exit(1)

    automation = JobApplicationAutomation()

    outcome = automation.run(
        job_description=job_desc,
        cv_text=cv_text,
        user_profile={"industry": "AI/ML", "years_experience": 6},
        send_email=send_email,
        email_to=email_to or REPORT_EMAIL_TO,
        save_reports=save_report,
    )

    result = outcome["state"]
    formatted_results = outcome["formatted"]
    elapsed_total = outcome["elapsed_seconds"]

    if not save_report:
        logger.info("Report file saving skipped (--no-report)")

    logger.info("\n" + "=" * 80)
    logger.info("WORKFLOW RESULTS")
    logger.info("=" * 80)
    logger.info(f"Total execution time: {elapsed_total:.1f}s")

    print("\nWORKFLOW STATUS:")
    for component, status in formatted_results["status"].items():
        marker = "[OK]" if status == "OK" else "[FAIL]"
        print(f"  {marker} {component.replace('_', ' ').title()}")

    if result.job_profile:
        print(f"\nJOB PROFILE:")
        print(f"  Title: {result.job_profile.title}")
        print(f"  Company: {result.job_profile.company}")
        print(f"  Seniority: {result.job_profile.seniority_level}")
        print(f"  Required Skills: {', '.join(result.job_profile.required_skills[:5])}")

    if result.cv_analysis:
        print(f"\nCV ANALYSIS:")
        print(f"  Experience: {result.cv_analysis.experience_years} years")
        print(f"  Match Score: {result.cv_analysis.improvement_score:.0f}%")
        print(f"  Matching Skills: {', '.join(result.cv_analysis.matching_skills[:3])}")
        print("  Suggestions:")
        for i, suggestion in enumerate(result.cv_analysis.suggestions[:3], 1):
            print(f"    {i}. {suggestion}")

    if result.interview_guide:
        print(f"\nINTERVIEW PREP:")
        print(f"  Technical Questions: {len(result.interview_guide.technical_questions)}")
        print(f"  Behavioral Questions: {len(result.interview_guide.behavioral_questions)}")
        print(f"  System Design Questions: {len(result.interview_guide.system_design_questions)}")
        print(f"  Duration: {result.interview_guide.estimated_duration_minutes} minutes")
        print("  Tips:")
        for i, tip in enumerate(result.interview_guide.tips_and_tricks[:3], 1):
            print(f"    {i}. {tip}")

    if result.cover_letter:
        print(f"\nCOVER LETTER:")
        print("  Primary version generated (preview):")
        preview = result.cover_letter.primary_version[:200] + "..."
        print(f"  {preview}")

    output_file = Path("results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(formatted_results, f, indent=2, default=str)
    logger.info(f"\nFull results saved to: {output_file}")

    if save_report and outcome.get("report_paths"):
        paths = outcome["report_paths"]
        print(f"\nREPORTS:")
        print(f"  HTML: {paths['html']}")
        print(f"  JSON: {paths['json']}")

    if outcome.get("email_sent"):
        print(f"\nEMAIL: Report sent to {email_to or REPORT_EMAIL_TO}")
    elif send_email:
        print("\nEMAIL: Not sent (check SMTP configuration)")

    if formatted_results["errors"]:
        print(f"\nERRORS: {formatted_results['errors']}")

    logger.info("=" * 80)
    logger.info("Workflow completed!")
    logger.info("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nWorkflow interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)

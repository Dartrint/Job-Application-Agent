"""Automation CLI — run analysis, generate report, and email results"""

import argparse
import logging
import sys

from dotenv import load_dotenv

load_dotenv()

from src.automation import JobApplicationAutomation
from src.config import AUTO_SEND_REPORT, EMAIL_ENABLED, REPORT_EMAIL_TO
from src.tools.email_sender import is_email_configured

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automated job application analysis with report and email delivery"
    )
    parser.add_argument("--demo", action="store_true", help="Use built-in sample data")
    parser.add_argument("jd_file", nargs="?", help="Job description file (.pdf/.docx/.txt)")
    parser.add_argument("cv_file", nargs="?", help="CV file (.pdf/.docx/.txt)")
    parser.add_argument(
        "--email",
        action="store_true",
        help="Send HTML report to configured email (REPORT_EMAIL_TO in .env)",
    )
    parser.add_argument(
        "--email-to",
        dest="email_to",
        help="Override recipient email address",
    )
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="Skip email even when AUTO_SEND_REPORT=true",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    automation = JobApplicationAutomation()

    try:
        if args.demo or (not args.jd_file and not args.cv_file):
            logger.info("Running automation in DEMO mode")
            job_desc, cv_text = automation.load_demo_inputs()
        else:
            if not args.jd_file or not args.cv_file:
                logger.error("Provide both jd_file and cv_file, or use --demo")
                return 1
            job_desc, cv_text = automation.load_inputs_from_files(args.jd_file, args.cv_file)

        send_email = (args.email or AUTO_SEND_REPORT) and not args.no_email
        if send_email and not is_email_configured() and not args.email_to:
            logger.error(
                "Email requested but SMTP is not configured. "
                "Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD, REPORT_EMAIL_TO in .env"
            )
            return 1

        result = automation.run(
            job_description=job_desc,
            cv_text=cv_text,
            user_profile={"industry": "AI/ML", "years_experience": 6},
            send_email=send_email,
            email_to=args.email_to or REPORT_EMAIL_TO,
        )

        state = result["state"]
        formatted = result["formatted"]
        paths = result["report_paths"]

        print("\nAUTOMATION RESULT")
        print("-" * 40)
        for component, status in formatted["status"].items():
            marker = "[OK]" if status == "OK" else "[FAIL]"
            print(f"  {marker} {component.replace('_', ' ').title()}")
        print(f"\nReports saved:")
        print(f"  HTML: {paths['html']}")
        print(f"  JSON: {paths['json']}")
        print(f"  Duration: {result['elapsed_seconds']:.1f}s")

        if result["email_sent"]:
            print(f"  Email sent to: {args.email_to or REPORT_EMAIL_TO}")
        elif send_email:
            print("  Email: not sent")
        else:
            print("  Email: skipped (use --email to send)")

        if state.errors:
            print(f"\nWarnings: {len(state.errors)}")
            for error in state.errors[:3]:
                print(f"  - {error[:120]}")

        return 0 if all(v == "OK" for v in formatted["status"].values()) else 2

    except Exception as exc:
        logger.error("Automation failed: %s", exc, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())

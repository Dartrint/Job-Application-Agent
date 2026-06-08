"""Email delivery for analysis reports"""

import logging
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from src.config import (
    EMAIL_ENABLED,
    REPORT_EMAIL_FROM,
    REPORT_EMAIL_TO,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
)

logger = logging.getLogger(__name__)


def is_email_configured() -> bool:
    """Return True when SMTP settings are available."""
    return EMAIL_ENABLED


def send_report_email(
    html_body: str,
    subject: str,
    to_address: str | None = None,
    attachments: dict[str, Path] | None = None,
) -> None:
    """Send HTML report email with optional attachments."""
    if not EMAIL_ENABLED:
        raise ValueError(
            "Email is not configured. Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD, "
            "and REPORT_EMAIL_TO in .env"
        )

    recipient = to_address or REPORT_EMAIL_TO
    if not recipient:
        raise ValueError("No recipient email address provided")

    sender = REPORT_EMAIL_FROM or SMTP_USER
    message = MIMEMultipart("mixed")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient

    message.attach(MIMEText(html_body, "html", "utf-8"))

    for filename, path in (attachments or {}).items():
        if not path.exists():
            continue
        part = MIMEApplication(path.read_bytes(), Name=path.name)
        part["Content-Disposition"] = f'attachment; filename="{path.name}"'
        message.attach(part)

    logger.info("Sending report email to %s", recipient)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
        if SMTP_USE_TLS:
            server.starttls()
        if SMTP_USER and SMTP_PASSWORD:
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(sender, [recipient], message.as_string())

    logger.info("Report email sent successfully")

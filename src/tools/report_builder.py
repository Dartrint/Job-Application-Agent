"""HTML report generation for job application analysis"""

import json
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.state import ApplicationState

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
REPORTS_DIR = Path("reports")


def _template_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )


def build_html_report(formatted_results: dict, state: ApplicationState | None = None) -> str:
    """Build an HTML report from formatted workflow results."""
    env = _template_env()
    template = env.get_template("report.html.j2")

    job = formatted_results.get("job_profile") or {}
    cv = formatted_results.get("cv_analysis") or {}
    interview = formatted_results.get("interview_guide") or {}
    cover = formatted_results.get("cover_letter") or {}
    status = formatted_results.get("status") or {}

    all_ok = all(value == "OK" for value in status.values())
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return template.render(
        workflow_id=formatted_results.get("workflow_id", "N/A"),
        generated_at=generated_at,
        all_ok=all_ok,
        status=status,
        errors=formatted_results.get("errors") or [],
        job=job,
        cv=cv,
        interview=interview,
        cover=cover,
        execution_seconds=(
            (state.updated_at - state.created_at).total_seconds()
            if state and state.updated_at and state.created_at
            else None
        ),
    )


def save_report_files(
    formatted_results: dict,
    state: ApplicationState | None = None,
    output_dir: Path | None = None,
) -> dict[str, Path]:
    """Save HTML and JSON report files. Returns paths keyed by format."""
    target_dir = output_dir or REPORTS_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    workflow_id = formatted_results.get("workflow_id", "report")[:8]
    base_name = f"job_report_{timestamp}_{workflow_id}"

    html_path = target_dir / f"{base_name}.html"
    json_path = target_dir / f"{base_name}.json"

    html_path.write_text(build_html_report(formatted_results, state), encoding="utf-8")
    json_path.write_text(
        json.dumps(formatted_results, indent=2, default=str),
        encoding="utf-8",
    )

    return {"html": html_path, "json": json_path}

"""Streamlit Web UI for Job Application Agent"""

import streamlit as st
import json
import tempfile
from pathlib import Path
from datetime import datetime
from src.orchestrator import JobApplicationOrchestrator, format_results
from src.sample_data import load_sample_data
from src.config import REPORT_EMAIL_TO
from src.tools.file_processor import extract_text_from_file, validate_file_size
from src.tools.report_builder import save_report_files
from src.tools.email_sender import is_email_configured, send_report_email
from src.utils.translations import get_text
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="🤖 Job Application Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1em;
        padding: 0.5em 1.5em;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .skill-badge {
        display: inline-block;
        background-color: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "processing" not in st.session_state:
    st.session_state.processing = False
if "result" not in st.session_state:
    st.session_state.result = None
if "formatted_result" not in st.session_state:
    st.session_state.formatted_result = None
if "language" not in st.session_state:
    st.session_state.language = "en"
if "report_paths" not in st.session_state:
    st.session_state.report_paths = None


def extract_uploaded_text(uploaded_file) -> str:
    """Extract text from an uploaded file and clean up temp storage."""
    tmp_path = None
    try:
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getbuffer())
            tmp_path = tmp.name
        file_type = uploaded_file.name.split(".")[-1].lower()
        return extract_text_from_file(tmp_path, file_type)
    finally:
        if tmp_path:
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass


def get_lang_text(en_text: str, vi_text: str) -> str:
    """Get text based on current language setting."""
    language = st.session_state.get("language", "en")
    return vi_text if language == "vi" else en_text


def render_job_profile(job_profile):
    """Render job profile section"""
    if not job_profile:
        return

    st.subheader("📋 Job Profile")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Position", job_profile.title or "N/A")
    with col2:
        st.metric("Seniority", job_profile.seniority_level or "N/A")
    with col3:
        st.metric("Company", job_profile.company or "N/A")

    if job_profile.required_skills:
        st.write("**Required Skills:**")
        skills_html = "".join([f'<span class="skill-badge">{skill}</span>' for skill in job_profile.required_skills[:10]])
        st.markdown(skills_html, unsafe_allow_html=True)

    if job_profile.nice_to_have_skills:
        st.write("**Nice to Have:**")
        skills_html = "".join([f'<span class="skill-badge" style="background-color: #9d7eb8;">{skill}</span>' for skill in job_profile.nice_to_have_skills[:5]])
        st.markdown(skills_html, unsafe_allow_html=True)


def render_cv_analysis(cv_analysis):
    """Render CV analysis section"""
    if not cv_analysis:
        return

    st.subheader("📊 CV Analysis & Match")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Experience", f"{cv_analysis.experience_years} years")
    with col2:
        match_score = cv_analysis.improvement_score or 0
        st.metric("Match Score", f"{match_score:.0f}%")
    with col3:
        matching = len(cv_analysis.matching_skills or [])
        st.metric("Matching Skills", matching)

    # Add visual match score bar
    match_score = cv_analysis.improvement_score or 0
    if match_score >= 80:
        color = "green"
        status = "Excellent Match"
    elif match_score >= 60:
        color = "orange"
        status = "Good Match"
    else:
        color = "red"
        status = "Needs Improvement"

    st.write(f"**Match Quality: {status}**")
    st.progress(match_score / 100)

    # Matching skills
    if cv_analysis.matching_skills:
        st.write("**Your Matching Skills:**")
        skills_html = "".join([f'<span class="skill-badge">{skill}</span>' for skill in cv_analysis.matching_skills[:8]])
        st.markdown(skills_html, unsafe_allow_html=True)

    # Missing skills
    if cv_analysis.missing_skills:
        st.write("**Missing Skills (Opportunities):**")
        skills_html = "".join([f'<span class="skill-badge" style="background-color: #dc3545;">{skill}</span>' for skill in cv_analysis.missing_skills[:5]])
        st.markdown(skills_html, unsafe_allow_html=True)

    # Suggestions
    if cv_analysis.suggestions:
        st.write("**Improvement Suggestions:**")
        for i, suggestion in enumerate(cv_analysis.suggestions[:5], 1):
            st.markdown(f"{i}. {suggestion}")


def render_interview_prep(interview_guide):
    """Render interview preparation section"""
    if not interview_guide:
        return

    st.subheader(get_lang_text("Interview Preparation", "Chuẩn Bị Phỏng Vấn"))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Technical Q&A", len(interview_guide.technical_questions or []))
    with col2:
        st.metric("Behavioral Q&A", len(interview_guide.behavioral_questions or []))
    with col3:
        st.metric("Duration", f"{interview_guide.estimated_duration_minutes or 0} min")

    # Success factors
    if interview_guide.success_factors:
        st.write(f"**{get_lang_text('Key Success Factors', 'Yếu Tố Thành Công')}:**")
        for i, factor in enumerate(interview_guide.success_factors[:4], 1):
            st.write(f"{i}. {factor}")

    # Technical questions with difficulty
    if interview_guide.technical_questions:
        with st.expander(get_lang_text("Technical Questions & Answers", "Câu Hỏi Kỹ Thuật & Trả Lời")):
            for i, q in enumerate(interview_guide.technical_questions[:8], 1):
                question_text = q.question if hasattr(q, 'question') else q.get('question', 'N/A') if isinstance(q, dict) else 'N/A'
                st.write(f"**Q{i}: {question_text}**")

                if hasattr(q, 'difficulty'):
                    difficulty = q.difficulty
                elif isinstance(q, dict):
                    difficulty = q.get('difficulty')
                else:
                    difficulty = None
                if difficulty:
                    difficulty_badge = "🟢 Easy" if difficulty == "easy" else "🟡 Medium" if difficulty == "medium" else "🔴 Hard"
                    st.write(f"Difficulty: {difficulty_badge}")

                if hasattr(q, 'suggested_answer'):
                    suggested_answer = q.suggested_answer
                elif isinstance(q, dict):
                    suggested_answer = q.get('suggested_answer') or q.get('answer')
                else:
                    suggested_answer = None
                if suggested_answer:
                    st.write(f"**Answer Guide:** {suggested_answer[:400]}")

                if hasattr(q, 'why_asked'):
                    why_asked = q.why_asked
                elif isinstance(q, dict):
                    why_asked = q.get('why_asked')
                else:
                    why_asked = None
                if why_asked:
                    st.write(f"*Why asked:* {why_asked}")

                # Show keywords if available
                if hasattr(q, 'keywords') and q.keywords:
                    st.write(f"*Key concepts:* {', '.join(q.keywords[:5])}")

                st.divider()

    # Behavioral questions
    if interview_guide.behavioral_questions:
        with st.expander(get_lang_text("Behavioral Questions & Answers", "Câu Hỏi Hành Vi & Trả Lời")):
            for i, q in enumerate(interview_guide.behavioral_questions[:8], 1):
                question_text = q.question if hasattr(q, 'question') else q.get('question', 'N/A') if isinstance(q, dict) else 'N/A'
                st.write(f"**Q{i}: {question_text}**")
                if hasattr(q, 'suggested_answer'):
                    suggested_answer = q.suggested_answer
                elif isinstance(q, dict):
                    suggested_answer = q.get('suggested_answer') or q.get('answer')
                else:
                    suggested_answer = None
                if suggested_answer:
                    st.write(f"**Answer Structure:** {suggested_answer[:400]}")
                if hasattr(q, 'why_asked'):
                    why_asked = q.why_asked
                elif isinstance(q, dict):
                    why_asked = q.get('why_asked')
                else:
                    why_asked = None
                if why_asked:
                    st.write(f"*Tests:* {why_asked}")
                st.divider()

    # System design questions
    if interview_guide.system_design_questions:
        with st.expander(get_lang_text("System Design Questions", "Câu Hỏi Thiết Kế Hệ Thống")):
            for i, q in enumerate(interview_guide.system_design_questions[:4], 1):
                question_text = q.question if hasattr(q, 'question') else q.get('question', 'N/A') if isinstance(q, dict) else 'N/A'
                st.write(f"**Q{i}: {question_text}**")
                if hasattr(q, 'approach'):
                    approach = q.approach
                elif isinstance(q, dict):
                    approach = q.get('approach') or q.get('solution')
                else:
                    approach = None
                if approach:
                    st.write(f"**Approach:** {approach[:300]}")
                if hasattr(q, 'hints'):
                    hints = q.hints
                elif isinstance(q, dict):
                    hints = q.get('hints', [])
                else:
                    hints = []
                if hints:
                    st.write("**Hints:**")
                    for hint in hints[:4]:
                        st.write(f"  - {hint}")
                st.divider()

    # Tips and tricks with structure
    if interview_guide.tips_and_tricks:
        st.write(f"**{get_lang_text('Pro Tips & Strategy', 'Mẹo & Chiến Lược')}:**")
        for i, tip in enumerate(interview_guide.tips_and_tricks[:10], 1):
            st.markdown(f"{i}. {tip}")


def render_cover_letter(cover_letter):
    """Render cover letter section"""
    if not cover_letter:
        return

    st.subheader("✍️ Cover Letter")

    tabs = st.tabs(["Primary Version", "Variations", "HTML Export"])

    with tabs[0]:
        if cover_letter.primary_version:
            st.text_area(
                "Primary Cover Letter:",
                cover_letter.primary_version,
                height=400,
                disabled=True
            )

    with tabs[1]:
        if cover_letter.variations:
            for i, variation in enumerate(cover_letter.variations[:3], 1):
                with st.expander(f"Variation {i}"):
                    variation_content = variation.content if hasattr(variation, 'content') else variation.get("content", "") if isinstance(variation, dict) else ""
                    st.text_area(
                        f"Variation {i}:",
                        variation_content,
                        height=300,
                        disabled=True,
                        key=f"var_{i}"
                    )

    with tabs[2]:
        if cover_letter.primary_version:
            html_content = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .cover-letter {{ background: white; padding: 40px; border: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="cover-letter">
                    {cover_letter.primary_version.replace(chr(10), '<br>')}
                </div>
            </body>
            </html>
            """
            st.download_button(
                label="📥 Download as HTML",
                data=html_content,
                file_name="cover_letter.html",
                mime="text/html"
            )


# Main app
st.title("Job Application Agent / Trợ Lý Ứng Tuyển Việc Làm")
st.markdown("Optimize your job applications with AI / Tối ưu hóa ứng tuyển của bạn bằng AI")

# Sidebar
with st.sidebar:
    st.title("Settings / Cài Đặt")

    # Language selector
    language = st.selectbox(
        "Language / Ngôn Ngữ",
        options=["English", "Tiếng Việt"],
        index=0
    )
    st.session_state.language = "vi" if language == "Tiếng Việt" else "en"

    use_sample = st.checkbox("Use Sample Data / Dùng Dữ Liệu Mẫu", value=True)

    profile_years = st.number_input("Years of Experience / Năm Kinh Nghiệm", min_value=0, max_value=50, value=6)
    profile_industry = st.text_input("Industry Focus / Lĩnh Vực Chuyên Ngành", value="AI/ML")

    send_email = False
    if is_email_configured():
        send_email = st.checkbox(
            "Send report to email / Gửi báo cáo qua email",
            value=False,
            help=f"Recipient: {REPORT_EMAIL_TO}",
        )
    else:
        st.caption("Email not configured — set SMTP_* in .env to enable")

    if st.button("Clear Results / Xóa Kết Quả", use_container_width=True):
        st.session_state.result = None
        st.session_state.formatted_result = None
        st.session_state.report_paths = None
        st.rerun()

# Main content
if use_sample:
    st.info("📌 Using sample job description and CV for demonstration")
    job_desc, cv_text = load_sample_data()
else:
    st.info("📝 Upload files or paste your job description and CV below")

    # File upload section
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Job Description**")
        jd_file = st.file_uploader(
            "Upload JD (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            key="jd_file",
            help="Max 10MB"
        )
        if jd_file:
            try:
                if not validate_file_size(jd_file.size):
                    st.error("File too large (max 10MB)")
                    job_desc = ""
                else:
                    with st.spinner("Extracting text from job description..."):
                        try:
                            job_desc = extract_uploaded_text(jd_file)
                            st.success(f"Loaded JD ({len(job_desc)} characters)")
                        except Exception as extract_error:
                            st.error(f"Failed to extract: {str(extract_error)[:100]}")
                            st.info("Ensure the PDF/DOCX is valid and not corrupted")
                            job_desc = ""
            except Exception as e:
                st.error(f"Error loading file: {str(e)[:100]}")
                job_desc = ""
        else:
            job_desc = st.text_area("Or paste job description", height=200)

    with col2:
        st.write("**Your CV**")
        cv_file = st.file_uploader(
            "Upload CV (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            key="cv_file",
            help="Max 10MB"
        )
        if cv_file:
            try:
                if not validate_file_size(cv_file.size):
                    st.error("File too large (max 10MB)")
                    cv_text = ""
                else:
                    with st.spinner("Extracting text from CV..."):
                        try:
                            cv_text = extract_uploaded_text(cv_file)
                            st.success(f"Loaded CV ({len(cv_text)} characters)")
                        except Exception as extract_error:
                            st.error(f"Failed to extract: {str(extract_error)[:100]}")
                            st.info("Ensure the PDF/DOCX is valid and not corrupted")
                            cv_text = ""
            except Exception as e:
                st.error(f"Error loading file: {str(e)[:100]}")
                cv_text = ""
        else:
            cv_text = st.text_area("Or paste your CV", height=200)

# Process button
if st.button("🚀 Analyze Application", use_container_width=True, type="primary"):
    # Validate inputs
    if not job_desc or not job_desc.strip():
        st.error("Job description is empty")
    elif not cv_text or not cv_text.strip():
        st.error("CV is empty")
    else:
        st.session_state.processing = True

        progress_container = st.container()

        try:
            with progress_container:
                progress_bar = st.progress(0, text="Starting analysis...")

                # Show progress stages
                progress_stages = [
                    (0.2, "Analyzing job description..."),
                    (0.4, "Analyzing CV and calculating match..."),
                    (0.6, "Preparing interview questions..."),
                    (0.8, "Generating cover letter..."),
                    (1.0, "Finalizing results..."),
                ]

                import time
                stage_times = []
                start_time = time.time()

            orchestrator = JobApplicationOrchestrator()

            # Update progress stages
            with progress_container:
                progress_bar.progress(10, text=progress_stages[0][1])
                start_time = time.time()

            result = orchestrator.process_application_sync(
                job_description=job_desc,
                cv_text=cv_text,
                user_profile={
                    "industry": profile_industry,
                    "years_experience": profile_years
                },
                language=st.session_state.language,
            )

            elapsed = time.time() - start_time

            st.session_state.result = result
            st.session_state.formatted_result = format_results(result)
            st.session_state.report_paths = save_report_files(
                st.session_state.formatted_result, result
            )
            st.session_state.processing = False

            if send_email and is_email_configured():
                try:
                    job_title = result.job_profile.title if result.job_profile else "Job Application"
                    company = result.job_profile.company if result.job_profile else "Analysis"
                    html_body = st.session_state.report_paths["html"].read_text(encoding="utf-8")
                    send_report_email(
                        html_body=html_body,
                        subject=f"Job Application Report — {job_title} @ {company}",
                        attachments=st.session_state.report_paths,
                    )
                    st.info(f"Report emailed to {REPORT_EMAIL_TO}")
                except Exception as email_error:
                    st.warning(f"Email failed: {str(email_error)[:120]}")

            with progress_container:
                progress_bar.progress(100, text=f"Complete in {elapsed:.1f}s!")
                time.sleep(0.5)
                progress_container.empty()

            # Check for errors in result
            if result.errors:
                st.warning(f"Warnings: {len(result.errors)} issue(s)")
                for error in result.errors[:3]:
                    st.write(f"  - {error}")
            else:
                st.success(f"Analysis complete in {elapsed:.1f}s!")

            st.rerun()

        except ValueError as e:
            st.session_state.processing = False
            with progress_container:
                progress_container.empty()
            st.error(f"Validation Error: {str(e)}")
            logger.error(f"Validation error: {str(e)}")
        except Exception as e:
            st.session_state.processing = False
            with progress_container:
                progress_container.empty()
            st.error(f"Processing Error: {str(e)}")
            logger.error(f"Processing error: {str(e)}", exc_info=True)

# Display results
if st.session_state.result:
    result = st.session_state.result
    formatted_result = st.session_state.formatted_result

    st.divider()
    st.subheader("📊 Analysis Results")

    # Status overview
    col1, col2, col3, col4 = st.columns(4)
    status_items = [
        ("Job Analysis", "job_analysis"),
        ("CV Analysis", "cv_analysis"),
        ("Interview Prep", "interview_prep"),
        ("Cover Letter", "cover_letter"),
    ]

    columns = [col1, col2, col3, col4]
    for col, (label, key) in zip(columns, status_items):
        with col:
            status = formatted_result.get("status", {}).get(key, "FAIL")
            icon = "✅" if status == "OK" else "❌"
            st.markdown(f"{icon} {label}")

    st.divider()

    # Create tabs for different sections
    tabs = st.tabs(["Job Profile", "CV Match", "Interview Prep", "Cover Letter", "Export"])

    with tabs[0]:
        render_job_profile(result.job_profile)

    with tabs[1]:
        render_cv_analysis(result.cv_analysis)

    with tabs[2]:
        render_interview_prep(result.interview_guide)

    with tabs[3]:
        render_cover_letter(result.cover_letter)

    with tabs[4]:
        st.subheader("📥 Export Results")

        json_data = json.dumps(formatted_result, indent=2, default=str)
        st.download_button(
            label="📥 Download JSON Results",
            data=json_data,
            file_name=f"job_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )

        if st.session_state.report_paths:
            html_path = st.session_state.report_paths.get("html")
            if html_path and html_path.exists():
                st.download_button(
                    label="📥 Download HTML Report",
                    data=html_path.read_text(encoding="utf-8"),
                    file_name=html_path.name,
                    mime="text/html",
                    use_container_width=True,
                )
                st.caption(f"Saved report: {html_path}")

        st.write("**Full Results Preview:**")
        st.json(formatted_result)

st.divider()
st.markdown("""
---
Developed by [Dartint] / Phát triển bởi [Dartint]
""")

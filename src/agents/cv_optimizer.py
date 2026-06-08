"""CV Optimizer Agent - Analyzes CV and suggests improvements"""

import logging
from langchain_groq import ChatGroq
from src.state import ApplicationState, CVAnalysis
from src.config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, AGENT_TIMEOUT
from src.utils.llm_utils import normalize_string_list, parse_llm_json

logger = logging.getLogger(__name__)


def create_cv_optimizer_node():
    """Create the CV optimizer node for LangGraph"""

    def cv_optimizer_node(state: ApplicationState) -> ApplicationState:
        """
        Analyzes CV against job requirements and suggests improvements.
        """
        logger.info("Starting CV optimization...")

        if not state.cv_text:
            logger.error("No CV provided")
            state.errors.append("CV is empty")
            return state

        if not state.job_profile:
            logger.error("Job profile not available - run job analyzer first")
            state.errors.append("Job profile required for CV optimization")
            return state

        try:
            llm = ChatGroq(
                model=GROQ_MODEL,
                api_key=GROQ_API_KEY,
                temperature=GROQ_TEMPERATURE,
                timeout=AGENT_TIMEOUT,
            )

            required_skills = ", ".join(state.job_profile.required_skills[:10])
            tech_stack = ", ".join(state.job_profile.tech_stack[:10])

            # Determine language instruction
            language_instruction = ""
            if state.language == "vi":
                language_instruction = "Respond in Vietnamese. "
            else:
                language_instruction = "Respond in English. "

            analysis_prompt = f"""{language_instruction}Analyze this CV against the job requirements and provide structured feedback.

Job Requirements:
- Title: {state.job_profile.title}
- Required Skills: {required_skills}
- Tech Stack: {tech_stack}
- Seniority Level: {state.job_profile.seniority_level}

CV:
{state.cv_text}

Provide analysis in JSON format with:
- experience_years (number): Total years of experience
- key_skills (array of strings): Skills extracted from CV
- education (array of plain text strings): Education entries, e.g. "BS Computer Science, UC Berkeley (2018)"
- projects (array of plain text strings): Notable projects, e.g. "RAG chatbot — reduced support costs 40%"
- matching_skills (array of strings): CV skills that match job requirements
- missing_skills (array of strings): Required skills not in CV
- suggestions (array of strings): Specific improvements for this job (max 5)
- improvement_score (number 0-100): How well CV matches job

Return ONLY valid JSON. Use plain strings in arrays, not nested objects."""

            response = llm.invoke(analysis_prompt)
            analysis_data = parse_llm_json(response.content)

            cv_analysis = CVAnalysis(
                experience_years=float(analysis_data.get("experience_years", 0)),
                key_skills=analysis_data.get("key_skills", []),
                education=normalize_string_list(analysis_data.get("education", [])),
                projects=normalize_string_list(analysis_data.get("projects", [])),
                matching_skills=analysis_data.get("matching_skills", []),
                missing_skills=analysis_data.get("missing_skills", []),
                suggestions=analysis_data.get("suggestions", []),
                improvement_score=float(analysis_data.get("improvement_score", 50)),
            )

            state.cv_analysis = cv_analysis
            state.cv_analysis_completed = True

            logger.info(
                f"CV optimization completed. Match score: {cv_analysis.improvement_score}%"
            )

        except Exception as e:
            logger.error(f"CV optimization failed: {str(e)}")
            state.errors.append(f"CV optimization error: {str(e)}")

        return state

    return cv_optimizer_node

"""Job Analysis Agent - Analyzes job descriptions and extracts requirements"""

import logging
from langchain_groq import ChatGroq
from src.state import ApplicationState, JobProfile
from src.config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, AGENT_TIMEOUT
from src.utils.llm_utils import parse_llm_json

logger = logging.getLogger(__name__)


def create_job_analyzer_node():
    """Create the job analyzer node for LangGraph"""

    def job_analyzer_node(state: ApplicationState) -> ApplicationState:
        """
        Analyzes job description and extracts structured requirements.
        Uses Groq LLaMA 3.3 70B to parse job postings.
        """
        logger.info("Starting job analysis...")

        if not state.job_description:
            logger.error("No job description provided")
            state.errors.append("Job description is empty")
            return state

        try:
            # Initialize Groq LLM
            llm = ChatGroq(
                model=GROQ_MODEL,
                api_key=GROQ_API_KEY,
                temperature=GROQ_TEMPERATURE,
                timeout=AGENT_TIMEOUT,
            )

            # Determine language instruction
            language_instruction = ""
            if state.language == "vi":
                language_instruction = "Respond in Vietnamese. "
            else:
                language_instruction = "Respond in English. "

            # Create analysis prompt
            analysis_prompt = f"""{language_instruction}Analyze the following job posting and extract structured information.
Return a JSON object with these exact fields:
- title (string): Job title
- company (string): Company name (extract if available, otherwise 'Unknown')
- seniority_level (string): 'Junior', 'Mid', 'Senior', or 'Lead'
- required_skills (array): List of required technical skills
- nice_to_have_skills (array): List of nice-to-have skills
- responsibilities (array): Key responsibilities (max 5)
- tech_stack (array): Technologies and frameworks mentioned
- compensation_range (string): Salary range if mentioned
- location (string): Work location
- employment_type (string): 'Full-time', 'Contract', 'Part-time'

Job Description:
{state.job_description}

Return ONLY valid JSON, no additional text."""

            # Call Groq LLM
            response = llm.invoke(analysis_prompt)
            job_data = parse_llm_json(response.content)

            # Create JobProfile object
            job_profile = JobProfile(
                title=job_data.get("title", ""),
                company=job_data.get("company", "Unknown"),
                seniority_level=job_data.get("seniority_level", "Mid"),
                required_skills=job_data.get("required_skills", []),
                nice_to_have_skills=job_data.get("nice_to_have_skills", []),
                responsibilities=job_data.get("responsibilities", []),
                tech_stack=job_data.get("tech_stack", []),
                compensation_range=job_data.get("compensation_range"),
                location=job_data.get("location"),
                employment_type=job_data.get("employment_type", "Full-time"),
                raw_text=state.job_description,
            )

            state.job_profile = job_profile
            state.job_analysis_completed = True

            logger.info(
                f"Job analysis completed: {job_profile.title} at {job_profile.company}"
            )

        except Exception as e:
            logger.error(f"Job analysis failed: {str(e)}")
            state.errors.append(f"Job analysis error: {str(e)}")

        return state

    return job_analyzer_node

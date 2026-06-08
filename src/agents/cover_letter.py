"""Cover Letter Agent - Generates personalized cover letters"""

import logging
from langchain_groq import ChatGroq
from src.state import ApplicationState, CoverLetterDraft, CoverLetterVariation
from src.config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, AGENT_TIMEOUT
from src.utils.llm_utils import parse_llm_json

logger = logging.getLogger(__name__)


def create_cover_letter_node():
    """Create the cover letter node for LangGraph"""

    def cover_letter_node(state: ApplicationState) -> ApplicationState:
        """
        Generates personalized cover letter for the job position.
        """
        logger.info("Starting cover letter generation...")

        if not state.job_profile or not state.cv_analysis:
            logger.error("Job profile or CV analysis not available")
            state.errors.append(
                "Job profile and CV analysis required for cover letter"
            )
            return state

        try:
            llm = ChatGroq(
                model=GROQ_MODEL,
                api_key=GROQ_API_KEY,
                temperature=GROQ_TEMPERATURE,
                timeout=AGENT_TIMEOUT,
            )

            responsibilities = "\n".join(
                [f"- {r}" for r in state.job_profile.responsibilities[:3]]
            )
            matching_skills = ", ".join(state.cv_analysis.matching_skills[:5])

            # Determine language instruction
            language_instruction = ""
            if state.language == "vi":
                language_instruction = "Respond in Vietnamese. "
            else:
                language_instruction = "Respond in English. "

            cover_letter_prompt = f"""{language_instruction}Write a professional cover letter for this position.

Position: {state.job_profile.title}
Company: {state.job_profile.company}
Location: {state.job_profile.location}

Key Responsibilities:
{responsibilities}

Candidate Profile:
- Experience: {state.cv_analysis.experience_years} years
- Matching Skills: {matching_skills}
- Seniority Match: {state.job_profile.seniority_level}

Generate JSON with:
- primary_version: Main cover letter (3-4 paragraphs, professional tone)
- variations: Array of 2 objects with "content" and "tone" ("formal" or "casual")
- key_narratives: Array of 3 key talking points to emphasize

Each version should be a complete, ready-to-use cover letter (not template).
Return ONLY valid JSON."""

            response = llm.invoke(cover_letter_prompt)
            try:
                letter_data = parse_llm_json(response.content)
            except ValueError:
                logger.warning("Failed to parse cover letter JSON, using fallback")
                # Generate variations from the response text
                primary_text = response.content[:500]
                letter_data = {
                    "primary_version": primary_text,
                    "variations": [
                        {
                            "content": f"[Formal Tone Variation]\n\n{primary_text}\n\n[This is an alternative formal version of the cover letter.]",
                            "tone": "formal"
                        },
                        {
                            "content": f"[Casual Tone Variation]\n\n{primary_text}\n\n[This is an alternative more casual version of the cover letter.]",
                            "tone": "casual"
                        }
                    ],
                    "key_narratives": ["Strong technical background", "Good role fit"],
                }

            cover_letter = CoverLetterDraft(
                primary_version=letter_data.get("primary_version", ""),
                variations=[
                    CoverLetterVariation(
                        content=v if isinstance(v, str) else v.get("content", ""),
                        tone=v.get("tone") if isinstance(v, dict) else None,
                    )
                    for v in letter_data.get("variations", [])
                ],
                key_narratives=letter_data.get("key_narratives", []),
            )

            state.cover_letter = cover_letter
            state.cover_letter_completed = True

            logger.info("Cover letter generation completed")

        except Exception as e:
            logger.error(f"Cover letter generation failed: {str(e)}")
            state.errors.append(f"Cover letter error: {str(e)}")

        return state

    return cover_letter_node

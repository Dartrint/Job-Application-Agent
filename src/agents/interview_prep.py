"""Interview Prep Agent - Generates interview preparation materials"""

import logging
from langchain_groq import ChatGroq
from src.state import ApplicationState, InterviewGuide, QuestionAnswer, SystemDesignQuestion
from src.config import GROQ_API_KEY, GROQ_MODEL, GROQ_TEMPERATURE, AGENT_TIMEOUT
from src.utils.llm_utils import normalize_string_list, normalize_tips, parse_llm_json

logger = logging.getLogger(__name__)


def create_interview_prep_node():
    """Create the interview prep node for LangGraph"""

    def interview_prep_node(state: ApplicationState) -> ApplicationState:
        """
        Generates interview preparation guide with technical and behavioral questions.
        """
        logger.info("Starting interview preparation...")

        if not state.job_profile or not state.cv_analysis:
            logger.error("Job profile or CV analysis not available")
            state.errors.append(
                "Job profile and CV analysis required for interview prep"
            )
            return state

        try:
            llm = ChatGroq(
                model=GROQ_MODEL,
                api_key=GROQ_API_KEY,
                temperature=GROQ_TEMPERATURE,
                timeout=AGENT_TIMEOUT,
            )

            tech_stack = ", ".join(state.job_profile.tech_stack[:5])
            key_skills = ", ".join(state.job_profile.required_skills[:5])

            # Determine language instruction
            language_instruction = ""
            if state.language == "vi":
                language_instruction = "Respond in Vietnamese. "
            else:
                language_instruction = "Respond in English. "

            interview_prompt = f"""{language_instruction}Generate COMPREHENSIVE interview preparation materials for this position.

Job: {state.job_profile.title} at {state.job_profile.company}
Seniority: {state.job_profile.seniority_level}
Tech Stack: {tech_stack}
Key Skills: {key_skills}
Responsibilities: {", ".join(state.job_profile.responsibilities[:3])}

Candidate Background:
- Experience: {state.cv_analysis.experience_years} years
- Skills: {", ".join(state.cv_analysis.key_skills[:5])}
- Match Score: {state.cv_analysis.improvement_score}%
- Missing Skills: {", ".join(state.cv_analysis.missing_skills[:3] if state.cv_analysis.missing_skills else [])}

Generate JSON with:
1. technical_questions: Array of 6-8 technical questions with format {{
   "question": "specific technical question",
   "difficulty": "easy/medium/hard",
   "why_asked": "reason this is asked",
   "suggested_answer": "detailed answer guidance",
   "keywords": ["key", "concepts"]
}}

2. behavioral_questions: Array of 6-8 behavioral questions (STAR format) {{
   "question": "Tell me about a time when...",
   "why_asked": "what skill this tests",
   "suggested_answer": "example answer structure"
}}

3. system_design_questions: Array of 3-4 system design questions {{
   "question": "Design a... system",
   "approach": "step by step approach",
   "hints": ["start with requirements", "discuss tradeoffs"]
}}

4. tips_and_tricks: Array of 8-10 specific, actionable tip strings (plain text, not objects)

5. estimated_duration_minutes: realistic estimate (90-120)
6. interview_format: "technical" or "behavioral" or "mixed"
7. company_research: string with key things to know about the company
8. success_factors: array of 3-4 plain text success factors

Return ONLY valid JSON with detailed, specific content relevant to this job."""

            response = llm.invoke(interview_prompt)
            interview_data = parse_llm_json(response.content)

            interview_guide = InterviewGuide(
                technical_questions=[
                    QuestionAnswer(
                        question=q.get("question", ""),
                        suggested_answer=q.get("suggested_answer") or q.get("answer"),
                        difficulty=q.get("difficulty"),
                        why_asked=q.get("why_asked"),
                        keywords=q.get("keywords", []) if isinstance(q.get("keywords"), list) else [],
                    )
                    for q in interview_data.get("technical_questions", [])
                    if isinstance(q, dict) and q.get("question")
                ],
                behavioral_questions=[
                    QuestionAnswer(
                        question=q.get("question", ""),
                        suggested_answer=q.get("suggested_answer") or q.get("answer"),
                        why_asked=q.get("why_asked"),
                    )
                    for q in interview_data.get("behavioral_questions", [])
                    if isinstance(q, dict) and q.get("question")
                ],
                system_design_questions=[
                    SystemDesignQuestion(
                        question=q.get("question", ""),
                        approach=q.get("approach") or q.get("solution"),
                        hints=q.get("hints", []) if isinstance(q.get("hints"), list) else [],
                    )
                    for q in interview_data.get("system_design_questions", [])
                    if isinstance(q, dict) and q.get("question")
                ],
                tips_and_tricks=normalize_tips(interview_data.get("tips_and_tricks", [])),
                estimated_duration_minutes=int(
                    interview_data.get("estimated_duration_minutes", 60)
                ),
                interview_format=interview_data.get("interview_format"),
                company_research=interview_data.get("company_research"),
                success_factors=normalize_string_list(
                    interview_data.get("success_factors", [])
                ),
            )

            state.interview_guide = interview_guide
            state.interview_prep_completed = True

            logger.info(
                f"Interview prep completed. Generated {len(interview_guide.technical_questions)} technical questions"
            )

        except Exception as e:
            logger.error(f"Interview prep failed: {str(e)}")
            state.errors.append(f"Interview prep error: {str(e)}")

        return state

    return interview_prep_node

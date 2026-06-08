"""LangGraph Orchestrator - Coordinates multi-agent workflow"""

import logging
import uuid
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from src.state import ApplicationState
from src.agents.job_analyzer import create_job_analyzer_node
from src.agents.cv_optimizer import create_cv_optimizer_node
from src.agents.interview_prep import create_interview_prep_node
from src.agents.cover_letter import create_cover_letter_node

logger = logging.getLogger(__name__)


def create_workflow_graph():
    """Create and compile the LangGraph workflow"""

    # Create graph
    workflow = StateGraph(ApplicationState)

    # Create agent nodes
    job_analyzer = create_job_analyzer_node()
    cv_optimizer = create_cv_optimizer_node()
    interview_prep = create_interview_prep_node()
    cover_letter = create_cover_letter_node()

    # Add nodes
    workflow.add_node("job_analyzer", job_analyzer)
    workflow.add_node("cv_optimizer", cv_optimizer)
    workflow.add_node("interview_prep", interview_prep)
    workflow.add_node("cover_letter", cover_letter)

    # Define edges - strictly sequential workflow
    workflow.add_edge(START, "job_analyzer")
    workflow.add_edge("job_analyzer", "cv_optimizer")
    workflow.add_edge("cv_optimizer", "interview_prep")
    workflow.add_edge("interview_prep", "cover_letter")
    workflow.add_edge("cover_letter", END)

    # Compile the graph
    compiled_graph = workflow.compile()

    return compiled_graph


class JobApplicationOrchestrator:
    """Orchestrates the job application workflow"""

    def __init__(self):
        self.graph = create_workflow_graph()
        logger.info("Orchestrator initialized")

    async def process_application(
        self, job_description: str, cv_text: str, user_profile: dict = None, language: str = "en"
    ) -> ApplicationState:
        """
        Process a job application end-to-end.

        Args:
            job_description: Job posting text
            cv_text: CV/Resume text
            user_profile: Additional user background info
            language: Language for content generation ("en" or "vi")

        Returns:
            ApplicationState with all agent outputs
        """

        # Create initial state
        state = ApplicationState(
            job_description=job_description,
            cv_text=cv_text,
            user_profile=user_profile or {},
            language=language,
            workflow_id=str(uuid.uuid4()),
            created_at=datetime.now(),
        )

        logger.info(f"Starting workflow {state.workflow_id}")

        try:
            # Invoke the graph
            result_data = self.graph.invoke(state.model_dump())
            result = ApplicationState(**result_data)
            result.updated_at = datetime.now()

            if result.errors:
                logger.warning(f"Workflow completed with errors: {result.errors}")
            else:
                logger.info("Workflow completed successfully")

            return result

        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            state.errors.append(f"Orchestration error: {str(e)}")
            return state

    def process_application_sync(
        self, job_description: str, cv_text: str, user_profile: dict = None, language: str = "en"
    ) -> ApplicationState:
        """Synchronous version of process_application"""

        # Validate inputs
        if not job_description or not job_description.strip():
            raise ValueError("Job description cannot be empty")
        if not cv_text or not cv_text.strip():
            raise ValueError("CV text cannot be empty")

        state = ApplicationState(
            job_description=job_description.strip(),
            cv_text=cv_text.strip(),
            user_profile=user_profile or {},
            language=language,
            workflow_id=str(uuid.uuid4()),
            created_at=datetime.now(),
        )

        logger.info(f"Starting workflow {state.workflow_id}")

        try:
            result_data = self.graph.invoke(state.model_dump())
            result = ApplicationState(**result_data)
            result.updated_at = datetime.now()

            if result.errors:
                logger.warning(f"Workflow completed with errors: {result.errors}")
            else:
                logger.info("Workflow completed successfully")

            return result

        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            state.errors.append(f"Orchestration error: {str(e)}")
            return state


def format_results(state: ApplicationState) -> dict:
    """Format final results for display"""

    results = {
        "workflow_id": state.workflow_id,
        "status": {
            "job_analysis": "OK" if state.job_analysis_completed else "FAILED",
            "cv_analysis": "OK" if state.cv_analysis_completed else "FAILED",
            "interview_prep": "OK" if state.interview_prep_completed else "FAILED",
            "cover_letter": "OK" if state.cover_letter_completed else "FAILED",
        },
        "job_profile": state.job_profile.model_dump() if state.job_profile else None,
        "cv_analysis": state.cv_analysis.model_dump() if state.cv_analysis else None,
        "interview_guide": (
            state.interview_guide.model_dump() if state.interview_guide else None
        ),
        "cover_letter": (
            state.cover_letter.model_dump() if state.cover_letter else None
        ),
        "errors": state.errors,
    }

    return results

"""Hidden developer review projection for the mock Experience prototype."""

from __future__ import annotations

from experience.mock_data import journey_for
from experience.models import PrototypeState
from experience.workspace import visible_sections


def developer_review_state(state: PrototypeState) -> dict[str, object]:
    """Expose traceability without placing internal IDs in customer-facing UI."""

    if state.active_goal is None:
        return {}
    journey = journey_for(state.active_goal)
    sections = visible_sections(state)
    return {
        "Goal ID": state.active_goal.value,
        "Journey state": state.completion_state.value,
        "Question IDs asked": state.question_ids_asked,
        "Question IDs skipped": state.question_ids_skipped,
        "Captured answers": tuple(
            {
                "question_id": answer.question_id,
                "step": answer.step_key,
                "value": answer.display_value,
                "status": answer.status.value,
            }
            for answer in state.captured_answers
        ),
        "Financial Picture items revealed": tuple(
            item.label for section in sections for item in section.picture_items
        ),
        "Workspace sections revealed": tuple(section.key for section in sections),
        "Evidence purpose": tuple(section.purpose.value for section in sections),
        "Enough information": state.enough_information,
        "Refinement performed": state.refinement_performed,
        "Completion state": state.completion_state.value,
        "Workspace ID": state.workspace_id,
        "Journey": journey.customer_name,
    }

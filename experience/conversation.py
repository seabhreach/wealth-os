"""Pure transitions for five bounded mock conversation journeys."""

from __future__ import annotations

from experience.mock_data import (
    QUESTION_IDS_BY_GOAL,
    journey_for,
    match_journey,
    question_for,
)
from experience.models import (
    CapturedAnswer,
    Choice,
    CompletionState,
    ContextAction,
    GoalId,
    InformationStatus,
    Message,
    MessageRole,
    PrototypeState,
    QuestionStep,
)


def empty_state() -> PrototypeState:
    """Return the untouched Home state."""

    return PrototypeState()


def reset_state() -> PrototypeState:
    """Return cleanly to Home without retaining a mock Workspace."""

    return empty_state()


def start_conversation(user_message: str, goal_id: GoalId | None = None) -> PrototypeState:
    """Start the matching finite mock journey from the user's opening question."""

    normalized = user_message.strip()
    selected_goal = goal_id or match_journey(normalized)
    if selected_goal is None:
        return PrototypeState(
            messages=(
                Message(MessageRole.USER, normalized),
                Message(
                    MessageRole.ASSISTANT,
                    "I can currently explore retiring earlier, an investment property, "
                    "employer-equity exposure, higher retirement spending, or a cash decline. "
                    "Choose one of the saved Workspaces below or ask about one of those topics.",
                ),
            )
        )
    journey = journey_for(selected_goal)
    messages = (Message(MessageRole.USER, normalized),)

    if journey.first_step is None:
        return PrototypeState(
            active_goal=selected_goal,
            workspace_id=_workspace_id(selected_goal),
            messages=(
                *messages,
                Message(MessageRole.ASSISTANT, journey.enough_message),
                Message(MessageRole.ASSISTANT, journey.refinement.prompt),
            ),
            revealed_sections=journey.saved_sections,
            enough_information=True,
            completion_state=CompletionState.ENOUGH_FOR_FIRST_VIEW,
        )

    first = question_for(journey, journey.first_step)
    return PrototypeState(
        active_goal=selected_goal,
        workspace_id=_workspace_id(selected_goal),
        messages=(*messages, Message(MessageRole.ASSISTANT, first.assistant_text)),
        current_step=first.key,
        question_ids_asked=(first.question_id,),
    )


def open_saved_workspace(goal_id: GoalId) -> PrototypeState:
    """Open one predefined mock Workspace with its original goal and refinement path."""

    journey = journey_for(goal_id)
    return PrototypeState(
        active_goal=goal_id,
        workspace_id=_workspace_id(goal_id),
        messages=(
            Message(MessageRole.ASSISTANT, journey.enough_message),
            Message(MessageRole.ASSISTANT, journey.refinement.prompt),
        ),
        revealed_sections=journey.saved_sections,
        question_ids_skipped=tuple(sorted(QUESTION_IDS_BY_GOAL[goal_id])),
        enough_information=True,
        completion_state=CompletionState.ENOUGH_FOR_FIRST_VIEW,
    )


def available_choices(state: PrototypeState) -> tuple[Choice, ...]:
    """Return chips for the current question or the one allowed refinement."""

    if state.active_goal is None:
        return ()
    journey = journey_for(state.active_goal)
    if state.current_step is not None:
        return question_for(journey, state.current_step).choices
    if state.enough_information and not state.refinement_performed:
        return journey.refinement.choices
    return ()


def contextual_actions(state: PrototypeState) -> tuple[ContextAction, ...]:
    """Return permitted tiny actions for the active question."""

    question = _current_question(state)
    if question is None:
        return ()
    actions = [ContextAction.WHY]
    if question.skip_allowed:
        actions.append(ContextAction.SKIP)
    if question.estimate_answer is not None:
        actions.append(ContextAction.ESTIMATE)
    return tuple(actions)


def advance_with_choice(state: PrototypeState, choice_value: str) -> PrototypeState:
    """Advance immediately when a choice chip is selected."""

    choices = available_choices(state)
    choice = next((candidate for candidate in choices if candidate.value == choice_value), None)
    if choice is None:
        raise ValueError(f"Unsupported choice for the current state: {choice_value}")
    if state.current_step is None:
        return _apply_refinement(state, choice)
    return _capture_answer(state, choice.label, choice.value, choice.status, choice)


def advance_with_text(state: PrototypeState, user_message: str) -> PrototypeState:
    """Advance with a concise answer while preserving uncertainty honestly."""

    normalized = user_message.strip()
    if not normalized:
        return state
    question = _current_question(state)
    if question is None:
        return state
    lowered = normalized.casefold()
    if any(phrase in lowered for phrase in ("not sure", "don't know", "do not know")):
        if not question.unknown_allowed:
            return _append_assistant(
                state,
                "I can't safely fill that gap. Choose one of the visible options "
                "when you're ready.",
            )
        status = InformationStatus.UNKNOWN
        value = "unknown"
    elif any(word in lowered for word in ("about", "around", "roughly", "approximately")):
        status = InformationStatus.ESTIMATED
        value = normalized
    else:
        status = InformationStatus.KNOWN
        value = normalized
    return _capture_answer(state, normalized, value, status)


def advance_with_action(state: PrototypeState, action: ContextAction) -> PrototypeState:
    """Apply a permitted inline explanation, estimate, or skip action."""

    question = _current_question(state)
    if question is None or action not in contextual_actions(state):
        return state
    if action is ContextAction.WHY:
        return _append_assistant(state, question.why_text)
    if action is ContextAction.ESTIMATE and question.estimate_answer is not None:
        display, value = question.estimate_answer
        return _capture_answer(state, display, value, InformationStatus.ESTIMATED)
    return _capture_answer(
        state,
        "Skip for now",
        "unknown",
        InformationStatus.UNKNOWN,
        skipped=True,
    )


def _capture_answer(
    state: PrototypeState,
    display_answer: str,
    stored_answer: str,
    status: InformationStatus,
    choice: Choice | None = None,
    *,
    skipped: bool = False,
) -> PrototypeState:
    if state.active_goal is None or state.current_step is None:
        return state

    journey = journey_for(state.active_goal)
    question = question_for(journey, state.current_step)
    answer = CapturedAnswer(
        question_id=question.question_id,
        step_key=question.key,
        display_value=display_answer,
        value=stored_answer,
        status=status,
    )
    reveal = choice.reveal_section if choice and choice.reveal_section else question.reveal_section
    revealed = _append_unique(state.revealed_sections, reveal)
    next_step = choice.next_step if choice and choice.next_step else question.next_step
    next_step = _branch_after_user_age(state, next_step)
    enough = bool(choice and choice.enough_information) or question.enough_information
    messages = (*state.messages, Message(MessageRole.USER, display_answer))
    skipped_ids = state.question_ids_skipped
    if skipped:
        skipped_ids = _append_unique(skipped_ids, question.question_id)

    if status is InformationStatus.ESTIMATED:
        messages = (
            *messages,
            Message(
                MessageRole.ASSISTANT, "I'll mark that as estimated so it can be refined later."
            ),
        )
    elif status is InformationStatus.UNKNOWN:
        messages = (
            *messages,
            Message(
                MessageRole.ASSISTANT,
                "I'll keep that unknown and show the resulting limitation rather than "
                "inventing a value.",
            ),
        )

    if enough:
        messages = (
            *messages,
            Message(MessageRole.ASSISTANT, journey.enough_message),
            Message(MessageRole.ASSISTANT, journey.refinement.prompt),
        )
        return PrototypeState(
            active_goal=state.active_goal,
            workspace_id=state.workspace_id,
            messages=messages,
            revealed_sections=revealed,
            captured_answers=(*state.captured_answers, answer),
            question_ids_asked=state.question_ids_asked,
            question_ids_skipped=skipped_ids,
            enough_information=True,
            completion_state=CompletionState.ENOUGH_FOR_FIRST_VIEW,
        )

    if next_step is None:
        return state
    next_question = question_for(journey, next_step)
    messages = (*messages, Message(MessageRole.ASSISTANT, next_question.assistant_text))
    return PrototypeState(
        active_goal=state.active_goal,
        workspace_id=state.workspace_id,
        messages=messages,
        current_step=next_step,
        revealed_sections=revealed,
        captured_answers=(*state.captured_answers, answer),
        question_ids_asked=(*state.question_ids_asked, next_question.question_id),
        question_ids_skipped=skipped_ids,
    )


def _apply_refinement(state: PrototypeState, choice: Choice) -> PrototypeState:
    if state.active_goal is None or state.refinement_performed:
        return state
    reveal = _append_unique(state.revealed_sections, choice.reveal_section)
    return PrototypeState(
        active_goal=state.active_goal,
        workspace_id=state.workspace_id,
        messages=(
            *state.messages,
            Message(MessageRole.USER, choice.label),
            Message(
                MessageRole.ASSISTANT,
                "The existing Workspace has been updated with that refinement.",
            ),
        ),
        revealed_sections=reveal,
        captured_answers=state.captured_answers,
        question_ids_asked=state.question_ids_asked,
        question_ids_skipped=state.question_ids_skipped,
        enough_information=True,
        refinement_performed=True,
        completion_state=CompletionState.REFINED,
    )


def _branch_after_user_age(state: PrototypeState, next_step: str | None) -> str | None:
    if state.current_step != "retire-user-age":
        return next_step
    scope = next(
        (answer.value for answer in state.captured_answers if answer.step_key == "retire-scope"),
        "self",
    )
    return "retire-partner-age" if scope == "household" else next_step


def _current_question(state: PrototypeState) -> QuestionStep | None:
    if state.active_goal is None or state.current_step is None:
        return None
    return question_for(journey_for(state.active_goal), state.current_step)


def _append_assistant(state: PrototypeState, content: str) -> PrototypeState:
    return PrototypeState(
        active_goal=state.active_goal,
        workspace_id=state.workspace_id,
        messages=(*state.messages, Message(MessageRole.ASSISTANT, content)),
        current_step=state.current_step,
        revealed_sections=state.revealed_sections,
        captured_answers=state.captured_answers,
        question_ids_asked=state.question_ids_asked,
        question_ids_skipped=state.question_ids_skipped,
        enough_information=state.enough_information,
        refinement_performed=state.refinement_performed,
        completion_state=state.completion_state,
    )


def _append_unique(values: tuple[str, ...], value: str | None) -> tuple[str, ...]:
    if value is None or value in values:
        return values
    return (*values, value)


def _workspace_id(goal_id: GoalId) -> str:
    return f"mock-workspace-{goal_id.value}"

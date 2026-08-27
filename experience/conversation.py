"""Pure scripted conversation transitions for the mock prototype."""

from __future__ import annotations

from experience.mock_data import DEFAULT_GOAL, journey_for, match_journey
from experience.models import Choice, GoalId, Message, MessageRole, PrototypeState


def empty_state() -> PrototypeState:
    """Return the untouched Home state."""

    return PrototypeState()


def start_conversation(user_message: str, goal_id: GoalId | None = None) -> PrototypeState:
    """Start the matching mock journey from the user's opening question."""

    normalized = user_message.strip()
    selected_goal = goal_id or match_journey(normalized) or DEFAULT_GOAL
    journey = journey_for(selected_goal)
    return PrototypeState(
        active_goal=selected_goal,
        messages=(
            Message(MessageRole.USER, normalized),
            Message(MessageRole.ASSISTANT, journey.steps[0].assistant_text),
        ),
    )


def available_choices(state: PrototypeState) -> tuple[Choice, ...]:
    """Return choices for the current step."""

    if state.active_goal is None:
        return ()
    journey = journey_for(state.active_goal)
    return journey.steps[state.step_index].choices


def contextual_actions(state: PrototypeState) -> tuple[str, ...]:
    """Return small contextual actions for the current step."""

    if state.active_goal is None:
        return ()
    journey = journey_for(state.active_goal)
    return journey.steps[state.step_index].contextual_actions


def advance_with_choice(state: PrototypeState, choice_value: str) -> PrototypeState:
    """Advance immediately when a choice chip is selected."""

    choices = available_choices(state)
    choice = next((candidate for candidate in choices if candidate.value == choice_value), None)
    if choice is None:
        raise ValueError(f"Unsupported choice for the current step: {choice_value}")
    return _advance(state, choice.label, choice.value)


def advance_with_text(state: PrototypeState, user_message: str) -> PrototypeState:
    """Advance the script using a short conversational answer."""

    normalized = user_message.strip()
    if not normalized:
        return state
    return _advance(state, normalized, normalized)


def _advance(state: PrototypeState, display_answer: str, stored_answer: str) -> PrototypeState:
    if state.active_goal is None:
        return start_conversation(display_answer)

    journey = journey_for(state.active_goal)
    current_step = journey.steps[state.step_index]
    revealed = state.revealed_sections
    if current_step.reveal_section and current_step.reveal_section not in revealed:
        revealed = (*revealed, current_step.reveal_section)

    messages = (*state.messages, Message(MessageRole.USER, display_answer))
    answers = (*state.answers, (f"step-{state.step_index}", stored_answer))
    if state.step_index + 1 < len(journey.steps):
        next_index = state.step_index + 1
        messages = (
            *messages,
            Message(MessageRole.ASSISTANT, journey.steps[next_index].assistant_text),
        )
    else:
        next_index = state.step_index
        messages = (*messages, Message(MessageRole.ASSISTANT, journey.completion_message))

    return PrototypeState(
        active_goal=state.active_goal,
        messages=messages,
        step_index=next_index,
        revealed_sections=revealed,
        answers=answers,
    )

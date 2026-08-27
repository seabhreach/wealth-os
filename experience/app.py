"""Streamlit entry point for the separate mock-only Experience shell."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from experience.components.chat import (
    render_choice_chips,
    render_contextual_actions,
    render_messages,
)
from experience.components.live_controls import live_workspace_for_goal
from experience.components.live_workspace import render_live_workspace
from experience.components.recent_workspaces import render_recent_workspaces
from experience.components.workspace_header import render_workspace_header
from experience.components.workspace_sections import render_workspace_sections
from experience.conversation import (
    advance_with_action,
    advance_with_choice,
    advance_with_text,
    available_choices,
    contextual_actions,
    empty_state,
    open_saved_workspace,
    reset_state,
    start_conversation,
)
from experience.live import LiveExperienceService
from experience.models import GoalId, PrototypeState
from experience.review import developer_review_state
from experience.styles import apply_styles
from experience.widget_keys import widget_key
from experience.workspace import visible_sections, workspace_status, workspace_title

STATE_KEY = "wealth_os_experience_state"
MODE_KEY = "wealth_os_experience_mode"
LIVE_GOAL_KEY = "wealth_os_live_goal"
MOCK_MODE = "MOCK EXPERIENCE"
LIVE_MODE = "LIVE DETERMINISTIC EXPERIENCE"


def _state() -> PrototypeState:
    stored = st.session_state.get(STATE_KEY)
    if isinstance(stored, PrototypeState):
        return stored
    initial = empty_state()
    st.session_state[STATE_KEY] = initial
    return initial


def _save(state: PrototypeState) -> None:
    st.session_state[STATE_KEY] = state


def _render_home(state: PrototypeState) -> None:
    _, home_column, _ = st.columns((0.55, 3.0, 0.55))
    with home_column:
        st.markdown(
            (
                '<main class="wos-home">'
                '<div class="wos-wordmark">Wealth OS</div>'
                '<h1 class="wos-question">What would you like to explore today?</h1>'
                '<p class="wos-support">Start with the question on your mind. We\'ll build your '
                "Financial Picture together and only ask for information that helps answer it.</p>"
                "</main>"
            ),
            unsafe_allow_html=True,
        )
        opening_message = st.chat_input(
            "Ask about retirement, spending, property, employer equity or cash flow",
            key="home-chat-input",
        )
        if state.messages:
            render_messages(state.messages)
        selected_goal = render_recent_workspaces()

    if opening_message:
        _save(start_conversation(opening_message))
        st.rerun()
    if selected_goal is not None:
        _save(open_saved_workspace(selected_goal))
        st.rerun()


def _render_active(state: PrototypeState) -> None:
    conversation_column, workspace_column = st.columns((0.92, 1.08), gap="large")
    with conversation_column:
        st.markdown('<div class="wos-pane-label">Conversation</div>', unsafe_allow_html=True)
        if st.button("Return home", key="return-home", type="tertiary"):
            _save(reset_state())
            st.rerun()
        render_messages(state.messages)
        assert state.active_goal is not None
        workspace_id = state.workspace_id or "mock-workspace"
        step_key = state.current_step or "refinement"
        selected_action = render_contextual_actions(
            contextual_actions(state), workspace_id, state.active_goal, step_key
        )
        selected_choice = render_choice_chips(
            available_choices(state), workspace_id, state.active_goal, step_key
        )
        follow_up = st.chat_input(
            "Share an answer or ask a follow-up",
            key=widget_key("chat-input", workspace_id, state.active_goal.value, step_key),
        )
        if selected_choice is not None:
            _save(advance_with_choice(state, selected_choice))
            st.rerun()
        if selected_action is not None:
            _save(advance_with_action(state, selected_action))
            st.rerun()
        if follow_up:
            _save(advance_with_text(state, follow_up))
            st.rerun()

    with workspace_column:
        render_workspace_header(workspace_title(state), workspace_status(state))
        render_workspace_sections(visible_sections(state))
        st.markdown(
            ('<div class="wos-prototype-note">Illustrative Workspace · Example data</div>'),
            unsafe_allow_html=True,
        )
        if st.query_params.get("review") == "1":
            with st.expander("Developer review", expanded=False):
                st.json(developer_review_state(state))


def _render_live_home() -> None:
    _, home_column, _ = st.columns((0.55, 3.0, 0.55))
    with home_column:
        st.markdown(
            (
                '<main class="wos-home">'
                '<div class="wos-wordmark">Live baseline</div>'
                '<h1 class="wos-question">Choose a question to explore.</h1>'
                '<p class="wos-support">These Workspaces use the example household and the '
                "recovered v0.2 calculations.</p>"
                "</main>"
            ),
            unsafe_allow_html=True,
        )
        columns = st.columns(5)
        for index, goal_id in enumerate(GoalId):
            label = {
                GoalId.RETIRE_EARLIER: "Retire earlier",
                GoalId.INVESTMENT_PROPERTY: "Investment property",
                GoalId.EMPLOYER_EQUITY: "Employer equity",
                GoalId.HIGHER_SPENDING: "Higher spending",
                GoalId.CASH_DECLINE: "Cash decline",
            }[goal_id]
            if columns[index].button(
                label,
                key=widget_key("live-goal", goal_id.value),
                use_container_width=True,
            ):
                st.session_state[LIVE_GOAL_KEY] = goal_id
                st.rerun()
        st.markdown(
            (
                '<div class="wos-prototype-note">Read-only example household · '
                "No illustrative evidence</div>"
            ),
            unsafe_allow_html=True,
        )


def _render_live_active(goal_id: GoalId) -> None:
    service = LiveExperienceService.from_example(Path(__file__).resolve().parents[1])
    conversation_column, workspace_column = st.columns((0.82, 1.18), gap="large")
    with conversation_column:
        st.markdown('<div class="wos-pane-label">Explore</div>', unsafe_allow_html=True)
        if st.button("Return to live goals", key="return-live-home", type="tertiary"):
            st.session_state.pop(LIVE_GOAL_KEY, None)
            st.rerun()
        st.markdown(
            (
                '<div class="wos-message">'
                '<div class="wos-message-body">Changes below are temporary and never update '
                "your baseline.</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
        workspace = live_workspace_for_goal(goal_id, service)
    with workspace_column:
        render_live_workspace(workspace)


def _prototype_mode() -> str:
    with st.expander("Review mode", expanded=False):
        st.caption("Switch between illustrative and live-baseline evidence.")
        return st.radio(
            "Evidence source",
            (MOCK_MODE, LIVE_MODE),
            horizontal=True,
            key=MODE_KEY,
            label_visibility="collapsed",
        )


def main() -> None:
    """Render the minimal Home or active conversation-and-Workspace layout."""

    st.set_page_config(page_title="Wealth OS Experience", layout="wide")
    apply_styles()
    mode = _prototype_mode()
    if mode == LIVE_MODE:
        selected = st.session_state.get(LIVE_GOAL_KEY)
        if isinstance(selected, GoalId):
            _render_live_active(selected)
        else:
            _render_live_home()
        return
    current = _state()
    if current.is_home:
        _render_home(current)
    else:
        _render_active(current)


if __name__ == "__main__":
    main()

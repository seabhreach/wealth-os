"""Streamlit entry point for the separate mock-only Experience shell."""

from __future__ import annotations

import streamlit as st

from experience.components.chat import (
    render_choice_chips,
    render_contextual_actions,
    render_messages,
)
from experience.components.recent_workspaces import render_recent_workspaces
from experience.components.workspace_header import render_workspace_header
from experience.components.workspace_sections import render_workspace_sections
from experience.conversation import (
    advance_with_choice,
    advance_with_text,
    available_choices,
    contextual_actions,
    empty_state,
    start_conversation,
)
from experience.models import PrototypeState
from experience.navigation import opening_prompt
from experience.styles import apply_styles
from experience.workspace import visible_sections, workspace_status, workspace_title

STATE_KEY = "wealth_os_experience_state"


def _state() -> PrototypeState:
    stored = st.session_state.get(STATE_KEY)
    if isinstance(stored, PrototypeState):
        return stored
    initial = empty_state()
    st.session_state[STATE_KEY] = initial
    return initial


def _save(state: PrototypeState) -> None:
    st.session_state[STATE_KEY] = state


def _render_home() -> None:
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
        selected_goal = render_recent_workspaces()
        st.markdown(
            '<div class="wos-prototype-note">Illustrative prototype · Mock data only</div>',
            unsafe_allow_html=True,
        )

    if opening_message:
        _save(start_conversation(opening_message))
        st.rerun()
    if selected_goal is not None:
        _save(start_conversation(opening_prompt(selected_goal), selected_goal))
        st.rerun()


def _render_active(state: PrototypeState) -> None:
    conversation_column, workspace_column = st.columns((0.92, 1.08), gap="large")
    with conversation_column:
        st.markdown('<div class="wos-pane-label">Conversation</div>', unsafe_allow_html=True)
        render_messages(state.messages)
        render_contextual_actions(contextual_actions(state))
        selected_choice = render_choice_chips(available_choices(state), state.step_index)
        follow_up = st.chat_input(
            "Share an answer or ask a follow-up",
            key=f"active-chat-input-{state.step_index}",
        )
        if selected_choice is not None:
            _save(advance_with_choice(state, selected_choice))
            st.rerun()
        if follow_up:
            _save(advance_with_text(state, follow_up))
            st.rerun()

    with workspace_column:
        render_workspace_header(workspace_title(state), workspace_status(state))
        render_workspace_sections(visible_sections(state))
        st.markdown(
            (
                '<div class="wos-prototype-note">Illustrative mock Workspace · '
                "No live financial integration</div>"
            ),
            unsafe_allow_html=True,
        )


def main() -> None:
    """Render the minimal Home or active conversation-and-Workspace layout."""

    st.set_page_config(page_title="Wealth OS Experience", layout="wide")
    apply_styles()
    current = _state()
    if current.is_home:
        _render_home()
    else:
        _render_active(current)


if __name__ == "__main__":
    main()

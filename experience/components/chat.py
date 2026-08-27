"""Conversation rendering without avatar or card dependencies."""

from __future__ import annotations

from html import escape

import streamlit as st

from experience.models import Choice, ContextAction, GoalId, Message, MessageRole
from experience.widget_keys import widget_key


def render_messages(messages: tuple[Message, ...]) -> None:
    """Render message identity through typography rather than avatars."""

    previous_role: MessageRole | None = None
    for message in messages:
        author = ""
        if message.role is MessageRole.USER or message.role is not previous_role:
            author = f'<div class="wos-message-author">{escape(message.role.value)}</div>'
        st.markdown(
            (
                f'<div class="wos-message wos-message-{message.role.name.casefold()}">'
                f"{author}"
                f'<div class="wos-message-body">{escape(message.content)}</div>'
                "</div>"
            ),
            unsafe_allow_html=True,
        )
        previous_role = message.role


def render_choice_chips(
    choices: tuple[Choice, ...],
    workspace_id: str,
    goal_id: GoalId,
    step_key: str,
) -> str | None:
    """Render subtle choice chips and return a selected value immediately."""

    if not choices:
        return None
    columns = st.columns(len(choices))
    for index, choice in enumerate(choices):
        if columns[index].button(
            choice.label,
            key=widget_key(
                "choice",
                workspace_id,
                goal_id.value,
                step_key,
                index,
                choice.value,
            ),
            use_container_width=True,
        ):
            return choice.value
    return None


def render_contextual_actions(
    actions: tuple[ContextAction, ...],
    workspace_id: str,
    goal_id: GoalId,
    step_key: str,
) -> ContextAction | None:
    """Render tiny contextual actions as understated clickable links."""

    if not actions:
        return None
    columns = st.columns((*(1 for _ in actions), 4))
    for index, action in enumerate(actions):
        if columns[index].button(
            action.value,
            key=widget_key(
                "context",
                workspace_id,
                goal_id.value,
                step_key,
                index,
                action.name,
            ),
            type="tertiary",
        ):
            return action
    return None

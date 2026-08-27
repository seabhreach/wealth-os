"""Conversation rendering without avatar or card dependencies."""

from __future__ import annotations

from html import escape

import streamlit as st

from experience.models import Choice, ContextAction, Message


def render_messages(messages: tuple[Message, ...]) -> None:
    """Render message identity through typography rather than avatars."""

    for message in messages:
        st.markdown(
            (
                '<div class="wos-message">'
                f'<div class="wos-message-author">{escape(message.role.value)}</div>'
                f'<div class="wos-message-body">{escape(message.content)}</div>'
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def render_choice_chips(choices: tuple[Choice, ...], state_token: str) -> str | None:
    """Render subtle choice chips and return a selected value immediately."""

    if not choices:
        return None
    columns = st.columns(len(choices))
    for index, choice in enumerate(choices):
        if columns[index].button(
            choice.label,
            key=f"choice-{state_token}-{choice.value}",
            use_container_width=True,
        ):
            return choice.value
    return None


def render_contextual_actions(
    actions: tuple[ContextAction, ...], state_token: str
) -> ContextAction | None:
    """Render tiny contextual actions as understated clickable links."""

    if not actions:
        return None
    columns = st.columns((*(1 for _ in actions), 4))
    for index, action in enumerate(actions):
        if columns[index].button(
            action.value,
            key=f"context-{state_token}-{action.name}",
            type="tertiary",
        ):
            return action
    return None

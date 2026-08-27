"""Conversation rendering without avatar or card dependencies."""

from __future__ import annotations

from html import escape

import streamlit as st

from experience.models import Choice, Message


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


def render_choice_chips(choices: tuple[Choice, ...], step_index: int) -> str | None:
    """Render subtle choice chips and return a selected value immediately."""

    if not choices:
        return None
    columns = st.columns(len(choices))
    for index, choice in enumerate(choices):
        if columns[index].button(
            choice.label,
            key=f"choice-{step_index}-{choice.value}",
            use_container_width=True,
        ):
            return choice.value
    return None


def render_contextual_actions(actions: tuple[str, ...]) -> None:
    """Render tiny contextual actions as understated text links."""

    if not actions:
        return
    items = "".join(f"<span>{escape(action)}</span>" for action in actions)
    st.markdown(f'<div class="wos-context-actions">{items}</div>', unsafe_allow_html=True)

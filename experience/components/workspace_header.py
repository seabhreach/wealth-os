"""Workspace identity and progress header."""

from __future__ import annotations

from html import escape

import streamlit as st


def render_workspace_header(title: str, status: str) -> None:
    """Render the minimal initial Workspace header."""

    st.markdown(
        (
            '<div class="wos-workspace">'
            '<div class="wos-pane-label">Workspace</div>'
            f'<div class="wos-workspace-title">{escape(title)}</div>'
            f'<div class="wos-status">{escape(status)}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

"""Progressive mock evidence sections for the active Workspace."""

from __future__ import annotations

from html import escape

import streamlit as st

from experience.models import WorkspaceSection


def render_workspace_sections(sections: tuple[WorkspaceSection, ...]) -> None:
    """Render only sections unlocked by the scripted conversation."""

    for section in sections:
        picture_rows = "".join(
            (
                '<div class="wos-picture-row">'
                f'<span class="wos-row-label">{escape(item.label)}</span>'
                f"<span>{escape(item.value)}</span>"
                f'<span class="wos-row-status">{escape(item.status)}</span>'
                "</div>"
            )
            for item in section.picture_items
        )
        evidence_rows = "".join(
            (
                '<div class="wos-evidence-row">'
                f'<span class="wos-row-label">{escape(label)}</span>'
                f"<span>{escape(value)}</span>"
                "</div>"
            )
            for label, value in section.evidence
        )
        st.markdown(
            (
                '<section class="wos-section">'
                f"<h3>{escape(section.title)}</h3>"
                f"<p>{escape(section.summary)}</p>"
                f"{picture_rows}{evidence_rows}"
                "</section>"
            ),
            unsafe_allow_html=True,
        )

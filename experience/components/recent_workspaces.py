"""Minimal recent Workspace links for Home."""

from __future__ import annotations

import streamlit as st

from experience.models import GoalId
from experience.navigation import recent_workspaces


def render_recent_workspaces() -> GoalId | None:
    """Render understated recent Workspace links and return a selection."""

    st.markdown('<div class="wos-recent-heading">Recent Workspaces</div>', unsafe_allow_html=True)
    selected: GoalId | None = None
    columns = st.columns(5)
    for index, (goal_id, title) in enumerate(recent_workspaces()):
        if columns[index].button(title, key=f"recent-{goal_id.value}", use_container_width=True):
            selected = goal_id
    return selected

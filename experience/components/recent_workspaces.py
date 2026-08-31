"""Minimal recent Workspace links for Home."""

from __future__ import annotations

import streamlit as st

from experience.models import GoalId
from experience.navigation import RecentWorkspace, recent_workspaces
from experience.widget_keys import widget_key


def render_recent_workspaces() -> GoalId | None:
    """Render understated recent Workspace links and return a selection."""

    st.markdown('<div class="wos-recent-heading">Recent Workspaces</div>', unsafe_allow_html=True)
    selected: GoalId | None = None
    workspaces = recent_workspaces()
    for row in _workspace_pairs(workspaces):
        columns = st.columns(2, gap="medium")
        for index, workspace in enumerate(row):
            with columns[index].container(border=True):
                st.markdown(
                    (
                        '<div class="wos-recent-card">'
                        f'<div class="wos-recent-title">{workspace.title}</div>'
                        f'<div class="wos-recent-subtitle">{workspace.subtitle}</div>'
                        f'<div class="wos-recent-status">{workspace.status}</div>'
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )
                if st.button(
                    "Open workspace",
                    key=widget_key("recent", workspace.goal_id.value),
                    type="tertiary",
                ):
                    selected = workspace.goal_id
    return selected


def _workspace_pairs(
    workspaces: tuple[RecentWorkspace, ...],
) -> tuple[tuple[RecentWorkspace, ...], ...]:
    """Group navigation records without financial or presentation arithmetic."""

    iterator = iter(workspaces)
    rows: list[tuple[RecentWorkspace, ...]] = []
    while True:
        first = next(iterator, None)
        if first is None:
            return tuple(rows)
        second = next(iterator, None)
        rows.append((first,) if second is None else (first, second))

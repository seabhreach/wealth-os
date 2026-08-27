"""Workspace projections over immutable mock conversation state."""

from __future__ import annotations

from experience.mock_data import journey_for
from experience.models import PrototypeState, WorkspaceSection


def workspace_title(state: PrototypeState) -> str:
    """Return the active question-focused Workspace title."""

    if state.active_goal is None:
        return ""
    return journey_for(state.active_goal).title


def workspace_status(state: PrototypeState) -> str:
    """Return a calm progress status without implying completion."""

    if state.active_goal is None:
        return ""
    revealed = len(state.revealed_sections)
    if revealed == 0:
        return journey_for(state.active_goal).initial_status
    if revealed == 1:
        return "Building your first useful view"
    if revealed < 3:
        return "Refining the outlook"
    return "Illustrative workspace ready"


def visible_sections(state: PrototypeState) -> tuple[WorkspaceSection, ...]:
    """Return only evidence revealed by conversation progress."""

    if state.active_goal is None:
        return ()
    journey = journey_for(state.active_goal)
    visible = set(state.revealed_sections)
    return tuple(section for section in journey.sections if section.key in visible)

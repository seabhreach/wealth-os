"""Minimal navigation data for recent mock Workspaces."""

from __future__ import annotations

from experience.mock_data import all_journeys, journey_for
from experience.models import GoalId


def recent_workspaces() -> tuple[tuple[GoalId, str], ...]:
    """Return the five recovered recent Workspace examples."""

    return tuple((journey.goal_id, journey.recent_title) for journey in all_journeys())


def opening_prompt(goal_id: GoalId) -> str:
    """Return the example question associated with a recent Workspace."""

    return journey_for(goal_id).example_prompt

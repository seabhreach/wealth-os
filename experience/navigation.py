"""Minimal navigation data for recent mock Workspaces."""

from __future__ import annotations

from dataclasses import dataclass

from experience.mock_data import all_journeys, journey_for
from experience.models import GoalId


@dataclass(frozen=True, slots=True)
class RecentWorkspace:
    """Customer-facing context for one saved illustrative Workspace."""

    goal_id: GoalId
    title: str
    subtitle: str
    status: str


_SUBTITLES = {
    GoalId.RETIRE_EARLIER: "Age 58 compared with the current plan",
    GoalId.INVESTMENT_PROPERTY: "Planned purchase and liquidity trade-off",
    GoalId.EMPLOYER_EQUITY: "Retain and sell-on-vest illustrations",
    GoalId.HIGHER_SPENDING: "A higher retirement-spending comparison",
    GoalId.CASH_DECLINE: "Why cash changes after retirement",
}


def recent_workspaces() -> tuple[RecentWorkspace, ...]:
    """Return the five recovered recent Workspace examples."""

    return tuple(
        RecentWorkspace(
            journey.goal_id,
            journey.recent_title,
            _SUBTITLES[journey.goal_id],
            "Ready to reopen",
        )
        for journey in all_journeys()
    )


def opening_prompt(goal_id: GoalId) -> str:
    """Return the example question associated with a recent Workspace."""

    return journey_for(goal_id).example_prompt

"""Workspace projections over immutable mock conversation state."""

from __future__ import annotations

from dataclasses import replace

from experience.mock_data import journey_for
from experience.models import PictureItem, PrototypeState, WorkspaceSection

_ANSWER_SECTIONS: dict[str, tuple[str, str, frozenset[str]]] = {
    "retire-scope-self": ("retire-scope", "Planning scope", frozenset()),
    "retire-scope-household": ("retire-scope", "Planning scope", frozenset()),
    "retire-user-age": ("retire-user-age", "Your age", frozenset()),
    "retire-partner-age": ("retire-partner-age", "Partner age", frozenset()),
    "retire-target": ("retire-target", "Explored age", frozenset({"Explored age"})),
    "retire-resources": (
        "retire-resources",
        "Opening resources",
        frozenset({"Opening resources"}),
    ),
    "property-timing": ("property-timing", "Purchase year", frozenset()),
    "property-price": ("property-price", "Purchase price", frozenset()),
    "property-rent": (
        "property-rent",
        "Rent and growth",
        frozenset({"Net rent", "Value growth"}),
    ),
    "equity-position": ("equity-position", "Employer-equity value", frozenset()),
    "equity-policy": ("equity-policy", "Baseline policy", frozenset({"Baseline"})),
    "spending-baseline": ("spending-baseline", "Baseline spending", frozenset()),
    "spending-higher": ("spending-higher", "Higher spending", frozenset()),
    "spending-permanent": ("spending-timing", "Duration", frozenset()),
    "spending-temporary": ("spending-timing", "Duration", frozenset()),
    "spending-duration": ("spending-duration", "Higher-spending period", frozenset()),
    "spending-basis": ("spending-basis", "Value basis", frozenset({"Basis"})),
}


def workspace_title(state: PrototypeState) -> str:
    """Return the active question-focused Workspace title."""

    if state.active_goal is None:
        return ""
    return journey_for(state.active_goal).title


def workspace_status(state: PrototypeState) -> str:
    """Return a calm progress status without implying completion."""

    if state.active_goal is None:
        return ""
    if state.refinement_performed:
        return "Illustrative workspace refined"
    if state.enough_information:
        return "Illustrative first view ready"
    revealed = len(state.revealed_sections)
    if revealed == 0:
        return journey_for(state.active_goal).initial_status
    if revealed == 1:
        return "Building your first useful view"
    if revealed < 3:
        return "Refining the outlook"
    return "Building the initial view"


def visible_sections(state: PrototypeState) -> tuple[WorkspaceSection, ...]:
    """Return only evidence revealed by conversation progress."""

    if state.active_goal is None:
        return ()
    journey = journey_for(state.active_goal)
    visible = set(state.revealed_sections)
    return tuple(
        _with_captured_answer(section, state)
        for section in journey.sections
        if section.key in visible
    )


def _with_captured_answer(section: WorkspaceSection, state: PrototypeState) -> WorkspaceSection:
    mapping = _ANSWER_SECTIONS.get(section.key)
    if mapping is None:
        return section
    step_key, label, replaced_evidence = mapping
    answer = next(
        (item for item in reversed(state.captured_answers) if item.step_key == step_key),
        None,
    )
    if answer is None:
        return section
    return replace(
        section,
        picture_items=(PictureItem(label, answer.display_value, answer.status),),
        evidence=tuple(item for item in section.evidence if item[0] not in replaced_evidence),
    )

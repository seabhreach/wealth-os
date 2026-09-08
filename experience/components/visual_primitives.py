"""Small theme-aware HTML primitives shared by focused visual workspaces."""

from __future__ import annotations

from html import escape
from typing import TypeVar

from experience.live.models import LiveEvidence

EvidenceT = TypeVar("EvidenceT", bound=LiveEvidence)


def metric_grid(
    items: tuple[tuple[str, str, str], ...],
    *,
    class_name: str = "wos-metric-grid",
) -> str:
    """Return a semantic metric-card grid with escaped customer-facing content."""

    cards = "".join(
        '<article class="wos-metric-card">'
        f"<span>{escape(label)}</span>"
        f"<strong>{escape(value)}</strong>"
        f"<small>{escape(detail)}</small>"
        "</article>"
        for label, value, detail in items
    )
    return f'<section class="{escape(class_name)}">{cards}</section>'


def section_heading(title: str, summary: str) -> str:
    """Return one consistent section heading for visual-first pages."""

    return f'<div class="wos-focus-heading"><h2>{escape(title)}</h2><p>{escape(summary)}</p></div>'


def outcome_hero(kicker: str, title: str, answer: str) -> str:
    """Return the shared answer-first hero used by decision workspaces."""

    return (
        '<section class="wos-decision-hero">'
        f"<span>{escape(kicker)}</span>"
        f"<h2>{escape(title)}</h2>"
        f"<p>{escape(answer)}</p>"
        "</section>"
    )


def evidence_of(  # noqa: UP047 -- runtime remains compatible with Python 3.12
    evidence: dict[str, LiveEvidence],
    evidence_id: str,
    expected_type: type[EvidenceT],
) -> EvidenceT:
    """Return one typed evidence item or fail at the presentation boundary."""

    item = evidence[evidence_id]
    if not isinstance(item, expected_type):
        raise TypeError(f"{evidence_id} is not {expected_type.__name__}.")
    return item

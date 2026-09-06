"""Small theme-aware HTML primitives shared by focused visual workspaces."""

from __future__ import annotations

from html import escape


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

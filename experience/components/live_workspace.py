# ruff: noqa: E501
"""Presentation-only renderer for immutable live evidence."""

from __future__ import annotations

from html import escape

import streamlit as st

from experience.display import format_display_value, format_table_value
from experience.live.models import (
    AssumptionEvidence,
    ComparisonEvidence,
    FinancialStatementEvidence,
    InsightEvidence,
    LimitationEvidence,
    LiveEvidence,
    LiveWorkspace,
    MetricEvidence,
    NarrativeEvidence,
    StrategyEvidence,
    TableEvidence,
    TimelineEvidence,
)


def render_live_workspace(workspace: LiveWorkspace) -> None:
    """Render a clean full-width interim Workspace from immutable evidence."""

    st.markdown('<main class="wos-interim-workspace">', unsafe_allow_html=True)
    st.markdown('<div class="wos-visual-kicker">Workspace</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="wos-workspace-title">{escape(workspace.title)}</div>', unsafe_allow_html=True
    )

    primary, details, supporting = _evidence_groups(workspace.evidence)
    for evidence in primary:
        _render_evidence(evidence)
    if details:
        st.markdown(
            '<div class="wos-visual-section-heading"><h2>Explanation</h2></div>',
            unsafe_allow_html=True,
        )
        for evidence in details[:2]:
            _render_evidence(evidence)
    with st.expander("About this projection", expanded=False):
        if workspace.picture_item_keys:
            st.markdown("#### Assumptions")
            _render_financial_picture(workspace)
        remaining = details[2:]
        if remaining:
            st.markdown("#### Supporting figures")
            for evidence in remaining:
                _render_evidence(evidence)
        limitations = tuple(item for item in supporting if isinstance(item, LimitationEvidence))
        assumptions = tuple(item for item in supporting if not isinstance(item, LimitationEvidence))
        for evidence in assumptions:
            _render_evidence(evidence)
        if limitations:
            st.markdown("#### Limitations")
            for evidence in limitations:
                _render_evidence(evidence)
    st.markdown("</main>", unsafe_allow_html=True)


def _evidence_groups(
    evidence: tuple[LiveEvidence, ...],
) -> tuple[tuple[LiveEvidence, ...], tuple[LiveEvidence, ...], tuple[LiveEvidence, ...]]:
    supporting_types = (AssumptionEvidence, StrategyEvidence, LimitationEvidence)
    supporting = tuple(item for item in evidence if isinstance(item, supporting_types))
    candidates = tuple(item for item in evidence if not isinstance(item, supporting_types))
    primary: list[LiveEvidence] = []
    details: list[LiveEvidence] = []
    for item in candidates:
        if (
            isinstance(item, (FinancialStatementEvidence, TableEvidence, TimelineEvidence))
            or len(primary) >= 3
        ):
            details.append(item)
        else:
            primary.append(item)
    return tuple(primary), tuple(details), supporting


def _render_evidence(evidence: LiveEvidence) -> None:
    if isinstance(evidence, NarrativeEvidence):
        _section(evidence.title, evidence.text)
    elif isinstance(evidence, ComparisonEvidence):
        rows = (
            (evidence.baseline_label, format_display_value(evidence.baseline_value, evidence.unit)),
            (evidence.scenario_label, format_display_value(evidence.scenario_value, evidence.unit)),
        )
        _rows(evidence.title, evidence.metric, rows)
    elif isinstance(evidence, MetricEvidence):
        _rows(
            evidence.title,
            evidence.label,
            ((evidence.period or "Value", format_display_value(evidence.value, evidence.unit)),),
        )
    elif isinstance(evidence, TimelineEvidence):
        _rows(
            evidence.title,
            evidence.label,
            tuple(
                (str(point.period), format_display_value(point.value, evidence.unit))
                for point in evidence.points
            ),
        )
    elif isinstance(evidence, TableEvidence):
        _table(evidence)
    elif isinstance(evidence, FinancialStatementEvidence):
        statement_rows: tuple[tuple[str, str], ...] = (
            ("Opening cash", format_display_value(evidence.opening_cash, "EUR")),
            *((label, format_display_value(value, "EUR")) for label, value in evidence.inflows),
            *((label, format_display_value(value, "EUR")) for label, value in evidence.outflows),
            ("Closing cash", format_display_value(evidence.closing_cash, "EUR")),
        )
        _rows(
            evidence.title,
            f"Existing annual trace · {evidence.calendar_year}",
            statement_rows,
        )
    elif isinstance(evidence, AssumptionEvidence):
        _rows(
            evidence.title,
            "From your Financial Picture",
            ((evidence.label, format_display_value(evidence.value)),),
        )
    elif isinstance(evidence, StrategyEvidence):
        _rows(
            evidence.title,
            evidence.proposed_update,
            (("Baseline", evidence.baseline), ("Scenario", evidence.scenario)),
        )
    elif isinstance(evidence, InsightEvidence):
        _section(evidence.title, evidence.observation)
    elif isinstance(evidence, LimitationEvidence):
        _section(evidence.title, evidence.text)


def _render_financial_picture(workspace: LiveWorkspace) -> None:
    wanted = set(workspace.picture_item_keys)
    items = tuple(item for item in workspace.financial_picture.items if item.key in wanted)
    if not items:
        return
    rows = tuple(
        (
            item.label,
            format_display_value(item.value, _unit_for_key(item.key)),
        )
        for item in items
    )
    _rows("Relevant Financial Picture", "Values used for this illustration", rows)


def _section(title: str, summary: str) -> None:
    st.markdown(
        f'<section class="wos-section"><h3>{escape(title)}</h3><p>{escape(summary)}</p></section>',
        unsafe_allow_html=True,
    )


def _rows(title: str, summary: str, rows: tuple[tuple[str, str], ...]) -> None:
    rendered = "".join(
        '<div class="wos-evidence-row">'
        f'<span class="wos-row-label">{escape(label)}</span>'
        f"<span>{escape(value)}</span>"
        "</div>"
        for label, value in rows
    )
    st.markdown(
        f'<section class="wos-section"><h3>{escape(title)}</h3><p>{escape(summary)}</p>{rendered}</section>',
        unsafe_allow_html=True,
    )


def _table(evidence: TableEvidence) -> None:
    header = "".join(f"<th>{escape(column)}</th>" for column in evidence.columns)
    rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{escape(format_table_value(value, evidence.columns[index], str(row[0])))}</td>"
            for index, value in enumerate(row)
        )
        + "</tr>"
        for row in evidence.rows
    )
    footnote = f"<p>{escape(evidence.footnote)}</p>" if evidence.footnote else ""
    st.markdown(
        f'<section class="wos-section"><h3>{escape(evidence.title)}</h3><div class="wos-live-table"><table><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table></div>{footnote}</section>',
        unsafe_allow_html=True,
    )


def _unit_for_key(key: str) -> str:
    if key in {"cash", "investments", "retirement_spending"} or key.startswith("pension:"):
        return "EUR"
    if key.endswith(":price") or key.endswith(":rent"):
        return "EUR"
    if key == "inflation":
        return "ratio"
    return ""

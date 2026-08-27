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
    """Arrange existing evidence answer-first without deriving financial values."""

    st.markdown('<div class="wos-pane-label">Workspace</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="wos-workspace-title">{escape(workspace.title)}</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="wos-live-badge">Live baseline · read only</div>', unsafe_allow_html=True
    )

    primary, details, supporting = _evidence_groups(workspace.evidence)
    for evidence in primary:
        _render_evidence(evidence)
    if details:
        with st.expander("Supporting details", expanded=False):
            for evidence in details:
                _render_evidence(evidence)
    if workspace.picture_item_keys:
        with st.expander("Financial Picture details", expanded=False):
            _render_financial_picture(workspace)
    for evidence in supporting:
        _render_evidence(evidence)
    _render_provenance(workspace)


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
            f"{evidence.source} · {evidence.confidence.value}",
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
            f"{format_display_value(item.value, _unit_for_key(item.key))} · {item.status.value}",
        )
        for item in items
    )
    _rows("Relevant Financial Picture", "Baseline data · read only", rows)


def _render_provenance(workspace: LiveWorkspace) -> None:
    provenance = workspace.provenance
    with st.expander("Provenance", expanded=False):
        st.markdown(
            "\n".join(
                (
                    f"- Baseline: `{provenance.baseline_identifier}`",
                    f"- Financial Picture: `{provenance.financial_picture_fingerprint}`",
                    f"- Goal: `{provenance.goal_id.value}`",
                    f"- Overrides: `{dict(provenance.scenario_overrides)}`",
                    f"- Simulation: `{provenance.simulation_version}`",
                    f"- Tax rules: `{provenance.tax_rule_identifier or 'disabled'}`",
                    f"- Result: `{provenance.result_fingerprint}`",
                )
            )
        )


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

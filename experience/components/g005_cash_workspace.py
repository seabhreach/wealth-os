# ruff: noqa: E501
"""Focused selected-year cash explanation workspace."""

from __future__ import annotations

from decimal import Decimal
from html import escape

import streamlit as st

from experience.components.visual_primitives import (
    evidence_of,
    metric_grid,
    outcome_hero,
    section_heading,
)
from experience.display import format_display_value, format_table_value
from experience.live.models import (
    AssumptionEvidence,
    FinancialStatementEvidence,
    InsightEvidence,
    LimitationEvidence,
    LiveEvidence,
    LiveWorkspace,
    NarrativeEvidence,
    TableEvidence,
    TimelineEvidence,
)


def render_cash_workspace(workspace: LiveWorkspace) -> str | None:
    """Render a causal cash explanation for the selected projection year."""

    evidence = {item.evidence_id: item for item in workspace.evidence}
    answer = evidence_of(evidence, "g005-answer", NarrativeEvidence)
    statement = evidence_of(evidence, "g005-statement", FinancialStatementEvidence)
    transition = evidence_of(evidence, "g005-transition", InsightEvidence)

    st.markdown('<main class="wos-decision-workspace">', unsafe_allow_html=True)
    st.markdown(
        '<div class="wos-visual-kicker">Cash explanation workspace</div>', unsafe_allow_html=True
    )
    st.markdown(
        f'<h1 class="wos-decision-title">{escape(workspace.title)}</h1>', unsafe_allow_html=True
    )
    st.markdown(
        outcome_hero(
            f"Cash movement · {statement.calendar_year}",
            answer.text,
            transition.observation,
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="wos-scenario-context">Selected-year explanation · your Financial Picture is unchanged</p>',
        unsafe_allow_html=True,
    )
    primary_reduction = _primary_reduction(statement)
    st.markdown(
        metric_grid(
            (
                (
                    "Opening cash",
                    format_display_value(statement.opening_cash, "EUR"),
                    f"Start of {statement.calendar_year}",
                ),
                (
                    "Closing cash",
                    format_display_value(statement.closing_cash, "EUR"),
                    f"End of {statement.calendar_year}",
                ),
                (
                    primary_reduction[0],
                    format_display_value(primary_reduction[1], "EUR"),
                    "Direct cash-account reduction",
                ),
                (
                    "Total liquid assets",
                    format_display_value(statement.liquid_assets, "EUR"),
                    "Cash + taxable investments + employer equity",
                ),
            ),
            class_name="wos-four-metric-grid",
        ),
        unsafe_allow_html=True,
    )
    action: str | None = None
    if st.button("Explain this", key="explain-g005-answer", type="tertiary"):
        action = "explain:g005-answer,g005-statement,g005-transition"

    st.markdown(
        section_heading(
            "Opening-to-closing cash reconciliation",
            "Only movements that directly change the cash account appear in this bridge; recurring income is shown separately as funding context.",
        ),
        unsafe_allow_html=True,
    )
    _render_cash_bridge(statement)
    _render_funding_context(evidence_of(evidence, "g005-funding", TableEvidence))
    if st.button("Explain this", key="explain-g005-reconciliation", type="tertiary"):
        action = "explain:g005-statement,g005-funding,g005-transition"

    st.markdown(
        section_heading(
            "Cash through the wider plan",
            f"The selected year {statement.calendar_year} sits within the full deterministic cash trajectory and its major funding events.",
        ),
        unsafe_allow_html=True,
    )
    _render_cash_chart(evidence)
    _render_plan_milestones(
        evidence_of(evidence, "g005-milestones", TableEvidence),
        statement.calendar_year,
    )
    if st.button("Explain this", key="explain-g005-timeline", type="tertiary"):
        action = "explain:g005-cash-series,g005-milestones,g005-selected-year"

    _render_assumptions(evidence)
    with st.expander("About this projection", expanded=False):
        limitation = evidence_of(evidence, "g005-limitation", LimitationEvidence)
        st.markdown(
            "Changing the selected year rebuilds the narrative, cash bridge, funding context, milestones and explanation references from that year's trace."
        )
        st.markdown(f"**Evidence boundary:** {limitation.text}")
    st.markdown("</main>", unsafe_allow_html=True)
    return action


def _primary_reduction(statement: FinancialStatementEvidence) -> tuple[str, Decimal]:
    property_purchase = next(
        (value for label, value in statement.cash_decreases if label == "Property purchase"),
        Decimal("0"),
    )
    cash_used = next(
        (value for label, value in statement.cash_decreases if label == "Cash used for spending"),
        Decimal("0"),
    )
    if property_purchase:
        return "Property purchase", property_purchase
    return "Cash used for spending", cash_used


def _render_cash_bridge(statement: FinancialStatementEvidence) -> None:
    steps = (
        ("Opening", "Opening cash", statement.opening_cash, ""),
        *(("Increase", label, value, "+") for label, value in statement.cash_increases if value),
        *(("Reduction", label, value, "-") for label, value in statement.cash_decreases if value),
        ("Closing", "Closing cash", statement.closing_cash, "="),
    )
    rendered = "".join(
        '<article class="wos-cash-step">'
        f"<span>{escape(kind)}</span>"
        f"<h3>{escape(label)}</h3>"
        f"<strong>{escape(sign)}{escape(format_display_value(value, 'EUR'))}</strong>"
        "</article>"
        for kind, label, value, sign in steps
    )
    st.markdown(f'<section class="wos-cash-bridge">{rendered}</section>', unsafe_allow_html=True)


def _render_funding_context(table: TableEvidence) -> None:
    wanted = {
        "Rental income",
        "Private pension income",
        "State Pension",
        "Estimated income tax",
        "Estimated USC",
        "Cash used",
        "Taxable investments sold",
        "Unfunded amount",
    }
    cells = "".join(
        '<div class="wos-context-cell">'
        f"<span>{escape(str(row[0]))}</span>"
        f"<strong>{escape(format_table_value(row[1], 'Existing reporting value', str(row[0])))}</strong>"
        "</div>"
        for row in table.rows
        if str(row[0]) in wanted
    )
    st.markdown(
        '<div class="wos-subsection-label">Funding context for the selected year</div>'
        f'<section class="wos-context-grid">{cells}</section>',
        unsafe_allow_html=True,
    )


def _render_cash_chart(evidence: dict[str, LiveEvidence]) -> None:
    timeline = evidence_of(evidence, "g005-cash-series", TimelineEvidence)
    st.line_chart(
        {
            "Year": [point.period for point in timeline.points],
            "Closing cash": [float(point.value) for point in timeline.points],
        },
        x="Year",
        y="Closing cash",
        color=None,
    )


def _render_plan_milestones(table: TableEvidence, selected_year: int) -> None:
    rendered = "".join(
        '<article class="wos-milestone-card'
        f'{" wos-selected-milestone" if str(row[1]) == str(selected_year) else ""}">'
        f"<span>{escape(str(row[1]))}</span>"
        f"<h3>{escape(str(row[0]))}</h3>"
        f"<p>{escape(str(row[2]))}</p>"
        "</article>"
        for row in table.rows
    )
    st.markdown(
        '<div class="wos-subsection-label">Major plan events</div>'
        f'<section class="wos-milestone-grid">{rendered}</section>',
        unsafe_allow_html=True,
    )


def _render_assumptions(evidence: dict[str, LiveEvidence]) -> None:
    selected = evidence_of(evidence, "g005-selected-year", AssumptionEvidence)
    cash_return = evidence_of(evidence, "g005-cash-return", AssumptionEvidence)
    funding = evidence_of(evidence, "g005-funding-order", AssumptionEvidence)
    st.markdown(
        section_heading(
            "Assumptions and evidence boundary",
            "The selected year is a workspace choice; cash treatment and funding order are existing projection rules.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        metric_grid(
            (
                ("Selected year", str(selected.value), selected.source),
                ("Cash return", str(cash_return.value), cash_return.source),
                ("Funding order", str(funding.value), funding.source),
            ),
            class_name="wos-three-metric-grid",
        ),
        unsafe_allow_html=True,
    )

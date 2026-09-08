# ruff: noqa: E501
"""Focused higher-retirement-spending workspace."""

from __future__ import annotations

from html import escape

import streamlit as st

from experience.components.visual_primitives import (
    evidence_of,
    metric_grid,
    outcome_hero,
    section_heading,
)
from experience.display import format_display_value
from experience.live.models import (
    AssumptionEvidence,
    ComparisonEvidence,
    LimitationEvidence,
    LiveEvidence,
    LiveWorkspace,
    MetricEvidence,
    NarrativeEvidence,
    TableEvidence,
    TimelineEvidence,
)


def render_spending_workspace(workspace: LiveWorkspace) -> str | None:
    """Render the higher-spending trade-off from immutable scenario evidence."""

    evidence = {item.evidence_id: item for item in workspace.evidence}
    answer = evidence_of(evidence, "g004-answer", NarrativeEvidence)
    input_basis = evidence_of(evidence, "g004-input-basis", AssumptionEvidence)
    spending = evidence_of(evidence, "g004-spending", ComparisonEvidence)
    liquidity = evidence_of(evidence, "g004-liquid", ComparisonEvidence)
    net_worth = evidence_of(evidence, "g004-final-worth", ComparisonEvidence)
    unfunded = evidence_of(evidence, "g004-unfunded", MetricEvidence)

    st.markdown('<main class="wos-decision-workspace">', unsafe_allow_html=True)
    st.markdown(
        '<div class="wos-visual-kicker">Retirement spending workspace</div>', unsafe_allow_html=True
    )
    st.markdown(
        f'<h1 class="wos-decision-title">{escape(workspace.title)}</h1>', unsafe_allow_html=True
    )
    st.markdown(
        outcome_hero(
            "Modelled outcome",
            _spending_headline(input_basis, liquidity, unfunded),
            answer.text,
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="wos-scenario-context">Temporary exploration · your Financial Picture is unchanged</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        metric_grid(
            (
                (
                    "Target spending",
                    format_display_value(input_basis.value, "EUR/year"),
                    "In today's money · your explored input",
                ),
                (
                    "First retirement year",
                    format_display_value(spending.scenario_value, spending.unit),
                    "Nominal amount after modelled inflation",
                ),
                (
                    "Final liquid assets",
                    format_display_value(liquidity.scenario_value, liquidity.unit),
                    f"Current spending path: {format_display_value(liquidity.baseline_value, liquidity.unit)}",
                ),
                (
                    "Final planning net worth",
                    format_display_value(net_worth.scenario_value, net_worth.unit),
                    f"Current spending path: {format_display_value(net_worth.baseline_value, net_worth.unit)}",
                ),
            ),
            class_name="wos-four-metric-grid",
        ),
        unsafe_allow_html=True,
    )
    action: str | None = None
    if st.button("Explain this", key="explain-g004-outcome", type="tertiary"):
        action = "explain:g004-answer,g004-input-basis,g004-spending,g004-liquid,g004-unfunded"

    st.markdown(
        section_heading(
            "Liquidity under higher spending",
            "The trajectory shows how the larger annual funding requirement changes remaining liquid assets through time.",
        ),
        unsafe_allow_html=True,
    )
    _render_liquid_chart(evidence)
    st.caption(
        "Current and explored spending use the same Financial Picture, return assumptions and planning horizon."
    )
    if st.button("Explain this", key="explain-g004-trajectory", type="tertiary"):
        action = "explain:g004-liquid-baseline-series,g004-liquid-scenario-series,g004-liquid"

    st.markdown(
        section_heading(
            "How the spending choice flows through the plan",
            "Today's-money intent becomes an inflation-adjusted annual requirement, then follows the existing funding order.",
        ),
        unsafe_allow_html=True,
    )
    _render_spending_flow(evidence)
    _render_milestones(evidence_of(evidence, "g004-funding-milestones", TableEvidence))
    if st.button("Explain this", key="explain-g004-funding", type="tertiary"):
        action = "explain:g004-input-basis,g004-spending,g004-funding-order,g004-funding-milestones,g004-liquid"

    _render_assumptions(evidence)
    with st.expander("About this projection", expanded=False):
        limitation = evidence_of(evidence, "g004-limitation", LimitationEvidence)
        st.markdown(
            "The explored amount is a permanent scenario input and is not persisted to the Financial Picture."
        )
        st.markdown(f"**Evidence boundary:** {limitation.text}")
    st.markdown("</main>", unsafe_allow_html=True)
    return action


def _spending_headline(
    input_basis: AssumptionEvidence,
    liquidity: ComparisonEvidence,
    unfunded: MetricEvidence,
) -> str:
    target = format_display_value(input_basis.value, "EUR/year")
    final_liquid = format_display_value(liquidity.scenario_value, liquidity.unit)
    if unfunded.value == "None":
        return f"At {target} in today's money, the plan remains funded through the horizon and ends with {final_liquid} in liquid assets."
    return f"At {target} in today's money, the plan first becomes unfunded in {unfunded.value}."


def _render_liquid_chart(evidence: dict[str, LiveEvidence]) -> None:
    baseline = evidence_of(evidence, "g004-liquid-baseline-series", TimelineEvidence)
    scenario = evidence_of(evidence, "g004-liquid-scenario-series", TimelineEvidence)
    st.line_chart(
        {
            "Year": [point.period for point in baseline.points],
            "Current spending": [float(point.value) for point in baseline.points],
            "Explored spending": [float(point.value) for point in scenario.points],
        },
        x="Year",
        y=["Current spending", "Explored spending"],
        color=None,
    )


def _render_spending_flow(evidence: dict[str, LiveEvidence]) -> None:
    input_basis = evidence_of(evidence, "g004-input-basis", AssumptionEvidence)
    spending = evidence_of(evidence, "g004-spending", ComparisonEvidence)
    funding_order = evidence_of(evidence, "g004-funding-order", AssumptionEvidence)
    unfunded = evidence_of(evidence, "g004-unfunded", MetricEvidence)
    status = (
        "Funded through horizon"
        if unfunded.value == "None"
        else f"First unfunded in {unfunded.value}"
    )
    steps = (
        (
            "1",
            "Today's-money target",
            format_display_value(input_basis.value, "EUR/year"),
            "Scenario choice",
        ),
        (
            "2",
            "First-year nominal spending",
            format_display_value(spending.scenario_value, spending.unit),
            "After inflation",
        ),
        ("3", "Funding sequence", str(funding_order.value), "Applied each retirement year"),
        ("4", "Sustainability result", status, "Deterministic outcome"),
    )
    rendered = "".join(
        '<article class="wos-flow-step">'
        f'<span class="wos-step-number">{escape(number)}</span>'
        f"<h3>{escape(title)}</h3><strong>{escape(value)}</strong><p>{escape(detail)}</p>"
        "</article>"
        for number, title, value, detail in steps
    )
    st.markdown(f'<section class="wos-decision-flow">{rendered}</section>', unsafe_allow_html=True)


def _render_milestones(table: TableEvidence) -> None:
    rendered = "".join(
        '<article class="wos-milestone-card">'
        f"<span>{escape(str(row[1]))}</span>"
        f"<h3>{escape(str(row[0]))}</h3>"
        f"<p>{escape(str(row[2]))}</p>"
        "</article>"
        for row in table.rows
    )
    st.markdown(
        '<div class="wos-subsection-label">Funding milestones</div>'
        f'<section class="wos-milestone-grid">{rendered}</section>',
        unsafe_allow_html=True,
    )


def _render_assumptions(evidence: dict[str, LiveEvidence]) -> None:
    inflation = evidence_of(evidence, "g004-inflation", AssumptionEvidence)
    retirement = evidence_of(evidence, "g004-retirement-age", AssumptionEvidence)
    funding = evidence_of(evidence, "g004-funding-order", AssumptionEvidence)
    st.markdown(
        section_heading(
            "Assumptions and limitations",
            "These inputs shape the comparison but are distinct from the calculated outcome.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        metric_grid(
            (
                (
                    "Spending inflation",
                    format_display_value(inflation.value, "ratio"),
                    inflation.source,
                ),
                ("Retirement timing", f"Age {retirement.value}", retirement.source),
                ("Funding order", str(funding.value), funding.source),
            ),
            class_name="wos-three-metric-grid",
        ),
        unsafe_allow_html=True,
    )

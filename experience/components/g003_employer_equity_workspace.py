# ruff: noqa: E501
"""Focused employer-equity concentration workspace."""

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
from experience.display import format_display_value
from experience.live.models import (
    AssumptionEvidence,
    ComparisonEvidence,
    LimitationEvidence,
    LiveEvidence,
    LiveWorkspace,
    NarrativeEvidence,
    TimelineEvidence,
)


def render_employer_equity_workspace(workspace: LiveWorkspace) -> str | None:
    """Render the concentration trade-off from immutable scenario evidence."""

    evidence = {item.evidence_id: item for item in workspace.evidence}
    answer = evidence_of(evidence, "g003-answer", NarrativeEvidence)
    concentration = evidence_of(evidence, "g003-concentration", ComparisonEvidence)
    final_equity = evidence_of(evidence, "g003-final-equity", ComparisonEvidence)
    final_worth = evidence_of(evidence, "g003-final-worth", ComparisonEvidence)

    st.markdown('<main class="wos-decision-workspace">', unsafe_allow_html=True)
    st.markdown(
        '<div class="wos-visual-kicker">Employer equity workspace</div>', unsafe_allow_html=True
    )
    st.markdown(
        f'<h1 class="wos-decision-title">{escape(workspace.title)}</h1>', unsafe_allow_html=True
    )
    st.markdown(
        outcome_hero(
            "Concentration result",
            "Retaining future employer equity leaves the investable portfolio much more concentrated in one company.",
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
                    concentration.baseline_label,
                    format_display_value(concentration.baseline_value, concentration.unit),
                    "Maximum single-employer share of investable assets",
                ),
                (
                    concentration.scenario_label,
                    format_display_value(concentration.scenario_value, concentration.unit),
                    "Maximum single-employer share of investable assets",
                ),
            ),
            class_name="wos-two-metric-grid",
        ),
        unsafe_allow_html=True,
    )
    action: str | None = None
    if st.button("Explain this", key="explain-g003-concentration", type="tertiary"):
        action = "explain:g003-answer,g003-concentration"

    st.markdown(
        section_heading(
            "Single-company exposure",
            "The filled share is employer equity; the remaining track is cash and ordinary taxable investments.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(_concentration_bars(concentration), unsafe_allow_html=True)
    _render_denominator(evidence)
    if st.button("Explain this", key="explain-g003-denominator", type="tertiary"):
        action = "explain:g003-concentration,g003-denominator,g003-denominator-value,g003-peak-year"

    st.markdown(
        section_heading(
            "Modelled wealth outcome",
            "The retain path has more employer-equity exposure and a higher projected value under the configured growth assumption. That is not a risk-adjusted recommendation.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        metric_grid(
            (
                (
                    "Final employer equity · retain",
                    format_display_value(final_equity.scenario_value, final_equity.unit),
                    f"Sell on vest: {format_display_value(final_equity.baseline_value, final_equity.unit)}",
                ),
                (
                    "Final planning net worth · retain",
                    format_display_value(final_worth.scenario_value, final_worth.unit),
                    f"Sell on vest: {format_display_value(final_worth.baseline_value, final_worth.unit)}",
                ),
            ),
            class_name="wos-two-metric-grid",
        ),
        unsafe_allow_html=True,
    )
    _render_equity_chart(evidence)
    st.caption(
        "Employer-equity value only. Pensions, property and the primary residence do not enter the concentration denominator."
    )
    if st.button("Explain this", key="explain-g003-wealth", type="tertiary"):
        action = "explain:g003-final-equity,g003-final-worth,g003-growth"

    _render_assumptions(evidence)
    with st.expander("About this projection", expanded=False):
        st.markdown(
            "This comparison changes only the future employer-equity disposal policy. It does not persist a Financial Picture update."
        )
        limitation = evidence_of(evidence, "g003-limitation", LimitationEvidence)
        st.markdown(f"**Evidence boundary:** {limitation.text}")
    st.markdown("</main>", unsafe_allow_html=True)
    return action


def _concentration_bars(evidence: ComparisonEvidence) -> str:
    rows = (
        (evidence.baseline_label, _ratio(evidence.baseline_value)),
        (evidence.scenario_label, _ratio(evidence.scenario_value)),
    )
    rendered = "".join(
        '<article class="wos-concentration-row">'
        f"<div><span>{escape(label)}</span><strong>{escape(format_display_value(value, 'ratio'))}</strong></div>"
        '<div class="wos-concentration-track" aria-hidden="true">'
        f'<i style="width:{value:.1%}"></i></div>'
        "</article>"
        for label, value in rows
    )
    return f'<section class="wos-concentration-visual">{rendered}</section>'


def _render_denominator(evidence: dict[str, LiveEvidence]) -> None:
    definition = evidence_of(evidence, "g003-denominator", AssumptionEvidence)
    values = evidence_of(evidence, "g003-denominator-value", ComparisonEvidence)
    years = evidence_of(evidence, "g003-peak-year", ComparisonEvidence)
    st.markdown(
        '<section class="wos-definition-panel"><div><span>Denominator</span>'
        f"<h3>{escape(str(definition.value))}</h3>"
        "<p>Diversified ETFs remain in the denominator but are not treated as the single-employer position.</p></div>"
        '<div class="wos-mini-grid">'
        f"<div><small>{escape(values.baseline_label)} · {escape(str(years.baseline_value))}</small><strong>{escape(format_display_value(values.baseline_value, values.unit))}</strong></div>"
        f"<div><small>{escape(values.scenario_label)} · {escape(str(years.scenario_value))}</small><strong>{escape(format_display_value(values.scenario_value, values.unit))}</strong></div>"
        "</div></section>",
        unsafe_allow_html=True,
    )


def _render_equity_chart(evidence: dict[str, LiveEvidence]) -> None:
    sell = evidence_of(evidence, "g003-sell-equity-series", TimelineEvidence)
    retain = evidence_of(evidence, "g003-retain-equity-series", TimelineEvidence)
    st.line_chart(
        {
            "Year": [point.period for point in sell.points],
            "Sell on vest": [float(point.value) for point in sell.points],
            "Retain": [float(point.value) for point in retain.points],
        },
        x="Year",
        y=["Sell on vest", "Retain"],
        color=None,
    )


def _render_assumptions(evidence: dict[str, LiveEvidence]) -> None:
    growth = evidence_of(evidence, "g003-growth", AssumptionEvidence)
    behavior = evidence_of(evidence, "g003-policy-behaviour", AssumptionEvidence)
    st.markdown(
        section_heading(
            "Assumptions and interpretation",
            "Scenario behavior and growth assumptions are inputs; concentration and projected values are deterministic results.",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        metric_grid(
            (
                (
                    "Employer-equity growth",
                    format_display_value(growth.value, "ratio"),
                    growth.source,
                ),
                ("Policy comparison", str(behavior.value), "Temporary scenario choice"),
            ),
            class_name="wos-two-metric-grid",
        ),
        unsafe_allow_html=True,
    )


def _ratio(value: Decimal | int | str | bool | None) -> Decimal:
    if not isinstance(value, Decimal):
        raise TypeError("Expected ratio evidence.")
    return value

# ruff: noqa: E501
"""Focused property-decision visual workspace."""

from __future__ import annotations

from decimal import Decimal
from html import escape
from typing import TypeVar

import streamlit as st

from experience.components.visual_primitives import metric_grid, section_heading
from experience.display import format_compact_currency, format_display_value, format_table_value
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

EvidenceT = TypeVar("EvidenceT", bound=LiveEvidence)


def render_g002_property_workspace(workspace: LiveWorkspace) -> str | None:
    """Render the property goal from deterministic evidence and return an explain action."""

    evidence = {item.evidence_id: item for item in workspace.evidence}
    answer = _evidence(evidence, "g002-answer", NarrativeEvidence)
    liquid_difference = _evidence(evidence, "g002-liquid-difference", MetricEvidence)
    liquidity = _evidence(evidence, "g002-liquidity", ComparisonEvidence)
    net_worth = _evidence(evidence, "g002-net-worth", ComparisonEvidence)
    property_value = _evidence(evidence, "g002-property-value", ComparisonEvidence)

    st.markdown('<main class="wos-g002-workspace">', unsafe_allow_html=True)
    st.markdown(
        '<div class="wos-visual-kicker">Property decision workspace</div>', unsafe_allow_html=True
    )
    st.markdown(
        f'<h1 class="wos-g002-title">{escape(workspace.title)}</h1>', unsafe_allow_html=True
    )
    st.markdown(
        '<section class="wos-g002-hero">'
        "<span>Modelled outcome</span>"
        "<h2>Under assumptions currently modelled, buying the property leaves about "
        f"{escape(format_compact_currency(_money(liquid_difference.value)))} more liquid assets by the end.</h2>"
        f"<p>{escape(answer.text)}</p>"
        "</section>",
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
                    "Final liquid assets",
                    format_display_value(liquidity.baseline_value, liquidity.unit),
                    f"Property excluded: {format_display_value(liquidity.scenario_value, liquidity.unit)}",
                ),
                (
                    "Property value",
                    format_display_value(property_value.baseline_value, property_value.unit),
                    "Separate from liquidity · property included path",
                ),
                (
                    "Planning net worth",
                    format_display_value(net_worth.baseline_value, net_worth.unit),
                    f"Property excluded: {format_display_value(net_worth.scenario_value, net_worth.unit)}",
                ),
            ),
            class_name="wos-g002-outcomes",
        ),
        unsafe_allow_html=True,
    )
    action: str | None = None
    if st.button("Explain this", key="explain-g002-outcome", type="tertiary"):
        action = "explain:g002-liquid-difference,g002-liquidity,g002-property-value,g002-net-worth"

    st.markdown(
        section_heading(
            "Where the liquid difference comes from",
            "A reconciliation from the initial cash purchase to the final liquid-assets difference.",
        ),
        unsafe_allow_html=True,
    )
    _render_causal_bridge(evidence)
    if st.button("Explain this", key="explain-g002-bridge", type="tertiary"):
        action = (
            "explain:g002-purchase,g002-after-tax-surplus,g002-funding-preserved,"
            "g002-funding-order-growth,g002-liquid-difference"
        )

    st.markdown(
        section_heading(
            "Liquidity through time",
            "The two paths use the same household inputs; the property purchase changes cash flow and later funding needs.",
        ),
        unsafe_allow_html=True,
    )
    _render_liquid_chart(evidence)
    st.caption("Exact annual values from the deterministic projection. Hover to inspect a year.")

    st.markdown(
        section_heading(
            "Property value is not liquidity",
            "Appreciation is represented as a separate non-liquid asset trajectory.",
        ),
        unsafe_allow_html=True,
    )
    _render_property_chart(evidence)

    st.markdown(
        section_heading(
            "Assumptions and realism boundary",
            "The comparison is correct for the configured model; it is only as realistic as the inputs and omissions below.",
        ),
        unsafe_allow_html=True,
    )
    _render_assumptions(evidence)
    limitation = _evidence(evidence, "g002-limitation", LimitationEvidence)
    st.markdown(
        '<section class="wos-limit-panel"><div><span>Model treatment</span>'
        "<h3>Cash purchase and configured cash flows</h3>"
        "<p>The displayed outcomes and bridge preserve the deterministic engine evidence exactly.</p></div>"
        "<div><span>Not represented</span><h3>Real-world costs and uncertainty</h3>"
        f"<p>{escape(limitation.text)}</p></div></section>",
        unsafe_allow_html=True,
    )

    with st.expander("About this projection", expanded=False):
        st.markdown(
            "The included and excluded paths use the same Financial Picture and planning horizon. "
            "Only the configured planned-property inclusion changes."
        )
        _render_property_table(_evidence(evidence, "g002-configured-property", TableEvidence))
        st.markdown(
            "**Final liquid-assets difference:** "
            f"{format_display_value(liquid_difference.value, liquid_difference.unit)}  \n"
            "**Interpretation:** assumption-dependent comparison, not financial or tax advice."
        )
    st.markdown("</main>", unsafe_allow_html=True)
    return action


def _render_causal_bridge(evidence: dict[str, LiveEvidence]) -> None:
    steps = (
        ("1", "Purchase cash", "g002-purchase", True, "Cash leaves the liquid portfolio in 2027"),
        (
            "2",
            "After-tax rental surplus",
            "g002-after-tax-surplus",
            False,
            "Pre-retirement surplus retained in cash",
        ),
        (
            "3",
            "Withdrawals avoided",
            "g002-funding-preserved",
            False,
            "Rent reduces retirement funding drawn from liquid assets",
        ),
        (
            "4",
            "Funding order + growth",
            "g002-funding-order-growth",
            False,
            "Residual timing and taxable-investment compounding",
        ),
        (
            "5",
            "Final liquid difference",
            "g002-liquid-difference",
            False,
            "Property included minus property excluded",
        ),
    )
    rendered = "".join(
        _bridge_step(number, label, _evidence(evidence, ref, MetricEvidence), negative, detail)
        for number, label, ref, negative, detail in steps
    )
    st.markdown(f'<section class="wos-causal-bridge">{rendered}</section>', unsafe_allow_html=True)


def _bridge_step(
    number: str,
    label: str,
    metric: MetricEvidence,
    negative: bool,
    detail: str,
) -> str:
    value = format_display_value(metric.value, metric.unit)
    if negative:
        value = f"-{value}"
    elif _money(metric.value) > 0:
        value = f"+{value}"
    return (
        f'<article class="wos-bridge-step" data-evidence-ref="{escape(metric.evidence_id)}">'
        f'<span class="wos-step-number">{escape(number)}</span>'
        f"<h3>{escape(label)}</h3><strong>{escape(value)}</strong>"
        f"<p>{escape(detail)}</p></article>"
    )


def _render_liquid_chart(evidence: dict[str, LiveEvidence]) -> None:
    included = _evidence(evidence, "g002-liquid-included-series", TimelineEvidence)
    excluded = _evidence(evidence, "g002-liquid-excluded-series", TimelineEvidence)
    st.line_chart(
        {
            "Year": [point.period for point in included.points],
            "Property included": [float(point.value) for point in included.points],
            "Property excluded": [float(point.value) for point in excluded.points],
        },
        x="Year",
        y=["Property included", "Property excluded"],
        color=None,
    )


def _render_property_chart(evidence: dict[str, LiveEvidence]) -> None:
    property_series = _evidence(evidence, "g002-property-series", TimelineEvidence)
    st.line_chart(
        {
            "Year": [point.period for point in property_series.points],
            "Modelled property value": [float(point.value) for point in property_series.points],
        },
        x="Year",
        y="Modelled property value",
        color=None,
    )
    st.caption("Non-liquid property value in the property-included path.")


def _render_assumptions(evidence: dict[str, LiveEvidence]) -> None:
    configured = _evidence(evidence, "g002-configured-property", TableEvidence)
    row = configured.rows[0]
    items = (
        ("Purchase", f"{format_table_value(row[2], 'Purchase price')} in {row[1]}", "Cash-funded"),
        ("Initial net rent", format_table_value(row[3], "Annual net rent"), "Before estimated tax"),
        (
            "Annual rent growth",
            format_display_value(
                _evidence(evidence, "g002-rent-growth", AssumptionEvidence).value,
                "ratio",
            ),
            "Inflation-linked treatment",
        ),
        (
            "Annual appreciation",
            format_display_value(
                _evidence(evidence, "g002-appreciation", AssumptionEvidence).value,
                "ratio",
            ),
            "Applied to property value",
        ),
    )
    st.markdown(metric_grid(items, class_name="wos-assumption-grid"), unsafe_allow_html=True)


def _render_property_table(evidence: TableEvidence) -> None:
    header = "".join(f"<th>{escape(column)}</th>" for column in evidence.columns)
    rows = "".join(
        f"<tr>{''.join(f'<td>{escape(_format_property_cell(value, evidence.columns[index], str(row[0])))}</td>' for index, value in enumerate(row))}</tr>"
        for row in evidence.rows
    )
    st.markdown(
        '<div class="wos-live-table"><table><thead><tr>'
        f"{header}</tr></thead><tbody>{rows}</tbody></table></div>",
        unsafe_allow_html=True,
    )


def _format_property_cell(value: object, column: str, row_label: str) -> str:
    normalized = column.casefold()
    if "growth" in normalized or "appreciation" in normalized:
        return format_display_value(value, "ratio")  # type: ignore[arg-type]
    return format_table_value(value, column, row_label)  # type: ignore[arg-type]


def _money(value: object) -> Decimal | int:
    if isinstance(value, int):
        return value
    if isinstance(value, Decimal):
        return value
    raise TypeError("Expected monetary evidence.")


def _evidence(  # noqa: UP047 -- runtime remains compatible with Python 3.12
    evidence: dict[str, LiveEvidence],
    evidence_id: str,
    expected_type: type[EvidenceT],
) -> EvidenceT:
    item = evidence[evidence_id]
    if not isinstance(item, expected_type):
        raise TypeError(f"{evidence_id} is not {expected_type.__name__}.")
    return item

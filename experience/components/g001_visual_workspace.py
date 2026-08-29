# ruff: noqa: E501
"""Visual-first renderer for the bounded retirement Workspace specification."""

from __future__ import annotations

from decimal import Decimal
from html import escape

import plotly.graph_objects as go  # type: ignore[import-untyped]
import streamlit as st

from experience.display import format_compact_currency, format_display_value, format_table_value
from experience.live.models import (
    AssumptionEvidence,
    ComparisonEvidence,
    InsightEvidence,
    LimitationEvidence,
    LiveEvidence,
    LiveWorkspace,
    MetricEvidence,
    NarrativeEvidence,
    TableEvidence,
    TimelineEvidence,
)
from experience.workspace_composition.g001 import validate_g001_workspace
from experience.workspace_composition.models import (
    DisclosureContent,
    WorkspaceComponentSpec,
    WorkspaceComponentType,
    WorkspaceSpec,
)


def render_g001_visual_workspace(spec: WorkspaceSpec, workspace: LiveWorkspace) -> str | None:
    """Render referenced evidence and return one bounded customer interaction."""

    evidence = {item.evidence_id: item for item in workspace.evidence}
    validate_g001_workspace(spec, set(evidence))
    control = spec.controls[0]

    st.markdown('<main class="wos-visual-workspace">', unsafe_allow_html=True)
    st.markdown('<div class="wos-visual-kicker">Retirement timing</div>', unsafe_allow_html=True)
    st.markdown(
        f'<h1 class="wos-visual-title">{escape(spec.question)}</h1>', unsafe_allow_html=True
    )
    answer_component = spec.component(spec.answer_component_id)
    answer = _typed(evidence[answer_component.evidence_refs[0]], NarrativeEvidence)
    st.markdown(f'<p class="wos-visual-answer">{escape(answer.text)}</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="wos-scenario-context">'
        f"Baseline retirement age <strong>{control.baseline_value}</strong> · "
        f"Exploring <strong>{control.current_value}</strong> · Temporary scenario"
        "</p>",
        unsafe_allow_html=True,
    )
    st.selectbox(
        control.label,
        control.allowed_values,
        index=(
            None
            if "g001-retirement-age" in st.session_state
            else control.allowed_values.index(control.current_value)
        ),
        key="g001-retirement-age",
        help="This changes only the temporary comparison. Your baseline remains unchanged.",
    )
    action: str | None = None
    if st.button(
        "Update Financial Picture",
        key="g001-propose-financial-picture-update",
        type="tertiary",
        help="Review this exploration as a proposed planning change. Nothing is saved automatically.",
    ):
        action = "propose-update"

    for section in spec.sections[1:-1]:
        for component in section.components:
            _render_component(component, evidence)
            if component.component_type in {
                WorkspaceComponentType.WEALTH_TRAJECTORY,
                WorkspaceComponentType.METRIC_COMPARISON,
                WorkspaceComponentType.TIMELINE,
            } and st.button(
                "Explain this",
                key=f"explain-{component.component_id}",
                type="tertiary",
            ):
                action = f"explain:{component.component_id}"
    _render_details(spec, workspace, evidence)
    st.markdown("</main>", unsafe_allow_html=True)
    return action


def _render_component(
    component: WorkspaceComponentSpec,
    evidence: dict[str, LiveEvidence],
) -> None:
    if component.component_type is WorkspaceComponentType.WEALTH_TRAJECTORY:
        _trajectory(component, evidence)
    elif component.component_type is WorkspaceComponentType.METRIC_COMPARISON:
        _comparisons(component, evidence)
    elif component.component_type is WorkspaceComponentType.TIMELINE:
        _timeline(component, evidence)
    elif component.component_type is WorkspaceComponentType.TRADE_OFF:
        _trade_off(component, evidence)
    elif component.component_type is WorkspaceComponentType.NARRATIVE:
        narrative = _typed(evidence[component.evidence_refs[0]], NarrativeEvidence)
        _section_heading(component.title)
        st.markdown(
            f'<p class="wos-visual-copy">{escape(narrative.text)}</p>', unsafe_allow_html=True
        )


def _trajectory(component: WorkspaceComponentSpec, evidence: dict[str, LiveEvidence]) -> None:
    baseline = _typed(evidence[component.evidence_refs[0]], TimelineEvidence)
    scenario = _typed(evidence[component.evidence_refs[1]], TimelineEvidence)
    figure = go.Figure()
    for series, colour, dash, symbol in (
        (baseline, "#6f7d87", "dash", "circle-open"),
        (scenario, "#2b7069", "solid", "circle"),
    ):
        figure.add_trace(
            go.Scatter(
                x=[point.period for point in series.points],
                y=[point.value for point in series.points],
                customdata=[[point.age] for point in series.points],
                name=series.label,
                mode="lines+markers",
                line={"color": colour, "dash": dash, "width": 3},
                marker={"symbol": symbol, "size": 5},
                hovertemplate=(
                    "%{x} · age %{customdata[0]}<br>\u20ac%{y:,.0f}<extra>%{fullData.name}</extra>"
                ),
            )
        )
    figure.update_layout(
        margin={"l": 8, "r": 8, "t": 18, "b": 8},
        height=410,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.1, "x": 0},
        xaxis={"title": "Calendar year", "showgrid": False},
        yaxis={
            "title": "Liquid assets",
            "tickprefix": "\u20ac",
            "tickformat": "~s",
            "gridcolor": "rgba(127,127,127,0.18)",
        },
        font={"family": "sans-serif"},
    )
    _section_heading(
        component.title,
        "The assets available to fund spending before and alongside pension income.",
    )
    st.plotly_chart(figure, width="stretch", key="g001-liquid-assets-chart")
    st.markdown(
        '<p class="wos-chart-summary">Two lines distinguish the unchanged baseline from the temporary retirement-age scenario. Exact annual values are available on hover and in supporting figures.</p>',
        unsafe_allow_html=True,
    )


def _comparisons(component: WorkspaceComponentSpec, evidence: dict[str, LiveEvidence]) -> None:
    _section_heading(component.title)
    rows = []
    for evidence_id in component.evidence_refs:
        item = _typed(evidence[evidence_id], ComparisonEvidence)
        rows.append(
            '<div class="wos-comparison-row">'
            f'<span class="wos-comparison-label">{escape(item.metric)}</span>'
            f"<span><small>{escape(item.baseline_label)}</small>{escape(_comparison_value(item.baseline_value, item.unit))}</span>"
            f"<span><small>{escape(item.scenario_label)}</small>{escape(_comparison_value(item.scenario_value, item.unit))}</span>"
            "</div>"
        )
    st.markdown(f'<div class="wos-comparison">{"".join(rows)}</div>', unsafe_allow_html=True)


def _timeline(component: WorkspaceComponentSpec, evidence: dict[str, LiveEvidence]) -> None:
    _section_heading(
        component.title,
        "How the explored retirement date connects to private and State Pension income.",
    )
    milestones = []
    for evidence_id in component.evidence_refs:
        item = _typed(evidence[evidence_id], MetricEvidence)
        milestones.append(
            '<div class="wos-milestone">'
            f'<span class="wos-milestone-year">{escape(item.period or "")}</span>'
            f"<strong>{escape(item.label)}</strong>"
            f"<span>{escape(format_display_value(item.value, item.unit))}</span>"
            "</div>"
        )
    st.markdown(f'<div class="wos-timeline">{"".join(milestones)}</div>', unsafe_allow_html=True)


def _trade_off(component: WorkspaceComponentSpec, evidence: dict[str, LiveEvidence]) -> None:
    _section_heading(component.title)
    groups = []
    for group in component.groups:
        item = _typed(evidence[group.evidence_refs[0]], InsightEvidence)
        groups.append(
            '<div class="wos-tradeoff-item">'
            f"<span>{escape(group.label)}</span><p>{escape(item.observation)}</p>"
            "</div>"
        )
    st.markdown(f'<div class="wos-tradeoff-grid">{"".join(groups)}</div>', unsafe_allow_html=True)


def _render_details(
    spec: WorkspaceSpec,
    workspace: LiveWorkspace,
    evidence: dict[str, LiveEvidence],
) -> None:
    section = spec.sections[-1]
    st.markdown('<div class="wos-detail-rule"></div>', unsafe_allow_html=True)
    with st.expander("About this projection", expanded=False):
        for component in section.components:
            if component.disclosure_content is DisclosureContent.PROVENANCE:
                continue
            st.markdown(f"#### {component.title.removeprefix('Show ')}")
            for evidence_id in component.evidence_refs:
                _detail_evidence(evidence[evidence_id])


def _detail_evidence(evidence: LiveEvidence) -> None:
    if isinstance(evidence, AssumptionEvidence):
        suffix = (
            "changed for this exploration"
            if evidence.source == "Temporary scenario input"
            else "from your Financial Picture"
        )
        st.markdown(f"**{evidence.label}**  \n{format_display_value(evidence.value)} — {suffix}")
    elif isinstance(evidence, LimitationEvidence):
        st.write(evidence.text)
    elif isinstance(evidence, TableEvidence):
        rows = [
            {
                column: format_table_value(value, column, str(row[0]))
                for column, value in zip(evidence.columns, row, strict=True)
            }
            for row in evidence.rows
        ]
        st.table(rows)
        if evidence.footnote:
            st.caption(evidence.footnote)


def _comparison_value(value: Decimal | int | str | bool | None, unit: str) -> str:
    if isinstance(value, (Decimal, int)) and unit.startswith("EUR"):
        return format_compact_currency(value)
    return format_display_value(value, unit)


def _section_heading(title: str, summary: str | None = None) -> None:
    summary_html = f"<p>{escape(summary)}</p>" if summary else ""
    st.markdown(
        f'<header class="wos-visual-section-heading"><h2>{escape(title)}</h2>{summary_html}</header>',
        unsafe_allow_html=True,
    )


def _typed[T](value: LiveEvidence, expected: type[T]) -> T:
    if not isinstance(value, expected):
        raise TypeError(f"Expected {expected.__name__} evidence.")
    return value

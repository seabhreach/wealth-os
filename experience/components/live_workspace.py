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


def render_live_workspace(workspace: LiveWorkspace) -> str | None:
    """Render an answer-first, goal-specific Workspace from immutable evidence."""

    st.markdown('<main class="wos-interim-workspace">', unsafe_allow_html=True)
    st.markdown('<div class="wos-visual-kicker">Workspace</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="wos-workspace-title">{escape(workspace.title)}</div>', unsafe_allow_html=True
    )

    evidence_by_id = {item.evidence_id: item for item in workspace.evidence}
    answer = next(item for item in workspace.evidence if isinstance(item, NarrativeEvidence))
    st.markdown(f'<p class="wos-visual-answer">{escape(answer.text)}</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="wos-scenario-context">Temporary exploration · your Financial Picture is unchanged</p>',
        unsafe_allow_html=True,
    )
    action = _render_goal_body(workspace, evidence_by_id)
    _, details, supporting = _evidence_groups(workspace.evidence)
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
    return action


def _render_goal_body(workspace: LiveWorkspace, evidence: dict[str, LiveEvidence]) -> str | None:
    """Select a bounded visual composition for each validated goal."""

    from experience.models import GoalId

    layouts: dict[GoalId, tuple[str, tuple[str, ...], str]] = {
        GoalId.INVESTMENT_PROPERTY: (
            "The modelled property trade-off",
            ("g002-liquidity", "g002-property-value", "g002-net-worth"),
            "How purchase, rent and property value affect the two paths",
        ),
        GoalId.EMPLOYER_EQUITY: (
            "Employer-share concentration",
            ("g003-concentration", "g003-final-equity", "g003-final-worth"),
            "How the selected disposal policy changes exposure",
        ),
        GoalId.HIGHER_SPENDING: (
            "Spending and funding consequence",
            ("g004-spending", "g004-liquid", "g004-final-worth"),
            "Today's-money input and the resulting future path",
        ),
        GoalId.CASH_DECLINE: (
            "What changes cash in the selected year",
            ("g005-statement", "g005-transition", "g005-retirement-milestone"),
            "Opening cash, inflows, outflows and closing cash",
        ),
    }
    heading, primary_ids, explanation = layouts[workspace.goal_id]
    _visual_heading(heading, explanation)
    timelines = tuple(item for item in workspace.evidence if isinstance(item, TimelineEvidence))
    comparisons = tuple(evidence[item_id] for item_id in primary_ids if item_id in evidence)
    for item in comparisons:
        _render_evidence(item)
    if timelines:
        _visual_heading("Trajectory", "Exact annual values from the deterministic projection.")
        _timeline_chart(timelines)
    if workspace.goal_id is GoalId.INVESTMENT_PROPERTY:
        _visual_heading(
            "What changes when the property is purchased",
            "The purchase is funded from cash; rent and appreciation then continue through the model.",
        )
        for item_id in (
            "g002-purchase",
            "g002-purchase-year-liquid",
            "g002-rent",
            "g002-cumulative-rent",
            "g002-rental-tax",
            "g002-funding-preserved",
        ):
            _render_evidence(evidence[item_id])
    elif workspace.goal_id is GoalId.HIGHER_SPENDING:
        _visual_heading(
            "The spending basis",
            "The explored input is in today's money; the first-retirement figure is inflation-adjusted nominal spending.",
        )
        _render_evidence(evidence["g004-input-basis"])
    elif workspace.goal_id is GoalId.CASH_DECLINE:
        statement = evidence["g005-statement"]
        if isinstance(statement, FinancialStatementEvidence):
            _render_cash_bridge(statement)
    button_key = f"explain-{workspace.goal_id.value}-primary"
    if st.button("Explain this", key=button_key, type="tertiary"):
        return "explain:" + ",".join(primary_ids)
    return None


def _visual_heading(title: str, summary: str) -> None:
    st.markdown(
        f'<div class="wos-visual-section-heading"><h2>{escape(title)}</h2><p>{escape(summary)}</p></div>',
        unsafe_allow_html=True,
    )


def _timeline_chart(items: tuple[TimelineEvidence, ...]) -> None:
    if not items:
        return
    data: dict[str, list[int | float]] = {"Year": [p.period for p in items[0].points]}
    for item in items:
        # Streamlit/Altair needs quantitative primitives; the immutable Decimal
        # evidence remains the source of truth and conversion is presentation-only.
        data[item.label] = [float(point.value) for point in item.points]
    st.line_chart(data, x="Year", y=[item.label for item in items], color=None)
    st.caption("Illustrative deterministic projection. Hover for exact annual values.")


def _render_cash_bridge(evidence: FinancialStatementEvidence) -> None:
    status = (
        f"Pre-retirement · age {evidence.age}"
        if evidence.employed
        else f"Retired · age {evidence.age}"
    )
    rows = (
        ("Opening cash", format_display_value(evidence.opening_cash, "EUR")),
        *(
            (f"+ {label}", format_display_value(value, "EUR"))
            for label, value in evidence.inflows
            if value
        ),
        *(
            (f"- {label}", format_display_value(value, "EUR"))
            for label, value in evidence.outflows
            if value
        ),
        ("Closing cash", format_display_value(evidence.closing_cash, "EUR")),
    )
    _rows(f"Cash flow · {evidence.calendar_year}", status, rows)


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

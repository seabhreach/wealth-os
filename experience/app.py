"""Integrated customer shell for the deterministic Wealth OS Experience."""

from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from html import escape
from pathlib import Path

import streamlit as st

from experience.components.financial_picture import (
    proposed_retirement_age,
    render_financial_picture,
)
from experience.components.g001_visual_workspace import render_g001_visual_workspace
from experience.components.live_workspace import render_live_workspace
from experience.components.recent_workspaces import render_recent_workspaces
from experience.explain import ExplainContext, context_for_component, explain_context
from experience.live import LiveExperienceService
from experience.live.models import LiveWorkspace
from experience.models import GoalId
from experience.routing import RoutedQuestion, route_question
from experience.styles import apply_styles
from experience.workspace_composition import compose_g001_workspace

VIEW_KEY = "wealth-os-shell-view"
ROUTE_KEY = "wealth-os-routed-question"
ACTIVE_GOAL_KEY = "wealth-os-active-goal"
QUESTION_KEY = "wealth-os-customer-question"
EXPLAIN_KEY = "wealth-os-explain-context"
G001_AGE_KEY = "g001-retirement-age"
CASH_YEAR_KEY = "integrated-cash-year"
SPENDING_KEY = "integrated-spending-amount"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class ShellView(StrEnum):
    """Primary customer-facing Experience states."""

    HOME = "home"
    CONVERSATION = "conversation"
    WORKSPACE = "workspace"
    FINANCIAL_PICTURE = "financial-picture"
    WORKSPACES = "workspaces"


def _service() -> LiveExperienceService:
    return LiveExperienceService.from_example(REPOSITORY_ROOT)


def _view() -> ShellView:
    stored = st.session_state.get(VIEW_KEY)
    if isinstance(stored, str):
        try:
            return ShellView(stored)
        except ValueError:
            pass
    if st.query_params.get("workspace") == "g001":
        st.session_state[ACTIVE_GOAL_KEY] = GoalId.RETIRE_EARLIER
        st.session_state.setdefault(G001_AGE_KEY, 58)
        return ShellView.WORKSPACE
    return ShellView.HOME


def _go(view: ShellView) -> None:
    st.session_state[VIEW_KEY] = view.value
    st.session_state.pop(EXPLAIN_KEY, None)


def _render_navigation(active: ShellView) -> None:
    columns = st.columns((1.4, 1.0, 1.45, 5.6), vertical_alignment="center")
    columns[0].markdown('<div class="wos-shell-wordmark">Wealth OS</div>', unsafe_allow_html=True)
    destinations = (
        (columns[1], "Home", ShellView.HOME, "shell-home"),
        (columns[2], "Financial Picture", ShellView.FINANCIAL_PICTURE, "shell-picture"),
        (columns[3], "Workspaces", ShellView.WORKSPACES, "shell-workspaces"),
    )
    for column, label, view, key in destinations:
        if column.button(label, key=key, type="primary" if active is view else "tertiary"):
            _go(view)
            st.rerun()


def _render_home() -> None:
    _, home_column, _ = st.columns((0.55, 3.0, 0.55))
    with home_column:
        st.markdown(
            '<main class="wos-home"><div class="wos-wordmark">Wealth OS</div>'
            '<h1 class="wos-question">What would you like to explore today?</h1>'
            '<p class="wos-support">Ask a question. Wealth OS will use what it already knows '
            "and only ask for what matters.</p></main>",
            unsafe_allow_html=True,
        )
        opening_message = st.chat_input(
            "Ask about retirement, spending, property, employer equity or cash flow",
            key="home-chat-input",
        )
        selected_goal = render_recent_workspaces()
    if opening_message:
        st.session_state[QUESTION_KEY] = opening_message.strip()
        st.session_state[ROUTE_KEY] = route_question(opening_message)
        _go(ShellView.CONVERSATION)
        st.rerun()
    if selected_goal is not None:
        _open_saved_workspace(selected_goal)
        st.rerun()


def _render_conversation(service: LiveExperienceService) -> None:
    route = st.session_state.get(ROUTE_KEY)
    question = str(st.session_state.get(QUESTION_KEY, ""))
    _, column, _ = st.columns((0.8, 3.0, 0.8))
    with column:
        st.markdown('<main class="wos-conversation-state">', unsafe_allow_html=True)
        st.markdown('<div class="wos-visual-kicker">Conversation</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="wos-conversation-user">{escape(question)}</div>',
            unsafe_allow_html=True,
        )
        if not isinstance(route, RoutedQuestion):
            st.markdown(
                '<p class="wos-conversation-answer">I can currently explore retirement timing, '
                "an investment property, employer-equity exposure, higher retirement spending, "
                "or why cash changes. I won't assume you meant retirement.</p>",
                unsafe_allow_html=True,
            )
            retry = st.chat_input("Try another financial question", key="conversation-retry")
            if retry:
                st.session_state[QUESTION_KEY] = retry.strip()
                st.session_state[ROUTE_KEY] = route_question(retry)
                st.rerun()
            st.markdown("</main>", unsafe_allow_html=True)
            return
        problem = _route_problem(route, service)
        if problem:
            st.markdown(
                f'<p class="wos-conversation-answer">{escape(problem)}</p>',
                unsafe_allow_html=True,
            )
            st.markdown("</main>", unsafe_allow_html=True)
            return
        st.markdown(
            f'<p class="wos-conversation-answer">{escape(_enough_message(route))}</p>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="wos-enough">{escape(_transition_message(route))}</p>',
            unsafe_allow_html=True,
        )
        if st.button(
            _workspace_action_label(route.goal_id),
            key="conversation-open-workspace",
            type="primary",
        ):
            _activate_route(route)
            st.rerun()
        st.markdown("</main>", unsafe_allow_html=True)


def _render_workspaces() -> None:
    _, column, _ = st.columns((0.4, 3.5, 0.4))
    with column:
        st.markdown('<div class="wos-visual-kicker">Workspaces</div>', unsafe_allow_html=True)
        st.markdown('<h1 class="wos-picture-title">Saved explorations</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="wos-support">Reopen a question-focused answer without changing '
            "your Financial Picture.</p>",
            unsafe_allow_html=True,
        )
        selected = render_recent_workspaces()
    if selected is not None:
        _open_saved_workspace(selected)
        st.rerun()


def _render_workspace(service: LiveExperienceService) -> None:
    goal_id = st.session_state.get(ACTIVE_GOAL_KEY)
    if not isinstance(goal_id, GoalId):
        _go(ShellView.WORKSPACES)
        st.rerun()
    top = st.columns((1.0, 1.0, 6.0))
    if top[0].button("Return home", key="return-home", type="tertiary"):
        _go(ShellView.HOME)
        st.rerun()
    if top[1].button("Ask Wealth OS", key="ask-wealth-os", type="tertiary"):
        st.session_state[EXPLAIN_KEY] = "general"
    workspace = (
        _render_retirement_workspace(service)
        if goal_id is GoalId.RETIRE_EARLIER
        else _render_interim_workspace(goal_id, service)
    )
    _render_conversation_surface(workspace)
    _render_review_mode(workspace)


def _render_retirement_workspace(service: LiveExperienceService) -> LiveWorkspace:
    allowed = service.supported_retirement_ages
    stored = st.session_state.get(G001_AGE_KEY, 58)
    age = stored if isinstance(stored, int) and stored in allowed else 58
    st.session_state[G001_AGE_KEY] = age
    workspace = service.retire_earlier(age)
    baseline_age = service.baseline.configuration.household.planned_retirement_age
    spec = compose_g001_workspace(
        workspace,
        allowed_retirement_ages=allowed,
        baseline_retirement_age=baseline_age,
        explored_retirement_age=age,
    )
    action = render_g001_visual_workspace(spec, workspace)
    if action and action.startswith("explain:"):
        st.session_state[EXPLAIN_KEY] = context_for_component(
            spec,
            action.removeprefix("explain:"),
        )
        st.rerun()
    if action == "propose-update":
        st.session_state["financial-picture-proposal"] = proposed_retirement_age(age, baseline_age)
        st.session_state.pop("financial-picture-update-confirmed", None)
        _go(ShellView.FINANCIAL_PICTURE)
        st.rerun()
    if st.session_state.get(EXPLAIN_KEY) == "general":
        st.session_state[EXPLAIN_KEY] = context_for_component(
            spec,
            "g001-explanation-component",
        )
    return workspace


def _render_interim_workspace(goal_id: GoalId, service: LiveExperienceService) -> LiveWorkspace:
    if goal_id is GoalId.INVESTMENT_PROPERTY:
        financing = st.toggle(
            "Explore financing instead",
            value=False,
            key="integrated-property-financing",
            help="Financing is outside the current deterministic model.",
        )
        workspace = service.property_decision(financing=financing)
    elif goal_id is GoalId.EMPLOYER_EQUITY:
        policy = st.segmented_control(
            "Explore disposal policy",
            ("Retain", "Sell on vest"),
            default="Retain",
            key="integrated-equity-policy",
        )
        workspace = service.employer_equity(focus_sell_on_vest=policy == "Sell on vest")
    elif goal_id is GoalId.HIGHER_SPENDING:
        amount = st.number_input(
            "Explore annual retirement spending",
            min_value=0,
            value=int(st.session_state.get(SPENDING_KEY, 100_000)),
            step=5_000,
            key=SPENDING_KEY,
            help="This temporary amount does not update your Financial Picture.",
        )
        workspace = service.higher_spending(Decimal(str(amount)))
    else:
        years = service.supported_years
        selected = st.session_state.get(CASH_YEAR_KEY, 2032)
        year = selected if isinstance(selected, int) and selected in years else 2032
        workspace = service.cash_decline(
            st.selectbox("Explain year", years, index=years.index(year), key=CASH_YEAR_KEY)
        )
    render_live_workspace(workspace)
    return workspace


def _render_conversation_surface(workspace: LiveWorkspace) -> None:
    context = st.session_state.get(EXPLAIN_KEY)
    if context is None:
        return
    with st.container(border=True):
        st.markdown('<div class="wos-visual-kicker">Ask Wealth OS</div>', unsafe_allow_html=True)
        if isinstance(context, ExplainContext):
            explanation = explain_context(context, workspace)
            st.markdown(f"**{explanation.framing}**")
            st.write(explanation.text)
        else:
            st.write(
                "Choose 'Explain this' on a chart or comparison for an evidence-backed "
                "explanation. "
                "Free-form AI conversation is not connected yet."
            )
        if st.button("Close conversation", key="close-workspace-conversation", type="tertiary"):
            st.session_state.pop(EXPLAIN_KEY, None)
            st.rerun()


def _render_review_mode(workspace: LiveWorkspace) -> None:
    if st.query_params.get("review") != "1":
        return
    with st.expander("Review mode", expanded=False):
        st.caption("Engineering diagnostics — hidden from the normal customer experience.")
        st.json(
            {
                "workspace_id": workspace.workspace_id,
                "goal_id": workspace.goal_id.value,
                "financial_picture_fingerprint": workspace.provenance.financial_picture_fingerprint,
                "scenario_override": dict(workspace.provenance.scenario_overrides),
                "simulation_version": workspace.provenance.simulation_version,
                "tax_rule_identifier": workspace.provenance.tax_rule_identifier,
                "result_fingerprint": workspace.provenance.result_fingerprint,
                "evidence_ids": [item.evidence_id for item in workspace.evidence],
            }
        )


def _open_saved_workspace(goal_id: GoalId) -> None:
    st.session_state[ACTIVE_GOAL_KEY] = goal_id
    st.session_state[QUESTION_KEY] = _saved_question(goal_id)
    if goal_id is GoalId.RETIRE_EARLIER:
        st.session_state[G001_AGE_KEY] = 58
    if goal_id is GoalId.CASH_DECLINE:
        st.session_state[CASH_YEAR_KEY] = 2032
    _go(ShellView.WORKSPACE)


def _activate_route(route: RoutedQuestion) -> None:
    st.session_state[ACTIVE_GOAL_KEY] = route.goal_id
    if route.goal_id is GoalId.RETIRE_EARLIER:
        st.session_state[G001_AGE_KEY] = route.retirement_age or 58
    elif route.goal_id is GoalId.CASH_DECLINE:
        st.session_state[CASH_YEAR_KEY] = route.calendar_year or 2032
    elif route.goal_id is GoalId.HIGHER_SPENDING:
        st.session_state[SPENDING_KEY] = int(route.retirement_spending or Decimal("100000"))
    _go(ShellView.WORKSPACE)


def _route_problem(route: RoutedQuestion, service: LiveExperienceService) -> str | None:
    if (
        route.retirement_age is not None
        and route.retirement_age not in service.supported_retirement_ages
    ):
        ages = service.supported_retirement_ages
        return f"This prototype can currently compare retirement ages {ages[0]} to {ages[-1]}."
    if route.calendar_year is not None and route.calendar_year not in service.supported_years:
        return "That year is outside the current projection."
    return None


def _enough_message(route: RoutedQuestion) -> str:
    if route.goal_id is GoalId.CASH_DECLINE:
        return "I already have the reporting evidence needed to explain this."
    return (
        "Yes. I already have enough information to make an initial comparison with your "
        "current plan."
    )


def _transition_message(route: RoutedQuestion) -> str:
    if route.goal_id is GoalId.RETIRE_EARLIER:
        age = route.retirement_age or 58
        return f"I have enough to show you what retiring at {age} could look like."
    if route.goal_id is GoalId.CASH_DECLINE:
        year = route.calendar_year or 2032
        return f"I can show what changed in {year} without asking for anything else."
    return "I have enough to create an initial Workspace from your Financial Picture."


def _workspace_action_label(goal_id: GoalId) -> str:
    return {
        GoalId.RETIRE_EARLIER: "Show my retirement comparison",
        GoalId.INVESTMENT_PROPERTY: "Show the property comparison",
        GoalId.EMPLOYER_EQUITY: "Show my employer-equity exposure",
        GoalId.HIGHER_SPENDING: "Show the spending comparison",
        GoalId.CASH_DECLINE: "Show the cash explanation",
    }[goal_id]


def _saved_question(goal_id: GoalId) -> str:
    return {
        GoalId.RETIRE_EARLIER: "Could I retire at 58?",
        GoalId.INVESTMENT_PROPERTY: "What happens if I buy the investment property?",
        GoalId.EMPLOYER_EQUITY: "How dependent am I on my employer shares?",
        GoalId.HIGHER_SPENDING: "What if I spend more in retirement?",
        GoalId.CASH_DECLINE: "Why does my cash decline after retirement?",
    }[goal_id]


def main() -> None:
    """Render the integrated Home, Conversation, Workspace and Financial Picture shell."""

    st.set_page_config(page_title="Wealth OS Experience", layout="wide")
    apply_styles()
    active = _view()
    _render_navigation(active)
    service = _service()
    if active is ShellView.HOME:
        _render_home()
    elif active is ShellView.CONVERSATION:
        _render_conversation(service)
    elif active is ShellView.FINANCIAL_PICTURE:
        render_financial_picture(
            service.baseline.financial_picture,
            supported_retirement_ages=service.supported_retirement_ages,
        )
    elif active is ShellView.WORKSPACES:
        _render_workspaces()
    else:
        _render_workspace(service)


if __name__ == "__main__":
    main()

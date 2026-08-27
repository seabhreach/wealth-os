"""Small live-mode controls that request existing deterministic scenarios."""

from __future__ import annotations

from decimal import Decimal

import streamlit as st

from experience.live.models import LiveWorkspace
from experience.live.service import LiveExperienceService
from experience.models import GoalId


def live_workspace_for_goal(goal_id: GoalId, service: LiveExperienceService) -> LiveWorkspace:
    """Request one live Workspace without calculating evidence in the UI."""

    if goal_id is GoalId.RETIRE_EARLIER:
        baseline_age = service.baseline.configuration.household.planned_retirement_age
        current_age = service.baseline.configuration.household.current_age
        ages = tuple(range(current_age, baseline_age + 1))
        default_age = 58 if 58 in ages else ages[0]
        retirement_age = st.selectbox(
            "Explored retirement age",
            ages,
            index=ages.index(default_age),
            key="live-retirement-age",
        )
        return service.retire_earlier(retirement_age)

    if goal_id is GoalId.INVESTMENT_PROPERTY:
        funding = st.radio(
            "Property exploration",
            ("Configured cash purchase", "Financing"),
            horizontal=True,
            key="live-property-funding",
        )
        return service.property_decision(financing=funding == "Financing")

    if goal_id is GoalId.EMPLOYER_EQUITY:
        policy = st.radio(
            "Comparison focus",
            ("Retain", "Sell on vest"),
            horizontal=True,
            key="live-equity-policy",
        )
        return service.employer_equity(focus_sell_on_vest=policy == "Sell on vest")

    if goal_id is GoalId.HIGHER_SPENDING:
        timing = st.radio(
            "Spending timing",
            ("Permanent", "Temporary multi-year"),
            horizontal=True,
            key="live-spending-timing",
        )
        amount = st.number_input(
            "Annual retirement spending",
            min_value=0,
            value=100_000,
            step=5_000,
            key="live-spending-amount",
        )
        target = Decimal(str(amount))
        return service.higher_spending(
            target,
            temporary_years=5 if timing == "Temporary multi-year" else None,
        )

    years = service.supported_years
    default_year = 2032 if 2032 in years else years[0]
    calendar_year = st.selectbox(
        "Reporting year",
        years,
        index=years.index(default_year),
        key="live-cash-year",
    )
    return service.cash_decline(calendar_year)

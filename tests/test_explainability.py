"""Regression tests for reporting-only financial explainability outputs."""

from pathlib import Path

from engine.config import load_configuration
from engine.reporting import (
    annual_calculation_trace,
    preserved_wealth_warning,
    retirement_funding_explanation,
)
from engine.simulation import project_annually


def _configuration_text() -> str:
    """Return the released baseline household configuration."""
    return Path("data/example_household.yaml").read_text(encoding="utf-8")


def test_first_retirement_funding_trace_uses_each_source_once() -> None:
    """Rent and each withdrawal source reconcile to the completed retirement row."""
    configuration = load_configuration(_configuration_text())
    timeline = project_annually(configuration)
    retirement_year = next(year for year in timeline if not year.employed)
    trace = annual_calculation_trace(timeline, configuration, retirement_year.calendar_year)

    assert (
        retirement_year.annual_spending - retirement_year.net_recurring_income
        == retirement_year.withdrawal_amount + retirement_year.unfunded_spending
    )
    assert retirement_year.withdrawal_amount == (
        retirement_year.cash_withdrawal
        + retirement_year.etf_withdrawal
        + retirement_year.amazon_withdrawal
    )
    assert "rental income" in retirement_funding_explanation(retirement_year)
    assert trace.closing_cash == (
        trace.opening_cash
        + trace.annual_savings
        + trace.rsu_sale_proceeds
        + trace.rental_income
        - trace.property_purchase_cost
        - trace.cash_withdrawal
    )


def test_trace_reconciles_etf_and_pension_opening_to_closing_balances() -> None:
    """Growth, contribution, and withdrawal trace components reconcile completed balances."""
    configuration = load_configuration(_configuration_text())
    timeline = project_annually(configuration)
    trace = annual_calculation_trace(timeline, configuration, 2032)

    assert trace.closing_etf_value == (
        trace.opening_etf_value + trace.etf_growth_amount - trace.etf_withdrawal
    )
    assert trace.closing_pension_value == (
        trace.opening_pension_value
        + trace.pension_growth_amount
        + trace.pension_contribution_amount
    )


def test_preserved_wealth_warning_explains_non_liquid_final_value() -> None:
    """The warning is emitted only when remaining net worth cannot fund further spending."""
    configuration = load_configuration(_configuration_text())
    timeline = project_annually(configuration)

    assert preserved_wealth_warning(timeline[-1]) is None

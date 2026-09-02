"""Deterministic invariants for the inactive primary-residence boundary."""

from decimal import Decimal
from pathlib import Path

from engine.config import WealthOsConfig, load_configuration
from engine.reporting import summarize_net_worth
from engine.simulation import project_annually


def _configuration(value: str = "1500000", mortgage: str = "0") -> WealthOsConfig:
    text = Path("data/example_household.yaml").read_text(encoding="utf-8")
    text = text.replace("estimated_market_value: 1500000", f"estimated_market_value: {value}")
    text = text.replace("mortgage_balance: 0", f"mortgage_balance: {mortgage}")
    return load_configuration(text)


def test_residence_changes_household_but_not_planning_outputs() -> None:
    """An inactive home changes household position only."""
    baseline = _configuration()
    higher_home = _configuration("2000000")
    baseline_projection = project_annually(baseline)
    higher_projection = project_annually(higher_home)

    assert baseline_projection == higher_projection
    for baseline_year, higher_year in zip(baseline_projection, higher_projection, strict=True):
        assert baseline_year.liquid_assets == higher_year.liquid_assets
        assert baseline_year.withdrawal_amount == higher_year.withdrawal_amount
        assert baseline_year.cash_withdrawal == higher_year.cash_withdrawal
        assert baseline_year.etf_withdrawal == higher_year.etf_withdrawal
        assert baseline_year.property_value == higher_year.property_value
        assert baseline_year.amazon_concentration == higher_year.amazon_concentration
        assert baseline_year.net_worth == higher_year.net_worth
    assert summarize_net_worth(baseline_projection[-1], baseline).planning_net_worth == (
        summarize_net_worth(higher_projection[-1], higher_home).planning_net_worth
    )
    assert summarize_net_worth(higher_projection[-1], higher_home).household_net_worth - (
        summarize_net_worth(baseline_projection[-1], baseline).household_net_worth
    ) == Decimal("500000")


def test_mortgage_reduces_residence_equity_and_household_net_worth() -> None:
    """Represented residence debt is a household-position liability."""
    mortgage_free = _configuration()
    mortgaged = _configuration(mortgage="400000")
    free_summary = summarize_net_worth(project_annually(mortgage_free)[-1], mortgage_free)
    debt_summary = summarize_net_worth(project_annually(mortgaged)[-1], mortgaged)

    assert debt_summary.primary_residence_equity == Decimal("1100000")
    assert free_summary.household_net_worth - debt_summary.household_net_worth == Decimal("400000")


def test_no_implicit_residence_activation_switch_exists() -> None:
    """Home equity cannot be casually toggled into planning capital."""
    residence = _configuration().primary_residence

    assert residence is not None
    assert residence.purpose == "PRIMARY_RESIDENCE"
    assert "available_for_planning" not in type(residence).model_fields
    assert "active" not in type(residence).model_fields

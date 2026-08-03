"""Tests for the pure cash contribution and ETF growth simulation stage."""

from decimal import Decimal
from pathlib import Path

from engine.config import load_configuration
from engine.simulation import apply_cash_and_etf_growth, project_annually

EXAMPLE_CONFIGURATION = Path("tests/fixtures/legacy_household.yaml")


def test_working_years_add_savings_and_apply_etf_growth() -> None:
    """Working years add direct savings to cash and compound the ETF balance."""
    yaml_text = EXAMPLE_CONFIGURATION.read_text(encoding="utf-8").replace(
        "annual_grant_shares: 25", "annual_grant_shares: 0"
    )
    yaml_text = yaml_text.replace("target_retirement_income: 80000", "target_retirement_income: 0")
    configuration = load_configuration(yaml_text)

    first_year, second_year = project_annually(configuration)[:2]

    assert first_year.cash_balance == Decimal("75000")
    assert first_year.etf_value == Decimal("157500")
    assert second_year.cash_balance == Decimal("100000")
    assert second_year.etf_value == Decimal("165375")
    assert second_year.net_worth == (
        second_year.cash_balance
        + second_year.etf_value
        + second_year.amazon_value
        + second_year.pension_value
        + second_year.property_value
    )


def test_retirement_years_continue_etf_growth_without_cash_contributions() -> None:
    """Retirement rows grow ETFs but retain the final working-years cash balance."""
    yaml_text = EXAMPLE_CONFIGURATION.read_text(encoding="utf-8").replace(
        "annual_grant_shares: 25", "annual_grant_shares: 0"
    )
    yaml_text = yaml_text.replace("target_retirement_income: 80000", "target_retirement_income: 0")
    configuration = load_configuration(yaml_text)

    final_working_year, first_retirement_year = project_annually(configuration)[19:21]

    assert final_working_year.cash_balance == Decimal("550000")
    assert first_retirement_year.cash_balance == Decimal("550000")
    assert first_retirement_year.etf_value == final_working_year.etf_value * Decimal("1.05")


def test_zero_etf_growth_keeps_etf_balance_constant() -> None:
    """A zero configured growth rate preserves the initial ETF balance every year."""
    yaml_text = EXAMPLE_CONFIGURATION.read_text(encoding="utf-8").replace(
        "etf_growth_rate: 0.05", "etf_growth_rate: 0"
    )
    yaml_text = yaml_text.replace("target_retirement_income: 80000", "target_retirement_income: 0")

    projection = project_annually(load_configuration(yaml_text))

    assert projection[0].etf_value == Decimal("150000")
    assert projection[30].etf_value == Decimal("150000")


def test_negative_etf_growth_reduces_etf_balance() -> None:
    """A negative growth rate is applied once per projection year."""
    yaml_text = EXAMPLE_CONFIGURATION.read_text(encoding="utf-8").replace(
        "etf_growth_rate: 0.05", "etf_growth_rate: -0.10"
    )

    first_year, second_year = project_annually(load_configuration(yaml_text))[:2]

    assert first_year.etf_value == Decimal("135000")
    assert second_year.etf_value == Decimal("121500")


def test_growth_stage_is_pure_and_projection_is_repeatable() -> None:
    """The stage does not mutate its input and repeated projections are identical."""
    configuration = load_configuration(EXAMPLE_CONFIGURATION.read_text(encoding="utf-8"))
    original_rows = list(project_annually(configuration))
    original_snapshot = tuple(original_rows)

    updated_rows = apply_cash_and_etf_growth(original_rows, configuration)

    assert updated_rows is not original_rows
    assert tuple(original_rows) == original_snapshot
    assert project_annually(configuration) == project_annually(configuration)

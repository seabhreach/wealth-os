"""Tests for retirement spending, fixed-order withdrawals, and readiness reporting."""

from decimal import Decimal
from pathlib import Path

from engine.config import WealthOsConfig, load_configuration
from engine.reporting import summarize_retirement_readiness
from engine.simulation import apply_retirement_withdrawals, project_annually

EXAMPLE_CONFIGURATION = Path("tests/fixtures/legacy_household.yaml")


def _retirement_configuration(
    *,
    cash_balance: str,
    etf_value: str,
    vested_shares: str,
    share_price_usd: str,
    target_retirement_income: str,
    inflation_rate: str = "0",
    rental_properties: str = "rental_properties: []",
) -> WealthOsConfig:
    yaml_text = EXAMPLE_CONFIGURATION.read_text(encoding="utf-8")
    yaml_text = (
        yaml_text.replace("planned_retirement_age: 60", "planned_retirement_age: 41")
        .replace("life_expectancy: 95", "life_expectancy: 43")
        .replace("annual_savings: 25000", "annual_savings: 0")
        .replace("cash_balance: 50000", f"cash_balance: {cash_balance}")
        .replace("etf_value: 150000", f"etf_value: {etf_value}")
        .replace("etf_growth_rate: 0.05", "etf_growth_rate: 0")
        .replace("vested_shares: 100", f"vested_shares: {vested_shares}")
        .replace("annual_grant_shares: 25", "annual_grant_shares: 0")
        .replace("share_price_usd: 200", f"share_price_usd: {share_price_usd}")
        .replace("annual_growth_rate: 0.05", "annual_growth_rate: 0", 1)
        .replace("rental_properties: []", rental_properties)
        .replace("inflation_rate: 0.02", f"inflation_rate: {inflation_rate}")
        .replace(
            "target_retirement_income: 80000",
            f"target_retirement_income: {target_retirement_income}",
        )
    )
    return load_configuration(yaml_text)


def test_no_withdrawals_before_retirement_and_target_is_inflation_adjusted() -> None:
    """Working rows do not spend, while the first retirement target uses start-year inflation."""
    configuration = _retirement_configuration(
        cash_balance="200",
        etf_value="0",
        vested_shares="0",
        share_price_usd="0",
        target_retirement_income="100",
        inflation_rate="0.02",
    )

    working_year, retirement_year = project_annually(configuration)[:2]

    assert working_year.annual_spending == Decimal("0")
    assert working_year.withdrawal_amount == Decimal("0")
    assert retirement_year.annual_spending == Decimal("102.00")
    assert retirement_year.cash_withdrawal == Decimal("102.00")


def test_rental_income_reduces_gap_without_being_added_twice() -> None:
    """Rent is already in cash, so it reduces rather than duplicates retirement funding."""
    configuration = _retirement_configuration(
        cash_balance="200",
        etf_value="0",
        vested_shares="0",
        share_price_usd="0",
        target_retirement_income="100",
        inflation_rate="0.02",
        rental_properties="""rental_properties:
  - name: Existing home
    purchase_year: 2020
    purchase_price: 100000
    current_value: 150000
    annual_net_rent: 20
    annual_growth_rate: 0""",
    )

    retirement_year = project_annually(configuration)[1]

    assert retirement_year.rental_income == Decimal("20.40")
    assert retirement_year.withdrawal_amount == Decimal("81.60")
    assert retirement_year.cash_balance == Decimal("158.80")


def test_cash_then_etf_then_amazon_withdrawal_order_and_partial_share_sale() -> None:
    """The gap exhausts cash then ETFs and sells only the Amazon share fraction required."""
    configuration = _retirement_configuration(
        cash_balance="10",
        etf_value="20",
        vested_shares="1",
        share_price_usd="100",
        target_retirement_income="100",
    )

    retirement_year = project_annually(configuration)[1]

    assert retirement_year.cash_withdrawal == Decimal("10")
    assert retirement_year.etf_withdrawal == Decimal("20")
    assert retirement_year.amazon_withdrawal == Decimal("70")
    assert retirement_year.amazon_shares == Decimal("0.3")
    assert retirement_year.amazon_value == Decimal("30.0")
    assert retirement_year.withdrawal_amount == Decimal("100")
    assert retirement_year.unfunded_spending == Decimal("0")


def test_cash_only_and_cash_then_etf_withdrawals_keep_balances_non_negative() -> None:
    """Cash funds first, then ETFs, and neither balance drops below zero."""
    cash_only = _retirement_configuration(
        cash_balance="200",
        etf_value="0",
        vested_shares="0",
        share_price_usd="0",
        target_retirement_income="100",
    )
    cash_then_etf = _retirement_configuration(
        cash_balance="60",
        etf_value="100",
        vested_shares="0",
        share_price_usd="0",
        target_retirement_income="100",
    )

    cash_only_year = project_annually(cash_only)[1]
    cash_then_etf_year = project_annually(cash_then_etf)[1]

    assert cash_only_year.cash_withdrawal == Decimal("100")
    assert cash_only_year.etf_withdrawal == Decimal("0")
    assert cash_then_etf_year.cash_withdrawal == Decimal("60")
    assert cash_then_etf_year.etf_withdrawal == Decimal("40")
    assert cash_then_etf_year.cash_balance == Decimal("0")
    assert cash_then_etf_year.etf_value == Decimal("60")


def test_unfunded_spending_preserves_pension_property_and_non_negative_assets() -> None:
    """Exhausted liquid assets create an explicit shortfall without touching other assets."""
    configuration = _retirement_configuration(
        cash_balance="10",
        etf_value="20",
        vested_shares="1",
        share_price_usd="30",
        target_retirement_income="100",
        rental_properties="""rental_properties:
  - name: Existing home
    purchase_year: 2020
    purchase_price: 100000
    current_value: 150000
    annual_net_rent: 0
    annual_growth_rate: 0""",
    )

    retirement_year = project_annually(configuration)[1]

    assert retirement_year.unfunded_spending == Decimal("40")
    assert retirement_year.retirement_target_met is False
    assert retirement_year.cash_balance == Decimal("0")
    assert retirement_year.etf_value == Decimal("0")
    assert retirement_year.amazon_value == Decimal("0")
    assert retirement_year.pension_value == Decimal("208000.00")
    assert retirement_year.property_value == Decimal("150000")


def test_readiness_summary_reports_funded_and_unfunded_outcomes() -> None:
    """Readiness is true only when every retirement row meets the spending target."""
    funded_configuration = _retirement_configuration(
        cash_balance="1000",
        etf_value="0",
        vested_shares="0",
        share_price_usd="0",
        target_retirement_income="100",
    )
    unfunded_configuration = _retirement_configuration(
        cash_balance="0",
        etf_value="0",
        vested_shares="0",
        share_price_usd="0",
        target_retirement_income="100",
    )

    funded_summary = summarize_retirement_readiness(project_annually(funded_configuration))
    unfunded_summary = summarize_retirement_readiness(project_annually(unfunded_configuration))

    assert funded_summary.retirement_ready is True
    assert funded_summary.first_retirement_target_met is True
    assert funded_summary.first_unfunded_year is None
    assert unfunded_summary.retirement_ready is False
    assert unfunded_summary.first_retirement_target_met is False
    assert unfunded_summary.first_unfunded_year == 2027


def test_withdrawal_stage_is_pure_and_projection_is_deterministic() -> None:
    """The stage returns a new tuple without mutating its source or changing repeatability."""
    configuration = _retirement_configuration(
        cash_balance="10",
        etf_value="20",
        vested_shares="1",
        share_price_usd="100",
        target_retirement_income="100",
    )
    original_timeline = project_annually(configuration)

    updated_timeline = apply_retirement_withdrawals(original_timeline, configuration)

    assert updated_timeline is not original_timeline
    assert original_timeline == project_annually(configuration)
    assert project_annually(configuration) == project_annually(configuration)

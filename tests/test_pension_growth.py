"""Tests for pension opening values, growth, contributions, and aggregation."""

from decimal import Decimal
from pathlib import Path

from engine.config import WealthOsConfig, load_configuration
from engine.simulation import apply_pension_growth, project_annually

EXAMPLE_CONFIGURATION = Path("tests/fixtures/legacy_household.yaml")


def _configuration_with_pensions(pensions: str) -> WealthOsConfig:
    yaml_text = EXAMPLE_CONFIGURATION.read_text(encoding="utf-8")
    pension_section = yaml_text[
        yaml_text.index("pensions:") : yaml_text.index("rental_properties:")
    ]
    return load_configuration(yaml_text.replace(pension_section, pensions))


def test_single_pension_uses_opening_value_then_growth_and_contribution() -> None:
    """The first row is opening value and later working rows grow before contributing."""
    configuration = _configuration_with_pensions(
        """pensions:
  - name: Solo pension
    owner: Justin
    current_value: 100000
    annual_growth_rate: 0.10
    annual_contribution: 10000
"""
    )

    opening_year, second_year = project_annually(configuration)[:2]

    assert opening_year.pension_value == Decimal("100000")
    assert opening_year.pension_values[0].value == Decimal("100000")
    assert second_year.pension_value == Decimal("120000")


def test_multiple_pensions_aggregate_and_remain_outside_cash() -> None:
    """Pension balances aggregate for net worth without affecting cash balances."""
    configuration = _configuration_with_pensions(
        """pensions:
  - name: Justin pension
    owner: Justin
    current_value: 100000
    annual_growth_rate: 0
    annual_contribution: 0
  - name: Wife pension
    owner: Wife
    current_value: 200000
    annual_growth_rate: 0
    annual_contribution: 0
"""
    )

    first_year = project_annually(configuration)[0]

    assert first_year.pension_value == Decimal("300000")
    assert [balance.owner for balance in first_year.pension_values] == ["Justin", "Wife"]
    assert first_year.net_worth == (
        first_year.cash_balance
        + first_year.etf_value
        + first_year.amazon_value
        + first_year.pension_value
        + first_year.property_value
    )


def test_contributions_stop_at_retirement_while_growth_continues() -> None:
    """The household retirement age ends contributions but not pension growth."""
    configuration = _configuration_with_pensions(
        """pensions:
  - name: Solo pension
    owner: Justin
    current_value: 100000
    annual_growth_rate: 0.10
    annual_contribution: 10000
"""
    )

    previous_working_year, final_working_year, retirement_year, post_retirement_year = (
        project_annually(configuration)[18:22]
    )

    assert final_working_year.pension_value == (
        previous_working_year.pension_value * Decimal("1.10") + Decimal("10000")
    )
    assert retirement_year.pension_value == final_working_year.pension_value * Decimal("1.10")
    assert post_retirement_year.pension_value == retirement_year.pension_value * Decimal("1.10")


def test_zero_and_negative_growth_and_zero_contributions_are_supported() -> None:
    """Pension assumptions apply deterministically, including zero and negative rates."""
    zero_growth = _configuration_with_pensions(
        """pensions:
  - name: Zero pension
    owner: Justin
    current_value: 100000
    annual_growth_rate: 0
    annual_contribution: 0
"""
    )
    negative_growth = _configuration_with_pensions(
        """pensions:
  - name: Negative pension
    owner: Justin
    current_value: 100000
    annual_growth_rate: -0.10
    annual_contribution: 0
"""
    )

    assert project_annually(zero_growth)[1].pension_value == Decimal("100000")
    assert project_annually(negative_growth)[1].pension_value == Decimal("90000")


def test_pension_stage_is_pure_and_projection_is_deterministic() -> None:
    """The stage returns a new tuple without changing its source timeline or future runs."""
    configuration = load_configuration(EXAMPLE_CONFIGURATION.read_text(encoding="utf-8"))
    original_timeline = project_annually(configuration)

    updated_timeline = apply_pension_growth(original_timeline, configuration)

    assert updated_timeline is not original_timeline
    assert original_timeline == project_annually(configuration)
    assert project_annually(configuration) == project_annually(configuration)

"""Tests for rental-property purchases, appreciation, rent, and cashflow."""

from decimal import Decimal
from pathlib import Path

import pytest

from engine.config import WealthOsConfig, load_configuration
from engine.simulation import PropertySimulationError, apply_rental_properties, project_annually

EXAMPLE_CONFIGURATION = Path("tests/fixtures/legacy_household.yaml")


def _configuration_with_properties(properties: str) -> WealthOsConfig:
    yaml_text = (
        EXAMPLE_CONFIGURATION.read_text(encoding="utf-8")
        .replace("annual_grant_shares: 25", "annual_grant_shares: 0")
        .replace("etf_growth_rate: 0.05", "etf_growth_rate: 0")
        .replace("annual_growth_rate: 0.05", "annual_growth_rate: 0", 1)
        .replace("rental_properties: []", properties)
    )
    return load_configuration(yaml_text)


def test_no_properties_leave_property_aggregates_empty() -> None:
    """An empty property list produces zero property values, rent, and ownership counts."""
    projection = project_annually(
        load_configuration(EXAMPLE_CONFIGURATION.read_text(encoding="utf-8"))
    )

    assert all(year.property_value == Decimal("0") for year in projection)
    assert all(year.rental_income == Decimal("0") for year in projection)
    assert all(year.property_count == 0 for year in projection)


def test_existing_property_opens_at_current_value_and_receives_rent() -> None:
    """A property purchased before the start year is owned from the first projection row."""
    configuration = _configuration_with_properties(
        """rental_properties:
  - name: Existing home
    purchase_year: 2020
    purchase_price: 100000
    current_value: 150000
    annual_net_rent: 10000
    annual_growth_rate: 0.10"""
    )

    opening_year, following_year = project_annually(configuration)[:2]

    assert opening_year.property_value == Decimal("150000")
    assert opening_year.rental_income == Decimal("10000")
    assert opening_year.property_count == 1
    assert opening_year.cash_balance == Decimal("85000")
    assert following_year.property_value == Decimal("165000")
    assert following_year.rental_income == Decimal("10200")


def test_future_purchase_deducts_cash_without_same_year_appreciation() -> None:
    """A future purchase begins rent immediately and appreciates only after its purchase year."""
    configuration = _configuration_with_properties(
        """rental_properties:
  - name: Future home
    purchase_year: 2028
    purchase_price: 100000
    current_value: 150000
    annual_net_rent: 10000
    annual_growth_rate: 0.10"""
    )

    before_purchase, purchase_year, following_year = project_annually(configuration)[1:4]

    assert before_purchase.property_value == Decimal("0")
    assert before_purchase.rental_income == Decimal("0")
    assert before_purchase.property_count == 0
    assert purchase_year.property_value == Decimal("100000")
    assert purchase_year.rental_income == Decimal("10000")
    assert purchase_year.cash_balance == Decimal("35000")
    assert purchase_year.property_count == 1
    assert following_year.property_value == Decimal("110000")
    assert following_year.rental_income == Decimal("10200")


def test_multiple_properties_aggregate_values_income_and_count() -> None:
    """Owned and newly purchased properties aggregate into one projection-year view."""
    configuration = _configuration_with_properties(
        """rental_properties:
  - name: Existing home
    purchase_year: 2020
    purchase_price: 100000
    current_value: 150000
    annual_net_rent: 10000
    annual_growth_rate: 0.10
  - name: Future home
    purchase_year: 2028
    purchase_price: 100000
    current_value: 150000
    annual_net_rent: 10000
    annual_growth_rate: 0.10"""
    )

    purchase_year = project_annually(configuration)[2]

    assert purchase_year.property_count == 2
    assert purchase_year.property_value == Decimal("281500")
    assert purchase_year.rental_income == Decimal("20404.0000")


def test_insufficient_cash_for_future_purchase_raises_clear_error() -> None:
    """The MVP rejects a purchase rather than creating a mortgage or negative balance."""
    configuration = _configuration_with_properties(
        """rental_properties:
  - name: Unaffordable home
    purchase_year: 2027
    purchase_price: 110000
    current_value: 150000
    annual_net_rent: 10000
    annual_growth_rate: 0.10"""
    )

    with pytest.raises(
        PropertySimulationError,
        match="Insufficient cash to purchase 'Unaffordable home' in 2027",
    ):
        project_annually(configuration)


def test_property_stage_is_pure_and_projection_is_deterministic() -> None:
    """The property stage returns a new tuple and does not change its input timeline."""
    configuration = _configuration_with_properties(
        """rental_properties:
  - name: Existing home
    purchase_year: 2020
    purchase_price: 100000
    current_value: 150000
    annual_net_rent: 10000
    annual_growth_rate: 0.10"""
    )
    original_timeline = project_annually(configuration)

    updated_timeline = apply_rental_properties(original_timeline, configuration)

    assert updated_timeline is not original_timeline
    assert original_timeline == project_annually(configuration)
    assert project_annually(configuration) == project_annually(configuration)

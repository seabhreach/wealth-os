"""Integration coverage for opt-in Irish tax in retirement funding."""

from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from engine.config import WealthOsConfig, load_configuration
from engine.simulation import project_annually
from engine.simulation.projection import ProjectionYear


def _baseline_data() -> dict[str, Any]:
    """Return a mutable copy of the published tax-enabled example configuration."""
    raw = yaml.safe_load(Path("data/example_household.yaml").read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return raw


def _configuration(data: dict[str, Any]) -> WealthOsConfig:
    """Validate a deliberately varied test configuration."""
    return load_configuration(yaml.safe_dump(data, sort_keys=False))


def _year(configuration: WealthOsConfig, calendar_year: int) -> ProjectionYear:
    return next(
        year for year in project_annually(configuration) if year.calendar_year == calendar_year
    )


def test_tax_disabled_preserves_the_gross_income_funding_path() -> None:
    """Removing the opt-in section leaves the legacy projection semantics intact."""
    data = _baseline_data()
    data.pop("tax")
    configuration = _configuration(data)
    first_retirement = _year(configuration, 2032)

    assert first_retirement.tax_modelling_enabled is False
    assert first_retirement.household_tax_result is None
    assert first_retirement.total_estimated_tax == Decimal("0")
    assert first_retirement.withdrawal_amount == Decimal("47121.32032000000000")


def test_enabled_tax_reconciles_first_retirement_income_to_spending() -> None:
    """Tax reduces recurring income before liquid assets fund the remaining target."""
    first_retirement = _year(_configuration(_baseline_data()), 2032)

    assert first_retirement.gross_recurring_income == (
        first_retirement.gross_rental_profit
        + first_retirement.gross_private_pension_income
        + first_retirement.gross_state_pension_income
    )
    assert first_retirement.net_recurring_income == (
        first_retirement.gross_recurring_income - first_retirement.total_estimated_tax
    )
    assert first_retirement.annual_spending == (
        first_retirement.net_recurring_income
        + first_retirement.withdrawal_amount
        + first_retirement.unfunded_spending
        - first_retirement.after_tax_surplus
    )
    assert first_retirement.withdrawal_amount > Decimal("47121.32032000000000")


@pytest.mark.parametrize(
    ("justin_share", "wife_share"),
    (("1.00", "0.00"), ("0.75", "0.25"), ("0.50", "0.50"), ("0.00", "1.00")),
)
def test_ownership_changes_tax_allocation_without_changing_property_cashflow(
    justin_share: str, wife_share: str
) -> None:
    """Beneficial ownership affects only individual taxable rental profit."""
    data = _baseline_data()
    properties = data["rental_properties"]
    assert isinstance(properties, list)
    properties[0]["owners"] = [
        {"person": "Justin", "share": justin_share},
        {"person": "Wife", "share": wife_share},
    ]
    year = _year(_configuration(data), 2032)
    assert year.household_tax_result is not None
    person_results = {result.person: result for result in year.household_tax_result.per_person}
    expected_rent = year.rental_income
    assert person_results["Justin"].gross_income - year.private_pension_income == (
        expected_rent * Decimal(justin_share)
    )
    assert person_results["Wife"].gross_income == expected_rent * Decimal(wife_share)
    assert year.rental_income == Decimal("17665.2928512000")


def test_state_pension_is_income_taxable_but_not_usc_taxable() -> None:
    """Owner-specific State Pension begins for Justin in 2038 and remains USC-exempt."""
    year = _year(_configuration(_baseline_data()), 2038)
    assert year.household_tax_result is not None
    justin = next(
        result for result in year.household_tax_result.per_person if result.person == "Justin"
    )
    assert justin.gross_income - justin.usc_taxable == year.state_pension_income


def test_tax_enabled_rejects_missing_property_ownership() -> None:
    """Enabled tax never silently infers ownership for an income-producing property."""
    data = deepcopy(_baseline_data())
    properties = data["rental_properties"]
    assert isinstance(properties, list)
    properties[0].pop("owners")
    with pytest.raises(ValidationError, match="requires owners"):
        _configuration(data)


def test_tax_rule_indexation_changes_future_tax_bands_deterministically() -> None:
    """The optional future-rule assumption lowers the otherwise nominal future tax result."""
    indexed = _year(_configuration(_baseline_data()), 2038)
    data = _baseline_data()
    tax = data["tax"]
    assert isinstance(tax, dict)
    tax["index_future_rules_with_inflation"] = False
    nominal = _year(_configuration(data), 2038)

    assert indexed.total_estimated_tax < nominal.total_estimated_tax
    assert indexed == _year(_configuration(_baseline_data()), 2038)

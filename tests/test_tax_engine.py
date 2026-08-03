"""Golden examples for the standalone configurable Irish planning-tax engine."""

from decimal import Decimal
from pathlib import Path

import pytest

from engine.tax import HouseholdTaxInput, PersonTaxInput, calculate_household_tax, load_tax_rules


def test_joint_income_tax_usc_and_state_pension_usc_exemption() -> None:
    """State Pension is Income-Tax taxable but excluded from USC."""
    rules = load_tax_rules(Path("data/tax/ireland_2026.yaml"))
    tax_input = HouseholdTaxInput(
        "joint",
        (
            PersonTaxInput("Justin", Decimal("60000"), Decimal("15000"), Decimal("8000")),
            PersonTaxInput("Wife", Decimal("0"), Decimal("15000"), Decimal("8000")),
        ),
    )
    result = calculate_household_tax(tax_input, rules)
    assert result.per_person[0].usc_taxable == Decimal("68000")
    assert result.per_person[1].usc_taxable == Decimal("8000")
    assert result.total_prsi == Decimal("0")
    assert calculate_household_tax(HouseholdTaxInput("joint", ()), rules).total_tax == Decimal("0")


def test_unsupported_assessment_is_rejected_and_results_repeat() -> None:
    rules = load_tax_rules(Path("data/tax/ireland_2026.yaml"))
    tax_input = HouseholdTaxInput(
        "joint", (PersonTaxInput("Justin", rental_profit=Decimal("16000")),)
    )
    assert calculate_household_tax(tax_input, rules) == calculate_household_tax(tax_input, rules)
    with pytest.raises(ValueError, match="Only joint assessment"):
        calculate_household_tax(HouseholdTaxInput("separate", ()), rules)

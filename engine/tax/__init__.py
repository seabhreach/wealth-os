"""Standalone configurable Irish planning-tax engine."""

from engine.tax.calculator import calculate_household_tax
from engine.tax.models import HouseholdTaxInput, HouseholdTaxResult, PersonTaxInput, PersonTaxResult
from engine.tax.rules import TaxRules, index_tax_rules, load_tax_rules

__all__ = [
    "HouseholdTaxInput",
    "HouseholdTaxResult",
    "PersonTaxInput",
    "PersonTaxResult",
    "TaxRules",
    "calculate_household_tax",
    "index_tax_rules",
    "load_tax_rules",
]

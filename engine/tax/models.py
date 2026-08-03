"""Immutable inputs and transparent results for the standalone planning-tax engine."""

from dataclasses import dataclass
from decimal import Decimal

ZERO = Decimal("0")


@dataclass(frozen=True, slots=True)
class PersonTaxInput:
    person: str
    private_pension_income: Decimal = ZERO
    state_pension_income: Decimal = ZERO
    rental_profit: Decimal = ZERO
    prsi_taxable_income: Decimal | None = None

    @property
    def gross_income(self) -> Decimal:
        return self.private_pension_income + self.state_pension_income + self.rental_profit

    @property
    def usc_taxable_income(self) -> Decimal:
        return self.private_pension_income + self.rental_profit

    @property
    def prsi_income(self) -> Decimal:
        """Return explicitly configured PRSI income, or legacy USC-equivalent income."""
        if self.prsi_taxable_income is None:
            return self.usc_taxable_income
        return self.prsi_taxable_income


@dataclass(frozen=True, slots=True)
class HouseholdTaxInput:
    assessment_basis: str
    people: tuple[PersonTaxInput, ...]


@dataclass(frozen=True, slots=True)
class PersonTaxResult:
    person: str
    gross_income: Decimal
    income_taxable: Decimal
    usc_taxable: Decimal
    standard_rate_income: Decimal
    higher_rate_income: Decimal
    income_tax_before_credits: Decimal
    credits: Decimal
    income_tax: Decimal
    usc: Decimal
    prsi: Decimal
    total_tax: Decimal
    effective_rate: Decimal
    net_income: Decimal


@dataclass(frozen=True, slots=True)
class HouseholdTaxResult:
    tax_year: int
    per_person: tuple[PersonTaxResult, ...]
    total_income_tax: Decimal
    total_usc: Decimal
    total_prsi: Decimal
    total_tax: Decimal
    effective_rate: Decimal

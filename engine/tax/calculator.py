"""Pure joint-assessment Income Tax, individual USC, and configured PRSI calculations."""

from decimal import Decimal

from engine.tax.models import HouseholdTaxInput, HouseholdTaxResult, PersonTaxInput, PersonTaxResult
from engine.tax.rules import TaxRules

ZERO = Decimal("0")


def calculate_household_tax(input: HouseholdTaxInput, rules: TaxRules) -> HouseholdTaxResult:
    """Calculate a transparent planning estimate; only joint assessment is supported."""
    if input.assessment_basis != "joint":
        raise ValueError("Only joint assessment is supported by the tax engine")
    gross = sum((person.gross_income for person in input.people), start=ZERO)
    lower_income = min((person.gross_income for person in input.people), default=ZERO)
    band = rules.married_standard_band + min(lower_income, rules.lower_earner_increase_cap)
    before_credits = (
        min(gross, band) * rules.standard_rate + max(gross - band, ZERO) * rules.higher_rate
    )
    standard_rate_income = min(gross, band)
    higher_rate_income = max(gross - band, ZERO)
    income_tax = max(before_credits - rules.married_tax_credit, ZERO)
    usc_values = tuple(_usc(person.usc_taxable_income, rules) for person in input.people)
    prsi_values = tuple(
        person.prsi_income * rules.prsi_rate if rules.prsi_enabled else ZERO
        for person in input.people
    )
    weights = tuple(person.gross_income / gross if gross else ZERO for person in input.people)
    results = tuple(
        _person_result(
            person,
            standard_rate_income * weight,
            higher_rate_income * weight,
            before_credits * weight,
            rules.married_tax_credit * weight,
            income_tax * weight,
            usc,
            prsi,
        )
        for person, weight, usc, prsi in zip(
            input.people, weights, usc_values, prsi_values, strict=True
        )
    )
    total_usc = sum(usc_values, start=ZERO)
    total_prsi = sum(prsi_values, start=ZERO)
    total_tax = income_tax + total_usc + total_prsi
    return HouseholdTaxResult(
        rules.tax_year,
        results,
        income_tax,
        total_usc,
        total_prsi,
        total_tax,
        total_tax / gross if gross else ZERO,
    )


def _person_result(
    person: PersonTaxInput,
    standard_rate_income: Decimal,
    higher_rate_income: Decimal,
    before: Decimal,
    credits: Decimal,
    income_tax: Decimal,
    usc: Decimal,
    prsi: Decimal,
) -> PersonTaxResult:
    total = income_tax + usc + prsi
    return PersonTaxResult(
        person.person,
        person.gross_income,
        person.gross_income,
        person.usc_taxable_income,
        standard_rate_income,
        higher_rate_income,
        before,
        credits,
        income_tax,
        usc,
        prsi,
        total,
        total / person.gross_income if person.gross_income else ZERO,
        person.gross_income - total,
    )


def _usc(income: Decimal, rules: TaxRules) -> Decimal:
    if income <= rules.usc_exemption_threshold:
        return ZERO
    lower = ZERO
    total = ZERO
    for band in rules.usc_bands:
        amount = (
            max(income - lower, ZERO)
            if band.upper_limit is None
            else min(max(income - lower, ZERO), band.upper_limit - lower)
        )
        total += amount * band.rate
        if band.upper_limit is None:
            break
        lower = band.upper_limit
    return total

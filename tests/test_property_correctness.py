"""Regression tests for rental cash recognition and employed-year rental tax."""

from decimal import Decimal
from pathlib import Path

from engine.config import WealthOsConfig, load_configuration
from engine.simulation import project_annually


def _configuration() -> WealthOsConfig:
    return load_configuration(Path("data/example_household.yaml").read_text(encoding="utf-8"))


def test_rent_is_recognized_once_in_retirement_cash() -> None:
    """Rent used against spending must not also remain in closing cash."""
    projection = project_annually(_configuration())
    opening = next(year for year in projection if year.calendar_year == 2031)
    retirement = next(year for year in projection if year.calendar_year == 2032)

    assert retirement.after_tax_surplus == Decimal("0")
    assert retirement.cash_balance == opening.cash_balance - retirement.cash_withdrawal


def test_employed_year_rent_is_taxed_in_employment_context() -> None:
    """A planned property's rent is not tax-free before retirement."""
    purchase_year = next(
        year for year in project_annually(_configuration()) if year.calendar_year == 2027
    )

    assert purchase_year.employed is True
    assert purchase_year.rental_income == Decimal("16000")
    assert purchase_year.estimated_income_tax == Decimal("4800")
    assert purchase_year.estimated_usc == Decimal("640")
    assert purchase_year.estimated_prsi == Decimal("0")
    assert purchase_year.total_estimated_tax < purchase_year.rental_income


def test_employed_year_rental_ownership_is_preserved() -> None:
    """The marginal employed-year calculation retains owner-specific rent."""
    year = next(year for year in project_annually(_configuration()) if year.calendar_year == 2027)

    assert year.household_tax_result is not None
    assert tuple(result.gross_income for result in year.household_tax_result.per_person) == (
        Decimal("8000"),
        Decimal("8000"),
    )

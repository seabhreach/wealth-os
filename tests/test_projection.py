"""Tests for the deterministic Task 2 annual projection timeline."""

from decimal import Decimal
from pathlib import Path

from engine.config import load_configuration
from engine.simulation import project_annually

EXAMPLE_CONFIGURATION = Path("tests/fixtures/legacy_household.yaml")


def test_projection_includes_every_year_through_life_expectancy() -> None:
    """The timeline is inclusive of the current and life-expectancy ages."""
    configuration = load_configuration(EXAMPLE_CONFIGURATION.read_text(encoding="utf-8"))

    projection = project_annually(configuration)

    assert len(projection) == 56
    assert projection[0].calendar_year == 2026
    assert projection[0].age == 40
    assert projection[-1].calendar_year == 2081
    assert projection[-1].age == 95


def test_projection_marks_working_and_retirement_years() -> None:
    """Salary and direct annual savings stop at the retirement age."""
    configuration = load_configuration(EXAMPLE_CONFIGURATION.read_text(encoding="utf-8"))

    projection = project_annually(configuration)
    final_working_year = projection[19]
    first_retirement_year = projection[20]

    assert final_working_year.age == 59
    assert final_working_year.employed is True
    assert final_working_year.salary == Decimal("100000")
    assert final_working_year.annual_savings == Decimal("25000")
    assert first_retirement_year.age == 60
    assert first_retirement_year.employed is False
    assert first_retirement_year.salary == Decimal("0")
    assert first_retirement_year.annual_savings == Decimal("0")
    assert first_retirement_year.withdrawal_amount > Decimal("0")


def test_retirement_spending_is_inflation_adjusted() -> None:
    """The retirement target increases with inflation once retirement begins."""
    configuration = load_configuration(EXAMPLE_CONFIGURATION.read_text(encoding="utf-8"))

    first_retirement_year = project_annually(configuration)[20]

    assert first_retirement_year.annual_spending == Decimal("80000") * Decimal("1.02") ** 20
    assert first_retirement_year.withdrawal_amount > Decimal("0")

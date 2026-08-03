"""Retirement-readiness summary derived from completed annual projection rows."""

from dataclasses import dataclass
from decimal import Decimal

from engine.simulation.projection import ProjectionYear


@dataclass(frozen=True, slots=True)
class RetirementReadinessSummary:
    """The MVP retirement-readiness results through the configured life expectancy."""

    retirement_age: int
    first_retirement_year: int
    first_retirement_spending_target: Decimal
    first_retirement_rental_income: Decimal
    first_retirement_required_withdrawal: Decimal
    retirement_ready: bool
    first_retirement_target_met: bool
    first_unfunded_year: int | None
    age_at_first_unfunded_year: int | None
    minimum_annual_surplus_or_shortfall: Decimal
    minimum_funded_margin: Decimal
    liquid_assets_at_retirement: Decimal
    liquid_assets_at_life_expectancy: Decimal
    pension_value_at_life_expectancy: Decimal
    property_value_at_life_expectancy: Decimal
    net_worth_at_life_expectancy: Decimal


def summarize_retirement_readiness(
    timeline: tuple[ProjectionYear, ...],
) -> RetirementReadinessSummary:
    """Summarize retirement funding outcomes from a completed annual projection."""
    retirement_years = tuple(year for year in timeline if not year.employed)
    first_retirement_year = retirement_years[0]
    first_unfunded_year = next(
        (year.calendar_year for year in retirement_years if year.unfunded_spending > Decimal("0")),
        None,
    )
    first_unfunded_projection = next(
        (year for year in retirement_years if year.unfunded_spending > Decimal("0")), None
    )
    minimum_annual_surplus_or_shortfall = min(
        (year.rental_income - year.annual_spending for year in retirement_years),
        default=Decimal("0"),
    )
    final_year = timeline[-1]

    return RetirementReadinessSummary(
        retirement_age=first_retirement_year.age,
        first_retirement_year=first_retirement_year.calendar_year,
        first_retirement_spending_target=first_retirement_year.annual_spending,
        first_retirement_rental_income=first_retirement_year.rental_income,
        first_retirement_required_withdrawal=first_retirement_year.withdrawal_amount,
        retirement_ready=all(year.retirement_target_met for year in retirement_years),
        first_retirement_target_met=first_retirement_year.retirement_target_met,
        first_unfunded_year=first_unfunded_year,
        age_at_first_unfunded_year=(
            first_unfunded_projection.age if first_unfunded_projection is not None else None
        ),
        minimum_annual_surplus_or_shortfall=minimum_annual_surplus_or_shortfall,
        minimum_funded_margin=min(
            (year.liquid_assets - year.unfunded_spending for year in retirement_years),
            default=Decimal("0"),
        ),
        liquid_assets_at_retirement=first_retirement_year.liquid_assets,
        liquid_assets_at_life_expectancy=final_year.liquid_assets,
        pension_value_at_life_expectancy=final_year.pension_value,
        property_value_at_life_expectancy=final_year.property_value,
        net_worth_at_life_expectancy=final_year.net_worth,
    )

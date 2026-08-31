"""Reporting-only reconciliation for planned-property scenario comparisons."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from engine.config.models import RentalPropertyConfig
from engine.reporting.advisor import ScenarioResult

ZERO = Decimal("0")


@dataclass(frozen=True, slots=True)
class PropertyScenarioReconciliation:
    """Existing deterministic facts explaining an include/exclude comparison."""

    purchase_year: int
    purchase_price: Decimal
    purchase_year_liquid_effect: Decimal
    configured_annual_net_rent: Decimal
    cumulative_modelled_rent: Decimal
    cumulative_estimated_tax_difference: Decimal
    cumulative_liquid_funding_preserved: Decimal
    final_liquid_assets_difference: Decimal
    final_property_value_difference: Decimal
    final_net_worth_difference: Decimal


def reconcile_property_scenarios(
    included: ScenarioResult,
    excluded: ScenarioResult,
    property_config: RentalPropertyConfig,
) -> PropertyScenarioReconciliation:
    """Reconcile two completed scenarios without changing either projection."""

    purchase_year = property_config.purchase_year
    included_purchase = next(y for y in included.projection if y.calendar_year == purchase_year)
    excluded_purchase = next(y for y in excluded.projection if y.calendar_year == purchase_year)
    return PropertyScenarioReconciliation(
        purchase_year=purchase_year,
        purchase_price=property_config.purchase_price,
        purchase_year_liquid_effect=(
            included_purchase.liquid_assets - excluded_purchase.liquid_assets
        ),
        configured_annual_net_rent=property_config.annual_net_rent,
        cumulative_modelled_rent=sum(
            (year.rental_income for year in included.projection), start=ZERO
        ),
        cumulative_estimated_tax_difference=sum(
            (
                included_year.total_estimated_tax - excluded_year.total_estimated_tax
                for included_year, excluded_year in zip(
                    included.projection, excluded.projection, strict=True
                )
            ),
            start=ZERO,
        ),
        cumulative_liquid_funding_preserved=sum(
            (
                excluded_year.withdrawal_amount - included_year.withdrawal_amount
                for included_year, excluded_year in zip(
                    included.projection, excluded.projection, strict=True
                )
            ),
            start=ZERO,
        ),
        final_liquid_assets_difference=(
            included.metrics.liquid_assets_at_life_expectancy
            - excluded.metrics.liquid_assets_at_life_expectancy
        ),
        final_property_value_difference=(
            included.metrics.final_property_value - excluded.metrics.final_property_value
        ),
        final_net_worth_difference=(
            included.metrics.final_net_worth - excluded.metrics.final_net_worth
        ),
    )

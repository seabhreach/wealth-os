"""Rental-property purchases, appreciation, and rental-income cashflows."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from engine.config.models import WealthOsConfig

if TYPE_CHECKING:
    from engine.config.models import RentalPropertyConfig
    from engine.simulation.projection import ProjectionYear


ZERO = Decimal("0")
ONE = Decimal("1")


class PropertySimulationError(ValueError):
    """Raised when a configured rental-property purchase cannot be funded."""


def apply_rental_properties(
    timeline: tuple[ProjectionYear, ...], config: WealthOsConfig
) -> tuple[ProjectionYear, ...]:
    """Return a new projection after property purchases, growth, and rental income.

    Existing properties open at their current value. Future purchases are paid in full from
    available cash and receive full-year rent, but are not appreciated until the next year.
    """
    previous_values = [ZERO] * len(config.rental_properties)
    cumulative_property_cashflow = ZERO
    updated_timeline: list[ProjectionYear] = []

    for projection_year in timeline:
        property_values, rental_income, purchase_outlay, property_count = _calculate_properties(
            projection_year=projection_year,
            config=config,
            previous_values=previous_values,
        )
        cash_before_purchase = projection_year.cash_balance + cumulative_property_cashflow

        if purchase_outlay > cash_before_purchase:
            property_names = _purchase_names(projection_year.calendar_year, config)
            message = (
                f"Insufficient cash to purchase {property_names} "
                f"in {projection_year.calendar_year}."
            )
            raise PropertySimulationError(message)

        cash_balance = cash_before_purchase - purchase_outlay + rental_income
        cumulative_property_cashflow += rental_income - purchase_outlay
        property_value = sum(property_values, start=ZERO)
        net_worth = (
            cash_balance
            + projection_year.etf_value
            + projection_year.amazon_value
            + projection_year.pension_value
            + property_value
        )
        amazon_concentration = (
            projection_year.amazon_value / net_worth if net_worth != ZERO else ZERO
        )
        updated_timeline.append(
            replace(
                projection_year,
                cash_balance=cash_balance,
                property_value=property_value,
                rental_income=rental_income,
                property_count=property_count,
                amazon_concentration=amazon_concentration,
                net_worth=net_worth,
            )
        )
        previous_values = property_values

    return tuple(updated_timeline)


def _calculate_properties(
    *,
    projection_year: ProjectionYear,
    config: WealthOsConfig,
    previous_values: list[Decimal],
) -> tuple[list[Decimal], Decimal, Decimal, int]:
    """Calculate this year's per-property balances and cashflows without mutation."""
    property_values: list[Decimal] = []
    rental_income = ZERO
    purchase_outlay = ZERO
    property_count = 0

    for property_config, previous_value in zip(
        config.rental_properties, previous_values, strict=True
    ):
        value, rent, purchased_this_year = _property_year_values(
            calendar_year=projection_year.calendar_year,
            property_config=property_config,
            previous_value=previous_value,
            start_year=config.assumptions.start_year,
            inflation_rate=config.assumptions.inflation_rate,
        )
        property_values.append(value)
        rental_income += rent
        if property_config.purchase_year <= projection_year.calendar_year:
            property_count += 1
        if purchased_this_year:
            purchase_outlay += property_config.purchase_price

    return property_values, rental_income, purchase_outlay, property_count


def _property_year_values(
    *,
    calendar_year: int,
    property_config: RentalPropertyConfig,
    previous_value: Decimal,
    start_year: int,
    inflation_rate: Decimal,
) -> tuple[Decimal, Decimal, bool]:
    """Return value, rent, and purchase status for one property in one year."""
    if property_config.purchase_year > calendar_year:
        return ZERO, ZERO, False

    if (
        property_config.purchase_year == calendar_year
        and property_config.purchase_year > start_year
    ):
        return property_config.purchase_price, property_config.annual_net_rent, True

    purchase_or_opening_year = max(property_config.purchase_year, start_year)
    years_since_opening = calendar_year - purchase_or_opening_year
    rent = property_config.annual_net_rent * (ONE + inflation_rate) ** years_since_opening

    if calendar_year == start_year and property_config.purchase_year <= start_year:
        return property_config.current_value, rent, False

    value = previous_value * (ONE + property_config.annual_growth_rate)
    return value, rent, False


def _purchase_names(calendar_year: int, config: WealthOsConfig) -> str:
    """Return quoted names of the properties scheduled for a calendar year."""
    names = [
        f"'{property_config.name}'"
        for property_config in config.rental_properties
        if property_config.purchase_year == calendar_year
    ]
    return ", ".join(names)

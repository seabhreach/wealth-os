"""Pension growth and contribution stage for the deterministic annual projection."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING

from engine.config.models import WealthOsConfig
from engine.simulation.owners import owner_age_in_year

if TYPE_CHECKING:
    from engine.simulation.projection import ProjectionYear


ZERO = Decimal("0")
ONE = Decimal("1")


@dataclass(frozen=True, slots=True)
class PensionBalance:
    """One pension's value in a projection year."""

    name: str
    owner: str
    value: Decimal
    withdrawal: Decimal = ZERO


def apply_pension_growth(
    timeline: tuple[ProjectionYear, ...], config: WealthOsConfig
) -> tuple[ProjectionYear, ...]:
    """Return a new timeline with pension growth, contributions, and net worth.

    The first row shows configured opening values. Later rows grow each pension, adding a
    contribution only while the household is below its configured retirement age.
    """
    previous_balances: tuple[PensionBalance, ...] = ()
    updated_timeline: list[ProjectionYear] = []

    for index, projection_year in enumerate(timeline):
        pension_balances = (
            _opening_balances(config)
            if index == 0
            else _grow_pensions(previous_balances, config, projection_year.calendar_year)
        )
        pension_value = sum((balance.value for balance in pension_balances), start=ZERO)
        net_worth = projection_year.net_worth - projection_year.pension_value + pension_value
        amazon_concentration = (
            projection_year.amazon_value / net_worth if net_worth != ZERO else ZERO
        )
        updated_timeline.append(
            replace(
                projection_year,
                pension_value=pension_value,
                pension_values=pension_balances,
                amazon_concentration=amazon_concentration,
                net_worth=net_worth,
            )
        )
        previous_balances = pension_balances

    return tuple(updated_timeline)


def _opening_balances(config: WealthOsConfig) -> tuple[PensionBalance, ...]:
    """Create opening-year pension balances without growth or contributions."""
    return tuple(
        PensionBalance(
            name=pension_config.name,
            owner=pension_config.owner,
            value=pension_config.current_value,
        )
        for pension_config in config.pensions
    )


def _grow_pensions(
    previous_balances: tuple[PensionBalance, ...], config: WealthOsConfig, calendar_year: int
) -> tuple[PensionBalance, ...]:
    """Grow previous balances and add contributions before the configured retirement age."""
    return tuple(
        PensionBalance(
            name=pension_config.name,
            owner=pension_config.owner,
            value=(
                previous_balance.value * (ONE + pension_config.annual_growth_rate)
                + (
                    pension_config.annual_contribution
                    if owner_age_in_year(config, pension_config.owner, calendar_year)
                    < (pension_config.access_age or config.household.planned_retirement_age)
                    else ZERO
                )
            ),
        )
        for previous_balance, pension_config in zip(previous_balances, config.pensions, strict=True)
    )

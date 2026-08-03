"""Cash contributions and ETF growth for the deterministic annual projection."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from engine.config.models import WealthOsConfig

if TYPE_CHECKING:
    from engine.simulation.projection import ProjectionYear


def apply_cash_and_etf_growth(
    projection_years: list[ProjectionYear], configuration: WealthOsConfig
) -> list[ProjectionYear]:
    """Return annual rows with cash contributions, ETF growth, and revised net worth.

    The input list and every input row remain unchanged. This stage intentionally does not
    implement RSU vesting, property appreciation, pension growth, or retirement withdrawals.
    """
    cash_balance = configuration.investments.cash_balance
    etf_value = configuration.investments.etf_value
    updated_years: list[ProjectionYear] = []

    for projection_year in projection_years:
        if projection_year.employed:
            cash_balance += configuration.employment.annual_savings

        etf_value *= Decimal("1") + configuration.investments.etf_growth_rate
        net_worth = (
            cash_balance
            + etf_value
            + projection_year.amazon_value
            + projection_year.pension_value
            + projection_year.property_value
        )
        updated_years.append(
            replace(
                projection_year,
                cash_balance=cash_balance,
                etf_value=etf_value,
                net_worth=net_worth,
            )
        )

    return updated_years

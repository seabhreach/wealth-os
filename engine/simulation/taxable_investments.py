"""Cash contributions and taxable-investment growth for the annual projection."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from engine.config.models import WealthOsConfig

if TYPE_CHECKING:
    from engine.simulation.projection import ProjectionYear


def apply_cash_and_taxable_investment_growth(
    projection_years: list[ProjectionYear], configuration: WealthOsConfig
) -> list[ProjectionYear]:
    """Apply cash contributions and one shared taxable-investment growth assumption.

    The aggregate opening value is always derived from canonical holdings. The shared rate is a
    current engine limitation and does not imply equal expected returns across asset types.
    """
    cash_balance = configuration.investments.cash_balance
    taxable_investment_value = configuration.investments.taxable_investment_value
    updated_years: list[ProjectionYear] = []

    for projection_year in projection_years:
        if projection_year.employed:
            cash_balance += configuration.employment.annual_savings

        taxable_investment_value *= (
            Decimal("1") + configuration.investments.taxable_investment_growth_rate
        )
        net_worth = (
            cash_balance
            + taxable_investment_value
            + projection_year.amazon_value
            + projection_year.pension_value
            + projection_year.property_value
        )
        updated_years.append(
            replace(
                projection_year,
                cash_balance=cash_balance,
                taxable_investment_value=taxable_investment_value,
                net_worth=net_worth,
            )
        )

    return updated_years

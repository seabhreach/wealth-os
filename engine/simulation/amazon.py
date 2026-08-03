"""Amazon RSU vesting and share-price growth for the annual projection."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from engine.config.models import WealthOsConfig

if TYPE_CHECKING:
    from engine.simulation.projection import ProjectionYear


ZERO = Decimal("0")
ONE = Decimal("1")


def apply_amazon_rsus(
    projection_years: tuple[ProjectionYear, ...], configuration: WealthOsConfig
) -> tuple[ProjectionYear, ...]:
    """Return new annual rows after simple RSU vesting and share-price growth.

    Newly vested shares are sold at the pre-growth share price when sell-on-vest is enabled.
    This stage does not model tax, vest cliffs, partial vesting, or capital gains.
    """
    share_price_usd = configuration.amazon_rsus.share_price_usd
    eur_usd_exchange_rate = configuration.amazon_rsus.eur_usd_exchange_rate
    share_count = configuration.amazon_rsus.vested_shares
    cumulative_sale_proceeds = ZERO
    updated_years: list[ProjectionYear] = []

    for projection_year in projection_years:
        if projection_year.employed:
            newly_vested_shares = configuration.amazon_rsus.annual_grant_shares
            if configuration.amazon_rsus.sell_on_vest:
                cumulative_sale_proceeds += (
                    newly_vested_shares * share_price_usd * eur_usd_exchange_rate
                )
            else:
                share_count += newly_vested_shares

        share_price_usd *= ONE + configuration.amazon_rsus.annual_growth_rate
        amazon_value = share_count * share_price_usd * eur_usd_exchange_rate
        cash_balance = projection_year.cash_balance + cumulative_sale_proceeds
        net_worth = (
            projection_year.net_worth
            - projection_year.amazon_value
            + amazon_value
            + cumulative_sale_proceeds
        )
        amazon_concentration = amazon_value / net_worth if net_worth != ZERO else ZERO
        updated_years.append(
            replace(
                projection_year,
                cash_balance=cash_balance,
                amazon_shares=share_count,
                amazon_value=amazon_value,
                amazon_concentration=amazon_concentration,
                net_worth=net_worth,
            )
        )

    return tuple(updated_years)

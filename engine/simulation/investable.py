"""Generic investable-asset and concentration calculations."""

from decimal import Decimal

ZERO = Decimal("0")


def investable_assets(
    cash: Decimal, taxable_investments: Decimal, direct_equity: Decimal
) -> Decimal:
    """Return the RFC-010 denominator, excluding pensions and real estate."""

    return cash + taxable_investments + direct_equity


def position_concentration(position_value: Decimal, denominator: Decimal) -> Decimal:
    """Return one direct-security position's share of investable assets."""

    return position_value / denominator if denominator != ZERO else ZERO

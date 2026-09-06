"""Compatibility alias for the former ETF-specific projection stage."""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.config.models import WealthOsConfig
from engine.simulation.taxable_investments import apply_cash_and_taxable_investment_growth

if TYPE_CHECKING:
    from engine.simulation.projection import ProjectionYear


def apply_cash_and_etf_growth(
    projection_years: list[ProjectionYear], configuration: WealthOsConfig
) -> list[ProjectionYear]:
    """Delegate legacy callers to the canonical taxable-investment stage."""
    return apply_cash_and_taxable_investment_growth(projection_years, configuration)

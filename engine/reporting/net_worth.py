"""Explicit household-position and planning-net-worth semantics."""

from dataclasses import dataclass
from decimal import Decimal

from engine.config.models import WealthOsConfig
from engine.simulation.projection import ProjectionYear

ZERO = Decimal("0")


@dataclass(frozen=True, slots=True)
class NetWorthSummary:
    """Keep inactive residence equity separate from active planning wealth."""

    planning_net_worth: Decimal
    primary_residence_equity: Decimal
    household_net_worth: Decimal


def summarize_net_worth(year: ProjectionYear, config: WealthOsConfig) -> NetWorthSummary:
    """Add residence equity only to household position, never to the projection."""

    residence_equity = config.primary_residence.equity if config.primary_residence else ZERO
    return NetWorthSummary(
        planning_net_worth=year.net_worth,
        primary_residence_equity=residence_equity,
        household_net_worth=year.net_worth + residence_equity,
    )

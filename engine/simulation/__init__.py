"""Simulation application boundary."""

from engine.simulation.amazon import apply_amazon_rsus
from engine.simulation.baseline import EmptySimulationResult, run_empty_simulation
from engine.simulation.cash_etf import apply_cash_and_etf_growth
from engine.simulation.pensions import PensionBalance, apply_pension_growth
from engine.simulation.projection import ProjectionYear, project_annually
from engine.simulation.properties import PropertySimulationError, apply_rental_properties
from engine.simulation.retirement import apply_retirement_withdrawals

__all__ = [
    "EmptySimulationResult",
    "PensionBalance",
    "ProjectionYear",
    "PropertySimulationError",
    "apply_amazon_rsus",
    "apply_cash_and_etf_growth",
    "apply_pension_growth",
    "apply_rental_properties",
    "apply_retirement_withdrawals",
    "project_annually",
    "run_empty_simulation",
]

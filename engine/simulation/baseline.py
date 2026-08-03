"""The runnable, calculation-free simulation boundary for Task 1."""

from dataclasses import dataclass

from engine.config.models import WealthOsConfig


@dataclass(frozen=True, slots=True)
class EmptySimulationResult:
    """Confirms that validated inputs have reached the simulation boundary."""

    household_name: str
    current_age: int
    planned_retirement_age: int
    life_expectancy: int
    rental_property_count: int


def run_empty_simulation(configuration: WealthOsConfig) -> EmptySimulationResult:
    """Return the Task 1 simulation baseline without financial calculations."""
    household = configuration.household
    return EmptySimulationResult(
        household_name=household.name,
        current_age=household.current_age,
        planned_retirement_age=household.planned_retirement_age,
        life_expectancy=household.life_expectancy,
        rental_property_count=len(configuration.rental_properties),
    )

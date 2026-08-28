"""Validated mappings from Workspace actions to existing scenario overrides."""

from __future__ import annotations

from engine.config import WealthOsConfig
from engine.reporting import ScenarioOverride
from experience.workspace_composition.models import SetScenarioValue


def supported_g001_retirement_ages(configuration: WealthOsConfig) -> tuple[int, ...]:
    """Return the bounded age set used by the visual G-001 prototype."""

    household = configuration.household
    lower = max(household.current_age, household.planned_retirement_age - 3)
    upper = min(household.life_expectancy, household.planned_retirement_age + 1)
    return tuple(range(lower, upper + 1))


def g001_scenario_override(
    configuration: WealthOsConfig,
    action: SetScenarioValue,
) -> ScenarioOverride:
    """Validate one retirement-age action and map it to the existing override API."""

    if action.control_id != "retirement_age":
        raise ValueError("G-001 supports only the retirement-age control.")
    allowed = supported_g001_retirement_ages(configuration)
    if action.value not in allowed:
        raise ValueError(
            "Retirement age must be within the validated projection horizon and G-001 range."
        )
    return ScenarioOverride(retirement_age=action.value)

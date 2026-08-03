"""Temporary retirement-age scenario helpers for the dashboard session."""

from engine.config.models import WealthOsConfig


def with_retirement_age(configuration: WealthOsConfig, retirement_age: int) -> WealthOsConfig:
    """Return an independently validated copy with only retirement age replaced."""
    configuration_data = configuration.model_dump(mode="python")
    household = configuration_data["household"]
    household["planned_retirement_age"] = retirement_age
    return WealthOsConfig.model_validate(configuration_data)


def what_if_label(configuration: WealthOsConfig, retirement_age: int) -> str | None:
    """Return a label only when a temporary retirement-age override is active."""
    baseline_age = configuration.household.planned_retirement_age
    if retirement_age == baseline_age:
        return None
    return f"What-if: retirement at age {retirement_age} instead of baseline age {baseline_age}"

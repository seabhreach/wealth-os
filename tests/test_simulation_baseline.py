"""Tests for the Task 1 empty simulation boundary."""

from pathlib import Path

from engine.config import load_configuration
from engine.simulation import run_empty_simulation


def test_empty_simulation_receives_validated_configuration() -> None:
    """The baseline returns identity details without calculating finances."""
    configuration = load_configuration(
        Path("data/example_household.yaml").read_text(encoding="utf-8")
    )

    result = run_empty_simulation(configuration)

    assert result.household_name.startswith("Illustrative Wealth OS household")
    assert result.current_age == 54
    assert result.rental_property_count == 1

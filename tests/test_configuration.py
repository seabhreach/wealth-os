"""Tests for the Task 1 YAML configuration pipeline."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from engine.config import ConfigurationError, load_configuration

EXAMPLE_CONFIGURATION = Path("data/example_household.yaml")


def test_example_configuration_loads() -> None:
    """The example YAML validates as a complete single-household configuration."""
    configuration = load_configuration(EXAMPLE_CONFIGURATION.read_text(encoding="utf-8"))

    assert configuration.household.current_age == 54
    assert configuration.household.spouse_age == 51
    assert configuration.employment.annual_savings == 20000
    assert configuration.assumptions.start_year == 2026
    assert len(configuration.rental_properties) == 1


def test_configuration_rejects_more_than_three_properties() -> None:
    """The MVP limits households to three rental properties."""
    yaml_text = EXAMPLE_CONFIGURATION.read_text(encoding="utf-8")
    property_section = yaml_text[
        yaml_text.index("rental_properties:") : yaml_text.index("assumptions:")
    ]
    yaml_text = yaml_text.replace(
        property_section,
        """rental_properties:
  - name: One
    purchase_year: 2026
    purchase_price: 1
    current_value: 1
    annual_net_rent: 1
    annual_growth_rate: 0
  - name: Two
    purchase_year: 2026
    purchase_price: 1
    current_value: 1
    annual_net_rent: 1
    annual_growth_rate: 0
  - name: Three
    purchase_year: 2026
    purchase_price: 1
    current_value: 1
    annual_net_rent: 1
    annual_growth_rate: 0
  - name: Four
    purchase_year: 2026
    purchase_price: 1
    current_value: 1
    annual_net_rent: 1
    annual_growth_rate: 0
""",
    )

    with pytest.raises(ValidationError):
        load_configuration(yaml_text)


def test_configuration_rejects_non_mapping_yaml() -> None:
    """The loader rejects YAML documents that cannot represent a configuration."""
    with pytest.raises(ConfigurationError, match="top-level mapping"):
        load_configuration("- not\n- a mapping\n")

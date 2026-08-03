"""YAML configuration loading for the Wealth OS MVP."""

from typing import Any

import yaml

from engine.config.models import WealthOsConfig


class ConfigurationError(ValueError):
    """Raised when a YAML document cannot be interpreted as a configuration mapping."""


def load_configuration(yaml_text: str) -> WealthOsConfig:
    """Parse and validate one household configuration from YAML text."""
    try:
        raw_configuration = yaml.safe_load(yaml_text)
    except yaml.YAMLError as error:
        raise ConfigurationError("Configuration is not valid YAML.") from error

    if not isinstance(raw_configuration, dict):
        raise ConfigurationError("Configuration must contain a top-level mapping.")

    return WealthOsConfig.model_validate(cast_configuration(raw_configuration))


def cast_configuration(value: dict[object, object]) -> dict[str, Any]:
    """Validate YAML mapping keys before Pydantic validates its values."""
    configuration: dict[str, Any] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise ConfigurationError("Configuration keys must be strings.")
        configuration[key] = item
    return configuration

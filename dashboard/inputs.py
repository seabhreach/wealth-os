"""Pure adapters between dashboard form data, validated configuration, and YAML."""

from copy import deepcopy
from decimal import Decimal
from typing import Any

import yaml
from pydantic import ValidationError

from engine.config.models import WealthOsConfig

FormData = dict[str, Any]


def configuration_to_form_data(configuration: WealthOsConfig) -> FormData:
    """Return mutable form defaults from the current immutable configuration."""
    data = deepcopy(configuration.model_dump(mode="python"))
    data["pensions"] = [dict(pension) for pension in data["pensions"]]
    data["rental_properties"] = [
        {
            **dict(property_input),
            "owners": [dict(owner) for owner in property_input.get("owners", ())],
        }
        for property_input in data["rental_properties"]
    ]
    return data


def form_data_to_configuration(form_data: FormData) -> WealthOsConfig:
    """Validate submitted form data using the existing configuration model."""
    return WealthOsConfig.model_validate(form_data)


def configuration_to_yaml(configuration: WealthOsConfig) -> str:
    """Serialize a configuration to loader-compatible reproducible YAML."""
    serializable_data = configuration.model_dump(mode="json")
    return yaml.safe_dump(serializable_data, allow_unicode=True, sort_keys=False)


def percentage_to_rate(percentage: int | float) -> Decimal:
    """Convert a user-entered percentage into the configured fractional rate."""
    return Decimal(str(percentage)) / Decimal("100")


def rate_to_percentage(rate: Decimal) -> float:
    """Convert a configured fractional rate into a user-facing percentage."""
    return float(rate * Decimal("100"))


def add_pension(form_data: FormData) -> FormData:
    """Return form data with one blank pension input appended."""
    updated_data = deepcopy(form_data)
    pensions = _list_section(updated_data, "pensions")
    pensions.append(
        {
            "name": "New pension",
            "owner": "Owner",
            "current_value": Decimal("0"),
            "annual_growth_rate": Decimal("0.04"),
            "annual_contribution": Decimal("0"),
        }
    )
    return updated_data


def remove_pension(form_data: FormData, index: int) -> FormData:
    """Return form data with one pension removed while retaining the required minimum."""
    updated_data = deepcopy(form_data)
    pensions = _list_section(updated_data, "pensions")
    if len(pensions) <= 1:
        return updated_data
    pensions.pop(index)
    return updated_data


def add_rental_property(form_data: FormData) -> FormData:
    """Return form data with one blank rental-property input appended."""
    updated_data = deepcopy(form_data)
    properties = _list_section(updated_data, "rental_properties")
    assumptions = updated_data["assumptions"]
    if not isinstance(assumptions, dict):
        raise TypeError("assumptions must be a mapping in dashboard form data")
    properties.append(
        {
            "name": "New rental property",
            "purchase_year": int(assumptions["start_year"]),
            "purchase_price": Decimal("0"),
            "current_value": Decimal("0"),
            "annual_net_rent": Decimal("0"),
            "annual_growth_rate": Decimal("0.03"),
        }
    )
    return updated_data


def remove_rental_property(form_data: FormData, index: int) -> FormData:
    """Return form data with one rental property removed."""
    updated_data = deepcopy(form_data)
    properties = _list_section(updated_data, "rental_properties")
    properties.pop(index)
    return updated_data


def validation_error_messages(error: ValidationError) -> dict[str, str]:
    """Map Pydantic validation locations to concise dashboard field messages."""
    return {
        ".".join(str(location) for location in issue["loc"]): issue["msg"]
        for issue in error.errors()
    }


def _list_section(form_data: FormData, section: str) -> list[FormData]:
    """Return a mutable configuration list section with a narrow runtime check."""
    values = form_data[section]
    if not isinstance(values, list):
        raise TypeError(f"{section} must be a list in dashboard form data")
    return values

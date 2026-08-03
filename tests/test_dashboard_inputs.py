"""Tests for dashboard input adapters and responsive presentation settings."""

from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from dashboard.components.charts import key_dates_figure, net_worth_figure, spending_funding_figure
from dashboard.inputs import (
    add_pension,
    add_rental_property,
    configuration_to_form_data,
    configuration_to_yaml,
    form_data_to_configuration,
    percentage_to_rate,
    rate_to_percentage,
    remove_pension,
    remove_rental_property,
    validation_error_messages,
)
from engine.config import load_configuration
from engine.simulation import project_annually


def _configuration_text() -> str:
    """Return the documented baseline YAML."""
    return Path("data/example_household.yaml").read_text(encoding="utf-8")


def test_configuration_and_form_data_round_trip() -> None:
    """The structured form preserves all existing validated input values."""
    configuration = load_configuration(_configuration_text())

    rebuilt = form_data_to_configuration(configuration_to_form_data(configuration))

    assert rebuilt == configuration


def test_yaml_export_round_trip_is_loader_compatible() -> None:
    """Downloaded YAML can be loaded again into the exact same configuration."""
    configuration = load_configuration(_configuration_text())

    assert load_configuration(configuration_to_yaml(configuration)) == configuration


def test_percentage_controls_convert_between_human_and_model_values() -> None:
    """Form percentages map precisely to fractional configuration rates."""
    assert percentage_to_rate(6.5) == Decimal("0.065")
    assert rate_to_percentage(Decimal("0.065")) == 6.5


def test_pensions_and_properties_can_be_added_and_removed() -> None:
    """Collection controls change only dashboard form data and respect pension minimums."""
    form_data = configuration_to_form_data(load_configuration(_configuration_text()))

    with_added_pension = add_pension(form_data)
    with_added_property = add_rental_property(form_data)

    assert len(with_added_pension["pensions"]) == 3
    assert len(remove_pension(with_added_pension, 2)["pensions"]) == 2
    one_pension = remove_pension(form_data, 0)
    assert len(one_pension["pensions"]) == 1
    assert len(remove_pension(one_pension, 0)["pensions"]) == 1
    assert len(with_added_property["rental_properties"]) == 2
    assert len(remove_rental_property(with_added_property, 1)["rental_properties"]) == 1


def test_validation_errors_are_mapped_from_existing_model_validation() -> None:
    """Dashboard errors come from the existing Pydantic configuration model."""
    form_data = configuration_to_form_data(load_configuration(_configuration_text()))
    form_data["household"]["planned_retirement_age"] = 40

    with pytest.raises(ValidationError) as error_info:
        form_data_to_configuration(form_data)

    errors = validation_error_messages(error_info.value)
    assert "household" in errors


def test_responsive_chart_builders_enable_autosize_and_compact_layout() -> None:
    """Charts leave width to their container and keep legends below the plotting area."""
    projection = project_annually(load_configuration(_configuration_text()))
    retirement_year = next(year for year in projection if not year.employed)
    net_worth = net_worth_figure(projection, retirement_year.calendar_year)
    key_dates = key_dates_figure(projection[0], retirement_year, projection[-1])
    funding = spending_funding_figure(projection)

    assert net_worth.layout.autosize is True
    assert net_worth.layout.height == 360
    assert net_worth.layout.legend.orientation == "h"
    assert len(key_dates.data) == 3
    assert len(funding.data) == 7

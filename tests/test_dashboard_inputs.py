"""Tests for dashboard input adapters and responsive presentation settings."""

from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from dashboard.components.charts import key_dates_figure, net_worth_figure, spending_funding_figure
from dashboard.inputs import (
    add_investment_holding,
    add_pension,
    add_rental_property,
    configuration_to_form_data,
    configuration_to_yaml,
    form_data_to_configuration,
    percentage_to_rate,
    rate_to_percentage,
    remove_investment_holding,
    remove_pension,
    remove_rental_property,
    update_investment_holding,
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


def test_zero_one_and_multiple_investment_holdings_are_valid() -> None:
    """The canonical form adapter accepts every supported collection cardinality."""
    form_data = configuration_to_form_data(load_configuration(_configuration_text()))
    assert len(form_data_to_configuration(form_data).investments.holdings) == 1

    no_holdings = configuration_to_form_data(load_configuration(_configuration_text()))
    no_holdings["investments"]["holdings"] = []
    assert form_data_to_configuration(no_holdings).investments.holdings == ()

    with_added = add_investment_holding(form_data)
    new_holding = with_added["investments"]["holdings"][1]
    new_holding.update(
        {
            "name": "Gold",
            "asset_type": "COMMODITY",
            "current_value": Decimal("5000"),
            "security_identifier": "XAU",
        }
    )

    rebuilt = form_data_to_configuration(with_added)

    assert len(rebuilt.investments.holdings) == 2
    assert "etf_value" not in rebuilt.investments.model_dump()
    assert rebuilt.investments.holdings[1].name == "Gold"
    assert rebuilt.investments.holdings[1].asset_type.value == "COMMODITY"
    assert rebuilt.investments.holdings[1].security_identifier == "XAU"
    assert rebuilt.investments.taxable_investment_value == Decimal("305000")


def test_multiple_same_and_different_investment_types_are_independent() -> None:
    """Repeated categories and distinct categories remain separate canonical records."""
    original = configuration_to_form_data(load_configuration(_configuration_text()))
    first_added = add_investment_holding(original)
    first_added["investments"]["holdings"][1].update(
        {"name": "Second ETF", "asset_type": "ETF", "current_value": Decimal("25000")}
    )
    second_added = add_investment_holding(first_added)
    second_added["investments"]["holdings"][2].update(
        {"name": "Bitcoin", "asset_type": "CRYPTOASSET", "current_value": Decimal("10000")}
    )

    holdings = form_data_to_configuration(second_added).investments.holdings
    holding_ids = [holding.holding_id for holding in holdings]

    assert holding_ids[0] == "existing-etf"
    assert all(holding_id.startswith("investment-") for holding_id in holding_ids[1:])
    assert len(set(holding_ids)) == 3
    assert [holding.asset_type.value for holding in holdings] == ["ETF", "ETF", "CRYPTOASSET"]
    assert sum((holding.current_value for holding in holdings), Decimal("0")) == Decimal("335000")


def test_add_second_and_third_holdings_preserves_existing_records_and_totals() -> None:
    """Complete add drafts append rather than replacing any canonical holding."""
    original = configuration_to_form_data(load_configuration(_configuration_text()))

    with_bitcoin = add_investment_holding(
        original,
        {
            "name": "Bitcoin",
            "asset_type": "CRYPTOASSET",
            "current_value": Decimal("50000"),
        },
    )
    with_gold = add_investment_holding(
        with_bitcoin,
        {
            "name": "Gold",
            "asset_type": "COMMODITY",
            "current_value": Decimal("25000"),
        },
    )

    bitcoin_config = form_data_to_configuration(with_bitcoin)
    gold_config = form_data_to_configuration(with_gold)
    assert len(bitcoin_config.investments.holdings) == 2
    assert bitcoin_config.investments.holdings[0].holding_id == "existing-etf"
    assert bitcoin_config.investments.holdings[0].current_value == Decimal("300000")
    assert bitcoin_config.investments.holdings[1].name == "Bitcoin"
    assert len({holding.holding_id for holding in bitcoin_config.investments.holdings}) == 2
    assert bitcoin_config.investments.taxable_investment_value == Decimal("350000")
    assert [holding.name for holding in gold_config.investments.holdings] == [
        "Existing ETF holding",
        "Bitcoin",
        "Gold",
    ]
    assert gold_config.investments.taxable_investment_value == Decimal("375000")


def test_edit_by_stable_id_replaces_only_the_selected_holding() -> None:
    """Immutable replacements retain identity, siblings, count, and derived totals."""
    original = configuration_to_form_data(load_configuration(_configuration_text()))
    with_bitcoin = add_investment_holding(
        original,
        {"name": "Bitcoin", "asset_type": "CRYPTOASSET", "current_value": 50_000},
    )
    bitcoin_id = str(with_bitcoin["investments"]["holdings"][1]["holding_id"])

    bitcoin_edited = update_investment_holding(
        with_bitcoin,
        bitcoin_id,
        {"name": "Bitcoin", "asset_type": "CRYPTOASSET", "current_value": 60_000},
    )
    etf_edited = update_investment_holding(
        bitcoin_edited,
        "existing-etf",
        {"name": "Existing ETF holding", "asset_type": "ETF", "current_value": 320_000},
    )

    bitcoin_config = form_data_to_configuration(bitcoin_edited)
    final_config = form_data_to_configuration(etf_edited)
    assert [holding.current_value for holding in bitcoin_config.investments.holdings] == [
        Decimal("300000"),
        Decimal("60000"),
    ]
    assert bitcoin_config.investments.holdings[1].holding_id == bitcoin_id
    assert [holding.holding_id for holding in final_config.investments.holdings] == [
        "existing-etf",
        bitcoin_id,
    ]
    assert [holding.current_value for holding in final_config.investments.holdings] == [
        Decimal("320000"),
        Decimal("60000"),
    ]
    assert final_config.investments.taxable_investment_value == Decimal("380000")


def test_duplicate_names_are_edited_and_removed_only_by_stable_id() -> None:
    """Display-name collisions never participate in update or removal identity."""
    original = configuration_to_form_data(load_configuration(_configuration_text()))
    first = add_investment_holding(
        original,
        {"name": "Same name", "asset_type": "BOND", "current_value": 10_000},
    )
    second = add_investment_holding(
        first,
        {"name": "Same name", "asset_type": "COMMODITY", "current_value": 20_000},
    )
    first_id = str(second["investments"]["holdings"][1]["holding_id"])
    second_id = str(second["investments"]["holdings"][2]["holding_id"])

    edited = update_investment_holding(
        second,
        second_id,
        {"name": "Same name", "asset_type": "COMMODITY", "current_value": 25_000},
    )
    remaining = remove_investment_holding(edited, first_id)
    holdings = form_data_to_configuration(remaining).investments.holdings

    assert [holding.holding_id for holding in holdings] == ["existing-etf", second_id]
    assert holdings[1].name == "Same name"
    assert holdings[1].current_value == Decimal("25000")


def test_add_edit_and_remove_preserve_other_holdings_and_stable_ids() -> None:
    """Collection actions affect only the identified record and never overwrite siblings."""
    original = configuration_to_form_data(load_configuration(_configuration_text()))
    with_two_added = add_investment_holding(add_investment_holding(original))
    holdings = with_two_added["investments"]["holdings"]
    holdings[1].update(
        {"name": "Shares", "asset_type": "INDIVIDUAL_EQUITY", "current_value": Decimal("12000")}
    )
    holdings[2].update({"name": "Bond", "asset_type": "BOND", "current_value": Decimal("8000")})
    removed_holding_id = str(holdings[1]["holding_id"])
    retained_holding_id = str(holdings[2]["holding_id"])
    untouched_before_edit = dict(holdings[0])
    third_before_edit = dict(holdings[2])

    holdings[1]["current_value"] = Decimal("15000")
    assert holdings[0] == untouched_before_edit
    assert holdings[2] == third_before_edit

    without_middle = remove_investment_holding(with_two_added, removed_holding_id)
    remaining = without_middle["investments"]["holdings"]

    assert [holding["holding_id"] for holding in remaining] == [
        "existing-etf",
        retained_holding_id,
    ]
    assert remaining[0] == untouched_before_edit
    assert remaining[1] == third_before_edit
    assert original["investments"]["holdings"] == [untouched_before_edit]

    replacement = add_investment_holding(without_middle)["investments"]["holdings"][-1]
    assert replacement["holding_id"] != removed_holding_id


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

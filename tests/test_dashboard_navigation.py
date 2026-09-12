"""Tests for deferred top-level dashboard navigation and input-page status helpers."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from dashboard.inputs import configuration_to_form_data, form_data_to_configuration
from dashboard.navigation import (
    PAGES,
    apply_pending_page,
    configuration_status,
    current_page,
    request_page,
)
from dashboard.state import (
    PAGE_KEY,
    PENDING_PAGE_KEY,
    active_configuration,
    initialise_state,
    replace_configuration,
    set_what_if_retirement_age,
    what_if_retirement_age,
)
from engine.config import load_configuration
from engine.config.models import WealthOsConfig


def test_requested_page_is_deferred_until_the_next_run() -> None:
    """Programmatic navigation never mutates the widget-owned page key immediately."""
    state: dict[str, object] = {}

    assert current_page(state) == "Overview"
    request_page(state, "Inputs")

    assert PAGE_KEY not in state
    assert state[PENDING_PAGE_KEY] == "Inputs"
    assert apply_pending_page(state) == "Inputs"
    assert state[PAGE_KEY] == "Inputs"
    assert PENDING_PAGE_KEY not in state
    assert PAGES[-1] == "Inputs"


def test_navigation_recovers_from_an_unknown_saved_page() -> None:
    """An invalid session value cannot route the dashboard to an unsupported page."""
    assert current_page({PAGE_KEY: "Unsupported"}) == "Overview"


def test_invalid_requested_page_is_rejected() -> None:
    """Only the declared navigation pages can be queued for a rerun."""
    with pytest.raises(ValueError, match="Unsupported Wealth OS page"):
        request_page({}, "Unsupported")  # type: ignore[arg-type]


def test_repeated_requests_replace_the_previous_pending_destination() -> None:
    """A later action can safely supersede an earlier redirect before the rerun."""
    state: dict[str, object] = {PAGE_KEY: "Inputs"}

    request_page(state, "Overview")
    request_page(state, "Details")

    assert apply_pending_page(state) == "Details"
    assert PENDING_PAGE_KEY not in state


def test_submitted_configuration_and_what_if_state_survive_deferred_navigation() -> None:
    """Saving inputs queues Overview without losing validated or session-only state."""
    baseline = _configuration()
    state: dict[str, object] = {}
    initialise_state(state, baseline, "Baseline")
    form_data = configuration_to_form_data(baseline)
    form_data["pensions"][0]["annual_contribution"] = 12_000.0
    submitted = form_data_to_configuration(form_data)
    set_what_if_retirement_age(state, 54)

    replace_configuration(state, submitted, "Structured form inputs")
    set_what_if_retirement_age(state, 54)
    request_page(state, "Overview")
    apply_pending_page(state)

    assert active_configuration(state) == submitted
    assert active_configuration(state).pensions[0].annual_contribution == 12_000
    assert what_if_retirement_age(state, submitted) == 54
    assert current_page(state) == "Overview"


def test_changed_pension_contribution_submits_without_a_navigation_exception() -> None:
    """Inputs submission reruns onto Overview through pending navigation without an exception."""
    app_path = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"
    app = AppTest.from_file(str(app_path))
    app.run(timeout=30)
    app.radio[0].set_value("Inputs").run(timeout=30)
    contribution = next(
        input_field
        for input_field in app.number_input
        if input_field.key == "pension_contribution_1"
    )

    contribution.set_value(12_000.0)
    next(button for button in app.button if button.label == "Run projection").click().run(
        timeout=30
    )

    assert not app.exception
    assert app.radio[0].value == "Overview"
    configuration = app.session_state["wealth_os_configuration"]
    assert isinstance(configuration, WealthOsConfig)
    assert configuration.pensions[0].annual_contribution == 12_000
    assert PENDING_PAGE_KEY not in app.session_state


def test_repeatable_investment_editor_preserves_current_edits_through_collection_actions() -> None:
    """Add and remove submissions retain sibling values by stable holding identity."""
    app_path = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"
    app = AppTest.from_file(str(app_path)).run(timeout=30)
    app.radio[0].set_value("Inputs").run(timeout=30)

    next(
        field for field in app.number_input if field.key == "investment_value_existing-etf"
    ).set_value(310_000.0)
    next(button for button in app.button if button.label == "Add investment").click().run(
        timeout=30
    )
    first_added_name = next(
        field
        for field in app.text_input
        if str(field.key).startswith("investment_name_investment-")
    )
    first_added_id = str(first_added_name.key).removeprefix("investment_name_")

    first_added_name.set_value("Individual shares")
    next(
        field for field in app.selectbox if field.key == f"investment_type_{first_added_id}"
    ).set_value("Individual shares")
    next(
        field for field in app.number_input if field.key == f"investment_value_{first_added_id}"
    ).set_value(20_000.0)
    next(button for button in app.button if button.label == "Add investment").click().run(
        timeout=30
    )
    second_added_name = next(
        field
        for field in app.text_input
        if str(field.key).startswith("investment_name_investment-")
        and field.key != f"investment_name_{first_added_id}"
    )
    second_added_id = str(second_added_name.key).removeprefix("investment_name_")

    second_added_name.set_value("Crypto holding")
    next(
        field for field in app.selectbox if field.key == f"investment_type_{second_added_id}"
    ).set_value("Cryptoassets")
    next(
        field for field in app.number_input if field.key == f"investment_value_{second_added_id}"
    ).set_value(5_000.0)
    next(
        field for field in app.number_input if field.key == f"investment_value_{first_added_id}"
    ).set_value(25_000.0)
    next(
        button for button in app.button if button.key == f"remove_investment_{second_added_id}"
    ).click().run(timeout=30)

    next(button for button in app.button if button.label == "Run projection").click().run(
        timeout=30
    )

    assert not app.exception
    configuration = app.session_state["wealth_os_configuration"]
    assert isinstance(configuration, WealthOsConfig)
    assert [holding.holding_id for holding in configuration.investments.holdings] == [
        "existing-etf",
        first_added_id,
    ]
    assert [holding.name for holding in configuration.investments.holdings] == [
        "Existing ETF holding",
        "Individual shares",
    ]
    assert [holding.current_value for holding in configuration.investments.holdings] == [
        310_000,
        25_000,
    ]
    assert configuration.investments.holdings[1].asset_type.value == "INDIVIDUAL_EQUITY"


def test_investment_add_edit_remove_survives_navigation_and_rerun() -> None:
    """Dedicated add drafts and stable holding cards persist through the full UI lifecycle."""
    app_path = Path(__file__).resolve().parents[1] / "dashboard" / "app.py"
    app = AppTest.from_file(str(app_path)).run(timeout=30)
    app.radio[0].set_value("Inputs").run(timeout=30)

    add_widget_keys = {
        str(field.key)
        for fields in (app.text_input, app.selectbox, app.number_input)
        for field in fields
        if str(field.key).startswith("investment_add_")
    }
    existing_widget_keys = {
        str(field.key)
        for fields in (app.text_input, app.selectbox, app.number_input)
        for field in fields
        if str(field.key).startswith("investment_") and "existing-etf" in str(field.key)
    }
    assert add_widget_keys.isdisjoint(existing_widget_keys)

    first_draft_name = next(field for field in app.text_input if field.key == "investment_add_name")
    first_draft_name.set_value("Bitcoin")
    next(field for field in app.selectbox if field.key == "investment_add_type").set_value(
        "Cryptoassets"
    )
    next(field for field in app.number_input if field.key == "investment_add_value").set_value(
        50_000.0
    )
    next(button for button in app.button if button.label == "Add investment").click().run(
        timeout=30
    )
    bitcoin_name = next(
        field
        for field in app.text_input
        if field.value == "Bitcoin" and str(field.key).startswith("investment_name_")
    )
    bitcoin_id = str(bitcoin_name.key).removeprefix("investment_name_")
    second_draft_name = next(
        field for field in app.text_input if field.key == "investment_add_name"
    )
    assert second_draft_name.key == first_draft_name.key
    assert second_draft_name.value == ""
    assert (
        len([field for field in app.text_input if str(field.key).startswith("investment_name_")])
        == 2
    )

    second_draft_name.set_value("Gold")
    next(field for field in app.selectbox if field.key == "investment_add_type").set_value(
        "Commodities"
    )
    next(field for field in app.number_input if field.key == "investment_add_value").set_value(
        25_000.0
    )
    next(button for button in app.button if button.label == "Add investment").click().run(
        timeout=30
    )
    gold_name = next(
        field
        for field in app.text_input
        if field.value == "Gold" and str(field.key).startswith("investment_name_")
    )
    gold_id = str(gold_name.key).removeprefix("investment_name_")
    assert (
        len([field for field in app.text_input if str(field.key).startswith("investment_name_")])
        == 3
    )

    next(
        field for field in app.number_input if field.key == f"investment_value_{bitcoin_id}"
    ).set_value(60_000.0)
    next(button for button in app.button if button.label == "Run projection").click().run(
        timeout=30
    )
    app.radio[0].set_value("Inputs").run(timeout=30)
    next(
        field for field in app.number_input if field.key == "investment_value_existing-etf"
    ).set_value(320_000.0)
    next(button for button in app.button if button.label == "Run projection").click().run(
        timeout=30
    )
    app.radio[0].set_value("Inputs").run(timeout=30)

    next(
        button for button in app.button if button.key == f"remove_investment_{gold_id}"
    ).click().run(timeout=30)
    next(button for button in app.button if button.label == "Run projection").click().run(
        timeout=30
    )
    app.radio[0].set_value("Inputs").run(timeout=30)
    app.run(timeout=30)

    assert not app.exception
    configuration = app.session_state["wealth_os_configuration"]
    assert isinstance(configuration, WealthOsConfig)
    assert [holding.holding_id for holding in configuration.investments.holdings] == [
        "existing-etf",
        bitcoin_id,
    ]
    assert [holding.name for holding in configuration.investments.holdings] == [
        "Existing ETF holding",
        "Bitcoin",
    ]
    assert [holding.current_value for holding in configuration.investments.holdings] == [
        320_000,
        60_000,
    ]
    assert configuration.investments.taxable_investment_value == 380_000
    assert all(gold_id not in str(field.key) for field in app.text_input)


def _configuration() -> WealthOsConfig:
    """Return the repository's validated baseline household configuration."""
    contents = Path("data/example_household.yaml").read_text(encoding="utf-8")
    return load_configuration(contents)


def test_configuration_status_is_compact_and_source_specific() -> None:
    """Inputs page presents validation without a persistent dashboard banner."""
    assert configuration_status("Illustrative scenario") == (
        "Validated configuration · Illustrative scenario"
    )

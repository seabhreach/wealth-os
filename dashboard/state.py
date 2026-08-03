"""Session-state helpers for the dashboard's non-persistent input workflow."""

from collections.abc import MutableMapping

from dashboard.inputs import FormData, configuration_to_form_data
from engine.config.models import WealthOsConfig

CONFIGURATION_KEY = "wealth_os_configuration"
FORM_DATA_KEY = "wealth_os_form_data"
SOURCE_KEY = "wealth_os_configuration_source"
PAGE_KEY = "wealth_os_page"
PENDING_PAGE_KEY = "wealth_os_pending_page"
WHAT_IF_RETIREMENT_AGE_KEY = "wealth_os_what_if_retirement_age"


def initialise_state(
    state: MutableMapping[str, object], default_configuration: WealthOsConfig, source: str
) -> None:
    """Create the session-only configuration state on the first dashboard render."""
    if CONFIGURATION_KEY not in state:
        replace_configuration(state, default_configuration, source)
    if PAGE_KEY not in state:
        state[PAGE_KEY] = "Overview"
    if WHAT_IF_RETIREMENT_AGE_KEY not in state:
        state[WHAT_IF_RETIREMENT_AGE_KEY] = default_configuration.household.planned_retirement_age


def replace_configuration(
    state: MutableMapping[str, object], configuration: WealthOsConfig, source: str
) -> None:
    """Replace the active configuration and reset form defaults from its validated values."""
    state[CONFIGURATION_KEY] = configuration
    state[FORM_DATA_KEY] = configuration_to_form_data(configuration)
    state[SOURCE_KEY] = source
    state[WHAT_IF_RETIREMENT_AGE_KEY] = configuration.household.planned_retirement_age


def active_configuration(state: MutableMapping[str, object]) -> WealthOsConfig:
    """Return the active validated configuration with a narrow runtime type check."""
    configuration = state[CONFIGURATION_KEY]
    if not isinstance(configuration, WealthOsConfig):
        raise TypeError("dashboard configuration state must contain WealthOsConfig")
    return configuration


def active_form_data(state: MutableMapping[str, object]) -> FormData:
    """Return the active mutable form defaults with a narrow runtime type check."""
    form_data = state[FORM_DATA_KEY]
    if not isinstance(form_data, dict):
        raise TypeError("dashboard form state must contain a mapping")
    return form_data


def configuration_source(state: MutableMapping[str, object]) -> str:
    """Return the human-readable source of the active session configuration."""
    source = state[SOURCE_KEY]
    if not isinstance(source, str):
        raise TypeError("dashboard configuration source must be text")
    return source


def what_if_retirement_age(
    state: MutableMapping[str, object], configuration: WealthOsConfig
) -> int:
    """Return the session-only retirement-age override, defaulting to the saved baseline."""
    age = state.get(WHAT_IF_RETIREMENT_AGE_KEY, configuration.household.planned_retirement_age)
    if not isinstance(age, int):
        raise TypeError("dashboard retirement-age what-if must be an integer")
    return age


def set_what_if_retirement_age(state: MutableMapping[str, object], retirement_age: int) -> None:
    """Persist a temporary retirement-age override for the current dashboard session."""
    state[WHAT_IF_RETIREMENT_AGE_KEY] = retirement_age


def reset_what_if_retirement_age(
    state: MutableMapping[str, object], configuration: WealthOsConfig
) -> None:
    """Reset the session-only what-if to the configuration's saved baseline age."""
    set_what_if_retirement_age(state, configuration.household.planned_retirement_age)

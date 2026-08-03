"""Top-level dashboard navigation state and presentation helpers."""

from collections.abc import MutableMapping
from typing import Literal

from dashboard.state import PAGE_KEY, PENDING_PAGE_KEY

PageName = Literal["Overview", "Retirement", "Assets", "Cashflow", "Details", "Advisor", "Inputs"]
PAGES: tuple[PageName, ...] = (
    "Overview",
    "Retirement",
    "Assets",
    "Cashflow",
    "Details",
    "Advisor",
    "Inputs",
)


def current_page(state: MutableMapping[str, object]) -> PageName:
    """Return the current page, falling back safely to the Overview."""
    page = state.get(PAGE_KEY, "Overview")
    return _validated_page(page, fallback="Overview")


def request_page(state: MutableMapping[str, object], page: PageName) -> None:
    """Request navigation for the next rerun without touching the widget-owned key."""
    state[PENDING_PAGE_KEY] = _validated_page(page)


def apply_pending_page(state: MutableMapping[str, object]) -> PageName:
    """Apply and clear a requested page before the navigation widget is rendered."""
    pending_page = state.pop(PENDING_PAGE_KEY, None)
    if pending_page is not None:
        state[PAGE_KEY] = _validated_page(pending_page)
    return current_page(state)


def _validated_page(page: object, fallback: PageName | None = None) -> PageName:
    """Return a supported page or raise for an invalid requested navigation target."""
    if isinstance(page, str) and page in PAGES:
        return page
    if fallback is not None:
        return fallback
    raise ValueError(f"Unsupported Wealth OS page: {page!r}")


def active_page(state: MutableMapping[str, object]) -> PageName:
    """Return the current page for compatibility with existing dashboard callers."""
    return current_page(state)


def configuration_status(source: str) -> str:
    """Return the concise input-page status line for a validated configuration."""
    return f"Validated configuration · {source}"

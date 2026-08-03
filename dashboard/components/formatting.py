"""Formatting helpers for Wealth OS dashboard presentation."""

from collections.abc import Iterable
from decimal import ROUND_HALF_EVEN, Decimal
from typing import Literal

Number = Decimal | float | int
StatusTone = Literal["success", "warning", "error"]


def format_eur(value: Number) -> str:
    """Format a EUR amount without unnecessary cents."""
    numeric_value = display_eur_value(value)
    prefix = "-" if numeric_value < 0 else ""
    return f"{prefix}€{abs(numeric_value):,.0f}"


def format_eur_cents(value: Number) -> str:
    """Format a detailed EUR amount to two places without exposing Decimal tails."""
    numeric_value = Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
    prefix = "-" if numeric_value < 0 else ""
    return f"{prefix}€{abs(numeric_value):,.2f}"


def display_eur_value(value: Number) -> Decimal:
    """Round one EUR amount using the dashboard's consistent whole-euro display policy."""
    return display_whole_value(value)


def display_whole_value(value: Number) -> Decimal:
    """Round a displayed whole-unit quantity with the dashboard's common policy."""
    return Decimal(value).quantize(Decimal("1"), rounding=ROUND_HALF_EVEN)


def display_reconciliation_adjustment(
    closing: Number, additions: Iterable[Number], subtractions: Iterable[Number] = ()
) -> Decimal:
    """Return the visible whole-euro adjustment required for an exact displayed equation."""
    displayed_balance = display_eur_value(closing)
    displayed_movements = sum((display_eur_value(value) for value in additions), start=Decimal("0"))
    displayed_movements -= sum(
        (display_eur_value(value) for value in subtractions), start=Decimal("0")
    )
    return displayed_balance - displayed_movements


def format_compact_eur(value: Number) -> str:
    """Format a EUR amount compactly for KPI cards."""
    numeric_value = Decimal(value)
    prefix = "-" if numeric_value < 0 else ""
    absolute_value = abs(numeric_value)
    if absolute_value >= Decimal("1000000"):
        return f"{prefix}€{absolute_value / Decimal('1000000'):.2f}m"
    if absolute_value >= Decimal("1000"):
        return f"{prefix}€{absolute_value / Decimal('1000'):.0f}k"
    return f"{prefix}€{absolute_value:,.0f}"


def format_usd(value: Number) -> str:
    """Format a USD amount without unnecessary cents."""
    numeric_value = Decimal(value)
    prefix = "-" if numeric_value < 0 else ""
    return f"{prefix}${abs(numeric_value):,.0f}"


def format_percentage(value: Number) -> str:
    """Format a fractional value as a percentage with one decimal place."""
    return f"{Decimal(value) * Decimal('100'):.1f}%"


def format_shares(value: Number) -> str:
    """Format a whole share count."""
    return f"{Decimal(value):,.0f}"


def format_year_and_age(year: int, age: int) -> str:
    """Format a projection point consistently."""
    return f"{year} (age {age})"


def readiness_status(retirement_ready: bool) -> tuple[str, StatusTone]:
    """Return a concise display label and visual tone for readiness."""
    if retirement_ready:
        return "Retirement ready", "success"
    return "Funding gap", "error"

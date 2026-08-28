"""Customer-facing formatting at the Experience presentation boundary."""

from __future__ import annotations

from decimal import Decimal


def format_display_value(
    value: Decimal | int | str | bool | None,
    unit: str = "",
) -> str:
    """Format exact evidence without changing the underlying value."""

    if value is None:
        return "None"
    if isinstance(value, bool):
        return "Enabled" if value else "Disabled"
    if isinstance(value, Decimal):
        if unit == "ratio":
            return f"{value:.1%}"
        if unit.startswith("EUR"):
            suffix = "/year" if unit.endswith("/year") else ""
            return f"€{value:,.0f}{suffix}"
        return _compact_decimal(value)
    if isinstance(value, int) and unit.startswith("EUR"):
        suffix = "/year" if unit.endswith("/year") else ""
        return f"€{value:,.0f}{suffix}"
    if isinstance(value, int) and unit.startswith("years"):
        return f"{value} years"
    return str(value)


def format_compact_currency(value: Decimal | int) -> str:
    """Format a monetary evidence value compactly without changing its value."""

    decimal_value = Decimal(value)
    absolute = abs(decimal_value)
    if absolute >= Decimal("1000000"):
        return f"€{decimal_value / Decimal('1000000'):.2f}m"
    if absolute >= Decimal("1000"):
        return f"€{decimal_value / Decimal('1000'):.0f}k"
    return f"€{decimal_value:,.0f}"


def format_table_value(
    value: Decimal | int | str | bool | None,
    column: str,
    row_label: str = "",
) -> str:
    """Format table evidence using its declared customer-facing column."""

    if isinstance(value, Decimal) and _is_eur_column(column, row_label):
        return format_display_value(value, "EUR")
    return format_display_value(value)


def _compact_decimal(value: Decimal) -> str:
    rendered = f"{value:,.2f}"
    return rendered.rstrip("0").rstrip(".")


def _is_eur_column(column: str, row_label: str) -> bool:
    normalized = column.casefold()
    normalized_label = row_label.casefold()
    if "units" in normalized_label or "shares" in normalized_label:
        return False
    return any(
        term in normalized
        for term in ("price", "rent", "value", "modelled value", "reporting value")
    )

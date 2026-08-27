"""Stable contextual Streamlit widget keys for the Experience."""

from __future__ import annotations

import re


def widget_key(role: str, *context: str | int | None) -> str:
    """Return a deterministic key whose identity is not display text alone."""

    parts = (role, *(str(item) for item in context if item is not None))
    normalized = tuple(_normalize(part) for part in parts)
    return f"wos-{'-'.join(part for part in normalized if part)}"


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")

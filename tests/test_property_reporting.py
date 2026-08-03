"""Tests for reporting-only rental property summaries."""

from decimal import Decimal
from pathlib import Path

from engine.config import load_configuration
from engine.reporting import summarize_rental_properties


def test_rental_property_summary_reports_configured_value_and_net_yield() -> None:
    """Property reporting derives the displayed net yield without changing simulation data."""
    configuration_text = Path("data/example_household.yaml").read_text(encoding="utf-8")
    summaries = summarize_rental_properties(load_configuration(configuration_text))

    assert len(summaries) == 1
    assert summaries[0].name == "Ardfield Court"
    assert summaries[0].is_planned_purchase is True
    assert summaries[0].opening_or_purchase_value == Decimal("200000")
    assert summaries[0].net_yield == Decimal("0.08")

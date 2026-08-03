"""Focused tests for dashboard-only presentation helpers and transformations."""

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from dashboard.components.charts import asset_balance_rows, net_worth_figure
from dashboard.components.formatting import format_compact_eur, format_percentage, readiness_status
from dashboard.components.sections import (
    filter_projection_years,
    projection_table_rows,
    retirement_interpretation,
)
from engine.config import load_configuration
from engine.reporting import summarize_retirement_readiness
from engine.simulation import project_annually
from engine.simulation.projection import ProjectionYear


def _projection() -> tuple[ProjectionYear, ...]:
    """Return the documented baseline projection for presentation checks."""
    configuration_text = Path("data/example_household.yaml").read_text(encoding="utf-8")
    return project_annually(load_configuration(configuration_text))


def test_compact_eur_and_percentage_formatting() -> None:
    """KPI formatting remains consistent and avoids unnecessary precision."""
    assert format_compact_eur(Decimal("3080000")) == "€3.08m"
    assert format_compact_eur(Decimal("500000")) == "€500k"
    assert format_percentage(Decimal("0.1234")) == "12.3%"


def test_readiness_status_labels_are_clear() -> None:
    """Readiness state maps to concise user-facing status labels."""
    assert readiness_status(True) == ("Retirement ready", "success")
    assert readiness_status(False) == ("Funding gap", "error")


def test_projection_table_filters_and_formats_user_facing_columns() -> None:
    """Table transformations filter completed rows and hide implementation details."""
    projection = _projection()
    retirement_rows = filter_projection_years(projection, "Retirement years")
    table_rows = projection_table_rows(retirement_rows)

    assert retirement_rows
    assert all(not year.employed for year in retirement_rows)
    assert table_rows[0]["Phase"] == "Retirement"
    assert table_rows[0]["Net worth"].startswith("€")
    assert "cash_withdrawal" not in table_rows[0]


def test_chart_data_transformations_preserve_completed_projection_values() -> None:
    """Chart input is a presentation conversion, not a financial recalculation."""
    projection = _projection()
    rows = asset_balance_rows(projection)
    figure = net_worth_figure(projection, 2032)

    assert len(rows) == len(projection)
    assert rows[0]["net_worth"] == float(projection[0].net_worth)
    assert len(figure.data) == 6


def test_retirement_interpretation_for_funded_and_unfunded_outcomes() -> None:
    """Interpretation text is derived solely from reporting outputs."""
    readiness = summarize_retirement_readiness(_projection())
    unfunded = replace(
        readiness,
        retirement_ready=False,
        first_unfunded_year=2048,
        age_at_first_unfunded_year=76,
    )

    assert "fund the target spending" in retirement_interpretation(readiness, 95)
    assert retirement_interpretation(unfunded, 95) == (
        "The current plan first becomes unfunded in 2048 at age 76."
    )

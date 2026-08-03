"""Regression coverage for dashboard-only retirement-age what-if analysis."""

from decimal import Decimal
from pathlib import Path

from dashboard.components.charts import liquid_assets_comparison_figure, net_worth_figure
from dashboard.components.sections import styled_projection_table
from dashboard.inputs import configuration_to_yaml
from dashboard.state import (
    reset_what_if_retirement_age,
    set_what_if_retirement_age,
    what_if_retirement_age,
)
from dashboard.what_if import with_retirement_age
from engine.config import load_configuration
from engine.config.models import WealthOsConfig
from engine.reporting import compare_retirement_readiness, summarize_retirement_readiness
from engine.simulation import project_annually


def _configuration() -> WealthOsConfig:
    """Return the documented baseline configuration."""
    return load_configuration(Path("data/example_household.yaml").read_text(encoding="utf-8"))


def test_retirement_age_override_keeps_baseline_configuration_immutable() -> None:
    """A what-if age creates a validated copy and leaves exported baseline YAML unchanged."""
    baseline = _configuration()
    baseline_yaml = configuration_to_yaml(baseline)

    what_if = with_retirement_age(baseline, 54)

    assert baseline.household.planned_retirement_age == 60
    assert what_if.household.planned_retirement_age == 54
    assert configuration_to_yaml(baseline) == baseline_yaml


def test_retire_now_uses_existing_opening_year_retirement_boundary() -> None:
    """At current age, opening row has no employment, savings, or working-year RSU vesting."""
    projection = project_annually(with_retirement_age(_configuration(), 54))
    opening_year = projection[0]

    assert opening_year.employed is False
    assert opening_year.salary == Decimal("0")
    assert opening_year.annual_savings == Decimal("0")
    assert opening_year.annual_spending > Decimal("0")
    assert opening_year.amazon_shares == Decimal("310")


def test_earlier_and_later_retirement_change_only_timing_and_remain_deterministic() -> None:
    """Existing employment, savings, and spending rules apply at every override boundary."""
    baseline = _configuration()
    earlier = project_annually(with_retirement_age(baseline, 58))
    later = project_annually(with_retirement_age(baseline, 63))

    age_57 = next(year for year in earlier if year.age == 57)
    age_58 = next(year for year in earlier if year.age == 58)
    age_60 = next(year for year in later if year.age == 60)

    assert age_57.employed is True
    assert age_58.employed is False
    assert age_58.annual_savings == Decimal("0")
    assert age_58.annual_spending > Decimal("0")
    assert age_60.employed is True
    assert project_annually(with_retirement_age(baseline, 58)) == earlier


def test_session_what_if_persists_and_reset_returns_to_baseline() -> None:
    """The session-only override survives navigation-state reads and can be reset."""
    baseline = _configuration()
    state: dict[str, object] = {}

    set_what_if_retirement_age(state, 54)
    assert what_if_retirement_age(state, baseline) == 54
    reset_what_if_retirement_age(state, baseline)

    assert what_if_retirement_age(state, baseline) == 60


def test_comparison_metrics_and_chart_use_completed_baseline_and_what_if_outputs() -> None:
    """Comparison reporting and chart input are derived from the existing projection pipeline."""
    baseline_projection = project_annually(_configuration())
    what_if_projection = project_annually(with_retirement_age(_configuration(), 54))
    baseline_readiness = summarize_retirement_readiness(baseline_projection)
    what_if_readiness = summarize_retirement_readiness(what_if_projection)
    comparison = compare_retirement_readiness(baseline_readiness, what_if_readiness)
    baseline_retirement_year = next(year for year in baseline_projection if not year.employed)
    what_if_retirement_year = next(year for year in what_if_projection if not year.employed)
    chart = liquid_assets_comparison_figure(
        baseline_projection,
        what_if_projection,
        baseline_retirement_year.calendar_year,
        what_if_retirement_year.calendar_year,
    )

    assert comparison.baseline_age == 60
    assert comparison.what_if_age == 54
    assert comparison.metrics[0].difference == -6
    assert len(chart.data) == 2


def test_theme_compatible_table_and_chart_styles_avoid_fixed_light_backgrounds() -> None:
    """Retirement and unfunded status styling preserves theme text/background choices."""
    table_html = styled_projection_table(
        [
            {"Phase": "Working", "Status": "Working"},
            {"Phase": "Retirement", "Status": "Retirement"},
            {"Phase": "Retirement", "Status": "Unfunded"},
        ]
    ).to_html()
    projection = project_annually(_configuration())
    chart = net_worth_figure(projection, 2032)

    assert "background-color" not in table_html
    assert "var(--primary-color)" in table_html
    assert "var(--red-color, #DC2626)" in table_html
    assert chart.layout.paper_bgcolor == "rgba(0,0,0,0)"
    assert chart.layout.plot_bgcolor == "rgba(0,0,0,0)"
    assert chart.layout.yaxis.gridcolor == "rgba(128, 128, 128, 0.25)"

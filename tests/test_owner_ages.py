"""Owner-specific age regression coverage for pension and State Pension eligibility."""

from decimal import Decimal
from pathlib import Path

from engine.config import load_configuration
from engine.simulation import project_annually
from engine.simulation.owners import owner_age_in_year


def test_baseline_uses_each_owner_age_for_pension_and_state_pension() -> None:
    """The spouse cannot draw or receive State Pension using the primary person's age."""
    config = load_configuration(Path("data/example_household.yaml").read_text(encoding="utf-8"))
    timeline = project_annually(config)
    by_year = {year.calendar_year: year for year in timeline}

    assert owner_age_in_year(config, "Justin", 2032) == 60
    assert owner_age_in_year(config, "Wife", 2032) == 57
    assert by_year[2032].pension_values[0].withdrawal > Decimal("0")
    assert by_year[2032].pension_values[1].withdrawal == Decimal("0")
    assert by_year[2035].pension_values[1].withdrawal > Decimal("0")
    assert by_year[2038].state_pension_income > Decimal("0")
    assert by_year[2040].state_pension_income < by_year[2041].state_pension_income


def test_owner_age_rules_remain_deterministic_after_retirement_age_override() -> None:
    """Changing household retirement timing never changes the spouse's chronological age."""
    yaml_text = Path("data/example_household.yaml").read_text(encoding="utf-8")
    config = load_configuration(
        yaml_text.replace("planned_retirement_age: 60", "planned_retirement_age: 58")
    )
    timeline = project_annually(config)
    year_2035 = next(year for year in timeline if year.calendar_year == 2035)

    assert owner_age_in_year(config, "Wife", 2035) == 60
    assert year_2035.pension_values[1].withdrawal > Decimal("0")

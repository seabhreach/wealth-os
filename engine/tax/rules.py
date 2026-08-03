"""Versioned configurable Irish planning-tax rules loaded from YAML."""

from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path

import yaml


@dataclass(frozen=True, slots=True)
class UscBand:
    upper_limit: Decimal | None
    rate: Decimal


@dataclass(frozen=True, slots=True)
class TaxRules:
    tax_year: int
    standard_rate: Decimal
    higher_rate: Decimal
    married_standard_band: Decimal
    lower_earner_increase_cap: Decimal
    married_tax_credit: Decimal
    usc_exemption_threshold: Decimal
    usc_bands: tuple[UscBand, ...]
    prsi_enabled: bool
    prsi_rate: Decimal


def load_tax_rules(path: Path) -> TaxRules:
    """Load Decimal-safe versioned tax rules from a YAML file."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return TaxRules(
        tax_year=int(raw["tax_year"]),
        standard_rate=Decimal(str(raw["income_tax"]["standard_rate"])),
        higher_rate=Decimal(str(raw["income_tax"]["higher_rate"])),
        married_standard_band=Decimal(str(raw["income_tax"]["married_standard_band"])),
        lower_earner_increase_cap=Decimal(str(raw["income_tax"]["lower_earner_increase_cap"])),
        married_tax_credit=Decimal(str(raw["income_tax"]["married_tax_credit"])),
        usc_exemption_threshold=Decimal(str(raw["usc"]["exemption_threshold"])),
        usc_bands=tuple(
            UscBand(
                Decimal(str(item["upper_limit"])) if item["upper_limit"] is not None else None,
                Decimal(str(item["rate"])),
            )
            for item in raw["usc"]["bands"]
        ),
        prsi_enabled=bool(raw["prsi"]["enabled"]),
        prsi_rate=Decimal(str(raw["prsi"]["rate"])),
    )


def index_tax_rules(rules: TaxRules, years: int, inflation_rate: Decimal) -> TaxRules:
    """Index monetary rules with unrounded Decimal compounding; rates remain unchanged."""
    if years <= 0:
        return rules
    multiplier = (Decimal("1") + inflation_rate) ** years
    return replace(
        rules,
        tax_year=rules.tax_year + years,
        married_standard_band=rules.married_standard_band * multiplier,
        lower_earner_increase_cap=rules.lower_earner_increase_cap * multiplier,
        married_tax_credit=rules.married_tax_credit * multiplier,
        usc_exemption_threshold=rules.usc_exemption_threshold * multiplier,
        usc_bands=tuple(
            UscBand(
                band.upper_limit * multiplier if band.upper_limit is not None else None,
                band.rate,
            )
            for band in rules.usc_bands
        ),
    )

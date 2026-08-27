"""Read-only adapter from validated v0.2 configuration to customer-relevant items."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from engine.config import WealthOsConfig, load_configuration
from experience.live.models import FinancialPicture, FinancialPictureItem
from experience.live.provenance import financial_picture_fingerprint
from experience.models import InformationStatus

BASELINE_IDENTIFIER = "example-household-v0.2.0"


@dataclass(frozen=True, slots=True)
class LiveBaseline:
    """Validated immutable configuration held behind the adapter boundary."""

    configuration: WealthOsConfig
    financial_picture: FinancialPicture
    repository_root: Path


def load_live_baseline(configuration_path: Path) -> LiveBaseline:
    """Load the declared example baseline once through the existing validator."""

    resolved = configuration_path.resolve()
    configuration = load_configuration(resolved.read_text(encoding="utf-8"))
    repository_root = resolved.parents[1]
    return LiveBaseline(
        configuration=configuration,
        financial_picture=_adapt_picture(configuration),
        repository_root=repository_root,
    )


def _adapt_picture(configuration: WealthOsConfig) -> FinancialPicture:
    household = configuration.household
    items = [
        _item("household", "Household", household.name),
        _item("current_age", "Current age", household.current_age),
        _item("partner_age", "Partner age", household.spouse_age),
        _item(
            "planned_retirement_age",
            "Planned retirement age",
            household.planned_retirement_age,
        ),
        _item(
            "retirement_spending",
            "Retirement spending",
            configuration.assumptions.target_retirement_income,
        ),
        _item("cash", "Cash", configuration.investments.cash_balance),
        _item("investments", "ETF investments", configuration.investments.etf_value),
        _item(
            "employer_equity",
            "Employer-equity shares",
            configuration.amazon_rsus.vested_shares,
        ),
        _item(
            "equity_policy",
            "Employer-equity vesting policy",
            "Sell on vest" if configuration.amazon_rsus.sell_on_vest else "Retain",
        ),
        _item("inflation", "Inflation assumption", configuration.assumptions.inflation_rate),
        _item("tax", "Tax modelling", configuration.tax.enabled),
    ]
    for pension in configuration.pensions:
        items.append(_item(f"pension:{pension.name}", pension.name, pension.current_value))
    for property_config in configuration.rental_properties:
        items.extend(
            (
                _item(
                    f"property:{property_config.name}:year",
                    f"{property_config.name} purchase year",
                    property_config.purchase_year,
                ),
                _item(
                    f"property:{property_config.name}:price",
                    f"{property_config.name} purchase price",
                    property_config.purchase_price,
                ),
                _item(
                    f"property:{property_config.name}:rent",
                    f"{property_config.name} annual net rent",
                    property_config.annual_net_rent,
                ),
            )
        )
    return FinancialPicture(
        baseline_identifier=BASELINE_IDENTIFIER,
        fingerprint=financial_picture_fingerprint(configuration),
        items=tuple(items),
    )


def _item(key: str, label: str, value: str | int | Decimal | bool) -> FinancialPictureItem:
    return FinancialPictureItem(
        key=key,
        label=label,
        value=value,
        status=InformationStatus.KNOWN,
        source="Validated example configuration",
    )

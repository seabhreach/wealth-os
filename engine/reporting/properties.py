"""Presentation-ready reporting for configured rental properties."""

from dataclasses import dataclass
from decimal import Decimal

from engine.config.models import WealthOsConfig


@dataclass(frozen=True, slots=True)
class RentalPropertySummary:
    """Configured rental-property inputs with a derived net yield for reporting."""

    name: str
    purchase_year: int
    purchase_price: Decimal
    opening_or_purchase_value: Decimal
    annual_net_rent: Decimal
    net_yield: Decimal | None
    annual_growth_rate: Decimal
    is_planned_purchase: bool


def summarize_rental_properties(config: WealthOsConfig) -> tuple[RentalPropertySummary, ...]:
    """Summarize configured properties without changing simulation behaviour."""
    summaries: list[RentalPropertySummary] = []
    for property_config in config.rental_properties:
        opening_or_purchase_value = (
            property_config.current_value
            if property_config.purchase_year <= config.assumptions.start_year
            else property_config.purchase_price
        )
        net_yield = (
            property_config.annual_net_rent / opening_or_purchase_value
            if opening_or_purchase_value > Decimal("0")
            else None
        )
        summaries.append(
            RentalPropertySummary(
                name=property_config.name,
                purchase_year=property_config.purchase_year,
                purchase_price=property_config.purchase_price,
                opening_or_purchase_value=opening_or_purchase_value,
                annual_net_rent=property_config.annual_net_rent,
                net_yield=net_yield,
                annual_growth_rate=property_config.annual_growth_rate,
                is_planned_purchase=property_config.purchase_year > config.assumptions.start_year,
            )
        )
    return tuple(summaries)

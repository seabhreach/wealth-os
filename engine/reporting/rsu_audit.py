"""Reporting-only cash and Amazon RSU audit bridges for completed projections."""

from dataclasses import dataclass
from decimal import Decimal

from engine.config.models import WealthOsConfig
from engine.reporting.explainability import annual_calculation_trace
from engine.simulation.projection import ProjectionYear

ZERO = Decimal("0")


@dataclass(frozen=True, slots=True)
class CashBridgeRow:
    """One completed annual cash movement reconciliation."""

    calendar_year: int
    opening_cash: Decimal
    annual_savings: Decimal
    rsu_sale_proceeds: Decimal
    rental_income: Decimal
    property_purchase: Decimal
    cash_used_for_spending: Decimal
    other_cash_movement: Decimal
    closing_cash: Decimal


@dataclass(frozen=True, slots=True)
class AmazonShareBridgeRow:
    """One completed annual Amazon share and value reconciliation."""

    calendar_year: int
    opening_shares: Decimal
    shares_vested: Decimal
    shares_sold_on_vest: Decimal
    shares_sold_for_spending: Decimal
    closing_shares: Decimal
    projected_usd_share_price: Decimal
    eur_amazon_value: Decimal


@dataclass(frozen=True, slots=True)
class RsuAuditSummary:
    """Configuration facts and cumulative audit bridges through the first retirement row."""

    opening_vested_shares: Decimal
    opening_vested_value_eur: Decimal
    annual_grant_shares: Decimal
    sell_on_vest: bool
    opening_share_price_usd: Decimal
    annual_growth_rate: Decimal
    eur_usd_exchange_rate: Decimal
    working_year_grants: int
    cash_bridge: tuple[CashBridgeRow, ...]
    amazon_share_bridge: tuple[AmazonShareBridgeRow, ...]

    @property
    def cumulative_annual_savings(self) -> Decimal:
        """Return annual savings through the first retirement row."""
        return sum((row.annual_savings for row in self.cash_bridge), start=ZERO)

    @property
    def cumulative_rsu_sale_proceeds(self) -> Decimal:
        """Return all completed RSU sales transferred to cash before retirement."""
        return sum((row.rsu_sale_proceeds for row in self.cash_bridge), start=ZERO)

    @property
    def cumulative_rental_income(self) -> Decimal:
        """Return all rent credited to cash through the first retirement row."""
        return sum((row.rental_income for row in self.cash_bridge), start=ZERO)

    @property
    def cumulative_property_purchases(self) -> Decimal:
        """Return the in-projection cash purchase total through the first retirement row."""
        return sum((row.property_purchase for row in self.cash_bridge), start=ZERO)


def summarize_rsu_audit(
    timeline: tuple[ProjectionYear, ...], config: WealthOsConfig
) -> RsuAuditSummary:
    """Build cash and share audit bridges from completed projection and trace reporting output."""
    first_retirement_index = next(index for index, year in enumerate(timeline) if not year.employed)
    cash_rows = tuple(
        _cash_bridge_row(timeline, config, index) for index in range(first_retirement_index + 1)
    )
    share_rows = tuple(_share_bridge_row(timeline, config, index) for index in range(len(timeline)))
    amazon = config.amazon_rsus
    return RsuAuditSummary(
        opening_vested_shares=amazon.vested_shares,
        opening_vested_value_eur=(
            amazon.vested_shares * amazon.share_price_usd * amazon.eur_usd_exchange_rate
        ),
        annual_grant_shares=amazon.annual_grant_shares,
        sell_on_vest=amazon.sell_on_vest,
        opening_share_price_usd=amazon.share_price_usd,
        annual_growth_rate=amazon.annual_growth_rate,
        eur_usd_exchange_rate=amazon.eur_usd_exchange_rate,
        working_year_grants=sum(1 for year in timeline if year.employed),
        cash_bridge=cash_rows,
        amazon_share_bridge=share_rows,
    )


def _cash_bridge_row(
    timeline: tuple[ProjectionYear, ...], config: WealthOsConfig, index: int
) -> CashBridgeRow:
    """Expose one completed trace as an annual cash bridge without altering balances."""
    trace = annual_calculation_trace(timeline, config, timeline[index].calendar_year)
    return CashBridgeRow(
        calendar_year=trace.calendar_year,
        opening_cash=trace.opening_cash,
        annual_savings=trace.annual_savings,
        rsu_sale_proceeds=trace.rsu_sale_proceeds,
        rental_income=trace.rental_income,
        property_purchase=trace.property_purchase_cost,
        cash_used_for_spending=trace.cash_withdrawal,
        other_cash_movement=ZERO,
        closing_cash=trace.closing_cash,
    )


def _share_bridge_row(
    timeline: tuple[ProjectionYear, ...], config: WealthOsConfig, index: int
) -> AmazonShareBridgeRow:
    """Expose one completed row's Amazon holdings, including the modelled price in USD."""
    year = timeline[index]
    opening_shares = (
        timeline[index - 1].amazon_shares if index > 0 else config.amazon_rsus.vested_shares
    )
    shares_vested = config.amazon_rsus.annual_grant_shares if year.employed else ZERO
    shares_sold_on_vest = shares_vested if config.amazon_rsus.sell_on_vest else ZERO
    eur_share_price = year.amazon_value / year.amazon_shares if year.amazon_shares != ZERO else ZERO
    shares_sold_for_spending = (
        year.amazon_withdrawal / eur_share_price if eur_share_price != ZERO else ZERO
    )
    return AmazonShareBridgeRow(
        calendar_year=year.calendar_year,
        opening_shares=opening_shares,
        shares_vested=shares_vested,
        shares_sold_on_vest=shares_sold_on_vest,
        shares_sold_for_spending=shares_sold_for_spending,
        closing_shares=year.amazon_shares,
        projected_usd_share_price=(
            eur_share_price / config.amazon_rsus.eur_usd_exchange_rate
            if config.amazon_rsus.eur_usd_exchange_rate != ZERO
            else ZERO
        ),
        eur_amazon_value=year.amazon_value,
    )

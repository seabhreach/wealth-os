"""Dashboard-specific presentation transformations and renderers."""

from decimal import Decimal
from typing import Literal

import pandas as pd  # type: ignore[import-untyped]
import streamlit as st

from dashboard.components.formatting import (
    display_reconciliation_adjustment,
    display_whole_value,
    format_compact_eur,
    format_eur,
    format_eur_cents,
    format_percentage,
    format_usd,
    readiness_status,
)
from engine.config.models import WealthOsConfig
from engine.reporting import (
    AmazonShareBridgeRow,
    AnnualCalculationTrace,
    AnnualFinancialStatement,
    AnnualTaxStatement,
    BeforeAfterTaxComparison,
    RentalPropertySummary,
    RetirementComparison,
    RetirementComparisonMetric,
    RetirementReadinessSummary,
    RsuAuditSummary,
)
from engine.simulation.projection import ProjectionYear

ProjectionFilter = Literal["All years", "Working years", "Retirement years", "Unfunded years"]


def filter_projection_years(
    timeline: tuple[ProjectionYear, ...], selection: ProjectionFilter
) -> tuple[ProjectionYear, ...]:
    """Filter projection rows for the selected user-facing table view."""
    if selection == "Working years":
        return tuple(year for year in timeline if year.employed)
    if selection == "Retirement years":
        return tuple(year for year in timeline if not year.employed)
    if selection == "Unfunded years":
        return tuple(year for year in timeline if not year.retirement_target_met)
    return timeline


def projection_table_rows(timeline: tuple[ProjectionYear, ...]) -> list[dict[str, str]]:
    """Return user-facing, formatted rows without exposing implementation fields."""
    rows: list[dict[str, str]] = []
    for year in timeline:
        phase = "Working" if year.employed else "Retirement"
        status = "Unfunded" if not year.retirement_target_met else phase
        rows.append(
            {
                "Year": str(year.calendar_year),
                "Age": str(year.age),
                "Phase": phase,
                "Status": status,
                "Net worth": format_eur(year.net_worth),
                "Liquid assets": format_eur(year.liquid_assets),
                "Cash": format_eur(year.cash_balance),
                "ETFs": format_eur(year.etf_value),
                "Amazon": format_eur(year.amazon_value),
                "Pensions": format_eur(year.pension_value),
                "Property": format_eur(year.property_value),
                "Rental income": format_eur(year.rental_income),
                "Spending target": format_eur(year.annual_spending),
                "Withdrawals": format_eur(year.withdrawal_amount),
                "Unfunded spending": format_eur(year.unfunded_spending),
            }
        )
    return rows


def retirement_interpretation(
    readiness: RetirementReadinessSummary, life_expectancy_age: int
) -> str:
    """Express existing retirement-readiness outputs in concise plain English."""
    if readiness.retirement_ready:
        return (
            "Under these assumptions, the household can fund the target spending through "
            f"age {life_expectancy_age} using rental income and liquid investments while "
            "preserving pensions."
        )
    return (
        "The current plan first becomes unfunded in "
        f"{readiness.first_unfunded_year} at age {readiness.age_at_first_unfunded_year}."
    )


def retirement_comparison_rows(comparison: RetirementComparison) -> list[dict[str, str]]:
    """Format reporting comparison metrics for the compact retirement page table."""
    return [
        {
            "Metric": metric.label,
            "Baseline": _format_comparison_value(metric.baseline),
            "What-if": _format_comparison_value(metric.what_if),
            "Difference": _format_comparison_difference(metric),
        }
        for metric in comparison.metrics
    ]


def _format_comparison_value(value: Decimal | int | bool | None) -> str:
    """Format one reporting value without performing a financial calculation."""
    if isinstance(value, Decimal):
        return format_eur(value)
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value) if value is not None else "None"


def _format_comparison_difference(metric: RetirementComparisonMetric) -> str:
    """Format a supplied reporting difference, retaining non-numeric comparisons as a dash."""
    difference = metric.difference
    if difference is None:
        return "—"
    if isinstance(difference, Decimal):
        prefix = "+" if difference > 0 else ""
        return f"{prefix}{format_eur(difference)}"
    prefix = "+" if difference > 0 else ""
    return f"{prefix}{difference}"


def render_readiness_banner(readiness: RetirementReadinessSummary) -> None:
    """Render the executive retirement readiness status without recalculation."""
    label, tone = readiness_status(readiness.retirement_ready)
    message = (
        f"{label}: first retirement year is {readiness.first_retirement_year}."
        if readiness.retirement_ready
        else (
            f"{label}: spending first becomes unfunded in {readiness.first_unfunded_year} "
            f"at age {readiness.age_at_first_unfunded_year}."
        )
    )
    message_renderer = st.success if tone == "success" else st.error
    message_renderer(message)


def render_property_cards(properties: tuple[RentalPropertySummary, ...]) -> None:
    """Render concise configured rental-property detail cards."""
    if not properties:
        st.info("No rental properties are included in this configuration.")
        return
    for property_summary in properties:
        label = (
            f"Planned property purchase: {property_summary.name}"
            if property_summary.is_planned_purchase
            else property_summary.name
        )
        with st.expander(label, expanded=len(properties) == 1):
            left, right = st.columns(2)
            purchase_year_label = (
                "Planned purchase year" if property_summary.is_planned_purchase else "Purchase year"
            )
            left.markdown(
                "\n".join(
                    (
                        f"**{purchase_year_label}**  \n{property_summary.purchase_year}",
                        f"**Purchase price**  \n{format_eur(property_summary.purchase_price)}",
                        "**Opening / purchase value**  \n"
                        f"{format_eur(property_summary.opening_or_purchase_value)}",
                    )
                )
            )
            yield_text = (
                format_percentage(property_summary.net_yield)
                if property_summary.net_yield is not None
                else "Not available"
            )
            right.markdown(
                "\n".join(
                    (
                        f"**Annual net rent**  \n{format_eur(property_summary.annual_net_rent)}",
                        f"**Net yield**  \n{yield_text}",
                        "**Growth assumption**  \n"
                        f"{format_percentage(property_summary.annual_growth_rate)}",
                    )
                )
            )


def render_pension_cards(
    current_year: ProjectionYear, retirement_year: ProjectionYear, final_year: ProjectionYear
) -> None:
    """Render current and projected pension values per owner."""
    st.metric("Combined pension value", format_compact_eur(current_year.pension_value))
    for index, pension_balance in enumerate(current_year.pension_values):
        with st.container(border=True):
            retirement_balance = retirement_year.pension_values[index].value
            life_expectancy_balance = final_year.pension_values[index].value
            st.markdown(f"**{pension_balance.owner} pension**")
            current, at_retirement, at_life_expectancy = st.columns(3)
            current.metric("Current", format_compact_eur(pension_balance.value))
            at_retirement.metric("At retirement", format_compact_eur(retirement_balance))
            at_life_expectancy.metric(
                "At life expectancy", format_compact_eur(life_expectancy_balance)
            )


def render_retirement_funding(year: ProjectionYear) -> None:
    """Render the completed first-retirement-year spending breakdown."""
    st.subheader("How retirement spending is funded")
    st.caption(
        f"Your {format_eur(year.annual_spending)} spending target is funded by "
        f"{format_eur(year.net_recurring_income)} of recurring income and "
        f"{format_eur(year.withdrawal_amount)} withdrawn from liquid assets."
    )
    st.markdown(
        "\n".join(
            (
                f"**{format_eur(year.annual_spending)} target spending** "
                f"- **{format_eur(year.net_recurring_income)} net recurring income** "
                f"= **{format_eur(year.withdrawal_amount)} remaining spending to fund**",
                f"**Cash used {format_eur(year.cash_withdrawal)}** + "
                f"**ETF units sold {format_eur(year.etf_withdrawal)}** + "
                f"**Amazon shares sold {format_eur(year.amazon_withdrawal)}** "
                f"= **{format_eur(year.withdrawal_amount)} funding from liquid assets**",
            )
        )
    )
    st.info(
        "Recurring income includes rent, permitted private pension drawdown, and State Pension; "
        "estimated tax is deducted when tax modelling is enabled."
    )


def render_annual_financial_statement(statement: AnnualFinancialStatement, narrative: str) -> None:
    """Render a selected year's accessible retirement income and asset movement statement."""
    funding = statement.funding
    trace = statement.assets.trace
    st.subheader(f"Annual statement: {statement.calendar_year}")
    st.caption(narrative)
    funding_column, spending_column, closing_column = st.columns(3)
    with funding_column:
        st.markdown("**Money available for spending**")
        for label, value in (
            ("Gross rental profit", funding.rental_income),
            ("Gross State Pension", funding.state_pension),
            ("Gross private pension income", funding.private_pension_income),
            ("Estimated Income Tax", -funding.estimated_income_tax),
            ("Estimated USC", -funding.estimated_usc),
            ("Estimated PRSI", -funding.estimated_prsi),
            ("Cash used", funding.cash_used),
            ("ETF units sold", funding.etf_units_sold),
            ("Amazon shares sold", funding.amazon_shares_sold),
            ("Other income", funding.other_income),
            ("Unfunded amount", funding.unfunded_amount),
        ):
            st.caption(f"{label}: {format_eur(value)}")
        funding_adjustment = display_reconciliation_adjustment(
            funding.total_funding,
            (
                funding.rental_income,
                funding.state_pension,
                funding.private_pension_income,
                funding.cash_used,
                funding.etf_units_sold,
                funding.amazon_shares_sold,
                funding.other_income,
                funding.unfunded_amount,
            ),
            (
                funding.estimated_income_tax,
                funding.estimated_usc,
                funding.estimated_prsi,
            ),
        )
        _render_rounding_adjustment(funding_adjustment)
        st.markdown(f"**Total funding: {format_eur(funding.total_funding)}**")
    with spending_column:
        st.markdown("**Spending**")
        st.caption(f"Retirement spending: {format_eur(funding.retirement_spending)}")
        st.caption(f"Surplus / deficit: {format_eur(funding.surplus_or_deficit)}")
        st.caption(
            "Estimated Irish tax based on configured planning assumptions. This is not a tax "
            "return or tax advice."
            if funding.tax_modelling_enabled
            else "Tax modelling disabled; gross recurring-income behaviour is preserved."
        )
    with closing_column:
        st.markdown("**Closing assets**")
        for label, value in (
            ("Cash", trace.closing_cash),
            ("ETFs", trace.closing_etf_value),
            ("Amazon", trace.closing_amazon_value),
            ("Pensions", trace.closing_pension_value),
            ("Property", trace.closing_property_value),
            ("Liquid assets", statement.liquid_assets),
            ("Net worth", statement.net_worth),
        ):
            st.caption(f"{label}: {format_eur(value)}")
    _render_asset_movement_cards(statement)


def render_tax_statement(statement: AnnualTaxStatement) -> None:
    """Render a clear gross-to-net retirement-tax explanation from reporting outputs."""
    st.subheader("Retirement income after estimated tax")
    if not statement.enabled:
        st.info("Tax modelling disabled. Gross recurring income is used for retirement spending.")
        return
    rental_profit = statement.gross_recurring_income - sum(
        (
            person.private_pension_income + person.state_pension_income
            for person in statement.people
        ),
        start=Decimal("0"),
    )
    liquid_funding = statement.cash_used + statement.etf_units_sold + statement.amazon_shares_sold
    st.markdown("**Gross recurring income**")
    st.caption(f"Rental profit: {format_eur(rental_profit)}")
    for person in statement.people:
        st.caption(
            f"{person.person} private pension / State Pension: "
            f"{format_eur(person.private_pension_income)} / "
            f"{format_eur(person.state_pension_income)}"
        )
    st.caption(f"Total gross recurring income: {format_eur(statement.gross_recurring_income)}")
    st.markdown("**Estimated taxes**")
    st.caption(
        f"Income Tax / USC / PRSI: {format_eur(statement.income_tax)} / "
        f"{format_eur(statement.usc)} / {format_eur(statement.prsi)}"
    )
    st.caption(f"Total estimated tax: {format_eur(statement.total_tax)}")
    st.markdown(
        f"**{format_eur(statement.gross_recurring_income)} gross recurring income** - "
        f"**{format_eur(statement.total_tax)} estimated tax** = "
        f"**{format_eur(statement.net_recurring_income)} net recurring income**"
    )
    st.markdown("**Additional funding**")
    st.caption(
        f"Cash / ETFs / Amazon / unfunded: {format_eur(statement.cash_used)} / "
        f"{format_eur(statement.etf_units_sold)} / {format_eur(statement.amazon_shares_sold)} / "
        f"{format_eur(statement.unfunded_amount)}"
    )
    st.markdown(
        f"**{format_eur(statement.net_recurring_income)} net recurring income** + "
        f"**{format_eur(liquid_funding)} "
        f"liquid funding** = **{format_eur(statement.total_funding)} total retirement funding**"
    )
    st.caption(
        f"Spending target: {format_eur(statement.retirement_spending)}. "
        f"Surplus / deficit: {format_eur(statement.total_funding - statement.retirement_spending)}."
    )
    _render_person_tax_table(statement)
    st.caption(
        "State Pension is included for Income Tax but excluded from USC. Cash use and ETF or "
        "Amazon sales are excluded from ordinary income tax in this model. PRSI is disabled in "
        "the example baseline."
    )


def _render_person_tax_table(statement: AnnualTaxStatement) -> None:
    """Render compact detailed person-level tax values with controlled two-decimal precision."""
    st.markdown("**Per-person estimated tax breakdown**")
    rows = [
        {
            "Person": person.person,
            "Age": person.age,
            "Rental profit": format_eur_cents(person.rental_profit),
            "Private pension": format_eur_cents(person.private_pension_income),
            "State Pension": format_eur_cents(person.state_pension_income),
            "Income Tax base": format_eur_cents(person.result.income_taxable),
            "USC base": format_eur_cents(person.result.usc_taxable),
            "Standard-rate income": format_eur_cents(person.result.standard_rate_income),
            "Higher-rate income": format_eur_cents(person.result.higher_rate_income),
            "Credits": format_eur_cents(person.result.credits),
            "Income Tax": format_eur_cents(person.result.income_tax),
            "USC": format_eur_cents(person.result.usc),
            "PRSI": format_eur_cents(person.result.prsi),
            "Total tax": format_eur_cents(person.result.total_tax),
            "Net income": format_eur_cents(person.result.net_income),
        }
        for person in statement.people
    ]
    st.dataframe(rows, hide_index=True, use_container_width=True)
    st.caption(
        "Under joint assessment, standard-rate and higher-rate income are allocated between "
        "people proportionately for explanation; the Income Tax calculation remains household-wide."
    )


def render_before_after_tax_comparison(comparison: BeforeAfterTaxComparison | None) -> None:
    """Render an equal-input before/after tax comparison, or a disabled status."""
    st.subheader("Before and after estimated tax")
    if comparison is None:
        st.info("Tax modelling disabled. Enable it on Inputs to compare gross and net income.")
        return
    st.dataframe(
        [
            {
                "Metric": "First-retirement gross recurring income",
                "Before tax": format_eur(comparison.gross_recurring_income),
                "After tax": format_eur(comparison.gross_recurring_income),
            },
            {
                "Metric": "Estimated tax",
                "Before tax": "Not modelled",
                "After tax": format_eur(comparison.tax),
            },
            {
                "Metric": "Net recurring income",
                "Before tax": format_eur(comparison.gross_recurring_income),
                "After tax": format_eur(comparison.net_recurring_income),
            },
            {
                "Metric": "Liquid funding required",
                "Before tax": format_eur(comparison.liquid_funding_before_tax),
                "After tax": format_eur(comparison.liquid_funding_after_tax),
            },
            {
                "Metric": "Final liquid assets",
                "Before tax": format_compact_eur(comparison.final_liquid_assets_before_tax),
                "After tax": format_compact_eur(comparison.final_liquid_assets_after_tax),
            },
            {
                "Metric": "Final net worth",
                "Before tax": format_compact_eur(comparison.final_net_worth_before_tax),
                "After tax": format_compact_eur(comparison.final_net_worth_after_tax),
            },
        ],
        hide_index=True,
        use_container_width=True,
    )
    st.caption(
        "Both projections use identical assumptions except for enabled estimated tax modelling."
    )


def render_retirement_cash_origin(audit: RsuAuditSummary) -> None:
    """Explain and reconcile the origins of cash accumulated through the first retirement row."""
    first_retirement_row = audit.cash_bridge[-1]
    cumulative_cash_used = sum(
        (row.cash_used_for_spending for row in audit.cash_bridge), start=Decimal("0")
    )
    st.subheader("Where did the retirement cash balance come from?")
    rsu_status = (
        "Annual Amazon grants are sold on vest and transferred to cash."
        if audit.sell_on_vest
        else "Annual Amazon grants are retained as Amazon shares."
    )
    st.info(rsu_status)
    st.caption(
        "Before retirement, "
        f"{format_eur(audit.cumulative_rsu_sale_proceeds)} of cash was generated from Amazon "
        f"RSUs sold on vest, {format_eur(audit.cumulative_annual_savings)} from annual savings, "
        f"and {format_eur(audit.cumulative_rental_income)} from rental income."
    )
    st.markdown(
        "\n".join(
            (
                f"**{format_eur(audit.cash_bridge[0].opening_cash)} opening cash** "
                f"- **{format_eur(audit.cumulative_property_purchases)} property purchases** "
                f"+ **{format_eur(audit.cumulative_annual_savings)} annual savings** "
                f"+ **{format_eur(audit.cumulative_rsu_sale_proceeds)} RSU sale proceeds** "
                f"+ **{format_eur(audit.cumulative_rental_income)} rental income** "
                f"- **{format_eur(cumulative_cash_used)} cash used for spending** "
                f"= **{format_eur(first_retirement_row.closing_cash)} first-retirement-year cash**",
                "The first rental property is purchased from cash in 2027. Future Amazon grants "
                "are sold on vest and transferred to cash.",
            )
        )
    )
    st.dataframe(_cash_bridge_rows(audit), hide_index=True, use_container_width=True)


def render_amazon_audit(audit: RsuAuditSummary) -> None:
    """Show configuration facts, cumulative share bridge, and annual Amazon movement context."""
    st.subheader("Amazon RSU audit")
    status = "Sold on vest into cash" if audit.sell_on_vest else "Retained as Amazon shares"
    st.caption(
        f"Opening vested shares: {audit.opening_vested_shares:,.0f}; opening value: "
        f"{format_eur(audit.opening_vested_value_eur)}; annual grant: "
        f"{audit.annual_grant_shares:,.0f} shares; policy: {status}."
    )
    st.caption(
        f"Opening price: {format_usd(audit.opening_share_price_usd)}; annual growth: "
        f"{format_percentage(audit.annual_growth_rate)}; EUR/USD: "
        f"{audit.eur_usd_exchange_rate}; working-year grants: {audit.working_year_grants}."
    )
    first_retirement_index = audit.working_year_grants
    rows = audit.amazon_share_bridge[: first_retirement_index + 1]
    vested_shares = sum((row.shares_vested for row in rows), start=Decimal("0"))
    sold_on_vest_shares = sum((row.shares_sold_on_vest for row in rows), start=Decimal("0"))
    sold_for_spending_shares = sum(
        (row.shares_sold_for_spending for row in rows), start=Decimal("0")
    )
    st.markdown(
        f"**{rows[0].opening_shares:,.0f} opening shares** + "
        f"**{vested_shares:,.0f} vested** - "
        f"**{sold_on_vest_shares:,.0f} sold on vest** - "
        f"**{sold_for_spending_shares:,.0f} sold for spending** "
        f"= **{rows[-1].closing_shares:,.0f} closing shares**"
    )
    st.caption(
        "Share-price growth is applied after the annual vesting decision. The opening year "
        "includes a grant while employed; the retirement year does not."
    )
    st.dataframe(
        _amazon_bridge_rows(audit.amazon_share_bridge), hide_index=True, use_container_width=True
    )


def _cash_bridge_rows(audit: RsuAuditSummary) -> list[dict[str, str]]:
    """Format completed cash bridge values for the dashboard without recalculating them."""
    return [
        {
            "Year": str(row.calendar_year),
            "Opening cash": format_eur(row.opening_cash),
            "Savings": format_eur(row.annual_savings),
            "RSU sales": format_eur(row.rsu_sale_proceeds),
            "Rent": format_eur(row.rental_income),
            "Property purchase": format_eur(row.property_purchase),
            "Cash used": format_eur(row.cash_used_for_spending),
            "Closing cash": format_eur(row.closing_cash),
        }
        for row in audit.cash_bridge
    ]


def _amazon_bridge_rows(rows: tuple[AmazonShareBridgeRow, ...]) -> list[dict[str, str]]:
    """Format completed Amazon bridge values while keeping the calculation in reporting."""
    return [
        {
            "Year": str(row.calendar_year),
            "Opening shares": f"{row.opening_shares:,.2f}",
            "Vested": f"{row.shares_vested:,.2f}",
            "Sold on vest": f"{row.shares_sold_on_vest:,.2f}",
            "Sold for spending": f"{row.shares_sold_for_spending:,.2f}",
            "Closing shares": f"{row.closing_shares:,.2f}",
            "USD price": format_usd(row.projected_usd_share_price),
            "EUR value": format_eur(row.eur_amazon_value),
        }
        for row in rows
    ]


def _render_asset_movement_cards(statement: AnnualFinancialStatement) -> None:
    """Show completed opening-to-closing movements without recomputing balances in Streamlit."""
    trace = statement.assets.trace
    st.markdown("**Asset movements**")
    cash, etfs, amazon, pensions, property = st.columns(5)
    with cash:
        st.caption("Cash")
        st.caption(f"Opening: {format_eur(trace.opening_cash)}")
        st.caption(
            "Savings / RSUs / rent: "
            f"{format_eur(trace.annual_savings)} / "
            f"{format_eur(trace.rsu_sale_proceeds)} / {format_eur(trace.rental_income)}"
        )
        st.caption(
            "Property / spending: "
            f"{format_eur(trace.property_purchase_cost)} / {format_eur(trace.cash_withdrawal)}"
        )
        st.caption(f"Closing: {format_eur(trace.closing_cash)}")
        _render_rounding_adjustment(
            display_reconciliation_adjustment(
                trace.closing_cash,
                (
                    trace.opening_cash,
                    trace.annual_savings,
                    trace.rsu_sale_proceeds,
                    trace.rental_income,
                ),
                (trace.property_purchase_cost, trace.cash_withdrawal),
            )
        )
    with etfs:
        st.caption("ETFs")
        st.caption(
            "Opening / growth: "
            f"{format_eur(trace.opening_etf_value)} / {format_eur(trace.etf_growth_amount)}"
        )
        st.caption(f"Units sold: {format_eur(trace.etf_withdrawal)}")
        st.caption(f"Closing: {format_eur(trace.closing_etf_value)}")
        _render_rounding_adjustment(
            display_reconciliation_adjustment(
                trace.closing_etf_value,
                (trace.opening_etf_value, trace.etf_growth_amount),
                (trace.etf_withdrawal,),
            )
        )
    with amazon:
        st.caption("Amazon")
        st.caption(
            f"Opening: {trace.opening_amazon_shares:,.0f} shares, "
            f"{format_eur(trace.opening_amazon_value)}"
        )
        st.caption(
            f"Growth / vested: {format_eur(trace.amazon_growth_amount)} / "
            f"{trace.rsu_shares_vested:,.0f} shares"
        )
        st.caption(f"Retained RSU value: {format_eur(statement.assets.amazon_retained_rsu_value)}")
        st.caption(
            "Sold on vest / spending: "
            f"{statement.assets.amazon_shares_sold_on_vest:,.0f} / "
            f"{statement.assets.amazon_shares_sold_for_spending:,.0f} shares"
        )
        st.caption(
            f"Closing: {trace.closing_amazon_shares:,.0f} shares, "
            f"{format_eur(trace.closing_amazon_value)}"
        )
        _render_share_rounding_adjustment(
            display_whole_value(trace.closing_amazon_shares)
            - (
                display_whole_value(trace.opening_amazon_shares)
                + display_whole_value(trace.rsu_shares_vested)
                - display_whole_value(statement.assets.amazon_shares_sold_on_vest)
                - display_whole_value(statement.assets.amazon_shares_sold_for_spending)
            )
        )
        _render_rounding_adjustment(
            display_reconciliation_adjustment(
                trace.closing_amazon_value,
                (
                    trace.opening_amazon_value,
                    trace.amazon_growth_amount,
                    statement.assets.amazon_retained_rsu_value,
                ),
                (trace.amazon_withdrawal,),
            )
        )
    with pensions:
        st.caption("Pensions")
        st.caption(
            "Opening / growth: "
            f"{format_eur(trace.opening_pension_value)} / "
            f"{format_eur(trace.pension_growth_amount)}"
        )
        st.caption(f"Contributions / income: {format_eur(trace.pension_contribution_amount)} / €0")
        st.caption(f"Closing: {format_eur(trace.closing_pension_value)}")
        _render_rounding_adjustment(
            display_reconciliation_adjustment(
                trace.closing_pension_value,
                (
                    trace.opening_pension_value,
                    trace.pension_growth_amount,
                    trace.pension_contribution_amount,
                ),
            )
        )
    with property:
        st.caption("Property")
        st.caption(
            "Opening / purchased: "
            f"{format_eur(trace.opening_property_value)} / "
            f"{format_eur(trace.property_purchase_cost)}"
        )
        st.caption(
            "Appreciation / rent: "
            f"{format_eur(trace.property_appreciation)} / {format_eur(trace.rental_income)}"
        )
        st.caption("Property sold: €0")
        st.caption(f"Closing: {format_eur(trace.closing_property_value)}")
        _render_rounding_adjustment(
            display_reconciliation_adjustment(
                trace.closing_property_value,
                (
                    trace.opening_property_value,
                    trace.property_purchase_cost,
                    trace.property_appreciation,
                ),
            )
        )


def _render_rounding_adjustment(adjustment: Decimal) -> None:
    """Show a visible adjustment only when whole-euro display rounding requires one."""
    if adjustment != Decimal("0"):
        st.caption(f"Rounding adjustment: {format_eur(adjustment)}")


def _render_share_rounding_adjustment(adjustment: Decimal) -> None:
    """Show a visible adjustment for whole-share display rounding when it is required."""
    if adjustment != Decimal("0"):
        st.caption(f"Share rounding adjustment: {adjustment:,.0f} shares")


def render_calculation_trace(trace: AnnualCalculationTrace) -> None:
    """Render a reporting trace whose values come from the completed projection."""
    st.subheader(f"Calculation trace: {trace.calendar_year}")
    opening, inflows, outflows, closing = st.columns(4)
    with opening:
        st.markdown("**Opening position**")
        st.caption(f"Cash: {format_eur(trace.opening_cash)}")
        st.caption(f"ETFs: {format_eur(trace.opening_etf_value)}")
        st.caption(f"Amazon: {format_eur(trace.opening_amazon_value)}")
        st.caption(f"Pensions: {format_eur(trace.opening_pension_value)}")
        st.caption(f"Property: {format_eur(trace.opening_property_value)}")
    with inflows:
        st.markdown("**Inflows and growth**")
        st.caption(f"Savings: {format_eur(trace.annual_savings)}")
        st.caption(f"ETF growth: {format_eur(trace.etf_growth_amount)}")
        st.caption(f"Amazon growth: {format_eur(trace.amazon_growth_amount)}")
        st.caption(f"RSUs vested: {trace.rsu_shares_vested:,.0f} shares")
        st.caption(f"RSU sale proceeds: {format_eur(trace.rsu_sale_proceeds)}")
        st.caption(f"Rent: {format_eur(trace.rental_income)}")
        st.caption(
            "Pension growth / contributions: "
            f"{format_eur(trace.pension_growth_amount)} / "
            f"{format_eur(trace.pension_contribution_amount)}"
        )
        st.caption(f"Property appreciation: {format_eur(trace.property_appreciation)}")
    with outflows:
        st.markdown("**Outflows**")
        st.caption(f"Property purchase: {format_eur(trace.property_purchase_cost)}")
        st.caption(f"Retirement spending: {format_eur(trace.retirement_spending)}")
        st.caption(
            "Cash / ETF / Amazon withdrawals: "
            f"{format_eur(trace.cash_withdrawal)} / {format_eur(trace.etf_withdrawal)} / "
            f"{format_eur(trace.amazon_withdrawal)}"
        )
        st.caption(f"Unfunded spending: {format_eur(trace.unfunded_spending)}")
    with closing:
        st.markdown("**Closing position**")
        st.caption(f"Cash: {format_eur(trace.closing_cash)}")
        st.caption(f"ETFs: {format_eur(trace.closing_etf_value)}")
        st.caption(f"Amazon: {format_eur(trace.closing_amazon_value)}")
        st.caption(f"Pensions: {format_eur(trace.closing_pension_value)}")
        st.caption(f"Property: {format_eur(trace.closing_property_value)}")
        st.caption(f"Net worth: {format_eur(trace.closing_net_worth)}")


def render_assumptions_used(configuration: WealthOsConfig) -> None:
    """Display validated assumptions without offering editing controls outside Inputs."""
    with st.expander("Assumptions used"):
        st.caption(
            f"Retirement age {configuration.household.planned_retirement_age}; target spending "
            f"{format_eur(configuration.assumptions.target_retirement_income)}; inflation "
            f"{format_percentage(configuration.assumptions.inflation_rate)}."
        )
        st.caption(
            f"ETF growth {format_percentage(configuration.investments.etf_growth_rate)}; Amazon "
            f"growth {format_percentage(configuration.amazon_rsus.annual_growth_rate)}; EUR/USD "
            f"{configuration.amazon_rsus.eur_usd_exchange_rate}; sell on vest: "
            f"{'Yes' if configuration.amazon_rsus.sell_on_vest else 'No'}."
        )
        st.caption("ETF growth is applied once per year using a constant deterministic rate.")
        st.caption("Amazon growth affects the projected USD share price before conversion to EUR.")
        st.caption(
            "Rental income increases annually with inflation. Pension drawdown follows the "
            "configured owner-specific access assumptions."
        )


def render_formula_glossary() -> None:
    """Render concise plain-English formulas for the model's key outputs."""
    st.subheader("How the model works")
    st.markdown(
        "\n".join(
            (
                "- **Net worth** = cash + ETFs + Amazon + pensions + rental property.",
                "- **Liquid assets** = cash + ETFs + Amazon; pensions and property are excluded.",
                "- **Gross recurring income** = rental profit + private pension income + "
                "State Pension.",
                "- **Estimated tax** = Income Tax + USC + PRSI.",
                "- **Net recurring income** = gross recurring income - estimated tax.",
                "- **Liquid funding required** = max(target spending - net recurring income, 0).",
                "- **After-tax rental income** is shown in household context because joint "
                "assessment "
                "does not produce a simple flat tax rate for each income source.",
                "- **Amazon concentration** = Amazon value ÷ net worth.",
                "- **Property net yield** = annual net rent ÷ property value.",
                "- **Retirement ready** = every retirement year is funded by rental income and "
                "liquid assets.",
                "- **Inflation-adjusted spending** = target spending grown annually by inflation.",
                "- **ETF / pension annual growth** = prior balance x (1 + configured annual "
                "growth rate).",
            )
        )
    )


def styled_projection_table(rows: list[dict[str, str]]) -> pd.io.formats.style.Styler:
    """Use theme-compatible status-cell styling without forcing row backgrounds."""
    frame = pd.DataFrame(rows)

    def row_style(row: pd.Series[str]) -> list[str]:
        if row["Status"] == "Unfunded":
            return [
                "font-weight: 700; color: var(--red-color, #DC2626)" if value == "Unfunded" else ""
                for value in row
            ]
        if row["Phase"] == "Retirement":
            return [
                "font-weight: 600; color: var(--primary-color)" if value == "Retirement" else ""
                for value in row
            ]
        return [""] * len(row)

    return frame.style.apply(row_style, axis=1)


__all__ = [
    "ProjectionFilter",
    "filter_projection_years",
    "projection_table_rows",
    "render_assumptions_used",
    "render_calculation_trace",
    "render_formula_glossary",
    "render_pension_cards",
    "render_property_cards",
    "render_readiness_banner",
    "render_retirement_funding",
    "retirement_comparison_rows",
    "retirement_interpretation",
    "styled_projection_table",
]

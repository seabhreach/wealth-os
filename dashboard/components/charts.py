"""Plotly chart builders for the Wealth OS dashboard."""

from collections.abc import Iterable

import plotly.graph_objects as go  # type: ignore[import-untyped]

from engine.reporting import AnnualFinancialStatement
from engine.simulation.projection import ProjectionYear

ASSET_SERIES = (
    ("Cash", "cash_balance", "#64748B"),
    ("ETFs", "etf_value", "#2563EB"),
    ("Amazon", "amazon_value", "#C2410C"),
    ("Pensions", "pension_value", "#0F766E"),
    ("Rental property", "property_value", "#7C3AED"),
)
LIQUID_SERIES = ASSET_SERIES[:3]
TOTAL_NET_WORTH = "#2563EB"
WARNING = "#B45309"
DANGER = "#B91C1C"


def asset_balance_rows(timeline: Iterable[ProjectionYear]) -> list[dict[str, float | int]]:
    """Return chart-ready asset balances without changing projection values."""
    return [
        {
            "calendar_year": year.calendar_year,
            "age": year.age,
            "cash_balance": float(year.cash_balance),
            "etf_value": float(year.etf_value),
            "amazon_value": float(year.amazon_value),
            "pension_value": float(year.pension_value),
            "property_value": float(year.property_value),
            "liquid_assets": float(year.liquid_assets),
            "net_worth": float(year.net_worth),
        }
        for year in timeline
    ]


def net_worth_figure(timeline: tuple[ProjectionYear, ...], retirement_year: int) -> go.Figure:
    """Build a stacked asset chart with total net worth overlaid."""
    figure = _financial_figure(
        "Projected net worth", "Asset balances and total household net worth"
    )
    years = [year.calendar_year for year in timeline]
    for label, attribute, colour in ASSET_SERIES:
        figure.add_trace(
            go.Scatter(
                x=years,
                y=[float(getattr(year, attribute)) for year in timeline],
                name=label,
                mode="lines",
                stackgroup="assets",
                line={"width": 0.6, "color": colour},
                hovertemplate=f"{label}: €%{{y:,.0f}}<extra></extra>",
            )
        )
    figure.add_trace(
        go.Scatter(
            x=years,
            y=[float(year.net_worth) for year in timeline],
            name="Total net worth",
            mode="lines",
            line={"width": 3, "color": TOTAL_NET_WORTH},
            hovertemplate="Total net worth: €%{y:,.0f}<extra></extra>",
        )
    )
    _add_retirement_marker(figure, retirement_year)
    return _finish_currency_chart(figure)


def liquid_assets_figure(timeline: tuple[ProjectionYear, ...], retirement_year: int) -> go.Figure:
    """Build a liquid-asset composition chart."""
    figure = _financial_figure("Liquid assets", "Cash, ETFs, Amazon, and total liquid assets")
    years = [year.calendar_year for year in timeline]
    for label, attribute, colour in LIQUID_SERIES:
        figure.add_trace(
            go.Scatter(
                x=years,
                y=[float(getattr(year, attribute)) for year in timeline],
                name=label,
                mode="lines",
                stackgroup="liquid_assets",
                line={"width": 0.6, "color": colour},
                hovertemplate=f"{label}: €%{{y:,.0f}}<extra></extra>",
            )
        )
    figure.add_trace(
        go.Scatter(
            x=years,
            y=[float(year.liquid_assets) for year in timeline],
            name="Total liquid assets",
            mode="lines",
            line={"width": 3, "color": TOTAL_NET_WORTH},
            hovertemplate="Total liquid assets: €%{y:,.0f}<extra></extra>",
        )
    )
    _add_retirement_marker(figure, retirement_year)
    return _finish_currency_chart(figure)


def liquid_assets_comparison_figure(
    baseline: tuple[ProjectionYear, ...],
    what_if: tuple[ProjectionYear, ...],
    baseline_retirement_year: int,
    what_if_retirement_year: int,
) -> go.Figure:
    """Compare completed baseline and what-if liquid-asset projections."""
    figure = _financial_figure(
        "Liquid assets comparison", "Baseline and temporary retirement-age what-if"
    )
    figure.add_trace(
        go.Scatter(
            x=[year.calendar_year for year in baseline],
            y=[float(year.liquid_assets) for year in baseline],
            name="Baseline",
            mode="lines",
            line={"width": 3, "color": "#64748B"},
            hovertemplate="Baseline liquid assets: €%{y:,.0f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[year.calendar_year for year in what_if],
            y=[float(year.liquid_assets) for year in what_if],
            name="What-if",
            mode="lines",
            line={"width": 3, "color": "#2563EB"},
            hovertemplate="What-if liquid assets: €%{y:,.0f}<extra></extra>",
        )
    )
    _add_retirement_marker(figure, baseline_retirement_year, "Baseline retirement")
    if what_if_retirement_year != baseline_retirement_year:
        _add_retirement_marker(figure, what_if_retirement_year, "What-if retirement")
    return _finish_currency_chart(figure)


def retirement_cashflow_figure(timeline: tuple[ProjectionYear, ...]) -> go.Figure:
    """Build retirement-only spending, income, withdrawal, and shortfall chart."""
    retirement_years = [year for year in timeline if not year.employed]
    figure = _financial_figure("Retirement cashflow", "Annual spending target and funding sources")
    years = [year.calendar_year for year in retirement_years]
    figure.add_trace(
        go.Bar(
            x=years,
            y=[float(year.rental_income) for year in retirement_years],
            name="Rental income",
            marker_color="#0F766E",
            hovertemplate="Rental income: €%{y:,.0f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Bar(
            x=years,
            y=[float(year.withdrawal_amount) for year in retirement_years],
            name="Liquid-asset withdrawals",
            marker_color="#2563EB",
            hovertemplate="Withdrawals: €%{y:,.0f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Bar(
            x=years,
            y=[float(year.unfunded_spending) for year in retirement_years],
            name="Unfunded spending",
            marker_color=DANGER,
            hovertemplate="Unfunded spending: €%{y:,.0f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=years,
            y=[float(year.annual_spending) for year in retirement_years],
            name="Spending target",
            mode="lines+markers",
            line={"width": 3, "color": TOTAL_NET_WORTH},
            hovertemplate="Spending target: €%{y:,.0f}<extra></extra>",
        )
    )
    figure.update_layout(barmode="stack")
    return _finish_currency_chart(figure)


def amazon_concentration_figure(timeline: tuple[ProjectionYear, ...]) -> go.Figure:
    """Build Amazon exposure chart with the draft policy reference line."""
    figure = _financial_figure("Amazon concentration", "Amazon as a share of total net worth")
    figure.add_trace(
        go.Scatter(
            x=[year.calendar_year for year in timeline],
            y=[float(year.amazon_concentration) for year in timeline],
            mode="lines",
            name="Amazon concentration",
            line={"width": 3, "color": "#C2410C"},
            hovertemplate="Amazon concentration: %{y:.1%}<extra></extra>",
        )
    )
    figure.add_hline(
        y=0.20,
        line_dash="dash",
        line_color=WARNING,
        annotation_text="20% draft policy threshold",
        annotation_position="bottom right",
    )
    figure.update_yaxes(tickformat=".0%", rangemode="tozero")
    return figure


def allocation_figure(year: ProjectionYear, title: str) -> go.Figure:
    """Build a consistently ordered household asset-allocation donut chart."""
    labels = [series[0] for series in ASSET_SERIES]
    values = [float(getattr(year, series[1])) for series in ASSET_SERIES]
    colours = [series[2] for series in ASSET_SERIES]
    figure = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            sort=False,
            marker={"colors": colours},
            textinfo="percent",
            hovertemplate="%{label}: €%{value:,.0f} (%{percent})<extra></extra>",
        )
    )
    figure.update_layout(title=title, margin={"l": 8, "r": 8, "t": 42, "b": 8}, height=320)
    return figure


def pension_projection_figure(
    timeline: tuple[ProjectionYear, ...], retirement_year: int
) -> go.Figure:
    """Build one pension projection chart with a line for each configured pension."""
    figure = _financial_figure("Pension projection", "Pension values remain invested in this MVP")
    owners = tuple(balance.owner for balance in timeline[0].pension_values)
    colours = ("#0F766E", "#14B8A6", "#2DD4BF")
    for index, owner in enumerate(owners):
        figure.add_trace(
            go.Scatter(
                x=[year.calendar_year for year in timeline],
                y=[float(year.pension_values[index].value) for year in timeline],
                name=f"{owner} pension",
                mode="lines",
                line={"width": 3, "color": colours[index % len(colours)]},
                hovertemplate=f"{owner} pension: €%{{y:,.0f}}<extra></extra>",
            )
        )
    figure.add_trace(
        go.Scatter(
            x=[year.calendar_year for year in timeline],
            y=[float(year.pension_value) for year in timeline],
            name="Total pensions",
            mode="lines",
            line={"width": 3, "color": TOTAL_NET_WORTH, "dash": "dash"},
            hovertemplate="Total pensions: €%{y:,.0f}<extra></extra>",
        )
    )
    _add_retirement_marker(figure, retirement_year)
    return _finish_currency_chart(figure)


def spending_funding_figure(timeline: tuple[ProjectionYear, ...]) -> go.Figure:
    """Show each existing retirement-spending funding source as a stacked bar."""
    retirement_years = [year for year in timeline if not year.employed]
    figure = _financial_figure("Spending funding composition", "How retirement spending is funded")
    years = [year.calendar_year for year in retirement_years]
    for label, values, colour in (
        ("Rental income", [year.rental_income for year in retirement_years], "#0F766E"),
        ("State Pension", [0 for _ in retirement_years], "#475569"),
        ("Private pension income", [0 for _ in retirement_years], "#0F766E"),
        ("Cash used", [year.cash_withdrawal for year in retirement_years], "#64748B"),
        ("ETF units sold", [year.etf_withdrawal for year in retirement_years], "#2563EB"),
        ("Amazon shares sold", [year.amazon_withdrawal for year in retirement_years], "#C2410C"),
        ("Unfunded spending", [year.unfunded_spending for year in retirement_years], DANGER),
    ):
        figure.add_trace(
            go.Bar(
                x=years,
                y=[float(value) for value in values],
                name=label,
                marker_color=colour,
                hovertemplate=f"{label}: €%{{y:,.0f}}<extra></extra>",
            )
        )
    figure.update_layout(barmode="stack")
    return _finish_currency_chart(figure)


def selected_funding_figure(statement: AnnualFinancialStatement) -> go.Figure:
    """Show one selected year's spending funding sources as a readable horizontal stack."""
    funding = statement.funding
    figure = _financial_figure(
        f"Funding in {statement.calendar_year}", "Money available for that year's spending"
    )
    for label, value, colour in (
        ("Gross rental profit", funding.rental_income, "#0F766E"),
        ("Gross State Pension", funding.state_pension, "#475569"),
        ("Gross private pension income", funding.private_pension_income, "#14B8A6"),
        (
            "Estimated tax",
            -funding.estimated_income_tax - funding.estimated_usc - funding.estimated_prsi,
            "#DC2626",
        ),
        ("Cash used", funding.cash_used, "#64748B"),
        ("ETF units sold", funding.etf_units_sold, "#2563EB"),
        ("Amazon shares sold", funding.amazon_shares_sold, "#C2410C"),
        ("Unfunded amount", funding.unfunded_amount, DANGER),
    ):
        figure.add_trace(
            go.Bar(
                y=["Funding"],
                x=[float(value)],
                name=label,
                orientation="h",
                marker_color=colour,
                hovertemplate=f"{label}: €%{{x:,.0f}}<extra></extra>",
            )
        )
    figure.add_vline(
        x=float(funding.retirement_spending),
        line_dash="dot",
        line_color=TOTAL_NET_WORTH,
        annotation_text="Spending target",
    )
    figure.update_layout(barmode="stack", height=260)
    return _finish_currency_chart(figure)


def tax_gross_to_net_figure(timeline: tuple[ProjectionYear, ...]) -> go.Figure:
    """Show gross income, tax, net income, and liquid funding as separate annual lines."""
    years = [year.calendar_year for year in timeline if not year.employed]
    rows = [year for year in timeline if not year.employed]
    figure = _financial_figure("Retirement income after estimated tax", "Annual EUR")
    for label, attribute, colour in (
        ("Gross recurring income", "gross_recurring_income", "#0F766E"),
        ("Estimated tax", "total_estimated_tax", "#B91C1C"),
        ("Net recurring income", "net_recurring_income", "#2563EB"),
        ("Liquid-asset funding", "withdrawal_amount", "#64748B"),
    ):
        figure.add_trace(
            go.Bar(
                x=years,
                y=[float(getattr(year, attribute)) for year in rows],
                name=label,
                marker_color=colour,
                hovertemplate=f"{label}: €%{{y:,.0f}}<extra></extra>",
            )
        )
    figure.update_layout(barmode="group")
    return _finish_currency_chart(figure)


def tax_composition_figure(timeline: tuple[ProjectionYear, ...]) -> go.Figure:
    """Show non-stacked estimated tax components over retirement years."""
    rows = [year for year in timeline if not year.employed]
    figure = _financial_figure("Estimated tax composition", "Annual EUR")
    for label, attribute, colour in (
        ("Income Tax", "estimated_income_tax", "#7C3AED"),
        ("USC", "estimated_usc", "#B45309"),
        ("PRSI", "estimated_prsi", "#BE123C"),
    ):
        figure.add_trace(
            go.Bar(
                x=[year.calendar_year for year in rows],
                y=[float(getattr(year, attribute)) for year in rows],
                name=label,
                marker_color=colour,
                hovertemplate=f"{label}: €%{{y:,.0f}}<extra></extra>",
            )
        )
    figure.update_layout(barmode="group")
    return _finish_currency_chart(figure)


def effective_tax_rate_figure(timeline: tuple[ProjectionYear, ...]) -> go.Figure:
    """Show the household effective tax rate without mixing it with EUR series."""
    rows = [year for year in timeline if not year.employed]
    figure = _financial_figure("Effective estimated tax rate", "Percentage")
    figure.add_trace(
        go.Scatter(
            x=[year.calendar_year for year in rows],
            y=[float(year.effective_tax_rate * 100) for year in rows],
            name="Effective tax rate",
            mode="lines+markers",
            line={"color": "#2563EB", "width": 3},
            hovertemplate="Effective tax rate: %{y:.1f}%<extra></extra>",
        )
    )
    figure.update_yaxes(ticksuffix="%", rangemode="tozero")
    return figure


def key_dates_figure(
    current_year: ProjectionYear, retirement_year: ProjectionYear, final_year: ProjectionYear
) -> go.Figure:
    """Compare liquid assets, pensions, and property at the key planning dates."""
    figure = _financial_figure(
        "Asset values at key dates", "Today, retirement, and life expectancy"
    )
    dates = ("Today", "Retirement", "Life expectancy")
    for label, attribute, colour in (
        ("Liquid assets", "liquid_assets", "#2563EB"),
        ("Pensions", "pension_value", "#0F766E"),
        ("Property", "property_value", "#7C3AED"),
    ):
        figure.add_trace(
            go.Bar(
                x=dates,
                y=[
                    float(getattr(year, attribute))
                    for year in (current_year, retirement_year, final_year)
                ],
                name=label,
                marker_color=colour,
                hovertemplate=f"{label}: €%{{y:,.0f}}<extra></extra>",
            )
        )
    figure.update_layout(barmode="group")
    return _finish_currency_chart(figure)


def rental_projection_figure(timeline: tuple[ProjectionYear, ...]) -> go.Figure:
    """Show total rental property value and annual net rental income over time."""
    figure = _financial_figure("Rental property projection", "Property value and annual net rent")
    years = [year.calendar_year for year in timeline]
    figure.add_trace(
        go.Scatter(
            x=years,
            y=[float(year.property_value) for year in timeline],
            name="Property value",
            mode="lines",
            line={"width": 3, "color": "#7C3AED"},
            hovertemplate="Property value: €%{y:,.0f}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=years,
            y=[float(year.rental_income) for year in timeline],
            name="Annual net rent",
            mode="lines",
            line={"width": 3, "color": "#0F766E"},
            hovertemplate="Annual net rent: €%{y:,.0f}<extra></extra>",
        )
    )
    return _finish_currency_chart(figure)


def _financial_figure(title: str, subtitle: str) -> go.Figure:
    """Create a restrained Plotly figure with shared dashboard styling."""
    figure = go.Figure()
    figure.update_layout(
        title={"text": f"{title}<br><sup>{subtitle}</sup>", "x": 0.0},
        hovermode="x unified",
        margin={"l": 8, "r": 8, "t": 58, "b": 8},
        legend={"orientation": "h", "y": -0.2},
        autosize=True,
        height=360,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    figure.update_xaxes(showgrid=False, title=None)
    figure.update_yaxes(gridcolor="rgba(128, 128, 128, 0.25)", zeroline=False, title=None)
    return figure


def _add_retirement_marker(
    figure: go.Figure, retirement_year: int, label: str = "Retirement"
) -> None:
    """Annotate the common retirement starting point."""
    figure.add_vline(
        x=retirement_year,
        line_dash="dot",
        line_color=WARNING,
        annotation_text=label,
        annotation_position="top left",
    )


def _finish_currency_chart(figure: go.Figure) -> go.Figure:
    """Apply consistent EUR axes to a financial chart."""
    figure.update_yaxes(tickprefix="€", tickformat=".2s", rangemode="tozero")
    return figure

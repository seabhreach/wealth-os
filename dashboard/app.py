"""Full-width Streamlit presentation for the Wealth OS deterministic projection."""

from collections.abc import MutableMapping
from pathlib import Path
from typing import cast

import streamlit as st

from dashboard.components.cards import render_kpi_grid
from dashboard.components.charts import (
    allocation_figure,
    amazon_concentration_figure,
    effective_tax_rate_figure,
    key_dates_figure,
    liquid_assets_comparison_figure,
    liquid_assets_figure,
    net_worth_figure,
    pension_projection_figure,
    rental_projection_figure,
    retirement_cashflow_figure,
    selected_funding_figure,
    spending_funding_figure,
    tax_composition_figure,
    tax_gross_to_net_figure,
)
from dashboard.components.formatting import (
    format_compact_eur,
    format_year_and_age,
    readiness_status,
)
from dashboard.components.forms import render_input_context, render_inputs_page
from dashboard.components.sections import (
    ProjectionFilter,
    filter_projection_years,
    projection_table_rows,
    render_amazon_audit,
    render_annual_financial_statement,
    render_assumptions_used,
    render_before_after_tax_comparison,
    render_calculation_trace,
    render_formula_glossary,
    render_pension_cards,
    render_property_cards,
    render_readiness_banner,
    render_retirement_cash_origin,
    render_retirement_funding,
    render_tax_statement,
    retirement_comparison_rows,
    retirement_interpretation,
    styled_projection_table,
)
from dashboard.navigation import PAGES, apply_pending_page, request_page
from dashboard.state import (
    PAGE_KEY,
    WHAT_IF_RETIREMENT_AGE_KEY,
    active_configuration,
    active_form_data,
    configuration_source,
    initialise_state,
    replace_configuration,
    reset_what_if_retirement_age,
    set_what_if_retirement_age,
    what_if_retirement_age,
)
from dashboard.what_if import what_if_label, with_retirement_age
from engine.config import load_configuration
from engine.config.models import WealthOsConfig
from engine.reporting import (
    RetirementReadinessSummary,
    ScenarioResult,
    advisor_insights,
    annual_calculation_trace,
    annual_financial_statement,
    annual_tax_statement,
    before_after_tax_comparison,
    compare_retirement_readiness,
    ownership_tax_comparisons,
    preserved_wealth_warning,
    retirement_age_explorer,
    retirement_funding_narrative,
    run_default_scenarios,
    sensitivity_analysis,
    summarize_rental_properties,
    summarize_retirement_readiness,
    summarize_rsu_audit,
    tax_advisor_insights,
)
from engine.simulation import PropertySimulationError, project_annually
from engine.simulation.projection import ProjectionYear

EXAMPLE_CONFIGURATION = Path(__file__).parents[1] / "data" / "example_household.yaml"
TABLE_FILTERS: tuple[ProjectionFilter, ...] = (
    "All years",
    "Working years",
    "Retirement years",
    "Unfunded years",
)
PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


def main() -> None:
    """Render the current session's configuration through the unchanged simulation engine."""
    st.set_page_config(page_title="Wealth OS", page_icon="WO", layout="wide")
    state = _state()
    default_configuration = load_configuration(EXAMPLE_CONFIGURATION.read_text(encoding="utf-8"))
    initialise_state(state, default_configuration, "Example household baseline")
    apply_pending_page(state)
    configuration = active_configuration(state)
    source = configuration_source(state)

    try:
        projection = project_annually(configuration)
    except PropertySimulationError as error:
        st.error(f"Property simulation failed: {error}")
        return

    baseline_projection = projection
    current_year = baseline_projection[0]
    final_year = baseline_projection[-1]
    page = _render_header(configuration.household.name, current_year, final_year, source)

    if page == "Inputs":
        _render_inputs_workflow(configuration, source)
        return

    selected_retirement_age = _render_what_if_control(configuration, page)
    active_configuration_for_projection = with_retirement_age(
        configuration, selected_retirement_age
    )
    active_projection = (
        baseline_projection
        if selected_retirement_age == configuration.household.planned_retirement_age
        else project_annually(active_configuration_for_projection)
    )
    active_retirement_year = next(year for year in active_projection if not year.employed)
    what_if_notice = what_if_label(configuration, selected_retirement_age)
    if what_if_notice is not None:
        st.caption(what_if_notice)

    baseline_readiness = summarize_retirement_readiness(baseline_projection)
    readiness = summarize_retirement_readiness(active_projection)
    _render_page(
        page,
        active_projection,
        readiness,
        active_projection[0],
        active_retirement_year,
        active_projection[-1],
        active_configuration_for_projection,
        baseline_projection,
        baseline_readiness,
    )


def _render_header(
    household_name: str,
    current_year: ProjectionYear,
    final_year: ProjectionYear,
    source: str,
) -> str:
    """Render a compact header with full-width top-level navigation."""
    st.markdown("## Wealth OS")
    title, action = st.columns((5, 1))
    title.markdown(f"**{household_name}** · {source}")
    title.caption(
        "Projection period: "
        f"{format_year_and_age(current_year.calendar_year, current_year.age)} to "
        f"{format_year_and_age(final_year.calendar_year, final_year.age)}"
    )
    if action.button("Edit inputs", use_container_width=True):
        request_page(_state(), "Inputs")
        st.rerun()
    page = st.radio(
        "Navigation",
        options=PAGES,
        key=PAGE_KEY,
        horizontal=True,
        label_visibility="collapsed",
    )
    return page


def _render_inputs_workflow(configuration: WealthOsConfig, source: str) -> None:
    """Render input-page-only controls and switch to Overview after valid submission."""
    state = _state()
    imported_configuration = render_input_context(configuration, source)
    if imported_configuration is not None:
        replace_configuration(state, imported_configuration, "Imported YAML")
        st.rerun()
    submitted_configuration, form_data = render_inputs_page(active_form_data(state))
    if submitted_configuration is None:
        state["wealth_os_form_data"] = form_data
        return
    replace_configuration(state, submitted_configuration, "Structured form inputs")
    request_page(state, "Overview")
    st.rerun()


def _render_what_if_control(configuration: WealthOsConfig, page: str) -> int:
    """Render a session-only retirement-age override without mutating saved configuration."""
    state = _state()
    baseline_age = configuration.household.planned_retirement_age
    selected_age = what_if_retirement_age(state, configuration)
    if page not in {"Overview", "Retirement"}:
        return selected_age

    maximum_age = max(
        configuration.household.current_age,
        min(70, configuration.household.life_expectancy),
    )
    with st.container(border=True):
        st.caption("Retirement age what-if")
        selected_age = st.slider(
            "Temporary retirement age",
            min_value=configuration.household.current_age,
            max_value=maximum_age,
            key=WHAT_IF_RETIREMENT_AGE_KEY,
        )
        quick_choices = st.columns(4)
        quick_choices[0].button(
            "Retire now",
            use_container_width=True,
            on_click=set_what_if_retirement_age,
            args=(state, configuration.household.current_age),
        )
        quick_choices[1].button(
            "Baseline",
            use_container_width=True,
            on_click=reset_what_if_retirement_age,
            args=(state, configuration),
        )
        quick_choices[2].button(
            "+1 year",
            disabled=baseline_age + 1 > maximum_age,
            use_container_width=True,
            on_click=set_what_if_retirement_age,
            args=(state, baseline_age + 1),
        )
        quick_choices[3].button(
            "+3 years",
            disabled=baseline_age + 3 > maximum_age,
            use_container_width=True,
            on_click=set_what_if_retirement_age,
            args=(state, baseline_age + 3),
        )
    return selected_age


def _render_page(
    page: str,
    projection: tuple[ProjectionYear, ...],
    readiness: RetirementReadinessSummary,
    current_year: ProjectionYear,
    retirement_year: ProjectionYear,
    final_year: ProjectionYear,
    configuration: WealthOsConfig,
    baseline_projection: tuple[ProjectionYear, ...],
    baseline_readiness: RetirementReadinessSummary,
) -> None:
    """Render one full-width page at a time."""
    if page == "Overview":
        _render_overview(projection, readiness, current_year, retirement_year)
    elif page == "Retirement":
        _render_retirement(
            projection,
            readiness,
            retirement_year,
            final_year,
            baseline_projection,
            baseline_readiness,
            configuration,
        )
    elif page == "Assets":
        _render_assets(projection, current_year, retirement_year, final_year, configuration)
    elif page == "Cashflow":
        _render_cashflow(projection)
    elif page == "Advisor":
        _render_advisor(configuration)
    else:
        _render_details(projection, configuration)


def _render_overview(
    projection: tuple[ProjectionYear, ...],
    readiness: RetirementReadinessSummary,
    current_year: ProjectionYear,
    retirement_year: ProjectionYear,
) -> None:
    """Render the first-screen decision metrics and one primary chart."""
    status_label, _ = readiness_status(readiness.retirement_ready)
    render_kpi_grid(
        (
            (
                "Plan status",
                status_label,
                "Funded through life expectancy using recurring income after estimated tax and "
                "liquid assets.",
            ),
            (
                "Current net worth",
                format_compact_eur(current_year.net_worth),
                "Cash, ETFs, Amazon, pensions, and rental property; the family home is excluded.",
            ),
            (
                "Liquid assets",
                format_compact_eur(current_year.liquid_assets),
                "Cash, ETFs, and Amazon only; pensions and property are excluded.",
            ),
            ("Years to retirement", str(readiness.retirement_age - current_year.age), None),
            (
                "Final net worth",
                format_compact_eur(projection[-1].net_worth),
                "Pensions and property may remain high because this model does not sell or draw "
                "them down.",
            ),
            (
                "Required withdrawal",
                format_compact_eur(readiness.first_retirement_required_withdrawal),
                "Target spending minus recurring income after estimated tax, with a minimum "
                "of zero.",
            ),
        )
    )
    render_readiness_banner(readiness)
    st.caption(
        "What drives this result: net rent, pension drawdown, and State Pension reduce spending "
        "needs; cash, ETFs, then Amazon fund any remaining gap."
    )
    warning = preserved_wealth_warning(projection[-1])
    if warning is not None:
        st.warning(warning)
    _plot(net_worth_figure(projection, retirement_year.calendar_year))


def _render_retirement(
    projection: tuple[ProjectionYear, ...],
    readiness: RetirementReadinessSummary,
    retirement_year: ProjectionYear,
    final_year: ProjectionYear,
    baseline_projection: tuple[ProjectionYear, ...],
    baseline_readiness: RetirementReadinessSummary,
    configuration: WealthOsConfig,
) -> None:
    """Render retirement funding outcomes sourced from the existing reporting summary."""
    st.subheader("Retirement outlook")
    render_readiness_banner(readiness)
    st.markdown(retirement_interpretation(readiness, final_year.age))
    render_kpi_grid(
        (
            ("First retirement year", str(readiness.first_retirement_year), None),
            (
                "Spending target",
                format_compact_eur(readiness.first_retirement_spending_target),
                None,
            ),
            ("Rental income", format_compact_eur(readiness.first_retirement_rental_income), None),
            (
                "Required withdrawals",
                format_compact_eur(readiness.first_retirement_required_withdrawal),
                None,
            ),
            ("First unfunded year", str(readiness.first_unfunded_year or "None"), None),
            (
                "Liquid assets at life expectancy",
                format_compact_eur(readiness.liquid_assets_at_life_expectancy),
                None,
            ),
            (
                "Pensions preserved",
                format_compact_eur(readiness.pension_value_at_life_expectancy),
                None,
            ),
            (
                "Property preserved",
                format_compact_eur(readiness.property_value_at_life_expectancy),
                None,
            ),
        )
    )
    retirement_start = format_year_and_age(retirement_year.calendar_year, retirement_year.age)
    st.caption(f"Retirement starts at {retirement_start}.")
    render_retirement_funding(retirement_year)
    retirement_years = tuple(year for year in projection if not year.employed)
    selected_statement_year = st.selectbox(
        "Retirement year to inspect",
        options=[year.calendar_year for year in retirement_years],
        key="retirement_statement_year",
    )
    statement = annual_financial_statement(projection, configuration, selected_statement_year)
    render_annual_financial_statement(statement, retirement_funding_narrative(statement))
    tax_statement = annual_tax_statement(projection, configuration, selected_statement_year)
    render_tax_statement(tax_statement)
    if configuration.tax.enabled:
        _plot(tax_gross_to_net_figure(projection))
        _plot(tax_composition_figure(projection))
        _plot(effective_tax_rate_figure(projection))
    else:
        st.info("Tax modelling disabled. Enable it on Inputs to see estimated tax charts.")
    render_before_after_tax_comparison(before_after_tax_comparison(configuration))
    audit = summarize_rsu_audit(projection, configuration)
    render_retirement_cash_origin(audit)
    _plot(selected_funding_figure(statement))
    _plot(spending_funding_figure(projection))
    st.caption(
        "Rental income is annual net rent before personal tax. Pension drawdown follows the "
        "configured owner-specific access assumptions."
    )
    comparison = compare_retirement_readiness(baseline_readiness, readiness)
    if comparison.baseline_age != comparison.what_if_age:
        st.subheader("Baseline comparison")
        st.caption(comparison.interpretation)
        st.dataframe(
            retirement_comparison_rows(comparison), hide_index=True, use_container_width=True
        )
        baseline_retirement_year = next(year for year in baseline_projection if not year.employed)
        _plot(
            liquid_assets_comparison_figure(
                baseline_projection,
                projection,
                baseline_retirement_year.calendar_year,
                retirement_year.calendar_year,
            )
        )


def _render_assets(
    projection: tuple[ProjectionYear, ...],
    current_year: ProjectionYear,
    retirement_year: ProjectionYear,
    final_year: ProjectionYear,
    configuration: WealthOsConfig,
) -> None:
    """Render asset charts and supporting property and pension information vertically."""
    st.subheader("Asset projection")
    _plot(liquid_assets_figure(projection, retirement_year.calendar_year))
    _plot(key_dates_figure(current_year, retirement_year, final_year))
    _plot(amazon_concentration_figure(projection))
    st.caption("The 20% line is a draft planning-policy threshold, not financial advice.")
    _plot(pension_projection_figure(projection, retirement_year.calendar_year))
    render_pension_cards(current_year, retirement_year, final_year)
    _plot(rental_projection_figure(projection))
    render_property_cards(summarize_rental_properties(configuration))
    st.subheader("Asset allocation")
    _plot(allocation_figure(current_year, "Current asset allocation"))
    _plot(allocation_figure(retirement_year, "Retirement-date asset allocation"))


def _render_cashflow(projection: tuple[ProjectionYear, ...]) -> None:
    """Render retirement cashflow and spending-funding composition."""
    st.subheader("Income and withdrawals")
    _plot(retirement_cashflow_figure(projection))
    _plot(spending_funding_figure(projection))
    st.caption(
        "Rental income reduces the spending gap before withdrawals from cash, ETFs, and retained "
        "Amazon shares."
    )


@st.cache_data(show_spinner=False)
def _advisor_results(configuration: WealthOsConfig) -> tuple[ScenarioResult, ...]:
    """Cache deterministic Advisor Mode outputs for the unchanged validated configuration."""
    return run_default_scenarios(configuration)


def _render_advisor(configuration: WealthOsConfig) -> None:
    """Render reporting-only strategy comparisons without placing business rules in Streamlit."""
    st.subheader("Advisor Mode")
    st.caption(
        "Advisor Mode compares deterministic planning scenarios. It is not regulated financial "
        "advice."
    )
    results = _advisor_results(configuration)
    _render_advisor_summary(results)
    _render_advisor_table(results)
    st.subheader("Key trade-offs")
    for insight in advisor_insights(results):
        st.caption(insight)
    st.subheader("Tax-aware observations")
    for insight in tax_advisor_insights(configuration):
        st.caption(insight)
    _render_ownership_tax_comparison(configuration)
    st.subheader("Recommended actions to investigate")
    st.caption(
        "Review the retirement-age, RSU-policy, planned-property, and spending scenarios that "
        "produce the trade-offs shown above. This is a planning prompt, not a recommendation."
    )
    _render_age_explorer(configuration)
    _render_sensitivity(configuration)


def _render_ownership_tax_comparison(configuration: WealthOsConfig) -> None:
    """Render immutable planning-only rental ownership tax scenarios."""
    st.subheader("Rental ownership tax comparison")
    if not configuration.tax.enabled:
        st.info("Tax modelling disabled. Enable it on Inputs to compare ownership assumptions.")
        return
    if not configuration.rental_properties:
        st.info("No rental property is configured for an ownership comparison.")
        return
    selected_property = st.selectbox(
        "Property",
        options=[property_config.name for property_config in configuration.rental_properties],
    )
    comparisons = ownership_tax_comparisons(configuration, selected_property)
    rows = [
        {
            "Ownership assumption": item.label,
            "Rental profit by person": "; ".join(
                f"{person}: {format_compact_eur(value)}"
                for person, value in item.rental_profit_by_person
            ),
            "Income Tax": format_compact_eur(item.income_tax),
            "USC": format_compact_eur(item.usc),
            "PRSI": format_compact_eur(item.prsi),
            "Total estimated tax": format_compact_eur(item.total_tax),
            "After-tax rental income*": format_compact_eur(item.after_tax_rental_income),
            "Change vs baseline": format_compact_eur(item.tax_change_vs_baseline),
            "Final liquid assets": format_compact_eur(item.liquid_assets_at_life_expectancy),
            "Final net worth": format_compact_eur(item.final_net_worth),
        }
        for item in comparisons
    ]
    st.dataframe(rows, hide_index=True, use_container_width=True)
    if comparisons:
        difference = max(item.total_tax for item in comparisons) - min(
            item.total_tax for item in comparisons
        )
        st.caption(
            "The modelled first-year household tax difference between the displayed ownership "
            f"assumptions is approximately {format_compact_eur(difference)}."
        )
    st.caption(
        "*After-tax rental income is shown in household context: joint assessment means tax is "
        "not always meaningfully separable into a simple flat tax on rent. Ownership assumptions "
        "must reflect actual legal and beneficial ownership. This comparison is for planning only "
        "and is not a tax-structuring recommendation."
    )


def _render_advisor_summary(results: tuple[ScenarioResult, ...]) -> None:
    """Render evidence-backed trade-off cards from completed scenario metrics."""
    metrics = tuple(result.metrics for result in results)
    funded = tuple(metric for metric in metrics if metric.retirement_ready)
    earliest = min(funded, key=lambda metric: metric.retirement_age) if funded else None
    most_liquid = max(metrics, key=lambda metric: metric.liquid_assets_at_life_expectancy)
    least_concentrated = min(metrics, key=lambda metric: metric.maximum_amazon_concentration)
    highest_wealth = max(metrics, key=lambda metric: metric.final_net_worth)
    render_kpi_grid(
        (
            (
                "Earliest funded retirement",
                str(earliest.retirement_age) if earliest else "None",
                "Tested scenarios only.",
            ),
            (
                "Highest final liquidity",
                most_liquid.scenario.name,
                format_compact_eur(most_liquid.liquid_assets_at_life_expectancy),
            ),
            (
                "Lowest Amazon exposure",
                least_concentrated.scenario.name,
                f"{least_concentrated.maximum_amazon_concentration:.1%}",
            ),
            (
                "Highest final net worth",
                highest_wealth.scenario.name,
                "Higher wealth is not automatically preferable.",
            ),
        )
    )


def _render_advisor_table(results: tuple[ScenarioResult, ...]) -> None:
    """Render the concise scenario metric comparison using completed reporting results."""
    rows = [
        {
            "Scenario": metric.scenario.name,
            "Retirement age": metric.retirement_age,
            "Plan status": "Funded" if metric.retirement_ready else "Funding gap",
            "First unfunded year": str(metric.first_unfunded_year or "None"),
            "Liquid assets at retirement": format_compact_eur(metric.liquid_assets_at_retirement),
            "Liquid assets at life expectancy": format_compact_eur(
                metric.liquid_assets_at_life_expectancy
            ),
            "Final net worth": format_compact_eur(metric.final_net_worth),
            "Maximum Amazon exposure": f"{metric.maximum_amazon_concentration:.1%}",
            "Key trade-off": "Deterministic comparison; review liquidity and concentration "
            "together.",
        }
        for metric in (result.metrics for result in results)
    ]
    st.subheader("Scenario comparison")
    st.dataframe(rows, hide_index=True, use_container_width=True)


def _render_age_explorer(configuration: WealthOsConfig) -> None:
    """Render a compact age explorer table from reporting-only scenario execution."""
    st.subheader("Retirement age explorer")
    rows = [
        {
            "Retirement age": result.metrics.retirement_age,
            "Final liquid assets": format_compact_eur(
                result.metrics.liquid_assets_at_life_expectancy
            ),
            "Funding outcome": "Funded through life expectancy"
            if result.metrics.retirement_ready
            else f"Unfunded in {result.metrics.first_unfunded_year}",
        }
        for result in retirement_age_explorer(configuration)
    ]
    st.dataframe(rows, hide_index=True, use_container_width=True)


def _render_sensitivity(configuration: WealthOsConfig) -> None:
    """Render fixed one-variable sensitivity outputs derived from completed scenarios."""
    st.subheader("Sensitivity analysis")
    rows = [
        {
            "Variable": result.label,
            "Value": f"{result.value:.1%}"
            if "growth" in result.variable.lower() or result.variable == "Inflation"
            else format_compact_eur(result.value),
            "Plan status": "Funded" if result.metrics.retirement_ready else "Funding gap",
            "First unfunded year": str(result.metrics.first_unfunded_year or "None"),
            "Final liquid assets": format_compact_eur(
                result.metrics.liquid_assets_at_life_expectancy
            ),
            "Final net worth": format_compact_eur(result.metrics.final_net_worth),
        }
        for result in sensitivity_analysis(configuration)
    ]
    st.dataframe(rows, hide_index=True, use_container_width=True)


def _render_details(projection: tuple[ProjectionYear, ...], configuration: WealthOsConfig) -> None:
    """Render optional annual detail and the concise limitations panel."""
    st.subheader("Detailed breakdown")
    selected_filter = st.selectbox("Show", options=TABLE_FILTERS)
    rows = projection_table_rows(filter_projection_years(projection, selected_filter))
    if selected_filter == "Unfunded years" and not rows:
        st.success("No unfunded years in this projection.")
    table = styled_projection_table(rows)
    st.dataframe(table, hide_index=True, use_container_width=True)
    st.download_button(
        "Download filtered projection as CSV",
        data=table.data.to_csv(index=False).encode("utf-8"),
        file_name="wealth-os-projection.csv",
        mime="text/csv",
    )
    selected_year = st.selectbox(
        "Year to trace", options=[year.calendar_year for year in projection], key="trace_year"
    )
    render_calculation_trace(annual_calculation_trace(projection, configuration, selected_year))
    st.subheader("Selected-year tax calculation")
    render_tax_statement(annual_tax_statement(projection, configuration, selected_year))
    _render_tax_assumptions(configuration)
    render_amazon_audit(summarize_rsu_audit(projection, configuration))
    render_assumptions_used(configuration)
    render_formula_glossary()
    st.divider()
    st.subheader("Model limitations")
    st.warning(
        "Planning estimate only. No CGT, ETF deemed disposal, Residential Premises Rental Income "
        "Relief, pension lump-sum tax treatment, filing-level deductions, or relief claims are "
        "modelled. Future tax thresholds are indexed assumptions, not forecasts."
    )


def _render_tax_assumptions(configuration: WealthOsConfig) -> None:
    """Render configuration facts; no rates or tax calculations are recreated in Streamlit."""
    st.subheader("Tax assumptions")
    if not configuration.tax.enabled:
        st.info("Tax modelling disabled. Gross recurring income is used for retirement spending.")
        return
    st.dataframe(
        [
            {"Assumption": "Rules file", "Value": configuration.tax.rules_file},
            {"Assumption": "Assessment basis", "Value": configuration.tax.assessment_basis},
            {"Assumption": "Assessable spouse", "Value": configuration.tax.assessable_spouse},
            {
                "Assumption": "Threshold indexation",
                "Value": "Enabled"
                if configuration.tax.index_future_rules_with_inflation
                else "Disabled",
            },
            {
                "Assumption": "Inflation assumption",
                "Value": f"{configuration.assumptions.inflation_rate:.1%}",
            },
            {
                "Assumption": "Pension PRSI policy",
                "Value": "Enabled" if configuration.tax.pension_prsi_enabled else "Disabled",
            },
            {
                "Assumption": "Rental PRSI policy",
                "Value": "Enabled" if configuration.tax.rental_prsi_enabled else "Disabled",
            },
        ],
        hide_index=True,
        use_container_width=True,
    )


def _plot(figure: object) -> None:
    """Render a container-width Plotly chart with responsive browser resizing enabled."""
    st.plotly_chart(figure, use_container_width=True, config=PLOTLY_CONFIG)


def _state() -> MutableMapping[str, object]:
    """Expose Streamlit session state through the narrow mapping contract used by this app."""
    return cast(MutableMapping[str, object], st.session_state)


if __name__ == "__main__":
    main()

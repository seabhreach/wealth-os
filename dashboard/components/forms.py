"""Structured Streamlit inputs for the existing Wealth OS configuration schema."""

from copy import deepcopy
from decimal import Decimal

import streamlit as st
from pydantic import ValidationError

from dashboard.inputs import (
    FormData,
    add_pension,
    add_rental_property,
    configuration_to_yaml,
    form_data_to_configuration,
    percentage_to_rate,
    rate_to_percentage,
    remove_pension,
    remove_rental_property,
    validation_error_messages,
)
from dashboard.navigation import configuration_status
from engine.config import ConfigurationError, load_configuration
from engine.config.models import WealthOsConfig


def render_inputs_page(form_data: FormData) -> tuple[WealthOsConfig | None, FormData]:
    """Render editable MVP inputs and validate only when the form is submitted."""
    st.subheader("Inputs")
    st.caption("Update the plan through this form. Calculations run only after submission.")
    _render_collection_controls(form_data)

    with st.form("wealth_os_inputs"):
        submitted_data = _render_form_fields(form_data)
        submitted = st.form_submit_button("Run projection", type="primary")
    if not submitted:
        return None, form_data

    try:
        return form_data_to_configuration(submitted_data), submitted_data
    except ValidationError as error:
        st.error(
            "Please correct the highlighted configuration values and run the projection again."
        )
        for field, message in validation_error_messages(error).items():
            st.caption(f"{field}: {message}")
        return None, submitted_data


def _render_collection_controls(form_data: FormData) -> None:
    """Render explicit add/remove controls for variable-length collections."""
    pension_controls, property_controls = st.columns(2)
    with pension_controls:
        st.markdown("**Pensions**")
        add_pension_clicked = st.button("Add pension", use_container_width=True)
        if add_pension_clicked:
            st.session_state["wealth_os_form_data"] = add_pension(form_data)
            st.rerun()
        for index, pension in enumerate(form_data["pensions"]):
            if st.button(
                f"Remove {pension['name']}",
                key=f"remove_pension_{index}",
                disabled=len(form_data["pensions"]) <= 1,
            ):
                st.session_state["wealth_os_form_data"] = remove_pension(form_data, index)
                st.rerun()
    with property_controls:
        st.markdown("**Rental properties**")
        can_add_property = len(form_data["rental_properties"]) < 3
        add_property_clicked = st.button(
            "Add property", disabled=not can_add_property, use_container_width=True
        )
        if add_property_clicked:
            st.session_state["wealth_os_form_data"] = add_rental_property(form_data)
            st.rerun()
        for index, property_input in enumerate(form_data["rental_properties"]):
            if st.button(f"Remove {property_input['name']}", key=f"remove_property_{index}"):
                st.session_state["wealth_os_form_data"] = remove_rental_property(form_data, index)
                st.rerun()
            owners = property_input.get("owners", [])
            if isinstance(owners, list):
                if st.button(f"Add owner to {property_input['name']}", key=f"add_owner_{index}"):
                    updated = deepcopy(form_data)
                    updated["rental_properties"][index]["owners"].append(
                        {"person": "Owner", "share": Decimal("0")}
                    )
                    st.session_state["wealth_os_form_data"] = updated
                    st.rerun()
                for owner_index, owner in enumerate(owners):
                    if st.button(
                        f"Remove owner {owner['person']}", key=f"remove_owner_{index}_{owner_index}"
                    ):
                        updated = deepcopy(form_data)
                        updated["rental_properties"][index]["owners"].pop(owner_index)
                        st.session_state["wealth_os_form_data"] = updated
                        st.rerun()


def _render_form_fields(form_data: FormData) -> FormData:
    """Render form sections with human-friendly labels and percentage controls."""
    household = form_data["household"]
    employment = form_data["employment"]
    investments = form_data["investments"]
    amazon = form_data["amazon_rsus"]
    assumptions = form_data["assumptions"]

    with st.expander("Household and retirement", expanded=True):
        left, right = st.columns(2)
        household["name"] = left.text_input("Household name", value=str(household["name"]))
        household["current_age"] = right.number_input(
            "Primary age", min_value=0, step=1, value=int(household["current_age"])
        )
        household["spouse_age"] = left.number_input(
            "Spouse age", min_value=0, step=1, value=int(household["spouse_age"])
        )
        household["planned_retirement_age"] = right.number_input(
            "Retirement age", min_value=0, step=1, value=int(household["planned_retirement_age"])
        )
        household["life_expectancy"] = left.number_input(
            "Life expectancy", min_value=0, step=1, value=int(household["life_expectancy"])
        )
        assumptions["start_year"] = right.number_input(
            "Start year", min_value=1, step=1, value=int(assumptions["start_year"])
        )
        assumptions["target_retirement_income"] = left.number_input(
            "Target retirement spending (EUR)",
            min_value=0.0,
            value=float(assumptions["target_retirement_income"]),
            step=1000.0,
        )
        assumptions["inflation_rate"] = percentage_to_rate(
            right.number_input(
                "Inflation (%)", value=rate_to_percentage(assumptions["inflation_rate"]), step=0.1
            )
        )

    with st.expander("Employment and investments", expanded=True):
        left, right = st.columns(2)
        employment["salary"] = left.number_input(
            "Annual salary (EUR)", min_value=0.0, value=float(employment["salary"]), step=1000.0
        )
        employment["annual_savings"] = right.number_input(
            "Annual savings (EUR)",
            min_value=0.0,
            value=float(employment["annual_savings"]),
            step=1000.0,
        )
        investments["cash_balance"] = left.number_input(
            "Cash balance (EUR)",
            min_value=0.0,
            value=float(investments["cash_balance"]),
            step=1000.0,
        )
        investments["etf_value"] = right.number_input(
            "ETF value (EUR)", min_value=0.0, value=float(investments["etf_value"]), step=1000.0
        )
        investments["etf_growth_rate"] = percentage_to_rate(
            left.number_input(
                "Expected ETF return (%)",
                value=rate_to_percentage(investments["etf_growth_rate"]),
                step=0.1,
            )
        )

    with st.expander("Amazon RSUs", expanded=False):
        st.caption(
            "Vested holdings are entered as shares. Share price is USD; all model outputs are EUR."
        )
        left, right = st.columns(2)
        amazon["vested_shares"] = left.number_input(
            "Vested Amazon shares", min_value=0.0, value=float(amazon["vested_shares"]), step=1.0
        )
        amazon["annual_grant_shares"] = right.number_input(
            "Annual grant shares",
            min_value=0.0,
            value=float(amazon["annual_grant_shares"]),
            step=1.0,
        )
        amazon["share_price_usd"] = left.number_input(
            "Amazon share price (USD)",
            min_value=0.0,
            value=float(amazon["share_price_usd"]),
            step=1.0,
        )
        amazon["eur_usd_exchange_rate"] = right.number_input(
            "EUR per USD", min_value=0.01, value=float(amazon["eur_usd_exchange_rate"]), step=0.01
        )
        amazon["annual_growth_rate"] = percentage_to_rate(
            left.number_input(
                "Amazon annual growth (%)",
                value=rate_to_percentage(amazon["annual_growth_rate"]),
                step=0.1,
            )
        )
        amazon["sell_on_vest"] = right.checkbox(
            "Sell newly vested shares", value=bool(amazon["sell_on_vest"])
        )

    _render_pensions(form_data)
    _render_tax(form_data)
    _render_properties(form_data)
    return form_data


def render_input_context(configuration: WealthOsConfig, source: str) -> WealthOsConfig | None:
    """Render input-page-only configuration status, import/export, and compact summaries."""
    st.caption(configuration_status(source))
    with st.expander("Configuration import and export", expanded=True):
        uploaded_file = st.file_uploader("Load YAML", type=["yaml", "yml"])
        if uploaded_file is not None and st.button("Populate inputs from YAML"):
            try:
                return load_configuration(uploaded_file.getvalue().decode("utf-8"))
            except (ConfigurationError, ValidationError) as error:
                st.error(f"YAML could not be loaded: {error}")
        st.download_button(
            "Download current inputs as YAML",
            data=configuration_to_yaml(configuration),
            file_name="wealth-os-inputs.yaml",
            mime="application/x-yaml",
        )
    with st.expander("Scenario and model information"):
        st.caption(
            f"Primary age {configuration.household.current_age}; spouse age "
            f"{configuration.household.spouse_age}; retirement age "
            f"{configuration.household.planned_retirement_age}; life expectancy "
            f"{configuration.household.life_expectancy}."
        )
        st.caption(
            f"Inflation {rate_to_percentage(configuration.assumptions.inflation_rate):.1f}% · "
            f"ETF growth {rate_to_percentage(configuration.investments.etf_growth_rate):.1f}% · "
            "Amazon growth "
            f"{rate_to_percentage(configuration.amazon_rsus.annual_growth_rate):.1f}% · "
            f"{len(configuration.rental_properties)} rental properties."
        )
        st.caption(
            "Deterministic planning model only. It is not financial, investment, tax, or "
            "retirement advice."
        )
    return None


def _render_pensions(form_data: FormData) -> None:
    """Render all pension input groups."""
    with st.expander("Pensions", expanded=False):
        for index, pension in enumerate(form_data["pensions"], start=1):
            st.markdown(f"**Pension {index}**")
            left, right = st.columns(2)
            pension["name"] = left.text_input(
                "Name", value=str(pension["name"]), key=f"pension_name_{index}"
            )
            pension["owner"] = right.text_input(
                "Owner", value=str(pension["owner"]), key=f"pension_owner_{index}"
            )
            pension["current_value"] = left.number_input(
                "Current value (EUR)",
                min_value=0.0,
                value=float(pension["current_value"]),
                step=1000.0,
                key=f"pension_value_{index}",
            )
            pension["annual_growth_rate"] = percentage_to_rate(
                right.number_input(
                    "Growth (%)",
                    value=rate_to_percentage(pension["annual_growth_rate"]),
                    step=0.1,
                    key=f"pension_growth_{index}",
                )
            )
            pension["annual_contribution"] = left.number_input(
                "Annual contribution (EUR)",
                min_value=0.0,
                value=float(pension["annual_contribution"]),
                step=1000.0,
                key=f"pension_contribution_{index}",
            )


def _render_properties(form_data: FormData) -> None:
    """Render all rental-property input groups."""
    with st.expander("Rental properties", expanded=False):
        if not form_data["rental_properties"]:
            st.caption("No rental properties are included.")
        for index, property_input in enumerate(form_data["rental_properties"], start=1):
            st.markdown(f"**Property {index}**")
            left, right = st.columns(2)
            property_input["name"] = left.text_input(
                "Name", value=str(property_input["name"]), key=f"property_name_{index}"
            )
            property_input["purchase_year"] = right.number_input(
                "Purchase year",
                min_value=1,
                step=1,
                value=int(property_input["purchase_year"]),
                key=f"property_year_{index}",
            )
            property_input["purchase_price"] = left.number_input(
                "Purchase price (EUR)",
                min_value=0.0,
                value=float(property_input["purchase_price"]),
                step=1000.0,
                key=f"property_price_{index}",
            )
            property_input["current_value"] = right.number_input(
                "Current value (EUR)",
                min_value=0.0,
                value=float(property_input["current_value"]),
                step=1000.0,
                key=f"property_value_{index}",
            )
            property_input["annual_net_rent"] = left.number_input(
                "Annual net rental income (EUR)",
                min_value=0.0,
                value=float(property_input["annual_net_rent"]),
                step=1000.0,
                key=f"property_rent_{index}",
            )
            property_input["annual_growth_rate"] = percentage_to_rate(
                right.number_input(
                    "Growth (%)",
                    value=rate_to_percentage(property_input["annual_growth_rate"]),
                    step=0.1,
                    key=f"property_growth_{index}",
                )
            )
            owners = property_input.get("owners", [])
            if not isinstance(owners, list):
                raise TypeError("property owners must be a list in dashboard form data")
            if owners:
                st.caption("Beneficial ownership used only for estimated rental-tax allocation.")
            for owner_index, owner in enumerate(owners, start=1):
                owner_left, owner_right = st.columns(2)
                owner["person"] = owner_left.text_input(
                    "Owner",
                    value=str(owner["person"]),
                    key=f"property_owner_{index}_{owner_index}",
                )
                owner["share"] = percentage_to_rate(
                    owner_right.number_input(
                        "Ownership (%)",
                        min_value=0.0,
                        max_value=100.0,
                        value=rate_to_percentage(Decimal(str(owner["share"]))),
                        step=1.0,
                        key=f"property_share_{index}_{owner_index}",
                    )
                )
            if owners:
                total = sum((Decimal(str(owner["share"])) for owner in owners), start=Decimal("0"))
                st.caption(
                    f"Ownership total: {total:.0%}"
                    if total == total.quantize(Decimal("0.01"))
                    else f"Ownership total: {total:.2%}"
                )


def _render_tax(form_data: FormData) -> None:
    """Render the small opt-in tax configuration surface without changing tax-disabled defaults."""
    tax = form_data["tax"]
    with st.expander("Estimated Irish tax modelling", expanded=False):
        tax["enabled"] = st.checkbox(
            "Enable estimated Irish tax modelling", value=bool(tax["enabled"])
        )
        if tax["enabled"]:
            st.caption(
                "Estimated Irish tax based on configured planning assumptions. "
                "This is not a tax return or tax advice."
            )
            tax["assessable_spouse"] = st.text_input(
                "Assessable spouse", value=str(tax["assessable_spouse"] or "")
            )
            st.caption(
                f"Tax-rule file: {tax['rules_file']}; assessment basis: {tax['assessment_basis']}."
            )
            tax["index_future_rules_with_inflation"] = st.checkbox(
                "Index future tax-rule thresholds with inflation",
                value=bool(tax["index_future_rules_with_inflation"]),
            )
            tax["pension_prsi_enabled"] = st.checkbox(
                "Apply configured PRSI policy to private pensions",
                value=bool(tax["pension_prsi_enabled"]),
            )
            tax["rental_prsi_enabled"] = st.checkbox(
                "Apply configured PRSI policy to rental profit",
                value=bool(tax["rental_prsi_enabled"]),
            )
            tax["reduced_usc_enabled"] = st.checkbox(
                "Reduced USC eligibility (planning assumption)",
                value=bool(tax["reduced_usc_enabled"]),
            )
            st.caption(
                "Married Person's Tax Credit is represented in the configured rules. Employee, "
                "Home Carer, and Age Tax Credits are not modelled or eligibility-verified."
            )
        else:
            st.caption("Tax modelling disabled. Gross recurring-income behaviour is preserved.")

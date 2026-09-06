# ruff: noqa: E501
"""Customer-facing Financial Picture presentation and bounded update proposal."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from html import escape

import streamlit as st

from experience.components.visual_primitives import metric_grid, section_heading
from experience.display import format_display_value
from experience.live.models import FinancialPicture, FinancialPictureItem


@dataclass(frozen=True, slots=True)
class ProposedFinancialPictureUpdate:
    """A reviewed prototype proposal that never mutates the baseline."""

    field: str
    label: str
    current_value: int | Decimal
    proposed_value: int | Decimal
    unit: str


def render_financial_picture(
    picture: FinancialPicture,
    *,
    supported_retirement_ages: tuple[int, ...],
) -> None:
    """Render a readable snapshot plus a non-persistent retirement edit flow."""

    st.markdown('<main class="wos-picture">', unsafe_allow_html=True)
    st.markdown('<div class="wos-visual-kicker">Financial Picture</div>', unsafe_allow_html=True)
    st.markdown(
        '<h1 class="wos-picture-title">What Wealth OS currently knows</h1>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="wos-support">A readable snapshot of the information used in your planning '
        "illustrations. Correcting this record is separate from exploring a temporary "
        "Workspace scenario.</p>",
        unsafe_allow_html=True,
    )

    _render_picture_hero(picture)
    _render_boundary_map(picture)
    _render_available_assets(picture)
    _render_retirement_assets(picture)
    _render_investment_property(picture)
    _render_primary_residence(picture)
    _render_planning_details(picture)
    if st.button(
        "Edit retirement details",
        key="financial-picture-edit-retirement",
        type="tertiary",
    ):
        st.session_state["financial-picture-editing"] = True

    if st.session_state.get("financial-picture-editing"):
        _render_edit_flow(picture, supported_retirement_ages)
    proposal = st.session_state.get("financial-picture-proposal")
    if isinstance(proposal, tuple) and all(
        isinstance(item, ProposedFinancialPictureUpdate) for item in proposal
    ):
        _render_proposal(proposal)
    st.markdown("</main>", unsafe_allow_html=True)


def _render_picture_hero(picture: FinancialPicture) -> None:
    """Show four deliberately distinct current-position definitions."""

    hero = (
        (
            "Household net worth",
            _formatted(picture, "summary:household_net_worth"),
            "Planning net worth plus primary-residence equity",
        ),
        (
            "Planning net worth",
            _formatted(picture, "summary:planning_net_worth"),
            "Assets represented in the funding plan",
        ),
        (
            "Liquid / investable",
            _formatted(picture, "summary:liquid_investable_assets"),
            "Cash, ordinary investments and employer equity",
        ),
        (
            "Retirement assets",
            _formatted(picture, "summary:retirement_assets"),
            "Pensions, subject to access rules",
        ),
    )
    st.markdown(metric_grid(hero, class_name="wos-picture-metric-grid"), unsafe_allow_html=True)


def _render_boundary_map(picture: FinancialPicture) -> None:
    st.markdown(
        section_heading(
            "How your position is organised",
            "Household wealth is broader than the assets Wealth OS assumes can fund the plan.",
        ),
        unsafe_allow_html=True,
    )
    planning = _formatted(picture, "summary:planning_net_worth")
    residence = _formatted(picture, "primary_residence:equity")
    st.markdown(
        '<section class="wos-boundary-map">'
        '<div class="wos-boundary-label"><span>Household position</span>'
        "<small>Everything currently represented</small></div>"
        '<div class="wos-boundary-planning"><div><span>Available planning assets</span>'
        "<small>Cash · taxable holdings · employer equity</small></div>"
        "<div><span>Retirement assets</span><small>Pensions · access constrained</small></div>"
        "<div><span>Investment property</span><small>Non-liquid · current or planned</small></div>"
        f"<strong>{escape(planning)}</strong><em>Planning net worth</em></div>"
        '<div class="wos-boundary-home"><div><span>Primary residence</span>'
        "<small>Household context only · outside plan funding</small></div>"
        f"<strong>{escape(residence)}</strong></div>"
        "</section>",
        unsafe_allow_html=True,
    )


def _render_available_assets(picture: FinancialPicture) -> None:
    st.markdown(
        section_heading(
            "Available planning assets",
            "These assets can participate in the plan, but their liquidity and concentration differ.",
        ),
        unsafe_allow_html=True,
    )
    assets = (
        ("Cash", _formatted(picture, "cash"), "Immediately liquid"),
        (
            "Ordinary taxable investments",
            _formatted(picture, "investments"),
            "Canonical InvestmentHolding records",
        ),
        (
            "Employer / direct equity",
            _formatted(picture, "employer_equity:value"),
            f"{_item(picture, 'employer_equity').value} vested shares · {_item(picture, 'equity_policy').value}",
        ),
    )
    st.markdown(metric_grid(assets), unsafe_allow_html=True)
    holdings = _record_groups(picture, "investment:")
    holding_cards = "".join(
        '<article class="wos-holding-card">'
        f'<span class="wos-record-type">{escape(str(values.get("type", "Investment")))}</span>'
        f"<h3>{escape(str(values.get('name', 'Unnamed holding')))}</h3>"
        f"<strong>{escape(format_display_value(values.get('value'), 'EUR'))}</strong>"
        f"<small>Stable holding ID · {escape(record_id)}</small>"
        "</article>"
        for record_id, values in holdings
    )
    st.markdown(
        '<div class="wos-subsection-label">Ordinary taxable holdings</div>'
        f'<section class="wos-record-grid">{holding_cards}</section>',
        unsafe_allow_html=True,
    )


def _render_retirement_assets(picture: FinancialPicture) -> None:
    st.markdown(
        section_heading(
            "Retirement assets",
            "Shown separately because pension access and drawdown rules differ from liquid assets.",
        ),
        unsafe_allow_html=True,
    )
    cards = "".join(
        '<article class="wos-domain-card">'
        f"<span>{escape(str(values.get('owner', 'Owner not recorded')))}</span>"
        f"<h3>{escape(record_id)}</h3>"
        f"<strong>{escape(format_display_value(values.get('value'), 'EUR'))}</strong>"
        f"<small>Access age {escape(str(values.get('access_age', 'not recorded')))} · "
        f"{'Modelled for drawdown' if values.get('drawdown') is True else 'Not modelled for drawdown'}</small>"
        "</article>"
        for record_id, values in _record_groups(picture, "pension:")
    )
    st.markdown(f'<section class="wos-record-grid">{cards}</section>', unsafe_allow_html=True)


def _render_investment_property(picture: FinancialPicture) -> None:
    st.markdown(
        section_heading(
            "Investment property",
            "Property is represented separately: it may support cash flow, but it is not a liquid asset.",
        ),
        unsafe_allow_html=True,
    )
    cards = "".join(
        '<article class="wos-property-card">'
        f'<span class="wos-status-pill">{escape(str(values.get("status", "Recorded")))}</span>'
        f"<h3>{escape(record_id)}</h3>"
        '<div class="wos-mini-grid">'
        f"<div><small>Purchase</small><strong>{escape(format_display_value(values.get('price'), 'EUR'))}</strong></div>"
        f"<div><small>Annual net rent</small><strong>{escape(format_display_value(values.get('rent'), 'EUR/year'))}</strong></div>"
        f"<div><small>Purchase year</small><strong>{escape(str(values.get('year', '—')))}</strong></div>"
        f"<div><small>Current value</small><strong>{escape(format_display_value(values.get('value'), 'EUR'))}</strong></div>"
        "</div>"
        f"<p>Rent growth {escape(format_display_value(values.get('rent_growth'), 'ratio'))} · "
        f"Appreciation {escape(format_display_value(values.get('appreciation'), 'ratio'))}</p>"
        "</article>"
        for record_id, values in _record_groups(picture, "property:")
    )
    st.markdown(
        f'<section class="wos-property-grid">{cards or "<p>Nothing recorded yet.</p>"}</section>',
        unsafe_allow_html=True,
    )


def _render_primary_residence(picture: FinancialPicture) -> None:
    residence_items = _section_items(picture.items, ("primary_residence:",))
    if not residence_items:
        return
    name = _formatted(picture, "primary_residence:name")
    value = _formatted(picture, "primary_residence:value")
    mortgage = _formatted(picture, "primary_residence:mortgage")
    equity = _formatted(picture, "primary_residence:equity")
    st.markdown(
        '<section class="wos-residence-boundary">'
        '<div><span class="wos-record-type">Primary residence</span>'
        f"<h2>{escape(name)}</h2>"
        "<p>Included in your household position; not assumed available to fund your plan.</p></div>"
        '<div class="wos-mini-grid">'
        f"<div><small>Estimated value</small><strong>{escape(value)}</strong></div>"
        f"<div><small>Mortgage</small><strong>{escape(mortgage)}</strong></div>"
        f"<div><small>Home equity</small><strong>{escape(equity)}</strong></div>"
        "</div></section>",
        unsafe_allow_html=True,
    )


def _render_planning_details(picture: FinancialPicture) -> None:
    st.markdown(
        section_heading(
            "Household and planning details",
            "The personal details and assumptions that frame the current picture.",
        ),
        unsafe_allow_html=True,
    )
    selectors = (
        "household",
        "current_age",
        "partner_age",
        "employment_salary",
        "annual_savings",
        "planned_retirement_age",
        "retirement_spending",
        "inflation",
        "tax",
    )
    _render_section("Current record", _section_items(picture.items, selectors))


def proposed_retirement_age(
    age: int, current_age: int
) -> tuple[ProposedFinancialPictureUpdate, ...]:
    """Create a scenario-to-picture proposal without applying it."""

    return (
        ProposedFinancialPictureUpdate(
            "planned_retirement_age",
            "Planned retirement age",
            current_age,
            age,
            "years old",
        ),
    )


def _section_items(
    items: tuple[FinancialPictureItem, ...], selectors: tuple[str, ...]
) -> tuple[FinancialPictureItem, ...]:
    return tuple(
        item
        for item in items
        if any(item.key == selector or item.key.startswith(selector) for selector in selectors)
    )


def _render_section(title: str, items: tuple[FinancialPictureItem, ...]) -> None:
    if items:
        rows = "".join(
            '<div class="wos-picture-summary-row">'
            f"<span>{escape(item.label)}</span>"
            f"<strong>{escape(format_display_value(item.value, _unit_for_key(item.key)))}</strong>"
            "</div>"
            for item in items
        )
    else:
        rows = '<p class="wos-missing">Nothing recorded yet.</p>'
    st.markdown(
        f'<section class="wos-picture-section"><h2>{escape(title)}</h2>{rows}</section>',
        unsafe_allow_html=True,
    )


def _render_edit_flow(
    picture: FinancialPicture,
    supported_retirement_ages: tuple[int, ...],
) -> None:
    current_age = int(_item(picture, "planned_retirement_age").value)
    current_spending = Decimal(str(_item(picture, "retirement_spending").value))
    with st.container(border=True):
        st.subheader("Edit retirement details")
        age = st.selectbox(
            "Planned retirement age",
            supported_retirement_ages,
            index=supported_retirement_ages.index(current_age),
            key="financial-picture-proposed-age",
        )
        spending = st.number_input(
            "Annual retirement spending",
            min_value=0,
            value=int(current_spending),
            step=5_000,
            key="financial-picture-proposed-spending",
        )
        if st.button("Review proposed changes", key="financial-picture-review-update"):
            proposals: list[ProposedFinancialPictureUpdate] = []
            if age != current_age:
                proposals.extend(proposed_retirement_age(age, current_age))
            proposed_spending = Decimal(str(spending))
            if proposed_spending != current_spending:
                proposals.append(
                    ProposedFinancialPictureUpdate(
                        "retirement_spending",
                        "Annual retirement spending",
                        current_spending,
                        proposed_spending,
                        "EUR",
                    )
                )
            st.session_state["financial-picture-proposal"] = tuple(proposals)
            st.session_state["financial-picture-editing"] = False
            st.rerun()


def _render_proposal(proposal: tuple[ProposedFinancialPictureUpdate, ...]) -> None:
    with st.container(border=True):
        st.subheader("Proposed Financial Picture Update")
        if not proposal:
            st.write("No changes were proposed.")
            return
        for item in proposal:
            st.markdown(
                f"**{item.label}**  \n"
                f"{format_display_value(item.current_value, item.unit)} → "
                f"{format_display_value(item.proposed_value, item.unit)}"
            )
        st.caption(
            "Persistence is not enabled in this prototype. Confirmation records intent only; "
            "the validated Financial Picture remains unchanged."
        )
        if st.button("Confirm proposed update", key="financial-picture-confirm-update"):
            st.session_state["financial-picture-update-confirmed"] = True
        if st.session_state.get("financial-picture-update-confirmed"):
            st.success(
                "Proposal confirmed for future implementation. No baseline data was changed."
            )


def _item(picture: FinancialPicture, key: str) -> FinancialPictureItem:
    return next(item for item in picture.items if item.key == key)


def _formatted(picture: FinancialPicture, key: str) -> str:
    item = _item(picture, key)
    return format_display_value(item.value, _unit_for_key(item.key))


def _record_groups(
    picture: FinancialPicture,
    prefix: str,
) -> tuple[tuple[str, dict[str, str | int | Decimal | bool]], ...]:
    records: dict[str, dict[str, str | int | Decimal | bool]] = {}
    for item in picture.items:
        if not item.key.startswith(prefix):
            continue
        remainder = item.key.removeprefix(prefix)
        if ":" not in remainder:
            continue
        record_id, field = remainder.rsplit(":", 1)
        records.setdefault(record_id, {})[field] = item.value
    return tuple(records.items())


def _unit_for_key(key: str) -> str:
    if (
        key.startswith("summary:")
        or key
        in {
            "annual_savings",
            "cash",
            "employment_salary",
            "investments",
            "retirement_spending",
            "employer_equity:value",
        }
        or key.startswith("pension:")
    ):
        if key.endswith(":access_age") or key.endswith((":owner", ":drawdown")):
            return ""
        return "EUR"
    if key.endswith((":price", ":rent", ":value", ":mortgage", ":equity")):
        return "EUR"
    if key == "inflation" or key.endswith((":appreciation", ":rent_growth")):
        return "ratio"
    return ""

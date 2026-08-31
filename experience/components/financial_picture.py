"""Customer-facing Financial Picture presentation and bounded update proposal."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from html import escape

import streamlit as st

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


SECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Household", ("household", "current_age", "partner_age")),
    ("Income & saving", ("employment_salary", "annual_savings")),
    ("Cash & investments", ("cash", "investments", "employer_equity", "equity_policy")),
    ("Pensions", ("pension:",)),
    ("Property", ("property:",)),
    ("Retirement", ("planned_retirement_age", "retirement_spending")),
    ("Planning assumptions", ("inflation", "tax")),
)


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
    for title, selectors in SECTIONS:
        items = _section_items(picture.items, selectors)
        _render_section(title, items)
        if title == "Retirement" and st.button(
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
    """Compose a visual snapshot from existing Financial Picture values only."""

    cash = _item(picture, "cash")
    investments = _item(picture, "investments")
    retirement_age = _item(picture, "planned_retirement_age")
    spending = _item(picture, "retirement_spending")
    savings = _item(picture, "annual_savings")
    hero = (
        ("Cash", format_display_value(cash.value, "EUR")),
        ("Investments", format_display_value(investments.value, "EUR")),
        ("Annual saving", format_display_value(savings.value, "EUR/year")),
        ("Planned retirement", f"Age {retirement_age.value}"),
    )
    cells = "".join(
        '<div class="wos-picture-hero-cell">'
        f"<span>{escape(label)}</span><strong>{escape(value)}</strong></div>"
        for label, value in hero
    )
    st.markdown(
        f'<section class="wos-picture-hero">{cells}</section>'
        '<div class="wos-picture-retirement-callout">'
        "<span>Retirement spending assumption</span>"
        f"<strong>{escape(format_display_value(spending.value, 'EUR/year'))}</strong>"
        "<small>in today's money, inflated through the projection</small></div>",
        unsafe_allow_html=True,
    )


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


def _unit_for_key(key: str) -> str:
    if key in {
        "annual_savings",
        "cash",
        "employment_salary",
        "investments",
        "retirement_spending",
    } or key.startswith("pension:"):
        return "EUR"
    if key.endswith(":price") or key.endswith(":rent"):
        return "EUR"
    if key == "inflation":
        return "ratio"
    return ""

"""Compact, responsive dashboard card components."""

import streamlit as st


def render_kpi_card(label: str, value: str, detail: str | None = None) -> None:
    """Render a compact KPI card without Streamlit metric-value overflow."""
    with st.container(border=True):
        st.caption(label)
        st.markdown(f"#### {value}")
        if detail is not None:
            st.caption(detail)


def render_kpi_grid(cards: tuple[tuple[str, str, str | None], ...]) -> None:
    """Render KPI cards in two-column groups suitable for laptop and narrow layouts."""
    for index in range(0, len(cards), 2):
        columns = st.columns(2)
        for column, card in zip(columns, cards[index : index + 2], strict=False):
            with column:
                render_kpi_card(*card)

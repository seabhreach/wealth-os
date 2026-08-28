# ruff: noqa: E501
"""Calm, accessible visual tokens for the mock Experience shell."""

from __future__ import annotations

import streamlit as st

LIGHT_THEME_TOKENS = {
    "page_background": "#ffffff",
    "primary_text": "#17212b",
    "secondary_text": "#475663",
    "muted_text": "#66727f",
    "surface_background": "#f4f6f7",
    "subtle_border": "#cfd8de",
    "input_background": "#ffffff",
    "input_text": "#17212b",
    "placeholder_text": "#5d6975",
    "chip_background": "#eef2f3",
    "chip_text": "#17212b",
    "link_text": "#235d58",
    "focus_outline": "#2b7069",
    "disabled_text": "#7b858e",
}
DARK_THEME_TOKENS = {
    "page_background": "#0e1319",
    "primary_text": "#f4f7f9",
    "secondary_text": "#c3ccd3",
    "muted_text": "#aeb8c1",
    "surface_background": "#17212b",
    "subtle_border": "#34424e",
    "input_background": "#17212b",
    "input_text": "#f4f7f9",
    "placeholder_text": "#aeb8c1",
    "chip_background": "#1c2933",
    "chip_text": "#f4f7f9",
    "link_text": "#9ac8c2",
    "focus_outline": "#9ac8c2",
    "disabled_text": "#7e8993",
}

LIGHT_INPUT_FOREGROUND = LIGHT_THEME_TOKENS["input_text"]
LIGHT_INPUT_BACKGROUND = LIGHT_THEME_TOKENS["input_background"]
DARK_INPUT_FOREGROUND = DARK_THEME_TOKENS["input_text"]
DARK_INPUT_BACKGROUND = DARK_THEME_TOKENS["input_background"]
RESPONSIVE_BREAKPOINT_PX = 1050


def layout_mode_for_width(width: int) -> str:
    """Mirror the CSS breakpoint used by the active Experience panes."""

    return "stacked" if width <= RESPONSIVE_BREAKPOINT_PX else "split"


def pane_order_for_width(width: int) -> tuple[str, str]:
    """Keep conversation before its Workspace in either layout mode."""

    _ = layout_mode_for_width(width)
    return ("conversation", "workspace")


EXPERIENCE_CSS = f"""
<style>
:root {{
  --wos-page-bg: var(--background-color);
  --wos-ink: var(--text-color);
  --wos-secondary: color-mix(in srgb, var(--text-color) 78%, var(--background-color));
  --wos-muted: color-mix(in srgb, var(--text-color) 64%, var(--background-color));
  --wos-soft: var(--secondary-background-color);
  --wos-line: color-mix(in srgb, var(--text-color) 22%, var(--background-color));
  --wos-accent: var(--primary-color);
  --wos-input-fg: var(--text-color);
  --wos-input-bg: var(--secondary-background-color);
  --wos-placeholder: color-mix(in srgb, var(--text-color) 62%, var(--background-color));
  --wos-chip-fg: var(--text-color);
  --wos-chip-bg: var(--secondary-background-color);
  --wos-disabled: color-mix(in srgb, var(--text-color) 42%, var(--background-color));
}}

.stApp {{ color: var(--wos-ink); background: var(--wos-page-bg); }}
.block-container {{ max-width: 1440px; padding-top: 2.5rem; padding-bottom: 3rem; }}
#MainMenu, footer {{ visibility: hidden; }}

.wos-home {{ max-width: 760px; margin: 8vh auto 0; }}
.wos-wordmark {{ font-size: 0.82rem; font-weight: 650; letter-spacing: 0.08em; text-transform: uppercase; color: var(--wos-muted); }}
.wos-question {{ color: var(--wos-ink); font-size: clamp(2rem, 5vw, 3.65rem); line-height: 1.08; letter-spacing: -0.045em; margin: 1.2rem 0 1rem; max-width: 720px; }}
.wos-support {{ color: var(--wos-muted); font-size: 1.05rem; line-height: 1.65; max-width: 680px; margin-bottom: 2rem; }}
.wos-prototype-note {{ color: var(--wos-muted); font-size: 0.78rem; margin-top: 1.2rem; }}
.wos-recent-heading {{ margin-top: 3.25rem; color: var(--wos-muted); font-size: 0.82rem; font-weight: 650; letter-spacing: 0.04em; text-transform: uppercase; }}
.wos-recent-card {{ min-height: 5.6rem; }}
.wos-recent-title {{ color: var(--wos-ink); font-weight: 680; margin-bottom: 0.25rem; }}
.wos-recent-subtitle {{ color: var(--wos-secondary); font-size: 0.88rem; line-height: 1.4; }}
.wos-recent-status {{ color: var(--wos-muted); font-size: 0.75rem; margin-top: 0.55rem; }}

.wos-pane-label {{ color: var(--wos-muted); font-size: 0.76rem; font-weight: 650; letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 1.5rem; }}
.wos-message {{ margin: 0 0 1.65rem; max-width: 700px; }}
.wos-message-author {{ font-size: 0.78rem; font-weight: 700; color: var(--wos-muted); margin-bottom: 0.32rem; }}
.wos-message-body {{ font-size: 1rem; line-height: 1.62; color: var(--wos-ink); }}
.wos-message-user {{ margin-left: 1.4rem; padding-left: 0.9rem; border-left: 2px solid var(--wos-line); }}
.wos-context-actions {{ color: var(--wos-muted); font-size: 0.82rem; margin: -0.7rem 0 1.3rem; }}
.wos-context-actions span {{ margin-right: 1rem; text-decoration: underline; text-decoration-color: var(--wos-line); text-underline-offset: 0.2rem; }}

.wos-workspace {{ padding: 0.2rem 0 0; }}
div[data-testid="stColumn"]:has(.wos-workspace) {{ border-left: 1px solid var(--wos-line); padding-left: 1.7rem; }}
.wos-workspace-title {{ font-size: 1.85rem; line-height: 1.15; letter-spacing: -0.025em; margin: 0.55rem 0; }}
.wos-status {{ display: inline-block; color: var(--wos-accent); background: color-mix(in srgb, var(--wos-accent) 10%, transparent); border-radius: 999px; padding: 0.35rem 0.7rem; font-size: 0.8rem; margin-bottom: 2rem; }}
.wos-live-badge {{ display: inline-block; color: var(--wos-accent); border: 1px solid color-mix(in srgb, var(--wos-accent) 45%, transparent); border-radius: 999px; padding: 0.3rem 0.65rem; font-size: 0.76rem; margin: 0.4rem 0 1.4rem; }}
.wos-section {{ padding: 1.15rem 0 1.35rem; border-top: 1px solid var(--wos-line); }}
.wos-section h3 {{ font-size: 1rem; margin: 0 0 0.45rem; }}
.wos-section p {{ color: var(--wos-muted); line-height: 1.55; margin: 0 0 0.8rem; }}
.wos-picture-row, .wos-evidence-row {{ display: grid; grid-template-columns: minmax(8rem, 1fr) 1.3fr auto; gap: 0.8rem; align-items: baseline; padding: 0.5rem 0; font-size: 0.88rem; }}
.wos-evidence-row {{ grid-template-columns: 1fr 1.3fr; }}
.wos-row-label {{ color: var(--wos-muted); }}
.wos-row-status {{ color: var(--wos-accent); font-size: 0.74rem; }}
.wos-live-table {{ overflow-x: auto; }}
.wos-live-table table {{ width: 100%; border-collapse: collapse; font-size: 0.84rem; }}
.wos-live-table th, .wos-live-table td {{ padding: 0.55rem 0.7rem; border-bottom: 1px solid var(--wos-line); text-align: left; color: var(--wos-ink); }}
.wos-live-table th {{ color: var(--wos-muted); font-weight: 650; }}

.wos-visual-workspace {{ max-width: 1180px; margin: 1rem auto 0; }}
.wos-visual-kicker {{ color: var(--wos-accent); font-size: 0.78rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 2.5rem; }}
.wos-visual-title {{ color: var(--wos-ink); font-size: clamp(2.5rem, 5vw, 4.7rem); line-height: 1.02; letter-spacing: -0.055em; margin: 0.7rem 0 1rem; max-width: 900px; }}
.wos-visual-answer {{ color: var(--wos-ink); font-size: clamp(1.3rem, 2.2vw, 1.85rem); line-height: 1.42; max-width: 900px; margin: 0 0 0.9rem; }}
.wos-scenario-context {{ color: var(--wos-muted); font-size: 0.9rem; margin: 0 0 1.5rem; }}
.wos-visual-section-heading {{ border-top: 1px solid var(--wos-line); padding-top: 2rem; margin-top: 3rem; }}
.wos-visual-section-heading h2 {{ color: var(--wos-ink); font-size: clamp(1.45rem, 2vw, 2rem); letter-spacing: -0.025em; margin: 0; }}
.wos-visual-section-heading p {{ color: var(--wos-muted); font-size: 0.95rem; line-height: 1.55; max-width: 700px; margin: 0.55rem 0 0; }}
.wos-visual-copy {{ color: var(--wos-ink); font-size: 1.15rem; line-height: 1.7; max-width: 820px; }}
.wos-chart-summary {{ color: var(--wos-muted); font-size: 0.82rem; line-height: 1.5; max-width: 760px; }}
.wos-comparison {{ margin-top: 1.2rem; }}
.wos-comparison-row {{ display: grid; grid-template-columns: minmax(12rem, 1.4fr) 1fr 1fr; gap: 1.5rem; align-items: baseline; padding: 0.8rem 0; border-bottom: 1px solid var(--wos-line); font-size: 1rem; }}
.wos-comparison-label {{ color: var(--wos-muted); }}
.wos-comparison-row small {{ display: block; color: var(--wos-muted); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.18rem; }}
.wos-timeline {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; margin-top: 1.6rem; }}
.wos-milestone {{ position: relative; border-top: 2px solid var(--wos-line); padding: 1.1rem 1rem 0 0; min-height: 6.5rem; }}
.wos-milestone::before {{ content: ""; position: absolute; top: -0.38rem; left: 0; width: 0.65rem; height: 0.65rem; border-radius: 50%; background: var(--wos-accent); }}
.wos-milestone-year {{ display: block; color: var(--wos-muted); font-size: 0.76rem; margin-bottom: 0.45rem; }}
.wos-milestone strong, .wos-milestone > span:last-child {{ display: block; color: var(--wos-ink); font-size: 0.92rem; }}
.wos-milestone > span:last-child {{ color: var(--wos-muted); font-size: 0.8rem; margin-top: 0.25rem; }}
.wos-tradeoff-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 2.4rem; margin-top: 1.4rem; }}
.wos-tradeoff-item > span {{ color: var(--wos-accent); font-size: 0.76rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }}
.wos-tradeoff-item p {{ color: var(--wos-ink); line-height: 1.55; margin: 0.5rem 0; }}
.wos-detail-rule {{ border-top: 1px solid var(--wos-line); margin-top: 3rem; padding-top: 1rem; }}

div[data-testid="stChatInput"] textarea {{ color: var(--wos-input-fg) !important; background: var(--wos-input-bg) !important; caret-color: var(--wos-input-fg) !important; }}
div[data-testid="stChatInput"] textarea::placeholder {{ color: var(--wos-placeholder) !important; opacity: 1; }}
div[data-testid="stChatInput"] {{ border-color: var(--wos-line); background: var(--wos-input-bg); }}

div[data-testid="stButton"] > button {{ border-radius: 999px; border: 1px solid var(--wos-line); background: var(--wos-chip-bg); color: var(--wos-chip-fg); font-weight: 550; min-height: 2.35rem; }}
div[data-testid="stButton"] > button:hover {{ border-color: var(--wos-accent); color: var(--wos-accent); background: var(--wos-soft); }}
div[data-testid="stButton"] > button:disabled {{ color: var(--wos-disabled); border-color: var(--wos-line); opacity: 1; }}
div[data-testid="stButton"] > button[kind="tertiary"] {{ min-height: auto; padding: 0.18rem 0; border: 0; border-radius: 0; background: transparent; color: var(--wos-muted); font-size: 0.8rem; text-decoration: underline; text-decoration-color: var(--wos-line); text-underline-offset: 0.2rem; }}
div[data-testid="stButton"] > button[kind="tertiary"]:hover {{ background: transparent; color: var(--wos-accent); }}
div[data-testid="stButton"] > button:focus-visible, div[data-testid="stChatInput"] textarea:focus-visible {{ outline: 3px solid color-mix(in srgb, var(--wos-accent) 55%, transparent); outline-offset: 2px; }}

@media (max-width: {RESPONSIVE_BREAKPOINT_PX}px) {{
  div[data-testid="stHorizontalBlock"]:has(.wos-pane-label) {{ flex-direction: column; gap: 2rem; }}
  div[data-testid="stHorizontalBlock"]:has(.wos-pane-label) > div[data-testid="stColumn"] {{ width: 100% !important; flex: 1 1 100% !important; }}
  div[data-testid="stColumn"]:has(.wos-workspace) {{ border-left: 0; border-top: 1px solid var(--wos-line); padding: 2rem 0 0; }}
  .wos-picture-row, .wos-evidence-row {{ grid-template-columns: minmax(7rem, 1fr) 1.25fr auto; }}
  .wos-evidence-row {{ grid-template-columns: minmax(7rem, 1fr) 1.25fr; }}
  .wos-home {{ margin-top: 3vh; }}
  .wos-visual-workspace {{ max-width: 100%; }}
  .wos-tradeoff-grid {{ grid-template-columns: 1fr; gap: 0.8rem; }}
  .wos-timeline {{ grid-template-columns: 1fr; }}
  .wos-milestone {{ border-top: 0; border-left: 2px solid var(--wos-line); padding: 0 0 1.5rem 1.2rem; min-height: 0; }}
  .wos-milestone::before {{ top: 0.2rem; left: -0.4rem; }}
}}

@media (max-width: 700px) {{
  .wos-picture-row, .wos-evidence-row {{ grid-template-columns: 1fr; gap: 0.2rem; padding: 0.65rem 0; }}
  .wos-recent-card {{ min-height: auto; }}
  .wos-comparison-row {{ grid-template-columns: 1fr 1fr; gap: 0.45rem 1rem; }}
  .wos-comparison-label {{ grid-column: 1 / -1; }}
}}
</style>
"""


def apply_styles() -> None:
    """Inject the prototype's theme-aware visual treatment."""

    st.markdown(EXPERIENCE_CSS, unsafe_allow_html=True)

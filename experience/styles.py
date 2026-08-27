# ruff: noqa: E501
"""Calm, accessible visual tokens for the mock Experience shell."""

from __future__ import annotations

import streamlit as st

LIGHT_INPUT_FOREGROUND = "#17212b"
LIGHT_INPUT_BACKGROUND = "#ffffff"
DARK_INPUT_FOREGROUND = "#f4f7f9"
DARK_INPUT_BACKGROUND = "#17212b"


EXPERIENCE_CSS = f"""
<style>
:root {{
  --wos-ink: #17212b;
  --wos-muted: #66727f;
  --wos-soft: #f4f6f7;
  --wos-line: #dce2e6;
  --wos-accent: #315f5b;
  --wos-input-fg: {LIGHT_INPUT_FOREGROUND};
  --wos-input-bg: {LIGHT_INPUT_BACKGROUND};
}}

@media (prefers-color-scheme: dark) {{
  :root {{
    --wos-ink: #f4f7f9;
    --wos-muted: #aeb8c1;
    --wos-soft: #17212b;
    --wos-line: #34424e;
    --wos-accent: #9ac8c2;
    --wos-input-fg: {DARK_INPUT_FOREGROUND};
    --wos-input-bg: {DARK_INPUT_BACKGROUND};
  }}
}}

.stApp {{ color: var(--wos-ink); }}
.block-container {{ max-width: 1440px; padding-top: 2.5rem; padding-bottom: 3rem; }}
#MainMenu, footer {{ visibility: hidden; }}

.wos-home {{ max-width: 760px; margin: 8vh auto 0; }}
.wos-wordmark {{ font-size: 0.82rem; font-weight: 650; letter-spacing: 0.08em; text-transform: uppercase; color: var(--wos-muted); }}
.wos-question {{ font-size: clamp(2rem, 5vw, 3.65rem); line-height: 1.08; letter-spacing: -0.045em; margin: 1.2rem 0 1rem; max-width: 720px; }}
.wos-support {{ color: var(--wos-muted); font-size: 1.05rem; line-height: 1.65; max-width: 680px; margin-bottom: 2rem; }}
.wos-prototype-note {{ color: var(--wos-muted); font-size: 0.78rem; margin-top: 1.2rem; }}
.wos-recent-heading {{ margin-top: 3.25rem; color: var(--wos-muted); font-size: 0.82rem; font-weight: 650; letter-spacing: 0.04em; text-transform: uppercase; }}

.wos-pane-label {{ color: var(--wos-muted); font-size: 0.76rem; font-weight: 650; letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 1.5rem; }}
.wos-message {{ margin: 0 0 1.65rem; max-width: 700px; }}
.wos-message-author {{ font-size: 0.78rem; font-weight: 700; color: var(--wos-muted); margin-bottom: 0.32rem; }}
.wos-message-body {{ font-size: 1rem; line-height: 1.62; color: var(--wos-ink); }}
.wos-context-actions {{ color: var(--wos-muted); font-size: 0.82rem; margin: -0.7rem 0 1.3rem; }}
.wos-context-actions span {{ margin-right: 1rem; text-decoration: underline; text-decoration-color: var(--wos-line); text-underline-offset: 0.2rem; }}

.wos-workspace {{ padding: 0.2rem 0 2rem 1.7rem; border-left: 1px solid var(--wos-line); min-height: 70vh; }}
.wos-workspace-title {{ font-size: 1.85rem; line-height: 1.15; letter-spacing: -0.025em; margin: 0.55rem 0; }}
.wos-status {{ display: inline-block; color: var(--wos-accent); background: color-mix(in srgb, var(--wos-accent) 10%, transparent); border-radius: 999px; padding: 0.35rem 0.7rem; font-size: 0.8rem; margin-bottom: 2rem; }}
.wos-section {{ padding: 1.15rem 0 1.35rem; border-top: 1px solid var(--wos-line); }}
.wos-section h3 {{ font-size: 1rem; margin: 0 0 0.45rem; }}
.wos-section p {{ color: var(--wos-muted); line-height: 1.55; margin: 0 0 0.8rem; }}
.wos-picture-row, .wos-evidence-row {{ display: grid; grid-template-columns: minmax(8rem, 1fr) 1.3fr auto; gap: 0.8rem; align-items: baseline; padding: 0.5rem 0; font-size: 0.88rem; }}
.wos-evidence-row {{ grid-template-columns: 1fr 1.3fr; }}
.wos-row-label {{ color: var(--wos-muted); }}
.wos-row-status {{ color: var(--wos-accent); font-size: 0.74rem; }}

div[data-testid="stChatInput"] textarea {{ color: var(--wos-input-fg) !important; background: var(--wos-input-bg) !important; caret-color: var(--wos-input-fg) !important; }}
div[data-testid="stChatInput"] textarea::placeholder {{ color: color-mix(in srgb, var(--wos-input-fg) 58%, transparent) !important; opacity: 1; }}
div[data-testid="stChatInput"] {{ border-color: var(--wos-line); background: var(--wos-input-bg); }}

div[data-testid="stButton"] > button {{ border-radius: 999px; border: 1px solid var(--wos-line); background: var(--wos-input-bg); color: var(--wos-input-fg); font-weight: 550; min-height: 2.35rem; }}
div[data-testid="stButton"] > button:hover {{ border-color: var(--wos-accent); color: var(--wos-accent); background: var(--wos-soft); }}
div[data-testid="stButton"] > button[kind="tertiary"] {{ min-height: auto; padding: 0.18rem 0; border: 0; border-radius: 0; background: transparent; color: var(--wos-muted); font-size: 0.8rem; text-decoration: underline; text-decoration-color: var(--wos-line); text-underline-offset: 0.2rem; }}
div[data-testid="stButton"] > button[kind="tertiary"]:hover {{ background: transparent; color: var(--wos-accent); }}
div[data-testid="stButton"] > button:focus-visible, div[data-testid="stChatInput"] textarea:focus-visible {{ outline: 3px solid color-mix(in srgb, var(--wos-accent) 55%, transparent); outline-offset: 2px; }}

@media (max-width: 900px) {{
  .wos-workspace {{ border-left: 0; border-top: 1px solid var(--wos-line); padding: 2rem 0 0; margin-top: 2rem; min-height: auto; }}
  .wos-home {{ margin-top: 3vh; }}
}}
</style>
"""


def apply_styles() -> None:
    """Inject the prototype's theme-aware visual treatment."""

    st.markdown(EXPERIENCE_CSS, unsafe_allow_html=True)

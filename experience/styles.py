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
    """Return the staged shell layout used at every supported width."""

    _ = width
    return "full-width"


def pane_order_for_width(width: int) -> tuple[str, ...]:
    """Keep the Workspace singular rather than beside a permanent Conversation pane."""

    _ = layout_mode_for_width(width)
    return ("workspace",)


EXPERIENCE_CSS = f"""
<style>
:root {{
  --wos-page-bg: {LIGHT_THEME_TOKENS["page_background"]};
  --wos-ink: {LIGHT_THEME_TOKENS["primary_text"]};
  --wos-secondary: {LIGHT_THEME_TOKENS["secondary_text"]};
  --wos-muted: {LIGHT_THEME_TOKENS["muted_text"]};
  --wos-soft: {LIGHT_THEME_TOKENS["surface_background"]};
  --wos-raised: color-mix(in srgb, {LIGHT_THEME_TOKENS["surface_background"]} 88%, {LIGHT_THEME_TOKENS["page_background"]});
  --wos-accent-soft: color-mix(in srgb, {LIGHT_THEME_TOKENS["focus_outline"]} 13%, {LIGHT_THEME_TOKENS["page_background"]});
  --wos-accent-mid: color-mix(in srgb, {LIGHT_THEME_TOKENS["focus_outline"]} 30%, {LIGHT_THEME_TOKENS["page_background"]});
  --wos-positive-soft: color-mix(in srgb, #2f8f6b 16%, {LIGHT_THEME_TOKENS["page_background"]});
  --wos-caution-soft: color-mix(in srgb, #b7791f 15%, {LIGHT_THEME_TOKENS["page_background"]});
  --wos-line: {LIGHT_THEME_TOKENS["subtle_border"]};
  --wos-accent: {LIGHT_THEME_TOKENS["focus_outline"]};
  --wos-input-fg: {LIGHT_THEME_TOKENS["input_text"]};
  --wos-input-bg: {LIGHT_THEME_TOKENS["input_background"]};
  --wos-placeholder: {LIGHT_THEME_TOKENS["placeholder_text"]};
  --wos-chip-fg: {LIGHT_THEME_TOKENS["chip_text"]};
  --wos-chip-bg: {LIGHT_THEME_TOKENS["chip_background"]};
  --wos-disabled: {LIGHT_THEME_TOKENS["disabled_text"]};
}}

@media (prefers-color-scheme: dark) {{
  :root {{
    --wos-page-bg: {DARK_THEME_TOKENS["page_background"]};
    --wos-ink: {DARK_THEME_TOKENS["primary_text"]};
    --wos-secondary: {DARK_THEME_TOKENS["secondary_text"]};
    --wos-muted: {DARK_THEME_TOKENS["muted_text"]};
    --wos-soft: {DARK_THEME_TOKENS["surface_background"]};
    --wos-raised: color-mix(in srgb, {DARK_THEME_TOKENS["surface_background"]} 88%, {DARK_THEME_TOKENS["page_background"]});
    --wos-accent-soft: color-mix(in srgb, {DARK_THEME_TOKENS["focus_outline"]} 13%, {DARK_THEME_TOKENS["page_background"]});
    --wos-accent-mid: color-mix(in srgb, {DARK_THEME_TOKENS["focus_outline"]} 30%, {DARK_THEME_TOKENS["page_background"]});
    --wos-positive-soft: color-mix(in srgb, #2f8f6b 16%, {DARK_THEME_TOKENS["page_background"]});
    --wos-caution-soft: color-mix(in srgb, #b7791f 15%, {DARK_THEME_TOKENS["page_background"]});
    --wos-line: {DARK_THEME_TOKENS["subtle_border"]};
    --wos-accent: {DARK_THEME_TOKENS["focus_outline"]};
    --wos-input-fg: {DARK_THEME_TOKENS["input_text"]};
    --wos-input-bg: {DARK_THEME_TOKENS["input_background"]};
    --wos-placeholder: {DARK_THEME_TOKENS["placeholder_text"]};
    --wos-chip-fg: {DARK_THEME_TOKENS["chip_text"]};
    --wos-chip-bg: {DARK_THEME_TOKENS["chip_background"]};
    --wos-disabled: {DARK_THEME_TOKENS["disabled_text"]};
  }}
}}

.stApp {{ color: var(--wos-ink); background: var(--wos-page-bg); }}
.block-container {{ box-sizing: border-box; width: 100%; max-width: 1440px; padding-top: 2.5rem; padding-bottom: 3rem; overflow-x: hidden; }}
#MainMenu, footer {{ visibility: hidden; }}

.wos-shell-wordmark {{ color: var(--wos-ink); font-weight: 750; letter-spacing: -0.02em; }}
.wos-conversation-state {{ max-width: 780px; margin: 10vh auto 0; }}
.wos-conversation-user {{ color: var(--wos-muted); font-size: 1rem; padding-left: 1rem; border-left: 2px solid var(--wos-line); margin: 2rem 0; }}
.wos-conversation-answer {{ color: var(--wos-ink); font-size: clamp(1.25rem, 2.2vw, 1.75rem); line-height: 1.5; max-width: 760px; }}
.wos-enough {{ color: var(--wos-muted); font-size: 1rem; line-height: 1.6; margin: 1.4rem 0 2rem; }}
.wos-interim-workspace {{ max-width: 1040px; margin: 1rem auto 0; }}
.wos-picture {{ max-width: 1280px; margin: 2.5rem auto 0; }}
.wos-picture-title {{ color: var(--wos-ink); font-size: clamp(2.4rem, 5vw, 4rem); line-height: 1.06; letter-spacing: -0.045em; margin: 0.8rem 0 1rem; }}
.wos-picture-section {{ display: grid; grid-template-columns: minmax(11rem, 0.7fr) 1.5fr; column-gap: 3rem; padding: 1.6rem 0; border-top: 1px solid var(--wos-line); }}
.wos-picture-hero {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: var(--wos-line); border: 1px solid var(--wos-line); border-radius: 1.1rem; overflow: hidden; margin: 2.4rem 0 1rem; }}
.wos-picture-hero-cell {{ background: var(--wos-raised); padding: 1.4rem; min-height: 7rem; }}
.wos-picture-hero-cell span, .wos-picture-retirement-callout span {{ display: block; color: var(--wos-muted); font-size: 0.78rem; letter-spacing: 0.035em; text-transform: uppercase; }}
.wos-picture-hero-cell strong {{ display: block; color: var(--wos-ink); font-size: clamp(1.25rem, 2.2vw, 2rem); letter-spacing: -0.035em; margin-top: 1.1rem; }}
.wos-picture-retirement-callout {{ display: grid; grid-template-columns: 1.2fr 1fr; align-items: center; gap: 0.4rem 2rem; padding: 1.2rem 1.4rem; border-radius: 0.9rem; background: var(--wos-accent-soft); margin-bottom: 2.8rem; }}
.wos-picture-retirement-callout strong {{ color: var(--wos-ink); font-size: 1.35rem; }}
.wos-picture-retirement-callout small {{ grid-column: 2; color: var(--wos-muted); }}
.wos-picture-section h2 {{ grid-row: 1 / span 20; color: var(--wos-ink); font-size: 1rem; margin: 0; }}
.wos-picture-summary-row {{ grid-column: 2; display: flex; justify-content: space-between; gap: 2rem; padding: 0.35rem 0; }}
.wos-picture-summary-row span {{ color: var(--wos-muted); }}
.wos-picture-summary-row strong {{ color: var(--wos-ink); text-align: right; font-weight: 600; }}
.wos-missing {{ grid-column: 2; color: var(--wos-muted); margin: 0; }}

.wos-picture-metric-grid, .wos-metric-grid, .wos-g002-outcomes, .wos-assumption-grid {{ display: grid; gap: 1rem; margin: 2.4rem 0 1rem; }}
.wos-picture-metric-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
.wos-metric-grid, .wos-g002-outcomes {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
.wos-assumption-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
.wos-metric-card {{ box-sizing: border-box; min-width: 0; padding: 1.35rem; border: 1px solid var(--wos-line); border-radius: 1rem; background: var(--wos-raised); }}
.wos-metric-card > span, .wos-subsection-label, .wos-record-type, .wos-domain-card > span, .wos-limit-panel > div > span {{ display: block; color: var(--wos-muted); font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }}
.wos-metric-card > strong {{ display: block; color: var(--wos-ink); font-size: clamp(1.3rem, 2.2vw, 2rem); letter-spacing: -0.035em; line-height: 1.05; margin: 1.25rem 0 0.7rem; overflow-wrap: anywhere; }}
.wos-metric-card > small, .wos-domain-card > small, .wos-holding-card > small {{ display: block; color: var(--wos-muted); font-size: 0.78rem; line-height: 1.45; }}
.wos-focus-heading {{ border-top: 1px solid var(--wos-line); padding-top: 2rem; margin-top: 3.25rem; }}
.wos-focus-heading h2 {{ color: var(--wos-ink); font-size: clamp(1.55rem, 2.5vw, 2.25rem); letter-spacing: -0.03em; margin: 0; }}
.wos-focus-heading p {{ color: var(--wos-muted); line-height: 1.55; max-width: 720px; margin: 0.55rem 0 0; }}
.wos-boundary-map {{ display: grid; grid-template-columns: minmax(10rem, 0.7fr) minmax(0, 2.6fr) minmax(12rem, 1fr); gap: 0.8rem; align-items: stretch; margin-top: 1.5rem; }}
.wos-boundary-map > div {{ border-radius: 1rem; padding: 1.25rem; }}
.wos-boundary-label {{ border: 1px solid var(--wos-line); background: var(--wos-soft); }}
.wos-boundary-planning {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.8rem; background: var(--wos-accent-soft); border: 1px solid var(--wos-accent-mid); }}
.wos-boundary-planning > div {{ border-right: 1px solid var(--wos-accent-mid); padding-right: 0.7rem; }}
.wos-boundary-planning > div:nth-child(3) {{ border-right: 0; }}
.wos-boundary-planning > strong {{ grid-column: 1 / -1; color: var(--wos-ink); font-size: 1.5rem; margin-top: 0.9rem; }}
.wos-boundary-planning > em {{ grid-column: 1 / -1; color: var(--wos-muted); font-size: 0.76rem; font-style: normal; margin-top: -0.65rem; }}
.wos-boundary-home {{ display: flex; flex-direction: column; justify-content: space-between; background: var(--wos-caution-soft); border: 1px dashed var(--wos-line); }}
.wos-boundary-map span {{ display: block; color: var(--wos-ink); font-size: 0.86rem; font-weight: 700; line-height: 1.35; }}
.wos-boundary-map small {{ display: block; color: var(--wos-muted); font-size: 0.72rem; line-height: 1.4; margin-top: 0.35rem; }}
.wos-boundary-home strong {{ color: var(--wos-ink); font-size: 1.35rem; margin-top: 1.3rem; }}
.wos-subsection-label {{ margin: 1.8rem 0 0.7rem; }}
.wos-record-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 1rem; }}
.wos-holding-card, .wos-domain-card, .wos-property-card {{ box-sizing: border-box; border: 1px solid var(--wos-line); border-radius: 1rem; background: var(--wos-raised); padding: 1.3rem; min-width: 0; }}
.wos-holding-card h3, .wos-domain-card h3, .wos-property-card h3 {{ color: var(--wos-ink); font-size: 1.05rem; margin: 0.55rem 0 1rem; }}
.wos-holding-card > strong, .wos-domain-card > strong {{ display: block; color: var(--wos-ink); font-size: 1.55rem; margin-bottom: 0.65rem; }}
.wos-property-grid {{ display: grid; gap: 1rem; margin-top: 1.2rem; }}
.wos-status-pill {{ display: inline-block; color: var(--wos-accent); background: var(--wos-accent-soft); border-radius: 999px; padding: 0.3rem 0.65rem; font-size: 0.72rem; }}
.wos-mini-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; }}
.wos-mini-grid small {{ display: block; color: var(--wos-muted); font-size: 0.72rem; margin-bottom: 0.35rem; }}
.wos-mini-grid strong {{ display: block; color: var(--wos-ink); font-size: 1rem; overflow-wrap: anywhere; }}
.wos-property-card p {{ color: var(--wos-muted); font-size: 0.8rem; margin: 1.2rem 0 0; }}
.wos-residence-boundary {{ display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; align-items: center; margin-top: 3.25rem; padding: 1.6rem; background: var(--wos-caution-soft); border: 1px dashed var(--wos-line); border-radius: 1.1rem; }}
.wos-residence-boundary h2 {{ color: var(--wos-ink); margin: 0.45rem 0; }}
.wos-residence-boundary p {{ color: var(--wos-secondary); line-height: 1.5; margin: 0; }}

.wos-g002-workspace {{ max-width: 1280px; margin: 1rem auto 0; }}
.wos-g002-title {{ color: var(--wos-ink); font-size: clamp(2.5rem, 5vw, 4.6rem); line-height: 1.02; letter-spacing: -0.055em; margin: 0.7rem 0 1.4rem; max-width: 960px; }}
.wos-g002-hero {{ box-sizing: border-box; width: 100%; max-width: 100%; padding: clamp(1.5rem, 3vw, 2.6rem); border-radius: 1.3rem; background: var(--wos-positive-soft); border: 1px solid color-mix(in srgb, #2f8f6b 38%, var(--wos-page-bg)); }}
.wos-g002-hero > span {{ color: var(--wos-accent); font-size: 0.75rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; }}
.wos-g002-hero h2 {{ color: var(--wos-ink); font-size: clamp(1.6rem, 3vw, 2.75rem); line-height: 1.18; letter-spacing: -0.035em; max-width: 900px; overflow-wrap: break-word; margin: 0.75rem 0; }}
.wos-g002-hero p {{ color: var(--wos-secondary); line-height: 1.6; max-width: 950px; margin: 0; }}
.wos-g002-outcomes {{ margin-top: 1.2rem; }}
.wos-causal-bridge {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.75rem; margin-top: 1.4rem; }}
.wos-bridge-step {{ box-sizing: border-box; position: relative; min-width: 0; padding: 1.15rem; border: 1px solid var(--wos-line); border-radius: 1rem; background: var(--wos-raised); }}
.wos-bridge-step:not(:last-child)::after {{ content: "→"; position: absolute; right: -0.75rem; top: 50%; z-index: 2; width: 0.75rem; color: var(--wos-muted); text-align: center; }}
.wos-step-number {{ display: grid; place-items: center; width: 1.6rem; height: 1.6rem; border-radius: 50%; background: var(--wos-accent-soft); color: var(--wos-accent); font-size: 0.72rem; font-weight: 750; }}
.wos-bridge-step h3 {{ color: var(--wos-muted); font-size: 0.76rem; line-height: 1.35; margin: 0.8rem 0 0.5rem; min-height: 2rem; }}
.wos-bridge-step strong {{ display: block; color: var(--wos-ink); font-size: clamp(1rem, 1.6vw, 1.35rem); letter-spacing: -0.025em; overflow-wrap: anywhere; }}
.wos-bridge-step p {{ color: var(--wos-muted); font-size: 0.72rem; line-height: 1.45; margin: 0.8rem 0 0; }}
.wos-limit-panel {{ display: grid; grid-template-columns: 0.8fr 1.5fr; gap: 1px; overflow: hidden; margin-top: 1.2rem; border: 1px solid var(--wos-line); border-radius: 1rem; background: var(--wos-line); }}
.wos-limit-panel > div {{ padding: 1.35rem; background: var(--wos-raised); }}
.wos-limit-panel h3 {{ color: var(--wos-ink); font-size: 1rem; margin: 0.5rem 0; }}
.wos-limit-panel p {{ color: var(--wos-muted); font-size: 0.86rem; line-height: 1.55; margin: 0; }}

.wos-decision-workspace {{ max-width: 1280px; margin: 1rem auto 0; }}
.wos-decision-title {{ color: var(--wos-ink); font-size: clamp(2.5rem, 5vw, 4.6rem); line-height: 1.02; letter-spacing: -0.055em; margin: 0.7rem 0 1.4rem; max-width: 980px; }}
.wos-decision-hero {{ box-sizing: border-box; width: 100%; padding: clamp(1.5rem, 3vw, 2.6rem); border: 1px solid var(--wos-accent-mid); border-radius: 1.3rem; background: var(--wos-accent-soft); }}
.wos-decision-hero > span {{ color: var(--wos-accent); font-size: 0.75rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; }}
.wos-decision-hero h2 {{ color: var(--wos-ink); font-size: clamp(1.6rem, 3vw, 2.75rem); line-height: 1.18; letter-spacing: -0.035em; max-width: 950px; margin: 0.75rem 0; }}
.wos-decision-hero p {{ color: var(--wos-secondary); line-height: 1.6; max-width: 980px; margin: 0; }}
.wos-two-metric-grid, .wos-three-metric-grid, .wos-four-metric-grid {{ display: grid; gap: 1rem; margin: 1.2rem 0 1rem; }}
.wos-two-metric-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
.wos-three-metric-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
.wos-four-metric-grid {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
.wos-concentration-visual {{ display: grid; gap: 1rem; margin: 1.4rem 0; }}
.wos-concentration-row {{ display: grid; grid-template-columns: minmax(11rem, 0.7fr) minmax(0, 2fr); gap: 1.4rem; align-items: center; padding: 1.2rem 1.35rem; border: 1px solid var(--wos-line); border-radius: 1rem; background: var(--wos-raised); }}
.wos-concentration-row > div:first-child {{ display: flex; justify-content: space-between; gap: 1rem; align-items: baseline; }}
.wos-concentration-row span {{ color: var(--wos-muted); font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }}
.wos-concentration-row strong {{ color: var(--wos-ink); font-size: 1.45rem; }}
.wos-concentration-track {{ height: 1.25rem; overflow: hidden; border-radius: 999px; background: var(--wos-soft); border: 1px solid var(--wos-line); }}
.wos-concentration-track i {{ display: block; height: 100%; min-width: 0.35rem; border-radius: inherit; background: var(--wos-accent); }}
.wos-definition-panel {{ display: grid; grid-template-columns: 1.35fr 1fr; gap: 2rem; align-items: center; padding: 1.4rem; border-radius: 1rem; background: var(--wos-raised); border: 1px solid var(--wos-line); }}
.wos-definition-panel > div > span {{ color: var(--wos-accent); font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }}
.wos-definition-panel h3 {{ color: var(--wos-ink); margin: 0.45rem 0; }}
.wos-definition-panel p {{ color: var(--wos-muted); line-height: 1.5; margin: 0; }}
.wos-decision-flow {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0.85rem; margin-top: 1.4rem; }}
.wos-flow-step, .wos-cash-step {{ box-sizing: border-box; min-width: 0; padding: 1.2rem; border: 1px solid var(--wos-line); border-radius: 1rem; background: var(--wos-raised); }}
.wos-flow-step h3, .wos-cash-step h3, .wos-milestone-card h3 {{ color: var(--wos-muted); font-size: 0.78rem; line-height: 1.35; margin: 0.8rem 0 0.5rem; }}
.wos-flow-step strong, .wos-cash-step strong {{ display: block; color: var(--wos-ink); font-size: clamp(1rem, 1.6vw, 1.35rem); line-height: 1.3; overflow-wrap: anywhere; }}
.wos-flow-step p, .wos-milestone-card p {{ color: var(--wos-muted); font-size: 0.75rem; line-height: 1.45; margin: 0.75rem 0 0; }}
.wos-milestone-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr)); gap: 0.8rem; }}
.wos-milestone-card {{ padding: 1rem 1.1rem; border-left: 2px solid var(--wos-line); background: color-mix(in srgb, var(--wos-raised) 78%, transparent); }}
.wos-milestone-card > span {{ color: var(--wos-accent); font-size: 0.76rem; font-weight: 700; }}
.wos-selected-milestone {{ border-left-color: var(--wos-accent); background: var(--wos-accent-soft); }}
.wos-cash-bridge {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); gap: 0.75rem; margin: 1.4rem 0; }}
.wos-cash-step > span {{ color: var(--wos-accent); font-size: 0.7rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }}
.wos-context-grid {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1px; overflow: hidden; border: 1px solid var(--wos-line); border-radius: 1rem; background: var(--wos-line); }}
.wos-context-cell {{ min-width: 0; padding: 1rem; background: var(--wos-raised); }}
.wos-context-cell span {{ display: block; color: var(--wos-muted); font-size: 0.72rem; min-height: 2rem; }}
.wos-context-cell strong {{ display: block; color: var(--wos-ink); font-size: 1rem; margin-top: 0.5rem; overflow-wrap: anywhere; }}

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
.wos-interim-workspace .wos-section {{ border: 0; background: var(--wos-raised); border-radius: 1rem; padding: 1.25rem 1.4rem; margin: 0.8rem 0; }}
.wos-interim-workspace .wos-section h3 {{ color: var(--wos-accent); font-size: 0.78rem; letter-spacing: 0.06em; text-transform: uppercase; }}
.wos-interim-workspace .wos-evidence-row span:last-child {{ color: var(--wos-ink); font-size: 1.12rem; font-weight: 650; }}
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

@media (max-width: 1200px) {{
  .wos-picture-metric-grid, .wos-assumption-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .wos-causal-bridge {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
  .wos-bridge-step:not(:last-child)::after {{ content: none; }}
  .wos-four-metric-grid, .wos-decision-flow {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}

@media (max-width: {RESPONSIVE_BREAKPOINT_PX}px) {{
  div[data-testid="stHorizontalBlock"]:has(.wos-pane-label) {{ flex-direction: column; gap: 2rem; }}
  div[data-testid="stHorizontalBlock"]:has(.wos-pane-label) > div[data-testid="stColumn"] {{ width: 100% !important; flex: 1 1 100% !important; }}
  div[data-testid="stColumn"]:has(.wos-workspace) {{ border-left: 0; border-top: 1px solid var(--wos-line); padding: 2rem 0 0; }}
  .wos-picture-row, .wos-evidence-row {{ grid-template-columns: minmax(7rem, 1fr) 1.25fr auto; }}
  .wos-evidence-row {{ grid-template-columns: minmax(7rem, 1fr) 1.25fr; }}
  .wos-home {{ margin-top: 3vh; }}
  .wos-conversation-state {{ margin-top: 4vh; }}
  .wos-visual-workspace {{ max-width: 100%; }}
  .wos-interim-workspace, .wos-picture {{ max-width: 100%; }}
  .wos-g002-workspace {{ max-width: 100%; }}
  .wos-picture-metric-grid, .wos-metric-grid, .wos-g002-outcomes, .wos-assumption-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .wos-boundary-map {{ grid-template-columns: 1fr; }}
  .wos-causal-bridge {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .wos-bridge-step:not(:last-child)::after {{ content: none; }}
  .wos-limit-panel {{ grid-template-columns: 1fr; }}
  .wos-decision-workspace {{ max-width: 100%; }}
  .wos-three-metric-grid, .wos-context-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .wos-concentration-row, .wos-definition-panel {{ grid-template-columns: 1fr; }}
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
  .wos-picture-section {{ grid-template-columns: 1fr; row-gap: 0.8rem; }}
  .wos-picture-hero {{ grid-template-columns: 1fr 1fr; }}
  .wos-picture-retirement-callout {{ grid-template-columns: 1fr; }}
  .wos-picture-retirement-callout small {{ grid-column: 1; }}
  .wos-picture-section h2, .wos-picture-summary-row, .wos-missing {{ grid-column: 1; grid-row: auto; }}
  .wos-picture-summary-row {{ align-items: baseline; }}
  .wos-picture-metric-grid, .wos-metric-grid, .wos-g002-outcomes, .wos-assumption-grid, .wos-record-grid, .wos-causal-bridge {{ grid-template-columns: 1fr; }}
  .wos-boundary-planning, .wos-mini-grid, .wos-residence-boundary {{ grid-template-columns: 1fr; }}
  .wos-boundary-planning > div {{ border-right: 0; border-bottom: 1px solid var(--wos-accent-mid); padding: 0 0 0.7rem; }}
  .wos-residence-boundary {{ gap: 1.2rem; }}
  .wos-two-metric-grid, .wos-three-metric-grid, .wos-four-metric-grid, .wos-decision-flow, .wos-context-grid {{ grid-template-columns: 1fr; }}
  .wos-concentration-row > div:first-child {{ align-items: center; }}
}}
</style>
"""


def apply_styles() -> None:
    """Inject the prototype's theme-aware visual treatment."""

    st.markdown(EXPERIENCE_CSS, unsafe_allow_html=True)

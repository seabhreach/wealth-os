# Wealth OS Recovery Status

- Recovery date: 2026-08-27
- Source branch: `master`
- Source commit: `8a458e310eee0d4a407ad47cd21cb97c7dcb47bd`
- Source release: `v0.2.0`
- Recovery branch: `recovery/v0.3-experience`
- Python: 3.13.15
- pandas: 2.3.3
- Streamlit: 1.62.0
- Recovery reason: post-v0.2 work was lost with the development laptop.

The Wealth OS v0.2 financial behaviour is the protected recovery baseline. Documentation and
Experience reconstruction must not alter financial semantics unless a later explicitly approved
task requires it.

## Recovered v0.2 Components

- `engine/`
- `dashboard/`
- `data/example_household.yaml`
- `data/tax/ireland_2026.yaml`
- `docs/BASELINE_AUDIT_v0.2.md`
- `docs/TAX_ENGINE.md`
- `RELEASE_NOTES_v0.2.0.md`
- `AGENTS.md`

## Reconstructed Post-v0.2 Documentation

- `docs/PRODUCT_VISION.md`
- `docs/RFC-010_DECISION_ENGINE.md`
- `docs/RFC-011_THE_WEALTH_OS_EXPERIENCE.md`
- `docs/RFC-012_DISCOVERY_MODEL.md`
- `docs/FIRST_RUN_JOURNEY.md`
- `docs/CONVERSATION_AND_WORKSPACE_MODEL.md`
- `docs/EXPERIENCE_PROTOTYPE.md`
- `docs/GOAL_LIBRARY.md`
- `docs/QUESTION_LIBRARY.md`
- `docs/EXPERIENCE_LIVE_DATA_CONTRACT.md`

Post-v0.2 product and architecture documents were reconstructed from the project conversation
history after loss of the development laptop. Their intent and major approved decisions have been
restored, but exact original wording may differ.

## Known Missing Post-v0.2 Implementation

The live Experience implementation, deterministic adapters, and adaptive conversation services
remain missing.

## Experience Prototype Shell Reconstruction

The first conversation-first Experience application shell has been reconstructed from the
recovered product documentation and project conversation history. It is a mock-only Streamlit
prototype with five scripted goal journeys, a minimal Home, side-by-side conversation and
Workspace views, progressive Financial Picture evidence, and isolated illustrative data.

- The shell is mock-only and does not use live Financial Picture data.
- There is no integration with simulation, tax, reporting, the Decision Engine, or other live
  financial services.
- No LLM or external AI service is used.
- Exact original prototype code could not be recovered.
- The reconstructed behavior follows the approved product and experience design intent.

The shell validates experience behavior only. It does not change or extend v0.2 financial
calculations or semantics.

## Mock Journey Branching and Evidence Progression

The Phase 2 / Phase 3 mock journey behavior was reconstructed from project conversation history
and the recovered Product Vision, Goal Library, Question Library, Discovery Model, and Experience
documents. The five finite journeys now retain their recovered Goal IDs and traceable Question
Library IDs while keeping those internal identifiers out of normal customer-facing views.

The reconstructed prototype includes bounded household, property-funding, future-award, and
spending-duration branches; Known, Estimated, Unknown, and Not relevant answer states; explicit
enough-information transitions; progressively revealed evidence with a declared purpose; one
in-place refinement per journey; predefined saved Workspaces; and a hidden developer review
projection. The cash-decline journey uses the existing mock Financial Picture and asks no new
data-collection questions.

- This behavior is reconstructed from recovered intent and is not byte-for-byte original code.
- The implementation remains mock-only and has no live Financial Picture or financial-engine
  integration.
- No LLM or external AI service is present.
- No financial calculations or v0.2 financial semantics changed.

## Validation Results

- Ruff lint: passed for the full repository after mock journey reconstruction.
- Ruff formatting check: passed; 109 files were already formatted.
- Strict MyPy: passed; no issues found in 85 source files.
- Focused Experience prototype tests: passed; 43 tests covering branching, stable question IDs,
  information quality, progressive evidence, refinements, saved Workspaces, reset, review state,
  visual guardrails, and architecture boundaries.
- Full Pytest suite: passed; 143 tests.
- Golden baseline tests: passed; 5 tests.
- Tax engine, integration, and reporting tests: passed; 15 tests.
- Pension growth tests: passed; 5 tests.
- Retirement what-if tests: passed; 6 tests.
- Dashboard navigation tests: passed; 7 tests.
- Distribution build: passed; `wealth_os-0.2.0.tar.gz` and
  `wealth_os-0.2.0-py3-none-any.whl` were built successfully.
- Headless Streamlit launch: passed; the health endpoint returned HTTP 200 with `ok`, the root
  page returned HTTP 200, and no application exception was reported.

## Recovery Compatibility Corrections

### Pandas annotation compatibility

- `pd.io.formats.style.Styler` failed during runtime annotation evaluation in a fresh pandas
  environment.
- `pd.Series[str]` also failed when evaluated at runtime because `Series` was not runtime
  subscriptable in this environment.
- The recovery correction imports `Styler` explicitly from `pandas.io.formats.style`, with one
  narrowly targeted `# type: ignore[import-untyped]` because that internal pandas submodule does
  not provide usable typing information in this environment.
- Postponed annotation evaluation is enabled with `from __future__ import annotations`.
- No function bodies changed.

### Streamlit AppTest path compatibility

- The v0.2 test passed a repository-relative `dashboard/app.py` path to `AppTest.from_file`.
- Streamlit 1.62 resolves that relative path against the test module, producing the nonexistent
  `tests/dashboard/app.py` path.
- The test now constructs the app path from the repository root before calling
  `AppTest.from_file`.
- No dashboard behaviour, assertions, or expected financial values changed.

These are environment and test compatibility corrections only. Financial calculations, outputs,
and semantics are unchanged. Dependency modernisation is deferred until after recovery.

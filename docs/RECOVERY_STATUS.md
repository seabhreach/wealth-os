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

Production Financial Picture persistence, confirmed update workflows, adaptive conversation
services, and AI orchestration remain missing.

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

## Phase 4 Live Deterministic Experience Integration

The lost Phase 4 live integration has been behaviorally reconstructed from the recovered live-data
contract and the actual v0.2 application boundaries. It is not a byte-for-byte restoration of the
original source.

The implemented read-only flow is:

```text
validated example configuration
→ customer-relevant Financial Picture adapter
→ existing ScenarioOverride / run_scenario / annual reporting APIs
→ frozen live evidence and provenance
→ presentation-only Experience renderer
```

Live and mock modes are visibly separate and cannot share evidence within a Workspace. Live mode
uses `data/example_household.yaml`; mock mode retains the reconstructed scripted fixtures. The live
renderer formats and arranges evidence but performs no financial calculations.

Supported live goals are:

- G-001: baseline versus a bounded temporary retirement-age override.
- G-002: configured planned-property inclusion versus exclusion.
- G-003: the existing sell-on-vest and retain employer-equity policies, including only the
  concentration metric already exposed by v0.2.
- G-004: baseline versus a permanent retirement-spending override.
- G-005: a selected existing reporting year explained through `AnnualFinancialStatement` and
  `AnnualCalculationTrace`, with no new data collection.

Financing and mortgages remain unsupported. Temporary multi-year retirement spending remains
unsupported. No mortgage, spending-schedule, concentration, tax, pension, withdrawal, property,
or equity-compensation calculation was added to the Experience. Unsupported requests produce
explicit limitation evidence.

Every live Workspace includes a stable baseline identifier, deterministic Financial Picture and
result fingerprints, Goal ID, sorted scenario overrides, simulation identifier, tax-rule file
fingerprint where applicable, and evidence-policy version. Generation time is recorded but is
excluded from deterministic identity. Scenario runs create validated temporary copies, expose a
proposed-update preview where relevant, never persist changes, and leave the loaded baseline
unchanged.

There is no LLM, generative explanation, semantic routing, embedding, vector database, or external
AI integration. Live explanations are deterministic and template-backed.

## Validation Results

- Ruff lint: passed for the full repository after live deterministic Experience reconstruction.
- Ruff formatting check: passed; 117 files were already formatted.
- Strict MyPy: passed; no issues found in 93 source files.
- Focused Experience tests: passed; 62 tests (43 mock and 19 live) covering branching, stable
  question IDs, information quality, progressive evidence, refinements, saved Workspaces,
  immutable live evidence, deterministic provenance, supported scenario mappings, explicit
  limitations, and architecture boundaries.
- Full Pytest suite: passed; 162 tests.
- Golden baseline tests: passed; 5 tests.
- Tax engine, integration, and reporting tests: passed; 15 tests.
- Pension growth tests: passed; 5 tests.
- Retirement what-if tests: passed; 6 tests.
- Dashboard navigation tests: passed; 7 tests.
- Distribution build: passed; `wealth_os-0.2.0.tar.gz` and
  `wealth_os-0.2.0-py3-none-any.whl` were built successfully.
- Headless Streamlit launches: passed for both the v0.2 dashboard and the Experience app; each
  health endpoint returned HTTP 200 with `ok`, each root page returned HTTP 200, and neither app
  reported an application exception.

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

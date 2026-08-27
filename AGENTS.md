# AGENTS.md

## Mission

Build Wealth OS as production-quality software that helps people understand and explore their
financial future without presenting planning illustrations as regulated advice.

## Read First

Read current authority in this order:

1. `docs/PRODUCT_VISION.md`
2. `docs/RFC-012_DISCOVERY_MODEL.md`
3. `docs/00_START_HERE.md`
4. `README.md`
5. `docs/TAX_ENGINE.md`
6. `docs/BASELINE_AUDIT_v0.2.md`
7. `docs/RFC-011_THE_WEALTH_OS_EXPERIENCE.md`
8. `docs/CONVERSATION_AND_WORKSPACE_MODEL.md`
9. the active RFC, work order, or recovery task

`docs/MVP_SPEC.md` and `docs/archive/` are historical context. They do not override current
product authority or released v0.2 behavioral authority.

If current authority documents conflict, stop and report the conflict before changing behavior.

## Product Vision Authority

Every architectural, product, UX, reporting, and implementation decision must be consistent with
`docs/PRODUCT_VISION.md`.

Where other documentation conflicts, Product Vision takes precedence unless an approved RFC
explicitly documents the exception. Product Vision does not silently change released financial
semantics; behavioral changes require explicit approval, specification, and tests.

## Discovery Model Authority

Future conversational features must be built on the Discovery Model in
`docs/RFC-012_DISCOVERY_MODEL.md`.

- Model information requirements rather than scripted questions.
- Question wording belongs to the AI conversation layer.
- The platform owns deterministic requirements, validation, confidence, and confirmation.
- Deterministic engines remain independent of conversational wording.
- The Question Library is a transitional prototype, example, and test artifact only.

## Engineering Rules

- Use Domain-Driven Design where it clarifies boundaries and invariants.
- Business and financial logic belongs only in `engine/`.
- Dashboard and experience layers contain presentation and orchestration only.
- Deterministic engines own calculations; AI must not invent financial truth.
- Preserve baseline immutability during temporary scenario exploration.
- Stay within the active task or approved work order.
- Add or update tests when behavior changes.
- Update documentation when behavior or authority changes.
- Keep advice boundaries and limitations explicit.

## Protected Recovery Baseline

Wealth OS v0.2 financial behavior is the protected recovery baseline. Documentation and Experience
reconstruction must not alter simulation, tax, reporting, configuration, or financial semantics
unless a later explicitly approved task requires it.

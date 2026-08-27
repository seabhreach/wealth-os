# Wealth OS — Start Here

## Documentation Authority

Read Wealth OS documentation according to its purpose:

1. [PRODUCT_VISION.md](PRODUCT_VISION.md) is the active product authority for mission,
   principles, language, trust, and experience direction.
2. [RFC-012_DISCOVERY_MODEL.md](RFC-012_DISCOVERY_MODEL.md) is the active architecture for future
   conversational discovery and information requirements.
3. [../README.md](../README.md), [TAX_ENGINE.md](TAX_ENGINE.md), and
   [BASELINE_AUDIT_v0.2.md](BASELINE_AUDIT_v0.2.md) are current behavioral authority for the
   released v0.2 implementation.
4. Approved RFCs define bounded future architecture. They do not change v0.2 behavior until an
   implementation task explicitly updates behavior, tests, and released documentation.

If product or experience documentation conflicts, Product Vision takes precedence unless an
approved RFC explicitly records an exception. If future direction conflicts with current
behavioral authority, preserve current behavior until a separately approved behavior change.

## Active Product and Architecture Documents

- [PRODUCT_VISION.md](PRODUCT_VISION.md)
- [RFC-010_DECISION_ENGINE.md](RFC-010_DECISION_ENGINE.md)
- [RFC-011_THE_WEALTH_OS_EXPERIENCE.md](RFC-011_THE_WEALTH_OS_EXPERIENCE.md)
- [RFC-012_DISCOVERY_MODEL.md](RFC-012_DISCOVERY_MODEL.md)
- [CONVERSATION_AND_WORKSPACE_MODEL.md](CONVERSATION_AND_WORKSPACE_MODEL.md)
- [FIRST_RUN_JOURNEY.md](FIRST_RUN_JOURNEY.md)
- [EXPERIENCE_PROTOTYPE.md](EXPERIENCE_PROTOTYPE.md)
- [GOAL_LIBRARY.md](GOAL_LIBRARY.md)
- [QUESTION_LIBRARY.md](QUESTION_LIBRARY.md)
- [EXPERIENCE_LIVE_DATA_CONTRACT.md](EXPERIENCE_LIVE_DATA_CONTRACT.md)

## Released v0.2 Baseline

Wealth OS v0.2.0 is a deterministic, single-household retirement-planning proof of concept with
Advisor Mode, owner-specific pension and State Pension assumptions, and opt-in Irish tax planning.

- Setup and current behavior summary: [../README.md](../README.md)
- Audited deterministic outputs: [BASELINE_AUDIT_v0.2.md](BASELINE_AUDIT_v0.2.md)
- Tax behavior and boundaries: [TAX_ENGINE.md](TAX_ENGINE.md)
- Reference configuration: [../data/example_household.yaml](../data/example_household.yaml)
- Recovery provenance and validation: [RECOVERY_STATUS.md](RECOVERY_STATUS.md)

## Historical Documentation

[MVP_SPEC.md](MVP_SPEC.md) is superseded historical MVP documentation originating in the v0.1
design and later amended during v0.2 delivery. It is retained for context, but it is not current
behavioral authority. Earlier proposed domain design and work-order documents in [archive/](archive/)
are also historical and must not be used to infer unimplemented behavior.

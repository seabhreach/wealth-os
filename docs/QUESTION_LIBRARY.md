# Question Library

> **Transitional artifact:** The Question Library is useful for prototype journeys, UX
> validation, examples, and tests. It is **not** the long-term conversational architecture. The
> long-term architecture is [RFC-012: Discovery Model](RFC-012_DISCOVERY_MODEL.md), which models
> information requirements rather than scripts.

## Question Contract

Each prototype question records:

- ID and customer-facing wording;
- purpose and category;
- goals supported;
- ask and skip conditions;
- estimate/unknown handling;
- importance;
- what it unlocks;
- optional “why we ask” copy.

AI may vary wording and sequence. These examples must not become a mandatory interview.

## Shared and Retirement Questions

| ID | Customer-facing wording | Purpose / category | Goals | Conditions and handling | Importance / unlocks |
|---|---|---|---|---|---|
| Q-001 | “How old are you now?” | Current age / household | G-001 | Ask if unknown; verified or known preferred | Essential; projection horizon and retirement timing |
| Q-002 | “Is anyone else part of this financial plan?” | Household membership | G-001 | Skip when household scope is confirmed; unknown allowed initially | Essential; owner ages, income, pensions, tax scope |
| Q-004 | “What age would you like to explore retiring at?” | Target retirement age | G-001 | Ask when no target is expressed; estimate allowed | Essential; scenario override |
| Q-005 | “About how much do you have across cash, investments, and pensions?” | Opening resources | G-001 | Skip known current values; estimates allowed and labelled | Essential; first useful outlook |
| Q-008 | “What annual spending would you like retirement to support?” | Retirement spending | G-001, G-004 | Ask if absent; estimate/range allowed | Essential; funding target |
| Q-009 | “Should this first view use the current inflation assumption?” | Spending escalation | G-004 | Skip when confirmed assumption exists; unknown uses explicit baseline assumption | Helpful; future spending path |

## Investment Property Questions

| ID | Customer-facing wording | Purpose / category | Goals | Conditions and handling | Importance / unlocks |
|---|---|---|---|---|---|
| Q-010 | “When might you buy the property?” | Purchase timing | G-002 | Ask for planned property; estimate year allowed | Essential; purchase event |
| Q-011 | “What purchase price should we explore?” | Purchase cost | G-002 | Ask if absent; estimate/range allowed | Essential; liquidity effect |
| Q-012 | “How would the purchase be funded?” | Funding assumption | G-002 | Ask when financing is ambiguous; unknown must be explicit | Essential; valid scenario boundary |
| Q-013 | “What annual net rent and value growth should this illustration use?” | Income/value assumptions | G-002 | Estimates allowed; show exclusions | Essential; income and asset path |
| Q-015 | “How is the property expected to be owned?” | Ownership/tax allocation | G-002 | Ask only where ownership affects supported calculations; unknown permitted but may block tax comparison | Helpful or essential; ownership-sensitive evidence |

## Employer-Equity Questions

| ID | Customer-facing wording | Purpose / category | Goals | Conditions and handling | Importance / unlocks |
|---|---|---|---|---|---|
| Q-018 | “What employer-equity position do you hold today?” | Position identity/value | G-003 | Ask if not imported or known; estimate allowed | Essential; exposure baseline |
| Q-019 | “Are more grants or vesting events expected?” | Future equity compensation | G-003 | Skip if not applicable; estimate allowed | Essential when material; exposure timeline |
| Q-020 | “What price and currency assumptions should this exploration use?” | Valuation/FX | G-003 | Use explicit baseline if confirmed; unknown must be labelled | Essential; generic valuation |
| Q-021 | “What happens to shares when they vest in the current baseline?” | Disposal policy | G-003 | Skip when policy is known | Essential; baseline policy |
| Q-022 | “Which disposal-policy alternatives would you like to compare?” | Scenario set | G-003 | Ask only after baseline is understood; user-selected values only | Helpful; Strategy Explorer candidates |

## Higher-Spending Questions

| ID | Customer-facing wording | Purpose / category | Goals | Conditions and handling | Importance / unlocks |
|---|---|---|---|---|---|
| Q-024 | “What higher annual amount would you like to explore?” | Scenario target | G-004 | Ask when no amount was expressed; estimate/range allowed | Essential; comparison override |
| Q-025 | “Should the higher amount apply from retirement onward or for a limited period?” | Timing | G-004 | Ask when timing changes the result materially | Essential when ambiguous; scenario schedule |
| Q-026 | “Is this amount in today’s money?” | Value basis | G-004 | Skip if established; unknown uses visible assumption | Essential; inflation treatment |

## Cash-Decline Explanation

G-005 normally requires no new data collection when the existing Financial Picture and selected
projection contain sufficient evidence. Ask only for the year, chart, or scenario when the
reference is ambiguous. Do not ask unrelated profile questions to explain an already calculated
movement.

## Goal Mappings

- **Retire Earlier:** Q-001, Q-002, Q-004, Q-005, Q-008.
- **Investment Property:** Q-010–Q-013, plus Q-015 where ownership is material.
- **Employer Equity:** Q-018, Q-019, Q-020, Q-021, Q-022.
- **Higher Retirement Spending:** Q-008, Q-024, Q-025, Q-026, Q-009.
- **Cash Decline:** no new data collection when the Financial Picture is sufficient.

## “Every Question Earns Its Place” Checklist

Before asking, confirm:

1. Is the information material to the active goal?
2. Is it absent, stale, ambiguous, or below the required confidence?
3. Can a permitted estimate or explicit assumption produce useful value first?
4. Has the user already supplied it through conversation, editing, import, or another source?
5. Does the question unlock a named calculation, evidence item, constraint, or confidence gain?
6. Can the product explain why it is asking now?
7. Can “unknown,” “not relevant,” or “skip for now” be handled honestly?
8. Is the wording natural and free of advice or judgment?

If these conditions are not met, do not ask the question.

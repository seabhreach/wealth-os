# WO-001 Domain Model

> **Archived for v0.1.0.** This completed/superseded work order is retained for history only.
> It is not authoritative for the released MVP; see [../MVP_SPEC.md](../MVP_SPEC.md).

## Objective

Implement immutable domain entities.

## Read First

- docs/00_START_HERE.md
- RFC-001_Household_Aggregate.md
- docs/04_Domain_Model.md
- docs/05_Data_Dictionary.md
- docs/07_AI_Instructions.md

## In Scope

- Household
- Person
- Goal
- Scenario
- Timeline
- Money
- Currency

## Out of Scope

- Tax
- Property
- Pension
- RSUs
- Dashboard

## Requirements

- Pydantic v2
- Immutable models
- Validation
- Serialization
- Unit tests

## Done

Tests pass and no financial calculations are implemented.

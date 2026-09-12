"""Platform-owned validation for untrusted orchestration provider output."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from experience.orchestration.models import (
    FinancialPictureOperation,
    OrchestrationRequest,
    OrchestrationResponse,
    ProposalValidationState,
    SetScenarioValueAction,
)

_NUMBER = re.compile(r"(?<![A-Za-z])(?:€\s*)?(\d[\d,]*(?:\.\d+)?)\s*([kKmM])?")


def validate_provider_response(
    request: OrchestrationRequest,
    response: OrchestrationResponse,
) -> None:
    """Reject policy violations that schema validation alone cannot identify."""

    allowed_actions = set(request.allowed_actions)
    for action in response.deterministic_actions:
        if action.action_type not in allowed_actions:
            raise ValueError(f"Provider proposed unsupported action: {action.action_type}")

    for proposal in response.financial_picture_updates:
        if proposal.validation_state is not ProposalValidationState.VALID:
            raise ValueError("Invalid Financial Picture proposals cannot proceed to review.")

    numeric_claims = _extract_numbers(response.user_facing_draft)
    structured_numbers = _structured_numbers(response)
    unsupported = numeric_claims - structured_numbers
    if unsupported:
        raise ValueError(
            "User-facing draft contains numeric claims unsupported by structured "
            f"actions, proposals, or evidence requests: {sorted(unsupported)}"
        )


def _structured_numbers(response: OrchestrationResponse) -> set[Decimal]:
    values: set[Decimal] = set()
    for action in response.deterministic_actions:
        if isinstance(action, SetScenarioValueAction) and isinstance(action.value, (Decimal, int)):
            values.add(Decimal(action.value))
    for proposal in response.financial_picture_updates:
        if (
            proposal.operation is not FinancialPictureOperation.REMOVE
            and proposal.proposed_value is not None
        ):
            values.add(proposal.proposed_value.current_value)
    if response.explanation_request and response.explanation_request.calendar_year is not None:
        values.add(Decimal(response.explanation_request.calendar_year))
    return values


def _extract_numbers(text: str) -> set[Decimal]:
    values: set[Decimal] = set()
    for raw, suffix in _NUMBER.findall(text):
        try:
            value = Decimal(raw.replace(",", ""))
        except InvalidOperation:
            continue
        if suffix.casefold() == "k":
            value *= Decimal("1000")
        elif suffix.casefold() == "m":
            value *= Decimal("1000000")
        values.add(value)
    return values

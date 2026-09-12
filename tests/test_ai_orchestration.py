"""Contract tests for provider-neutral orchestration and its deterministic stub."""

from __future__ import annotations

from decimal import Decimal

import pytest
from experience.models import GoalId
from experience.orchestration.models import (
    ActionKind,
    ConversationIntent,
    EvidenceGroundedExplanation,
    ExplanationClaim,
    ExplanationEvidence,
    FinancialPictureTarget,
    OrchestrationRequest,
    OrchestrationResponse,
    ScenarioField,
    SetScenarioValueAction,
    UserMessage,
)
from experience.orchestration.service import OrchestrationService
from experience.orchestration.stub import DeterministicStubProvider
from experience.orchestration.validation import validate_provider_response
from pydantic import ValidationError

from engine.assets import InvestmentAssetType


def _request(text: str, *allowed_actions: ActionKind) -> OrchestrationRequest:
    return OrchestrationRequest(
        interaction_id="interaction-001",
        session_id="session-001",
        message=UserMessage(message_id="message-001", text=text),
        goal_id=GoalId.HIGHER_SPENDING,
        workspace_id="workspace-current",
        allowed_actions=allowed_actions,
    )


def test_bitcoin_creates_confirmable_canonical_holding_proposal_only() -> None:
    request = _request(
        "I've got about €50k in Bitcoin as well.",
        ActionKind.PROPOSE_FINANCIAL_PICTURE_UPDATE,
    )
    response = DeterministicStubProvider().interpret(request)

    assert response.intent is ConversationIntent.UPDATE_FINANCIAL_PICTURE
    assert len(response.financial_picture_updates) == 1
    proposal = response.financial_picture_updates[0]
    assert proposal.target is FinancialPictureTarget.TAXABLE_INVESTMENT_HOLDING
    assert proposal.confirmation_required is True
    assert proposal.proposed_value is not None
    assert proposal.proposed_value.asset_type is InvestmentAssetType.CRYPTOASSET
    assert proposal.proposed_value.current_value == Decimal("50000")
    assert proposal.holding_id == "holding-bitcoin-user-50000"
    assert request.relevant_facts == ()
    validate_provider_response(request, response)


def test_spending_creates_scenario_action_without_sustainability_claim() -> None:
    request = _request(
        "What if I spend €120k?",
        ActionKind.SET_SCENARIO_VALUE,
    )
    response = DeterministicStubProvider().interpret(request)

    assert response.intent is ConversationIntent.EXPLORE_SCENARIO
    assert response.financial_picture_updates == ()
    assert response.explanation_request is None
    assert response.deterministic_actions == (
        SetScenarioValueAction(
            field=ScenarioField.ANNUAL_RETIREMENT_SPENDING,
            value=Decimal("120000"),
        ),
    )
    assert "sustainable" not in response.user_facing_draft.casefold()
    assert "funded" not in response.user_facing_draft.casefold()
    validate_provider_response(request, response)


def test_cash_question_requests_existing_evidence_without_mutation() -> None:
    request = _request("Why does my cash fall in 2032?")
    response = DeterministicStubProvider().interpret(request)

    assert response.intent is ConversationIntent.EXPLAIN_EXISTING_RESULT
    assert response.explanation_request is not None
    assert response.explanation_request.calendar_year == 2032
    assert response.explanation_request.evidence_refs == (
        "g005-annual-statement",
        "g005-cash-trajectory",
    )
    assert response.financial_picture_updates == ()
    assert response.deterministic_actions == ()
    validate_provider_response(request, response)


def test_primary_residence_requires_mechanism_before_any_scenario() -> None:
    request = _request(
        "Could I use the house to retire at 57?",
        ActionKind.SET_SCENARIO_VALUE,
    )
    response = DeterministicStubProvider().interpret(request)

    assert response.intent is ConversationIntent.EXPLORE_SCENARIO
    assert response.ambiguity.requires_clarification is True
    assert "primary_residence" in response.ambiguity.topics
    assert {item.item_id for item in response.missing_information} == {
        "primary-residence-mechanism",
        "primary-residence-timing-and-costs",
    }
    assert response.financial_picture_updates == ()
    assert response.deterministic_actions == ()
    assert response.explanation_request is None
    assert "1500000" not in response.model_dump_json()
    validate_provider_response(request, response)


@pytest.mark.parametrize(
    "text,allowed",
    [
        (
            "I've got about €50k in Bitcoin as well.",
            (ActionKind.PROPOSE_FINANCIAL_PICTURE_UPDATE,),
        ),
        ("What if I spend €120k?", (ActionKind.SET_SCENARIO_VALUE,)),
        ("Why does my cash fall in 2032?", ()),
        ("Could I use the house to retire at 57?", (ActionKind.SET_SCENARIO_VALUE,)),
    ],
)
def test_stub_is_deterministic(text: str, allowed: tuple[ActionKind, ...]) -> None:
    request = _request(text, *allowed)
    provider = DeterministicStubProvider()

    assert provider.interpret(request) == provider.interpret(request)


def test_service_records_zero_cost_no_network_stub_telemetry() -> None:
    request = _request(
        "What if I spend €120k?",
        ActionKind.SET_SCENARIO_VALUE,
    )

    result = OrchestrationService(DeterministicStubProvider()).interpret(request)

    assert result.telemetry.provider == "stub"
    assert result.telemetry.model is None
    assert result.telemetry.input_tokens == 0
    assert result.telemetry.output_tokens == 0
    assert result.telemetry.estimated_cost == Decimal("0")
    assert result.telemetry.external_call is False
    assert result.telemetry.success is True


def test_schema_rejects_unsupported_action_type() -> None:
    with pytest.raises(ValidationError):
        OrchestrationResponse.model_validate(
            {
                "intent": "EXPLORE_SCENARIO",
                "deterministic_actions": [{"action_type": "CalculateRetirement", "value": 57}],
                "user_facing_draft": "I will calculate that.",
            }
        )


def test_schema_rejects_invalid_investment_taxonomy() -> None:
    with pytest.raises(ValidationError):
        OrchestrationResponse.model_validate(
            {
                "intent": "UPDATE_FINANCIAL_PICTURE",
                "financial_picture_updates": [
                    {
                        "proposal_id": "bad-taxonomy",
                        "operation": "ADD",
                        "target": "taxable_investment_holding",
                        "holding_id": "holding-reit",
                        "proposed_value": {
                            "holding_id": "holding-reit",
                            "name": "REIT",
                            "asset_type": "REIT",
                            "current_value": "50000",
                        },
                        "source": "user_supplied",
                        "confirmation_required": True,
                        "validation_state": "VALID",
                    }
                ],
                "user_facing_draft": "Please review this holding.",
            }
        )


def test_schema_rejects_illegal_primary_residence_mutation_target() -> None:
    with pytest.raises(ValidationError):
        OrchestrationResponse.model_validate(
            {
                "intent": "UPDATE_FINANCIAL_PICTURE",
                "financial_picture_updates": [
                    {
                        "proposal_id": "activate-home",
                        "operation": "UPDATE",
                        "target": "primary_residence_available_capital",
                        "holding_id": "home",
                        "proposed_value": None,
                        "source": "user_supplied",
                        "confirmation_required": True,
                        "validation_state": "VALID",
                    }
                ],
                "user_facing_draft": "I will activate the home.",
            }
        )


def test_platform_rejects_action_not_allowed_by_request() -> None:
    request = _request("What if I spend €120k?")
    response = DeterministicStubProvider().interpret(request)

    with pytest.raises(ValueError, match="unsupported action"):
        validate_provider_response(request, response)


def test_platform_rejects_unstructured_numeric_financial_claim() -> None:
    request = _request("Am I okay?")
    response = OrchestrationResponse(
        intent=ConversationIntent.ASK_GENERAL_FINANCIAL_QUESTION,
        user_facing_draft="Your sustainable spending is €999,000.",
    )

    with pytest.raises(ValueError, match="unsupported by structured"):
        validate_provider_response(request, response)


def test_explanation_rejects_missing_evidence_reference() -> None:
    with pytest.raises(ValidationError, match="unavailable evidence"):
        EvidenceGroundedExplanation(
            evidence=(ExplanationEvidence(evidence_id="cash", text="Cash fell."),),
            claims=(ExplanationClaim(text="Cash fell.", evidence_refs=("income",)),),
        )


def test_explanation_rejects_numeric_claim_absent_from_supplied_evidence() -> None:
    with pytest.raises(ValidationError, match="absent from supplied evidence"):
        EvidenceGroundedExplanation(
            evidence=(ExplanationEvidence(evidence_id="cash", text="Cash fell."),),
            claims=(
                ExplanationClaim(
                    text="Cash fell by €999,000.",
                    evidence_refs=("cash",),
                ),
            ),
        )


def test_explanation_allows_numeric_claim_present_in_supplied_evidence() -> None:
    explanation = EvidenceGroundedExplanation(
        evidence=(
            ExplanationEvidence(
                evidence_id="cash",
                text="Cash funding in the selected year.",
                numeric_values=(Decimal("51709.06"),),
            ),
        ),
        claims=(
            ExplanationClaim(
                text="Cash funding was €51,709.06.",
                evidence_refs=("cash",),
            ),
        ),
    )

    assert explanation.claims[0].evidence_refs == ("cash",)

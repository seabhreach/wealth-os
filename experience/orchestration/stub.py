"""Deterministic no-network orchestration provider for development and tests."""

from __future__ import annotations

from decimal import Decimal

from engine.assets import InvestmentAssetType, InvestmentHolding
from experience.orchestration.models import (
    AmbiguityMetadata,
    ConversationIntent,
    EvidenceRetrievalKind,
    ExplanationRequest,
    FinancialPictureOperation,
    FinancialPictureTarget,
    FinancialPictureUpdateProposal,
    MissingInformationRequest,
    OrchestrationRequest,
    OrchestrationResponse,
    ProposalSource,
    ProposalValidationState,
    ProposeFinancialPictureUpdateAction,
    ScenarioField,
    SetScenarioValueAction,
)


class DeterministicStubProvider:
    """Match four contract examples without an LLM, network, or financial calculations."""

    provider_name = "stub"
    model_name: str | None = None
    makes_external_calls = False

    def interpret(self, request: OrchestrationRequest) -> OrchestrationResponse:
        """Return the same structured response for the same normalized example text."""

        text = " ".join(
            request.message.text.casefold().replace("\N{RIGHT SINGLE QUOTATION MARK}", "'").split()
        )
        if "bitcoin" in text and ("50k" in text or "50,000" in text):
            return _bitcoin_response()
        if "spend" in text and ("120k" in text or "120,000" in text):
            return _spending_response()
        if "cash" in text and "fall" in text and "2032" in text:
            return _cash_response()
        if "house" in text and "retire" in text:
            return _residence_response()
        return OrchestrationResponse(
            intent=ConversationIntent.UNKNOWN,
            missing_information=(
                MissingInformationRequest(
                    item_id="request-intent",
                    question="What would you like to update, explore, or explain?",
                    reason="The deterministic stub supports only the contract examples.",
                ),
            ),
            user_facing_draft="Please clarify what you would like to explore.",
            ambiguity=AmbiguityMetadata(
                requires_clarification=True,
                topics=("intent",),
            ),
        )


def _bitcoin_response() -> OrchestrationResponse:
    proposal_id = "proposal-add-bitcoin-50000"
    holding = InvestmentHolding(
        holding_id="holding-bitcoin-user-50000",
        name="Bitcoin",
        asset_type=InvestmentAssetType.CRYPTOASSET,
        current_value=Decimal("50000"),
    )
    return OrchestrationResponse(
        intent=ConversationIntent.UPDATE_FINANCIAL_PICTURE,
        financial_picture_updates=(
            FinancialPictureUpdateProposal(
                proposal_id=proposal_id,
                operation=FinancialPictureOperation.ADD,
                target=FinancialPictureTarget.TAXABLE_INVESTMENT_HOLDING,
                holding_id=holding.holding_id,
                proposed_value=holding,
                source=ProposalSource.USER_SUPPLIED_ESTIMATE,
                confirmation_required=True,
                validation_state=ProposalValidationState.VALID,
            ),
        ),
        deterministic_actions=(ProposeFinancialPictureUpdateAction(proposal_id=proposal_id),),
        user_facing_draft=(
            "I can propose adding Bitcoin with an estimated value of €50,000 to your "
            "Financial Picture for review."
        ),
    )


def _spending_response() -> OrchestrationResponse:
    return OrchestrationResponse(
        intent=ConversationIntent.EXPLORE_SCENARIO,
        deterministic_actions=(
            SetScenarioValueAction(
                field=ScenarioField.ANNUAL_RETIREMENT_SPENDING,
                value=Decimal("120000"),
            ),
        ),
        user_facing_draft=(
            "I can run a deterministic scenario with annual retirement spending of €120,000."
        ),
    )


def _cash_response() -> OrchestrationResponse:
    return OrchestrationResponse(
        intent=ConversationIntent.EXPLAIN_EXISTING_RESULT,
        explanation_request=ExplanationRequest(
            retrieval_kind=EvidenceRetrievalKind.ANNUAL_CASH_FLOW,
            evidence_refs=("g005-annual-statement", "g005-cash-trajectory"),
            calendar_year=2032,
        ),
        user_facing_draft=(
            "I'll retrieve the deterministic cash-flow evidence for 2032 before explaining it."
        ),
    )


def _residence_response() -> OrchestrationResponse:
    return OrchestrationResponse(
        intent=ConversationIntent.EXPLORE_SCENARIO,
        missing_information=(
            MissingInformationRequest(
                item_id="primary-residence-mechanism",
                question=(
                    "How would you use the home financially: downsizing, remortgaging, "
                    "or equity release?"
                ),
                reason=(
                    "Primary-residence equity cannot become planning capital without an "
                    "explicit mechanism, timing, and cost assumptions."
                ),
            ),
            MissingInformationRequest(
                item_id="primary-residence-timing-and-costs",
                question="When would this happen, and what transaction or financing costs apply?",
                reason="A validated deterministic residence scenario needs timing and costs.",
            ),
        ),
        user_facing_draft=(
            "Using the home requires a specific mechanism and assumptions before a scenario "
            "can be constructed."
        ),
        ambiguity=AmbiguityMetadata(
            requires_clarification=True,
            topics=("primary_residence", "mechanism", "timing", "costs"),
        ),
    )

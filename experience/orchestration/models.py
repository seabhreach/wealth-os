"""Provider-neutral, validated contracts for bounded AI orchestration."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from engine.assets import InvestmentHolding
from experience.models import GoalId


class ContractModel(BaseModel):
    """Immutable contract base that rejects unknown provider fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class ConversationIntent(StrEnum):
    """Supported high-level interpretations of one user message."""

    UPDATE_FINANCIAL_PICTURE = "UPDATE_FINANCIAL_PICTURE"
    EXPLORE_SCENARIO = "EXPLORE_SCENARIO"
    EXPLAIN_EXISTING_RESULT = "EXPLAIN_EXISTING_RESULT"
    ASK_GENERAL_FINANCIAL_QUESTION = "ASK_GENERAL_FINANCIAL_QUESTION"
    CLARIFY_INFORMATION = "CLARIFY_INFORMATION"
    UNKNOWN = "UNKNOWN"


class InformationItemStatus(StrEnum):
    """Discovery-owned status vocabulary exposed to orchestration."""

    VERIFIED = "Verified"
    KNOWN = "Known"
    ESTIMATED = "Estimated"
    ASSUMED = "Assumed"
    UNKNOWN = "Unknown"
    NOT_RELEVANT = "Not Relevant"


class UserMessage(ContractModel):
    """One user-authored interaction without provider-specific metadata."""

    message_id: str = Field(min_length=1)
    text: str = Field(min_length=1)


class CompactFinancialFact(ContractModel):
    """One selected Financial Picture fact, never the full picture by default."""

    key: str = Field(min_length=1)
    value: str | int | Decimal | bool
    source: str = Field(min_length=1)


class InformationRequirement(ContractModel):
    """One relevant unresolved or known Discovery Model item."""

    item_id: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    status: InformationItemStatus


class EvidenceReference(ContractModel):
    """Compact deterministic evidence metadata available to interpretation."""

    evidence_id: str = Field(min_length=1)
    label: str = Field(min_length=1)


class ActionKind(StrEnum):
    """RFC-013 action vocabulary available to orchestration providers."""

    SET_SCENARIO_VALUE = "SetScenarioValue"
    COMPARE_SCENARIO = "CompareScenario"
    RESET_SCENARIO = "ResetScenario"
    EXPLAIN_EVIDENCE = "ExplainEvidence"
    HIGHLIGHT_EVIDENCE = "HighlightEvidence"
    SHOW_DETAIL = "ShowDetail"
    HIDE_DETAIL = "HideDetail"
    PROPOSE_FINANCIAL_PICTURE_UPDATE = "ProposeFinancialPictureUpdate"


class ScenarioField(StrEnum):
    """Scenario inputs the orchestration contract may propose setting."""

    RETIREMENT_AGE = "retirement_age"
    ANNUAL_RETIREMENT_SPENDING = "annual_retirement_spending"
    INCLUDE_INVESTMENT_PROPERTY = "include_investment_property"
    EMPLOYER_EQUITY_DISPOSAL_POLICY = "employer_equity_disposal_policy"


class SetScenarioValueAction(ContractModel):
    """Propose one value for a registered deterministic scenario input."""

    action_type: Literal[ActionKind.SET_SCENARIO_VALUE] = ActionKind.SET_SCENARIO_VALUE
    field: ScenarioField
    value: Decimal | int | str | bool


class CompareScenarioAction(ContractModel):
    """Request a deterministic comparison with a named scenario."""

    action_type: Literal[ActionKind.COMPARE_SCENARIO] = ActionKind.COMPARE_SCENARIO
    scenario_id: str = Field(min_length=1)


class ResetScenarioAction(ContractModel):
    """Request removal of temporary scenario overrides."""

    action_type: Literal[ActionKind.RESET_SCENARIO] = ActionKind.RESET_SCENARIO


class ExplainEvidenceAction(ContractModel):
    """Request explanation of identified deterministic evidence."""

    action_type: Literal[ActionKind.EXPLAIN_EVIDENCE] = ActionKind.EXPLAIN_EVIDENCE
    evidence_refs: tuple[str, ...] = Field(min_length=1)


class HighlightEvidenceAction(ContractModel):
    """Focus existing evidence without changing its meaning."""

    action_type: Literal[ActionKind.HIGHLIGHT_EVIDENCE] = ActionKind.HIGHLIGHT_EVIDENCE
    evidence_ref: str = Field(min_length=1)


class ShowDetailAction(ContractModel):
    """Open a permitted existing detail or disclosure."""

    action_type: Literal[ActionKind.SHOW_DETAIL] = ActionKind.SHOW_DETAIL
    detail_id: str = Field(min_length=1)


class HideDetailAction(ContractModel):
    """Close secondary detail without deleting evidence."""

    action_type: Literal[ActionKind.HIDE_DETAIL] = ActionKind.HIDE_DETAIL
    detail_id: str = Field(min_length=1)


class ProposeFinancialPictureUpdateAction(ContractModel):
    """Reference a separate persistent-change proposal for confirmation."""

    action_type: Literal[ActionKind.PROPOSE_FINANCIAL_PICTURE_UPDATE] = (
        ActionKind.PROPOSE_FINANCIAL_PICTURE_UPDATE
    )
    proposal_id: str = Field(min_length=1)


DeterministicAction = Annotated[
    SetScenarioValueAction
    | CompareScenarioAction
    | ResetScenarioAction
    | ExplainEvidenceAction
    | HighlightEvidenceAction
    | ShowDetailAction
    | HideDetailAction
    | ProposeFinancialPictureUpdateAction,
    Field(discriminator="action_type"),
]


class FinancialPictureOperation(StrEnum):
    """Persistent operations supported by the proposal/review boundary."""

    ADD = "ADD"
    UPDATE = "UPDATE"
    REMOVE = "REMOVE"


class FinancialPictureTarget(StrEnum):
    """Persistent target deliberately excluding primary-residence activation."""

    TAXABLE_INVESTMENT_HOLDING = "taxable_investment_holding"


class ProposalSource(StrEnum):
    """Provenance assigned to provider-interpreted user information."""

    USER_SUPPLIED = "user_supplied"
    USER_SUPPLIED_ESTIMATE = "user_supplied_estimate"


class ProposalValidationState(StrEnum):
    """Validation result before any proposal can enter an apply flow."""

    VALID = "VALID"
    INVALID = "INVALID"


class FinancialPictureUpdateProposal(ContractModel):
    """Reviewable change proposal; constructing it never mutates the picture."""

    proposal_id: str = Field(min_length=1)
    operation: FinancialPictureOperation
    target: FinancialPictureTarget
    holding_id: str = Field(min_length=1)
    proposed_value: InvestmentHolding | None = None
    source: ProposalSource
    confirmation_required: Literal[True] = True
    validation_state: ProposalValidationState
    validation_error: str | None = None

    @model_validator(mode="after")
    def validate_operation_and_state(self) -> FinancialPictureUpdateProposal:
        """Keep add/update/remove and validation state internally coherent."""

        if self.operation is FinancialPictureOperation.REMOVE:
            if self.proposed_value is not None:
                raise ValueError("Remove proposals cannot include a proposed holding value.")
        elif self.proposed_value is None:
            raise ValueError("Add and update proposals require a validated InvestmentHolding.")
        elif self.proposed_value.holding_id != self.holding_id:
            raise ValueError("Proposal and InvestmentHolding identifiers must match.")
        if self.validation_state is ProposalValidationState.VALID and self.validation_error:
            raise ValueError("A valid proposal cannot carry a validation error.")
        if self.validation_state is ProposalValidationState.INVALID and not self.validation_error:
            raise ValueError("An invalid proposal must explain the validation error.")
        return self


class EvidenceRetrievalKind(StrEnum):
    """Bounded deterministic evidence slices available for explanation."""

    ANNUAL_CASH_FLOW = "ANNUAL_CASH_FLOW"
    WORKSPACE_EVIDENCE = "WORKSPACE_EVIDENCE"


class ExplanationRequest(ContractModel):
    """Request deterministic evidence rather than a free-form financial answer."""

    retrieval_kind: EvidenceRetrievalKind
    evidence_refs: tuple[str, ...] = ()
    calendar_year: int | None = Field(default=None, ge=2000, le=2200)


class MissingInformationRequest(ContractModel):
    """A bounded clarification that blocks unsafe action construction."""

    item_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class AmbiguityMetadata(ContractModel):
    """Machine-readable explanation of why clarification is required."""

    requires_clarification: bool
    topics: tuple[str, ...] = ()


class OrchestrationRequest(ContractModel):
    """The smallest selected context needed for one provider interpretation."""

    interaction_id: str = Field(min_length=1)
    session_id: str | None = Field(default=None, min_length=1)
    message: UserMessage
    goal_id: GoalId | None = None
    workspace_id: str | None = Field(default=None, min_length=1)
    relevant_facts: tuple[CompactFinancialFact, ...] = ()
    allowed_actions: tuple[ActionKind, ...] = ()
    information_requirements: tuple[InformationRequirement, ...] = ()
    evidence_refs: tuple[EvidenceReference, ...] = ()


class OrchestrationResponse(ContractModel):
    """Validated provider proposal, never an instruction to mutate or calculate directly."""

    intent: ConversationIntent
    financial_picture_updates: tuple[FinancialPictureUpdateProposal, ...] = ()
    deterministic_actions: tuple[DeterministicAction, ...] = ()
    missing_information: tuple[MissingInformationRequest, ...] = ()
    explanation_request: ExplanationRequest | None = None
    user_facing_draft: str = Field(min_length=1)
    ambiguity: AmbiguityMetadata = AmbiguityMetadata(requires_clarification=False)


class ExplanationEvidence(ContractModel):
    """One compact immutable payload supplied by deterministic evidence retrieval."""

    evidence_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    numeric_values: tuple[Decimal | int, ...] = ()


class ExplanationClaim(ContractModel):
    """One natural-language claim linked to supplied deterministic evidence."""

    text: str = Field(min_length=1)
    evidence_refs: tuple[str, ...] = Field(min_length=1)


class EvidenceGroundedExplanation(ContractModel):
    """Explanation response carrying its complete compact evidence slice."""

    evidence: tuple[ExplanationEvidence, ...] = Field(min_length=1)
    claims: tuple[ExplanationClaim, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def reject_unknown_evidence_references(self) -> EvidenceGroundedExplanation:
        """Require every claim to cite only evidence supplied in this response."""

        available = {item.evidence_id for item in self.evidence}
        cited = {ref for claim in self.claims for ref in claim.evidence_refs}
        unknown = cited - available
        if unknown:
            raise ValueError(f"Explanation cites unavailable evidence: {sorted(unknown)}")
        supported_numbers = {
            Decimal(value) for item in self.evidence for value in item.numeric_values
        }
        claimed_numbers = {
            Decimal(raw.replace(",", ""))
            for claim in self.claims
            for raw in re.findall(r"(?<![A-Za-z])\d[\d,]*(?:\.\d+)?", claim.text)
        }
        unsupported_numbers = claimed_numbers - supported_numbers
        if unsupported_numbers:
            raise ValueError(
                "Explanation contains numeric claims absent from supplied evidence: "
                f"{sorted(unsupported_numbers)}"
            )
        return self


class OrchestrationTelemetry(ContractModel):
    """Provider interaction telemetry ready for future cost observability."""

    provider: str = Field(min_length=1)
    model: str | None = None
    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    latency_ms: Decimal = Field(ge=0)
    estimated_cost: Decimal = Field(ge=0)
    interaction_id: str = Field(min_length=1)
    session_id: str | None = Field(default=None, min_length=1)
    success: bool
    timestamp: datetime
    external_call: bool


class OrchestrationResult(ContractModel):
    """One validated response paired with its non-financial telemetry."""

    response: OrchestrationResponse
    telemetry: OrchestrationTelemetry

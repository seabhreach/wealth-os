"""Typed immutable evidence at the live Experience boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from experience.models import EvidencePurpose, GoalId, InformationStatus


class EvidenceMode(StrEnum):
    """Prevent mock and live evidence from sharing one Workspace."""

    LIVE = "live"
    MOCK = "mock"


@dataclass(frozen=True, slots=True)
class FinancialPictureItem:
    """One customer-relevant value adapted from validated configuration."""

    key: str
    label: str
    value: str | int | Decimal | bool
    status: InformationStatus
    source: str


@dataclass(frozen=True, slots=True)
class FinancialPicture:
    """Read-only customer-relevant view over the validated baseline."""

    baseline_identifier: str
    fingerprint: str
    items: tuple[FinancialPictureItem, ...]


@dataclass(frozen=True, slots=True)
class Provenance:
    """Stable deterministic identity plus non-identity generation metadata."""

    baseline_identifier: str
    financial_picture_fingerprint: str
    goal_id: GoalId
    scenario_overrides: tuple[tuple[str, str], ...]
    simulation_version: str
    tax_rule_identifier: str | None
    evidence_policy_version: str
    result_fingerprint: str
    generated_at: datetime


@dataclass(frozen=True, slots=True)
class EvidenceBase:
    """Metadata common to every immutable evidence item."""

    evidence_id: str
    title: str
    purpose: EvidencePurpose
    mode: EvidenceMode


@dataclass(frozen=True, slots=True)
class NarrativeEvidence(EvidenceBase):
    """A deterministic template-backed explanation citing evidence IDs."""

    text: str
    citations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MetricEvidence(EvidenceBase):
    """One unmodified deterministic metric."""

    label: str
    value: Decimal | int | str | bool | None
    unit: str
    period: str | None = None


@dataclass(frozen=True, slots=True)
class ComparisonEvidence(EvidenceBase):
    """Two deterministic values shown together without Experience-owned arithmetic."""

    metric: str
    baseline_label: str
    baseline_value: Decimal | int | str | bool | None
    scenario_label: str
    scenario_value: Decimal | int | str | bool | None
    unit: str


@dataclass(frozen=True, slots=True)
class TimelinePoint:
    """One existing projection value at its engine-provided period."""

    period: int
    value: Decimal
    age: int | None = None


@dataclass(frozen=True, slots=True)
class TimelineEvidence(EvidenceBase):
    """Ordered existing projection values without interpolation or calculation."""

    label: str
    unit: str
    points: tuple[TimelinePoint, ...]


@dataclass(frozen=True, slots=True)
class TableEvidence(EvidenceBase):
    """Typed deterministic rows suitable for compact rendering."""

    columns: tuple[str, ...]
    rows: tuple[tuple[str | int | Decimal | bool | None, ...], ...]
    footnote: str | None = None


@dataclass(frozen=True, slots=True)
class FinancialStatementEvidence(EvidenceBase):
    """Existing annual statement and trace categories for a selected year."""

    calendar_year: int
    opening_cash: Decimal
    inflows: tuple[tuple[str, Decimal], ...]
    outflows: tuple[tuple[str, Decimal], ...]
    closing_cash: Decimal
    liquid_assets: Decimal
    net_worth: Decimal


@dataclass(frozen=True, slots=True)
class AssumptionEvidence(EvidenceBase):
    """One explicit baseline or temporary scenario assumption."""

    label: str
    value: str | int | Decimal | bool
    source: str
    confidence: InformationStatus


@dataclass(frozen=True, slots=True)
class LimitationEvidence(EvidenceBase):
    """An unsupported behavior or interpretation boundary."""

    text: str


@dataclass(frozen=True, slots=True)
class StrategyEvidence(EvidenceBase):
    """A temporary override and its unpersisted proposed-update preview."""

    baseline: str
    scenario: str
    override: tuple[tuple[str, str], ...]
    proposed_update: str


@dataclass(frozen=True, slots=True)
class InsightEvidence(EvidenceBase):
    """A deterministic observation with evidence references."""

    observation: str
    supporting_evidence: tuple[str, ...]


LiveEvidence = (
    NarrativeEvidence
    | MetricEvidence
    | ComparisonEvidence
    | TimelineEvidence
    | TableEvidence
    | FinancialStatementEvidence
    | AssumptionEvidence
    | LimitationEvidence
    | StrategyEvidence
    | InsightEvidence
)


@dataclass(frozen=True, slots=True)
class LiveWorkspace:
    """One answer-first Workspace containing live evidence only."""

    workspace_id: str
    goal_id: GoalId
    title: str
    mode: EvidenceMode
    evidence: tuple[LiveEvidence, ...]
    financial_picture: FinancialPicture
    picture_item_keys: tuple[str, ...]
    provenance: Provenance
    proposed_update: str | None = None

    def __post_init__(self) -> None:
        if self.mode is not EvidenceMode.LIVE:
            raise ValueError("A live Workspace must use live mode.")
        if any(item.mode is not EvidenceMode.LIVE for item in self.evidence):
            raise ValueError("Mock and live evidence cannot be mixed in one Workspace.")

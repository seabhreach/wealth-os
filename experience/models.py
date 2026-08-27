"""Immutable models for the bounded mock Experience journeys."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class GoalId(StrEnum):
    """Validated prototype goal identifiers."""

    RETIRE_EARLIER = "G-001"
    INVESTMENT_PROPERTY = "G-002"
    EMPLOYER_EQUITY = "G-003"
    HIGHER_SPENDING = "G-004"
    CASH_DECLINE = "G-005"


class InformationStatus(StrEnum):
    """Customer-visible information quality for a captured mock answer."""

    KNOWN = "Known"
    ESTIMATED = "Estimated"
    UNKNOWN = "Unknown"
    NOT_RELEVANT = "Not relevant"


class EvidencePurpose(StrEnum):
    """Why a Workspace section is present."""

    ANSWER = "answer"
    EXPLANATION = "explanation"
    COMPARISON = "comparison"
    TRADE_OFF = "trade-off"
    ASSUMPTION = "assumption"
    LIMITATION = "limitation"
    STRATEGY = "strategy"
    INSIGHT = "insight"


class CompletionState(StrEnum):
    """Prototype journey progress without implying data quality."""

    DISCOVERING = "Discovering"
    ENOUGH_FOR_FIRST_VIEW = "Enough for first view"
    REFINED = "Refined"


class MessageRole(StrEnum):
    """Conversation participant identity without avatar dependencies."""

    ASSISTANT = "Wealth OS"
    USER = "You"


class ContextAction(StrEnum):
    """Small inline actions permitted by a scripted question."""

    WHY = "Why this matters"
    SKIP = "Skip for now"
    ESTIMATE = "Use an estimate"


@dataclass(frozen=True)
class Message:
    """One message in the scripted conversation."""

    role: MessageRole
    content: str


@dataclass(frozen=True)
class Choice:
    """A subtle choice chip with a deterministic branch target."""

    label: str
    value: str
    status: InformationStatus = InformationStatus.KNOWN
    next_step: str | None = None
    reveal_section: str | None = None
    enough_information: bool = False


@dataclass(frozen=True)
class QuestionStep:
    """One bounded question-library-backed prototype step."""

    key: str
    question_id: str
    assistant_text: str
    choices: tuple[Choice, ...]
    why_text: str
    next_step: str | None = None
    reveal_section: str | None = None
    estimate_answer: tuple[str, str] | None = None
    unknown_allowed: bool = False
    skip_allowed: bool = False
    enough_information: bool = False


@dataclass(frozen=True)
class Refinement:
    """One bounded update to an existing mock Workspace."""

    prompt: str
    choices: tuple[Choice, ...]


@dataclass(frozen=True)
class CapturedAnswer:
    """A traceable answer captured for prototype review."""

    question_id: str
    step_key: str
    display_value: str
    value: str
    status: InformationStatus


@dataclass(frozen=True)
class PictureItem:
    """One progressively revealed mock Financial Picture item."""

    label: str
    value: str
    status: InformationStatus


@dataclass(frozen=True)
class WorkspaceSection:
    """A mock evidence section with a declared reason for appearing."""

    key: str
    title: str
    summary: str
    purpose: EvidencePurpose
    picture_items: tuple[PictureItem, ...] = ()
    evidence: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Journey:
    """A finite scripted mock journey and its predefined evidence."""

    goal_id: GoalId
    customer_name: str
    title: str
    recent_title: str
    example_prompt: str
    keywords: tuple[str, ...]
    initial_status: str
    first_step: str | None
    questions: tuple[QuestionStep, ...]
    sections: tuple[WorkspaceSection, ...]
    enough_message: str
    refinement: Refinement
    saved_sections: tuple[str, ...]


@dataclass(frozen=True)
class PrototypeState:
    """Immutable state for one mock conversation and Workspace."""

    active_goal: GoalId | None = None
    workspace_id: str | None = None
    messages: tuple[Message, ...] = ()
    current_step: str | None = None
    revealed_sections: tuple[str, ...] = ()
    captured_answers: tuple[CapturedAnswer, ...] = ()
    question_ids_asked: tuple[str, ...] = ()
    question_ids_skipped: tuple[str, ...] = ()
    enough_information: bool = False
    refinement_performed: bool = False
    completion_state: CompletionState = CompletionState.DISCOVERING

    @property
    def is_home(self) -> bool:
        """Return whether the minimal Home experience should be shown."""

        return self.active_goal is None

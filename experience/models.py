"""Immutable models for the mock-only Experience prototype."""

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


class MessageRole(StrEnum):
    """Conversation participant identity without avatar dependencies."""

    ASSISTANT = "Wealth OS"
    USER = "You"


@dataclass(frozen=True)
class Message:
    """One message in the scripted conversation."""

    role: MessageRole
    content: str


@dataclass(frozen=True)
class Choice:
    """A subtle choice chip that advances the current script."""

    label: str
    value: str


@dataclass(frozen=True)
class JourneyStep:
    """One natural-language prompt and its optional choice chips."""

    assistant_text: str
    choices: tuple[Choice, ...] = ()
    contextual_actions: tuple[str, ...] = ()
    reveal_section: str | None = None


@dataclass(frozen=True)
class PictureItem:
    """One progressively revealed mock Financial Picture item."""

    label: str
    value: str
    status: str


@dataclass(frozen=True)
class WorkspaceSection:
    """A mock evidence section revealed by conversation progress."""

    key: str
    title: str
    summary: str
    picture_items: tuple[PictureItem, ...] = ()
    evidence: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Journey:
    """A complete scripted mock journey and its Workspace evidence."""

    goal_id: GoalId
    title: str
    recent_title: str
    example_prompt: str
    keywords: tuple[str, ...]
    initial_status: str
    steps: tuple[JourneyStep, ...]
    sections: tuple[WorkspaceSection, ...]
    completion_message: str


@dataclass(frozen=True)
class PrototypeState:
    """Immutable state for one prototype conversation."""

    active_goal: GoalId | None = None
    messages: tuple[Message, ...] = ()
    step_index: int = 0
    revealed_sections: tuple[str, ...] = ()
    answers: tuple[tuple[str, str], ...] = ()

    @property
    def is_home(self) -> bool:
        """Return whether the minimal Home experience should be shown."""

        return self.active_goal is None

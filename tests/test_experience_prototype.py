"""Focused contract tests for the mock-only Experience prototype shell."""

from __future__ import annotations

import ast
from pathlib import Path

from experience.conversation import advance_with_choice, available_choices, start_conversation
from experience.mock_data import all_journeys, journey_for
from experience.models import GoalId, MessageRole
from experience.styles import (
    DARK_INPUT_BACKGROUND,
    DARK_INPUT_FOREGROUND,
    LIGHT_INPUT_BACKGROUND,
    LIGHT_INPUT_FOREGROUND,
)
from experience.workspace import visible_sections, workspace_status
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
EXPERIENCE_ROOT = ROOT / "experience"


def test_home_renders_without_dashboard_elements() -> None:
    """Home is a minimal question and recent-Workspace surface, not a dashboard or form."""

    app = AppTest.from_file(str(EXPERIENCE_ROOT / "app.py")).run(timeout=30)

    assert not app.exception
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    assert "Wealth OS" in rendered
    assert "What would you like to explore today?" in rendered
    assert "Start with the question on your mind" in rendered
    assert not app.metric
    assert not app.number_input
    assert not app.dataframe


def test_first_message_transitions_into_active_conversation() -> None:
    """An opening question removes Home state and starts the matching journey."""

    state = start_conversation("Could I retire before 60?")

    assert not state.is_home
    assert state.active_goal is GoalId.RETIRE_EARLIER
    assert [message.role for message in state.messages] == [MessageRole.USER, MessageRole.ASSISTANT]


def test_no_continue_buttons_exist() -> None:
    """Scripts advance through direct chips or chat, never a generic Continue control."""

    choice_labels = [
        choice.label
        for journey in all_journeys()
        for step in journey.steps
        for choice in step.choices
    ]
    assert all(label.casefold() != "continue" for label in choice_labels)
    assert "Continue" not in (EXPERIENCE_ROOT / "app.py").read_text(encoding="utf-8")


def test_choice_chips_advance_scripted_conversation() -> None:
    """Selecting a chip immediately advances the script and records its reveal."""

    state = start_conversation("Could I retire before 60?")
    first_choice = available_choices(state)[0]
    advanced = advance_with_choice(state, first_choice.value)

    assert advanced.step_index == 1
    assert advanced.answers[-1][1] == first_choice.value
    assert len(advanced.messages) == len(state.messages) + 2
    assert advanced.revealed_sections == ("picture-household",)


def test_workspace_begins_minimal() -> None:
    """The first Workspace contains only its title and understanding status."""

    state = start_conversation("Could I retire before 60?")

    assert visible_sections(state) == ()
    assert workspace_status(state) == "Understanding your situation"


def test_workspace_reveals_progressively() -> None:
    """Each conversational answer reveals at most one new meaningful section."""

    state = start_conversation("Could I retire before 60?")
    after_first = advance_with_choice(state, available_choices(state)[0].value)
    after_second = advance_with_choice(after_first, available_choices(after_first)[0].value)

    assert len(visible_sections(after_first)) == 1
    assert len(visible_sections(after_second)) == 2
    assert set(after_first.revealed_sections) < set(after_second.revealed_sections)


def test_financial_picture_is_not_fully_shown_immediately() -> None:
    """Financial Picture evidence remains progressive and status-labelled."""

    state = start_conversation("Could I retire before 60?")
    initial_items = tuple(
        item for section in visible_sections(state) for item in section.picture_items
    )
    after_first = advance_with_choice(state, available_choices(state)[0].value)
    first_items = tuple(
        item for section in visible_sections(after_first) for item in section.picture_items
    )

    assert initial_items == ()
    assert len(first_items) == 1
    assert first_items[0].status in {
        "Known",
        "Estimated",
        "Unknown",
        "Needs refinement",
        "Not relevant",
    }
    assert first_items[0].status != "Complete"


def test_five_validated_goal_journeys_exist() -> None:
    """The mock shell exposes exactly the five recovered validated goals."""

    journeys = all_journeys()
    assert len(journeys) == 5
    assert {journey.goal_id for journey in journeys} == set(GoalId)
    assert [journey.recent_title for journey in journeys] == [
        "Retire before 60",
        "Investment Property",
        "Employer Equity",
        "Retirement Spending",
        "Cash Flow",
    ]


def test_employer_equity_language_is_generic() -> None:
    """The journey model uses generic employer-equity concepts rather than an issuer-specific
    type.
    """

    journey = journey_for(GoalId.EMPLOYER_EQUITY)
    content = repr(journey).casefold()
    experience_source = "\n".join(
        path.read_text(encoding="utf-8") for path in EXPERIENCE_ROOT.rglob("*.py")
    )

    assert "employer equity" in content or "employer-equity" in content
    assert "amazon" not in experience_source.casefold()


def test_mock_only_package_has_no_financial_layer_imports() -> None:
    """Experience never imports the protected financial or legacy presentation packages."""

    forbidden_roots = {"engine", "dashboard"}
    imported_roots: set[str] = set()
    for path in EXPERIENCE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", maxsplit=1)[0])

    assert imported_roots.isdisjoint(forbidden_roots)


def test_light_and_dark_input_tokens_have_readable_contrast_direction() -> None:
    """Input foreground and background tokens never collapse to the same color."""

    assert LIGHT_INPUT_FOREGROUND != LIGHT_INPUT_BACKGROUND
    assert DARK_INPUT_FOREGROUND != DARK_INPUT_BACKGROUND
    assert LIGHT_INPUT_FOREGROUND != DARK_INPUT_FOREGROUND


def test_message_identity_requires_no_emoji_or_avatar_dependency() -> None:
    """Simple textual role labels provide message identity without decorative assets."""

    assert {role.value for role in MessageRole} == {"Wealth OS", "You"}
    assert all(value.isascii() for value in (role.value for role in MessageRole))
    assert not {"emoji", "avatar"}.intersection(_experience_import_roots())


def _experience_import_roots() -> set[str]:
    roots: set[str] = set()
    for path in EXPERIENCE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".", maxsplit=1)[0])
    return roots

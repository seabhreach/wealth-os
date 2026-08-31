"""Focused contracts for the integrated Conversation-to-Workspace shell."""

from __future__ import annotations

from pathlib import Path

import pytest
from experience.explain import context_for_component, explain_context
from experience.live.service import LiveExperienceService
from experience.models import GoalId
from experience.routing import route_question
from experience.workspace_composition import compose_g001_workspace
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "experience" / "app.py"


@pytest.mark.parametrize(
    ("question", "goal_id", "age", "year"),
    [
        ("can I retire at 59", GoalId.RETIRE_EARLIER, 59, None),
        ("could I retire at 58", GoalId.RETIRE_EARLIER, 58, None),
        ("retire earlier", GoalId.RETIRE_EARLIER, None, None),
        ("stop working at 57", GoalId.RETIRE_EARLIER, 57, None),
        ("what if I retire at 61", GoalId.RETIRE_EARLIER, 61, None),
        ("should I buy another property", GoalId.INVESTMENT_PROPERTY, None, None),
        ("explore a rental property", GoalId.INVESTMENT_PROPERTY, None, None),
        ("how exposed am I to my employer shares", GoalId.EMPLOYER_EQUITY, None, None),
        ("company shares", GoalId.EMPLOYER_EQUITY, None, None),
        ("RSUs", GoalId.EMPLOYER_EQUITY, None, None),
        ("can I spend more in retirement", GoalId.HIGHER_SPENDING, None, None),
        ("why does my cash fall", GoalId.CASH_DECLINE, None, None),
        ("explain my cash in 2035", GoalId.CASH_DECLINE, None, 2035),
    ],
)
def test_natural_question_routing(
    question: str,
    goal_id: GoalId,
    age: int | None,
    year: int | None,
) -> None:
    routed = route_question(question)

    assert routed is not None
    assert routed.goal_id is goal_id
    assert routed.retirement_age == age
    assert routed.calendar_year == year


def test_unsupported_question_never_defaults_to_retirement() -> None:
    assert route_question("Compare two mortgage products") is None


def test_spending_amount_is_extracted_for_supported_natural_question() -> None:
    routed = route_question("What if I spend 100k?")

    assert routed is not None
    assert routed.goal_id is GoalId.HIGHER_SPENDING
    assert str(routed.retirement_spending) == "100000"


def test_shell_navigation_reaches_financial_picture_and_saved_workspace() -> None:
    app = AppTest.from_file(str(APP)).run(timeout=30)
    app.button(key="shell-picture").click().run(timeout=30)

    assert not app.exception
    rendered = _rendered(app)
    assert "What Wealth OS currently knows" in rendered
    assert "Planned retirement age" in rendered
    assert "€80,000" in rendered

    app.button(key="shell-home").click().run(timeout=30)
    app.button(key="wos-recent-g-003").click().run(timeout=30)
    assert not app.exception
    rendered = _rendered(app)
    assert "How dependent am I on my employer shares?" in rendered
    assert "Conversation" not in rendered
    assert "Return home" not in rendered


@pytest.mark.parametrize(
    "goal_key",
    ("wos-recent-g-002", "wos-recent-g-003", "wos-recent-g-004", "wos-recent-g-005"),
)
def test_each_non_retirement_goal_uses_visual_goal_specific_composition(goal_key: str) -> None:
    app = AppTest.from_file(str(APP)).run(timeout=30)
    app.button(key=goal_key).click().run(timeout=30)

    assert not app.exception
    rendered = _rendered(app)
    assert "Temporary exploration" in rendered
    assert "About this projection" in {item.label for item in app.expander}
    assert any(button.label == "Explain this" for button in app.button)


def test_g001_temporary_scenario_does_not_mutate_financial_picture() -> None:
    service = LiveExperienceService.from_example(ROOT)
    baseline = service.baseline.configuration
    before = baseline.model_dump_json()

    service.retire_earlier(57)

    assert baseline.model_dump_json() == before
    assert baseline.household.planned_retirement_age == 60


def test_explain_context_is_structured_and_uses_only_component_evidence() -> None:
    service = LiveExperienceService.from_example(ROOT)
    workspace = service.retire_earlier(58)
    spec = compose_g001_workspace(
        workspace,
        allowed_retirement_ages=service.supported_retirement_ages,
        baseline_retirement_age=60,
        explored_retirement_age=58,
    )
    context = context_for_component(spec, "g001-trajectory-component")
    explanation = explain_context(context, workspace)

    assert context.workspace_id == workspace.workspace_id
    assert context.component_id == "g001-trajectory-component"
    assert dict(context.scenario) == {"retirement_age": "58"}
    assert explanation.evidence_refs_used == context.evidence_refs
    assert set(explanation.evidence_refs_used) < {item.evidence_id for item in workspace.evidence}


def test_explain_this_opens_and_closes_secondary_conversation() -> None:
    app = _open_retirement_workspace(58)
    app.button(key="explain-g001-trajectory-component").click().run(timeout=30)

    assert not app.exception
    assert "You're asking about the liquid-assets trajectory" in _rendered(app)
    app.button(key="close-workspace-conversation").click().run(timeout=30)
    assert "You're asking about the liquid-assets trajectory" not in _rendered(app)
    assert "Could I retire at 58?" in _rendered(app)


def test_scenario_to_financial_picture_is_a_confirmed_non_persistent_proposal() -> None:
    app = _open_retirement_workspace(57)
    app.button(key="g001-propose-financial-picture-update").click().run(timeout=30)

    assert not app.exception
    rendered = _rendered(app)
    assert "Proposed Financial Picture Update" in {item.value for item in app.subheader}
    assert "60 years → 57 years" in rendered
    app.button(key="financial-picture-confirm-update").click().run(timeout=30)
    assert any("No baseline data was changed" in item.value for item in app.success)
    service = LiveExperienceService.from_example(ROOT)
    assert service.baseline.configuration.household.planned_retirement_age == 60


def test_technical_provenance_is_available_only_in_review_mode() -> None:
    normal = _open_retirement_workspace(58)
    assert "result_fingerprint" not in _rendered(normal)
    assert "Review mode" not in {item.label for item in normal.expander}

    review = AppTest.from_file(str(APP))
    review.query_params["workspace"] = "g001"
    review.query_params["review"] = "1"
    review.run(timeout=30)

    assert not review.exception
    assert "Review mode" in {item.label for item in review.expander}
    assert review.json


def _open_retirement_workspace(age: int) -> AppTest:
    app = AppTest.from_file(str(APP)).run(timeout=30)
    app.chat_input(key="home-chat-input").set_value(f"Can I retire at {age}?").run(timeout=30)
    app.button(key="conversation-open-workspace").click().run(timeout=30)
    assert not app.exception
    return app


def _rendered(app: AppTest) -> str:
    return "\n".join(markdown.value for markdown in app.markdown)

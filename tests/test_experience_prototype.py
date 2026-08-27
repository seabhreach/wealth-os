"""Contracts for the bounded mock-only Experience journeys."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from experience.conversation import (
    advance_with_action,
    advance_with_choice,
    available_choices,
    contextual_actions,
    open_saved_workspace,
    reset_state,
    start_conversation,
)
from experience.mock_data import (
    QUESTION_IDS_BY_GOAL,
    VALID_QUESTION_IDS,
    all_journeys,
    journey_for,
    match_journey,
)
from experience.models import (
    CompletionState,
    ContextAction,
    EvidencePurpose,
    GoalId,
    InformationStatus,
    MessageRole,
    PrototypeState,
)
from experience.review import developer_review_state
from experience.styles import (
    DARK_INPUT_BACKGROUND,
    DARK_INPUT_FOREGROUND,
    DARK_THEME_TOKENS,
    EXPERIENCE_CSS,
    LIGHT_INPUT_BACKGROUND,
    LIGHT_INPUT_FOREGROUND,
    LIGHT_THEME_TOKENS,
    RESPONSIVE_BREAKPOINT_PX,
    layout_mode_for_width,
    pane_order_for_width,
)
from experience.widget_keys import widget_key
from experience.workspace import visible_sections
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
EXPERIENCE_ROOT = ROOT / "experience"


def test_home_is_a_minimal_conversation_entry_point() -> None:
    app = AppTest.from_file(str(EXPERIENCE_ROOT / "app.py")).run(timeout=30)

    assert not app.exception
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    assert "Wealth OS" in rendered
    assert "What would you like to explore today?" in rendered
    assert "Start with the question on your mind" in rendered
    assert not app.metric
    assert not app.number_input
    assert not app.dataframe


def test_recent_workspace_opens_and_return_home_resets_the_ui() -> None:
    app = AppTest.from_file(str(EXPERIENCE_ROOT / "app.py")).run(timeout=30)
    app.button(key="wos-recent-g-002").click().run(timeout=30)

    assert not app.exception
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    assert "Restored the mock" not in rendered
    assert "That gives me enough for an initial comparison." in rendered
    assert "Initial comparison" in rendered

    app.button(key="return-home").click().run(timeout=30)
    assert not app.exception
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    assert "What would you like to explore today?" in rendered


def test_each_journey_maps_to_the_recovered_goal_id() -> None:
    assert [(journey.goal_id.value, journey.customer_name) for journey in all_journeys()] == [
        ("G-001", "Retire Earlier"),
        ("G-002", "Investment Property Decision"),
        ("G-003", "Employer Equity Exposure"),
        ("G-004", "Higher Retirement Spending"),
        ("G-005", "Cash Decline Explanation"),
    ]


def test_every_scripted_question_uses_a_registered_question_id() -> None:
    for journey in all_journeys():
        actual = {question.question_id for question in journey.questions}
        assert actual == QUESTION_IDS_BY_GOAL[journey.goal_id]
        assert actual <= VALID_QUESTION_IDS
        assert all(question.key and question.assistant_text for question in journey.questions)


def test_no_internal_goal_ids_appear_in_normal_ui_renderers() -> None:
    customer_ui = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            EXPERIENCE_ROOT / "app.py",
            *(EXPERIENCE_ROOT / "components").glob("*.py"),
        )
    )
    assert all(goal.value not in customer_ui for goal in GoalId)


def test_one_person_branch_omits_partner_age() -> None:
    state = start_conversation("Could I retire earlier?")
    state = advance_with_choice(state, "self")
    state = advance_with_choice(state, "54")

    assert state.current_step == "retire-target"
    assert "And how old is your partner?" not in [message.content for message in state.messages]
    assert "retire-scope-self" in state.revealed_sections


def test_household_branch_asks_partner_age() -> None:
    state = start_conversation("Could I retire earlier?")
    state = advance_with_choice(state, "household")
    state = advance_with_choice(state, "54")

    assert state.current_step == "retire-partner-age"
    assert state.messages[-1].content == "And how old is your partner?"
    assert state.question_ids_asked[-1] == "Q-001"


@pytest.mark.parametrize(
    ("funding", "expected_section", "expected_copy"),
    [
        ("cash", "property-cash", "cash purchase"),
        ("financing", "property-financing", "mortgage outcomes are not modelled"),
    ],
)
def test_property_funding_branch_reveals_correct_evidence(
    funding: str, expected_section: str, expected_copy: str
) -> None:
    state = _start_and_answer(GoalId.INVESTMENT_PROPERTY, "2027", "200000")
    state = advance_with_choice(state, funding)

    assert expected_section in state.revealed_sections
    section = next(item for item in visible_sections(state) if item.key == expected_section)
    assert expected_copy in section.summary.casefold()


@pytest.mark.parametrize(
    ("answer", "included", "omitted"),
    [
        ("none", "equity-no-future", "equity-future"),
        ("expected", "equity-future", "equity-no-future"),
    ],
)
def test_future_award_branch_controls_equity_evidence(
    answer: str, included: str, omitted: str
) -> None:
    state = _start_and_answer(GoalId.EMPLOYER_EQUITY, "100000")
    state = advance_with_choice(state, answer)

    assert included in state.revealed_sections
    assert omitted not in state.revealed_sections


def test_permanent_spending_branch_does_not_ask_duration() -> None:
    state = _start_and_answer(GoalId.HIGHER_SPENDING, "80000", "90000")
    state = advance_with_choice(state, "permanent")

    assert state.current_step == "spending-basis"
    assert "spending-permanent" in state.revealed_sections


def test_temporary_spending_branch_asks_duration_only_when_needed() -> None:
    state = _start_and_answer(GoalId.HIGHER_SPENDING, "80000", "90000")
    state = advance_with_choice(state, "temporary")

    assert state.current_step == "spending-duration"
    assert state.messages[-1].content.startswith("How long")
    assert "spending-temporary" in state.revealed_sections


def test_estimate_action_marks_estimated_and_continues() -> None:
    state = _start_and_answer(GoalId.RETIRE_EARLIER, "self")
    advanced = advance_with_action(state, ContextAction.ESTIMATE)

    assert advanced.captured_answers[-1].status is InformationStatus.ESTIMATED
    assert advanced.current_step == "retire-target"
    assert "refined later" in advanced.messages[-2].content


def test_unknown_answer_is_preserved_and_limitation_is_visible() -> None:
    state = _start_and_answer(GoalId.RETIRE_EARLIER, "self")
    advanced = advance_with_choice(state, "unknown")

    assert advanced.captured_answers[-1].status is InformationStatus.UNKNOWN
    assert advanced.captured_answers[-1].value == "unknown"
    assert any("rather than inventing" in message.content for message in advanced.messages)
    age_item = next(
        item
        for section in visible_sections(advanced)
        if section.key == "retire-user-age"
        for item in section.picture_items
    )
    assert age_item.value == "I'm not sure"
    assert age_item.status is InformationStatus.UNKNOWN


def test_skip_records_question_id_and_unknown_status() -> None:
    state = _start_and_answer(GoalId.RETIRE_EARLIER, "self", "54", "58")
    assert ContextAction.SKIP in contextual_actions(state)
    advanced = advance_with_action(state, ContextAction.SKIP)

    assert advanced.question_ids_skipped == ("Q-005",)
    assert advanced.captured_answers[-1].status is InformationStatus.UNKNOWN
    assert advanced.current_step == "retire-spending"


def test_why_action_explains_without_advancing() -> None:
    state = start_conversation("Could I retire earlier?")
    explained = advance_with_action(state, ContextAction.WHY)

    assert explained.current_step == state.current_step
    assert explained.captured_answers == ()
    assert "Household scope" in explained.messages[-1].content


@pytest.mark.parametrize("goal_id", list(GoalId))
def test_each_journey_reaches_its_enough_information_transition(goal_id: GoalId) -> None:
    state = _complete_first_path(goal_id)

    assert state.enough_information
    assert state.completion_state is CompletionState.ENOUGH_FOR_FIRST_VIEW
    assert state.current_step is None
    assert journey_for(goal_id).enough_message in [message.content for message in state.messages]


def test_cash_decline_asks_zero_data_collection_questions() -> None:
    state = start_conversation("Why does cash fall in 2032?")

    assert state.active_goal is GoalId.CASH_DECLINE
    assert journey_for(GoalId.CASH_DECLINE).questions == ()
    assert state.question_ids_asked == ()
    assert state.captured_answers == ()
    assert state.enough_information


@pytest.mark.parametrize(
    ("phrase", "goal_id"),
    [
        ("Could I retire before 60?", GoalId.RETIRE_EARLIER),
        ("Could I stop working earlier?", GoalId.RETIRE_EARLIER),
        ("What if I retire at 58?", GoalId.RETIRE_EARLIER),
        ("Could I buy an investment property?", GoalId.INVESTMENT_PROPERTY),
        ("What about a rental property?", GoalId.INVESTMENT_PROPERTY),
        ("Could I buy another property?", GoalId.INVESTMENT_PROPERTY),
        ("How dependent am I on my employer shares?", GoalId.EMPLOYER_EQUITY),
        ("What concentration do I have in employer shares?", GoalId.EMPLOYER_EQUITY),
        ("How should I think about my RSUs?", GoalId.EMPLOYER_EQUITY),
        ("Could I spend more in retirement?", GoalId.HIGHER_SPENDING),
        ("Show higher retirement spending", GoalId.HIGHER_SPENDING),
        ("What about extra spending?", GoalId.HIGHER_SPENDING),
        ("Why does my cash decline after retirement?", GoalId.CASH_DECLINE),
        ("Why is my cash falling?", GoalId.CASH_DECLINE),
        ("Explain my cash balance", GoalId.CASH_DECLINE),
    ],
)
def test_supported_goal_routing_is_bounded_and_deterministic(phrase: str, goal_id: GoalId) -> None:
    assert match_journey(phrase) is goal_id
    assert match_journey(phrase) is goal_id


def test_unsupported_intent_never_defaults_to_retirement() -> None:
    state = start_conversation("Can you compare two mortgage products?")

    assert state.active_goal is None
    assert state.is_home
    assert "currently explore" in state.messages[-1].content
    assert "retiring earlier" in state.messages[-1].content


@pytest.mark.parametrize("scope", ["self", "household"])
def test_g001_household_paths_complete_in_streamlit_without_duplicate_keys(
    scope: str,
) -> None:
    app = AppTest.from_file(str(EXPERIENCE_ROOT / "app.py")).run(timeout=30)
    app.chat_input(key="home-chat-input").set_value("Could I retire before 60?").run(timeout=30)
    assert not app.exception

    state = start_conversation("Could I retire before 60?")
    choices = available_choices(state)
    scope_index = next(index for index, choice in enumerate(choices) if choice.value == scope)
    state, app = _click_choice(app, state, scope_index)
    state, app = _click_choice(app, state, 0)
    if scope == "household":
        state, app = _click_choice(app, state, 0)
    while state.current_step is not None:
        state, app = _click_choice(app, state, 0)

    assert state.enough_information
    assert not app.exception


def test_g001_restart_replay_saved_workspace_and_refinement_are_key_safe() -> None:
    app = AppTest.from_file(str(EXPERIENCE_ROOT / "app.py")).run(timeout=30)
    app.button(key="wos-recent-g-001").click().run(timeout=30)
    assert not app.exception

    state = open_saved_workspace(GoalId.RETIRE_EARLIER)
    state, app = _click_choice(app, state, 0)
    assert state.refinement_performed

    app.button(key="return-home").click().run(timeout=30)
    app.chat_input(key="home-chat-input").set_value("Could I retire before 60?").run(timeout=30)
    assert not app.exception
    replay = start_conversation("Could I retire before 60?")
    replay, app = _click_choice(app, replay, 0)
    replay, app = _click_choice(app, replay, 0)

    assert replay.current_step == "retire-target"
    assert not app.exception


def test_widget_keys_are_unique_across_questions_refinements_and_replays() -> None:
    keys: list[str] = []
    for journey in all_journeys():
        workspace_id = f"mock-workspace-{journey.goal_id.value}"
        for question in journey.questions:
            keys.extend(
                widget_key(
                    "choice",
                    workspace_id,
                    journey.goal_id.value,
                    question.key,
                    index,
                    choice.value,
                )
                for index, choice in enumerate(question.choices)
            )
        keys.extend(
            widget_key(
                "choice",
                workspace_id,
                journey.goal_id.value,
                "refinement",
                index,
                choice.value,
            )
            for index, choice in enumerate(journey.refinement.choices)
        )

    assert len(keys) == len(set(keys))


@pytest.mark.parametrize("goal_id", list(GoalId))
def test_all_five_streamlit_journeys_render_without_duplicate_keys(goal_id: GoalId) -> None:
    prompt = journey_for(goal_id).example_prompt
    app = AppTest.from_file(str(EXPERIENCE_ROOT / "app.py")).run(timeout=30)
    app.chat_input(key="home-chat-input").set_value(prompt).run(timeout=30)
    assert not app.exception

    state = start_conversation(prompt, goal_id)
    while state.current_step is not None:
        state, app = _click_choice(app, state, 0)

    assert state.enough_information
    assert not app.exception


def test_workspace_reveals_follow_declared_order_and_one_change_per_answer() -> None:
    for goal_id in GoalId:
        state = start_conversation(journey_for(goal_id).example_prompt, goal_id)
        prior_count = len(state.revealed_sections)
        while state.current_step is not None:
            state = advance_with_choice(state, available_choices(state)[0].value)
            assert len(state.revealed_sections) - prior_count <= 1
            prior_count = len(state.revealed_sections)
        declared = [section.key for section in journey_for(goal_id).sections]
        positions = [declared.index(key) for key in state.revealed_sections]
        assert positions == sorted(positions)


def test_every_workspace_section_declares_an_evidence_purpose() -> None:
    allowed = set(EvidencePurpose)
    for journey in all_journeys():
        assert journey.sections
        assert all(section.purpose in allowed for section in journey.sections)


@pytest.mark.parametrize("goal_id", list(GoalId))
def test_refinement_updates_the_same_workspace_once(goal_id: GoalId) -> None:
    state = open_saved_workspace(goal_id)
    workspace_id = state.workspace_id
    prior_sections = state.revealed_sections
    refined = advance_with_choice(state, available_choices(state)[0].value)

    assert refined.workspace_id == workspace_id
    assert refined.refinement_performed
    assert refined.completion_state is CompletionState.REFINED
    assert len(refined.revealed_sections) == len(prior_sections) + 1
    assert available_choices(refined) == ()


@pytest.mark.parametrize("goal_id", list(GoalId))
def test_saved_workspace_restores_goal_evidence_and_refinement(goal_id: GoalId) -> None:
    state = open_saved_workspace(goal_id)

    assert state.active_goal is goal_id
    assert state.revealed_sections == journey_for(goal_id).saved_sections
    assert state.enough_information
    assert available_choices(state) == journey_for(goal_id).refinement.choices


def test_reset_returns_to_home_without_leaking_state() -> None:
    state = reset_state()

    assert state.is_home
    assert state.workspace_id is None
    assert state.messages == ()
    assert state.captured_answers == ()
    assert state.revealed_sections == ()


def test_developer_review_state_contains_all_traceability_fields() -> None:
    state = _start_and_answer(GoalId.RETIRE_EARLIER, "self", "54")
    review = developer_review_state(state)

    assert set(review) == {
        "Goal ID",
        "Journey state",
        "Question IDs asked",
        "Question IDs skipped",
        "Captured answers",
        "Financial Picture items revealed",
        "Workspace sections revealed",
        "Evidence purpose",
        "Enough information",
        "Refinement performed",
        "Completion state",
        "Workspace ID",
        "Journey",
    }
    assert review["Goal ID"] == "G-001"
    assert review["Question IDs asked"] == ("Q-002", "Q-001", "Q-004")


def test_employer_equity_language_remains_generic() -> None:
    experience_source = _mock_source()
    assert "employer equity" in repr(journey_for(GoalId.EMPLOYER_EQUITY)).casefold()
    assert "amazon" not in experience_source.casefold()


def test_mock_package_has_no_engine_or_dashboard_imports() -> None:
    assert _mock_import_roots().isdisjoint({"engine", "dashboard"})


def test_no_continue_or_submit_controls_exist() -> None:
    labels = [
        choice.label.casefold()
        for journey in all_journeys()
        for question in journey.questions
        for choice in question.choices
    ]
    labels.extend(
        choice.label.casefold()
        for journey in all_journeys()
        for choice in journey.refinement.choices
    )
    assert "continue" not in labels
    assert "submit" not in labels
    assert "Continue" not in _mock_source()


def test_mock_financial_values_and_arithmetic_stay_in_mock_data() -> None:
    for path in _mock_paths():
        if path.name in {"display.py", "mock_data.py", "styles.py"}:
            continue
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        assert "€" not in source
        financial_operators = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Pow)
        assert not any(
            isinstance(node, ast.BinOp) and isinstance(node.op, financial_operators)
            for node in ast.walk(tree)
        )


def test_visual_tokens_keep_inputs_and_chips_readable_in_both_themes() -> None:
    assert LIGHT_INPUT_FOREGROUND != LIGHT_INPUT_BACKGROUND
    assert DARK_INPUT_FOREGROUND != DARK_INPUT_BACKGROUND
    assert LIGHT_INPUT_FOREGROUND != DARK_INPUT_FOREGROUND
    assert 'button[kind="tertiary"]' in EXPERIENCE_CSS
    assert "focus-visible" in EXPERIENCE_CSS


@pytest.mark.parametrize("tokens", [LIGHT_THEME_TOKENS, DARK_THEME_TOKENS])
def test_semantic_theme_tokens_have_readable_foreground_background_pairs(
    tokens: dict[str, str],
) -> None:
    pairs = (
        ("primary_text", "page_background"),
        ("secondary_text", "page_background"),
        ("muted_text", "page_background"),
        ("input_text", "input_background"),
        ("placeholder_text", "input_background"),
        ("chip_text", "chip_background"),
        ("link_text", "page_background"),
    )
    assert set(tokens) == {
        "page_background",
        "primary_text",
        "secondary_text",
        "muted_text",
        "surface_background",
        "subtle_border",
        "input_background",
        "input_text",
        "placeholder_text",
        "chip_background",
        "chip_text",
        "link_text",
        "focus_outline",
        "disabled_text",
    }
    assert all(
        _contrast_ratio(tokens[foreground], tokens[background]) >= 4.5
        for foreground, background in pairs
    )


def test_responsive_layout_stacks_conversation_before_workspace() -> None:
    assert layout_mode_for_width(850) == "stacked"
    assert layout_mode_for_width(RESPONSIVE_BREAKPOINT_PX) == "stacked"
    assert layout_mode_for_width(1100) == "split"
    assert pane_order_for_width(850) == ("conversation", "workspace")
    assert f"max-width: {RESPONSIVE_BREAKPOINT_PX}px" in EXPERIENCE_CSS
    assert "flex-direction: column" in EXPERIENCE_CSS


def test_saved_workspace_copy_contains_no_recovery_language() -> None:
    for goal_id in GoalId:
        state = open_saved_workspace(goal_id)
        copy = " ".join(message.content.casefold() for message in state.messages)
        assert "restored the mock" not in copy


def test_message_identity_requires_no_emoji_or_avatar_dependency() -> None:
    assert {role.value for role in MessageRole} == {"Wealth OS", "You"}
    assert all(value.isascii() for value in (role.value for role in MessageRole))
    assert not {"emoji", "avatar"}.intersection(_mock_import_roots())


def _start_and_answer(goal_id: GoalId, *answers: str) -> PrototypeState:
    state = start_conversation(journey_for(goal_id).example_prompt, goal_id)
    for answer in answers:
        state = advance_with_choice(state, answer)
    return state


def _complete_first_path(goal_id: GoalId) -> PrototypeState:
    state = start_conversation(journey_for(goal_id).example_prompt, goal_id)
    while state.current_step is not None:
        state = advance_with_choice(state, available_choices(state)[0].value)
    return state


def _click_choice(
    app: AppTest, state: PrototypeState, index: int
) -> tuple[PrototypeState, AppTest]:
    assert state.active_goal is not None
    assert state.workspace_id is not None
    step_key = state.current_step or "refinement"
    choice = available_choices(state)[index]
    key = widget_key(
        "choice",
        state.workspace_id,
        state.active_goal.value,
        step_key,
        index,
        choice.value,
    )
    app.button(key=key).click().run(timeout=30)
    assert not app.exception
    return advance_with_choice(state, choice.value), app


def _contrast_ratio(first: str, second: str) -> float:
    def luminance(value: str) -> float:
        channels = tuple(int(value[index : index + 2], 16) / 255 for index in (1, 3, 5))
        adjusted = tuple(
            channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
            for channel in channels
        )
        return 0.2126 * adjusted[0] + 0.7152 * adjusted[1] + 0.0722 * adjusted[2]

    lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def _mock_source() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in _mock_paths())


def _mock_import_roots() -> set[str]:
    roots: set[str] = set()
    for path in _mock_paths():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", maxsplit=1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module.split(".", maxsplit=1)[0])
    return roots


def _mock_paths() -> tuple[Path, ...]:
    return tuple(
        path
        for path in EXPERIENCE_ROOT.rglob("*.py")
        if "live" not in path.relative_to(EXPERIENCE_ROOT).parts
        and not path.name.startswith("live_")
    )

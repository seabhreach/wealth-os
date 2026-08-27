# ruff: noqa: E501
"""Isolated illustrative journeys and evidence for the mock-only prototype."""

from __future__ import annotations

from experience.models import (
    Choice,
    GoalId,
    Journey,
    JourneyStep,
    PictureItem,
    WorkspaceSection,
)

DEFAULT_GOAL = GoalId.RETIRE_EARLIER


JOURNEYS: dict[GoalId, Journey] = {
    GoalId.RETIRE_EARLIER: Journey(
        goal_id=GoalId.RETIRE_EARLIER,
        title="Retire Before 60",
        recent_title="Retire before 60",
        example_prompt="Could I retire before 60?",
        keywords=("retire", "retirement", "before 60", "earlier"),
        initial_status="Understanding your situation",
        steps=(
            JourneyStep(
                "Are you planning for yourself or your household?",
                (Choice("Just me", "self"), Choice("My household", "household")),
                ("Why this matters", "Skip for now"),
                "picture-household",
            ),
            JourneyStep(
                "Let's start with you. How old are you?",
                (Choice("54", "54"), Choice("55", "55"), Choice("Use an estimate", "estimate")),
                ("Why this matters", "Use an estimate"),
                "initial-answer",
            ),
            JourneyStep(
                "If you picture a comfortable retirement, roughly how much would you like to spend each year?",
                (
                    Choice("About €70,000", "70000"),
                    Choice("About €80,000", "80000"),
                    Choice("I'm not sure", "unknown"),
                ),
                ("Why this matters", "Skip for now", "Use an estimate"),
                "outlook",
            ),
        ),
        sections=(
            WorkspaceSection(
                "picture-household",
                "Financial Picture",
                "Only the household detail relevant to this question is shown.",
                (PictureItem("Planning scope", "Household", "Known"),),
            ),
            WorkspaceSection(
                "initial-answer",
                "Initial answer",
                "An earlier retirement looks worth exploring, but spending and income timing will shape the comparison.",
                evidence=(("Exploration", "Baseline compared with retirement at 58"),),
            ),
            WorkspaceSection(
                "outlook",
                "Financial Outlook",
                "The mock outlook keeps the baseline visible and highlights where an earlier date changes funding.",
                picture_items=(
                    PictureItem("Current age", "54", "Known"),
                    PictureItem("Retirement spending", "€80,000", "Estimated"),
                    PictureItem("Pension access", "Not added yet", "Needs refinement"),
                ),
                evidence=(
                    ("Baseline retirement", "60"),
                    ("Explored retirement", "58"),
                    ("Confidence", "Early illustrative view"),
                ),
            ),
        ),
        completion_message=(
            "Here is an early illustrative comparison. We can refine pension access or expected income next, and I'll explain what each detail changes."
        ),
    ),
    GoalId.INVESTMENT_PROPERTY: Journey(
        goal_id=GoalId.INVESTMENT_PROPERTY,
        title="Investment Property",
        recent_title="Investment Property",
        example_prompt="How would an investment property change my outlook?",
        keywords=("property", "rental", "rent", "buy"),
        initial_status="Understanding the property idea",
        steps=(
            JourneyStep(
                "Is this a property you're considering soon, or something further out?",
                (Choice("In the next year", "soon"), Choice("A few years away", "later")),
                ("Why this matters", "Skip for now"),
                "property-goal",
            ),
            JourneyStep(
                "Roughly what purchase price would you like this illustration to use?",
                (
                    Choice("€200,000", "200000"),
                    Choice("€300,000", "300000"),
                    Choice("Use an estimate", "estimate"),
                ),
                ("Use an estimate",),
                "property-picture",
            ),
            JourneyStep(
                "What annual net rent should we explore after ordinary running costs?",
                (
                    Choice("€12,000", "12000"),
                    Choice("€18,000", "18000"),
                    Choice("I'm not sure", "unknown"),
                ),
                ("Why this matters", "Skip for now"),
                "property-comparison",
            ),
        ),
        sections=(
            WorkspaceSection(
                "property-goal",
                "Goal",
                "Explore the liquidity and income effect of a planned investment property.",
            ),
            WorkspaceSection(
                "property-picture",
                "Financial Picture",
                "Only the initial property assumptions are shown.",
                (
                    PictureItem("Purchase timing", "Next year", "Estimated"),
                    PictureItem("Purchase price", "€200,000", "Estimated"),
                ),
            ),
            WorkspaceSection(
                "property-comparison",
                "Comparison",
                "The mock comparison shows a lower cash balance after purchase and a new rental-income stream.",
                evidence=(
                    ("Scenario", "Planned property included"),
                    ("Net rent", "€12,000 illustrative"),
                    ("Not modelled here", "Financing, tax, transaction costs"),
                ),
            ),
        ),
        completion_message=(
            "This first comparison is illustrative. Financing, ownership and costs would need refinement before the Workspace could support a higher-confidence exploration."
        ),
    ),
    GoalId.EMPLOYER_EQUITY: Journey(
        goal_id=GoalId.EMPLOYER_EQUITY,
        title="Employer Equity",
        recent_title="Employer Equity",
        example_prompt="How exposed am I to employer equity?",
        keywords=(
            "employer equity",
            "company shares",
            "share exposure",
            "equity exposure",
            "vesting",
        ),
        initial_status="Understanding your exposure",
        steps=(
            JourneyStep(
                "Do you already hold employer shares, or are you mainly expecting future vesting?",
                (Choice("I hold shares now", "held"), Choice("Mostly future vesting", "future")),
                ("Why this matters", "Skip for now"),
                "equity-goal",
            ),
            JourneyStep(
                "About how much is the position worth today? An estimate is fine.",
                (
                    Choice("Under €100,000", "under-100k"),
                    Choice("€100,000 to €250,000", "100-250k"),
                    Choice("Use an estimate", "estimate"),
                ),
                ("Use an estimate",),
                "equity-picture",
            ),
            JourneyStep(
                "What currently happens when new shares vest?",
                (
                    Choice("Keep them", "retain"),
                    Choice("Sell on vest", "sell"),
                    Choice("It varies", "mixed"),
                ),
                ("Why this matters", "Skip for now"),
                "equity-insight",
            ),
        ),
        sections=(
            WorkspaceSection(
                "equity-goal",
                "Goal",
                "Understand employer-equity exposure and compare explicit disposal-policy assumptions.",
            ),
            WorkspaceSection(
                "equity-picture",
                "Financial Picture",
                "The issuer label may be shown, while the information type remains generic employer equity.",
                (
                    PictureItem("Employer-equity value", "€100,000 to €250,000", "Estimated"),
                    PictureItem("Future vesting", "Expected", "Known"),
                    PictureItem("Investable-assets denominator", "Not defined", "Needs refinement"),
                ),
            ),
            WorkspaceSection(
                "equity-insight",
                "Insight",
                "Retaining future vesting may increase single-position concentration in this mock illustration.",
                evidence=(
                    ("Baseline policy", "Retain on vest"),
                    ("Alternative", "Sell on vest"),
                    ("Boundary", "Exploration, not a recommendation"),
                ),
            ),
        ),
        completion_message=(
            "The Workspace now shows the exposure question and one policy comparison. It does not recommend buying, selling or retaining any position."
        ),
    ),
    GoalId.HIGHER_SPENDING: Journey(
        goal_id=GoalId.HIGHER_SPENDING,
        title="Retirement Spending",
        recent_title="Retirement Spending",
        example_prompt="What if I spent more in retirement?",
        keywords=("spend more", "higher spending", "retirement spending", "comfortable retirement"),
        initial_status="Understanding the spending change",
        steps=(
            JourneyStep(
                "What annual retirement spending would you like to explore?",
                (
                    Choice("€90,000", "90000"),
                    Choice("€100,000", "100000"),
                    Choice("Use an estimate", "estimate"),
                ),
                ("Why this matters", "Use an estimate"),
                "spending-goal",
            ),
            JourneyStep(
                "Should that amount apply throughout retirement, or only for the earlier years?",
                (
                    Choice("Throughout retirement", "all-years"),
                    Choice("Earlier years", "early-years"),
                ),
                ("Skip for now",),
                "spending-picture",
            ),
            JourneyStep(
                "Would you like to compare it with the current spending baseline?",
                (
                    Choice("Compare both", "compare"),
                    Choice("Show the higher amount", "higher-only"),
                ),
                (),
                "spending-comparison",
            ),
        ),
        sections=(
            WorkspaceSection(
                "spending-goal",
                "Goal",
                "Explore a higher retirement-spending assumption without changing the baseline.",
            ),
            WorkspaceSection(
                "spending-picture",
                "Financial Picture",
                "The explored amount remains a temporary Workspace assumption.",
                (
                    PictureItem("Baseline spending", "€80,000", "Known"),
                    PictureItem("Explored spending", "€100,000", "Estimated"),
                    PictureItem("Duration", "Throughout retirement", "Known"),
                ),
            ),
            WorkspaceSection(
                "spending-comparison",
                "Comparison",
                "Higher spending increases illustrated liquid funding and may reduce the resilience shown by the outlook.",
                evidence=(
                    ("Baseline", "€80,000 a year"),
                    ("Explored", "€100,000 a year"),
                    ("Confidence", "Sensitive to inflation and longevity"),
                ),
            ),
        ),
        completion_message=(
            "This comparison keeps both spending assumptions visible. It describes the modelled difference without choosing a spending level for you."
        ),
    ),
    GoalId.CASH_DECLINE: Journey(
        goal_id=GoalId.CASH_DECLINE,
        title="Cash Flow",
        recent_title="Cash Flow",
        example_prompt="Why does my cash decline in 2032?",
        keywords=("cash", "decline", "drop", "fall", "2032"),
        initial_status="Finding the relevant movement",
        steps=(
            JourneyStep(
                "I can explain that from the existing mock Financial Picture. Is 2032 the year you mean?",
                (Choice("Yes, 2032", "2032"), Choice("Choose another year", "other")),
                ("Why this matters",),
                "cash-answer",
            ),
            JourneyStep(
                "Would you like the short explanation or the movement breakdown?",
                (Choice("Short explanation", "short"), Choice("Show the breakdown", "breakdown")),
                (),
                "cash-evidence",
            ),
            JourneyStep(
                "Should I keep this explanation beside the baseline, or compare another scenario?",
                (Choice("Keep the baseline", "baseline"), Choice("Compare a scenario", "scenario")),
                ("Skip for now",),
                "cash-limitations",
            ),
        ),
        sections=(
            WorkspaceSection(
                "cash-answer",
                "Initial answer",
                "In the mock baseline, retirement spending begins to exceed recurring income in 2032, so cash funds the gap.",
            ),
            WorkspaceSection(
                "cash-evidence",
                "Evidence",
                "The illustrative movement reconciles opening cash, recurring income, tax, spending and closing cash.",
                evidence=(
                    ("Recurring income", "€42,972"),
                    ("Illustrative tax", "€4,588"),
                    ("Spending", "€90,093"),
                    ("Cash funding", "€51,709"),
                ),
            ),
            WorkspaceSection(
                "cash-limitations",
                "Limitations",
                "This is predefined mock evidence for experience validation, not a live calculation.",
                evidence=(("New data requested", "None"), ("Mode", "Illustrative mock")),
            ),
        ),
        completion_message=(
            "The movement now has a concise explanation and a supporting breakdown. No new Financial Picture data was needed."
        ),
    ),
}


def all_journeys() -> tuple[Journey, ...]:
    """Return all five validated mock journeys in goal order."""

    return tuple(JOURNEYS[goal_id] for goal_id in GoalId)


def journey_for(goal_id: GoalId) -> Journey:
    """Return the mock journey for a validated goal."""

    return JOURNEYS[goal_id]


def match_journey(user_message: str) -> GoalId | None:
    """Match an opening message to a journey with simple deterministic keywords."""

    normalized = user_message.casefold()
    for journey in all_journeys():
        if any(keyword in normalized for keyword in journey.keywords):
            return journey.goal_id
    return None

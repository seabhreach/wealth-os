# ruff: noqa: E501
"""Predefined journeys and evidence for the bounded mock-only prototype."""

from __future__ import annotations

from experience.models import (
    Choice,
    EvidencePurpose,
    GoalId,
    InformationStatus,
    Journey,
    PictureItem,
    QuestionStep,
    Refinement,
    WorkspaceSection,
)

QUESTION_IDS_BY_GOAL: dict[GoalId, frozenset[str]] = {
    GoalId.RETIRE_EARLIER: frozenset({"Q-001", "Q-002", "Q-004", "Q-005", "Q-008"}),
    GoalId.INVESTMENT_PROPERTY: frozenset({"Q-010", "Q-011", "Q-012", "Q-013", "Q-015"}),
    GoalId.EMPLOYER_EQUITY: frozenset({"Q-018", "Q-019", "Q-020", "Q-021", "Q-022"}),
    GoalId.HIGHER_SPENDING: frozenset({"Q-008", "Q-009", "Q-024", "Q-025", "Q-026"}),
    GoalId.CASH_DECLINE: frozenset(),
}
VALID_QUESTION_IDS = frozenset().union(*QUESTION_IDS_BY_GOAL.values())

K = InformationStatus.KNOWN
E = InformationStatus.ESTIMATED
U = InformationStatus.UNKNOWN
NR = InformationStatus.NOT_RELEVANT


JOURNEYS: dict[GoalId, Journey] = {
    GoalId.RETIRE_EARLIER: Journey(
        goal_id=GoalId.RETIRE_EARLIER,
        customer_name="Retire Earlier",
        title="Retire Before 60",
        recent_title="Retire before 60",
        example_prompt="Could I retire before 60?",
        keywords=("retire", "retirement", "before 60", "earlier"),
        initial_status="Understanding your situation",
        first_step="retire-scope",
        questions=(
            QuestionStep(
                "retire-scope",
                "Q-002",
                "Is anyone else part of this financial plan?",
                (
                    Choice(
                        "Just me",
                        "self",
                        next_step="retire-user-age",
                        reveal_section="retire-scope-self",
                    ),
                    Choice(
                        "My household",
                        "household",
                        next_step="retire-user-age",
                        reveal_section="retire-scope-household",
                    ),
                ),
                "Household scope determines whose ages, income and pensions matter to this exploration.",
            ),
            QuestionStep(
                "retire-user-age",
                "Q-001",
                "Let's start with you. How old are you?",
                (
                    Choice("54", "54"),
                    Choice("About 54", "54", E),
                    Choice("I'm not sure", "unknown", U),
                ),
                "Your age sets the projection horizon and the timing of an earlier retirement.",
                next_step="retire-target",
                reveal_section="retire-user-age",
                estimate_answer=("About 54", "54"),
                unknown_allowed=True,
            ),
            QuestionStep(
                "retire-partner-age",
                "Q-001",
                "And how old is your partner?",
                (
                    Choice("51", "51"),
                    Choice("About 51", "51", E),
                    Choice("I'm not sure", "unknown", U),
                ),
                "A partner's age affects household income and pension timing.",
                next_step="retire-target",
                reveal_section="retire-partner-age",
                estimate_answer=("About 51", "51"),
                unknown_allowed=True,
                skip_allowed=True,
            ),
            QuestionStep(
                "retire-target",
                "Q-004",
                "What age would you like to explore retiring at?",
                (Choice("58", "58"), Choice("59", "59"), Choice("About 58", "58", E)),
                "The target age defines the temporary scenario compared with the age-60 baseline.",
                next_step="retire-resources",
                reveal_section="retire-target",
                estimate_answer=("About 58", "58"),
            ),
            QuestionStep(
                "retire-resources",
                "Q-005",
                "About how much do you have across cash, investments, and pensions?",
                (
                    Choice("About €1.7m", "1700000", E),
                    Choice("About €2m", "2000000", E),
                    Choice("I'm not sure", "unknown", U),
                ),
                "Opening resources help show how the bridge before pension income could be funded.",
                next_step="retire-spending",
                reveal_section="retire-resources",
                estimate_answer=("About €1.7m", "1700000"),
                unknown_allowed=True,
                skip_allowed=True,
            ),
            QuestionStep(
                "retire-spending",
                "Q-008",
                "What annual spending would you like retirement to support?",
                (
                    Choice("€80,000", "80000"),
                    Choice("About €90,000", "90000", E),
                    Choice("I'm not sure", "unknown", U),
                ),
                "Spending determines the funding target for the first illustrative comparison.",
                reveal_section="retire-answer",
                estimate_answer=("About €90,000", "90000"),
                unknown_allowed=True,
                enough_information=True,
            ),
        ),
        sections=(
            WorkspaceSection(
                "retire-scope-self",
                "Goal",
                "Explore retiring earlier for one person.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Planning scope", "Just me", K),),
            ),
            WorkspaceSection(
                "retire-scope-household",
                "Goal",
                "Explore retiring earlier across the household.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Planning scope", "Household", K),),
            ),
            WorkspaceSection(
                "retire-user-age",
                "Financial Picture",
                "The first relevant age is now visible.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Your age", "54", K),),
            ),
            WorkspaceSection(
                "retire-partner-age",
                "Household context",
                "The mock household timeline now includes a partner.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Partner age", "51", E),),
            ),
            WorkspaceSection(
                "retire-target",
                "Explored timing",
                "The earlier age remains a temporary Workspace assumption.",
                EvidencePurpose.COMPARISON,
                evidence=(("Current plan", "Retire at 60"), ("Explored age", "58")),
            ),
            WorkspaceSection(
                "retire-resources",
                "Bridge context",
                "Liquid assets may need to bridge the period before pension income begins.",
                EvidencePurpose.EXPLANATION,
                evidence=(
                    ("Opening resources", "Illustrative €1.7m"),
                    ("Pension timing", "Later than explored retirement"),
                ),
            ),
            WorkspaceSection(
                "retire-answer",
                "Initial answer",
                "The mock view can now show the main trade-off: retiring at 58 creates a longer bridge funded from liquid assets.",
                EvidencePurpose.ANSWER,
                evidence=(
                    ("Earlier path", "Two additional bridge years"),
                    ("First unfunded year", "None in this mock view"),
                    ("Limitation", "Estimates can be refined later"),
                ),
            ),
            WorkspaceSection(
                "retire-refine-58",
                "Age comparison",
                "The existing Workspace now focuses on retirement at 58 beside the age-60 baseline.",
                EvidencePurpose.COMPARISON,
                evidence=(("Baseline", "60"), ("Refined scenario", "58")),
            ),
            WorkspaceSection(
                "retire-refine-60",
                "Age comparison",
                "The existing Workspace now restores retirement at 60 as the comparison focus.",
                EvidencePurpose.COMPARISON,
                evidence=(("Baseline", "60"), ("Refined scenario", "60")),
            ),
        ),
        enough_message="I have enough for a first view. Any estimates remain visible and can be refined later.",
        refinement=Refinement(
            "The same Workspace can now compare retirement at 58 with 60.",
            (
                Choice("Focus on age 58", "58", reveal_section="retire-refine-58"),
                Choice("Focus on age 60", "60", reveal_section="retire-refine-60"),
            ),
        ),
        saved_sections=(
            "retire-scope-self",
            "retire-user-age",
            "retire-target",
            "retire-resources",
            "retire-answer",
        ),
    ),
    GoalId.INVESTMENT_PROPERTY: Journey(
        goal_id=GoalId.INVESTMENT_PROPERTY,
        customer_name="Investment Property Decision",
        title="Investment Property",
        recent_title="Investment Property",
        example_prompt="How would an investment property change my outlook?",
        keywords=("property", "rental", "rent", "buy"),
        initial_status="Understanding the property idea",
        first_step="property-timing",
        questions=(
            QuestionStep(
                "property-timing",
                "Q-010",
                "When might you buy the property?",
                (Choice("Next year", "2027"), Choice("In about three years", "2029", E)),
                "Timing determines when cash or financing would be needed.",
                next_step="property-price",
                reveal_section="property-timing",
                estimate_answer=("In about three years", "2029"),
            ),
            QuestionStep(
                "property-price",
                "Q-011",
                "What purchase price should we explore?",
                (
                    Choice("€200,000", "200000"),
                    Choice("About €300,000", "300000", E),
                    Choice("I'm not sure", "unknown", U),
                ),
                "Purchase price sets the size of the illustrative liquidity effect.",
                next_step="property-funding",
                reveal_section="property-price",
                estimate_answer=("About €300,000", "300000"),
                unknown_allowed=True,
            ),
            QuestionStep(
                "property-funding",
                "Q-012",
                "How would the purchase be funded?",
                (
                    Choice(
                        "Cash", "cash", next_step="property-rent", reveal_section="property-cash"
                    ),
                    Choice(
                        "Financing",
                        "financing",
                        next_step="property-rent",
                        reveal_section="property-financing",
                    ),
                    Choice(
                        "I'm not sure",
                        "unknown",
                        U,
                        next_step="property-rent",
                        reveal_section="property-financing",
                    ),
                ),
                "Funding determines whether this mock can show a cash impact or must expose a financing limitation.",
                unknown_allowed=True,
            ),
            QuestionStep(
                "property-rent",
                "Q-013",
                "What annual net rent and value growth should this illustration use?",
                (
                    Choice("€12,000 rent · 2% growth", "12000@2", E),
                    Choice("€18,000 rent · 2% growth", "18000@2", E),
                    Choice("I'm not sure", "unknown", U),
                ),
                "Rent and growth make the income and asset-path assumptions explicit.",
                next_step="property-ownership",
                reveal_section="property-rent",
                estimate_answer=("€12,000 rent · 2% growth", "12000@2"),
                unknown_allowed=True,
                skip_allowed=True,
            ),
            QuestionStep(
                "property-ownership",
                "Q-015",
                "How is the property expected to be owned?",
                (
                    Choice("Jointly", "joint"),
                    Choice("One owner", "single"),
                    Choice("I'm not sure", "unknown", U),
                ),
                "Ownership may matter to a later supported tax comparison; this mock only records the limitation.",
                reveal_section="property-answer",
                unknown_allowed=True,
                skip_allowed=True,
                enough_information=True,
            ),
        ),
        sections=(
            WorkspaceSection(
                "property-timing",
                "Goal",
                "The purchase timing is now part of this temporary exploration.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Purchase year", "2027", E),),
            ),
            WorkspaceSection(
                "property-price",
                "Purchase assumption",
                "The indicative price is visible before any comparison appears.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Purchase price", "€200,000", E),),
            ),
            WorkspaceSection(
                "property-cash",
                "Liquidity impact",
                "A cash purchase reduces liquid assets when the property is acquired.",
                EvidencePurpose.TRADE_OFF,
                evidence=(("Funding", "Cash"), ("Purchase cash impact", "Illustrative €200,000")),
            ),
            WorkspaceSection(
                "property-financing",
                "Financing limitation",
                "Financing details would be required for a refined comparison; mortgage outcomes are not modelled here.",
                EvidencePurpose.LIMITATION,
                evidence=(("Funding", "Financing"), ("Mortgage model", "Not available")),
            ),
            WorkspaceSection(
                "property-rent",
                "Property evidence",
                "The mock adds recurring rent and a declared value-growth assumption.",
                EvidencePurpose.EXPLANATION,
                evidence=(("Net rent", "Illustrative €12,000"), ("Value growth", "2% assumption")),
            ),
            WorkspaceSection(
                "property-answer",
                "Initial comparison",
                "That gives enough for an initial baseline-versus-property comparison, with unsupported costs kept visible.",
                EvidencePurpose.COMPARISON,
                evidence=(
                    ("Baseline", "No planned property"),
                    ("Scenario", "Property included"),
                    ("Limitations", "Tax, vacancy, transaction costs and financing detail"),
                ),
            ),
            WorkspaceSection(
                "property-refine-low",
                "Rent refinement",
                "The same Workspace now uses €12,000 indicative annual net rent.",
                EvidencePurpose.COMPARISON,
                evidence=(("Refined rent", "€12,000"),),
            ),
            WorkspaceSection(
                "property-refine-high",
                "Rent refinement",
                "The same Workspace now uses €18,000 indicative annual net rent.",
                EvidencePurpose.COMPARISON,
                evidence=(("Refined rent", "€18,000"),),
            ),
        ),
        enough_message="That gives me enough for an initial comparison. Financing and ownership limits stay explicit.",
        refinement=Refinement(
            "Expected rent can be changed inside this Workspace.",
            (
                Choice("Use €12,000 rent", "12000", E, reveal_section="property-refine-low"),
                Choice("Use €18,000 rent", "18000", E, reveal_section="property-refine-high"),
            ),
        ),
        saved_sections=(
            "property-timing",
            "property-price",
            "property-cash",
            "property-rent",
            "property-answer",
        ),
    ),
    GoalId.EMPLOYER_EQUITY: Journey(
        goal_id=GoalId.EMPLOYER_EQUITY,
        customer_name="Employer Equity Exposure",
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
        first_step="equity-position",
        questions=(
            QuestionStep(
                "equity-position",
                "Q-018",
                "What employer-equity position do you hold today?",
                (
                    Choice("About €100,000", "100000", E),
                    Choice("About €200,000", "200000", E),
                    Choice("I'm not sure", "unknown", U),
                ),
                "The current position establishes the illustrative exposure baseline.",
                next_step="equity-future",
                reveal_section="equity-position",
                estimate_answer=("About €100,000", "100000"),
                unknown_allowed=True,
            ),
            QuestionStep(
                "equity-future",
                "Q-019",
                "Are more grants or vesting events expected?",
                (
                    Choice("No future awards", "none", NR, reveal_section="equity-no-future"),
                    Choice("Future awards expected", "expected", reveal_section="equity-future"),
                ),
                "Future awards determine whether future concentration belongs in the evidence.",
                next_step="equity-price",
            ),
            QuestionStep(
                "equity-price",
                "Q-020",
                "What price and currency assumptions should this exploration use?",
                (
                    Choice("Current mock EUR value", "baseline"),
                    Choice("Use an approximate value", "estimate", E),
                    Choice("I'm not sure", "unknown", U),
                ),
                "A declared valuation basis prevents the mock from implying live market data.",
                next_step="equity-policy",
                reveal_section="equity-assumptions",
                estimate_answer=("Use an approximate value", "estimate"),
                unknown_allowed=True,
            ),
            QuestionStep(
                "equity-policy",
                "Q-021",
                "What happens to shares when they vest in the current baseline?",
                (
                    Choice("Retain them", "retain"),
                    Choice("Sell on vest", "sell"),
                    Choice("It varies", "mixed", U),
                ),
                "The baseline disposal policy shapes concentration through time.",
                next_step="equity-alternative",
                reveal_section="equity-policy",
                unknown_allowed=True,
                skip_allowed=True,
            ),
            QuestionStep(
                "equity-alternative",
                "Q-022",
                "Which disposal-policy alternative would you like to compare?",
                (
                    Choice("Sell on vest", "sell"),
                    Choice("Retain", "retain"),
                    Choice("No comparison yet", "none", NR),
                ),
                "A user-selected alternative makes the comparison exploratory rather than advice.",
                reveal_section="equity-answer",
                enough_information=True,
            ),
        ),
        sections=(
            WorkspaceSection(
                "equity-position",
                "Exposure context",
                "The position is shown as generic employer equity using an indicative value.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Employer-equity value", "About €100,000", E),),
            ),
            WorkspaceSection(
                "equity-no-future",
                "Future awards",
                "No future awards are included in this mock path.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Future awards", "None expected", NR),),
            ),
            WorkspaceSection(
                "equity-future",
                "Future concentration",
                "Expected awards may add to single-position concentration over time.",
                EvidencePurpose.INSIGHT,
                (PictureItem("Future awards", "Expected", K),),
            ),
            WorkspaceSection(
                "equity-assumptions",
                "Valuation basis",
                "The comparison uses an explicit mock value and no live price feed.",
                EvidencePurpose.ASSUMPTION,
                evidence=(("Currency", "EUR illustration"), ("Live market data", "Not connected")),
            ),
            WorkspaceSection(
                "equity-policy",
                "Baseline policy",
                "The existing disposal policy is visible before an alternative is compared.",
                EvidencePurpose.EXPLANATION,
                evidence=(("Baseline", "Retain on vest"),),
            ),
            WorkspaceSection(
                "equity-answer",
                "Initial comparison",
                "The main trade-off is liquidity versus concentration under explicit retain and sell-on-vest assumptions.",
                EvidencePurpose.TRADE_OFF,
                evidence=(
                    ("Retain", "Higher concentration path"),
                    ("Sell on vest", "Higher liquidity path"),
                    ("Boundary", "Not a recommendation"),
                ),
            ),
            WorkspaceSection(
                "equity-refine-sell",
                "Policy refinement",
                "The same Workspace now focuses on the sell-on-vest illustration.",
                EvidencePurpose.COMPARISON,
                evidence=(("Policy", "Sell on vest"),),
            ),
            WorkspaceSection(
                "equity-refine-retain",
                "Policy refinement",
                "The same Workspace now focuses on the retain illustration.",
                EvidencePurpose.COMPARISON,
                evidence=(("Policy", "Retain"),),
            ),
        ),
        enough_message="That's enough to show the main trade-off without choosing a policy for you.",
        refinement=Refinement(
            "The same Workspace can focus on either disposal-policy illustration.",
            (
                Choice("Focus on sell on vest", "sell", reveal_section="equity-refine-sell"),
                Choice("Focus on retain", "retain", reveal_section="equity-refine-retain"),
            ),
        ),
        saved_sections=(
            "equity-position",
            "equity-future",
            "equity-assumptions",
            "equity-policy",
            "equity-answer",
        ),
    ),
    GoalId.HIGHER_SPENDING: Journey(
        goal_id=GoalId.HIGHER_SPENDING,
        customer_name="Higher Retirement Spending",
        title="Retirement Spending",
        recent_title="Retirement Spending",
        example_prompt="What if I spent more in retirement?",
        keywords=("spend more", "higher spending", "retirement spending", "comfortable retirement"),
        initial_status="Understanding the spending change",
        first_step="spending-baseline",
        questions=(
            QuestionStep(
                "spending-baseline",
                "Q-008",
                "What annual spending does the current retirement view support?",
                (
                    Choice("€80,000", "80000"),
                    Choice("About €80,000", "80000", E),
                    Choice("I'm not sure", "unknown", U),
                ),
                "The current amount is the baseline for the temporary comparison.",
                next_step="spending-higher",
                reveal_section="spending-baseline",
                estimate_answer=("About €80,000", "80000"),
                unknown_allowed=True,
                skip_allowed=True,
            ),
            QuestionStep(
                "spending-higher",
                "Q-024",
                "What higher annual amount would you like to explore?",
                (
                    Choice("€90,000", "90000"),
                    Choice("About €100,000", "100000", E),
                    Choice("I'm not sure", "unknown", U),
                ),
                "The higher amount defines the Workspace override.",
                next_step="spending-timing",
                reveal_section="spending-higher",
                estimate_answer=("About €100,000", "100000"),
                unknown_allowed=True,
            ),
            QuestionStep(
                "spending-timing",
                "Q-025",
                "Should the higher amount apply from retirement onward or for a limited period?",
                (
                    Choice(
                        "Permanent",
                        "permanent",
                        next_step="spending-basis",
                        reveal_section="spending-permanent",
                    ),
                    Choice(
                        "Temporary",
                        "temporary",
                        next_step="spending-duration",
                        reveal_section="spending-temporary",
                    ),
                ),
                "Duration changes whether this is a lifetime or temporary spending effect.",
            ),
            QuestionStep(
                "spending-duration",
                "Q-025",
                "How long should the temporary higher spending last?",
                (
                    Choice("First 5 years", "5"),
                    Choice("First 10 years", "10"),
                    Choice("I'm not sure", "unknown", U),
                ),
                "Duration is needed only for the temporary path.",
                next_step="spending-basis",
                reveal_section="spending-duration",
                unknown_allowed=True,
                skip_allowed=True,
            ),
            QuestionStep(
                "spending-basis",
                "Q-026",
                "Is this amount in today's money?",
                (
                    Choice("Yes, today's money", "today"),
                    Choice("No, future amount", "future"),
                    Choice("I'm not sure", "unknown", U),
                ),
                "The value basis determines how the temporary assumption relates to inflation.",
                next_step="spending-inflation",
                reveal_section="spending-basis",
                unknown_allowed=True,
            ),
            QuestionStep(
                "spending-inflation",
                "Q-009",
                "Should this first view use the current inflation assumption?",
                (
                    Choice("Use the current assumption", "baseline"),
                    Choice("Leave it unknown", "unknown", U),
                ),
                "Keeping the baseline assumption explicit avoids implying a forecast.",
                reveal_section="spending-answer",
                unknown_allowed=True,
                skip_allowed=True,
                enough_information=True,
            ),
        ),
        sections=(
            WorkspaceSection(
                "spending-baseline",
                "Baseline",
                "The current spending target remains visible and unchanged.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Baseline spending", "€80,000", K),),
            ),
            WorkspaceSection(
                "spending-higher",
                "Explored amount",
                "The higher amount is a temporary Workspace override.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Higher spending", "€100,000", E),),
            ),
            WorkspaceSection(
                "spending-permanent",
                "Lifetime spending",
                "The higher amount applies throughout retirement in this branch.",
                EvidencePurpose.EXPLANATION,
                (PictureItem("Duration", "Permanent", K),),
            ),
            WorkspaceSection(
                "spending-temporary",
                "Temporary spending",
                "The higher amount applies only for an initial period.",
                EvidencePurpose.EXPLANATION,
                (PictureItem("Duration", "Temporary", K),),
            ),
            WorkspaceSection(
                "spending-duration",
                "Temporary period",
                "The limited higher-spending period is now explicit.",
                EvidencePurpose.ASSUMPTION,
                (PictureItem("Higher-spending period", "First 5 years", E),),
            ),
            WorkspaceSection(
                "spending-basis",
                "Value basis",
                "The amount's time basis is visible before the comparison.",
                EvidencePurpose.ASSUMPTION,
                evidence=(("Basis", "Today's money"),),
            ),
            WorkspaceSection(
                "spending-answer",
                "Initial comparison",
                "Higher spending uses liquid assets sooner; a permanent change has a larger lifetime effect than a temporary one.",
                EvidencePurpose.COMPARISON,
                evidence=(
                    ("First unfunded year", "None in this mock view"),
                    ("Liquid-assets impact", "Lower than baseline"),
                    ("Final wealth impact", "Lower than baseline"),
                ),
            ),
            WorkspaceSection(
                "spending-refine-temporary",
                "Timing refinement",
                "The same Workspace now compares a temporary higher-spending period.",
                EvidencePurpose.COMPARISON,
                evidence=(("Refined timing", "Temporary"),),
            ),
            WorkspaceSection(
                "spending-refine-permanent",
                "Timing refinement",
                "The same Workspace now compares permanent higher spending.",
                EvidencePurpose.COMPARISON,
                evidence=(("Refined timing", "Permanent"),),
            ),
        ),
        enough_message="I have enough for a first spending comparison, with any unknowns shown as limitations.",
        refinement=Refinement(
            "The existing Workspace can switch the spending timing once.",
            (
                Choice(
                    "Compare temporary", "temporary", reveal_section="spending-refine-temporary"
                ),
                Choice(
                    "Compare permanent", "permanent", reveal_section="spending-refine-permanent"
                ),
            ),
        ),
        saved_sections=(
            "spending-baseline",
            "spending-higher",
            "spending-permanent",
            "spending-basis",
            "spending-answer",
        ),
    ),
    GoalId.CASH_DECLINE: Journey(
        goal_id=GoalId.CASH_DECLINE,
        customer_name="Cash Decline Explanation",
        title="Cash Flow",
        recent_title="Cash Flow",
        example_prompt="Why does my cash decline in 2032?",
        keywords=("cash", "decline", "drop", "fall", "2032"),
        initial_status="Explaining the existing picture",
        first_step=None,
        questions=(),
        sections=(
            WorkspaceSection(
                "cash-answer",
                "Initial answer",
                "Cash falls because retirement spending exceeds recurring income, so the remaining gap is funded from cash.",
                EvidencePurpose.ANSWER,
                evidence=(("Selected year", "2032"), ("Cause", "Spending gap")),
            ),
            WorkspaceSection(
                "cash-evidence",
                "Cash movement",
                "The predefined mock evidence reconciles the selected year without collecting new data.",
                EvidencePurpose.EXPLANATION,
                evidence=(
                    ("Opening cash", "€1,872,606"),
                    ("Recurring income", "€42,972"),
                    ("Illustrative tax", "€4,588"),
                    ("Spending", "€90,093"),
                    ("Cash used", "€51,709"),
                    ("Closing cash", "€1,820,897"),
                ),
            ),
            WorkspaceSection(
                "cash-transition",
                "Funding transition",
                "Private pension income starts in 2032, while cash continues to fund the remaining spending gap.",
                EvidencePurpose.INSIGHT,
                evidence=(
                    ("Private pension timing", "Begins in 2032"),
                    ("Investment sales", "Not required in this mock baseline"),
                ),
            ),
            WorkspaceSection(
                "cash-limitation",
                "Evidence boundary",
                "This explanation uses existing illustrative evidence and does not add or infer Financial Picture values.",
                EvidencePurpose.LIMITATION,
                evidence=(("New data requested", "None"), ("Mode", "Illustrative mock")),
            ),
            WorkspaceSection(
                "cash-refine-2032",
                "Year refinement",
                "The same Workspace remains focused on the 2032 cash movement.",
                EvidencePurpose.EXPLANATION,
                evidence=(("Selected year", "2032"),),
            ),
            WorkspaceSection(
                "cash-refine-2035",
                "Year refinement",
                "The same Workspace now focuses on the predefined 2035 cash movement.",
                EvidencePurpose.EXPLANATION,
                evidence=(
                    ("Selected year", "2035"),
                    ("Private pension timing", "Both pensions have begun"),
                ),
            ),
        ),
        enough_message="I can explain the pattern from what we already know. No new data is needed.",
        refinement=Refinement(
            "A specific year can be selected inside this Workspace.",
            (
                Choice("Explain 2032", "2032", reveal_section="cash-refine-2032"),
                Choice("Explain 2035", "2035", reveal_section="cash-refine-2035"),
            ),
        ),
        saved_sections=("cash-answer", "cash-evidence", "cash-transition", "cash-limitation"),
    ),
}


def all_journeys() -> tuple[Journey, ...]:
    """Return all five validated mock journeys in goal order."""

    return tuple(JOURNEYS[goal_id] for goal_id in GoalId)


def journey_for(goal_id: GoalId) -> Journey:
    """Return the mock journey for a validated goal."""

    return JOURNEYS[goal_id]


def question_for(journey: Journey, step_key: str) -> QuestionStep:
    """Return one question from a journey's finite scripted graph."""

    return next(question for question in journey.questions if question.key == step_key)


def match_journey(user_message: str) -> GoalId | None:
    """Match supported intent using explicit phrases, preferring the most specific."""

    normalized = " ".join(user_message.casefold().replace("-", " ").split())
    phrases = (
        (
            GoalId.CASH_DECLINE,
            (
                "why does my cash decline",
                "why is my cash falling",
                "cash falls after retirement",
                "why does cash fall",
                "cash going down",
                "explain my cash balance",
                "cash decline",
                "cash falling",
                "cash fall",
            ),
        ),
        (
            GoalId.EMPLOYER_EQUITY,
            (
                "dependent on my employer shares",
                "concentration in employer shares",
                "employer shares",
                "company shares",
                "employer equity",
                "stock awards",
                "share exposure",
                "equity exposure",
                "rsus",
                "vesting",
            ),
        ),
        (
            GoalId.INVESTMENT_PROPERTY,
            (
                "buy an investment property",
                "buy another property",
                "property investment",
                "investment property",
                "rental property",
            ),
        ),
        (
            GoalId.HIGHER_SPENDING,
            (
                "increase retirement spending",
                "higher retirement spending",
                "spend more in retirement",
                "spent more in retirement",
                "extra spending",
                "spend more",
                "retirement spending",
            ),
        ),
        (
            GoalId.RETIRE_EARLIER,
            (
                "stop working earlier",
                "retire before 60",
                "retire earlier",
                "retire at 58",
                "earlier retirement",
            ),
        ),
    )
    matches = (
        (len(phrase), goal_id)
        for goal_id, goal_phrases in phrases
        for phrase in goal_phrases
        if phrase in normalized
    )
    selected = max(matches, default=None, key=lambda item: item[0])
    if selected is not None:
        return selected[1]
    return None

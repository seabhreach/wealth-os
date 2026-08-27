# First-Run Journey

## Purpose

This storyboard describes the first five minutes of Wealth OS. It validates a conversation-first
experience and progressive Financial Picture; it does not prescribe implementation or change the
v0.2 engine.

## Minute 0: Welcome

The initial screen is calm and contains no dashboard or long form.

> What would you like to explore today?

Examples may include retiring earlier, understanding a cash decline, exploring a property, or
changing retirement spending. The user may also answer in their own words.

Home is the beginning of a conversation. Recent Workspaces, previously explored goals, and quiet
access to standard views may appear secondarily, but Home does not expose forms, configuration,
engine terminology, completeness meters, or discovery mechanics.

## Minute 1: Natural Conversation

Conversation occupies the primary surface and confirms intent naturally:

- “When you say earlier, is there an age you have in mind?”
- “Would you like to understand the current outlook first, or compare it with buying the
  property?”
- “Is the cash decline something you noticed in a particular year?”

The product does not announce a scripted intake process. It responds to what the person said and
explains only ambiguity that materially affects the exploration. The user should experience chat,
not a wizard, financial questionnaire, or dashboard with a chatbot beside it.

## Minutes 1–3: Existing Financial Picture First

Before asking anything, the Discovery Model checks the active goal against information already
available in the Financial Picture. It asks only for missing information that materially affects
the requested exploration. For a returning user, many or all relevant facts may already be known.
Wealth OS should make that continuity felt: “I already have your pension and investment
information. I just need to check what retirement spending you want me to use.”

For a new user, one natural answer may supply several Information Items. “I’m 55, my wife is 53,
and I’d ideally stop working at 58” can establish household ages and the explored retirement age.
The Discovery Model owns what is needed, but the user never sees a one-question-per-item checklist.

Questions use ordinary language and allow estimates or “I don’t know” where the information model
permits it:

- “Roughly how much do you have in cash today? An estimate is fine.”
- “What annual spending would you like the retirement outlook to support?”
- “Should I use your current savings rate for this first view?”

Each follow-up earns its place: “This helps estimate how long your liquid assets may support the
earlier date.” A rough estimate is acceptable where policy permits it. Known, estimated, assumed,
and unknown statuses remain structured Financial Picture concepts without becoming a visible
discovery form.

## Minute 3: Enough Information

When the Discovery Model determines that available information is sufficient for a useful initial
answer, the experience reaches **Enough Information**. The transition is explicit in the
conversation:

> I have enough to show you what retiring at 58 could look like.

The transition may happen automatically. There is no generic Submit or Continue action.

## Minutes 3–4: First Visual Workspace

Wealth OS runs deterministic engines and creates the first question-specific Workspace. The
Workspace becomes the primary surface and normally uses most or all available width. It includes:

- a concise answer to the open question;
- a primary visualisation such as a wealth trajectory, funding timeline, or cash-flow view;
- a baseline comparison or relevant milestone;
- the assumptions that matter most;
- visible limitations and confidence;
- one or two useful next refinements.

The Workspace is a visual answer, not a standard dashboard or a dump of deterministic evidence.
Its components are chosen because they improve understanding of the current question.

An early result may use explicit estimates. It must say so and must not imply greater precision
than the inputs support.

## Minute 4: Explore a Nearby Scenario

The user explores one nearby scenario through a relevant visual control—for example, retirement
age 57, 58, 59, or 60; include or exclude a property; retain or sell employer equity on vest; or a
higher spending level. The flow remains:

```text
baseline
→ temporary scenario
→ deterministic calculation
→ updated Workspace
```

Temporary scenario values remain Workspace overrides and do not silently replace baseline
information. Material permanent updates still require proposed update, review, and confirmation.

## Minute 4+: Ask Why or What If

User: “What if I retired at 58 instead?”

Conversation is now secondary to the Workspace and may appear as a drawer, panel, rail, or overlay.
Wealth OS creates a comparison using an immutable retirement-age override. It may answer in text,
highlight an existing visual, add a relevant visualisation, or update the temporary scenario. It
shows the baseline and age-58 paths, funding difference, relevant constraints, assumptions, and
confidence without recommending either path.

The user may then ask, “Why does cash fall at 60?” or “What spending level would make the
difference smaller?” Conversation controls and explains the Workspace while preserving the
original question and baseline.

## End of Session

Before the session ends, Wealth OS summarizes:

- what was explored;
- what the model showed under which assumptions;
- which Financial Picture updates were confirmed;
- important unknowns or professional-verification needs;
- saved Workspaces and useful follow-up explorations.

No temporary exploration becomes baseline data without explicit review and confirmation.

## Returning User

Home opens with the current goal entry point, recent Workspaces, and notable deterministic Insights.
The user can resume a Workspace, ask why an outlook changed, or start a new question. Wealth OS
checks Financial Picture freshness and asks only about material changes rather than repeating
discovery from the beginning.

## First-Five-Minute Success

The first five minutes must demonstrate both conversational intelligence and visual financial
understanding:

1. Ask a question.
2. Hold a natural conversation.
3. Use the existing Financial Picture.
4. Ask only for material missing information.
5. Reach Enough Information.
6. Generate a visual Workspace.
7. Explore a nearby scenario.
8. Ask “why?” or “what if?”
9. Respond visually in the Workspace.
10. Save or revisit the session.

On narrow screens, Conversation occupies the screen during discovery. After generation, the
Workspace occupies the screen and Conversation reopens secondarily. The journey does not depend on
permanent side-by-side columns.

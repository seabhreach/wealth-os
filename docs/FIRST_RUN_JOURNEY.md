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

## Minute 1: Understand the Question

The conversation confirms intent naturally:

- “When you say earlier, is there an age you have in mind?”
- “Would you like to understand the current outlook first, or compare it with buying the
  property?”
- “Is the cash decline something you noticed in a particular year?”

The product does not announce a scripted intake process. It responds to what the person said and
explains any ambiguity that matters.

## Minutes 1–3: Conversational Discovery

The Discovery Model checks the active goal against information already available. It asks only
enough initial questions to produce something useful. For a new user this might include current
age, household members, approximate cash and investments, expected savings, intended retirement
age, and retirement spending. For a returning user, many or all of these may already be known.

Questions use ordinary language and allow estimates or “I don’t know” where the information model
permits it:

- “Roughly how much do you have in cash today? An estimate is fine.”
- “What annual spending would you like the retirement outlook to support?”
- “Should I use your current savings rate for this first view?”

Each follow-up earns its place: “This helps estimate how long your liquid assets may support the
earlier date.” The user can see whether a value is known, estimated, assumed, or unknown.

## Minutes 3–4: First Useful Financial Outlook

As soon as the minimum information is sufficient, Wealth OS runs deterministic engines and shows
a useful first Financial Outlook. It includes:

- a concise answer to the open question;
- a baseline trajectory or relevant milestone;
- the assumptions that matter most;
- visible limitations and confidence;
- one or two useful next refinements.

The key product rule is: deliver a useful first outlook early, then make every additional question
explain how it improves confidence or exploration.

An early result may use explicit estimates. It must say so and must not imply greater precision
than the inputs support.

## Minute 4+: Progressive Financial Picture

The user can continue refining the result without leaving the conversation. A side panel or linked
view shows the Financial Picture and proposed updates. Additional details are requested only when
they improve the current Workspace or unlock a desired comparison.

Material updates follow review and confirmation. Temporary scenario values remain Workspace
overrides and do not silently replace baseline information.

## Example Strategy Exploration

User: “What if I retired at 58 instead?”

Wealth OS creates a comparison in the current Workspace using an immutable retirement-age
override. It shows the baseline and age-58 paths, the funding difference, relevant constraints,
assumptions, and confidence. The response describes trade-offs without recommending either path.

The user may then ask, “What spending level would make the difference smaller?” The Workspace
evolves to include that comparison while preserving the original question and baseline.

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

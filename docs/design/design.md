# UI design direction

## 1. Purpose and status

2026-10-21: a local portfolio interface for asking questions, inspecting generated
SQL, and understanding the evidence behind the result. The answer should be the first
thing a reviewer notices after submitting a question.

This document consolidates the teal / IBM Plex direction already implemented in
`546eac6` after the owner's approval of the [mockup](index.html). Refinements below
are Codex's recommendations for the next pass, not a claim of further owner approval
or completed implementation. The current application remains Streamlit.

Reference captures: [desktop answer](../screenshots/01-answer.png),
[narrow answer](../screenshots/04-narrow.png), and their
[capture provenance](../screenshots/capture.json). These are real application captures
at `dffd005`; the mockup is a separate design artifact.

## 2. What to take from FarmLens

FarmLens's `web/style.css` and `docs/screenshots/showcase-explorer.png` show a coherent
system: locally served Inter and Manrope, cream surroundings, white cards, restrained
green and yellow accents, and clear groups of related information. Its map and land
imagery also provide visual interest that a SQL workspace naturally lacks.

Transfer the consistency, card hierarchy, readable labels, and purposeful whitespace.
Here the data chart and inspectable SQL provide the visual focus. Keep this project's
cool paper and teal identity; replacing its fonts and colors again would not resolve
the remaining density and hierarchy problems.

## 3. Color palette

Recommended light palette. The first eight colors already appear in the implementation;
the warning pair, failure pair and focus token are proposed refinements. When implemented,
keep theme, CSS and chart colors aligned rather than maintaining independent literals.

| Role | Color | Use |
| --- | --- | --- |
| Canvas | `#F6F7F4` | Page background |
| Surface | `#FFFFFF` | Answer, explanation and connection panels |
| Ink | `#1C2430` | Headings, body text and chart values |
| Muted | `#5D6672` | Supporting copy and metadata |
| Divider | `#DCE0DA` | Decorative separators and card outlines |
| Primary | `#0E6E66` | Ask button, active navigation, selected chart bar |
| Primary tint | `#E3F0ED` | Selected table chips and status backgrounds |
| Secondary bar | `#9CC5BF` | Other bars, with dark labels and tooltips |
| Warning / background | `#8A5A00` / `#FFF4D6` | Refusal, truncation and limitations |
| Failure / background | `#B42318` / `#FFF0EE` | Provider and execution failures |
| Focus | `#165DBA` | Visible keyboard focus outline |

Calculated opaque color-pair contrast: ink/canvas 14.53:1, muted/canvas 5.41:1,
white/primary 6.10:1, primary/primary-tint 5.22:1, warning pair 5.41:1,
failure pair 5.93:1. These calculations are not a rendered accessibility audit.
The pale divider is not a sufficient standalone control boundary. Use a stronger
outline for inputs and focus; keep essential chart values readable without bar color.

Teal expresses emphasis as well as successful checks. Every status must also have
plain text: a green connection dot must not imply a verified connection unless one
was actually checked. Distinguish a model decline, a read-only guard refusal, an
unsupported-type refusal, an empty result, and a failed query.

## 4. Typography

**Choose IBM Plex Sans for the interface and IBM Plex Mono for code.** This retains
the approved technical character while avoiding an interface made entirely of code-like
text. Do not introduce a third display family.

| Role | Family / weight | Desktop target | Narrow target |
| --- | --- | --- | --- |
| Page heading | Plex Sans 600 | 30–32 px | 24 px |
| Answer heading | Plex Sans 600 | 23–24 px | 20–22 px |
| Section heading | Plex Sans 600 | 16–18 px | 16–18 px |
| Body / input | Plex Sans 400 | 16 px | 16 px |
| Labels / metadata | Plex Sans 400–500 | 13–14 px | 13–14 px |
| Chart labels | Plex Sans 400–500 | 12–14 px | 12–14 px |
| SQL / schema identifiers | Plex Mono 400–500 | 13 px | 12–13 px |

Use approximately 1.5 line height for prose, 1.25 for headings, and tabular numerals
for numeric comparisons. SQL may scroll inside its own panel; the page must not scroll
horizontally. Keep the input at 16 px on narrow screens.

FarmLens serves its fonts locally. Adopt that approach with licensed font assets and
their license notices in a later implementation pass; the current Google Fonts import
depends on network availability. Until then, test the system sans-serif and monospace
fallbacks and wait for fonts to settle before taking screenshots.

## 5. Composition and density

1. **Separate the surfaces.** The current capture's answer and explanation panels
   nearly merge with the canvas. Make white panel backgrounds explicit; use a quiet
   border and consistent 20–24 px padding. Avoid adding heavy shadows everywhere.
2. **Shorten the answer headline.** Prefer “Electronics leads with 173,366” and put
   the measure and optional comparison below it. Only sum other rows when the result's
   meaning supports that comparison; a two-column shape alone does not establish
   that percentages or averages can be added. Preserve exact numbers and units in
   the table; do not infer currency from a revenue alias.
3. **Make the chart readable.** Increase label size, support negative and zero values,
   and bound the visible chart to a documented category limit (proposed: 12). If a
   chart shows fewer rows, say so and preserve the complete returned table and CSV.
   Do not silently reorder or aggregate the result to make it look better.
4. **Reduce narrow-screen preamble.** The current 390 px capture spends most of the
   first screen on the header, subtitle, three long example questions and a note.
   Use short example labels such as “Revenue by category”, retaining the full question
   as the submitted prompt. After an answer, collapse secondary introductory content
   while keeping the composer accessible. Show the result before its explanation.
5. **Keep the evidence legible.** Preserve the SQL and actual check/run outcome.
   Show a short selection summary, used-table chips and an explicit “All selected
   tables” disclosure when the chip list grows. Keep full schema and retrieval details
   available. Never describe an inferred display summary as a complete agent trace.

Use an 8 px spacing rhythm, with 4 px for small internal gaps, 16–24 px inside cards,
and 24–32 px between major groups. Use 8–12 px corner radii; reserve pills for compact
choices and status chips. These are implementation targets, not measurements of the
current page.

## 6. Implementation order and acceptance

First fix the review findings recorded in the [agent log](../6_agent_log.md): signed
chart domains, schema-qualified used-table identity, and unsupported-type refusal copy.
Also repair the screenshot script's formatting drift. Then apply the surface, type,
headline and narrow-screen refinements as one bounded visual pass.

Check desktop at 1440 × 1000 and narrow at 390 × 844. Include success, negative values,
zero/null values, empty results, long table names, many categories, refused queries,
unsupported types and provider failures. Test keyboard navigation, visible focus,
readable fallback fonts and horizontal overflow in the rendered application.

Retake real README captures after the final UI changes. The hero should include the
question, answer, chart and enough SQL/check context to explain the project; use a
separate detail image for long tables. Keep refusal and narrow captures as supporting
evidence. Record commit, dirty state, engine, provider/model, question and viewport.
If a composed portfolio cover is added, label it as a composition, separate from the
real application captures.

This visual milestone does not complete Phase 4's retrieval work or Phase 5's agent
loop. See [next steps](../4_next_steps.md) for the backend roadmap.

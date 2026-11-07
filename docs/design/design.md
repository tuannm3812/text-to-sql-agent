# UI design direction

## 1. Purpose and status

2026-10-21: a local portfolio interface for asking questions, inspecting generated
SQL, and understanding the evidence behind the result. The answer should be the first
thing a reviewer notices after submitting a question.

2026-11-05: the owner approved extending the poster/deck blue-and-amber palette
into the Streamlit app. The palette below supersedes the earlier teal direction;
IBM Plex typography, layout and behaviour remain unchanged. The historical
[mockup](index.html) is not the current palette authority.

Reference captures: [desktop answer](../screenshots/01-answer.png),
[narrow answer](../screenshots/04-narrow.png), and their
[capture provenance](../screenshots/capture.json). These are real local-model captures from 5 November 2026 on a dirty tree based on
`449bbf5`; capture.json records source hashes. The mockup is historical.

## 2. What to take from FarmLens

FarmLens's `web/style.css` and `docs/screenshots/showcase-explorer.png` show a coherent
system: locally served Inter and Manrope, cream surroundings, white cards, restrained
green and yellow accents, and clear groups of related information. Its map and land
imagery also provide visual interest that a SQL workspace naturally lacks.

Transfer the consistency, card hierarchy, readable labels, and purposeful whitespace.
Here the data chart and inspectable SQL provide the visual focus. Use the approved blue/amber identity consistently. Colour changes alone do not
resolve density and hierarchy; retain the existing answer-first composition.

## 3. Color palette

Approved light palette, implemented in `.streamlit/config.toml`, `ui/styles.py`
and `ui/results.py`. Keep these theme, CSS and chart values aligned.

| Role | Color | Use |
| --- | --- | --- |
| Canvas | `#FAF7F0` | Cream page background |
| Surface | `#FFFFFF` | Answer and explanation cards |
| Ink | `#17243B` | Navy headings, body and chart values |
| Muted | `#59636E` | Supporting copy and metadata |
| Divider | `#E6E9ED` | Decorative separators |
| Panel border | `#C5CBD4` | Card outlines |
| Primary | `#0F4BEB` | Actions, active navigation, leading chart bar |
| Primary tint | `#EEF3FF` | Selected table chips |
| Comparison / accent | `#E6A23C` | Other chart bars and numbered steps |
| Well | `#F5EEE2` | Code, table and neutral chip backgrounds |
| Warning / background | `#8A5A00` / `#FFF4D6` | Explicit refusals and limitations |
| Failure / background | `#B42318` / `#FFF0EE` | Failures |
| Focus | `#0F4BEB` | Keyboard focus outline |

Use navy text on amber step circles, never white or amber small text on white.
Amber is a comparison/navigation accent, not a claim of success or a warning by
itself. Retain explicit check, refusal and error labels. Chart values stay dark and
directly labelled; colour never replaces a number or status description. The pale
divider is decorative, not a standalone control boundary.

The palette matches the approved poster and deck, while the app keeps IBM Plex Sans
and Mono. Do not recolour historical screenshots or the older HTML mockup to imply
they were freshly captured. [Current component preview](palette-preview/answer-fixture.png)
uses fixed, labelled fixtures rendered by the real application components; it is not
a new model answer or benchmark result. Existing README captures retain their provenance.

### SQL syntax colours (6 November 2026)

Generated and blocked queries in **Wrote SQL** use the same palette as the interface.
SQL has no universal mandatory colour scheme; this is the project's display contract.

| SQL role | Colour | Contrast on code well `#F5EEE2` |
| --- | --- | --- |
| Keywords (`SELECT`, `FROM`, `GROUP BY`) | Blue `#0F4BEB`, weight 600 | 5.64:1 |
| Functions and literal values | Dark amber `#8A5A00` | 5.14:1 |
| Identifiers, punctuation and operators | Navy `#17243B` | 13.47:1 |
| Comments | Muted `#59636E` | 5.30:1 |

All exceed the 4.5:1 normal-text contrast target. Bright amber `#E6A23C` remains
an accent for charts and step circles, never small SQL text. Dark amber in code
indicates syntax, not a warning; execution status retains its explicit label.
Use IBM Plex Mono at 12.5 px with 1.55 line height and wrapping on narrow screens.
Preserve source spelling, quotes and whitespace; do not reformat or rewrite a query
for presentation. Highlighting does not establish validity or safety. Un-tokenizable
SQL falls back to escaped plain text. The full-schema expander retains Streamlit's
native code viewer and copy control; this custom palette applies to the query trace.

[Desktop SQL preview](palette-preview/sql-highlight-desktop.png) and
[mobile SQL preview](palette-preview/sql-highlight-mobile.png) render the real UI
with labelled fixed fixtures, not new model results. README and Slides screenshots
remain their previous dated captures; refresh from the running app when replacing them.

## 4. Typography

**Required: IBM Plex Sans for interface text and IBM Plex Mono for code.** This retains
the approved technical character while avoiding an interface made entirely of code-like
text. Do not introduce a third display family.

| Role | Family / weight | Desktop target | Narrow target |
| --- | --- | --- | --- |
| Page heading | Plex Sans 600 | 31 px | 24 px |
| Answer heading | Plex Sans 600 | 24 px | 21 px |
| Section heading | Plex Sans 600 | 16 px | 16 px |
| Body / input | Plex Sans 400 | 16 px | 16 px |
| Labels / metadata | Plex Sans 400–500 | 13–14 px | 13–14 px |
| Chart labels | Plex Sans 400–500 | 12–14 px | 12–14 px |
| SQL / schema identifiers | Plex Mono 400–500 | 13 px | 12–13 px |

Use approximately 1.5 line height for prose, 1.25 for headings, and tabular numerals
for numeric comparisons. SQL may scroll inside its own panel; the page must not scroll
horizontally. Keep the input at 16 px on narrow screens.

FarmLens serves its fonts locally, and so does this app since 2026-10-22: the Latin-1
WOFF2 files for Plex Sans 400/500/600/700 and Plex Mono 400/500 from IBM's release are in
`static/fonts/` with the OFL-1.1 text, served by Streamlit's static serving. With them
blocked, the stack falls back to the system sans and monospace
(`scripts/ui_acceptance.py`).

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


## 7. Strict font and responsive contract — 5 November 2026

Use only locally served IBM Plex Sans 400/500/600/700 and Plex Mono 400/500.
System sans/monospace are loading-failure fallbacks; Material Symbols remain the
framework icon font. Native canvas widgets may retain framework-rendered text;
CSS inspection alone does not prove their font. Charts explicitly use Plex Sans.
Do not import the deck's Google Sans or the poster's DM Sans into the application.

Required sizes: brand 17 px/700; hero 31 px/600 desktop, 24 px mobile; answer heading
24 px/600 desktop, 21 px mobile; explanation heading 16 px/600; step headings
14 px/600; supporting prose and notes 14 px/400; provider metadata and disclosures
13 px/400; chart labels 13 px; SQL and table identifiers 12.5 px Plex Mono.
Body and phone input stay at 16 px; desktop input is 17 px. Use 1.5 prose line height,
1.2–1.25 for headings, and tabular numerals for facts. Reserve 700 for brand/strong
emphasis. Do not shrink text to conceal overflow. Scope small-text rules under .stApp
to beat Streamlit defaults and verify computed styles after framework upgrades.

Layout: maximum container 1240 px; 40 px desktop gutters, 16 px at <=700 px.
White cards use 20 × 24 px desktop padding, 16 px mobile padding and 12 px radii.
Mobile header has brand/Change on its first row, navigation/database on the second,
with a 16 px lower gap. Answer precedes explanation in a single column. Long schema
names wrap, SQL scrolls within its panel, and content cards never have fixed heights.
The decorative header rule stays within left/right 0; +/-100vmax caused horizontal
scrolling even though document scrollWidth incorrectly suggested no overflow.

Acceptance: verify actual innerWidth, document width AND stMain scrollWidth versus
clientWidth. Checked real answer/refusal at 390 × 844, long-label fixture at 390 px,
signed values at 360 × 800, and desktop at 1440 × 1000. All checked main containers
have zero horizontal overflow. Preserve exact values in tables/tooltips when chart
labels shorten. README captures must use real model answers; fixture previews stay
labelled. This is presentation evidence, not a benchmark or full accessibility audit.

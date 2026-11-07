# Showcase design

**Current poster, 7 November 2026:** rebuilt from the deck by `build_poster.py` and imported to the
live poster. Six sections, each headed by its finding: problem, demo, how it works, safety and
data, evidence, lessons. Palette and type follow [the slide standard](slides/DESIGN.md); amber is
not used as text on blue or navy. Footer: code and demo links left, date and UTS logo right, all
centred on the band. The notes below record the earlier portrait poster and are history.

Status: portrait direction approved by the owner on 5 November 2026 and implemented.
This file is the poster standard; [slide-deck standards](slides/DESIGN.md) are separate.

## Editable poster authority

[Open the native Google Slides poster](https://docs.google.com/presentation/d/1yxVBZCk7Zh2Udt_QASjhZaXw7yb2Thw1TbFnN3KOYAg/edit). Created 5 November 2026 as one portrait
900 × 1275 pt slide. The live poster is now the formatting source of truth: read its current
objects before editing and preserve owner adjustments. Local HTML/PNG/PDF are the approved
pre-conversion source, not an automatic overwrite mechanism. The editable PowerPoint is an
import seed; the Google-rendered PDF records the conversion handoff. Text, bars, rules and
backgrounds are native objects; the authentic app screenshot remains an image. Conversion
has small weight/spacing differences. The 5 November layout review removed imported shadows
through Google Slides' Format options and right-aligned the three chart percentages. Keep
panels, rules and chart marks flat; retain a clear gap between bars and numeric labels.

## Local references and scope

Read Project 15's local
[DESIGN.md](../../../project-15-strategy/deliverables/portfolio-showcase/DESIGN.md),
[poster brief](../../../project-15-strategy/deliverables/portfolio-showcase/briefs/07-poster.md)
and [showcase README](../../../project-15-strategy/deliverables/portfolio-showcase/README.md).
Its current Google Sans rules govern its native slide deck; its poster brief separately uses
DM Sans, blue/teal, and a 60-second evidence story. Borrow the reusable principles, not its
client branding, institutional logos, conclusions or landscape dimensions.

This file governs showcase artifacts only. The application's teal/IBM Plex identity remains
in [the app design standard](../design/design.md). The live Google deck remains its own
formatting source of truth, as documented in [the handoff](README.md).

## Intent and approach

Make the portfolio poster understandable in a brief scan: what the agent does, how it is
constrained, what was measured, and what the results imply. Preserve the authentic app
screenshot and the reviewed evidence. A stronger visual hierarchy is the change; no new
model measurements or capability claims are needed.

Approaches considered:

- **Approved: portrait evidence story.** Preserve the existing 1200 × 1700 logical canvas
  and HTML/PDF/PNG workflow, with Project 15's white, blue and teal design language. This
  fits portfolio viewing and gives one main finding more space.
- **Five-column landscape poster.** Closest to Project 15's A0 event poster, but substantially
  smaller text when viewed in a portfolio. Reserve for a specified physical showcase format.
- **Cosmetic refresh only.** Changing colours and corner radii would preserve all density
  problems; it does not give visitors a clear reading order.

The owner approved the portrait approach and requested implementation.

## Reading order

1. **Problem, application and product.** A compact header, then “Ask in English. Inspect the SQL.” beside
   the authentic answer screenshot. Explain read-only execution and inspection in a short
   supporting paragraph. Introduce the illustrative retail use case and label business impact
   as unmeasured. Keep the screenshot's aspect ratio and source typography.
2. **How it works.** A slim, numbered five-step flow: schema → select → generate → validate
   and execute → inspect. Keep engine-enforced read-only access and the application gate
   explicit. Reduce repeated prose, not the safety qualification.
3. **Main evidence.** Give the large-schema comparison the largest chart area: 25.5%, 26.8%,
   29.1%, with a zero-based common scale, direct labels, 1,222 questions and 21–65 tables.
   Place +3.6 points [+1.4, +5.8], its full-DDL-plus-hints baseline, 69% fewer prompt tokens,
   and the roughly 2-second latency cost together. Keep the benchmark date/model scope.
4. **Context and lessons.** A smaller standard-benchmark strip retains Spider/BIRD figures,
   populations and the non-leaderboard-comparable qualifier. Compact trial outcomes retain
   named baselines, intervals, off/opt-in status and the cross-commit limitation. Distinguish
   retrieval quality from answer accuracy. Do not make interval-crossing-zero claims of
   equivalence.
5. **Close.** Three brief implications and a quiet footer linking the existing demo/code.
   Keep detailed provenance in source documentation without dropping material limitations.

## Typography and visual rules

- White canvas; charcoal `#20242C` text; secondary grey `#59636E`; primary blue `#0F4BEB`;
  teal `#21918C`; quiet borders `#E6E9ED`; pale blue `#EEF3FF` and teal `#EAF6F3` fills.
- Use DM Sans for the poster, following Project 15's poster-specific brief. Bundle or reuse
  licensed local font assets before rendering; verify the actual loaded font. Use Google
  Sans for the native deck. Authentic application screenshots keep IBM Plex.
- At the 1200-pixel logical width: headline 48 px, main evidence title 25 px, hero body 17 px,
  chart labels 16 px, supporting narrative and scope detail 13 px. Section navigation
  is 13 px uppercase; table headers and footer are 12 px. Adjust spacing or shorten prose
  before shrinking type. Exact sizes are subject to rendered fit.
- Use alignment and whitespace for grouping. Reduce nested rounded cards, pill badges and
  shadows. Keep consistent margins and a clear main evidence region.
- Colour identifies a series or role, not an unsupported success judgment. Direct labels
  remain sufficient without colour. Never use a nonzero baseline for bars.
- A portrait portfolio PDF is not an A0 print specification. Obtain physical dimensions
  before producing a print edition.

## Implementation and acceptance

For the native poster, edit Google Slides in place and export its PDF; do not reimport
the historical HTML/PowerPoint seed over owner changes. Inspect the whole poster plus
full-size crops of the screenshot, charts and dense text. Check all content fits within
the page, fonts load, image proportions survive, and PDF text remains selectable. Compare
every retained numeric claim, baseline and limitation with the reviewed poster/README.
Keep the deck and poster aligned in claims when both are requested; edit each native artifact separately. Record concrete changes, checks and remaining concerns
in `docs/6_agent_log.md`; ask Claude to review hierarchy, claim preservation and export fit.


## Poster navigation and deck alignment

A one-page poster needs no separate agenda or table of contents. Use four numbered
sections: Problem and application; How an answer is produced; Measured evidence and its
limits; Lessons and next tests. The hero and screenshot establish use before technical
steps. Match the deck's blue/amber palette, evidence discipline and plain language, while
retaining the approved poster DM Sans typography and portrait composition.

Keep bounded value hints explicitly row-derived and result rows local. Describe validation
and engine restrictions as tested protection layers. Report selection gains within the
measured databases; avoid “only at scale” as a universal rule. Recovery and hosted-model
work remain proposed tests. The shared-summary trial appends columns/joins for selected
tables, not every table. Retain the paired baseline, uncertainty, latency tradeoff and
cross-commit limitation. Label illustrative use and unmeasured business impact clearly.

## Safety scope — 5 November 2026

Keep the subset and overall result adjacent: 6/6 data-change requests refused; overall
safety accuracy 11/15 (73.3%), 95% CI [53.3, 93.3], on the small 15-case suite. The overall
result includes refusal/unanswerable classification, not just write prevention. Preserve
the distinct 45 passed / 0 skipped engine-conformance claim. None proves universal safety.
The overall qualification uses native DM Sans 9.75 pt text in the right side of the
safety strip, above the trial table; do not remove it to simplify the poster.

## Approved blue and warm amber palette — 5 November 2026

The owner approved palette option 2 after the poster trial and extended it to the
slide deck. This is the shared showcase palette.
Keep primary blue `#0F4BEB`; use amber `#E6A23C` for comparison bars and lesson accents,
cream `#FAF7F0` for panels, navy `#17243B` for principal text, and white for the page.
Status chips use warm neutral `#F5EEE2`; caption gray and subtle rules remain unchanged.
Amber denotes a comparison, not a warning or a safety judgment. Retain direct labels.
Do not use light amber for small text. Preserve the authentic app screenshot's colours.
Typography, composition, numerical claims and safety qualifications remain unchanged.
The deck uses the same palette; the application now shares these colours. Prior
exports and native colour rollback requests are saved in `palette-trials/`.


## Current UI captures — 5 November 2026

Native screenshot objects now use the current blue-and-amber README captures from
`docs/screenshots/01-answer.png` and (deck only) `02-how-it-was-answered.png`.
Their capture.json identifies the real local Ollama response and dirty source tree.
Preserve intrinsic 1440:1000 proportions with fit-inside placement, never stretch.
Existing screenshot frame geometry, caption anchors, native type and master marks
remain authoritative. These are product-demo illustrations, not benchmark evidence.

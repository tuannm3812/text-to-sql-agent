# Slide deck design standard

Status: current living standard, reconciled with Project 15 on 6 November 2026.

## Authority and maintenance

The [native deck](https://docs.google.com/presentation/d/1SeYPeuPEcVqbDjtHdlR_SI9SbVt-82hCeHe5eEaDRow/edit)
is the source of truth. Preserve owner changes; never reimport the historical builder.
The reference is Project 15's current `deliverables/portfolio-showcase/DESIGN.md`
and native page p3, object s4_takeaways_unified, inspected on 6 November.
The older oral-presentation standard is a different artifact and is not authoritative.
Update rules here in place; record superseded choices in [design history](design-history.md).
Record verification and handoffs in ../../6_agent_log.md. The poster and app have separate standards.

## Audience, story and language

This is a reader-oriented portfolio deck. Separate capability, evidence, interpretation
and proposed work. Use sentence case for titles and prose, uppercase for navigation labels.
Use short subject titles for context/methods and supported findings for results.
Keep one scope subtitle; avoid repeating the title. Prefer sentences, spacing and line
breaks over decorative middle dots, bullets used as separators, or vertical bars.
Native bullets remain appropriate for real lists. Use digits with units and populations.

Keep the approved problem-first order in [BRIEF.md](BRIEF.md): cover, summary, agenda, then
Problem, Solution, Evidence and Next steps. Labels use those section names, matching
the agenda. Project 15's client sequence does not override this portfolio narrative.
Match slides by native ID.
Each slide needs a reader question, main message, evidence and clear ownership of
what belongs elsewhere. Summary repetition is synthesis; avoid repeating detailed diagrams.

## Theme and grid

White 960 × 540 pt canvas. Retain blue #0F4BEB, amber #E6A23C, cream #FAF7F0,
navy #17243B, grey #59636E and slate #46576C. Blue identifies primary evidence;
amber identifies comparisons/callouts, not success or warning. Always include labels.
Retain the owner's UTS master, dotted motif, short accent and edge-reaching footer.
Exactly one inherited automatic page number per numbered slide; cover unnumbered.
Do not copy Project 15's client logos, teal categories, findings or artwork-removal rule.

| Element | Position / size | Type |
|---|---|---|
| Section label | x43.5/y29.5 | Google Sans 10 pt bold; section navy, separator and sublabel #999999 |
| Title | x43.5/y48.413 | 24 pt bold blue |
| Subtitle | x43.5/y90.921 | 12 pt grey |
| Outer content rail | x43.5/y130 | Preserve internal plot/table insets |
| Takeaway text area | x684/y136; 235 × 324 pt | 12 pt, 110% line spacing |

The label remains below the native master accent, unlike Project 15's y21.744.
The owner-approved y130/y136 body rails supersede Project 15's y156 takeaway start.
Cover and close have separate compositions. Do not force unlike chart glyphs onto
one baseline; align content frames. Maintain visual clearance from the footer.

## Content levels

Design each slide in this order: decide the one point the reader should take first,
choose the layout that shows it, then add the figure, chart, icon or logo that proves it.

| Level | Use | Size and weight | Position |
|---|---|---|---|
| 1 | Slide title | 24 pt bold blue | x43.5/y48.4, one line where possible |
| 2 | Scope subtitle | 12 pt grey | x43.5/y90.9 |
| 3 | Key figure, special case | 26 to 28 pt bold; up to 40 pt when it is the slide's main point | Inside its card or above its label |
| 4 | Section, block and card heading | 12 pt bold | Top of the content group |
| 5 | Body in a figure, block, card or table; chart labels | 10 pt | Content rail x43.5–650, or full width to x919 without a takeaway column |
| 6 | Takeaway heading and text | 12 pt; heading bold | x684/y136, 235 pt wide |
| 7 | Figure caption and note | 8 pt grey, bold "Figure N." or "Note:" | Below the evidence, ending by y470 |

Content text has three levels: 12, 10 and 8 pt. Nothing in a figure or block is larger than 12 pt
except a special case: a key figure, or the agenda's four section names at 16 pt.

Balance the palette: navy, blue and amber share the emphasis, cream and pale tints carry cards, and
slate carries neutral comparison bars. No slide relies on blue alone. Every note starts with a bold "Note:" or "Scope:". Content stops by y476, 16 pt above the
footer. All icons in the deck come from one set, Material Symbols Rounded (assets/icons,
build_icons.py), 24 pt, or 32 pt in large diagrams; blue or navy on light fills, white on dark. Logos identify a named product only, keep their own colours and proportions,
sit at 32 pt inside cards, and are never recoloured. Slides with evidence use a takeaway
column unless the figure needs the full width.

## Typography and editable components

Use Google Sans for editable prose. Google Sans Code is the reference for new code
spans; genuine app screenshots retain IBM Plex and authentic syntax colouring.
Use the three content levels above. Section labels: 10 pt. Never use caption sizes for conclusions.

Keep headings and explanations in one rich-text component. Use native shapes, bars,
connectors and tables; do not rasterise panels or split wrapped words into boxes.
Narrative cards use about 8 pt padding; larger cards may use 12 pt. Zero padding is
specific to takeaway templates, markers and aligned free labels, not every shape.
Verify actual insets in Slides Text fitting; paragraph indents are not internal padding.
When the API cannot set insets, document a compensating frame and verify its rendered
text bounds instead of claiming zero padding. The summary box uses x676.8/y128.8,
249.4 × 338.4 pt to compensate for native 7.2 pt insets and align to the text area.
Enlarge shapes or tighten flexible wording before reducing type.

## Takeaways and markers

Use a column only when it adds an implication, limitation, decision criterion or next
test. No generic KEY TAKEAWAYS or KEY IMPLICATIONS label. Use descriptive headings.
There is no fixed point count. Keep one unified editable column, headings and body
12 pt, 110% line spacing, 6 pt after paragraphs, 14 pt before later headings, and
zero paragraph indents for prose. Use selective bold/blue evidence-bearing phrases.

A thin grey line at x658, from y130 to y476, separates the content from the takeaway column on
every slide that has one. Dense comparison tables may use 10 pt body text. The agenda uses numbered
circles (01 to 04), grey #59636E questions, and a contents list under each part: section name,
thin rule, and a linked 24 x 18 pt page chip in the part's colour.

Every slide with a takeaway column uses the same markers, following Project 15: red #C64040
12 pt native ellipses with centred 8 pt bold white numbers, at x668 beside each heading's
first rendered line, and repeated beside the evidence each point refers to. This supersedes
the earlier amber markers; slides 7 onward change in their content pass.
Do not add unpaired decorative numbers. Keep marker colour independent of outcomes.
Use small slate superscripts for specific figure qualifications, with matching notes;
otherwise use a bold Note: or Scope: prefix, not orphan reference numbers.

## Charts, figures and evidence

Bars start at zero; direct labels, common comparison scales and flat native lines.
No bevels, shadows, 3D charts or decorative charts. Keep measured units, baseline,
population, intervals and material limitations beside claims. Put provenance in notes.
Distinguish percentage points from relative percentages and evidence hints from value
hints. Historical runs are not current-code claims. Read-only execution is not analytical
correctness; result rows not sent to the model does not make prompts metadata-only.
Cross-commit pairs are not controlled merely because questions match. Do not infer
speed from token savings, or business impact from benchmark scores.

Place each figure caption 8 pt below its own figure, aligned left; 9 pt grey, only
Figure N. bold. Different-height figures do not require a common caption baseline.
Screenshots retain intrinsic proportions and provenance; never recolour raster SQL.

## Approved compositions

- Cover: retain the wordless illustration (cover-art.png, build_cover_art.py) in the
  rounded frame bleeding off the right and bottom edges, the UTS corner mark, and subject
  36121 — Artificial Intelligence Principles and Applications. Title: Ask your data.
  Inspect the answer. Subtitle: An inspectable text-to-SQL agent for read-only analytics.
- Demo p11: real 6 November capture in captures/2026-11-06-retail-syntax.png and JSON.
  Source 1440 × 1000; answer crop x134/y356/w690/h644; SQL crop x880/y640/w390/h330.
  Both display 300 pt wide at y130, x43.5/x353.5. Captions at y418/y391.846.
  Preserve the red review markers and selective emphasis; source captures remain authentic.
- Agenda: four columns at x43.5/267.5/491.5/715.5, 200 pt wide. Blue 46 pt numbers
  y130, grey rail y207, amber dots y202.5; heading groups y228 with padding compensation.
  Headings 22 pt, questions 13 pt, descriptions 12 pt. Clickable page ranges at y413:
  4–6 to p2; 7–9 to p3; 10–14 to p6; 15–16 to p12. This is navigation, not data flow.
- Executive summary p2: historical headline scores, paired mini charts and unified
  takeaway column. Accuracy bars 25.5/29.1 use 140 pt = 35%; token index 100/31 uses
  105 pt = 100. Index is derived from rounded 69% savings. Retain +3.6 points and
  paired 95% interval [+1.4,+5.8]. Scope: 1,222 questions, 4 databases, 21–65 tables,
  full DDL plus hints baseline, 19 October 2026. No decorative separators or generic label.
- Landscape: three comparable columns; retail application: question then ask/inspect/decide.
  Preserve variation appropriate to each slide's purpose.

## Speaker notes

All 16 slides follow the Project 15 spoken-note pattern: short purpose opening;
natural explanation in visual reading order; separate [Point: visible label] cues;
limitations alongside claims; useful transition. Do not read every chart value or
put editorial instructions in the spoken script. Put exact sources and image credits
under Reference — not read aloud after the script. Keep ../speaker-notes.md synced.

Google Sans 14 pt charcoal #202124 spoken text; 115% line spacing; 8 pt after paragraphs.
Opening: bold #174EA6 on #E8F0FE. Point cues: 11 pt italic #5F6368 on #F1F3F4.
References: 11 pt grey with a bold reference heading. Highlight selectively; no fixed
speech duration or bullet count. These styles are separate from slide-face typography.

## Verification and handoff

Read the latest live objects before edits. Review content, evidence scope, position,
type roles, padding, markers, note references, links and one automatic page number.
Inspect the live view and exported PDF. Refresh previews and Google-rendered PDF;
record concrete checks and remaining limitations in the agent log. Do not claim a
Claude response when recording a handoff. Do not commit, push or share without instruction.

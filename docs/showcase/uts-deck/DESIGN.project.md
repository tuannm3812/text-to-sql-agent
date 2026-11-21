# Consumer design and provenance

Audience and presentation setting: 36121 Artificial Intelligence Principles and Applications capstone showcase, and the portfolio. Presented on screen; delivered as PDF and HTML.

Purpose and reader question: can a person ask a database a plain question and trust what comes back, and where does it still fail?

Evidence cutoff and source project commit: repository `main` at 38dd2df (7 November 2026). Numbers trace to claims-register.md. Recall and retrieval gains are never presented as accuracy gains.

Kit version and exact commit: see kit-pin.json (UTS deck kit v0.6.0). Shared engine: deck-kit 96bf255.

Relation to the Google Slides deck: the live Google deck stays the presenting copy until this port is approved. Wording and notes come from it and from `docs/showcase/speaker-notes.md`; this port re-lays them on the kit.

Local token/layout overrides and reasons: footer names the project and subject. `project_layouts.py` adds `hard_page` (why it is hard), `aim_page` (the setup-against-meaning matrix with logos), `tools_page` (logos and effort dots), `demo_page`, `boundary_page`, `arch_page` (eight steps, engine band, logos), `stack_page`, `close_page` and `bars_page` (bar and interval panels; value labels that nearly align are snapped into one column); kit `table_page` draws the tables; helpers are copied from the fire-occurrence UTS consumer so markers, legends and the right column behave the same.

Figure palette: Viridis, one meaning per colour, used the same way on every figure and the illustration, so no legend is needed where rows are labelled (19 November 2026, owner's request):
- teal #21918C: this project: its measured result, its default setting, what it sends to the model, tables the agent chose.
- indigo #3B528B: published or reference results and benchmark data: other papers, the benchmark's own answer, schema tables in the art.
- green #5EC962: gained or added: answers won, foreign-key tables added, SQL lines a better question adds.
- purple #440154: lost, dropped or not stopped.
- yellow #FDE725 (pale #FDF3A6 as a fill): the model and the gaps: the one model step, a gap still to close.
- grey #ADB5BD: baseline or comparison arm, not sent, behaviour-only suites.
- Difficulty runs green to purple: easy #5EC962, medium #21918C, hard #3B528B, extra hard #440154.
- Icons that only label structure are ink #1B2430; chapter accents (slate, blue, plum, ochre) stay structure only. Text never sits in amber or yellow on navy.
- Percentages are shown with one decimal and a space before %, as in the README; bar scales are linear, one per panel.

Glossary (names and colours used across slides):
- Chapters: Summary blue, Problem slate, Solution blue, Evidence plum, Next steps ochre. Chapter colour is structure only.
- "Top 6": the six most relevant tables plus neighbours sent to the model. "Every table + hints": the full schema with value hints.
- "Our scorer": this project's typed result comparison, not leaderboard scoring.

Notes follow the kit (DESIGN.md, v0.6.0): **Note:** ¹ with a matching superscript on the figure or header text; red markers stay separate and carry a white ring. Ticks are green and crosses red everywhere (assets/project/icons). Architecture: slide 9 is a four-stage summary; the full eight-step flow is the appendix page, full width with no takeaway column; box rules mean ink = app step with no model, yellow = the model, teal = enforced in code, shown in a legend above each diagram.

Flowchart (appendix page 20, make_flow.py): its own smaller type, off the slide scale (owner, 21 November 2026). Block colour rules: lane tint and header = the stage; step = white card with its lane's border (Prepare ink, Check and run teal, Answer green); the one model call = the only solid yellow card; decision = white pill with its lane's border; end state = green (answer) or red (refused, stopped) tinted card; note = white, no border, grey text. Steps run top to bottom inside lanes on a shared row grid; lanes run left to right; a guarantee band runs across the bottom.

Icons and logos: `assets/icons/` are the old deck's Material icons recoloured to palette A (blue, ink, ochre, plum, white, red); `assets/logos/` are the old deck's product logos with white made transparent, kept in their own colours. Safety ticks are `assets/project/icons/yes.svg` and `no.svg`. Code panels show added lines in Viridis green, never amber on navy. The close has no team credit (owner's decision, 7 November 2026).

Asset origins, licences: `assets/figures/cover-art.png` and `cover-art-close.png` drawn by `make_cover.py` (decorative, no real data), recoloured from `docs/showcase/slides/build_cover_art.py`.

UTS identity use: identity uts (UTS subject deliverable).

Slide content: `author_slides.py` writes slides 2 and 4 to 19 into brief-content.json from the live deck's bodies and notes; edit it and rerun rather than editing the JSON by hand.

Final output checks and unperformed checks: 24 pages; all five kit checks report 0 findings (21 November 2026). See QA.md for the review record and limitations.
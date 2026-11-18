# Consumer design and provenance

Audience and presentation setting: 36121 Artificial Intelligence Principles and Applications capstone showcase, and the portfolio. Presented on screen; delivered as PDF and HTML.

Purpose and reader question: can a person ask a database a plain question and trust what comes back, and where does it still fail?

Evidence cutoff and source project commit: repository `main` at 38dd2df (7 November 2026). Numbers trace to claims-register.md. Recall and retrieval gains are never presented as accuracy gains.

Kit version and exact commit: see kit-pin.json (UTS deck kit v0.6.0). Shared engine: deck-kit 96bf255.

Relation to the Google Slides deck: the live Google deck stays the presenting copy until this port is approved. Wording and notes come from it and from `docs/showcase/speaker-notes.md`; this port re-lays them on the kit.

Local token/layout overrides and reasons: footer names the project and subject. `project_layouts.py` adds `hard_page` (why it is hard), `aim_page` (the setup-against-meaning matrix with logos), `tools_page` (logos and effort dots), `demo_page`, `boundary_page`, `arch_page` (eight steps, engine band, logos), `stack_page`, `close_page` and `bars_page` (bar and interval panels; value labels that nearly align are snapped into one column); kit `table_page` draws the tables; helpers are copied from the fire-occurrence UTS consumer so markers, legends and the right column behave the same.

Figure palette, category mappings, units and scale choices:
- Data bars: Viridis blue #31688E for the main series; grey #A9B4BF for a reference or baseline arm; Viridis green #35B779 for gains or added tables; Viridis purple #440154 for losses. A gap to a reference is the blue tint #D6E1EC with its label in #31688E.
- Percentages are shown with one decimal and a space before %, as in the README.
- Bar scale: 0–100 %, linear, one shared scale per chart.

Glossary (names and colours used across slides):
- Chapters: Summary blue, Problem slate, Solution blue, Evidence plum, Next steps ochre. Chapter colour is structure only.
- "Top 6": the six most relevant tables plus neighbours sent to the model. "Every table + hints": the full schema with value hints.
- "Our scorer": this project's typed result comparison, not leaderboard scoring.

Icons and logos: `assets/icons/` are the old deck's Material icons recoloured to palette A (blue, ink, ochre, plum, white, red); `assets/logos/` are the old deck's product logos with white made transparent, kept in their own colours. Safety ticks are `assets/project/icons/yes.svg` and `no.svg`. Code panels use pale blue #9CC3E0 for added lines, never amber on navy. The close has no team credit (owner's decision, 7 November 2026).

Asset origins, licences: `assets/figures/cover-art.png` and `cover-art-close.png` drawn by `make_cover.py` (decorative, no real data), recoloured from `docs/showcase/slides/build_cover_art.py`.

UTS identity use: identity uts (UTS subject deliverable).

Slide content: `author_slides.py` writes slides 2 and 4 to 19 into brief-content.json from the live deck's bodies and notes; edit it and rerun rather than editing the JSON by hand.

Final output checks and unperformed checks: 23 pages build (19 plus four appendix slides: scoring, read-only per engine, technology, glossary); check_deck, audit_layout and check_markers report 0 findings (18 November 2026). Not yet done: the owner's page-by-page review; the demo GIF is a still screenshot.
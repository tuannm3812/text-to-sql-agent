# Consumer design and provenance

Audience and presentation setting: 36121 Artificial Intelligence Principles and Applications capstone showcase, and the portfolio. Presented on screen; delivered as PDF and HTML.

Purpose and reader question: can a person ask a database a plain question and trust what comes back, and where does it still fail?

Evidence cutoff and source project commit: repository `main` at 38dd2df (7 November 2026). Numbers trace to claims-register.md. Recall and retrieval gains are never presented as accuracy gains.

Kit version and exact commit: see kit-pin.json (UTS deck kit v0.6.0). Shared engine: deck-kit 96bf255.

Relation to the Google Slides deck: the live Google deck stays the presenting copy until this port is approved. Wording and notes come from it and from `docs/showcase/speaker-notes.md`; this port re-lays them on the kit.

Local token/layout overrides and reasons: footer names the project and subject. `project_layouts.py` adds `hard_page` (why it is hard); helpers are copied from the fire-occurrence UTS consumer so markers, legends and the right column behave the same.

Figure palette, category mappings, units and scale choices:
- Data bars: Viridis blue #31688E; a gap to a reference is its tint #D6E1EC with the label in #31688E.
- Percentages are shown with one decimal and a space before %, as in the README.
- Bar scale: 0–100 %, linear, one shared scale per chart.

Glossary (names and colours used across slides):
- Chapters: Summary blue, Problem slate, Solution blue, Evidence plum, Next steps ochre. Chapter colour is structure only.
- "Top 6": the six most relevant tables plus neighbours sent to the model. "Every table + hints": the full schema with value hints.
- "Our scorer": this project's typed result comparison, not leaderboard scoring.

Asset origins, licences: `assets/figures/cover-art.png` and `cover-art-close.png` drawn by `make_cover.py` (decorative, no real data), recoloured from `docs/showcase/slides/build_cover_art.py`.

UTS identity use: identity uts (UTS subject deliverable).

Final output checks and unperformed checks: batch 1 (pages 1–3) builds; check_deck, audit_layout and check_markers report 0 findings (18 November 2026). Agenda waits until all chapter slides exist.

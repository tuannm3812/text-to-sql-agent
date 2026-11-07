# Showcase handoff

The current poster and deck for Text-to-SQL Agent, and what a portfolio page should reuse.
Updated 7 November 2026.

## Assets

| Asset | Where | Status |
|---|---|---|
| Poster PDF and PNG | [PDF](text-to-sql-agent-poster.pdf), [PNG](text-to-sql-agent-poster.png) | Current, exported from the live poster |
| Live poster | [Google Slides](https://docs.google.com/presentation/d/1yxVBZCk7Zh2Udt_QASjhZaXw7yb2Thw1TbFnN3KOYAg/edit), private | Slide 1 is current; slide 2 is the old poster, kept to compare |
| Live deck | [Google Slides](https://docs.google.com/presentation/d/1SeYPeuPEcVqbDjtHdlR_SI9SbVt-82hCeHe5eEaDRow/edit), private | 18 slides; amber "PENDING" tags stay until release |
| Speaker notes | [speaker-notes.md](speaker-notes.md) | Synced from the deck on 7 November |
| Demo clip | [GIF](slides/captures/2026-11-06-retail-demo.gif), [details](slides/captures/2026-11-06-retail-demo.json) | A real run on a local model |
| App screenshots | [docs/screenshots/](../screenshots/) | Current app design |
| Icons and logos | [slides/assets/](slides/assets/) | Product names and logos belong to their owners |

The live Google files are the source of truth. `build_poster.py` and `slides/build_body_slides.py`
build editable shapes for import into them. `poster.html`, `render.py` and `build_deck.py` are
historical. The deck PDF is not refreshed yet, because the pending tags would show in it.

## Story for a portfolio page

**Headline:** Ask in English. Inspect the SQL.

**One line:** Text-to-SQL Agent turns a plain-English question into read-only SQL a person can
check, on SQLite, DuckDB or PostgreSQL.

1. **Problem:** a fluent answer can still be the wrong answer. Published scores fall from 91.2 %
   on Spider 1.0 to 21.3 % on Spider 2.0 enterprise tasks (o1-preview, Spider 2.0 paper, 2024;
   not this project).
2. **Demo:** the SQL shows what the answer includes. Electronics revenue is 173,366 on all 220
   orders at list price, and 136,984 on 179 completed orders after discounts, 21 % lower.
3. **How it works:** one step of eight uses a model; the application controls execution.
4. **Safety:** it does not rest on the model. The model declined 6 of 6 write requests, but
   sqlglot validation and each engine's read-only connection are tested separately. No layer
   checks meaning, so a person reads the answer and its SQL.
5. **Evidence:** on 1,222 questions over 21 to 65 tables, top 6 tables scored 29.1 % against
   25.5 % for every table with hints: +3.6 points [+1.4, +5.8], with 69 % fewer prompt tokens and
   about 2 s more per question.
6. **Lesson:** better retrieval is not better answers. Fixes for missed tables gained answers
   there and lost them elsewhere.

## Numbers to quote

| Claim | Value | Scope |
|---|---|---|
| Spider 1.0 dev | 64.6 % [61.6, 67.5] | 1,034 questions |
| BIRD dev with evidence | 35.2 % [32.9, 37.6] | 1,534 questions |
| BIRD dev without evidence | 25.1 % [22.9, 27.3] | 1,534 questions |
| Demo suite | 4 of 12 | Interval 50 points wide |
| Safety accuracy | 11 of 15, 73.3 % [53.3, 93.3] | 15 cases |
| Engine conformance | 45 of 45, none skipped | 15 per engine, 3 engines |
| Values in the demo prompt | 79 of 608 stored text values | One question, Retail Analytics |

Results use a local `qwen3.5:9b-q4_K_M` model, thinking off, runs of 10 and 19 October 2026,
and this project's typed comparison, so they are not leaderboard scores.

## Wording rules

- Do not present a retrieval improvement as an accuracy gain.
- Do not treat an interval that crosses zero as a measured change or as equivalence.
- Say "declined by the model" for the 6 of 6, not "blocked" or "refused by the system".
- Say result rows stay out of the prompt, not all row data: value hints are stored values.
- Business impact is unmeasured. Gemini is offered in the app but has no measured results here.

## Design tokens

Blue `#0F4BEB`, amber `#E6A23C`, navy `#17243B`, cream `#FAF7F0`, slate `#46576C`, grey `#59636E`,
pale blue `#E7EDFD`, pale amber `#FBEFD9`. Google Sans and Google Sans Code; Material Symbols
Rounded icons. On blue or navy, use white text: amber text does not read well there. Use amber
for bars and highlights on light backgrounds. Blue marks the default or measurable result; amber
marks a comparison, a gap or a loss.

Standards: [poster](DESIGN.md), [slides](slides/DESIGN.md), [content decisions](slides/BRIEF.md).
Pending work is listed at the end of the brief.

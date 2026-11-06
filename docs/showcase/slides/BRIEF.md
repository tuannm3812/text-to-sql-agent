# Showcase deck brief

**Status: approved by Mike, 6 November 2026.** Structure pass applied to the live deck; awaiting his flip-through before the content pass.

This file decides what the deck says. [DESIGN.md](DESIGN.md) decides how it looks. The [live Google Slides deck](https://docs.google.com/presentation/d/1SeYPeuPEcVqbDjtHdlR_SI9SbVt-82hCeHe5eEaDRow/edit) follows both. When the story changes, change this file first, then the slides.

## 1. The story

**One sentence:** Text-to-SQL is easy to demo and hard to trust, so this agent shows how each answer was produced, enforces read-only execution, and measures what actually helps.

**The thread through the deck:**

1. Asking a database in plain English is useful, but a fluent answer can still be wrong.
2. Other tools mostly solve this with curated business definitions or stored examples, which need setup.
3. This project takes a different route: it needs no curated semantic model, shows its work, validates generated SQL and enforces read-only execution, and can run on a local model.
4. The demo shows why that matters: the SQL reveals which orders and prices its "revenue" includes.
5. The evidence shows where the design helps, and which ideas did not.
6. The next tests follow directly from those limits.

**Audience (decided):** a portfolio reader, such as a hiring manager or lecturer, who may read the deck without a presenter. Each slide has to make sense alone.

**Tone:** say what was measured, on what, against what. No claim that the agent beats any product. The other tools solve a wider problem, and the deck says so.

## 2. Workflow

Each stage ends at a gate. The next stage starts only after the gate passes.

| Stage | What happens | Who | Gate |
|---|---|---|---|
| 1. Brief | Agree the story, slide list and content below | Claude drafts, Mike edits | Mike approves this file |
| 2. Evidence lock | Check every claim against its source; recheck outside facts on the day | Codex | No open findings |
| 3. Structure pass | Reorder slides, add the new slide, set section labels and agenda; no restyling | One editor | Mike flips through the deck |
| 4. Content pass | Titles, subtitles, evidence, takeaways and notes, one section at a time | One editor per section | Mike approves each section |
| 5. Design pass | Apply DESIGN.md: alignment, markers, spacing, figures | One editor | Rendered check of every slide |
| 6. Release | Codex review, sync `speaker-notes.md`, export PDF, commit | Codex and Claude | Mike says push |

**Working rules:**

- Only one agent edits the live deck at a time. Say which one before starting.
- A new number goes into the README first, then the deck.
- Each pass adds a short entry to `docs/6_agent_log.md`.
- Design waits until stage 5, so nothing gets polished and then cut.

## 3. Section map

These four names appear in both the agenda and the slide labels, so the two always match.

| Section | Reader question | Slides |
|---|---|---|
| Opening | What is this, and what did it find? | 1–3 |
| 01 Problem | Why is this hard, and what do others do? | 4–6 |
| 02 Solution | What did we build, and how is it controlled? | 7–10 |
| 03 Evidence | What did we measure, and what did we learn? | 11–15 |
| 04 Next steps | What is still unproven? | 16–17 |

| New | Was | Label | Change |
|---|---|---|---|
| 1 | 1 | none | Illustration replaces the photo |
| 2 | 4 | EXECUTIVE SUMMARY | Moved up; content revised |
| 3 | 3 | AGENDA | New sections and ranges |
| 4 | 5 | PROBLEM > WHY IT IS HARD | Rewritten |
| 5 | new | PROBLEM > OTHER APPROACHES | New slide |
| 6 | 6 | PROBLEM > OUR AIM | Rewritten around the gap |
| 7 | 2 | SOLUTION > DEMO | Moved; new message |
| 8 | 7 | SOLUTION > DATA BOUNDARY | Label only, light edits |
| 9 | 8 | SOLUTION > ARCHITECTURE | Label only |
| 10 | 9 | SOLUTION > SAFETY | Label only |
| 11 | 10 | EVIDENCE > METHOD | Label only |
| 12 | 11 | EVIDENCE > BENCHMARKS | Adds demo suite result |
| 13 | 12 | EVIDENCE > LARGE SCHEMAS | Label only |
| 14 | 13 | EVIDENCE > WHAT WAS TRIED | Label only |
| 15 | 14 | EVIDENCE > RETRIEVAL AND ANSWERS | Label only |
| 16 | 15 | NEXT STEPS > TESTS | Adds semantic definitions test |
| 17 | 16 | close | Card removed; illustration added |

## 4. Slide briefs

Each brief gives the reader question, the main message, what goes on the slide, and where it comes from. Titles are working titles.

### Opening

**Slide 1. Cover**
- **Message:** the name and the promise, nothing else.
- **Content:** "Ask your data. Inspect the answer." and "An inspectable text-to-SQL agent for read-only analytics." Illustration only, no text on it.
- **Cover label:** keep 36121 and the full subject name.

**Slide 2. Executive summary: "Inspectable SQL, with measured limits"**
- **Question:** if I read one slide, what should I know?
- **Message:** the agent's read-only controls are tested, its accuracy is measured, one idea clearly helped, and better retrieval alone did not.
- **Content, four highlights:**
  1. **Read-only controls:** SQL validation plus engine read-only protection on 3 engines; 45 conformance tests, 0 skipped.
  2. **Measured accuracy:** 64.6 % on Spider dev and 35.2 % on BIRD dev with evidence, on a local 9B model and this project's scorer.
  3. **Main finding:** on 21- to 65-table databases, top 6 selection scored +3.6 points [+1.4, +5.8] over full DDL plus hints, with 69 % fewer prompt tokens.
  4. **Honest limit:** better table retrieval did not measurably improve answers; a person still reviews the result.
- **Source:** README Evaluation Results; `AGENTS.md`, 2026-11-04.
- **Change:** adds read-only protection, which is the product's main promise and is missing today. The moved slide must not refer back to the demo.

**Slide 3. Agenda: "From the problem to the evidence"**
- **Subtitle:** replace "You have seen the product" with "Why it is hard, what we built, what we measured, what comes next."
- **Content:** four numbered parts with grey questions, and a contents list under each with a linked page chip per slide. The Problem question is "What are we solving?". Short section names (Other tools, Trials, Retrieval) match the slide labels. Recheck the chips whenever slides move.

### 01 Problem

**Slide 4. "A fluent answer can still be the wrong answer"**
- **Question:** what does text-to-SQL do, and why is it hard?
- **Message:** translating a question into SQL is the easy part. Knowing what the question means in this database is the hard part.
- **Content:** a simple flow, question → schema → SQL → rows, then three difficulties:
  1. **Meaning:** business words such as "revenue" are not columns.
  2. **Scale:** real schemas are large. Spider 2.0 databases often exceed 1,000 columns.
  3. **Risk:** generated SQL must be stopped from changing the data.
- **Takeaway:** the benchmark gap. In the Spider 2.0 paper, an o1-preview agent solved 21.3 % of enterprise tasks, against 91.2 % on Spider 1.0 and 73.0 % on BIRD.
- **Findings added 6 November:** the 69.9-point gap, why scores fall (metadata, dialects, project code, queries past 100 lines), and this project's 64.6 % and 35.2 %, labelled as not comparable with the published chart.
- **Keep from the old slide:** one line that dashboards and analyst SQL remain the right tools for recurring, defined metrics.
- **Source:** Spider 2.0 paper (R1).

**Slide 5. "Other tools add business meaning before the SQL" (new)**
- **Question:** how do other agents solve this?
- **Message:** the main approaches ground the model in curated knowledge, which adds business meaning and control but also setup.
- **Content:** one neutral comparison, grouped by approach, not ranked:

| Approach | Example | How it grounds the model | What it needs |
|---|---|---|---|
| Warehouse semantic model | Snowflake Cortex Analyst | Semantic model adds business definitions the schema lacks | Authoring the model; runs in Snowflake |
| Curated knowledge | Databricks Genie Agents | Annotated tables, knowledge store, instructions, example SQL | Domain experts configure it; runs in Databricks |
| Open semantic layer | WrenAI | Approved metric definitions, joins and examples kept in Git | Writing and reviewing the definitions |
| Retrieval over past work | Vanna | Retrieves DDL, documents and stored question–SQL pairs | Training data; repository archived March 2026 |
| Research agents | BIRD leaderboard systems | Multi-step, benchmark-tuned pipelines | Mostly research systems |

- **Takeaway:** for scale, the top BIRD test score was 83.40 % against 92.96 % for humans, read 6 November 2026. Vendor accuracy claims are not comparable, so the deck omits them.
- **Scope note:** "Product descriptions from public documentation, November 2026; not a ranking."
- **Source:** R2–R6. Snowflake now recommends moving to Cortex Agents, so mention that in the notes, and show the read date on the slide.

**Slide 6. "Our aim: useful without setup, and checkable by default"**
- **Question:** where does this project fit, and who is it for?
- **Message:** this is a narrower tool. It needs no curated semantic model and puts the checking in the user's hands.
- **Content:**
  - **Who it helps:** an analyst who knows the question but not the schema, and a reviewer deciding whether an LLM can be trusted near a database.
  - **What we chose:** no curated semantic model to build; it uses schema metadata and bounded, row-derived value hints; SQL always visible; generated SQL validated and run read-only; local model option; query-result rows not sent to the model.
  - **What we gave up:** no governed metric definitions, so "revenue" stays ambiguous unless a person checks it.
  - **Retail example:** "Which product categories generate the most revenue?" leads into the demo.
- **Source:** `docs/1_brief.md`; README What It Does and Inspiration sections.

### 02 Solution

**Slide 7. Demo: "The SQL shows what the answer includes"**
- **Question:** what does it look like, and why does inspection matter?
- **Message:** the answer looks finished, but only the SQL shows what "revenue" counted.
- **Content:** an animated capture of the real app (`slides/captures/2026-11-06-retail-demo.gif`), then a comparison of two differently worded questions:

| | Demo question | Separate benchmark question |
|---|---|---|
| Wording | "...generate the most revenue?" | "...generate the most completed order revenue?" |
| Orders counted | All 220, including cancelled and returned | 179 completed |
| Discounts | Ignored | Applied |
| Electronics | 173,366 | 136,984 |

- **Takeaway:** the demo question did not say which orders or prices to use, and the SQL makes that choice visible. Stating completed, net revenue gives a figure about 21 % lower, with the same top category.
- **Boundary:** this is an illustration of inspection, not a benchmark failure, and not evidence that a semantic model would have changed this response.
- **Source:** capture of 6 November (`slides/captures/`); `evaluation/cases.json`, `retail_revenue_by_category`; recomputed on `data/retail_analytics.db`.

**Slide 8. Data boundary: "The model sees 79 stored values, not the 1,851 rows"**

*Reader question:* can I point this at my data, and what would leave? The old slide listed four items, so it described the design without answering that.

*Measured on 6 November* (Retail demo, demo question, default settings; `rag.retrieve_schema_context` on `data/retail_analytics.db`):

| Fact | Value |
|---|---|
| Database | 11 tables, 1,851 rows, 11,562 cells |
| Schema text sent | 4,971 characters, 9 tables; 1,419 characters (29 %) are hints |
| Stored values in the prompt | 79, on 17 hint lines, of 608 distinct text values (13 %) |
| Result rows sent | 0 |
| Text columns | 30, of which 23 are within the 20-value limit |
| Sent as hints | Includes `gender` and `supplier_name` |
| Kept out | `full_name` (51 distinct) and `email` (60), only because they exceed the limit |

Also found in the code: the question is sent too; a failed query and its error go back on the one repair try; the limit counts distinct values and has no check on sensitivity; a hosted model receives all of this, a local model keeps it on the machine; turning table selection off sends plain DDL with no hints.

*Options considered:*

| Option | Shows | Insight | Verdict |
|---|---|---|---|
| A. Real prompt, annotated | The actual text the model gets | Concrete, and matches the slide 7 SQL card | Use as the main visual |
| B. Proportion bar | 79 of 608 distinct text values | How much is sent, like for like | Use. Comparing with 11,562 cells mixed units and overstated how little is sent |
| C. Local against hosted | Where the boundary sits | The model choice moves it | Use as the decision strip |
| D. Limit stress test | What a count limit misses | Hints are real data; emails stay out only by count | Use as the main takeaway |
| E. Keep the boundary map | Four items crossing a line | Clear but descriptive | Drop |

*Decision:* combine A to D. **Message:** a small share of stored text values reaches the prompt, as lists and never as rows, but what does is real, so the model choice and the hint columns are the two things to check first.

*Boundary:* 79 is for this question on this demo database, and varies by question. It is not a privacy guarantee.

**Slide 9. Architecture: "The model proposes SQL; the application controls execution"**

*Reader question:* where does control sit, and where can an answer still go wrong? The old diagram named components, left out the Run step, and gave no example or limit.

*Checked on 6 November:* `pipeline.ask_database` runs select, generate, check, execute; a failed run triggers one repair, and the repaired SQL is checked again. The app itself names the steps Picked, Wrote SQL, Checked it and Ran it (`ui/results.py`). Demo capture: 6 of 11 tables plus 3 neighbours, 2 of the 9 used, 5 rows.

*Options considered:*

| Option | Shows | Insight | Verdict |
|---|---|---|---|
| A. Swimlanes by owner | Who does what | Control, but no example | Keep the idea as a label per step |
| B. Demo question traced | Real values at each step | Links slides 7 and 8 | Use |
| C. Limit per step | Where each step can fail | Links to the evidence section | Use: this is the insight |
| D. Code module map | Files and functions | For developers only | Drop |

*Decision, revised by Mike:* a detailed eight-step architecture flow with the tech stack logos, following `docs/2_architecture.md`: Streamlit, schema, retrieval, prompt, model (Ollama or Gemini), sqlglot validation, read-only run on SQLite, DuckDB or PostgreSQL, results. It replaces the five-step journey map (commit `2212672`). **Message:** one step of eight uses a model, behind two separate gates that do not check meaning. Mike then asked to split it by stage: five stage bars (Ask, Prepare, Generate, Check and run, Answer), each with its output, and notes that explain the content rather than ownership. After review the eight steps became equal cards on one template on a four-column grid, top row left to right and bottom row right to left, with the database between Read schema and Run and the legend kept.

**Slide 10. Safety: "Safety does not rest on the model".** Replaces the two-layer diagram. Keep the 11 of 15 scope note.

*Checked on 6 November:* in the 10 October safety run, 14 of 15 cases ended in the model's own control statement: 6 `BLOCKED_UNSAFE_SQL`, 8 `UNANSWERABLE_WITH_GIVEN_SCHEMA`. The fifteenth was the substitute metric. So no write request reached the two layers, and "6 of 6 refused" measures the model, not the layers shown above it. The layers are tested separately: `test_writes_are_refused_by_the_connection_itself` bypasses the application check and runs writes straight at each engine.

*Decision, approved by Mike (sample B):* a threat matrix of three lines of defence: model (a behaviour measured in one run), application check, engine. Ticks and a legend separate enforced and tested from behaviour, a gap and not this layer's role, and dots count the lines each threat meets. Examples are real safety cases. **Message:** safety does not rest on the model, because each later layer holds when the earlier one fails.

### 03 Evidence

**Slide 11. Method: "Every result can be traced and compared fairly".** Each suite states the question it answers, and a new panel teaches how to read a paired change with two real results. Message: read the interval, not the point, because slides 12 to 15 use that rule.

**Slide 18. Backup: "Schema RAG ranks every table against the question".** After Thank you, for questions on step 3 of slide 9. Real scores for the demo question from `rag.rank_schema_chunks`: 11 tables scored, top 6 kept, 3 neighbours added, 2 used. It is built with `ONLY=17` because the bodies stop at deck slide 16.

**Slide 12. Benchmarks: "The local model scored 64.6 % on Spider and 35.2 % on BIRD with evidence"**
- **Mike's review, 6 November:** the difficulty panels were unclear, so each Spider level now says what it means, BIRD shows evidence on and off with an example hint, and the note defines "matched".
- **Change:** add the demo suite beside the three bars: 33.3 % [8.3, 58.3], 4 of 12. This is the suite built on the demo's databases, so leaving it out would flatter the demo.
- **Note:** runs of 10 October 2026. Project scorer, so not comparable with leaderboards. The re-runs after the hint label (64.0, 35.7 and 25.4) were not a measurable change; keep them in the notes.

**Slide 13. Large schemas, rebuilt 7 November:** one colour per way of sending the schema, three measures side by side, a labelled by-database interval chart, a split showing selection wins until it drops a table, and three stat cards with icons.

*Earlier plan:* keep the current content. Add to the notes that 29.1 % is the 19 October arm behind the +3.6, and that the kept scorer has since scored 30.0 %.

**Slide 14. What was tried: keep the current content.** Message: later trials found tradeoffs, not a further accuracy gain. *Approved by Mike, in the deck:* a decision table with what changed, the interval, the side effect and the decision.

**Slide 15. Retrieval and answers: keep the current content.** Message: better table coverage did not measurably improve accuracy. *Approved by Mike, in the deck:* the two question groups, one gained-and-lost chart for all three fixes, and why totals barely move. The dense row is derived: 8 to 26 on the 128 and 359 to 343 on the 1,094 (369 total).

### 04 Next steps

**Slide 16. "Four tests would address the main evidence gaps"**
- **Change:** replace "Test broader value hints" with a combined item, or add a fifth, for **business definitions**: test whether a small set of definitions, such as "revenue means completed, net of discount", changes answers on ambiguous questions. This follows from slides 5 and 7, and its result is unknown.
- **Keep:** hosted model under the same contract; targeted table recovery; new large schemas. Value hints still need a data-boundary decision first.

**Whole-deck pass, 6 November:** slides 8 to 16 were rebuilt as diagrams and charts from `build_body_slides.py`: a boundary map (8), swimlanes (9), two gates (10), suite bars (11), intervals plus difficulty bars (12), by-database intervals (13), a forest plot (14), diverging gains and losses (15), a gap-to-test roadmap (16). Slide 12 now shows the demo suite. Slide 16 leads with business definitions; broader hints moved to its scope note.

**Slide 17. Close**
- **Message:** inspectable SQL, measured tradeoffs and a clear next experiment.
- **Content:** demo and repository links, group credits, and the smaller illustration.

## 5. Decisions

Mike's picks, 6 November 2026:

1. **Audience:** portfolio deck. The cover keeps the full subject name (Mike, 6 November).
2. **Slide 5:** one neutral table.
3. **Slide 17 card:** removed.
4. **Cover image:** a custom wordless illustration replaced the photo on slide 1, with a smaller version on slide 17 (`build_cover_art.py`). No credit needed.
5. **Editor:** Claude edits the live deck through Chrome; Codex reviews.
6. **Push:** done for the brief.

## 6. External sources

Product pages change, so the deck must state the date it read them.

| ID | Source | Used for | Status |
|---|---|---|---|
| R1 | [Spider 2.0 paper, arXiv 2411.07763](https://arxiv.org/abs/2411.07763) | 632 tasks, often over 1,000 columns; 21.3 %, 91.2 %, 73.0 % | Read at source, 6 Nov 2026 |
| R2 | [BIRD leaderboard](https://bird-bench.github.io/) | Human 92.96 %; AskData test 83.40 %, dev 78.49 % | Read at source, 6 Nov 2026 |
| R3 | [Cortex Analyst overview](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst) | Semantic model for definitions schemas lack; Snowflake recommends moving to Cortex Agents | Read at source, 6 Nov 2026 |
| R4 | [Genie Agents concepts](https://docs.databricks.com/aws/en/genie-agents/concepts) | Domain experts configure datasets, knowledge store, instructions, example SQL; formerly Genie Spaces | Read at source, 6 Nov 2026 |
| R5 | [WrenAI on GitHub](https://github.com/Canner/WrenAI) | Governed semantic layer; definitions as YAML and Markdown in a repository | Read at source, 6 Nov 2026 |
| R6 | [Vanna on GitHub](https://github.com/vanna-ai/vanna); [Vanna with Qdrant](https://qdrant.tech/documentation/frameworks/vanna-ai/) | Retrieval approach; repository archived 29 March 2026 | Status read at source; approach from Qdrant docs |
| R7 | [Holistics, "Why is Text-to-SQL so hard?"](https://www.holistics.io/blog/text-to-sql/) | Semantic layers; already cited in the README | Optional background |

Internal figures come from the README's Evaluation Results at `f3a4e93` and later, `AGENTS.md`, `evaluation/cases.json` and `data/retail_analytics.db`.

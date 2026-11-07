# Speaker notes — Text-to-SQL agent deck

Synced from the live 18-slide deck on 7 November 2026. The deck's notes are the source;
regenerate this file from an export rather than editing it by hand.

## Slide 1 — Cover

This deck is about one idea: ask your data, then inspect the answer.
It began as a UTS group project and has since been refined as a portfolio project. The illustration shows what the agent does: it finds the right tables, then lets you look closely at the result.
Reference — not read aloud
Cover illustration from docs/showcase/slides/build_cover_art.py. It is decorative and shows no real data.

## Slide 2 — Executive summary

Here is the whole story before the detail.
[Point: 45 of 45]
Read-only comes first: generated SQL is validated and run read-only, and all 45 tests passed on three database engines with none skipped.
[Point: 64.6% and 35.2%]
With a local 9B model, 64.6 % of Spider dev answers and 35.2 % of the harder BIRD dev answers matched, using this project's scorer. These are not leaderboard scores.
[Point: +3.6 pts]
On databases of 21 to 65 tables, sending the top six tables and their neighbours scored 3.6 points above sending every table with hints, using 69 % fewer prompt tokens. The gain comes from the 65- and 34-table databases.
[Point: Judge the whole answer]
About one in three Spider answers still did not match, and better retrieval did not measurably help, so a person should review results.
[Point: Smaller prompts are not faster here]
Those smaller prompts took about two seconds longer per answer, because each question gets a different schema and the local model cannot reuse its cache.
Reference — not read aloud
README Evaluation Results: release runs of 10 Oct 2026 at 7708295; bird_train_large at 47284f5, 19 Oct 2026, +3.6 [+1.4, +5.8] against full DDL plus hints. 69 % is 68.6 % rounded; the token index is derived from it. 29.1 % is that comparison's arm; the kept scorer later scored 30.0 %. AGENTS.md 2026-11-04: conformance 45 passed, 0 skipped, 15 per engine. AGENTS.md 2026-10-19: top 6 is 2.0 s slower, from Ollama prefix caching.

## Slide 3 — Agenda

The deck follows four questions, in this order.
[Point: 01 Problem]
First, why is this hard, and what do other tools do about it?
[Point: 02 Solution]
Then, what was built, starting with the demo, and how it is controlled.
[Point: 03 Evidence]
Then what was measured, including the ideas that did not help.
[Point: 04 Next steps]
Finally, what is still unproven and how to test it.
Reference — not read aloud
Section names match the slide labels. Structure: docs/showcase/slides/BRIEF.md.

## Slide 4 — Why it is hard

Text-to-SQL turns a question into SQL over a schema and returns rows. Writing the SQL is the easy part.
[Point: SQL is the easy part]
The hard part is what the question means here. A word like revenue is not a column, and the schema does not say whether it is gross or net. Real schemas are also large: Spider 2.0 databases often exceed 1,000 columns.
[Point: Demos flatter; enterprise data does not]
In the Spider 2.0 paper, an o1-preview agent solved 21.3 % of enterprise tasks, against 91.2 % on Spider 1.0 and 73.0 % on BIRD. That is about 70 points lower, because these tasks need metadata, several SQL dialects and project code, and queries often pass 100 lines.
[Point: We see the same direction]
Our local model also falls on the harder test, from 64.6 % on Spider to 35.2 % on BIRD with evidence. That uses our own scorer, so it cannot be compared with the published chart.
[Point: Keep a person in the loop]
The SQL runs on real data, so it must be stopped from changing that data, and a valid query can still answer the wrong question. Dashboards and analyst SQL remain the right tools for defined, recurring metrics. Next: how other tools handle this.
Reference — not read aloud
Spider 2.0 paper, arXiv 2411.07763 abstract, read 6 November 2026: 632 tasks; databases often over 1,000 columns; 21.3 %, 91.2 % and 73.0 % as stated. 91.2 minus 21.3 is 69.9 points. Project scores: README Evaluation Results, release runs of 10 Oct 2026 at 7708295.

## Slide 5 — Other tools

Other tools reach business meaning through setup. This table compares them on the same criteria; the effort dots are our assessment, not a ranking.
[Point: Setup is the price of meaning]
Snowflake says schemas lack business definitions and metrics handling, so people add them in a semantic view. Databricks has a domain expert curate SQL expressions and example SQL. WrenAI keeps its semantic layer in Git.
[Point: That work does not end]
Read down the Upkeep column. Snowflake tells teams to refine with evaluations, and Databricks calls curation an iterative process.
[Point: Systems are close, not done]
Vanna saves past queries and learns from use, though its repository was archived in March 2026. The top BIRD test score is 83.40 %, still below 92.96 % for humans.
[Point: We pay in review, not setup]
This project only needs a database connection, so it pays in the last column: a person checks what each answer means. Next: where that puts us.
Reference — not read aloud
All read 6 November 2026. docs.snowflake.com Cortex Analyst: semantic views, legacy YAML supported, recommends transitioning to Cortex Agents, Autopilot, evaluations. docs.databricks.com Genie best practices: Genie Agents formerly Genie Spaces, domain expert, iterative, aim for five or fewer tables, up to 50. github.com/Canner/WrenAI: MDL semantic layer, versioned files; engine Apache-2.0, some features commercial. github.com/vanna-ai/vanna: archived 29 March 2026; Vanna 2.0 Tool Memory; legacy trained on DDL, documentation and question-SQL pairs. bird-bench.github.io: AskData 83.40 test; humans 92.96; most entries give name and affiliation only. Effort dots and Best for and Risk entries are our reading.

## Slide 6 — Our aim

Our aim has two halves: useful without setup, and checkable by default.
[Point: Who it helps]
It is for an analyst who knows the question but not the schema, and for a reviewer deciding whether to trust the answer.
[Point: The matrix]
Left to right is the setup needed before the first useful answer. Bottom to top is how much business meaning is built in. Curated tools and BI dashboards sit top right: they earn meaning through setup. Top left would be meaning with no setup, the ideal, which is not yet available.
[Point: What we chose]
This project sits bottom left, a quick start, but above a general chatbot because it uses the real schema and bounded hints. There is no model to build, and all 45 conformance tests passed. Query-result rows are not sent to the model.
[Point: What we gave up]
There are no governed metric definitions, so a word like revenue stays ambiguous until a person checks it.
[Point: When a curated tool fits better]
If metrics must match across teams, choose a governed tool. This project suits a first look at a database. Next: the demo shows that revenue question.
Reference — not read aloud
docs/1_brief.md; README, What It Does. AGENTS.md 2026-11-04: conformance 45 passed, 0 skipped. Value hints are row-derived: up to 6 frequent values of text columns with at most 20 distinct values. Product horizontal positions follow the slide 5 Setup ratings; everything else, including BI dashboards and a general chatbot, is qualitative judgement. BIRD systems are omitted because their setup is not listed.

## Slide 7 — Demo

Here is the agent answering one question, and why the SQL matters.
[Point: The answer looks finished]
Asked which product categories generate the most revenue, the local model says Electronics leads with 173,366. It looks complete, but the chart does not say which orders it counted.
[Point: The SQL shows the choice]
The SQL sums price times quantity. It has no status filter and no discounts, so all 220 orders count, including cancelled and returned ones.
[Point: Wording changes the number]
A separate benchmark question asks for completed order revenue. That counts 179 orders with discounts and gives 136,984, about 21 % lower, with the same top category.
[Point: This is why inspection matters]
Neither figure is wrong by itself. The first question did not say which revenue it meant, so a person decides. This illustrates inspection; it is not a benchmark failure. Next: what the model is allowed to see.
Reference — not read aloud
GIF: docs/showcase/slides/captures/2026-11-06-retail-demo.gif, real app and local Ollama qwen3.5:9b-q4_K_M; it opens on the SQL frame, so a PDF export shows that frame. evaluation/cases.json, retail_revenue_by_category. Recomputed on data/retail_analytics.db, 6 November 2026: 173,366 and 136,984; orders: 179 completed, 21 returned, 20 cancelled. (173,366 - 136,984) / 173,366 = 21.0 %.

## Slide 8 — Data boundary

Before pointing this at your own data, you need to know what the model sees.
[Point: The prompt is mostly structure]
For the demo question, the prompt held nine table definitions and 79 stored values. That is 79 of the 608 distinct text values in the database, about 13 %, sent as lists and never linked to a row. Result rows are never sent, and about 71 % of the schema text is structure.
[Point: Hints are real data]
The hints are real stored values, such as order status and gender. The limit counts distinct values, not sensitivity. Customer emails stay out here only because there are more than twenty of them; a smaller table could qualify.
[Point: The model choice moves the boundary]
With a local model, nothing leaves your machine. With a hosted model, the question, schema and hints all go to the provider.
[Point: Check before using real data]
So review what is in the prompt first, or turn table selection off, which sends plain table definitions with no hints. Next: how the application controls what runs.
Reference — not read aloud
Measured 6 November 2026 with rag.retrieve_schema_context on data/retail_analytics.db, question: Which product categories generate the most revenue? 608 is the sum of COUNT(DISTINCT) over the 30 text columns in all 11 tables; the 79 values are counted from the 17 hint lines of the 9 tables sent; 79 / 608 = 13.0 %, and 79 varies by question. The 37 non-text columns send no values. 4,971 schema characters, 1,419 on hint lines. full_name 51 distinct, email 60. config.py: DEFAULT_VALUE_HINT_LIMIT 6, DEFAULT_VALUE_HINT_MAX_CARDINALITY 20. pipeline.prompt_schema: table selection off sends get_schema, plain DDL. pipeline._repair_sql sends the failed SQL and engine error. Question value matching stays off: +0.4 [-0.9, +1.6].

## Slide 9 — Architecture

This is the whole path of one question: five stages, eight steps, and only one step is the model.
[Point: Ask, top left]
A person picks a demo database, a file, a connection string or CSV uploads, then asks in plain English in the Streamlit app.
[Point: Prepare, top row]
The application reads the schema from the database, selects the most relevant tables, and builds the prompt. Retrieval and prompt building use no model.
[Point: Generate, blue card at bottom right, marker 1]
Step five is the only model call. The app offers Gemini as a hosted model or Ollama running locally. The model writes one SQL statement, or declines if the request would change data or the schema cannot answer it. It never sees result rows. It returns text, and the application decides what happens to that text.
[Point: Check and run, bottom row, marker 2]
The flow now runs right to left through two separate gates. sqlglot refuses anything that is not a single read, and then the engine runs the query read-only with a work budget and a row cap. Neither gate can tell whether the query means the right thing, so a valid query can still be wrong. That is why the person still reads the answer.
[Point: Database band, marker 3]
The same stages work on SQLite, DuckDB and PostgreSQL. The connection string sets the engine. Each engine enforces read-only in its own way, and each passes the same 15 conformance tests.
[Point: Dashed arrow, marker 4]
If a query raises an error when it runs, that error goes back to the model once. The repaired query passes the same checks, so a retry never skips a gate. If the repair is refused or fails again, the attempt ends there. A query stopped by the work budget is not retried.
[Point: Answer, bottom left]
The flow ends where it began, with the person. The app shows the answer, the table, a chart when the result suits one, the SQL and why those tables were chosen, so they can inspect it before trusting it.
Reference — not read aloud
Sources: pipeline.answer_question and _sentinel_code (max_repair_attempts=1; budget aborts return a result, so no repair); config.py (top 6, one foreign-key hop, 6 hints, 20-value ceiling, 1,000 rows, 100,000 VM steps, 5,000 ms; dense retrieval off); docs/2_architecture.md step 7; ui/connection.py offers Gemini first and Ollama second; llm.py uses LangChain for Ollama only; the benchmark runs on later slides used Ollama. Conformance: 45 tests, 15 per engine, 0 skipped.

## Slide 10 — Safety

Safety here does not rest on the model. Each threat meets its own set of defences, and this table shows exactly which.
[Point: Column headers, marker 1]
There are three lines of defence. The first is the model itself, which declines a request. In our safety run, 14 of 15 cases ended in the model's own decline. That is useful, but it is behaviour, shown in amber, and it can change with the model or the prompt.
[Point: Blue ticks, marker 2]
The blue ticks are enforced in code and tested on their own. The application check uses sqlglot. For the engine, writes run straight at each one, bypassing the application check, and all three refuse them.
[Point: Lines column, marker 3]
Read the dots on the right. A write meets all three lines. A runaway query or an oversized result meets only the engine. And a question about data the schema lacks meets only the model, which declined 5 of 6.
[Point: Would run]
There is one honest gap in the table: a read of the engine's own internals would run if it reached the engine, so the application check is what stops it.
[Point: Amber row, marker 4]
The last row is the limit. Asked for average shipping weight, the model returned average unit cost. That query was valid, so every check passed. No layer checks meaning, so the person is the last check.
Reference — not read aloud
Sources: run 2026-10-10T061911 safety, qwen3.5:9b, safety accuracy 73.3 % [53.3, 93.3] (11/15): 6 BLOCKED_UNSAFE_SQL, 8 UNANSWERABLE_WITH_GIVEN_SCHEMA including 3 internals requests, 1 substitute metric (retail_shipping_weight). tests/test_engine_conformance.py: 5 write statements on each engine, 45 tests, 15 per engine, 0 skipped. tests/test_safety.py: 182 passed. File reads: DuckDB enable_external_access off, SQLite ATTACH denied, PostgreSQL least-privilege role. Earlier full suite: 1,870 passed against live PostgreSQL 16 on 4 November.

## Slide 11 — Method

Before the results, this slide says why the numbers can be trusted and how to read them.
[Point: Left, the five suites]
We ran 3,817 questions in five suites, and each suite answers one question. Spider and BIRD measure accuracy. The large-schema suite tests table selection, because the dev databases have at most 14 tables, so selection barely matters there. Demo and Safety are small diagnostics.
[Point: Right, the method cards]
Results are compared by value and type, so wording of the SQL does not matter. Every rate carries a 95 percent bootstrap interval. Each of the 37 recorded runs pins its commit, data, prompt and model, and every change is compared on the same questions against a named baseline.
[Point: Small suites, marker 3]
With 12 and 15 cases, Demo and Safety show behaviour rather than accuracy, because their intervals are wide.
[Point: Blue panel, marker 4]
Here is the one rule for the next slides. Read the interval, not the point. On the top line the whole interval sits above zero, so that change of 3.6 points is measurable. On the second line the interval crosses zero, so we cannot say the change did anything.
Reference — not read aloud
Sources: evaluation/suites (1,034 + 1,534 + 1,222 + 12 + 15 = 3,817); 37 run directories under evaluation/results, all from a clean tree; stats.py 10,000 resamples, seed 0. Paired examples on bird_train_large: top 6 against full DDL plus hints +3.6 [+1.4, +5.8]; shared-summary against shared +0.2 [-1.5, +2.0]. Accuracy uses this project's typed comparison, not the benchmark scorers.

## Slide 12 — Benchmarks

These are the headline results for one local 9B model on the public benchmarks and our demo suite.
[Point: Top chart]
Each dot is the share of questions whose result matched the reference answer, and the line is its 95 percent interval. Spider reached 64.6 percent and BIRD with evidence 35.2 percent.
[Point: Spider panel, marker 1]
Harder questions score lower. Spider's own rule sets the level from how many SQL parts a query needs: a simple count is easy, while joins with grouping and ordering are extra hard. Scores fall from 84.3 to 38.0 percent.
[Point: BIRD panel, marker 2]
Evidence is a hint the benchmark supplies, for example that promotional name refers to the column flavorName. Paired on the same questions, it adds 10.1 points, and the blue bars beat the grey ones at every level.
[Point: Demo suite, marker 3]
Our own demo suite matched 4 of 12, with an interval 50 points wide. A good demo on stage proves little.
[Point: Marker 4]
One practical lesson: thinking used up the output budget and left empty SQL. Turning it off added 8.5 points on Spider.
Reference — not read aloud
Runs of 10 October 2026, qwen3.5:9b-q4_K_M, commit 7708295. Spider 1,034: easy 248, medium 446, hard 174, extra 166. BIRD 1,534: simple 860, moderate 443, challenging 231; no evidence 34.2, 16.3, 8.2. Project scorer, not leaderboard scores. Re-runs after the hint label: 64.0, 35.7 and 25.4, not a measurable change.

## Slide 13 — Large schemas

On databases of 21 to 65 tables, sending fewer tables scored higher, but the trade-off has three sides.
[Point: Top row]
Here are the three ways to send the schema on the same 1,222 questions. Top 6 plus neighbours is the most accurate at 29.1 percent and uses by far the fewest prompt tokens, but it is the slowest.
[Point: Left panel, marker 1]
The gain is concentrated. The 65-table and 34-table databases gain 5 to 6 points, and their intervals sit clear of zero. The two smaller databases cross zero, so nothing is measurable there.
[Point: Every table + hints, marker 2]
Adding hints to a full schema did not help: minus 1.3 points, and the interval crosses zero. About half the values the questions need sit in columns too large to hint.
[Point: Stat cards, marker 3]
Fewer tokens did not mean faster. Top 6 takes about 2 seconds longer, because a prompt that changes per question cannot reuse the local model's cache.
[Point: Right panel, marker 4]
This is the real risk. When every needed table was sent, top 6 scored 32.9 percent against 26.7. When a needed table was dropped, on 167 questions, it scored 5.4 against 18.0. Selection still stays the default for its overall gain.
Reference — not read aloud
Runs of 19 October 2026 at 47284f5, bird_train_large, 1,222 questions. Top 6 against every table + hints +3.6 [+1.4, +5.8], helped 117, hurt 73; against every table without hints +2.3 [+0.0, +4.6], borderline. Latency +2.0 s [+1.8, +2.2]. The split is observed, not causal. The later scorer reached 30.0 % and cut dropped-table questions from 167 to 128 (slide 15). Sources: evaluation/results/bird_train_large/README.md, evaluation/results/retrieval/README.md.

## Slide 14 — Trials

After table selection, we ran five more trials. They found tradeoffs, not a further accuracy gain.
[Point: Top row, marker 1]
Each row shows what changed, the paired result, the side effect, and what we decided. Sending the best tables is the one clear gain, with an interval clear of zero. None of the five later trials added to it.
[Point: Scorer signals, marker 2]
The scorer change sent all needed tables more often, from 1,055 questions to 1,094. Its 0.9 points still spans zero, so better retrieval did not become measurably better answers. We kept it for the retrieval gain.
[Point: Dense embeddings, marker 3]
Dense embeddings took dropped-table questions from 8 to 26 correct, but other answers churned, so the whole suite moved only 0.2 points. We left it off.
[Point: Shared layout, marker 4]
The shared layout is the one measurable loss. It cut latency by 58 percent and lost 2.4 points. Adding column summaries did not recover that. Both stay opt-in, and the cause is unresolved.
Reference — not read aloud
All rows on 1,222 bird_train_large questions, paired 95 % intervals against each row's own baseline. Value matching reads row data at question time, so it stays off (owner, 2026-10-19). Shared plus summaries is not controlled: the commit differs. Sources: evaluation/results/value_matches, scorer_signals, dense_embeddings, shared_layout.

## Slide 15 — Retrieval

Better table coverage did not measurably improve accuracy, and this slide shows why.
[Point: Two groups at the top]
The later scorer leaves two groups. On 128 questions a needed table was missed, and top 6 got 8 right. On the other 1,094 every needed table was sent.
[Point: Chart, marker 1]
Each fix helps where it aims. Blue is answers gained on the missed group. Dense embeddings took those questions from 8 to 26 correct.
[Point: Amber bars, marker 2]
But the other questions pay. Sending every table won 15 answers and lost 44, so the whole suite fell. That is a net of minus 29. Adding column summaries was much the same.
[Point: 22 of 480, marker 3]
Small prompt changes flip answers. Even when the set of tables stayed the same, reordering them changed 22 of 480 answers, so gains can vanish in the churn.
[Point: Unknown live, marker 4]
The groups come from the evaluation, so a live system cannot see which group a question is in. The next test is targeted recovery: recover missed tables only where needed, and report both groups.
Reference — not read aloud
Baseline: selected tables with the kept scorer, 367 of 1,222 (8 + 359). Dense embeddings: 369, of which 26 on the 128, so 343 on the 1,094; the +18 and -16 are derived from those counts. Whole suite +0.2 [-1.6, +2.0]. Dense also cut missed-table questions from 128 to 74. Every table: 338 (23 + 315). Summaries: 341 (21 + 320), comparison spans commits. Gained and lost are net changes per group, not flip counts. Sources: evaluation/results/dense_embeddings, shared_layout, scorer_signals.

## Slide 16 — Next tests

These four tests would close the main gaps in the evidence. Each needs a measured outcome before any default changes.
[Point: Row 1]
First, business definitions. Revenue stays ambiguous until a person checks it, so we would add a few definitions and compare answers on ambiguous questions. That tells us whether the product should carry a definitions layer.
[Point: Row 2]
Second, targeted table recovery. On 128 questions a needed table is missed. We would report gains on those and losses on the other 1,094, to see whether recovery can keep its gains without losing other answers.
[Point: Row 3]
Third, new large schemas. The gain comes from 2 of 4 databases, so we would test databases outside these four, one by one, to see whether top 6 stays the default at every size.
[Point: Row 4]
Fourth, a hosted model. All results use one local model. Running the same suites would show whether a hosted model is worth sending it the prompt.
Reference — not read aloud
All accuracy figures use one local model and this project's comparison, not a leaderboard. Broader value hints would need a data-boundary decision first. The decision column states proposals, not results.

## Slide 17 — Close

The contribution is an inspectable SQL application and an evaluation record that makes its tradeoffs visible.
[Point: Inspectable SQL, measured tradeoffs and a clear next experiment]
The current default keeps table selection because it improved the large-schema comparison. Answer accuracy remains limited, and better retrieval alone has not established a further gain.
[Point: Live demo]
The demo shows the interaction; the repository contains the code, runs and decisions behind the claims.
This began as a UTS group project with Huy Duc Vu, Ngoc Bao Tran Nguyen and Nguyen Nghia Doan Dang, and I have refined it since. Thank you.

Reference — not read aloud
Close. Origin: UTS AT3 group project, May 2026 (docs/academic/). Refinement since then on tuannm3812/main-refinement.

## Slide 18 — Backup: schema RAG

This is a backup slide for questions about step three of the architecture: how tables are selected.
[Point: Three steps at the top, marker 1]
First the question's words are widened with synonyms, so revenue also searches amount, sales and total. A business word can reach columns it never names.
[Point: Step 2, marker 3]
Then every table gets a relevance score from its names, keywords, trigrams and value hints. Only schema text and those short value lists are scored. Full rows are never searched, and no model is called.
[Point: The bars and the cut]
These are the real scores for the demo question. The top six are kept. products is the clear winner, but the last six tables all sit below two, so the cut can be close: suppliers made it at 1.7 and marketing campaigns missed at 1.6.
[Point: Amber bars, marker 2]
Foreign-key neighbours are added next. orders ranks tenth, yet it arrives because a foreign key links it to order_items. That matters: slide 7 showed the benchmark's answer needs orders.
[Point: Ticks]
Nine tables reached the model, and its SQL used two of them, marked with the ticks.
Reference — not read aloud
Scores from rag.rank_schema_chunks on data/retail_analytics.db with the default scorer, 6 November. The score has no fixed scale; it only ranks tables for one question. Sent: products, returns, order_items, inventory_snapshots, customer_support_tickets, suppliers, plus orders, stores, customers. Weights in config.py: table 8, embedding 5, column 4, semantic 3, schema BM25 1, value BM25 0.25; dense off. Limit if asked: a name that appears only in rows, such as a person's name, matches nothing, because rows are not searched (evaluation/results/retrieval/README.md).

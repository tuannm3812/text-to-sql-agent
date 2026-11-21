# Presenter notes

## 1. Ask your data.
Inspect the answer.

Open with the one idea of the deck.

This deck is about one idea: ask your data, then inspect the answer. It began as a UTS group project and has since been refined as a portfolio project. The illustration shows what the agent does: it finds the right tables, then lets you look closely at the result.
Reference: cover illustration from make_cover.py in this folder. It is decorative and shows no real data.

References:
- sources.md
- claims-register.md

## 2. Agenda

Show the order of the talk.

The deck follows four questions. [Point: Problem] Why is this hard, and what do other tools do? [Point: Solution] What was built, and how it is controlled. [Point: Evidence] What was measured, including the ideas that did not help. [Point: Next steps] What is still unproven and how to test it.

References:
- sources.md
- claims-register.md

## 3. Inspectable SQL, with measured limits

Give the whole story before the detail.

Here is the whole story before the detail. [Point: 45 of 45] Read-only comes first: generated SQL is validated and run read-only, and all 45 tests passed on three database engines with none skipped.
[Point: 64.6 % and 35.2 %] With a local 9B model, 64.6 % of Spider dev answers and 35.2 % of the harder BIRD dev answers matched, using this project's scorer. These are not leaderboard scores.
[Point: +3.6 points] On databases of 21 to 65 tables, sending the top six tables and their neighbours scored 3.6 points above sending every table with hints, using 69 % fewer prompt tokens. The gain comes from the 65- and 34-table databases.
[Point: not faster] Those smaller prompts took about two seconds longer per answer, because each question gets a different schema and the local model cannot reuse its cache. [Point: takeaway] About one in three Spider answers still did not match, so a person should review results.
Reference: README Evaluation Results, release runs of 10 October 2026 at 7708295; bird_train_large at 47284f5, 19 October 2026. AGENTS.md 4 November 2026: conformance 45 passed, 0 skipped.

References:
- sources.md
- claims-register.md

## 4. A fluent answer can still be the wrong answer

Say why a fluent answer is not enough.

Text-to-SQL turns a question into SQL over a schema and returns rows. Writing the SQL is the easy part. [Point: Meaning] The hard part is what the question means here. A word like revenue is not a column. [Point: Scale] Real schemas are also large: Spider 2.0 databases often exceed 1,000 columns.
[Point: Spider 2.0 bar] In the Spider 2.0 paper, an o1-preview agent solved 21.3 % of enterprise tasks, against 91.2 % on Spider 1.0 and 73.0 % on BIRD. Our local model also falls on the harder test, from 64.6 % to 35.2 %, on our own scorer.
[Point: Risk] The SQL runs on real data, so it must be stopped from changing that data, and a valid query can still answer the wrong question.
Reference: Spider 2.0 paper, arXiv 2411.07763, read 6 November 2026. 91.2 minus 21.3 is 69.9 points. Project scores: README Evaluation Results.

References:
- sources.md
- claims-register.md

## 5. Other tools get business meaning through setup

Place the project among the tools that already exist.

Other tools reach business meaning through setup. [Point: People define the meaning] Snowflake says schemas lack business definitions, so people add them in a semantic view. Databricks has a domain expert curate SQL expressions and example SQL. WrenAI keeps its semantic layer in Git.
[Point: Upkeep column] That work does not end: Snowflake tells teams to refine with evaluations, and Databricks calls curation iterative.
[Point: Systems work it out] Vanna saves past queries and learns from use, though its repository was archived in March 2026. The top BIRD test score is 83.40 %, still below 92.96 % for humans.
[Point: This project] This project only needs a database connection, so it pays in the last column: a person checks what each answer means.
Reference: Snowflake Cortex Analyst docs, Databricks Genie best practices, WrenAI and Vanna repositories, BIRD leaderboard, all read 6 November 2026 (S1 to S5).

References:
- sources.md
- claims-register.md

## 6. Our aim: useful without setup, and checkable by default

State the aim and what it costs.

Our aim has two halves: useful without setup, and checkable by default. [Point: Who it helps] It is for an analyst who knows the question but not the schema, and for a reviewer deciding whether to trust the answer.
[Point: The matrix] Left to right is the setup needed before the first useful answer. Bottom to top is how much business meaning is built in. Curated tools and dashboards sit top right. Top left would be the ideal, which is not yet available.
[Point: This project] This project sits bottom left, a quick start, but above a general chatbot because it uses the real schema and bounded hints. [Point: What we gave up] There are no governed metric definitions, so revenue stays ambiguous until a person checks it.
Reference: docs/1_brief.md; README, What It Does. Placements are qualitative.

References:
- sources.md
- claims-register.md

## 7. The SQL shows which revenue the answer counted

Show the agent answering one question, and why the SQL matters.

[Point: The answer] Asked which product categories generate the most revenue, the local model says Electronics leads with 173,366. It looks complete, but the chart does not say which orders it counted.
[Point: The SQL] The SQL sums price times quantity. It has no status filter and no discounts, so all 220 orders count, including cancelled and returned ones.
[Point: Wording] A separate benchmark question asks for completed order revenue. That counts 179 orders with discounts and gives 136,984, about 21 % lower, with the same top category. This illustrates inspection; it is not a benchmark failure.
Reference: evaluation/cases.json, retail_revenue_by_category; recomputed on data/retail_analytics.db, 6 November 2026.

References:
- sources.md
- claims-register.md

## 8. The model sees the schema and a few stored values, never result rows

Say what the model sees before anyone points it at their own data.

[Point: Structure] For the demo question, the prompt held nine table definitions and 79 stored values. That is 79 of the 608 distinct text values, about 13 %, sent as lists and never linked to a row. Result rows are never sent.
[Point: Hints] The hints are real stored values, such as order status. The limit counts distinct values, not sensitivity. Customer emails stay out only because there are more than twenty of them.
[Point: Model] With a local model, nothing leaves your machine. With a hosted model, the question, schema and hints go to the provider. So review the prompt first, or turn table selection off.
Reference: 608 is the sum of COUNT(DISTINCT) over the 30 text columns; 79 / 608 = 13.0 %; 4,971 schema characters, 1,419 on hint lines.

References:
- sources.md
- claims-register.md

## 9. The model proposes SQL; the application controls execution

Walk one question through the app.

This is the path of one question in four stages, and only one is the model. [Point: Ask and prepare] A person asks in plain English; the application reads the schema, keeps the top six tables and builds the prompt, with no model.
[Point: Generate, marker 1] The model writes one SQL statement, or declines. It never sees result rows. [Point: Check and run, marker 2] Then two gates in code: sqlglot allows one read only, and the engine runs the query read-only with a work budget and a row cap.
[Point: engine band, marker 3] The same flow runs on SQLite, DuckDB and PostgreSQL. [Point: dashed arrow, marker 4] A query error goes back to the model once, and the repair passes the same checks. The full eight-step flow is in the appendix.
Reference: pipeline.answer_question (max_repair_attempts=1); config.py; docs/2_architecture.md. Conformance: 45 tests, 15 per engine, 0 skipped.

References:
- sources.md
- claims-register.md

## 10. Safety does not rest on the model

Show which defence stops which threat.

Safety here does not rest on the model. [Point: Column headers] There are three lines of defence. The first is the model, which declines; in our safety run, 14 of 15 cases ended in its own decline. That is behaviour, and it can change.
[Point: Application and engine] The application check uses sqlglot. For the engine, writes run straight at each one, bypassing the application check, and all three refuse them.
[Point: Lines column] A write meets all three lines. A runaway query or an oversized result meets only the engine. [Point: Would run] A read of engine internals would run if it reached the engine, so the application check is what stops it.
[Point: Last row] Asked for average shipping weight, the model returned average unit cost. That query was valid, so every check passed. No layer checks meaning.
Reference: safety run 2026-10-10T061911, 15 cases; tests/test_engine_conformance.py, 45 tests, 15 per engine; tests/test_safety.py.

References:
- sources.md
- claims-register.md

## 11. Read the interval, not the point

Say why the numbers can be trusted and how to read them.

[Point: Suites] We ran 3,817 questions in five suites, and each answers one question. Spider and BIRD measure accuracy. The large-schema suite tests table selection. Demo and Safety are small diagnostics.
[Point: Method] Results are compared by value and type. Every rate carries a 95 percent bootstrap interval. Each of the 37 recorded runs pins its commit, data, prompt and model.
[Point: Intervals] Here is the one rule for the next slides. Read the interval, not the point. On the top line the whole interval sits above zero, so that change of 3.6 points is measurable. On the second line it crosses zero.
Reference: evaluation/suites (1,034 + 1,534 + 1,222 + 12 + 15 = 3,817); 37 run directories under evaluation/results; stats.py 10,000 resamples, seed 0.

References:
- sources.md
- claims-register.md

## 12. The local model scored 64.6 % on Spider and 35.2 % on BIRD

Give the headline results and how to read them.

[Point: Top chart] Each dot is the share of questions whose result matched the reference, and the line is its 95 percent interval. Spider reached 64.6 percent and BIRD with evidence 35.2 percent.
[Point: Spider panel] Harder questions score lower. Scores fall from 84.3 to 38.0 percent. [Point: BIRD panel] Evidence is a hint the benchmark supplies. Paired on the same questions, it adds 10.1 points.
[Point: Demo suite] Our own demo suite matched 4 of 12, with an interval 50 points wide. A good demo on stage proves little. Turning thinking off added 8.5 points on Spider.
Reference: runs of 10 October 2026 at 7708295. BIRD moderate 29.1 with evidence, 16.3 without; README Evaluation Results.

References:
- sources.md
- claims-register.md

## 13. On large databases, sending fewer tables scored 3.6 points higher

Show the three-sided trade-off of table selection.

[Point: Top panel] Here are three ways to send the schema on the same 1,222 questions. Top 6 plus neighbours is the most accurate at 29.1 percent and uses the fewest prompt tokens, but it is the slowest.
[Point: Middle panel] The gain is concentrated. The 65-table and 34-table databases gain 5 to 6 points, and their intervals sit clear of zero. [Point: Every table + hints] Adding hints to a full schema did not help.
[Point: Bottom panel] This is the real risk. When every needed table was sent, top 6 scored 32.9 percent against 26.7. When a needed table was dropped, on 167 questions, it scored 5.4 against 18.0. Fewer tokens did not mean faster: about 2 seconds longer, because the local model cannot reuse its cache.
Reference: runs of 19 October 2026 at 47284f5. Latency +2.0 s [+1.8, +2.2]. Sources: evaluation/results/bird_train_large/README.md, evaluation/results/retrieval/README.md.

References:
- sources.md
- claims-register.md

## 14. Later trials found trade-offs, not a further accuracy gain

Show what the later trials found.

[Point: Top row, marker 1] Each dot is a trial’s paired change and the line is its 95 percent interval. Sending the best tables is the one clear gain. None of the five later trials added to it.
[Point: Scorer signals] The scorer change sent all needed tables more often, from 1,055 questions to 1,094. Its 0.9 points still spans zero, so better retrieval did not become measurably better answers. We kept it for the retrieval gain.
[Point: Dense embeddings] Dense embeddings helped dropped-table questions, but other answers churned, so the whole suite moved only 0.2 points. [Point: Shared layout] The shared layout cut latency by 58 percent and lost 2.4 points. Both layouts stay opt-in.
Reference: evaluation/results/value_matches, scorer_signals, dense_embeddings, shared_layout.

References:
- sources.md
- claims-register.md

## 15. Better table coverage did not measurably improve accuracy

Explain why better coverage did not become better accuracy.

[Point: Two groups] The later scorer leaves two groups. On 128 questions a needed table was missed, and top 6 got 8 right. On the other 1,094 every needed table was sent.
[Point: Dense embeddings] Each fix helps where it aims. Dense embeddings took those questions from 8 to 26 correct. [Point: Every table] But the other questions pay. Sending every table won 15 answers and lost 44, a net of minus 29.
[Point: Churn] Small prompt changes flip answers: reordering the same tables changed 22 of 480 answers. The groups come from the evaluation, so a live system cannot see them.
Reference: evaluation/results/dense_embeddings, shared_layout, scorer_signals. Baseline 367 of 1,222 (8 + 359).

References:
- sources.md
- claims-register.md

## 16. Four tests would close the main gaps in the evidence

Name the four tests that would close the gaps.

[Point: Row 1] First, business definitions: add a few and compare answers on ambiguous questions. [Point: Row 2] Second, targeted table recovery, reporting gains on the 128 and losses on the 1,094.
[Point: Row 3] Third, new large schemas, because the gain comes from 2 of 4 databases. [Point: Row 4] Fourth, a hosted model, since all results use one local model.
Reference: all accuracy figures use one local model and this project’s comparison.

References:
- sources.md
- claims-register.md

## 17. Sources behind the claims

List where the audience can check the claims.

These are the sources behind every number in the deck.

References:
- sources.md
- claims-register.md

## 18. Inspectable SQL, measured trade-offs and a clear next experiment

Close on the contribution.

The contribution is an inspectable SQL application and an evaluation record that makes its trade-offs visible. The default keeps table selection because it improved the large-schema comparison. Answer accuracy remains limited, and better retrieval alone has not added a gain.
[Point: links] The demo shows the interaction; the repository holds the code, runs and decisions behind every claim. Thank you.

References:
- sources.md
- claims-register.md

## 19. Backup: how the top 6 tables are chosen

Backup for questions about table selection.

[Point: Steps] First the question’s words are widened with synonyms, so revenue also searches amount, sales and total. Then every table gets a relevance score from its names, keywords, trigrams and value hints. No model is called.
[Point: The cut] The top six are kept. suppliers made it at 1.7 and marketing campaigns missed at 1.6. [Point: Neighbours] orders ranks tenth, yet it arrives because a foreign key links it to order_items. Nine tables reached the model, and its SQL used two.
Reference: weights in config.py; dense off.

References:
- sources.md
- claims-register.md

## 20. Backup: one question’s path through the app, stage by stage

Backup for questions about the full flow.

One question passes six stages, top to bottom. Ask and Prepare use no model; Generate is the only model call; Validate and Run are the two gates in code; Show puts the answer and the SQL in front of the person.
Reference: pipeline.answer_question; schema.py; rag.py; llm.py; safety.py; execution.py; engines/; ui/results.py. AGENTS.md 2026-10-19 for the 4 ms retrieval.

References:
- sources.md
- claims-register.md

## 21. Backup: matched means the same rows as the reference

Backup for questions about how accuracy is measured.

An answer counts as matched when its rows equal the reference rows. Columns compare by position, rows as a set unless the reference orders them, numbers across integer and decimal types, and text exactly.
Reference: text_to_sql_agent/evaluation_v2/comparator.py and scoring.py (scorer version 2).

References:
- sources.md
- claims-register.md

## 22. Backup: each engine enforces read-only in its own way

Backup for questions about engine safety.

Each engine enforces read-only in its own way, and every mechanism is load-bearing. SQLite uses a read-only connection, query_only and an authorizer. DuckDB uses its read_only flag plus external access off. PostgreSQL uses a least-privilege role and a read-only transaction.
Reference: text_to_sql_agent/engines/sqlite.py, duckdb.py, postgres.py; docs/0_coding_standards.md; tests/test_engine_conformance.py.

References:
- sources.md
- claims-register.md

## 23. Backup: the technology behind each step

Backup for questions about the stack.

These are the tools behind each step. Nothing is trained; the evaluation harness measures the agent.
Reference: pyproject.toml; ui/connection.py; text_to_sql_agent/llm.py.

References:
- sources.md
- claims-register.md

## 24. Backup: terms used in this deck

Backup glossary.

These are the plain meanings of the terms on the evidence slides.

References:
- sources.md
- claims-register.md

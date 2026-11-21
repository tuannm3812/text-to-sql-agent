# Generated slide brief

Edit brief-content.json, then rebuild.

## 1. Ask your data.
Inspect the answer.

Layout: cover

Reader question: 

Message: Open with the one idea of the deck.

Exact face text:

- 36121 ARTIFICIAL INTELLIGENCE PRINCIPLES AND APPLICATIONS | CAPSTONE PROJECT
- Ask your data. / Inspect the answer.
- A text-to-SQL agent that writes read-only SQL, shows its work and measures where it fails
- Manh Tuan (Mike) Nguyen
- TD School, University of Technology Sydney
- November 2026

## 2. Agenda

Layout: agenda

Reader question: 

Message: Show the order of the talk.

Exact face text:

- Text-to-SQL Agent
- 2
- Agenda
- 1
- Problem
- 3
- Summary
- 4
- Why it is hard
- 5
- Other tools
- 6
- Our aim
- 2
- Solution
- 7
- Demo
- 8
- Data boundary
- 9
- Architecture
- 10
- Safety
- 3
- Evidence
- 11
- Method
- 12
- Benchmarks
- 13
- Large schemas
- 14–15
- Trials and retrieval
- 4
- Next steps
- 16
- Next tests
- 17
- Sources

## 3. Inspectable SQL, with measured limits

Layout: summary_page

Reader question: 

Message: Inspectable and read-only, but **a person should still review** each answer.

Exact face text:

- 1
- 2
- 3
- 4
- PROBLEM
- Executive summary
- Inspectable SQL, with measured limits
- What the agent does, how well it did, and what to keep in mind
- Text-to-SQL Agent
- 3
- Read-only / checks
- 45 of 45
- tests passed, none skipped, on 3 / database engines
- Read-only, not proof of right / answers.
- Spider
- 64.6 %
- of answers matched¹: common / test, local 9B model
- Our scorer, not the leaderboard.
- BIRD
- 35.2 %
- of answers matched: harder test, / with evidence hints
- One local model only.
- Large / databases
- +3.6 pts
- from choosing tables [+1.4, +5.8]
- From 2 of 4 databases.
- Large databases: more correct answers from less context²
- Answers matched
- Every table + hints
- 25.5 %
- Top 6 tables
- 29.1 %
- Sending only the most relevant tables scored 3.6 points higher.
- Prompt size, every table = 100
- Every table + hints
- 100
- Top 6 tables
- 31
- The prompt was 69 % smaller, but each answer took about two seconds / longer.
- Note: ¹ This project’s result comparison, not leaderboard scoring; Spider (Yu et al., 2018) and BIRD (Li et al., 2023). ² 1,222 BIRD train questions on 4 databases of 21 to 65 / tables.
- TAKEAWAY
- Inspectable and read-only, but a person / should still review each answer.
- 1
- 1
- Read-only is not the same as right
- The controls limit what can run. They do not show / the answer is correct.
- 2
- 2
- Selection helps at scale
- The gain comes from the 65- and 34-table / databases. It is not a universal result.
- 3
- 3
- Judge the whole answer
- About one in three Spider answers still did not / match.
- 4
- 4
- Smaller prompts are not faster here
- Each question gets a different schema, so the local / model cannot reuse its cache.

## 4. A fluent answer can still be the wrong answer

Layout: hard_page

Reader question: 

Message: Published scores fall about 70 points on enterprise tasks, so a good demo is not evidence.

Exact face text:

- 1
- 2
- 3
- 4
- PROBLEM
- Why it is hard
- A fluent answer can still be the wrong answer
- Text-to-SQL turns a question into SQL over a schema, then returns rows; each step can go wrong
- Text-to-SQL Agent
- 4
- Question
- What the person asks
- Schema
- Tables and columns
- SQL
- The generated query
- Rows
- The answer returned
- Published scores fall on enterprise tasks
- Spider 1.0
- 91.2 %
- BIRD
- 73.0 %
- Spider 2.0 enterprise
- 21.3 %
- 69.9 points below Spider 1.0
- Source: share of tasks solved by an o1-preview agent, as reported in the Spider 2.0 paper (2024); not this project's results.
- This project, for comparison: 64.6 % on Spider dev and 35.2 % on BIRD dev, local 9B model, our own scorer; not comparable with the bars above.
- Meaning
- Words like “revenue” are not / columns. Gross or net? The schema / does not say.
- Scale
- Real schemas are large. Spider 2.0 / databases often exceed 1,000 / columns.
- Risk
- Generated SQL runs on real data, so / it must be stopped from changing it.
- TAKEAWAY
- Published scores fall about 70 points on / enterprise tasks, so a good demo is not / evidence.
- 1
- 1
- SQL is the easy part
- The hard part is knowing what the question means / in this database.
- 2
- 2
- We see the same direction
- Spider 2.0 sits 69.9 points below Spider 1.0. Our / model also falls on the harder test, from 64.6 % on / Spider to 35.2 % on BIRD, using our own scorer.
- 3
- 3
- Keep a person in the loop
- A valid query can still answer the wrong question. / Dashboards and analyst SQL remain best for / defined, recurring metrics.

## 5. Other tools get business meaning through setup

Layout: tools_page

Reader question: 

Message: Other tools pay for meaning in setup and upkeep. **This project pays in review**: a person checks what each answer means.

Exact face text:

- 1
- 2
- 3
- 4
- PROBLEM
- Other tools
- Other tools get business meaning through setup
- Two routes to meaning, compared on the same criteria; sources read 6 November 2026
- Text-to-SQL Agent
- 5
- EFFORT
- High
- Moderate
- Low
- None
- APPROACH
- SOURCE OF MEANING
- SETUP¹
- UPKEEP¹
- BEST FOR
- RISK
- PEOPLE DEFINE THE MEANING
- Snowflake Cortex Analyst
- Semantic view
- Define the view
- Refine with evaluations
- Agreed metrics
- Teams already on Snowflake
- Stale definitions
- Upkeep as metrics change
- Databricks Genie Agents
- SQL expressions, example / SQL
- Expert curation
- Iterate with feedback
- One topic and audience
- Curated example SQL
- Depends on the curator
- Advises five or fewer tables
- WrenAI
- Semantic layer in Git
- Define the MDL model
- Review in Git
- Versioned definitions
- Open-source engine
- Unmodelled data
- Some features commercial
- SYSTEMS WORK IT OUT
- Vanna
- Saved past queries
- Learns from use
- Self-maintained
- Repeated questions
- Learns from saved queries
- Repeats past errors
- Repository archived³
- BIRD leaderboard systems
- Mostly not listed
- Not listed
- Not listed
- Benchmark scores
- Top test entry 83.40 %²
- Transfer unproven
- Methods rarely listed
- This project
- Schema and bounded hints
- Connect only
- None
- A first look at a database
- SQL shown, run read-only
- A person checks the meaning
- No governed metrics
- Note: ¹ Setup and upkeep are our reading of each tool’s documentation, read 6 November 2026, not a ranking. ² AskData, the top BIRD test entry; humans score 92.96 %. ³ Archived on 29 March 2026.
- TAKEAWAY
- Other tools pay for meaning in setup and upkeep. This project pays in review: a person checks what each answer means.

## 6. Our aim: useful without setup, and checkable by default

Layout: aim_page

Reader question: 

Message: A quick start that **people check**, not a governed metrics layer.

Exact face text:

- 1
- 2
- 3
- 4
- PROBLEM
- Our aim
- Our aim: useful without setup, and checkable by default
- A narrower tool: no curated semantic model, with the checking in the user’s hands
- Text-to-SQL Agent
- 6
- Useful without setup
- Connect a database and ask a question.
- Checkable by default
- SQL shown, validated and run read-only.
- Not yet available.
- MEANING WITHOUT SETUP: THE IDEAL
- MEANING THROUGH SETUP: CURATED TOOLS
- QUICK START: PEOPLE CHECK THE MEANING
- Effort spent, but meaning still left to the reader.
- SETUP WITHOUT MEANING: TO AVOID
- Setup before the first useful answer¹ →
- ↑ Business meaning built in
- BI dashboards
- Databricks Genie Agents
- Snowflake Cortex Analyst
- WrenAI
- Vanna
- This project
- General chatbot
- TAKEAWAY
- A quick start that people check, not a / governed metrics layer.
- 1
- 1
- Who it helps
- An analyst who knows the question but not the / schema, and a reviewer deciding whether to trust / the answer.
- 2
- 2
- What we chose
- A quick start that uses the real schema and / bounded hints. Query-result rows are never sent to / the model.
- 3
- 3
- What we gave up
- No governed metric definitions, so a word like / revenue stays ambiguous until a person checks it. If / metrics must match across teams, choose a / curated tool.

## 7. The SQL shows which revenue the answer counted

Layout: demo_page

Reader question: 

Message: Neither figure is wrong. The question did not say which revenue, so **a person decides**.

Exact face text:

- 1
- 2
- 3
- 4
- SOLUTION
- Demo
- The SQL shows which revenue the answer counted
- One revenue question on the retail demo, answered by the local 9B model
- Text-to-SQL Agent
- 7
- Try it live
- aipa-text-to-sql-agent.streamlit.app: the same question on / the same demo database
- THE SQL, AND WHAT COMPLETED REVENUE ADDS²
- SELECT category, SUM(unit_price * quantity
- +   * (1 - discount_pct)
-   ) AS total_revenue
- FROM order_items oi
- JOIN products p
-   ON oi.product_id = p.product_id
- + JOIN orders o ON oi.order_id = o.order_id
- + WHERE o.order_status = 'Completed'
- GROUP BY category
- ORDER BY total_revenue DESC;
- Same top category, two definitions of revenue¹
- All 220 orders, list price
- 173,366
- 179 completed, after discounts
- 136,984
- 21 % lower
- Note: ¹ Electronics revenue, recomputed on data/retail_analytics.db; this illustrates inspection, not a benchmark failure. ² Lines marked + are added by the benchmark’s / completed-revenue question.
- TAKEAWAY
- Neither figure is wrong. The question did / not say which revenue, so a person / decides.
- 1
- 1
- The answer looks finished
- Electronics leads with 173,366, but the chart does / not say which orders it counted.
- 2
- 2
- The SQL shows the choice
- Price times quantity, no status filter and no / discounts, so all 220 orders count.
- 3
- 3
- Wording changes the number
- Completed orders after discounts give 136,984, / about 21 % lower, with the same top category.

## 8. The model sees the schema and a few stored values, never result rows

Layout: boundary_page

Reader question: 

Message: Before using real data, **check what the prompt contains** and where it goes.

Exact face text:

- 1
- 2
- 3
- 4
- SOLUTION
- Data boundary
- The model sees the schema and a few stored values, never result rows
- What the prompt held for the demo question on the retail database
- Text-to-SQL Agent
- 8
- 79 of the 608 stored text values reach the prompt¹
- Each square is one distinct stored text value across the database’s 30 text columns: 79 sent as lists, never linked to a row; 529 not sent.
- FROM THE REAL PROMPT (SHORTENED)²
- CREATE TABLE orders (
-   order_id INTEGER PRIMARY KEY,
-   order_status TEXT NOT NULL ...
- );
- -- order_status sample values:
-      Completed, Returned, Cancelled
- -- gender sample values: Female, Other, Male
- ### User question
- Which product categories generate the most revenue?
- IN THE PROMPT
- Tables, columns, keys
- 79 stored values as hints
- The question
- NOT IN THE PROMPT
- Result rows
- Names and emails: over the limit
- All other stored values
- Local model
- The prompt stays on your machine.
- Hosted model
- Question, schema and hints go to the provider.
- Note: ¹ Counted for this question on data/retail_analytics.db; it varies by question. Numeric columns send no values. ² Hint lines in green.
- TAKEAWAY
- Before using real data, check what the / prompt contains and where it goes.
- 1
- 1
- The prompt is mostly structure
- About 71 % of the schema text is table definitions; / hints are the rest.
- 2
- 2
- Hints are real stored values
- Up to 6 values from columns with at most 20 / distinct values. The limit counts values, not / sensitivity.
- 3
- 3
- The model choice moves the boundary
- With a local model nothing leaves the machine. A / hosted model receives the whole prompt.
- 4
- 4
- Check before real data
- Review which columns qualify, or turn table / selection off to send no hints.

## 9. The model proposes SQL; the application controls execution

Layout: arch_summary

Reader question: 

Message: One stage uses a model; **the application decides** what runs.

Exact face text:

- 1
- 2
- 3
- 4
- SOLUTION
- Architecture
- The model proposes SQL; the application controls execution
- One question’s path through the app, in four stages; the full eight-step flow is in the appendix
- Text-to-SQL Agent
- 9
- App step, no model
- The model: behaviour
- Enforced in code
- Ask and / prepare
- A plain question. The app reads / the schema, keeps the top 6 / tables and builds the prompt.
- Generate
- Gemini or Ollama writes one / SQL statement, or declines. It / never sees result rows.
- Check and run
- sqlglot allows one read only; the / engine runs it read-only with a / budget and a row cap.
- Answer
- The answer, table, chart, the / SQL and why those tables, for / the person to inspect.
- One repair try on a query error
- Database engine
- Set by the connection string; read-only on all three.
- SQLite
- DuckDB
- PostgreSQL
- The person asks first and inspects last: the SQL is always shown with the answer.
- TAKEAWAY
- One stage uses a model; the application / decides what runs.
- 1
- 1
- Only one stage is a model
- It returns text and never sees result rows.
- 2
- 2
- Two gates, both in code
- sqlglot, then a read-only engine. Neither checks / meaning.
- 3
- 3
- One flow, three engines
- Each passes the same 15 conformance tests.
- 4
- 4
- One repair try
- The repaired query passes the same checks; / nothing skips a gate.

## 10. Safety does not rest on the model

Layout: table_page

Reader question: 

Message: Writes meet three lines of defence. **A wrong meaning meets none**, so the person is the last check.

Exact face text:

- 1
- 2
- 3
- 4
- SOLUTION
- Safety
- Safety does not rest on the model
- Three lines of defence stop different threats, and each is tested on its own
- Text-to-SQL Agent
- 10
- Stops it
- Does not stop it
- Threat, with an example
- 1 Model declines¹
- 2 Application check
- 3 Engine, read-only
- Lines of defence
- Stopped in code by the application or the engine
- Write or schema change  DROP TABLE students
- Declined 6 of 6
- Blocked
- Denied on 3 engines
- 3 LINES
- Engine internals  SELECT * FROM sqlite_master
- Declined 3 of 3
- Blocked
- Would run
- 2 LINES
- Files on disk  read_csv('local.csv')
- –
- Blocked
- Denied
- 2 LINES
- Runaway query  a cross join of large tables
- –
- –
- Stopped by work budget
- 1 LINE
- Oversized result  more rows than the cap
- –
- –
- Cut at 1,000 rows
- 1 LINE
- Only the model declines
- Data the schema lacks  each patient’s blood type
- Declined 5 of 6
- –
- –
- 1 LINE
- The limit: no layer checks meaning
- Wrong meaning  average shipping weight
- Returned average unit cost
- Passed: valid read
- Ran
- NONE
- Note: ⁠¹ The model’s decline is behaviour and can change with the model or prompt: 14 of 15 safety cases ended in its own decline. The other two columns are enforced in code and tested on their own.
- TAKEAWAY
- Writes meet three lines of defence. A wrong meaning meets none, so the person is the last check.

## 11. Read the interval, not the point

Layout: bars_page

Reader question: 

Message: A change counts only when its **whole interval sits clear of zero**.

Exact face text:

- 1
- 2
- 3
- 4
- EVIDENCE
- Method
- Read the interval, not the point
- 3,817 questions in five suites, 37 recorded runs, each change paired against a named baseline
- Text-to-SQL Agent
- 11
- Questions per suite
- Spider dev
- BIRD dev
- Large schemas
- Demo
- Safety
- How to read a paired change, accuracy points¹
- Top 6 vs every table + hints
- Shared + summaries vs shared
- 1,034  accuracy
- 1,534  accuracy
- 1,222  table selection
- 12  behaviour
- 15  behaviour
- +3.6  [+1.4, +5.8]
- +0.2  [−1.5, +2.0]
- Note: ¹ Results are compared by value and type, so the SQL’s wording does not matter. Intervals are 95 % paired bootstrap, 10,000 resamples. Not leaderboard scoring.
- TAKEAWAY
- A change counts only when its whole / interval sits clear of zero.
- 1
- 1
- Each suite answers one question
- Spider and BIRD measure accuracy. The / large-schema suite tests table selection, because / the dev databases have at most 14 tables.
- 2
- 2
- Small suites show behaviour
- With 12 and 15 cases, Demo and Safety have / intervals too wide to measure accuracy.
- 3
- 3
- Measurable, or not
- The top change of 3.6 points sits above zero. The / second crosses zero, so we cannot say it did / anything.

## 12. The local model scored 64.6 % on Spider and 35.2 % on BIRD

Layout: bars_page

Reader question: 

Message: Harder questions score lower, and **a good demo proves little**.

Exact face text:

- 1
- 2
- 3
- 4
- EVIDENCE
- Benchmarks
- The local model scored 64.6 % on Spider and 35.2 % on BIRD
- Share of answers that matched the reference; one local 9B model, runs of 10 October 2026
- Text-to-SQL Agent
- 12
- Overall, with 95 % interval
- Spider dev
- BIRD dev, with evidence
- Demo suite, 4 of 12
- Spider by difficulty
- Easy
- Medium
- Hard
- Extra hard
- BIRD by difficulty, with and without evidence
- Simple
- Simple, no evidence
- Challenging
- Challenging, no evidence
- 64.6 %  [61.6 %, 67.5 %]
- 35.2 %  [32.9 %, 37.6 %]
- 4 of 12, interval 50 points wide
- 84.3 %
- 65.9 %
- 58.6 %
- 38.0 %
- 43.1 %
- 34.2 %
- 17.3 %
- 8.2 %
- Source: release runs at 7708295, qwen3.5 9B; this project’s scorer, not leaderboard scores. Spider 1,034 and BIRD 1,534 questions.
- TAKEAWAY
- Harder questions score lower, and a / good demo proves little.
- 1
- 1
- Harder questions score lower
- Spider sets the level from how many SQL parts a / query needs. Scores fall from 84.3 % to 38.0 %.
- 2
- 2
- Evidence hints help
- Paired on the same questions, BIRD’s evidence / hints add 10.1 points, at every level.
- 3
- 3
- The demo suite is too small
- It matched 4 of 12. Turning model thinking off / added 8.5 points on Spider, by not running out of / output.

## 13. On large databases, sending fewer tables scored 3.6 points higher

Layout: bars_page

Reader question: 

Message: +3.6 points [+1.4, +5.8] with **69 % fewer tokens**, but about 2 s slower per answer.

Exact face text:

- 1
- 2
- 3
- 4
- EVIDENCE
- Large schemas
- On large databases, sending fewer tables scored 3.6 points higher
- 1,222 BIRD train questions on 4 databases of 21 to 65 tables; runs of 19 October 2026
- Text-to-SQL Agent
- 13
- Answers matched, by schema sent
- Every table + hints
- Every table, no hints
- Top 6 + neighbours
- Top 6 against every table + hints, by database size, points
- 65 tables, 464 questions
- 34 tables, 293 questions
- 22 tables, 207 questions
- 21 tables, 258 questions
- When a needed table is dropped
- All sent, top 6
- All sent, every table
- Table dropped, top 6
- Table dropped, every table
- 25.5 %  8,501 tokens, 4.0 s
- 26.8 %  6,221 tokens, 4.2 s
- 29.1 %  2,670 tokens, 6.0 s
- +5.6  [+1.7, +9.5]
- +6.1  [+2.0, +10.6]
- −2.4  [−6.8, +1.9]
- +1.9  [−3.1, +7.0]
- 32.9 %  on 1,055 questions
- 26.7 %
- 5.4 %  on 167 questions
- 18.0 %
- Source: evaluation/results/bird_train_large at 47284f5. Paired 95 % intervals; the dropped-table split is observed, not causal.
- TAKEAWAY
- +3.6 points [+1.4, +5.8] with 69 % fewer / tokens, but about 2 s slower per answer.
- 1
- 1
- The gain is concentrated
- The 65- and 34-table databases gain 5 to 6 points. / The two smaller ones cross zero.
- 2
- 2
- Hints on a full schema did not help
- About half the values the questions need sit in / columns too large to hint.
- 3
- 3
- Dropping a table is the real risk
- Top 6 scored 5.4 % against 18.0 % when a needed / table was dropped. Selection stays the default for / its overall gain.

## 14. Later trials found trade-offs, not a further accuracy gain

Layout: table_page

Reader question: 

Message: Table selection is the **one clear gain**. Five later trials traded speed or recall, not accuracy.

Exact face text:

- 1
- 2
- 3
- 4
- EVIDENCE
- Trials
- Later trials found trade-offs, not a further accuracy gain
- 1,222 large-schema questions; paired change against each row’s own baseline
- Text-to-SQL Agent
- 14
- Trial
- Change, and its baseline
- Accuracy points¹
- Side effect
- Decision
- Top 6 + neighbours
- Send the best tables, vs every table + hints
- +3.6 [+1.4, +5.8]
- 69 % fewer tokens, 2 s slower
- DEFAULT
- Question value matching
- Add stored values the question names, vs top 6
- +0.4 [−0.9, +1.6]
- Reads row data at question time
- OFF
- Scorer signals
- Weight hints down, match plurals, vs top 6
- +0.9 [−0.7, +2.4]
- All needed tables sent: 1,055 to 1,094
- KEPT
- Dense embeddings
- Add sentence embeddings, vs the kept scorer
- +0.2 [−1.6, +2.0]
- All needed tables sent: 1,094 to 1,148
- OFF
- Shared layout
- Send every table, name the top 6, vs top 6
- −2.4 [−4.6, −0.2]
- 58 % faster, 3 times the tokens
- OPT-IN
- Shared plus summaries
- Also list their columns, vs top 6, not controlled
- −2.1 [−4.3, +0.0]
- Same speed as shared
- OPT-IN
- Note: ⁠¹ Paired 95 % intervals. Only the first row’s interval sits clear of zero above it; the shared layout’s sits clear below it. The others cross zero.
- TAKEAWAY
- Table selection is the one clear gain. Five later trials traded speed or recall, not accuracy.

## 15. Better table coverage did not measurably improve accuracy

Layout: bars_page

Reader question: 

Message: Each fix helps where it aims, and **the other questions pay**.

Exact face text:

- 1
- 2
- 3
- 4
- EVIDENCE
- Retrieval
- Better table coverage did not measurably improve accuracy
- Correct answers gained and lost by each fix against selected tables, on 1,222 questions
- Text-to-SQL Agent
- 15
- Dense embeddings: net +2 answers¹
- Gained
- Lost
- Every table, shared layout: net −29 answers
- Gained
- Lost
- Shared plus summaries: net −26 answers
- Gained
- Lost
- +18
- −16
- +15
- −44
- +13
- −39
- Note: ¹ Gained and lost are net changes per group, not flip counts. Baseline: selected tables with the kept scorer, 8 of 128 and 359 of 1,094 correct.
- TAKEAWAY
- Each fix helps where it aims, and the / other questions pay.
- 1
- 1
- Fixes help where they aim
- Dense embeddings took the missed-table / questions from 8 to 26 correct.
- 2
- 2
- The other questions pay
- Sending every table won 15 answers and lost 44. / Even reordering the same tables changed 22 of / 480 answers.
- 3
- 3
- A live system cannot see the groups
- The next test is targeted recovery: recover missed / tables only where needed, and report both groups.

## 16. Four tests would close the main gaps in the evidence

Layout: table_page

Reader question: 

Message: Measure first, then **change a default only on evidence**.

Exact face text:

- 1
- 2
- 3
- 4
- NEXT STEPS
- Next tests
- Four tests would close the main gaps in the evidence
- Each needs a measured outcome before any default changes
- Text-to-SQL Agent
- 16
- Test
- Why it is needed
- What we would measure
- What it decides¹
- 1  Business definitions
- Revenue stays ambiguous until a person checks it.
- Answers on ambiguous questions, with and / without a few definitions.
- Whether to carry a definitions layer.
- 2  Targeted table recovery
- On 128 questions a needed table is missed.
- Gains on those, and losses on the other 1,094.
- Whether recovery keeps its gains.
- 3  New large schemas
- The gain comes from 2 of 4 databases.
- Top 6 on databases outside these four, one by / one.
- Whether top 6 stays the default at every / size.
- 4  A hosted model
- All results use one local model.
- The same suites on a hosted model.
- Whether it is worth sending it the prompt.
- Note: ⁠¹ Proposals, not results. Broader value hints would need a data-boundary decision first.
- TAKEAWAY
- Measure first, then change a default only on evidence.

## 17. Sources behind the claims

Layout: references

Reader question: 

Message: List where the audience can check the claims.

Exact face text:

- 1
- 2
- 3
- 4
- NEXT STEPS
- Sources
- Sources behind the claims
- Every number traces to the repository or to a source read on the date given
- Text-to-SQL Agent
- 17
- Repository: README Evaluation Results; large-schema and retrieval results
- Spider: Yu et al. (2018), EMNLP, arXiv 1809.08887
- BIRD: Li et al. (2023), NeurIPS, arXiv 2305.03111; leaderboard read 6 November 2026
- Spider 2.0: Lei et al. (2024), arXiv 2411.07763 (read 6 November 2026)
- Snowflake Cortex Analyst documentation (read 6 November 2026)
- Databricks Genie best practices (read 6 November 2026)
- WrenAI and Vanna repositories; Vanna archived 29 March 2026 (read 6 November 2026)

## 18. Inspectable SQL, measured trade-offs and a clear next experiment

Layout: close_page

Reader question: 

Message: Close on the contribution.

Exact face text:

- THANK YOU
- Inspectable SQL, measured trade-offs / and a clear next experiment
- Questions and feedback are welcome.
- Live demo
- aipa-text-to-sql-agent.streamlit.app
- Code and runs
- github.com/tuannm3812/text-to-sql-agent
- Manh Tuan (Mike) Nguyen
- TD School, University of Technology Sydney  ·  November 2026

## 19. Backup: how the top 6 tables are chosen

Layout: bars_page

Reader question: 

Message: 9 tables reached the model; its SQL used 2. **No rows are searched and no model is called.**

Exact face text:

- APPENDIX
- Schema RAG
- Backup: how the top 6 tables are chosen
- Relevance score by table for: Which product categories generate the most revenue?
- Text-to-SQL Agent
- 19
- Top 6, sent
- Foreign-key neighbour, added
- Not sent
- Score, no fixed scale; it only ranks tables for one question
- products
- returns
- order_items
- inventory_snapshots
- customer_support_tickets
- suppliers
- marketing_campaigns
- customers
- regions
- orders
- stores
- 30.1  used by the SQL
- 11.7
- 9.9  used by the SQL
- 9.8
- 5.8
- 1.7
- 1.6
- 1.4
- 1.3
- 1.3
- 1.3
- Source: rag.rank_schema_chunks on data/retail_analytics.db with the default scorer, 6 November 2026.
- TAKEAWAY
- 9 tables reached the model; its SQL used / 2. No rows are searched and no model / is called.
- 1
- 1
- The cut can be close
- Words are widened with synonyms, then each / table is scored from names, keywords, trigrams / and value hints. suppliers made it at 1.7; marketing / campaigns missed at 1.6.
- 2
- 2
- Neighbours are added
- orders ranks tenth, yet arrives through a foreign / key from order_items. The benchmark’s answer / needs it.

## 20. Backup: one question’s path through the app, as a flowchart

Layout: flow_page

Reader question: 

Message: Backup for questions about the full flow.

Exact face text:

- APPENDIX
- Full flow
- Backup: one question’s path through the app, as a flowchart
- 
- Text-to-SQL Agent
- 20

## 21. Backup: matched means the same rows as the reference

Layout: table_page

Reader question: 

Message: Matched means **the same rows**, not similar SQL.

Exact face text:

- APPENDIX
- How answers are scored
- Backup: matched means the same rows as the reference
- The project’s own result comparison, used for every accuracy figure in this deck
- Text-to-SQL Agent
- 21
- How two result sets are compared
- Part
- Rule
- Why
- Columns
- Same number of columns, compared by position; names do not matter.
- The SQL’s aliases are free.
- Rows
- Compared as a set with repeats, matched one to one. Order counts only when the / reference SQL ends in ORDER BY.
- Row order is not part of the answer unless asked.
- Numbers
- Equal across integer and decimal types; otherwise within one part in a million.
- 1 and 1.0 are the same answer.
- Text and NULL
- Text matches exactly after trimming and never equals a number. NULL equals only / NULL.
- No loose string matching.
- What each outcome means¹
- Outcome
- When
- Counts as
- Correct
- Rows match the reference, or a request that should be refused was refused.
- Matched
- Wrong, refused, / unanswerable or error
- Rows differ, a safe question was blocked or declined, or the SQL failed or came back / empty.
- Not matched
- Note: ⁠¹ This is not the Spider or BIRD leaderboard scorer, so scores are not comparable with published ones. An empty answer is an error, never a correct refusal.
- TAKEAWAY
- Matched means the same rows, not similar SQL.

## 22. Backup: each engine enforces read-only in its own way

Layout: table_page

Reader question: 

Message: Read-only is **enforced by each engine**, not assumed from the application check.

Exact face text:

- APPENDIX
- Read-only per engine
- Backup: each engine enforces read-only in its own way
- The engine layer of the safety slide; each mechanism is required, not optional
- Text-to-SQL Agent
- 22
- Engine¹
- Writes refused by
- Files and internals
- Work budget
- SQLite
- A read-only connection, query_only on, and an authorizer that / denies every write action.
- The authorizer also denies ATTACH, so other files / cannot be opened.
- 100,000 virtual-machine steps, then the query / stops.
- DuckDB
- The read_only connect flag, which protects the database file.
- External access off, so read_csv and other file / readers are refused.
- 5,000 ms, then the query stops.
- PostgreSQL
- A least-privilege role and a read-only transaction, each enough / on its own.
- A superuser or file-reading role is refused at / connect.
- 5,000 ms, then the query stops.
- Note: ⁠¹ All three pass the same 15 conformance tests, 45 in all, none skipped. Every engine also caps results at 1,000 rows.
- TAKEAWAY
- Read-only is enforced by each engine, not assumed from the application check.

## 23. Backup: the technology behind each step

Layout: stack_page

Reader question: 

Message: No model is trained: the app **wraps an existing model** with checks around it.

Exact face text:

- APPENDIX
- Technology
- Backup: the technology behind each step
- Open-source tools, plus a hosted model only when the user picks one
- Text-to-SQL Agent
- 23
- APP
- Streamlit
- The question box, answer, chart and SQL
- pandas
- Result tables and CSV uploads
- MODEL
- Ollama
- A local model; nothing leaves the machine
- Gemini
- A hosted model, when chosen
- LangChain
- The Ollama client
- CHECKS
- sqlglot
- Parses the SQL and refuses anything but one read
- Python
- Table selection, prompts and the evaluation harness
- ENGINES
- SQLite
- The demo databases and uploaded files
- DuckDB
- Analytical files, read-only
- PostgreSQL
- A live server, through a least-privilege role
- TAKEAWAY
- No model is trained: the app wraps an existing model with checks around it.

## 24. Backup: terms used in this deck

Layout: table_page

Reader question: 

Message: Backup glossary.

Exact face text:

- APPENDIX
- Glossary
- Backup: terms used in this deck
- Plain meanings for the words on the evidence slides
- Text-to-SQL Agent
- 24
- Term
- Meaning
- Where it appears
- Schema
- The tables, columns and keys of a database, without its rows.
- Why it is hard, data boundary
- Value hints
- Up to 6 stored values from text columns with at most 20 distinct values, sent with the schema.
- Data boundary, large schemas
- Top 6 + neighbours
- The six most relevant tables for a question, plus tables one foreign key away.
- Architecture, large schemas
- Every table + hints
- The whole schema with value hints; the baseline for table selection.
- Large schemas, trials
- Evidence hints
- BIRD’s own note for each question, such as which column a phrase refers to.
- Benchmarks
- Paired change
- The difference between two settings on the same questions, in accuracy points.
- Method, trials
- 95 % interval
- The range the change could plausibly take; measurable when it sits clear of zero.
- Method onwards
- Conformance tests
- The same 15 read-only tests run on each engine, none skipped.
- Summary, safety

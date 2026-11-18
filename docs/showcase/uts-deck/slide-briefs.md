# Generated slide brief

Edit brief-content.json, then rebuild.

## 1. Ask your data. Inspect the answer.

Layout: cover

Reader question: 

Message: Open with the one idea of the deck.

Exact face text:

- 36121 ARTIFICIAL INTELLIGENCE PRINCIPLES AND APPLICATIONS | CAPSTONE PROJECT
- Ask your data. Inspect the / answer.
- A text-to-SQL agent that writes read-only SQL from a plain question, shows its work, and / measures where it fails
- Manh Tuan Nguyen
- University of Technology Sydney
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

Layout: research_summary

Reader question: 

Message: About one answer in three still did not match on Spider, so a person should review results.

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
- The problem
- People need answers from databases without writing SQL, but a fluent answer can still be / wrong.
- The approach
- An agent picks the relevant tables, writes SQL that runs read-only, and shows it with the rows.
- Read-only holds: 45 of 45
- Safety tests passed on 3 database engines, none skipped.
- 64.6 % on Spider, 35.2 % on BIRD
- Answers matched on a local 9B model, with this project's scorer, not leaderboard scoring.
- +3.6 points on large databases
- Sending the top 6 tables beat every table with hints [+1.4, +5.8], with a 69 % smaller / prompt.
- Smaller prompts were not faster
- Each answer took about 2 s longer, because the local model could not reuse its cache.
- TAKEAWAY
- About one answer in three still did not match on Spider, so a person should review results.

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
- SETUP
- UPKEEP
- BEST FOR
- RISK
- PEOPLE DEFINE THE MEANING
- Snowflake Cortex Analyst
- Semantic view
- Define the view
- Refine with evaluations
- Agreed metrics
- Stale definitions
- Databricks Genie Agents
- SQL expressions, example SQL
- Expert curation
- Iterate with feedback
- One topic and audience
- Depends on the curator
- WrenAI
- Semantic layer in Git
- Define the MDL model
- Review in Git
- Versioned definitions
- Unmodelled data
- SYSTEMS WORK IT OUT
- Vanna
- Saved past queries
- Learns from use
- Self-maintained
- Repeated questions
- Repeats past errors
- BIRD leaderboard systems
- Mostly not listed
- Not listed
- Not listed
- Benchmark scores
- Transfer unproven
- THIS PROJECT
- This project
- Schema and bounded hints
- Connect only
- None
- A first look
- A person checks the / meaning
- Note: Setup and upkeep are our reading of each tool’s documentation, not a ranking. Vanna’s repository was archived on 29 March 2026. The top BIRD test entry, AskData, scores 83.40 %, below 92.96 % for humans.
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
- MEANING WITHOUT SETUP: THE IDEAL
- MEANING THROUGH SETUP: CURATED TOOLS
- QUICK START: PEOPLE CHECK THE MEANING
- SETUP WITHOUT MEANING: TO AVOID
- Setup before the first useful answer →
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

Layout: figure_evidence

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
- Retail demo database, local 9B model; the app’s answer, chart and SQL for one question
- Text-to-SQL Agent
- 7
- 
- The running app on the retail demo database; screenshot cropped.
- Source: Running app on data/retail_analytics.db, 6 November 2026; evaluation/cases.json, retail_revenue_by_category.
- TAKEAWAY
- Neither figure is wrong. The question did / not say which revenue, so a person / decides.
- 1
- 1
- The answer looks finished
- Electronics leads with 173,366, but the chart does / not say which orders it counted.
- 2
- 2
- The SQL shows the choice
- It sums price times quantity with no status filter, so / all 220 orders count, cancelled and returned ones / too.
- 3
- 3
- Wording changes the number
- Completed orders with discounts give 136,984, / about 21 % lower, with the same top category.

## 8. The model sees the schema and a few stored values, never result rows

Layout: evidence

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
- TAKEAWAY
- Before using real data, check what the / prompt contains and where it goes.
- 1
- The prompt is mostly structure
- 9 table definitions and 79 stored values: 79 of 608 distinct text values, about 13 %. About 71 % of the schema text is structure.
- 1
- Rows stay out
- Result rows are never sent, and hints are lists, never / linked to a row.
- 2
- Hints are real stored values
- Up to 6 values from text columns with at most 20 distinct values, such as order status. The limit counts values, not sensitivity.
- 2
- Small tables can qualify
- Customer emails stay out only because there are / more than 20 of them.
- 3
- The model choice moves the boundary
- With a local model nothing leaves the machine. With a hosted model, the question, schema and hints go to the provider.
- 3
- Check before real data
- Review the prompt first, or turn table selection off / to send plain table definitions with no hints.
- Source: Measured 6 November 2026 with rag.retrieve_schema_context on data/retail_analytics.db; config.py hint limits.

## 9. One question, four stages, and only one model call

Layout: process

Reader question: 

Message: The model returns text; **the application decides** what runs. Neither gate checks meaning.

Exact face text:

- 1
- 2
- 3
- 4
- SOLUTION
- Architecture
- One question, four stages, and only one model call
- The path of a question through the app, on SQLite, DuckDB or PostgreSQL
- Text-to-SQL Agent
- 9
- Ask and prepare
- A person asks in plain English. The app / reads the schema, selects the top 6 / tables and neighbours, and builds the / prompt, with no model.
- Generate
- The only model call: Gemini hosted or / Ollama local writes one SQL statement, / or declines.
- Check and run
- sqlglot refuses anything but a single / read; the engine runs it read-only with / a work budget and a row cap.
- Answer
- Show the answer, table, chart, SQL and / why those tables were chosen. A / runtime error goes back to the model / once.
- Source: pipeline.answer_question; config.py defaults; docs/2_architecture.md. 15 conformance tests per engine.
- TAKEAWAY
- The model returns text; the application decides what runs. Neither gate checks meaning.

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
- Threat and example
- 1 Model declines
- 2 Application check
- 3 Engine, read-only
- Lines of defence
- Write or schema change: drop the / students table
- Declined 6 of 6
- Blocked
- Denied on 3 engines
- 3
- Reading engine internals: show me / sqlite_master
- Declined 3 of 3
- Blocked
- Would run
- 2
- Reading files on disk: read_csv on a / local file
- –
- Blocked
- Denied
- 2
- Runaway query: a cross join on large / tables
- –
- –
- Stopped by work budget
- 1
- Oversized result: more rows than the / cap
- –
- –
- Cut at 1,000 rows
- 1
- Data the schema lacks: each patient’s / blood type
- Declined 5 of 6
- –
- –
- 1
- The limit: no layer checks meaning
- Asked for average shipping weight
- Returned average unit cost
- Passed: valid read
- Ran
- 0
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
- How to read a paired change, accuracy points
- Top 6 vs every table + hints
- Shared + summaries vs shared
- 1,034  accuracy
- 1,534  accuracy
- 1,222  table selection
- 12  behaviour
- 15  behaviour
- +3.6  [+1.4, +5.8]
- +0.2  [−1.5, +2.0]
- Note: results are compared by value and type, so the SQL’s wording does not matter. Intervals are 95 % paired bootstrap, 10,000 resamples. Not leaderboard scoring.
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
- With evidence hints (BIRD) or overall
- Without evidence hints
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
- Accuracy points
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
- Gained on the 128 where a table was missed
- Lost on the 1,094 where all were sent
- Dense embeddings: net +2 answers
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
- Note: gained and lost are net changes per group, not flip counts. Baseline: selected tables with the kept scorer, 8 of 128 and 359 of 1,094 correct.
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
- What it decides
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
- Repository: README Evaluation Results and evaluation/results/
- Spider 2.0 paper, arXiv 2411.07763 (read 6 November 2026)
- BIRD leaderboard (read 6 November 2026)
- Snowflake Cortex Analyst documentation (read 6 November 2026)
- Databricks Genie best practices (read 6 November 2026)
- WrenAI and Vanna repositories (read 6 November 2026)

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
- Manh Tuan Nguyen
- University of Technology Sydney  ·  November 2026

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
- Foreign-key neighbour, sent
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

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

## 2. Inspectable SQL, with measured limits

Layout: research_summary

Reader question: 

Message: About one answer in three still did not match on Spider, so a person should review results.

Exact face text:

- SUMMARY
- Executive summary
- Inspectable SQL, with measured limits
- What the agent does, how well it did, and what to keep in mind
- Text-to-SQL Agent   36121 Artificial Intelligence Principles and Applications
- 2
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

## 3. A fluent answer can still be the wrong answer

Layout: hard_page

Reader question: 

Message: Published scores fall about 70 points on enterprise tasks, so a good demo is not evidence.

Exact face text:

- PROBLEM
- Why it is hard
- A fluent answer can still be the wrong answer
- Text-to-SQL turns a question into SQL over a schema, then returns rows; each step can go wrong
- Text-to-SQL Agent   36121 Artificial Intelligence Principles and Applications
- 3
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

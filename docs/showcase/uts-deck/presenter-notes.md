# Presenter notes

## 1. Ask your data. Inspect the answer.

Open with the one idea of the deck.

This deck is about one idea: ask your data, then inspect the answer. It began as a UTS group project and has since been refined as a portfolio project. The illustration shows what the agent does: it finds the right tables, then lets you look closely at the result.
Reference: cover illustration from make_cover.py in this folder. It is decorative and shows no real data.

References:
- sources.md
- claims-register.md

## 2. Inspectable SQL, with measured limits

Give the whole story before the detail.

Here is the whole story before the detail. [Point: 45 of 45] Read-only comes first: generated SQL is validated and run read-only, and all 45 tests passed on three database engines with none skipped.
[Point: 64.6 % and 35.2 %] With a local 9B model, 64.6 % of Spider dev answers and 35.2 % of the harder BIRD dev answers matched, using this project's scorer. These are not leaderboard scores.
[Point: +3.6 points] On databases of 21 to 65 tables, sending the top six tables and their neighbours scored 3.6 points above sending every table with hints, using 69 % fewer prompt tokens. The gain comes from the 65- and 34-table databases.
[Point: not faster] Those smaller prompts took about two seconds longer per answer, because each question gets a different schema and the local model cannot reuse its cache. [Point: takeaway] About one in three Spider answers still did not match, so a person should review results.
Reference: README Evaluation Results, release runs of 10 October 2026 at 7708295; bird_train_large at 47284f5, 19 October 2026. AGENTS.md 4 November 2026: conformance 45 passed, 0 skipped.

References:
- sources.md
- claims-register.md

## 3. A fluent answer can still be the wrong answer

Say why a fluent answer is not enough.

Text-to-SQL turns a question into SQL over a schema and returns rows. Writing the SQL is the easy part. [Point: Meaning] The hard part is what the question means here. A word like revenue is not a column. [Point: Scale] Real schemas are also large: Spider 2.0 databases often exceed 1,000 columns.
[Point: Spider 2.0 bar] In the Spider 2.0 paper, an o1-preview agent solved 21.3 % of enterprise tasks, against 91.2 % on Spider 1.0 and 73.0 % on BIRD. Our local model also falls on the harder test, from 64.6 % to 35.2 %, on our own scorer.
[Point: Risk] The SQL runs on real data, so it must be stopped from changing that data, and a valid query can still answer the wrong question.
Reference: Spider 2.0 paper, arXiv 2411.07763, read 6 November 2026. 91.2 minus 21.3 is 69.9 points. Project scores: README Evaluation Results.

References:
- sources.md
- claims-register.md

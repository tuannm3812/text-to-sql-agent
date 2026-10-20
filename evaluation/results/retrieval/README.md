# Retrieval metrics: recall@k, coverage@k and MRR (2026-10-20)

`scripts/report_retrieval.py` ranks every table for each question with
`rag.rank_schema_chunks` (the order `retrieve_schema_context` cuts at `top_k`, before
foreign-key neighbours) and reads off where each gold table (`expected_tables`) lands.
No model is called. Metrics are defined in `text_to_sql_agent/evaluation_v2/retrieval.py`.
The ranking refactor is behaviour-preserving: 18,519 retrievals (every Spider dev, BIRD
dev and `bird_train_large` question, evidence on and off, `top_k` 3, 6 and 10) gave the
same tables, scores, reasons and schema text before and after.

| Suite (evidence) | MRR | recall@6 | coverage@6 | coverage@10 | Sent at top 6: recall / coverage |
|---|---:|---:|---:|---:|---:|
| Spider dev (off) | 0.951 | 99.9 | 99.8 | 100.0 | 100.0 / 100.0 |
| BIRD dev (on) | 0.935 | 97.0 | 92.1 | 99.3 | 99.5 / 98.0 |
| `bird_train_large` (on) | 0.853 | 86.1 | 72.3 | 80.0 | 93.1 / 86.3 |

Coverage@k is the share of questions with every gold table in the first k. "Sent" adds
the foreign-key neighbours, as a run does; its recall equals the runs' mean
`schema_recall` (0.931 on `bird_train_large`, 30 of 1,534 BIRD dev cases below 1.0).
Full tables: `spider_dev.md`, `bird_dev.md`, `bird_train_large.md`.

## What the misses cost on `bird_train_large`

Top 6 sends every gold table for 1,055 of 1,222 questions and misses one for 167. Joined
with the three full-suite arms at `47284f5` (EX):

| Questions | Plain DDL | Full DDL plus hints | Top 6 |
|---|---:|---:|---:|
| Every gold table sent (1,055) | 28.3 % | 26.7 % | 32.9 % |
| A gold table not sent (167) | 17.4 % | 18.0 % | 5.4 % |

Observed, not causal: where top 6 sent every gold table it scored 4.6 to 6.2 points above
the full-schema arms; where it dropped one, 12 to 13 points below them. On the 167 missed
cases full DDL plus hints got 30 right and top 6 got 9 (22 right only with full hints, 1
only with top 6), a net gap of 21 questions. These are different prompts on different
cases, so the gap is a comparison, not a ceiling on what a better selector would recover;
only a run of a revised selector can say that (corrected after Codex, 2026-10-20). Coverage
is also lower on harder questions (coverage@6 60.6 % on hard, 62.3 % on extra, 92.8 % on
easy), which is consistent with, but does not show, missed tables explaining top 6's lack
of gain there.

## Why tables are missed

The 196 misses concentrate on a few tables (`bird_train_large.md`, last table): `hockey`
`goalies` and `scoring` (13 each, median rank 11), `works_cycles` `person` (12, median
rank 28), `mondial_geo` `located` and `borders`. Two patterns in the `person` misses:

- **A person named in the question.** "Did Rachel Valdez complete her sales task?" ranks
  `Person` 29th: nothing in the question's words matches the table's name, columns or
  hints; only its rows hold "Rachel Valdez". Linking names to tables needs row values,
  the same privacy line value matching crossed (kept off, `docs/3_decisions.md`).
- **The same generic tables fill the top 6.** `ContactType`, `SpecialOffer`,
  `SalesTaxRate` and `Department` appear in the top 6 of unrelated questions, ahead of
  `Person` and `SalesPerson`, which points at the scorer's weighting rather than at the
  question.

Next (Phase 4 retrieval rewrite): split the scorer into named signals with their weights in
config, measure each signal's contribution with these metrics, and fix the generic-table
noise first, since it needs no row data. Any change is then checked for EX against the
top-6 run, since recall is necessary but not sufficient (the value-matching trial).

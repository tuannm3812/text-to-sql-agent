# `bird_train_large`: the large-schema suite (2026-10-18)

The first suite whose schemas top-6 selection cannot send nearly whole. Every
Spider dev and BIRD dev database has at most 14 tables; these have 21 to 65.
It exists to test table selection, schema recall at scale and prompt-size
claims, none of which the dev suites can measure
(`docs/superpowers/specs/2026-10-18-large-schema-suite-design.md`).

## What is in it

BIRD train (`train.zip`, SHA-256 `66e9e311...`, CC BY-SA 4.0), questions on
the four databases with at least 20 tables, out of 69. Built by
`scripts/prepare_benchmarks.py --suite bird_train_large --draw-subset 200`,
which extracts only these four (140 MB) from the 8.9 GB archive.

| Database | Tables | Questions |
|---|---:|---:|
| `works_cycles` (AdventureWorks) | 65 | 464 |
| `mondial_geo` | 34 | 293 |
| `soccer_2016` | 21 | 258 |
| `hockey` | 22 | 207 |
| **Total** | | **1,222** |

- **IDs** are each record's 0-based position in `train.json`; the file carries
  no `question_id`. The filter does not renumber, so an ID means the same
  record whatever the threshold.
- **Hardness** is Spider's rule counted from the gold SQL text
  (`sql_hardness`), since train has no `difficulty` field. It agrees with the
  official label on all 1,034 Spider dev queries. Split: 152 easy, 485 medium,
  264 hard, 321 extra.
- **Evidence** is carried as in BIRD dev; runs choose `--evidence on|off`.
- **Dropped, not silently:** 10 `works_cycles` records (7122, 7129, 7172,
  7173, 7178, 7218, 7227, 7325, 7409, 7438) whose gold SQL reads a
  `PersonPhone` table the database does not have. They are listed in
  `bird_train_large.source.json` under `dropped`. 474 questions name this
  database; 464 remain.
- **Gold gate: pass.** 1,221 of 1,222 references self-match. The one
  exception, 7638, returns 319,882 rows against the 100,000-row cap and is on
  `bird_train_large.gold_exceptions.txt` with that reason.
- `subset200` is drawn with the shared seed (`20261008`): 25 easy, 79 medium,
  43 hard, 53 extra.

## It is a train split

Nothing in this repository trains, so the agent has never seen these
questions. Any future fine-tune scored by this harness must exclude these four
databases and their questions from its training data, or this suite stops
being a test (`docs/3_decisions.md`, 2026-10-18).

## Prompt sizes against the context window

`scripts/report_prompt_sizes.py --suite bird_train_large`, saved as
`prompt_sizes.md`. The largest prompt is `works_cycles` with full DDL plus
hints: 49,417 characters. At the lowest chars-per-token ratio measured on BIRD
dev (1.6), that is about 31k tokens, inside the 32,768-token context `ollama
ps` reports for `qwen3.5:9b-q4_K_M`; at the median ratio (3.9) it is about
13k. No case is over budget in any arm, so none of the three attribution arms
would be truncated. Top-6 selection sends at most 21,939 characters here, less
than half of the full rendering, which is the first setting where it saves a
material share of the prompt.

## First experiment

The three attribution arms, same model and settings as the release runs:
plain DDL (RAG off), full DDL plus hints (`--rag-top-k 0`) and the shipped
top 6. `subset200` first, paired with `--compare`; the full suite after if the
subset is informative. Results will be tabled here.

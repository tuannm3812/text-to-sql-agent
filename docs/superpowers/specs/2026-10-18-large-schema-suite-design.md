# Large-schema evaluation suite: design (2026-10-18)

## Why

Every database in Spider dev and BIRD dev has at most 14 tables, so top-6
selection with foreign-key neighbours usually sends most of the schema. That is
why selection showed no measurable gain over full DDL plus hints and why its
cost claim was withdrawn (`docs/3_decisions.md`, 2026-10-11 and 2026-10-12).
Phase 4's remaining work, better retrieval and any prompt-size claim, cannot be
tested until a suite exists whose schemas do not fit comfortably in a prompt.

## What is chosen

**Source: BIRD train (`train.zip`, 8.9 GB, CC BY-SA 4.0).** It is the same
benchmark family, format and licence as `bird_dev`, its gold SQL is public, and
it holds the largest SQLite schemas available with ready questions
(`works_cycles` is the AdventureWorks port, around 70 tables). The alternatives
were ruled out: LiveSQLBench-Large-v1 (about 54 tables per database) ships
PostgreSQL dumps only and withholds the gold SQL behind an email request;
Spider 2.0-lite's SQLite part has 135 questions written for multi-step agents
and would score near zero here.

**Suite `bird_train_large`:** every BIRD train question whose database has at
least `LARGE_SCHEMA_MIN_TABLES` tables. The threshold is a named constant in
`scripts/prepare_benchmarks.py`, set once from the real table counts so the
suite has at least three databases and a few hundred questions, and recorded
with each database's table count in `bird_train_large.source.json`. Only the
selected databases are extracted; the rest of the 8.9 GB stays in the cached
archive, which is pinned by SHA-256 like the others.

**It is a train split, and nothing here trains.** The agent has never seen it.
The decision log records that any future fine-tune (the planned Gemma work)
must exclude these databases and questions from its training data, or this
suite stops being a test.

## Adapter

- `bird_to_cases` is generalised: the record loop moves to a shared helper that
  takes the suite name and a hardness function. `bird_dev` keeps BIRD's own
  `difficulty` field. BIRD train has no `difficulty`, so `bird_train_large`
  uses the Spider hardness rule on the gold SQL (`spider_hardness`), which the
  Spider adapter already applies; the suite's source block says so.
- `id` is BIRD's `question_id`; `evidence` is carried verbatim; `expected` is
  `answerable`; `expected_tables` come from the gold SQL as today.
- `ADAPTER_VERSION` is bumped, since the adapter grows a suite.
- `prepare_benchmarks.py` gains `prepare_bird_train_large`, following
  `prepare_bird`: fetch, verify, extract the selected databases, convert, write
  the suite, the source block and (if the suite exceeds 400 cases) a
  `subset200` drawn with the existing seed. Archive layout is read from the
  real file before the extractor is written; the dev archive nests a second zip
  and the same path is reused if train does.

## Validation before any model run

1. `--gate gold` on the new suite: every gold query self-matches or is listed
   in `bird_train_large.gold_exceptions.txt` with the reason, as for `bird_dev`.
2. Prompt size against the context window. `ollama ps` reports a 32,768-token
   context for `qwen3.5:9b-q4_K_M`; the largest prompt sent so far is 7,488
   tokens. Before the full-DDL arms run, a read-only pass renders each case's
   three schema contexts (plain DDL, DDL plus hints, top 6 plus hints) and
   reports their sizes, so any case whose prompt could exceed the window is
   known in advance. Ollama truncates an over-long prompt silently from the
   front, which would drop the system prompt, so such cases are flagged in the
   suite's README rather than discovered after a run.

## First experiment, once the suite exists

The three attribution arms on the new suite, same model and settings as the
release runs: RAG off, RAG on at `top_k=0`, RAG on at top 6 (shipped). Paired
with `--compare`. This is the first run where selection sends a small fraction
of the schema, so it tests the retrieval report's size figures, schema recall
at scale, and whether the embedding rewrite is worth doing.

## Tests

- Adapter: a `bird_train_mini` fixture in the shape of `bird_mini`, covering a
  record without `difficulty`, the table threshold, and a database below it
  being skipped with its questions.
- Prepare script: the existing fake-archive pattern in
  `tests/test_scripts_prepare_benchmarks.py`, with the train layout.
- Manifest tests cover the suite file as they do the others.

## Out of scope

Changing the shipped default, the embedding rewrite, any change to `num_ctx`,
and the BIRD-without-evidence refresh (running separately).

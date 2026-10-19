# text-to-sql-agent

A Streamlit decision-support agent that translates natural-language questions
into safe, read-only SQLite queries, grounding the LLM with a local hybrid schema
RAG layer that indexes DDL and column metadata but never row data.

It is **not** a modelling repo — nothing is trained, and the `evaluation/`
harness measures the agent rather than a model. Do not confuse it with the
sibling `ai-meal-planner`, which is a FastAPI service.

## Standards

Follow the master standard at `~/Documents/GitHub/coding-standards/`.
Project-specific rules and deliberate overrides: @docs/0_coding_standards.md

## Deltas from the master

- `line-length = 100`, not 79 — see `docs/0_coding_standards.md` §2 for the count.
- `mypy --strict` over `text_to_sql_agent/` only. No sibling project following
  this standard uses a type checker — the master standard asks for type hints
  without enforcing them; this one does because Phases 3-4 rewrite that
  package heavily.
- **No feature branches.** Commit directly to `tuannm3812/main-refinement`, which
  is this repo's default branch — not `main`.
- `data/` and the notebook's saved outputs are deliberate §8 and §4 exceptions.
  **Do not "tidy" either.**
- `requirements.txt` is **generated** by `uv export`. Edit `pyproject.toml` and
  re-export; CI and `tests/test_packaging.py` both fail on drift.

## Evidence locations

- `docs/3_decisions.md` — dated decision log; architectural claims trace here
- `docs/6_agent_log.md` — append-only record of agent work and what was verified
- `docs/superpowers/specs/` — the five-phase refactor roadmap and per-phase specs
- `evaluation/results/` — measured accuracy per provider and model

## Current state

- 2026-09-11: Phase 1 (foundation and standards alignment) complete. Baseline is
  20 passing tests. CI has two jobs: `test` runs `pytest` on a 3.11-3.13
  matrix; `quality` runs ruff, mypy, and the packaging drift guard once,
  unmatrixed. Phases 2-5 are specced in `docs/4_next_steps.md`.
- 2026-09-19: Phase 3a (engine protocol, SQLite port, DuckDB) complete. `439`
  tests pass with `uv run pytest` (`uv sync --extra engines` first); the
  engine conformance suite (`uv run pytest -m conformance -v`) runs `24`
  tests, `12` per engine (SQLite, DuckDB), `0` skipped. Both CI jobs now
  `uv sync --extra engines` and `test` fails the build if any conformance
  test is skipped. `duckdb` stays out of `requirements.txt` — it is an
  optional extra.
- 2026-09-26: Phase 3b (PostgreSQL as the third engine, schema-qualified
  table identity carried through all three) complete. `750` tests pass with
  `uv run pytest` (`uv sync --extra engines` first, `TEXT_TO_SQL_TEST_POSTGRES_DSN`
  set against a live `docker compose -f docker/postgres.yml up -d`
  container); the 6 skips left even with the DSN set are a deliberate SQLite
  exemption (`ATTACH` is denied), not a gap. Without the DSN, the same
  command reports `503` passed, `253` skipped. The engine conformance suite
  (`uv run pytest -m conformance -rs`) runs `36` tests, `12` per engine
  (SQLite, DuckDB, PostgreSQL), `0` skipped. CI runs a `postgres:16` service
  container and fails the build if any conformance test is skipped, the same
  guard Phase 3a added for `duckdb`. `psycopg` stays out of
  `requirements.txt`, like `duckdb` — both are optional extras (`postgres`,
  or `engines` for both together).
- 2026-10-09: Evaluation contract v2 (gate G2) implemented — Tasks 1-9 of
  `docs/superpowers/plans/2026-10-08-evaluation-contract-v2.md`. `1492`
  passed / `6` skipped with the DSN set, `1148` / `350` without; conformance
  `36` / `0`. CI also runs the v2 gold gate on `demo` and `safety`. First
  results on `qwen3.5:9b-q4_K_M` are committed under `evaluation/results/`;
  the Spider and BIRD **full** release runs are still pending. Run the v2
  harness and anything touching `evaluation/results/` from a clean tree —
  a dirty run is recorded as not citable. Phase 4 (real RAG) follows; see
  `docs/4_next_steps.md`.
- 2026-10-10: Ollama thinking is an explicit setting, off by default
  (`7708295`, `docs/3_decisions.md`): with the model's default thinking, many
  answers came back empty under the 512-token cap. `ollama_think` is part of
  the run identity; `langchain-ollama` is now 0.3.10. Token counts are
  recorded per case and survive a resumed outage. `1288` passed / `350`
  skipped without the DSN (the manifest tests cover every committed run); CI,
  which runs the PostgreSQL suite, is green. The Spider and BIRD full release
  runs with thinking off are in progress from a pinned worktree, not this
  checkout.
- 2026-10-11: Spider and BIRD full release runs committed and tabled in the
  README (Spider dev 64.6%, BIRD dev 35.2% with evidence, 25.1% without).
  Gate G8 done: schema RAG adds 3.0 points on Spider, nothing measurable on
  BIRD, and makes the prompt larger (`evaluation/results/rag_ablation.md`).
  `scripts/evaluate_v2.py --compare` pairs runs that differ in one setting.
  `1328` passed / `350` skipped without the DSN. Next: Phase 4, starting with
  the full-DDL-plus-hints arm (`docs/4_next_steps.md`).
- 2026-10-12: Codex's P2s closed: the retrieval report counts the exact
  schema strings sent, with signed changes against plain DDL and against full
  DDL plus hints (`21d15a0`), and keeping RAG on is stated as provisional.
  Attribution: the value hints earn RAG's gain; top-6 selection adds nothing
  measurable (`evaluation/results/rag_ablation.md`). `--compare` says whether a
  pair is controlled. The MVP notebook reads removed fields and needs updating
  before any re-run. Next: the owner's choice of default (top 6 or full DDL plus
  hints), then Phase 4 led by hint quality.
- 2026-10-18: Flip analysis corrected and reproducible
  (`scripts/analyse_rag_flips.py`). Cut value-hint lists now say "6 of 16
  shown" (`fe90991`), kept by the owner: regression gate passes on Spider
  (-0.6) and BIRD (+0.5), neither measurable; BIRD gains 3 of 49 hidden-literal
  targets. Identical prompts proved nearly deterministic (1 of 524 BIRD SQL
  texts changed). The README table predates the label. `1377` passed / `351`
  skipped without the DSN.
- 2026-10-18 (later): `bird_train_large`, the large-schema suite from BIRD
  train (4 databases of 21-65 tables, 1,222 questions, gold gate pass,
  `evaluation/results/bird_train_large/README.md`). Train data is gitignored
  like the dev suites; `scripts/prepare_benchmarks.py --suite bird_train_large`
  rebuilds it (8.9 GB download). `sql_hardness` labels raw SQL by Spider's
  rule. `scripts/report_prompt_sizes.py` checks prompts against the context
  window before a run. Next: the three attribution arms on its `subset200`.
  `1399` passed / `351` skipped without the DSN.
- 2026-10-19: `bird_train_large` full suite, three arms at `47284f5`: top 6
  29.1 %, plain DDL 26.8 %, full DDL plus hints 25.5 %. Top 6 vs DDL plus hints
  +3.6 [+1.4, +5.8] with 69 % fewer prompt tokens, from the 65- and 34-table
  databases. Top 6 is 2.0 s slower. The first evidence that selection pays as
  schemas grow (`evaluation/results/bird_train_large/`).
- 2026-10-19 (later): retrieval profiled. Scoring was 6-75 ms per question, not
  the 2.0 s; the per-chunk index is now cached per schema version
  (`rag._cached_corpus_index`, same `(dsn, fingerprint)` key as the chunks),
  scoring is about 4 ms, and all 7,580 suite retrievals are byte-identical. The
  2.0 s is Ollama's KV prefix cache: a top-6 prompt's schema differs per
  question, so it prefills from scratch (2.7k tokens at 550 tok/s), while the
  full schema is prefilled once per database. Not fixable in `rag.py` without
  changing the prompt (`docs/4_next_steps.md`, Phase 4).

- 2026-10-19 (later): why value hints do not help on `bird_train_large`: 49 % of
  gold literals are in text columns over the 20-value ceiling (never hinted), and
  78 % of shown ones are already in the evidence. Question value matching
  (`rag.match_question_values`, `Engine.text_values`, **off by default**: it reads
  row data) trialled at tag `trial/value-matches-on`: +0.4 [-0.9, +1.6], not
  measurable (`evaluation/results/value_matches/`). Owner kept it off (2026-10-19).
  `1419` passed / `352` skipped without the DSN.

## Open risks

- The RAG "embedding" in `rag.py` is a hashed bag of character n-grams, not a
  semantic embedding. It is computed once per schema version since 2026-10-19,
  but it largely duplicates the semantic signal beside it. Phase 4.

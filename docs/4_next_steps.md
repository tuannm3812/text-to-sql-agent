# Next Steps

Phases 1, 2, 3a, and 3b are complete. Phases 4-5 are specced in
`docs/superpowers/specs/2026-09-10-refactor-roadmap.md`; this file is the
prioritised working view.

## Evaluation v2 — what is left (do first)

The contract, harness, gates and first routine results landed on 2026-10-09.
On 2026-10-10 Ollama thinking became an explicit setting, off by default, after
it was found to leave many answers empty (`docs/3_decisions.md`). Remaining, in
order:

1. **Full release runs: done 2026-10-11.** Spider dev and BIRD dev with
   evidence on and off, thinking off, commit `7708295`, committed in `a4ce1eb`
   and tabled in the README. The earlier runs at the model's default thinking
   are history: the Spider dev full run in `509998b`; the BIRD run stopped at
   1,289 of 1,534 cases is not committed.
2. **Gate G8, the RAG on/off ablation: done 2026-10-11.** Write-up in
   `evaluation/results/rag_ablation.md`; decision in `docs/3_decisions.md`.
   RAG adds 3.0 points on Spider, nothing measurable on BIRD, and makes the
   prompt 6-21 % larger. Paired comparisons now go through
   `scripts/evaluate_v2.py --compare`, which re-derived the thinking
   comparison exactly.
3. **Gemini: same flaw by design, rate unmeasured; blocked on a key.**
   Google's thinking docs (checked 2026-10-11) say `max_output_tokens` includes
   thought tokens, and `gemini-2.5-flash` thinks dynamically by default. The
   Gemini call caps output at 512 and sets no thinking budget, and the SDK's
   `response.text` is empty when only thought parts come back. So a hard
   question can return no SQL, as with Ollama. The installed SDK supports
   `ThinkingConfig(thinking_budget=0)`. No key is configured locally, so the
   empty-answer rate is not measured. With a key: run demo and a sample of
   hard BIRD questions, then disable thinking and record it in the run
   identity. Also: Google's deprecations page now limits 2.5-model access to
   users who used them before and recommends 3.5 Flash-Lite or 3.8 Flash, so
   the hosted demo's default `gemini-2.5-flash` may fail for a fresh key.
4. **Carried forward, not fixed:** a database changed *during* an uninterrupted
   session is not detected (the fingerprint is taken at start and resume), and
   SQLite `-wal`/`-shm` side files are not hashed; schema recall uses a second
   retrieval call rather than the one the pipeline made; the manifest's prompt
   hash is rebuilt through a private `llm` helper; "same hostname and dead pid"
   is not proof across pid namespaces sharing a hostname. The v1 script
   (`scripts/evaluate_text_to_sql.py`) and the May tables remain as history.

## Phase 4 — Real RAG (next)

**Lead with the hints (from G8 and its attribution, 2026-10-12).** The value
hints earn RAG's gain on both benchmarks; top-6 table selection adds nothing
measurable on Spider and leans negative on BIRD (`evaluation/results/rag_ablation.md`).
So, in order: (1) **done 2026-10-19:** the owner kept top 6 as the default over full
DDL plus hints (`docs/3_decisions.md`); (2) improve hint coverage and quality, measured
paired against the current arms. The flip analysis
(`evaluation/results/rag_attribution/error_analysis.md`) points at one defect: the
six-value cap hides needed values and the model reads the cut list as complete.
Cut lists are now labelled ("6 of 16 shown", `fe90991`, kept 2026-10-18): the
gate passes on both suites with no measurable change, and BIRD gains 3 of 49
hidden-literal targets (`evaluation/results/hint_label/README.md`). Listing all
values under the 20-value ceiling stays untested and needs a privacy decision
entry first; (3) **done 2026-10-18:** `bird_train_large`, four BIRD train databases of
21-65 tables (`evaluation/results/bird_train_large/README.md`). The three
attribution arms on its `subset200` ran 2026-10-18: top 6 beats full DDL plus
hints by +7.0 [+2.5, +11.5] with 70 % fewer prompt tokens, and full DDL plus
hints is -4.5 [-8.5, -0.5] below plain DDL, so selection matters at this size.
The full suite (2026-10-19) confirms selection at a smaller size: top 6 beats
full DDL plus hints by +3.6 [+1.4, +5.8] with 69 % fewer prompt tokens, driven
by the 65- and 34-table databases (+5 to +6 points each); the hint penalty
does not hold up (-1.3 [-2.9, +0.2]). Top 6 stays the default; (4) **done
2026-10-19:** retrieval profiled. Scoring was 6-75 ms per question, so it cannot
explain the 2.0 s; the question-independent half (tokens, n-grams, hashed
embedding per chunk, document frequencies) is now cached per schema version, scoring
is about 4 ms, and every one of the 7,580 suite retrievals selects the same tables,
scores, reasons and prompt bytes as before. The 2.0 s is Ollama's KV prefix cache:
a full-schema prompt shares its 11k-token schema across questions and prefills
only the question (about 1.1 s), while a top-6 prompt differs from the start of
its schema section, so its 2.7k tokens prefill from scratch at this model's
550 tok/s (about 4.9 s). Flash attention is already on and `num_batch` does not
help. Closing the gap means changing the prompt so questions share a prefix
again, which is a Phase 4 prompt-layout decision, not a retrieval one; (5) **done
2026-10-19:** why hints do not help on `bird_train_large`: half the needed literals are in
columns over the 20-value ceiling, and most shown ones repeat the evidence. Question value
matching (off by default, it reads row data) reached the gold value but moved EX only
+0.4 [-0.9, +1.6] (`evaluation/results/value_matches/README.md`); owner to keep or drop it; (6) next,
the retrieval rewrite below. The retrieval report's prompt size is
fixed (`21d15a0`): signed character changes against plain DDL and against full
DDL plus hints.

**The MVP notebook runs at a pinned commit.** Cell 9 reads retrieval fields
that `21d15a0` removed, so at HEAD it fails. At `dcbf669` every code cell
reproduces its saved output except cell 3's machine-specific path (verified
2026-10-13); the command is in the notebook's dated cell. Cell 17 reads the
committed May CSVs, which keep `prompt_saved_pct`, so it is unaffected. Owner
decision: migrate cell 9 to the signed size fields and take a new dated
snapshot with a full re-run, or keep the pinned historical path. Its markdown
also repeats the withdrawn claim that RAG reduces prompt size.

Decompose `retrieve_schema_context`'s 182-line body into named, individually
testable signal functions with weights in config. Replace the hashed
pseudo-embedding with real sentence embeddings behind an optional dependency
group, falling back to the lexical path so the hosted demo stays light. Persist
the index keyed by schema hash. Add recall@k and MRR to the evaluation harness so
the academic report's RAG claims become measurable.

Carried over from Phase 3b, still open:

1. **The schema cache keys on the raw DSN, not a normalised one.** A relative
   and an absolute path to the same SQLite/DuckDB file, or two equivalent
   spellings of the same PostgreSQL host (`localhost` vs `127.0.0.1`), still
   produce two separate `lru_cache` entries under `(dsn, fingerprint)` keying
   (see `docs/3_decisions.md`), since nothing canonicalises the DSN string
   before it becomes half the cache key. Low impact today — a wrong cache
   entry recomputes rather than serves stale data, because the fingerprint
   still has to match — but worth resolving alongside any RAG-layer caching
   work in this phase.
2. **Value hints can go stale on a coarse-mtime filesystem**, for SQLite and
   DuckDB specifically — both fingerprint by file `(path, mtime_ns, size)`,
   which some filesystems report at whole-second resolution. PostgreSQL does
   not have this problem: its `schema_fingerprint()` hashes a live catalogue
   read instead of a file stat (`docs/3_decisions.md`, 2026-09-26), at the
   cost of one catalogue query per cache check. Predates Phase 3a.
3. **`PostgresEngine.raw_schema()` loses column type precision.**
   `information_schema.columns.data_type` reports the bare type name
   (`numeric`, not `numeric(10,2)`); the synthesised `CREATE TABLE` DDL sent
   to the model is therefore less precise than the server's real schema.
   Low impact today — nothing in the demo corpus depends on numeric
   precision for correct SQL generation — but worth fixing if a future
   evaluation case needs it (`information_schema.columns.numeric_precision`/
   `numeric_scale` carry the missing detail).
4. **`execution.execute_query`'s `max_vm_steps` parameter is misleadingly
   named for DuckDB and PostgreSQL.** Both hold a millisecond budget there,
   not a VM-instruction count; the name is documented as back-compatible in
   the parameter's own docstring, but a rename (with the SQLite call sites
   updated too) would remove the need for that caveat.
5. **The PostgreSQL conformance fixture's cleanup only runs at test setup.**
   `tests/test_engine_conformance.py` drops any stray table before each
   PostgreSQL test starts, so a real read-only bypass still fails loudly in
   its own test, but leaves no artifact for the next run to inspect — unlike
   SQLite/DuckDB, which get a fresh `tmp_path` file per test. Worth adding a
   post-test snapshot if a bypass is ever suspected but not reproduced.

## Phase 5 — Agent loop

plan → retrieve → generate → self-critique → execute → repair, with a structured
trace surfaced in the UI. The current single-shot repair becomes a degenerate
case.

## Smaller items, not tied to a phase

1. **`safety.py` rejects a leading comment or BOM.** `/* report */ SELECT 1`,
   `-- report\nSELECT 1` and a BOM-prefixed `SELECT 1` are all refused, because
   `_ALLOWED_PREFIX` anchors on the first character and `.strip()` does not
   remove U+FEFF. Low impact in the main path — `_extract_sql_from_text` in
   `llm.py` re-anchors model output at the first `SELECT`/`WITH` — but reachable
   wherever raw SQL is fed in directly, such as the evaluation harness. Found by
   adversarial review during Phase 2 and deliberately left; fix by stripping
   leading comments and a BOM before the prefix check.

2. **`Settings.gemini_key` has no consumers.** `ui/settings.py` carries the
   field, but nothing outside `ui/sidebar.py` reads it — `key_ok` is what the
   chat path actually uses. Drop the field, or give it a consumer.

3. **`create_dummy_university_data`'s `seed` argument is inert.** It is accepted
   and ignored; the docstring says so. Either make it seed the generator or
   remove it.

## Deferred markers

Nothing is currently deferred with a `# noqa: ... # Phase N` or
`# type: ignore[...] # Phase N` marker comment. Check with
`grep -rn "noqa:.*Phase\|type: ignore.*Phase" --include="*.py" .` — treat an
empty result as "nothing deferred", not as a hidden backlog. (A bare
`grep -rn "Phase [0-9]"` is no longer a useful proxy for this check: Phase 3b
left dozens of comments and docstrings narrating what it changed and why,
none of which are deferral markers.)

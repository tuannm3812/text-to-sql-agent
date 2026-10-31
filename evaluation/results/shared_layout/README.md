# Shared prompt layout on `bird_train_large` (2026-10-31)

**Question.** Top 6 is about 2 s slower per question than the full schema because every
top-6 prompt's schema differs, so Ollama prefills it from scratch while a full-schema
prompt's 11k-token prefix is cached (`docs/4_next_steps.md`, Phase 4 item 4). Offline,
re-sorting the six tables into schema order still left 89.4 % of each prompt uncached
(94.0 % in score order), so reordering cannot close the gap.

**Change** (`20ee05f`, `rag_layout="shared"`, off by default): the prompt sends every table,
rendered exactly as RAG on at `top_k=0`, so the text is the same for every question on a
database, and names the six selected tables in a section after the schema, before the
question (`pipeline.prompt_schema`, `llm.build_user_prompt`). Retrieval, scoring and the
selected set are unchanged; only the prompt layout differs.

**Arms.** `qwen3.5:9b-q4_K_M`, think off, top 6, evidence on, `--work-limit 1000000000
--max-rows 100000`, both at `20ee05f`, run back to back on the same machine; complete and
citable, 0 outages. Baseline `2026-10-31T084042_..._07b94755_100c` (selected), new
`2026-10-31T132415_..._3c3b2752_5c3c` (shared). `compare_shared_vs_selected.md` is the
`--compare` output, `by_database.md` the database split.

| | Selected (shipped) | Shared | Paired change |
|---|---:|---:|---|
| EX, 1,222 questions | 30.0 % (367) | 27.7 % (338) | **-2.4 [-4.6, -0.2]**, 85 helped / 114 hurt |
| Latency, mean | 10.2 s | 4.3 s | **-5.9 s [-6.3, -5.6]** (-58 %) |
| Latency, median | 9.1 s | 3.3 s | |
| Prompt tokens, mean (max) | 2,641 (9,280) | 8,430 (23,355) | +219 % |
| Completion tokens, mean | 61 | 72 | +17 % |

By database: `works_cycles` -2.4 [-6.2, +1.5], `mondial_geo` -6.5 [-10.6, -2.4],
`soccer_2016` +2.7 [-2.7, +8.5], `hockey` -2.9 [-7.2, +1.4]. By hardness, the loss is in
`extra` (-5.0 [-9.0, -0.9]); the other three bands span zero.

- **It is as fast as hoped.** Prefill of the shared prefix is cached after the first
  question on a database, and the per-question tail (focus list, question, evidence) is
  small, so each question costs 4.3 s instead of 10.2 s; the full suite ran in 1.5 h
  instead of 3.5 h.
- **But it loses accuracy, measurably.** The interval excludes zero. The 1,222-question
  shared arm scores 27.7 %, between full DDL plus hints (25.5 % at `47284f5`) and top 6:
  naming the selected tables recovers part of what selection earns, not all of it. The
  model mostly stays inside the focus list (1,134 of 1,222 answers), so the loss is not
  the model wandering off to other tables; it is the same six tables being read less well
  inside a 3x larger prompt (86 of the 114 hurt cases are `wrong`, 24 `error`).
- **The 128 focus misses did better**, as expected: EX on the questions whose focus list
  lacks a gold table rose from 8 to 23 correct, because the table was in the prompt
  anyway. That gain is outweighed by the loss on the other 1,094.
- Prompt sizes stay within the context window (max 23,355 tokens against the 32k budget
  `scripts/report_prompt_sizes.py` checks), but the mean prompt is 3.2x larger, which is
  the cost that a hosted provider would bill.

**Reading.** Speed and accuracy trade off here: the shared layout is a 58 % latency cut
for a 2.4-point EX loss on large schemas. It stays off by default; keeping or offering
it is the owner's call (`docs/3_decisions.md`, 2026-10-31). A layout that keeps the
cached prefix and also repeats the six selected tables' DDL in the tail would restore
what the model reads but prefills about as much as top 6 does, so it is unlikely to keep
the speed gain; a shorter per-table summary in the tail is the untested middle.

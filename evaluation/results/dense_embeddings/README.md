# Dense embeddings trial on `bird_train_large` (2026-10-22)

**Change** (`e6d3799`): a dense-embedding signal in the retrieval scorer, Ollama
`all-minilm`, weight 80, chosen on the 1,022 questions outside `subset200`
(`evaluation/results/retrieval/README.md`).

**Arms.** `qwen3.5:9b-q4_K_M`, think off, top 6, evidence on, `--work-limit 1000000000
--max-rows 100000`; complete and citable, 0 outages. The run was interrupted once at 545
questions when the session closed and resumed in place (`--resume`, stale lock taken
over). Baseline: the kept scorer at `28f21bc` (`2026-10-20T142015_..._d1f11402_edc0`).

| Set | Kept scorer | Dense | Paired change, points | Helped / hurt |
|---|---:|---:|---|---:|
| Full suite | 30.0 % (367/1222) | 30.2 % (369/1222) | +0.2 [-1.6, +2.0] | 67 / 65 |
| Tuning questions (1,022) | 308 | 308 | 0.0 [-2.1, +2.1] | 55 / 55 |
| Held-out `subset200` | 59 | 61 | +1.0 [-3.5, +5.5] | 12 / 10 |

Against top 6 at `47284f5`:
+1.1 [-0.9, +3.0]. By database (`by_database.md`): `works_cycles` +0.6, `mondial_geo` +1.0,
`soccer_2016` +0.4, `hockey` -2.4 [-5.8, +0.5]; every interval spans zero.

- **Gate pass, no measurable change.**
- **Where retrieval improved, answers did too.** Questions with every gold table sent rose
  from 1,094 to 1,148 (the runs' own `schema_recall`). Of the 128 questions the kept
  scorer had missed a gold table on, 68 now get all of them, and EX on those 128 rose
  from 8 to 26 correct.
- **But the rest churned.** Elsewhere, a changed table set or order changes the prompt,
  and those flips (helped and hurt in about equal numbers) absorb that gain at suite
  level, as in the two earlier retrieval trials.
- **Cost:** latency 7.6 s to 7.0 s per question, prompt tokens 2,641 to 2,654 on average;
  the embeddings are computed once per schema and per question locally.

Keeping or reverting the default is the owner's call (`docs/3_decisions.md`, 2026-10-22).

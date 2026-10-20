# Scorer signals trial on `bird_train_large` (2026-10-21)

**Change** (`28f21bc`): value-hint words weighted at 0.25 in BM25 and plurals matched to
singulars (`evaluation/results/retrieval/README.md`, last section). Weight chosen on the
1,022 questions outside `subset200`.

**Arms.** `qwen3.5:9b-q4_K_M`, think off, top 6, evidence on, `--work-limit 1000000000
--max-rows 100000`; both complete and citable, 0 outages, 0 generation failures. The
pair differs only in commit.

| Run | Directory |
|---|---|
| Baseline, top 6 at `47284f5` | `2026-10-18T164708_..._82113302_30ea` |
| New scorer, `28f21bc` | `2026-10-20T142015_..._d1f11402_edc0` |

| Set | Baseline | New | Paired change, points | Helped / hurt |
|---|---:|---:|---|---:|
| Full suite | 29.1 % (356/1222) | 30.0 % (367/1222) | +0.9 [-0.7, +2.4] | 51 / 40 |
| Tuning questions (1,022) | 295 | 308 | +1.3 [-0.4, +2.9] | 46 / 33 |
| Held-out `subset200` | 61 | 59 | -1.0 [-4.5, +2.5] | 5 / 7 |

By database (`by_database.md`): `works_cycles` +1.5 [-0.9, +3.9], `mondial_geo` 0.0
[-3.4, +3.1], `soccer_2016` -0.4 [-3.9, +3.1], `hockey` +2.4 [-1.0, +6.3].

- **Gate pass, no measurable change** (`bird_train_large_gate.txt`). Every interval
  spans zero; the held-out slice, the fairer test of a tuned weight, leans negative.
- **Retrieval improved as measured:** questions with every gold table sent rose from
  1,055 to 1,094 (the runs' own `schema_recall`), matching the offline report.
- **Order matters too.** 480 questions got the same table set, 22 of them flipped, so
  reordering the same tables changes answers; part of the 91 flips is that.
- **Latency** 6.0 s to 7.6 s with 29 fewer prompt tokens on average. The value-matching
  trial showed the same rise (7.5 s) with a near-identical prompt, so this looks like a
  change in the machine or Ollama since the baseline, not the scorer; not attributed.

Better recall did not become measurable accuracy, as with value matching. Keeping or
reverting the scorer default is the owner's call (`docs/3_decisions.md`, 2026-10-21).

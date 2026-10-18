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
subset is informative.

### `subset200` results (2026-10-18, commit `47284f5`)

All three runs are complete, citable and controlled (same commit, clean
trees, same prompt), with no outages or empty answers. The runs are under
`evaluation/results/2026-10-18T1*_bird_train_large_subset200_*`. Paired
comparisons are in `compare_k0_vs_off.md`, `compare_k6_vs_k0.md` and
`compare_k6_vs_off.md`.

| Arm | EX (95 % CI) | Prompt tokens, mean | Schema recall | Latency, mean |
|---|---|---:|---:|---:|
| Plain DDL (RAG off) | 28.0 % [22.0, 34.5] (56/200) | 6,237 | n/a | 4.2 s |
| Full DDL plus hints (`--rag-top-k 0`) | 23.5 % [17.5, 29.5] (47/200) | 8,657 | 1.000 | 4.8 s |
| Top 6 (shipped) | 30.5 % [24.0, 37.0] (61/200) | 2,562 | 0.918 | 6.8 s |

| Pair (new vs baseline) | Paired change, points | Helped / hurt |
|---|---|---:|
| Top 6 vs full DDL plus hints | **+7.0 [+2.5, +11.5]** | 18 / 4 |
| Full DDL plus hints vs plain DDL | **-4.5 [-8.5, -0.5]** | 4 / 13 |
| Top 6 vs plain DDL | +2.5 [-3.0, +8.0] | 18 / 13 |

- **Selection matters here, unlike on the dev suites.** Top 6 beats full DDL
  plus hints by 7.0 points, an interval that excludes zero, while sending
  70 % fewer prompt tokens. Most of the gain is on medium (+13.9) and extra
  (+9.4) questions. On Spider and BIRD dev, where every database has at most
  14 tables, selection added nothing measurable.
- **Adding hints to the full schema hurts at this size.** Full DDL plus hints
  is 4.5 points below plain DDL, with the prompt 39 % larger. The dev-suite
  attribution (hints earn RAG's gain) does not carry over to 21-65 tables.
- **Top 6 against plain DDL is not measurable** on 200 cases (+2.5, interval
  spans zero), and it loses 14.0 points on hard questions, where recall below
  1.0 can drop a needed table.
- **Top 6 is slower despite the smaller prompt** (+2.1 s against full DDL plus
  hints). Profiled 2026-10-19: retrieval scoring is not the cause (see the
  full-suite latency note below).

These are `subset200` figures. The full suite below supersedes them.

### Full-suite results (2026-10-19, commit `47284f5`)

All 1,222 questions, the same three arms and settings. Every run is complete,
citable and controlled, with no outages, empty answers or generation
failures. Paired comparisons are in `full_compare_k0_vs_off.md`,
`full_compare_k6_vs_k0.md` and `full_compare_k6_vs_off.md`.

| Arm | EX (95 % CI) | Prompt tokens, mean | Schema recall | Latency, mean |
|---|---|---:|---:|---:|
| Plain DDL (RAG off) | 26.8 % [24.4, 29.4] (328/1222) | 6,221 | n/a | 4.2 s |
| Full DDL plus hints (`--rag-top-k 0`) | 25.5 % [23.2, 28.0] (312/1222) | 8,501 | 1.000 | 4.0 s |
| Top 6 (shipped) | 29.1 % [26.7, 31.7] (356/1222) | 2,670 | 0.931 | 6.0 s |

| Pair (new vs baseline) | Paired change, points | Helped / hurt | Prompt tokens |
|---|---|---:|---:|
| Top 6 vs full DDL plus hints | **+3.6 [+1.4, +5.8]** | 117 / 73 | -68.6 % |
| Full DDL plus hints vs plain DDL | -1.3 [-2.9, +0.2] | 39 / 55 | +36.6 % |
| Top 6 vs plain DDL | +2.3 [+0.0, +4.6] | 116 / 88 | -57.1 % |

By database (EX; paired change of top 6 against each full-schema arm):

| Database | Questions | Plain DDL | DDL plus hints | Top 6 | Top 6 vs hints | Top 6 vs plain |
|---|---:|---:|---:|---:|---|---|
| `works_cycles` (65 tables) | 464 | 23.7 % | 23.1 % | 28.7 % | **+5.6 [+1.7, +9.5]** | **+5.0 [+1.1, +8.8]** |
| `mondial_geo` (34) | 293 | 18.8 % | 19.1 % | 25.3 % | **+6.1 [+2.0, +10.6]** | **+6.5 [+2.0, +10.9]** |
| `hockey` (22) | 207 | 17.9 % | 17.9 % | 15.5 % | -2.4 [-6.8, +1.9] | -2.4 [-6.8, +1.9] |
| `soccer_2016` (21) | 258 | 48.8 % | 43.4 % | 45.3 % | +1.9 [-3.1, +7.0] | -3.5 [-8.9, +1.9] |

- **Selection's gain holds on the full suite, at half the subset's size.**
  Top 6 beats full DDL plus hints by 3.6 points, an interval that excludes
  zero, with 69 % fewer prompt tokens. The subset's +7.0 was at the high end.
- **The gain comes from the two largest schemas.** On `works_cycles` (65
  tables) and `mondial_geo` (34), top 6 beats both full-schema arms by 5 to 6
  points, each interval excluding zero. On the two 21-22-table databases it
  changes nothing measurable. Selection pays off as schemas grow, which is the
  claim the dev suites could not test.
- **Top 6 against plain DDL is borderline overall** (+2.3, the interval's
  lower end at 0.0) and clear only on the two largest databases.
- **Hints on a full large schema: no measurable harm on the full suite**
  (-1.3 [-2.9, +0.2]). The subset's -4.5 does not hold up; the hints neither
  help nor clearly hurt at this size.
- **Latency.** Top 6 is 2.0 s slower per question than full DDL plus hints
  ([+1.8, +2.2] s) although its prompt is two thirds smaller. Profiled
  2026-10-19 on these databases: retrieval scoring took 6-75 ms per question
  (about 4 ms once its per-chunk index was cached), so the gap is not
  retrieval. It is Ollama's KV prefix cache. On `works_cycles`, fresh suite
  prompts prefilled in 1.1 s with the full schema (the 11k-token schema is a
  shared prefix, cached once per database; only the question is new) and in
  4.9 s with top 6 (the schema section differs per question, so 2.7k tokens
  prefill from scratch at this model's 550 tok/s on this machine). Flash
  attention was already on; `num_batch` 1024 and 2048 were slower than 512.
  Reclaiming the time needs a prompt that shares a prefix across questions,
  which would change what the model sees and so needs its own run.
- **Recall.** Top 6 drops a gold table in some cases (mean recall 0.931). Hard
  questions show no gain (-0.8 against plain DDL), consistent with that.

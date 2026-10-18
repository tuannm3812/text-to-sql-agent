# Schema context: RAG off (plain DDL) (baseline) vs RAG on, k=0 (all tables: full DDL plus value hints) (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-18T135948_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-off-evidence-on-think-off_3d4b6fb6_83d3` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`
- New: `2026-10-18T152535_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k0-evidence-on-think-off_7e00b59f_95a2` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`

Suite `bird_train_large`, subset `full`, mode `llm`: 1222 cases, paired by id. The runs differ in `use_rag`. They also record different `rag_top_k` values, but the RAG-off run's `rag_top_k` is unused - with RAG off the pipeline sends plain full DDL and retrieves nothing - so it is no second factor. They differ in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1222 | 1222 |
| use_rag | `False` | `True` |
| rag_top_k | `6` (unused: RAG off) | `0` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1222 | 26.8% [24.4, 29.4] (328/1222) | 25.5% [23.2, 28.0] (312/1222) | -1.3 [-2.9, +0.2] | 39 | 55 |
| easy | 152 | 45.4% [37.5, 53.3] (69/152) | 44.1% [36.2, 52.0] (67/152) | -1.3 [-6.6, +3.9] | 7 | 9 |
| medium | 485 | 32.0% [27.8, 36.3] (155/485) | 31.5% [27.6, 35.9] (153/485) | -0.4 [-3.1, +2.1] | 19 | 21 |
| hard | 264 | 20.5% [15.5, 25.4] (54/264) | 18.6% [14.0, 23.5] (49/264) | -1.9 [-5.3, +1.1] | 7 | 12 |
| extra | 321 | 15.6% [11.5, 19.6] (50/321) | 13.4% [9.7, 17.1] (43/321) | -2.2 [-4.7, +0.3] | 6 | 13 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1222 | 6221.4 | 8500.6 | +2279.2 [+2102.9, +2461.3] | +36.6% |
| completion | 1222 | 67.6 | 67.1 | -0.5 [-3.2, +2.2] | -0.7% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1222 | 4194.2 | 3250.9 |
| New | 1222 | 3980.6 | 3101.2 |

Paired difference in mean latency, new minus baseline, over the 1222 cases both runs timed: -213.6 [-351.6, -78.9] ms (-5.1%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | not applicable | 1.000 (n=1222) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

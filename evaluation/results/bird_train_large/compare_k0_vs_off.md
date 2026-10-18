# Schema context: RAG off (plain DDL) (baseline) vs RAG on, k=0 (all tables: full DDL plus value hints) (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-18T125932_bird_train_large_subset200_ollama_qwen3.5-9b-q4_K_M_rag-off-evidence-on-think-off_8b5fafe2_a92c` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`
- New: `2026-10-18T131341_bird_train_large_subset200_ollama_qwen3.5-9b-q4_K_M_rag-on-k0-evidence-on-think-off_6bb3ad07_47dd` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`

Suite `bird_train_large`, subset `subset200`, mode `llm`: 200 cases, paired by id. The runs differ in `use_rag`. They also record different `rag_top_k` values, but the RAG-off run's `rag_top_k` is unused - with RAG off the pipeline sends plain full DDL and retrieves nothing - so it is no second factor. They differ in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 200 | 200 |
| use_rag | `False` | `True` |
| rag_top_k | `6` (unused: RAG off) | `0` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 200 | 28.0% [22.0, 34.5] (56/200) | 23.5% [17.5, 29.5] (47/200) | -4.5 [-8.5, -0.5] | 4 | 13 |
| easy | 25 | 56.0% [36.0, 76.0] (14/25) | 52.0% [32.0, 72.0] (13/25) | -4.0 [-20.0, +12.0] | 2 | 3 |
| medium | 79 | 29.1% [19.0, 39.2] (23/79) | 24.1% [15.2, 34.2] (19/79) | -5.1 [-11.4, +0.0] | 1 | 5 |
| hard | 43 | 30.2% [16.3, 44.2] (13/43) | 20.9% [9.3, 32.6] (9/43) | -9.3 [-18.6, -2.3] | 0 | 4 |
| extra | 53 | 11.3% [3.8, 20.8] (6/53) | 11.3% [3.8, 20.8] (6/53) | +0.0 [-5.7, +5.7] | 1 | 1 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 200 | 6237.3 | 8657.0 | +2419.7 [+1947.0, +2913.7] | +38.8% |
| completion | 200 | 62.8 | 67.9 | +5.1 [-2.2, +13.1] | +8.2% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 200 | 4231.7 | 3119.4 |
| New | 200 | 4775.7 | 3360.8 |

Paired difference in mean latency, new minus baseline, over the 200 cases both runs timed: +544.0 [+114.3, +999.3] ms (+12.9%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | not applicable | 1.000 (n=200) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

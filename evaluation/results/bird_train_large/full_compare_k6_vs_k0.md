# `rag_top_k`: 0 (baseline) vs 6 (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-18T152535_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k0-evidence-on-think-off_7e00b59f_95a2` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`
- New: `2026-10-18T164708_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-on-think-off_82113302_30ea` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`

Suite `bird_train_large`, subset `full`, mode `llm`: 1222 cases, paired by id. The runs differ in `rag_top_k` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1222 | 1222 |
| rag_top_k | `0` | `6` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1222 | 25.5% [23.2, 28.0] (312/1222) | 29.1% [26.7, 31.7] (356/1222) | +3.6 [+1.4, +5.8] | 117 | 73 |
| easy | 152 | 44.1% [36.2, 52.0] (67/152) | 46.7% [38.8, 54.6] (71/152) | +2.6 [-3.3, +9.2] | 14 | 10 |
| medium | 485 | 31.5% [27.6, 35.9] (153/485) | 35.7% [31.5, 40.0] (173/485) | +4.1 [+0.4, +7.8] | 51 | 31 |
| hard | 264 | 18.6% [14.0, 23.5] (49/264) | 19.7% [15.2, 24.3] (52/264) | +1.1 [-3.8, +6.1] | 23 | 20 |
| extra | 321 | 13.4% [9.7, 17.1] (43/321) | 18.7% [14.6, 23.1] (60/321) | +5.3 [+1.6, +9.3] | 29 | 12 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1222 | 8500.6 | 2670.3 | -5830.3 [-6140.8, -5526.4] | -68.6% |
| completion | 1222 | 67.1 | 62.1 | -5.0 [-8.1, -1.7] | -7.5% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1222 | 3980.6 | 3101.2 |
| New | 1222 | 6007.2 | 5406.3 |

Paired difference in mean latency, new minus baseline, over the 1222 cases both runs timed: +2026.6 [+1844.8, +2210.7] ms (+50.9%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | 1.000 (n=1222) | 0.931 (n=1222) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

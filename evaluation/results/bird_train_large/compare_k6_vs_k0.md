# `rag_top_k`: 0 (baseline) vs 6 (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-18T131341_bird_train_large_subset200_ollama_qwen3.5-9b-q4_K_M_rag-on-k0-evidence-on-think-off_6bb3ad07_47dd` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`
- New: `2026-10-18T132940_bird_train_large_subset200_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-on-think-off_89c292e9_a873` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`

Suite `bird_train_large`, subset `subset200`, mode `llm`: 200 cases, paired by id. The runs differ in `rag_top_k` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 200 | 200 |
| rag_top_k | `0` | `6` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 200 | 23.5% [17.5, 29.5] (47/200) | 30.5% [24.0, 37.0] (61/200) | +7.0 [+2.5, +11.5] | 18 | 4 |
| easy | 25 | 52.0% [32.0, 72.0] (13/25) | 52.0% [32.0, 72.0] (13/25) | +0.0 [-12.0, +12.0] | 1 | 1 |
| medium | 79 | 24.1% [15.2, 34.2] (19/79) | 38.0% [27.8, 49.4] (30/79) | +13.9 [+6.3, +21.5] | 11 | 0 |
| hard | 43 | 20.9% [9.3, 32.6] (9/43) | 16.3% [7.0, 27.9] (7/43) | -4.7 [-14.0, +4.7] | 1 | 3 |
| extra | 53 | 11.3% [3.8, 20.8] (6/53) | 20.8% [11.3, 32.1] (11/53) | +9.4 [+1.9, +18.9] | 5 | 0 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 200 | 8657.0 | 2562.1 | -6094.9 [-6864.0, -5313.5] | -70.4% |
| completion | 200 | 67.9 | 56.7 | -11.2 [-20.7, -1.5] | -16.5% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 200 | 4775.7 | 3360.8 |
| New | 200 | 6827.2 | 6329.9 |

Paired difference in mean latency, new minus baseline, over the 200 cases both runs timed: +2051.4 [+1431.5, +2655.7] ms (+43.0%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | 1.000 (n=200) | 0.918 (n=200) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

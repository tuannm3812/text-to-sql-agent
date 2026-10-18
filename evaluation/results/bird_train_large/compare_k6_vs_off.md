# `use_rag`: False (baseline) vs True (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-18T125932_bird_train_large_subset200_ollama_qwen3.5-9b-q4_K_M_rag-off-evidence-on-think-off_8b5fafe2_a92c` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`
- New: `2026-10-18T132940_bird_train_large_subset200_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-on-think-off_89c292e9_a873` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`

Suite `bird_train_large`, subset `subset200`, mode `llm`: 200 cases, paired by id. The runs differ in `use_rag` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 200 | 200 |
| use_rag | `False` | `True` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 200 | 28.0% [22.0, 34.5] (56/200) | 30.5% [24.0, 37.0] (61/200) | +2.5 [-3.0, +8.0] | 18 | 13 |
| easy | 25 | 56.0% [36.0, 76.0] (14/25) | 52.0% [32.0, 72.0] (13/25) | -4.0 [-20.0, +12.0] | 2 | 3 |
| medium | 79 | 29.1% [19.0, 39.2] (23/79) | 38.0% [27.8, 49.4] (30/79) | +8.9 [+0.0, +17.7] | 10 | 3 |
| hard | 43 | 30.2% [16.3, 44.2] (13/43) | 16.3% [7.0, 27.9] (7/43) | -14.0 [-25.6, -2.3] | 1 | 7 |
| extra | 53 | 11.3% [3.8, 20.8] (6/53) | 20.8% [11.3, 32.1] (11/53) | +9.4 [+1.9, +18.9] | 5 | 0 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 200 | 6237.3 | 2562.1 | -3675.3 [-4152.1, -3200.5] | -58.9% |
| completion | 200 | 62.8 | 56.7 | -6.1 [-14.5, +2.8] | -9.7% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 200 | 4231.7 | 3119.4 |
| New | 200 | 6827.2 | 6329.9 |

Paired difference in mean latency, new minus baseline, over the 200 cases both runs timed: +2595.4 [+2050.7, +3142.9] ms (+61.3%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | not applicable | 0.918 (n=200) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

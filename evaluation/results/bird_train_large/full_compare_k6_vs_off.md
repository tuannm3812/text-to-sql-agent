# `use_rag`: False (baseline) vs True (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-18T135948_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-off-evidence-on-think-off_3d4b6fb6_83d3` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`
- New: `2026-10-18T164708_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-on-think-off_82113302_30ea` at commit `47284f5c6eebe925b8d8684ce3469fc108fc3903`

Suite `bird_train_large`, subset `full`, mode `llm`: 1222 cases, paired by id. The runs differ in `use_rag` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1222 | 1222 |
| use_rag | `False` | `True` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1222 | 26.8% [24.4, 29.4] (328/1222) | 29.1% [26.7, 31.7] (356/1222) | +2.3 [+0.0, +4.6] | 116 | 88 |
| easy | 152 | 45.4% [37.5, 53.3] (69/152) | 46.7% [38.8, 54.6] (71/152) | +1.3 [-5.3, +7.9] | 15 | 13 |
| medium | 485 | 32.0% [27.8, 36.3] (155/485) | 35.7% [31.5, 40.0] (173/485) | +3.7 [-0.2, +7.6] | 55 | 37 |
| hard | 264 | 20.5% [15.5, 25.4] (54/264) | 19.7% [15.2, 24.3] (52/264) | -0.8 [-5.7, +4.2] | 22 | 24 |
| extra | 321 | 15.6% [11.5, 19.6] (50/321) | 18.7% [14.6, 23.1] (60/321) | +3.1 [-0.6, +6.9] | 24 | 14 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1222 | 6221.4 | 2670.3 | -3551.1 [-3750.4, -3355.9] | -57.1% |
| completion | 1222 | 67.6 | 62.1 | -5.5 [-8.8, -2.2] | -8.1% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1222 | 4194.2 | 3250.9 |
| New | 1222 | 6007.2 | 5406.3 |

Paired difference in mean latency, new minus baseline, over the 1222 cases both runs timed: +1812.9 [+1627.9, +1999.4] ms (+43.2%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | not applicable | 0.931 (n=1222) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

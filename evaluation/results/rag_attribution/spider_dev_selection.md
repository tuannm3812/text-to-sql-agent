# `rag_top_k`: 0 (baseline) vs 6 (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-11T233024_spider_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k0-evidence-off-think-off_3a2be932_2dea` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`
- New: `2026-10-10T071608_spider_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-off-think-off_a8ebee81_e6c2` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`

Suite `spider_dev`, subset `full`, mode `llm`: 1034 cases, paired by id. The runs differ in `rag_top_k` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1034 | 1034 |
| rag_top_k | `0` | `6` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1034 | 64.2% [61.3, 67.2] (664/1034) | 64.6% [61.6, 67.5] (668/1034) | +0.4 [-1.4, +2.2] | 47 | 43 |
| easy | 248 | 85.1% [80.6, 89.5] (211/248) | 84.3% [79.8, 88.7] (209/248) | -0.8 [-3.2, +1.2] | 3 | 5 |
| medium | 446 | 66.8% [62.3, 71.1] (298/446) | 65.9% [61.4, 70.4] (294/446) | -0.9 [-3.8, +1.8] | 18 | 22 |
| hard | 174 | 56.3% [48.9, 63.8] (98/174) | 58.6% [51.1, 66.1] (102/174) | +2.3 [-2.9, +7.5] | 12 | 8 |
| extra | 166 | 34.3% [27.1, 41.6] (57/166) | 38.0% [30.7, 45.2] (63/166) | +3.6 [-1.8, +9.0] | 14 | 8 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1034 | 1503.5 | 1463.1 | -40.4 [-65.2, -16.5] | -2.7% |
| completion | 1034 | 34.9 | 35.4 | +0.5 [-0.7, +1.8] | +1.5% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1034 | 2631.3 | 2229.1 |
| New | 1034 | 2897.4 | 2313.7 |

Paired difference in mean latency, new minus baseline, over the 1034 cases both runs timed: +266.1 [+166.8, +370.1] ms (+10.1%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | 1.000 (n=1034) | 1.000 (n=1034) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

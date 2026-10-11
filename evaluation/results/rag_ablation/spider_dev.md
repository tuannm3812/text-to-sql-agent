# `use_rag`: False (baseline) vs True (new)

- Baseline: `2026-10-11T033934_spider_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-off-evidence-off-think-off_f934dfb5_9f67` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`
- New: `2026-10-10T071608_spider_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-off-think-off_a8ebee81_e6c2` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`

Suite `spider_dev`, subset `full`, mode `llm`: 1034 cases, paired by id. The runs differ in `use_rag` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1034 | 1034 |
| use_rag | `False` | `True` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1034 | 61.6% [58.7, 64.6] (637/1034) | 64.6% [61.6, 67.5] (668/1034) | +3.0 [+1.1, +4.9] | 68 | 37 |
| easy | 248 | 83.9% [79.0, 88.3] (208/248) | 84.3% [79.8, 88.7] (209/248) | +0.4 [-2.8, +3.6] | 9 | 8 |
| medium | 446 | 63.5% [59.0, 67.9] (283/446) | 65.9% [61.4, 70.4] (294/446) | +2.5 [-0.4, +5.4] | 27 | 16 |
| hard | 174 | 54.0% [46.6, 61.5] (94/174) | 58.6% [51.1, 66.1] (102/174) | +4.6 [-0.6, +9.8] | 15 | 7 |
| extra | 166 | 31.3% [24.1, 38.6] (52/166) | 38.0% [30.7, 45.2] (63/166) | +6.6 [+1.2, +12.0] | 17 | 6 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1034 | 1207.9 | 1463.1 | +255.3 [+224.4, +287.4] | +21.1% |
| completion | 1034 | 34.4 | 35.4 | +0.9 [-0.4, +2.4] | +2.7% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1034 | 2537.0 | 2147.7 |
| New | 1034 | 2897.4 | 2313.7 |

Paired difference in mean latency, new minus baseline, over the 1034 cases both runs timed: +360.4 [+259.7, +469.1] ms (+14.2%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | not applicable | 1.000 (n=1034) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

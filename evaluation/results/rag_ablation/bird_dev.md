# `use_rag`: False (baseline) vs True (new)

- Baseline: `2026-10-11T042329_bird_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-off-evidence-on-think-off_2e606bf4_a071` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`
- New: `2026-10-10T080619_bird_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-on-think-off_22491cc9_3ef9` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`

Suite `bird_dev`, subset `full`, mode `llm`: 1534 cases, paired by id. The runs differ in `use_rag` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1534 | 1534 |
| use_rag | `False` | `True` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1534 | 34.8% [32.5, 37.2] (534/1534) | 35.2% [32.9, 37.6] (540/1534) | +0.4 [-1.5, +2.2] | 109 | 103 |
| easy | 860 | 43.3% [40.0, 46.6] (372/860) | 43.1% [39.9, 46.5] (371/860) | -0.1 [-2.8, +2.6] | 65 | 66 |
| medium | 443 | 28.7% [24.4, 33.0] (127/443) | 29.1% [24.8, 33.4] (129/443) | +0.5 [-2.9, +3.8] | 32 | 30 |
| hard | 231 | 15.2% [10.8, 19.9] (35/231) | 17.3% [12.6, 22.1] (40/231) | +2.2 [-1.7, +6.1] | 12 | 7 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1534 | 2047.4 | 2175.4 | +128.0 [+84.7, +171.5] | +6.3% |
| completion | 1534 | 85.9 | 85.5 | -0.4 [-3.7, +2.8] | -0.5% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1534 | 6103.9 | 4295.7 |
| New | 1534 | 6211.0 | 4505.2 |

Paired difference in mean latency, new minus baseline, over the 1534 cases both runs timed: +107.2 [-98.6, +305.1] ms (+1.8%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | not applicable | 0.995 (n=1534) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

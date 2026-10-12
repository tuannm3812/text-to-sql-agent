# `rag_top_k`: 0 (baseline) vs 6 (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-12T001558_bird_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k0-evidence-on-think-off_8844615e_b6ed` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`
- New: `2026-10-10T080619_bird_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-on-think-off_22491cc9_3ef9` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`

Suite `bird_dev`, subset `full`, mode `llm`: 1534 cases, paired by id. The runs differ in `rag_top_k` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1534 | 1534 |
| rag_top_k | `0` | `6` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1534 | 36.7% [34.4, 39.2] (563/1534) | 35.2% [32.9, 37.6] (540/1534) | -1.5 [-3.2, +0.2] | 78 | 101 |
| easy | 860 | 45.2% [42.0, 48.5] (389/860) | 43.1% [39.9, 46.5] (371/860) | -2.1 [-4.4, +0.1] | 41 | 59 |
| medium | 443 | 30.2% [26.0, 34.5] (134/443) | 29.1% [24.8, 33.4] (129/443) | -1.1 [-4.7, +2.5] | 31 | 36 |
| hard | 231 | 17.3% [12.6, 22.1] (40/231) | 17.3% [12.6, 22.1] (40/231) | +0.0 [-3.0, +3.0] | 6 | 6 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1534 | 2325.1 | 2175.4 | -149.7 [-193.8, -105.5] | -6.4% |
| completion | 1534 | 85.8 | 85.5 | -0.3 [-3.9, +3.2] | -0.4% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1534 | 4807.4 | 3203.8 |
| New | 1534 | 6211.0 | 4505.2 |

Paired difference in mean latency, new minus baseline, over the 1534 cases both runs timed: +1403.6 [+1208.6, +1595.3] ms (+29.2%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | 1.000 (n=1534) | 0.995 (n=1534) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

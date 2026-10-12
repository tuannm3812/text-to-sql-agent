# Schema context: RAG off (plain DDL) (baseline) vs RAG on, k=0 (all tables: full DDL plus value hints) (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-11T042329_bird_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-off-evidence-on-think-off_2e606bf4_a071` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`
- New: `2026-10-12T001558_bird_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k0-evidence-on-think-off_8844615e_b6ed` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`

Suite `bird_dev`, subset `full`, mode `llm`: 1534 cases, paired by id. The runs differ in `use_rag`. They also record different `rag_top_k` values, but the RAG-off run's `rag_top_k` is unused - with RAG off the pipeline sends plain full DDL and retrieves nothing - so it is no second factor. They differ in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1534 | 1534 |
| use_rag | `False` | `True` |
| rag_top_k | `6` (unused: RAG off) | `0` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1534 | 34.8% [32.5, 37.2] (534/1534) | 36.7% [34.4, 39.2] (563/1534) | +1.9 [+0.5, +3.3] | 80 | 51 |
| easy | 860 | 43.3% [40.0, 46.6] (372/860) | 45.2% [42.0, 48.5] (389/860) | +2.0 [-0.1, +4.1] | 48 | 31 |
| medium | 443 | 28.7% [24.4, 33.0] (127/443) | 30.2% [26.0, 34.5] (134/443) | +1.6 [-1.4, +4.3] | 24 | 17 |
| hard | 231 | 15.2% [10.8, 19.9] (35/231) | 17.3% [12.6, 22.1] (40/231) | +2.2 [-0.4, +5.2] | 8 | 3 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1534 | 2047.4 | 2325.1 | +277.7 [+243.4, +312.4] | +13.6% |
| completion | 1534 | 85.9 | 85.8 | -0.1 [-3.4, +3.1] | -0.1% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1534 | 6103.9 | 4295.7 |
| New | 1534 | 4807.4 | 3203.8 |

Paired difference in mean latency, new minus baseline, over the 1534 cases both runs timed: -1296.4 [-1490.2, -1117.1] ms (-21.2%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | not applicable | 1.000 (n=1534) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

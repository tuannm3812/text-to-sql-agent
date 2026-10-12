# Schema context: RAG off (plain DDL) (baseline) vs RAG on, k=0 (all tables: full DDL plus value hints) (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-11T033934_spider_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-off-evidence-off-think-off_f934dfb5_9f67` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`
- New: `2026-10-11T233024_spider_dev_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k0-evidence-off-think-off_3a2be932_2dea` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`

Suite `spider_dev`, subset `full`, mode `llm`: 1034 cases, paired by id. The runs differ in `use_rag`. They also record different `rag_top_k` values, but the RAG-off run's `rag_top_k` is unused - with RAG off the pipeline sends plain full DDL and retrieves nothing - so it is no second factor. They differ in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1034 | 1034 |
| use_rag | `False` | `True` |
| rag_top_k | `6` (unused: RAG off) | `0` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1034 | 61.6% [58.7, 64.6] (637/1034) | 64.2% [61.3, 67.2] (664/1034) | +2.6 [+0.9, +4.4] | 56 | 29 |
| easy | 248 | 83.9% [79.0, 88.3] (208/248) | 85.1% [80.6, 89.5] (211/248) | +1.2 [-1.2, +3.6] | 7 | 4 |
| medium | 446 | 63.5% [59.0, 67.9] (283/446) | 66.8% [62.3, 71.1] (298/446) | +3.4 [+0.7, +6.1] | 26 | 11 |
| hard | 174 | 54.0% [46.6, 61.5] (94/174) | 56.3% [48.9, 63.8] (98/174) | +2.3 [-3.4, +8.0] | 15 | 11 |
| extra | 166 | 31.3% [24.1, 38.6] (52/166) | 34.3% [27.1, 41.6] (57/166) | +3.0 [-0.6, +6.6] | 8 | 3 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1034 | 1207.9 | 1503.5 | +295.7 [+264.1, +327.9] | +24.5% |
| completion | 1034 | 34.4 | 34.9 | +0.4 [-0.6, +1.6] | +1.2% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1034 | 2537.0 | 2147.7 |
| New | 1034 | 2631.3 | 2229.1 |

Paired difference in mean latency, new minus baseline, over the 1034 cases both runs timed: +94.2 [+30.1, +160.9] ms (+3.7%).

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

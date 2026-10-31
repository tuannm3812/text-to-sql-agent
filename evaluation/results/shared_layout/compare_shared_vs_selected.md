# `rag_layout`: selected (baseline) vs shared (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-31T084042_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-on-think-off_07b94755_100c` at commit `20ee05f6213a64190b78e21abf37e0851204de8b`
- New: `2026-10-31T132415_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-shared-evidence-on-think-off_3c3b2752_5c3c` at commit `20ee05f6213a64190b78e21abf37e0851204de8b`

Suite `bird_train_large`, subset `full`, mode `llm`: 1222 cases, paired by id. The runs differ in `rag_layout` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1222 | 1222 |
| rag_layout | `selected` | `shared` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1222 | 30.0% [27.5, 32.7] (367/1222) | 27.7% [25.1, 30.2] (338/1222) | -2.4 [-4.6, -0.2] | 85 | 114 |
| easy | 152 | 47.4% [39.5, 55.3] (72/152) | 48.0% [40.1, 55.9] (73/152) | +0.7 [-6.6, +7.2] | 15 | 14 |
| medium | 485 | 37.1% [33.0, 41.4] (180/485) | 35.5% [31.1, 39.8] (172/485) | -1.6 [-5.4, +2.1] | 39 | 47 |
| hard | 264 | 21.2% [16.3, 26.1] (56/264) | 18.9% [14.4, 23.9] (50/264) | -2.3 [-6.8, +2.3] | 16 | 22 |
| extra | 321 | 18.4% [14.3, 22.7] (59/321) | 13.4% [9.7, 17.1] (43/321) | -5.0 [-9.0, -0.9] | 15 | 31 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1222 | 2640.9 | 8430.3 | +5789.4 [+5492.0, +6093.8] | +219.2% |
| completion | 1222 | 61.1 | 71.7 | +10.6 [+7.3, +14.0] | +17.3% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1222 | 10240.5 | 9055.8 |
| New | 1222 | 4318.5 | 3298.5 |

Paired difference in mean latency, new minus baseline, over the 1222 cases both runs timed: -5922.0 [-6303.2, -5550.8] ms (-57.8%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | 0.948 (n=1222) | 0.948 (n=1222) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

Schema recall is recall of the *selected* tables under either layout; a shared layout run sent every table, so there a missed table was absent from the focus list, not from the prompt.

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

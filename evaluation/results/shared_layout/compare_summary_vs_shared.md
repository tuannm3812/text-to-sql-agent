# `rag_layout`: shared (baseline) vs shared-summary (new)

**Not controlled: `commit` differs, so this measures the setting and those changes together.**

- Baseline: `2026-10-31T132415_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-shared-evidence-on-think-off_3c3b2752_5c3c` at commit `20ee05f6213a64190b78e21abf37e0851204de8b`
- New: `2026-11-04T042109_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-shared-summary-evidence-on-think-off_738e2cbb_5ca9` at commit `5ec389320b96650fe89b30e3d9b325a6968d4efa`

Suite `bird_train_large`, subset `full`, mode `llm`: 1222 cases, paired by id. The runs differ in `rag_layout` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 1222 | 1222 |
| rag_layout | `shared` | `shared-summary` |
| commit | `20ee05f6213a64190b78e21abf37e0851204de8b` | `5ec389320b96650fe89b30e3d9b325a6968d4efa` |

Also differing: `commit`. The regression gate lets the code under test and the prompt differ too, so these do not make the pair incompatible; they are part of what changed between the two runs.

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 1222 | 27.7% [25.1, 30.2] (338/1222) | 27.9% [25.5, 30.4] (341/1222) | +0.2 [-1.5, +2.0] | 57 | 54 |
| easy | 152 | 48.0% [40.1, 55.9] (73/152) | 46.7% [38.8, 54.6] (71/152) | -1.3 [-5.9, +3.3] | 6 | 8 |
| medium | 485 | 35.5% [31.1, 39.8] (172/485) | 33.0% [28.9, 37.3] (160/485) | -2.5 [-5.2, +0.2] | 18 | 30 |
| hard | 264 | 18.9% [14.4, 23.9] (50/264) | 20.8% [15.9, 25.8] (55/264) | +1.9 [-1.5, +5.3] | 14 | 9 |
| extra | 321 | 13.4% [9.7, 17.1] (43/321) | 17.1% [13.1, 21.5] (55/321) | +3.7 [+0.6, +6.9] | 19 | 7 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 1222 | 8430.3 | 8625.2 | +195.0 [+21.6, +364.8] | +2.3% |
| completion | 1222 | 71.7 | 66.0 | -5.7 [-8.7, -2.9] | -8.0% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 1222 | 4318.5 | 3298.5 |
| New | 1222 | 4359.8 | 3440.1 |

Paired difference in mean latency, new minus baseline, over the 1222 cases both runs timed: +41.3 [-117.1, +195.5] ms (+1.0%).

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

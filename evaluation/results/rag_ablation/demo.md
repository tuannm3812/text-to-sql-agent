# `use_rag`: False (baseline) vs True (new)

**Controlled: same commit, clean trees and same prompt.**

- Baseline: `2026-10-11T033836_demo_full_ollama_qwen3.5-9b-q4_K_M_rag-off-evidence-off-think-off_ff782800_6210` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`
- New: `2026-10-10T061821_demo_full_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-off-think-off_b3215300_55cb` at commit `77082957a8d6306fde5efc8e00f7f5f6d6c65c5a`

Suite `demo`, subset `full`, mode `llm`: 12 cases, paired by id. The runs differ in `use_rag` and in no other setting the regression gate checks.

| | Baseline | New |
|---|---|---|
| Citable | yes | yes |
| Cases | 12 | 12 |
| use_rag | `False` | `True` |

## Execution accuracy (answerable cases)

| Population | Cases | Baseline EX | New EX | Paired change (points) | Helped | Hurt |
|---|---:|---|---|---|---:|---:|
| overall | 12 | 16.7% [0.0, 41.7] (2/12) | 33.3% [8.3, 58.3] (4/12) | +16.7 [+0.0, +41.7] | 2 | 0 |
| easy | 5 | 40.0% [0.0, 80.0] (2/5) | 60.0% [20.0, 100.0] (3/5) | +20.0 [+0.0, +60.0] | 1 | 0 |
| medium | 4 | 0.0% [0.0, 0.0] (0/4) | 25.0% [0.0, 75.0] (1/4) | +25.0 [+0.0, +75.0] | 1 | 0 |
| hard | 3 | 0.0% [0.0, 0.0] (0/3) | 0.0% [0.0, 0.0] (0/3) | +0.0 [+0.0, +0.0] | 0 | 0 |

## Cost (tokens per case)

| Tokens | Cases both reported | Baseline mean | New mean | Paired difference (mean) | Relative change |
|---|---:|---:|---:|---|---:|
| prompt | 12 | 1456.7 | 1624.7 | +168.0 [-32.9, +309.9] | +11.5% |
| completion | 12 | 55.7 | 47.5 | -8.2 [-25.5, +3.3] | -14.7% |

## Latency (ms per case)

| Run | Cases | Mean | Median |
|---|---:|---:|---:|
| Baseline | 12 | 4777.7 | 4776.7 |
| New | 12 | 4114.0 | 3331.9 |

Paired difference in mean latency, new minus baseline, over the 12 cases both runs timed: -663.8 [-1648.2, +146.2] ms (-13.9%).

## Other

| | Baseline | New |
|---|---:|---:|
| Mean schema recall | not applicable | 1.000 (n=12) |
| `EMPTY_GENERATED_SQL` errors | 0 | 0 |
| Generation failures | 0 | 0 |
| Outages | 0 | 0 |

## How to read this

Each paired change is new minus baseline, case by case over the cases both runs share: a 95 % percentile-bootstrap interval, 10,000 resamples of the cases with replacement, each case keeping its pair, seed 0. Cases both runs get right, or both get wrong, cancel out, which usually makes the interval narrower than the two runs' separate intervals suggest. Accuracy changes are in percentage points: helped counts the cases correct only in the new run, hurt those correct only in the baseline, and the point change is (helped - hurt) / cases. An interval that excludes zero is a difference larger than resampling the cases explains; one that spans zero is not. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

Each run's own EX and safety cells are the cells of its `report.md`: `point [low, high] (k/n)` in percent. Token and latency differences are means over the cases both runs reported; a blank cell in `cases.csv` is not reported and is never counted as zero. This is a measurement, not a regression verdict: `--gate regression` refuses a pair that differs in a setting.

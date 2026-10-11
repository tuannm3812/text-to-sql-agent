# Gate G8: schema RAG on versus off

Date: 2026-10-11. Code: commit `7708295`. Model: Ollama `qwen3.5:9b-q4_K_M`,
thinking off. Every run below is `complete` and citable, with no outages and no
empty answers.

## Hypothesis

The schema RAG layer sends the model the DDL of the six most relevant tables
plus low-cardinality value hints, instead of the DDL of every table. The
project's claim (README, "Schema RAG") is that this improves prompt size,
latency and cost, and table selection, without losing execution accuracy.

## Design

- **One factor.** Each pair differs only in `use_rag`. The comparison tool,
  `scripts/evaluate_v2.py --compare`, refuses any pair that differs in more
  than one setting, and it accepted all three. Commit, prompt, model, cases,
  budget and thinking are identical.
- **Suites.** `demo` (12 questions), Spider dev in full (1,034) and BIRD dev in
  full with evidence hints (1,534). The RAG-on runs are the committed release
  runs. The RAG-off runs repeat them with `--no-rag`.
- **What each arm sends.** RAG off sends the `CREATE TABLE` statement of every
  table and no value hints. RAG on sends the DDL of the top six retrieved tables
  and value hints for low-cardinality text columns. The ablation therefore
  measures the shipped RAG layer as a whole. It cannot separate the effect of
  choosing tables from the effect of the value hints.
- **Analysis.** Paired over the same questions, RAG on minus RAG off: a 95 %
  percentile-bootstrap interval, 10,000 resamples, seed 0. Accuracy changes are
  in percentage points. Token and latency changes are paired means over the
  questions both runs reported. An interval is sampling uncertainty over
  questions for a fixed model and prompt, not generation variance.

## Result

Effect of RAG, RAG on minus RAG off:

| Suite | EX, RAG off | EX, RAG on | EX change (points) | Helped / hurt | Prompt tokens per question | Mean latency |
|---|---|---|---|---|---|---|
| demo | 2/12 | 4/12 | +16.7 [+0.0, +41.7] | 2 / 0 | +168 [-33, +310], +11.5 % | -664 ms [-1,648, +146] |
| Spider dev | 61.6% (637/1034) | 64.6% (668/1034) | **+3.0 [+1.1, +4.9]** | 68 / 37 | **+255 [+224, +287], +21.1 %** | **+360 ms [+260, +469]** |
| BIRD dev, evidence | 34.8% (534/1534) | 35.2% (540/1534) | +0.4 [-1.5, +2.2] | 109 / 103 | **+128 [+85, +172], +6.3 %** | +107 ms [-99, +305] |

Full tool output per suite: [demo](rag_ablation/demo.md),
[Spider dev](rag_ablation/spider_dev.md), [BIRD dev](rag_ablation/bird_dev.md).

1. **Accuracy.** RAG helps on Spider by 3.0 points, most of it on the hardest
   questions: extra-hard +6.6 [+1.2, +12.0]. On BIRD it makes no measurable
   difference. Demo is too small to tell.
2. **Prompt size.** RAG never shrinks the prompt here. It grows it by 6 % on
   BIRD and 21 % on Spider. On schemas of this size, the value hints add more
   text than leaving out tables removes. Completion tokens do not change.
3. **Latency.** RAG adds 0.36 s per question on Spider and nothing measurable
   on BIRD.
4. **Table selection.** Retrieval keeps the tables the reference query needs:
   mean schema recall is 1.000 on Spider and demo and 0.995 on BIRD.

## Decision

- **Keep RAG on as the default, provisionally.** It is better on Spider by a
  measured margin. On BIRD the interval [-1.5, +2.2] allows a small loss as
  well as a gain, so it shows neither equivalence nor non-inferiority; the
  BIRD effect is uncertain, and the prompt overhead is real. (Corrected
  2026-10-12: this line first said "never worse within the intervals".)
- **Withdraw the cost claim.** The README no longer says RAG improves prompt
  size, latency or cost. On every suite measured it costs prompt tokens. A
  saving on schemas much larger than BIRD's is plausible but unmeasured.
- **Phase 4 must attribute the gain.** Before replacing the retrieval, add an
  arm with full DDL plus value hints. That separates table selection from the
  hints, and shows which one earns the Spider gain. The app's retrieval report
  also clamped "prompt savings" at zero against the wrong baseline, so it
  showed 0 % when RAG grew the prompt. Fixed 2026-10-12 (`21d15a0`): it now
  reports signed character changes against plain DDL and against full DDL
  plus hints, counted from the exact strings sent.

## Reproduce

```bash
uv run python scripts/evaluate_v2.py --suite spider_dev --subset full --mode llm \
    --provider ollama --model qwen3.5:9b-q4_K_M --ollama-think off --no-rag \
    --max-retries 2 --retry-base-seconds 10 --work-limit 1000000000 --max-rows 100000
uv run python scripts/evaluate_v2.py --compare --new <RAG-on run> --baseline <RAG-off run> \
    --out <file>
```

Runs compared:

| Suite | RAG on | RAG off |
|---|---|---|
| demo | `2026-10-10T061821_..._b3215300_55cb` | `2026-10-11T033836_..._ff782800_6210` |
| Spider dev | `2026-10-10T071608_..._a8ebee81_e6c2` | `2026-10-11T033934_..._f934dfb5_9f67` |
| BIRD dev, evidence | `2026-10-10T080619_..._22491cc9_3ef9` | `2026-10-11T042329_..._2e606bf4_a071` |

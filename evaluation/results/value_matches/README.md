# Question value matching: trial on `bird_train_large` (2026-10-19)

**Why hints do not help here.** Over the three `bird_train_large` arms at `47284f5`,
711 of 1,222 questions filter on a string literal (892 literal predicates in the gold
SQL, matched to their column with `sqlglot`). 440 of those literals (49 %) sit in text
columns with more than 20 distinct values (names, cities, teams, stores, codes), which
never get a value hint. Of the 306 literals a hint does show, 238 (78 %) are already
in BIRD's evidence, so with evidence on the hints mostly repeat it. Only 11 shown
literals are in neither the question nor the evidence.

**Change** (`753b6e6`, off by default; trial commit `3acc3b6`, tag
`trial/value-matches-on`, which only flips `DEFAULT_VALUE_MATCHES`). The prompt gets one
block after the schema listing the stored values of the prompt's tables that a phrase of
the question (evidence included) names, as SQL literals:

```
-- Stored values that match words in the question:
-- Store.Name: 'Valley Bicycle Specialists'
```

Phrases of one to five words; the longest match wins; a one-word phrase must be
capitalised past the first word, all caps or contain a digit; at most 4 columns per
phrase and 10 values in all. 633 of 1,222 top-6 prompts carry a block, about 60
characters (25 prompt tokens) on average.

**Arms.** `qwen3.5:9b-q4_K_M`, think off, top 6, evidence on, `--work-limit 1000000000
--max-rows 100000`. Both complete and citable, 0 outages, 0 generation failures. The pair
differs only in commit.

| Run | Directory |
|---|---|
| Baseline, top 6 at `47284f5` | `2026-10-18T164708_..._82113302_30ea` |
| Value matching on, `3acc3b6` | `2026-10-19T011547_..._3310c00d_5376` |

## Results

| Set | Baseline | New | Paired change, points | Helped / hurt |
|---|---:|---:|---|---:|
| Full suite | 29.1 % (356/1222) | 29.5 % (361/1222) | +0.4 [-0.9, +1.6] | 34 / 29 |
| Prompts with a match block | 178/633 | 183/633 | | 34 / 29 |
| Prompts without one (byte-identical) | 178/589 | 178/589 | | 0 / 0 |
| Wrong-value targets (post hoc, see below) | 0/58 | 4/58 | | 4 / 0 |

By database (`by_database.md`): `works_cycles` +0.2 [-1.7, +2.2], `mondial_geo` +1.4
[-1.4, +4.1], `soccer_2016` +1.2 [-1.9, +4.3], `hockey` -1.4 [-3.9, +1.0].

- **Gate: pass, no measurable change** (`bird_train_large_gate.txt`). The interval spans
  zero on the suite and on every database.
- **The value now reaches the SQL, but the questions still fail.** The targets are the
  58 questions where the top-6 baseline was wrong, its SQL lacked a gold literal, and the
  matcher puts that literal in the prompt. With matching on, 30 of the 58 SQL texts use
  the gold value, but only 4 become correct; the rest fail on joins, aggregation or
  projection. The set was chosen after seeing the baseline, so it is an upper bound on
  what the change can reach, not a frozen test set.
- **Noise costs some.** Hurt cases include one-word names that are not values in context:
  `Hall` (Hall of Fame) as `Master.lastName`, `Stanley` (Stanley Cup), `Max` (most).
- **Generation is deterministic on unchanged prompts.** All 589 prompts without a block
  produced byte-identical SQL, so every flip is in a changed prompt.
- **Latency** rose from 6.0 s to 7.5 s per question, not explained by the change:
  the prompt grew 25 tokens on average and matching took about 2 ms per question in a
  separate timing. The machine ran other work during the trial, so this is not
  attributed to the change.

## Conclusion

Value matching fixes the coverage gap it targets (the gold value is in the prompt for 58
failing questions, and the model uses it in 30) but does not move accuracy measurably on
this model. It also reads row data beyond the low-cardinality hints. The owner kept it off
by default (`docs/3_decisions.md`, 2026-10-19).

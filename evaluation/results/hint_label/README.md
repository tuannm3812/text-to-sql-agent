# Partial-list hint label: trial results (2026-10-18)

**Change** (`fe90991`). A value-hint list cut by the six-value cap now says so:
`-- language sample values (6 of 16 shown): ...`. A complete list renders as
before, the shown values are unchanged, and no extra database values are sent.
This was the next bounded experiment from the flip analysis
(`../rag_attribution/error_analysis.md`): both misleading hints there were cut
lists the model read as complete.

**Arms.** Everything ran on `qwen3.5:9b-q4_K_M`, think off, RAG on, top 6, with
`--work-limit 1000000000 --max-rows 100000`. The baseline is the shipped arm at
`7708295`; the new runs are at `fe90991` from a clean pinned worktree. All are
complete and citable, with 0 outages. The pairs differ only in commit and code.

| Run | Baseline | New |
|---|---|---|
| Spider dev, full | `2026-10-10T071608_..._a8ebee81_e6c2` | `2026-10-17T132739_..._8ee9d7ba_1e82` |
| BIRD dev, evidence on, full | `2026-10-10T080619_..._22491cc9_3ef9` | `2026-10-17T141854_..._6b49db00_e305` |
| Spider dev, `hiddenlit` (66) | rows of the full baseline | `2026-10-17T131748_..._fe47e07e_4933` |
| BIRD dev, `hiddenlit` (49) | rows of the full baseline | `2026-10-17T132132_..._42942f84_451a` |

The BIRD full run was interrupted once after 41 cases and resumed in place with
the same identity (`--resume`); the resume took over the stale lock.

## Results

Official EX, paired 95 % bootstrap intervals over cases. The full-suite verdicts
are the regression gate's output, saved beside this file.

| Set | Baseline | New | Change | Helped / hurt |
|---|---:|---:|---:|---:|
| Spider dev, full | 64.6 % (668/1034) | 64.0 % (662/1034) | -0.6 [-1.7, +0.5] | 14 / 20 |
| BIRD dev, full | 35.2 % (540/1534) | 35.7 % (548/1534) | +0.5 [-0.3, +1.4] | 26 / 18 |
| Spider, hidden-literal targets | 69.7 % (46/66) | 69.7 % (46/66) | 0.0 [-4.5, +4.5] | 1 / 1 |
| BIRD, hidden-literal targets | 28.6 % (14/49) | 34.7 % (17/49) | +6.1 [0.0, +14.3] | 3 / 0 |

- **Gate: pass on both suites.** Neither interval lies below zero and neither
  drop reaches the 5-point floor.
- **No measurable change on either full suite.** Both intervals include zero,
  with opposite signs.
- **Targets.** The BIRD gains are 405, 468 and 507, with no target lost. The
  full run reproduced the same 3 / 0 on those 49 IDs. On Spider the targets did
  not move (214 gained, 363 lost).
- **The two documented cases.** Spider 599 no longer answers
  `UNANSWERABLE_WITH_GIVEN_SCHEMA`. It now filters
  `LOWER(series_name) LIKE '%sky radio%'`, but projects an extra column, so it
  is still wrong under the official contract. BIRD 381 still switches to
  `set_translations`, whose list shows the value.

## Generation variance: what identical prompts did

Every Spider prompt carries at least one label, because every Spider dev
database has a cut column and top 6 sends most of each schema. On BIRD, 524 of
the 1534 prompts carry no label, so their schema text is byte-identical to the
baseline's. On those 524, **1 SQL text changed and no outcome flipped**. On the
1010 labelled BIRD prompts, 386 SQL texts changed (26 helped, 18 hurt); on
Spider, 184 of 1034 changed.

So every observed accuracy flip is in a case whose context changed, and
unchanged contexts were highly repeatable here, a week apart. That shows the
results are sensitive to the change. It does not measure the label's exact
causal share, or how much generation varies on the changed cases: the repeat
covers only the 524 BIRD cases with no cut list, not the 1010 labelled BIRD
cases or any Spider case, whose prompts all changed. It also covers one model
and one week, and BIRD 1304's earlier flip with an identical schema text shows
that variation can still happen. (Qualified 2026-10-18 after Codex's review;
the first version said the flips "follow the prompt change".)

## Reading

The label is cheap: no data is sent and complete lists are unchanged. It
corrects the mechanism on 599 and helps a few BIRD targets, and the gate passes
on both suites. It does not move either full suite measurably. Whether to keep
it is for the review. Keeping it changes the shipped prompt, so the README's
release table, measured at `7708295`, would then describe the previous code.
That covers BIRD without evidence too, which was not re-run.

Reproduce the target subsets with `scripts/analyse_rag_flips.py --write` and
the verdicts with `scripts/evaluate_v2.py --gate regression --new NEW
--baseline OLD`.

# Evaluation v2: bird_dev / hiddenlit / ollama / qwen3.5:9b-q4_K_M

Status: **complete** - citable: **yes** - 49 of 49 cases recorded - 0 outage(s).

## Identity

| Field | Value |
|---|---|
| run_id | `2026-10-17T132132_bird_dev_hiddenlit_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-on-think-off_42942f84_451a` |
| identity_sha256 | `42942f848aa21b04e263d9a5dfc9e05d225c5224407fbe95e4468e50735aa2e1` |
| commit | `fe90991eba7d48999754d87e0e60bd1aa173423e` |
| dirty | `False` |
| suite | `bird_dev` |
| suite_sha256 | `e774beb1020e7c8ee420742ae26e36e74e23fe4706a4a09ede225ead12101bde` |
| subset | `hiddenlit` |
| subset_sha256 | `1ea71279794302bb9a0a67aab36782dc67dbcc67e496bf00e0a2e64cf7107d57` |
| source_release | `bird-sql-dev-20251106 (2025-11-13 development split; questions birdsql/bird_sql_dev_20251106@3c11fb193e54, databases dev.zip dev_20240627)` |
| database_fingerprint | `(('data/benchmarks/bird/dev_databases/california_schools/california_schools.sqlite', '986817d793479801ed55133e55aa27e335422c0cd3866b54a3d6317b7c5f09c1'), ('data/benchmarks/bird/dev_databases/card_games/card_games.sqlite', 'c98bdb57fe7474da798b407785544b9af0daaad5d61fd21e2a73309493bc1227'), ('data/benchmarks/bird/dev_databases/european_football_2/european_football_2.sqlite', 'e4d361dbeec6591a4b315877c0c481da05c8ff5a3d389b34d6e17b6f15bee4e0'), ('data/benchmarks/bird/dev_databases/financial/financial.sqlite', 'd15d89cdb068a202b6f2b99342af44dffc1d52545b39ceaf62efdc0ba570101e'), ('data/benchmarks/bird/dev_databases/student_club/student_club.sqlite', 'eb89bcfe97eefa386a27904ec5aa15159811a7eac894ec659a36e48fa9f76b77'), ('data/benchmarks/bird/dev_databases/thrombosis_prediction/thrombosis_prediction.sqlite', 'e7e16d74b4731b4b8d33fdbe8c29cd5622620788ce8d1f335631f65fc7cf1db9'))` |
| adapter_version | `3` |
| scorer_version | `2` |
| prompt_sha256 | `89d91cbac0ecc8b32b0af647d3d1238f513249cf6cdcc9bf4ff7eb597be333c3` |
| provider | `ollama` |
| model | `qwen3.5:9b-q4_K_M` |
| evidence | `True` |
| use_rag | `True` |
| rag_top_k | `6` |
| work_limit | `1000000000` |
| max_rows | `100000` |
| max_repair_attempts | `1` |
| retry_policy | `2x10.0` |
| ollama_think | `off` |
| mode | `llm` |
| source | kind=download, release=bird-sql-dev-20251106 (2025-11-13 development split; questions birdsql/bird_sql_dev_20251106@3c11fb193e54, databases dev.zip dev_20240627), url=https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip, sha256=cdd6d19faeb45a23970b98d3ef6c40a87987c95459c2cf12076897a60cf5a630, licence=cc-by-sa-4.0, adapter_version=3, unpacked_at=2026-10-09T04:23:58+00:00, questions_url=https://huggingface.co/datasets/birdsql/bird_sql_dev_20251106/resolve/3c11fb193e5439b338e23677fa0aae11e8b85db9/data/dev_20251106-00000-of-00001.json, questions_sha256=ffd8018378ddb1a8794753e0a31cfc81862ff7318a5184c22f3dc4ce03a03feb, licence_source=front matter of birdsql/bird_sql_dev_20251106@3c11fb193e54 README.md (dev.zip bundles no licence file; bird-bench.github.io agrees: CC BY-SA 4.0 since 2024-04-27), licence_source_sha256=2ed0fcf8e873ef953d70bcf5e96042155b86a534d7b7c550509f7903dbfaeed5 |
| started | `2026-10-17T13:21:32+00:00` |
| duration_s | `348.401` |
| outage_count | `0` |
| generation_failures | `0` |

## Metrics

| Population | Cases | EX (headline) | EX over valid references | Reference coverage | Safety accuracy | Declined as unanswerable (refusal cases) | False-refusal rate | Schema recall (mean of per-case fractions) |
|---|---:|---|---|---|---|---|---|---|
| overall | 49 | 34.7% [22.4, 49.0] (17/49) | 34.7% [22.4, 49.0] (17/49) | 100.0% [100.0, 100.0] (49/49) | not applicable | not applicable | 0.0% [0.0, 0.0] (0/49) | 99.7% [99.0, 100.0] (n=49) |
| easy | 18 | 50.0% [27.8, 72.2] (9/18) | 50.0% [27.8, 72.2] (9/18) | 100.0% [100.0, 100.0] (18/18) | not applicable | not applicable | 0.0% [0.0, 0.0] (0/18) | 100.0% [100.0, 100.0] (n=18) |
| medium | 21 | 28.6% [9.5, 47.6] (6/21) | 28.6% [9.5, 47.6] (6/21) | 100.0% [100.0, 100.0] (21/21) | not applicable | not applicable | 0.0% [0.0, 0.0] (0/21) | 100.0% [100.0, 100.0] (n=21) |
| hard | 10 | 20.0% [0.0, 50.0] (2/10) | 20.0% [0.0, 50.0] (2/10) | 100.0% [100.0, 100.0] (10/10) | not applicable | not applicable | 0.0% [0.0, 0.0] (0/10) | 98.3% [95.0, 100.0] (n=10) |

Each rate cell is `point [low, high] (k/n)` in percent: a 95 % percentile-bootstrap interval, 10,000 resamples over cases, seed 0. Schema recall is not a rate: its cell is `mean [low, high] (n=cases)`, the same bootstrap over the mean of per-case recall fractions. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

EX (headline) counts every answerable case and a `reference_invalid` one as not correct; EX over valid references excludes those; reference coverage is valid references over all answerable cases. Safety accuracy is over refusal and unanswerable cases only. Declined as unanswerable is over refusal cases only: the model answered the sentinel instead of refusing, which is safe but not counted in safety accuracy.

These scorer v2 numbers are not comparable to the May 2026 12-case tables (`evaluation/results/evaluation_llm_*`). v2 applies a different comparison policy - typed values, exact text, multiset rows, order only under a top-level `ORDER BY` - not a uniformly stricter version of v1's, so a difference between the two is neither an improvement nor a regression.

## Outcomes

| Outcome | Cases |
|---|---:|
| correct | 17 |
| error | 4 |
| wrong | 28 |

## Reference-invalid cases

None.

## Generation failures

0 of 49 terminal case(s) failed before the model answered - generation raised a non-retryable provider error, or the harness did - and are scored `error` (their IDs are the rows with `generation_failure` set in `cases.csv`). A key that dies partway through a run shows here even when the run is citable.

## Latency and tokens

- Latency: median 5243.6 ms, mean 7062.0 ms over 49 cases.
- Tokens, prompt: 118581 total, 2420.0 mean over 49 cases that reported them.
- Tokens, completion: 4276 total, 87.3 mean over 49 cases that reported them.

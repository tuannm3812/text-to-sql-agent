# Evaluation v2: bird_train_large / full / ollama / qwen3.5:9b-q4_K_M

Status: **complete** - citable: **yes** - 1222 of 1222 cases recorded - 0 outage(s).

## Identity

| Field | Value |
|---|---|
| run_id | `2026-10-18T135948_bird_train_large_full_ollama_qwen3.5-9b-q4_K_M_rag-off-evidence-on-think-off_3d4b6fb6_83d3` |
| identity_sha256 | `3d4b6fb6f249ad3f111cbd3755bc5fce84e0af6da03d107f685b35b7ddfcfbb9` |
| commit | `47284f5c6eebe925b8d8684ce3469fc108fc3903` |
| dirty | `False` |
| suite | `bird_train_large` |
| suite_sha256 | `16a8c1d4fabd2fdcabb44a047422930e3693b9f448dcd444771e543423bbab49` |
| subset | `full` |
| subset_sha256 | `` |
| source_release | `bird-sql train (train.zip, folder train; questions train.json)` |
| database_fingerprint | `(('data/benchmarks/bird/train_databases/hockey/hockey.sqlite', '2987cba3921e2544fcd4603eccf5ff97b17f63103d8feb6fb908d55eb5bd9ba2'), ('data/benchmarks/bird/train_databases/mondial_geo/mondial_geo.sqlite', '02e71c23c27973be373e0c110600b4f12c77904c7594f3e345310511fe8b8d63'), ('data/benchmarks/bird/train_databases/soccer_2016/soccer_2016.sqlite', '84651eed21dbfae9f36a15697a5df81f3cb6ad78740f7301096e99dd7c4c06d5'), ('data/benchmarks/bird/train_databases/works_cycles/works_cycles.sqlite', '5a5968b86a2de3cf521294eca7cdc54887830b765e8ca7ab0b103d0f1d7daf1b'))` |
| adapter_version | `4` |
| scorer_version | `2` |
| prompt_sha256 | `89d91cbac0ecc8b32b0af647d3d1238f513249cf6cdcc9bf4ff7eb597be333c3` |
| provider | `ollama` |
| model | `qwen3.5:9b-q4_K_M` |
| evidence | `True` |
| use_rag | `False` |
| rag_top_k | `6` |
| work_limit | `1000000000` |
| max_rows | `100000` |
| max_repair_attempts | `1` |
| retry_policy | `2x10.0` |
| ollama_think | `off` |
| mode | `llm` |
| source | kind=download, release=bird-sql train (train.zip, folder train; questions train.json), url=https://bird-bench.oss-cn-beijing.aliyuncs.com/train.zip, sha256=66e9e3115b59559554013aa3b124156249f30437a6b4e4f96de3d2dfb5ae8cbc, licence=cc-by-sa-4.0, adapter_version=4, unpacked_at=2026-10-18T04:41:47+00:00, licence_source=front matter of birdsql/bird_sql_dev_20251106@3c11fb193e54 README.md, the BIRD benchmark's dataset card (train.zip bundles no licence file; bird-bench.github.io says CC BY-SA 4.0 for the benchmark since 2024-04-27), licence_source_sha256=2ed0fcf8e873ef953d70bcf5e96042155b86a534d7b7c550509f7903dbfaeed5, min_tables=20, databases={'hockey': 22, 'mondial_geo': 34, 'soccer_2016': 21, 'works_cycles': 65}, train_databases_total=69, dropped={'7122': "bird_train_large case 7122: gold SQL reads ['personphone'], not tables of database 'works_cycles'", '7129': "bird_train_large case 7129: gold SQL reads ['personphone'], not tables of database 'works_cycles'", '7172': "bird_train_large case 7172: gold SQL reads ['personphone'], not tables of database 'works_cycles'", '7173': "bird_train_large case 7173: gold SQL reads ['personphone'], not tables of database 'works_cycles'", '7178': "bird_train_large case 7178: gold SQL reads ['personphone'], not tables of database 'works_cycles'", '7218': "bird_train_large case 7218: gold SQL reads ['personphone'], not tables of database 'works_cycles'", '7227': "bird_train_large case 7227: gold SQL reads ['personphone'], not tables of database 'works_cycles'", '7325': "bird_train_large case 7325: gold SQL reads ['personphone'], not tables of database 'works_cycles'", '7409': "bird_train_large case 7409: gold SQL reads ['personphone'], not tables of database 'works_cycles'", '7438': "bird_train_large case 7438: gold SQL reads ['personphone'], not tables of database 'works_cycles'"} |
| started | `2026-10-18T13:59:48+00:00` |
| duration_s | `5143.146` |
| outage_count | `0` |
| generation_failures | `0` |

## Metrics

| Population | Cases | EX (headline) | EX over valid references | Reference coverage | Safety accuracy | Declined as unanswerable (refusal cases) | False-refusal rate | Schema recall (mean of per-case fractions) |
|---|---:|---|---|---|---|---|---|---|
| overall | 1222 | 26.8% [24.4, 29.4] (328/1222) | 26.9% [24.4, 29.4] (328/1221) | 99.9% [99.8, 100.0] (1221/1222) | not applicable | not applicable | 2.6% [1.8, 3.5] (32/1222) | not applicable |
| easy | 152 | 45.4% [37.5, 53.3] (69/152) | 45.4% [37.5, 53.3] (69/152) | 100.0% [100.0, 100.0] (152/152) | not applicable | not applicable | 0.7% [0.0, 2.0] (1/152) | not applicable |
| medium | 485 | 32.0% [27.8, 36.3] (155/485) | 32.0% [27.8, 36.3] (155/485) | 100.0% [100.0, 100.0] (485/485) | not applicable | not applicable | 1.6% [0.6, 2.9] (8/485) | not applicable |
| hard | 264 | 20.5% [15.5, 25.4] (54/264) | 20.5% [15.5, 25.4] (54/264) | 100.0% [100.0, 100.0] (264/264) | not applicable | not applicable | 2.3% [0.8, 4.2] (6/264) | not applicable |
| extra | 321 | 15.6% [11.5, 19.6] (50/321) | 15.6% [11.9, 19.7] (50/320) | 99.7% [99.1, 100.0] (320/321) | not applicable | not applicable | 5.3% [2.8, 7.8] (17/321) | not applicable |

Each rate cell is `point [low, high] (k/n)` in percent: a 95 % percentile-bootstrap interval, 10,000 resamples over cases, seed 0. Schema recall is not a rate: its cell is `mean [low, high] (n=cases)`, the same bootstrap over the mean of per-case recall fractions. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

EX (headline) counts every answerable case and a `reference_invalid` one as not correct; EX over valid references excludes those; reference coverage is valid references over all answerable cases. Safety accuracy is over refusal and unanswerable cases only. Declined as unanswerable is over refusal cases only: the model answered the sentinel instead of refusing, which is safe but not counted in safety accuracy.

These scorer v2 numbers are not comparable to the May 2026 12-case tables (`evaluation/results/evaluation_llm_*`). v2 applies a different comparison policy - typed values, exact text, multiset rows, order only under a top-level `ORDER BY` - not a uniformly stricter version of v1's, so a difference between the two is neither an improvement nor a regression.

## Outcomes

| Outcome | Cases |
|---|---:|
| correct | 328 |
| error | 122 |
| reference_invalid | 1 |
| refused | 32 |
| unanswerable | 10 |
| wrong | 729 |

## Reference-invalid cases

- `7638`

## Generation failures

0 of 1222 terminal case(s) failed before the model answered - generation raised a non-retryable provider error, or the harness did - and are scored `error` (their IDs are the rows with `generation_failure` set in `cases.csv`). A key that dies partway through a run shows here even when the run is citable.

## Latency and tokens

- Latency: median 3250.9 ms, mean 4194.2 ms over 1222 cases.
- Tokens, prompt: 7602535 total, 6221.4 mean over 1222 cases that reported them.
- Tokens, completion: 82579 total, 67.6 mean over 1222 cases that reported them.

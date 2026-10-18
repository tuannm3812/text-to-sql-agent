# Evaluation v2: spider_dev / hiddenlit / ollama / qwen3.5:9b-q4_K_M

Status: **complete** - citable: **yes** - 66 of 66 cases recorded - 0 outage(s).

## Identity

| Field | Value |
|---|---|
| run_id | `2026-10-17T131748_spider_dev_hiddenlit_ollama_qwen3.5-9b-q4_K_M_rag-on-k6-evidence-off-think-off_fe47e07e_4933` |
| identity_sha256 | `fe47e07e049c39cfbe2d0004f5dc33f4e9c2b989dc0442fc6838617fe5626ef3` |
| commit | `fe90991eba7d48999754d87e0e60bd1aa173423e` |
| dirty | `False` |
| suite | `spider_dev` |
| suite_sha256 | `04f185608f946e75e2a37a65b078b5925798de8e4b9950631acebaa2a6ae0091` |
| subset | `hiddenlit` |
| subset_sha256 | `d76381c3e25c578a9fb4d32a67acd5774b67c960f69d840324f4eda333b41131` |
| source_release | `spider-1.0 dev (spider_data.zip, dev.json revised 2020-08-03)` |
| database_fingerprint | `(('data/benchmarks/spider/database/car_1/car_1.sqlite', '9d851e396e02997a1de073ae982fe1e4b1769fdffce2fac6e325857a3a938709'), ('data/benchmarks/spider/database/course_teach/course_teach.sqlite', 'da45fcdde64ac2b9330146506b7653ad4417489d8e496e509045e1b02245d793'), ('data/benchmarks/spider/database/cre_Doc_Template_Mgt/cre_Doc_Template_Mgt.sqlite', '9c3fdd03d8795ecde60aae782ce50c4fb1d6c03de1401fcdd6dc177342a53df5'), ('data/benchmarks/spider/database/dog_kennels/dog_kennels.sqlite', 'ea5fbc6cf6aaf500371c5c121c339d9802ba6f5fbecd948a5274c0b487a9f486'), ('data/benchmarks/spider/database/flight_2/flight_2.sqlite', 'db777ba6488ae2b515cb138d71ff23c4533e5fd0355854648a1102faff3fb7af'), ('data/benchmarks/spider/database/network_1/network_1.sqlite', 'bec92cd9a68d6f23469a0df246429299f44caaf75eab12275784e0bb7d0aa9ca'), ('data/benchmarks/spider/database/student_transcripts_tracking/student_transcripts_tracking.sqlite', '5a1f4928a1fd36f6edb31c4f054203b2e2fab6b18e5951c4f5633628f82a8e56'), ('data/benchmarks/spider/database/tvshow/tvshow.sqlite', '1212c2e75cf1dcf3aeb4055331a85298b073d8a613ead77975b13bd3346b9fc4'), ('data/benchmarks/spider/database/voter_1/voter_1.sqlite', '815bf1611b8a32f649d292a6138562f1761a0c10cb256e20f6561199cff31531'))` |
| adapter_version | `3` |
| scorer_version | `2` |
| prompt_sha256 | `89d91cbac0ecc8b32b0af647d3d1238f513249cf6cdcc9bf4ff7eb597be333c3` |
| provider | `ollama` |
| model | `qwen3.5:9b-q4_K_M` |
| evidence | `False` |
| use_rag | `True` |
| rag_top_k | `6` |
| work_limit | `1000000000` |
| max_rows | `100000` |
| max_repair_attempts | `1` |
| retry_policy | `2x10.0` |
| ollama_think | `off` |
| mode | `llm` |
| source | kind=download, release=spider-1.0 dev (spider_data.zip, dev.json revised 2020-08-03), url=https://drive.usercontent.google.com/download?id=1403EGqzIDoHMdQF4c9Bkyl7dZLZ5Wt6J&export=download&confirm=t, sha256=00636695dabed6b5f4b8328a16b13e069a2f16591d5efcce57660669c85b121b, licence=CC BY-SA 4.0, adapter_version=3, unpacked_at=2026-10-09T04:23:56+00:00, licence_source=https://yale-lily.github.io/spider (the archive bundles no licence file) |
| started | `2026-10-17T13:17:48+00:00` |
| duration_s | `222.631` |
| outage_count | `0` |
| generation_failures | `0` |

## Metrics

| Population | Cases | EX (headline) | EX over valid references | Reference coverage | Safety accuracy | Declined as unanswerable (refusal cases) | False-refusal rate | Schema recall (mean of per-case fractions) |
|---|---:|---|---|---|---|---|---|---|
| overall | 66 | 69.7% [59.1, 80.3] (46/66) | 69.7% [59.1, 80.3] (46/66) | 100.0% [100.0, 100.0] (66/66) | not applicable | not applicable | 0.0% [0.0, 0.0] (0/66) | 100.0% [100.0, 100.0] (n=66) |
| easy | 20 | 75.0% [55.0, 90.0] (15/20) | 75.0% [55.0, 90.0] (15/20) | 100.0% [100.0, 100.0] (20/20) | not applicable | not applicable | 0.0% [0.0, 0.0] (0/20) | 100.0% [100.0, 100.0] (n=20) |
| medium | 33 | 81.8% [66.7, 93.9] (27/33) | 81.8% [66.7, 93.9] (27/33) | 100.0% [100.0, 100.0] (33/33) | not applicable | not applicable | 0.0% [0.0, 0.0] (0/33) | 100.0% [100.0, 100.0] (n=33) |
| hard | 10 | 40.0% [10.0, 70.0] (4/10) | 40.0% [10.0, 70.0] (4/10) | 100.0% [100.0, 100.0] (10/10) | not applicable | not applicable | 0.0% [0.0, 0.0] (0/10) | 100.0% [100.0, 100.0] (n=10) |
| extra | 3 | 0.0% [0.0, 0.0] (0/3) | 0.0% [0.0, 0.0] (0/3) | 100.0% [100.0, 100.0] (3/3) | not applicable | not applicable | 0.0% [0.0, 0.0] (0/3) | 100.0% [100.0, 100.0] (n=3) |

Each rate cell is `point [low, high] (k/n)` in percent: a 95 % percentile-bootstrap interval, 10,000 resamples over cases, seed 0. Schema recall is not a rate: its cell is `mean [low, high] (n=cases)`, the same bootstrap over the mean of per-case recall fractions. What an interval means: it is sampling uncertainty over cases, for a fixed model and prompt. It is not generation variance across repeated runs of the same model.

EX (headline) counts every answerable case and a `reference_invalid` one as not correct; EX over valid references excludes those; reference coverage is valid references over all answerable cases. Safety accuracy is over refusal and unanswerable cases only. Declined as unanswerable is over refusal cases only: the model answered the sentinel instead of refusing, which is safe but not counted in safety accuracy.

These scorer v2 numbers are not comparable to the May 2026 12-case tables (`evaluation/results/evaluation_llm_*`). v2 applies a different comparison policy - typed values, exact text, multiset rows, order only under a top-level `ORDER BY` - not a uniformly stricter version of v1's, so a difference between the two is neither an improvement nor a regression.

## Outcomes

| Outcome | Cases |
|---|---:|
| correct | 46 |
| error | 2 |
| unanswerable | 1 |
| wrong | 17 |

## Reference-invalid cases

None.

## Generation failures

0 of 66 terminal case(s) failed before the model answered - generation raised a non-retryable provider error, or the harness did - and are scored `error` (their IDs are the rows with `generation_failure` set in `cases.csv`). A key that dies partway through a run shows here even when the run is citable.

## Latency and tokens

- Latency: median 2881.2 ms, mean 3366.3 ms over 66 cases.
- Tokens, prompt: 111561 total, 1690.3 mean over 66 cases that reported them.
- Tokens, completion: 2484 total, 37.6 mean over 66 cases that reported them.

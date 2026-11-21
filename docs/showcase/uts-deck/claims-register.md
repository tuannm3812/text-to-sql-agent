# Claims register: Text-to-SQL Agent deck (UTS kit port)

Every number the deck shows, with where it comes from. The deck check refuses any number not written here.
Paths are relative to the repository root.

| Claim | Number | Source |
|---|---|---|
| Read-only conformance tests passed, skipped; engines | 45 of 45; 0; 3 | AGENTS.md, 2026-11-04 (15 per engine: SQLite, DuckDB, PostgreSQL) |
| Spider dev answers matched, local model | 64.6 % | README Evaluation Results; release run 10 Oct 2026 at 7708295 |
| BIRD dev answers matched, with evidence | 35.2 % | README Evaluation Results; same release |
| Local model size | 9B | qwen3.5:9b-q4_K_M, evaluation/results/ |
| Top 6 tables against every table with hints, bird_train_large | +3.6 points [+1.4, +5.8] | evaluation/results/bird_train_large/README.md, 47284f5, 19 Oct 2026 |
| Prompt size reduction (68.6 % rounded) | 69 % | evaluation/results/bird_train_large/README.md |
| Extra time per answer for top 6 | about 2 s (2.0 s) | AGENTS.md, 2026-10-19 |
| Large-schema databases, table counts | 21 to 65; 65 and 34 | evaluation/results/bird_train_large/README.md |
| Spider 2.0 paper: o1-preview solved, enterprise; Spider 1.0; BIRD | 21.3 %; 91.2 %; 73.0 % | R1, arXiv 2411.07763 abstract, read 6 Nov 2026 |
| Gap Spider 1.0 minus Spider 2.0 (derived) | 69.9 points; about 70 | 91.2 − 21.3 |
| Spider 2.0 databases often exceed | 1,000 columns | R1 |
| Steps in the chain; tables selected | 4; 6 | drawn structure; rag top-k default |

## Batch 2 (18 November 2026): slides 4 to 19

Numbers carried from the live Google deck, which checked them against these sources on 6 to 7 November 2026; the
large-schema, demo and retrieval rows were spot-checked again on 18 November 2026.

| Claim | Number | Source |
|---|---|---|
| BIRD top test entry (AskData); humans | 83.40 %; 92.96 % | S5, bird-bench.github.io, read 6 Nov 2026 |
| Vanna repository archived | 29 March 2026 | S4 |
| Demo answer: Electronics revenue; orders counted | 173,366; 220 | data/retail_analytics.db, recomputed 6 Nov 2026 |
| Completed-order revenue with discounts; orders; difference | 136,984; 179; about 21 % | evaluation/cases.json retail_revenue_by_category; (173,366 − 136,984) / 173,366 = 21.0 % |
| Prompt for the demo question: tables, stored values, of distinct text values, not sent, share | 9; 79; 608; 529; about 13 % | rag.retrieve_schema_context, 6 Nov 2026; 79 / 608 = 13.0 % |
| Share of schema text that is structure | about 71 % | 1 − 1,419 / 4,971 schema characters |
| Hint limits: values per column; distinct-value ceiling | 6; 20 | config.py DEFAULT_VALUE_HINT_LIMIT, DEFAULT_VALUE_HINT_MAX_CARDINALITY |
| Row cap | 1,000 rows | config.py |
| Safety run: model declines; write declines; internals; schema-lacks | 14 of 15; 6 of 6; 3 of 3; 5 of 6 | safety run 2026-10-10T061911 |
| Engines denying writes | 3 | tests/test_engine_conformance.py |
| Suites: Spider, BIRD, large schemas, demo, safety; total | 1,034; 1,534; 1,222; 12; 15; 3,817 | evaluation/suites |
| Recorded runs | 37 | evaluation/results run directories |
| Dev databases, most tables | 14 | README, gate G8 |
| Bootstrap resamples | 10,000 | stats.py |
| Shared + summaries vs shared | +0.2 [−1.5, +2.0] | evaluation/results/shared_layout/README.md |
| Spider and BIRD intervals | 64.6 [61.6, 67.5]; 35.2 [32.9, 37.6] | README v2 results, 7708295 |
| Demo suite | 4 of 12, 33.3 % [8.3, 58.3]; interval 50 points wide | README v2 results |
| Spider by difficulty | easy 84.3, medium 65.9, hard 58.6, extra 38.0 | README v2 results |
| BIRD by difficulty with evidence; without | simple 43.1, challenging 17.3; simple 34.2, challenging 8.2 | README v2 results |
| Evidence hints paired gain; thinking off on Spider | +10.1; +8.5 points | README v2 results |
| Large schemas, three arms: accuracy, prompt tokens, seconds | 25.5 %, 8,501, 4.0; 26.8 %, 6,221, 4.2; 29.1 %, 2,670, 6.0 | evaluation/results/bird_train_large/README.md |
| By database: tables, questions, change | 65, 464, +5.6 [+1.7, +9.5]; 34, 293, +6.1 [+2.0, +10.6]; 22, 207, −2.4 [−6.8, +1.9]; 21, 258, +1.9 [−3.1, +7.0] | evaluation/results/bird_train_large/README.md |
| Gain from 5 to 6 points on 2 of 4 databases | 5 to 6; 2 of 4 | same |
| All gold tables sent vs dropped: questions, top 6, every table | 1,055: 32.9 %, 26.7 %; 167: 5.4 %, 18.0 % | evaluation/results/retrieval/README.md |
| Trials: value matching, scorer signals, dense, shared, shared + summaries | +0.4 [−0.9, +1.6]; +0.9 [−0.7, +2.4]; +0.2 [−1.6, +2.0]; −2.4 [−4.6, −0.2]; −2.1 [−4.3, +0.0] | evaluation/results/value_matches, scorer_signals, dense_embeddings, shared_layout |
| All needed tables sent | 1,055 to 1,094; 1,094 to 1,148 | scorer_signals; dense_embeddings |
| Shared layout faster; tokens | 58 %; 3 times | shared_layout (10.2 s to 4.3 s) |
| Missed-table group and rest; correct by top 6 | 128 and 1,094; 8 and 359 | evaluation/results/dense_embeddings/README.md |
| Dense embeddings on the 128 | 8 to 26 | same |
| Gained and lost: dense, shared, shared + summaries | +18 / −16; +15 / −44; +13 / −39; nets +2, −29, −26 | derived from run counts (369, 338, 341 of 1,222) |
| Reordering the same tables changed | 22 of 480 answers | evaluation/results/shared_layout/README.md |
| Schema RAG scores, demo question | 30.1, 11.7, 9.9, 9.8, 5.8, 1.7, 1.6, 1.4, 1.3, 1.3, 1.3 | rag.rank_schema_chunks, 6 Nov 2026 |
| Tables reaching the model; used by the SQL | 9; 2 | same |
| Bar chart scales | 0 to 40, 0 to 100, 0 to 1,600, −50 to 25, −8 to 12 | drawn scale, not a result |

## Appendix (18 November 2026)

| Claim | Number | Source |
|---|---|---|
| Work budgets: SQLite; DuckDB and PostgreSQL | 100,000 VM steps; 5,000 ms | docs/0_coding_standards.md §3; engines/*.py default_work_limit |
| Conformance tests per engine; total | 15; 45 | AGENTS.md, 2026-11-04 |
| Number tolerance | one part in a million (1e-6 relative) | text_to_sql_agent/evaluation_v2/comparator.py |
| Scorer version | 2 | text_to_sql_agent/evaluation_v2/scoring.py |
| Prompt size index, every table + hints = 100; top 6 | 100; 31 | 2,670 / 8,501 = 31.4 % (derived; 69 % smaller is 68.6 % rounded) |
| Benchmark citations: Spider; BIRD | Yu et al. 2018, arXiv 1809.08887; Li et al. 2023, arXiv 2305.03111 | the papers' arXiv records |
| Retrieval scoring time per question, cached index | about 4 ms | AGENTS.md, 2026-10-19 |
| Questions per difficulty: Spider easy, medium, hard, extra; BIRD simple, challenging | 248, 446, 174, 166; 860, 231 | release run reports at 7708295 (2026-10-10T071608 Spider, 2026-10-10T080619 BIRD) |

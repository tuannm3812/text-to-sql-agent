# Retrieval: `bird_dev` / full, evidence on

Suite file SHA-256 `e774beb1020e7c8ee420742ae26e36e74e23fe4706a4a09ede225ead12101bde`.

1534 cases with gold tables. Ranking = `rag.rank_schema_chunks`, before foreign-key neighbours. Sent = `retrieve_schema_context(top_k=6)`, neighbours included, what a run's `schema_recall` records. Percentages.

| k | 1 | 2 | 3 | 4 | 6 | 8 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| recall@k | 50.2 | 78.2 | 88.3 | 93.1 | 97.0 | 99.3 | 99.8 |
| coverage@k | 19.1 | 59.1 | 76.2 | 85.1 | 92.1 | 98.4 | 99.3 |

MRR 0.935. Sent at top 6: recall 99.5, every gold table sent in 98.0 % of cases.

## By hardness

| Hardness | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| easy | 860 | 0.921 | 97.4 | 94.9 | 99.7 | 99.3 |
| medium | 443 | 0.946 | 96.7 | 92.3 | 99.5 | 98.6 |
| hard | 231 | 0.966 | 95.9 | 81.4 | 98.5 | 92.2 |

## By database

| Database | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| card_games | 191 | 0.919 | 100.0 | 100.0 | 100.0 | 100.0 |
| codebase_community | 186 | 0.889 | 94.2 | 88.2 | 99.5 | 98.4 |
| formula_1 | 174 | 0.840 | 90.5 | 79.9 | 97.8 | 94.3 |
| thrombosis_prediction | 163 | 0.968 | 100.0 | 100.0 | 100.0 | 100.0 |
| student_club | 158 | 0.987 | 97.9 | 95.6 | 100.0 | 100.0 |
| toxicology | 145 | 0.945 | 100.0 | 100.0 | 100.0 | 100.0 |
| european_football_2 | 129 | 0.993 | 98.8 | 98.4 | 100.0 | 100.0 |
| superhero | 129 | 0.979 | 97.6 | 93.8 | 100.0 | 100.0 |
| financial | 106 | 0.951 | 89.6 | 55.7 | 97.1 | 84.0 |
| california_schools | 89 | 0.886 | 100.0 | 100.0 | 100.0 | 100.0 |
| debit_card_specializing | 64 | 0.982 | 100.0 | 100.0 | 100.0 | 100.0 |

## Gold tables most often not sent at top 6

32 gold-table misses over 30 cases.

| Database | Table | Misses | Median rank when missed |
|---|---|---:|---:|
| `financial` | `disp` | 8 | 7 |
| `financial` | `card` | 7 | 7 |
| `formula_1` | `results` | 7 | 8 |
| `codebase_community` | `posthistory` | 3 | 7 |
| `financial` | `loan` | 2 | 7 |
| `formula_1` | `driverstandings` | 2 | 7.5 |
| `financial` | `order` | 1 | 8 |
| `financial` | `trans` | 1 | 7 |
| `formula_1` | `constructorstandings` | 1 | 7 |

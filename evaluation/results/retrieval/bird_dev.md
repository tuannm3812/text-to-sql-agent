# Retrieval: `bird_dev` / full, evidence on

Suite file SHA-256 `e774beb1020e7c8ee420742ae26e36e74e23fe4706a4a09ede225ead12101bde`.

1534 cases with gold tables. Ranking = `rag.rank_schema_chunks`, before foreign-key neighbours. Sent = `retrieve_schema_context(top_k=6)`, neighbours included, what a run's `schema_recall` records. Percentages.

| k | 1 | 2 | 3 | 4 | 6 | 8 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| recall@k | 52.7 | 82.0 | 91.2 | 94.9 | 97.9 | 99.3 | 99.8 |
| coverage@k | 20.3 | 64.5 | 81.4 | 88.5 | 94.3 | 98.4 | 99.5 |

MRR 0.958. Sent at top 6: recall 99.6, every gold table sent in 98.4 % of cases.

## By hardness

| Hardness | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| easy | 860 | 0.950 | 98.3 | 96.5 | 99.8 | 99.4 |
| medium | 443 | 0.964 | 98.1 | 95.7 | 99.5 | 98.6 |
| hard | 231 | 0.980 | 96.2 | 83.1 | 98.9 | 93.9 |

## By database

| Database | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| card_games | 191 | 0.970 | 100.0 | 100.0 | 100.0 | 100.0 |
| codebase_community | 186 | 0.955 | 98.1 | 95.7 | 99.5 | 98.4 |
| formula_1 | 174 | 0.892 | 92.0 | 83.9 | 98.3 | 95.4 |
| thrombosis_prediction | 163 | 0.965 | 100.0 | 100.0 | 100.0 | 100.0 |
| student_club | 158 | 0.984 | 98.7 | 97.5 | 100.0 | 100.0 |
| toxicology | 145 | 0.972 | 100.0 | 100.0 | 100.0 | 100.0 |
| european_football_2 | 129 | 0.994 | 100.0 | 100.0 | 100.0 | 100.0 |
| superhero | 129 | 0.989 | 97.6 | 93.8 | 100.0 | 100.0 |
| financial | 106 | 0.922 | 91.1 | 62.3 | 97.6 | 86.8 |
| california_schools | 89 | 0.919 | 100.0 | 100.0 | 100.0 | 100.0 |
| debit_card_specializing | 64 | 0.974 | 100.0 | 100.0 | 100.0 | 100.0 |

## Gold tables most often not sent at top 6

26 gold-table misses over 25 cases.

| Database | Table | Misses | Median rank when missed |
|---|---|---:|---:|
| `formula_1` | `results` | 7 | 8 |
| `financial` | `disp` | 6 | 7 |
| `financial` | `card` | 5 | 8 |
| `codebase_community` | `posthistory` | 3 | 7 |
| `financial` | `trans` | 2 | 7 |
| `financial` | `loan` | 1 | 7 |
| `financial` | `client` | 1 | 8 |
| `formula_1` | `driverstandings` | 1 | 8 |

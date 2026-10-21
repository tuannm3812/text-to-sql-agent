# Retrieval: `bird_dev` / full, evidence on

Suite file SHA-256 `e774beb1020e7c8ee420742ae26e36e74e23fe4706a4a09ede225ead12101bde`.

1534 cases with gold tables. Ranking = `rag.rank_schema_chunks`, before foreign-key neighbours. Sent = `retrieve_schema_context(top_k=6)`, neighbours included, what a run's `schema_recall` records. Percentages.

| k | 1 | 2 | 3 | 4 | 6 | 8 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| recall@k | 52.9 | 80.7 | 91.0 | 94.9 | 97.8 | 99.5 | 99.9 |
| coverage@k | 20.7 | 62.0 | 81.0 | 88.5 | 93.4 | 98.9 | 99.8 |

MRR 0.959. Sent at top 6: recall 99.7, every gold table sent in 98.4 % of cases.

## By hardness

| Hardness | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| easy | 860 | 0.954 | 98.1 | 95.7 | 99.9 | 99.8 |
| medium | 443 | 0.959 | 98.2 | 95.5 | 99.9 | 99.5 |
| hard | 231 | 0.977 | 95.5 | 80.5 | 98.5 | 91.3 |

## By database

| Database | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| card_games | 191 | 0.982 | 100.0 | 100.0 | 100.0 | 100.0 |
| codebase_community | 186 | 0.963 | 98.5 | 96.8 | 99.6 | 98.9 |
| formula_1 | 174 | 0.876 | 91.0 | 79.3 | 100.0 | 100.0 |
| thrombosis_prediction | 163 | 0.952 | 100.0 | 100.0 | 100.0 | 100.0 |
| student_club | 158 | 0.991 | 99.5 | 98.7 | 99.8 | 99.4 |
| toxicology | 145 | 0.966 | 100.0 | 100.0 | 100.0 | 100.0 |
| european_football_2 | 129 | 0.995 | 99.7 | 99.2 | 100.0 | 100.0 |
| superhero | 129 | 1.000 | 99.4 | 98.4 | 100.0 | 100.0 |
| financial | 106 | 0.939 | 86.6 | 48.1 | 96.5 | 80.2 |
| california_schools | 89 | 0.925 | 100.0 | 100.0 | 100.0 | 100.0 |
| debit_card_specializing | 64 | 0.956 | 100.0 | 100.0 | 100.0 | 100.0 |

## Gold tables most often not sent at top 6

24 gold-table misses over 24 cases.

| Database | Table | Misses | Median rank when missed |
|---|---|---:|---:|
| `financial` | `disp` | 13 | 7 |
| `financial` | `card` | 7 | 8 |
| `codebase_community` | `posthistory` | 2 | 7 |
| `financial` | `client` | 1 | 8 |
| `student_club` | `expense` | 1 | 7 |

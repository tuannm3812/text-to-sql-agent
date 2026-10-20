# Retrieval: `bird_train_large` / full, evidence on

1222 cases with gold tables. Ranking = `rag.rank_schema_chunks`, before foreign-key neighbours. Sent = `retrieve_schema_context(top_k=6)`, neighbours included, what a run's `schema_recall` records. Percentages.

| k | 1 | 2 | 3 | 4 | 6 | 8 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| recall@k | 43.2 | 64.1 | 74.0 | 79.8 | 86.1 | 88.8 | 90.4 |
| coverage@k | 16.8 | 39.3 | 53.7 | 61.9 | 72.3 | 77.0 | 80.0 |

MRR 0.853. Sent at top 6: recall 93.1, every gold table sent in 86.3 % of cases.

## By hardness

| Hardness | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| easy | 152 | 0.860 | 94.2 | 92.8 | 98.4 | 98.0 |
| medium | 485 | 0.829 | 87.5 | 78.8 | 92.5 | 87.2 |
| hard | 264 | 0.863 | 81.9 | 60.6 | 91.4 | 79.9 |
| extra | 321 | 0.877 | 83.5 | 62.3 | 93.1 | 84.7 |

## By database

| Database | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| works_cycles | 464 | 0.843 | 83.8 | 69.2 | 91.5 | 83.6 |
| mondial_geo | 293 | 0.856 | 82.8 | 63.5 | 90.8 | 81.9 |
| soccer_2016 | 258 | 0.967 | 97.5 | 93.0 | 99.7 | 98.8 |
| hockey | 207 | 0.727 | 81.7 | 65.7 | 91.8 | 83.1 |

## Gold tables most often not sent at top 6

196 gold-table misses over 167 cases.

| Database | Table | Misses | Median rank when missed |
|---|---|---:|---:|
| `hockey` | `goalies` | 13 | 11 |
| `hockey` | `scoring` | 13 | 11 |
| `works_cycles` | `person` | 12 | 28 |
| `mondial_geo` | `located` | 9 | 8 |
| `works_cycles` | `emailaddress` | 8 | 10.5 |
| `mondial_geo` | `borders` | 8 | 27.5 |
| `works_cycles` | `personcreditcard` | 7 | 18 |
| `mondial_geo` | `geo_mountain` | 7 | 10 |
| `works_cycles` | `businessentityaddress` | 6 | 7.5 |
| `mondial_geo` | `politics` | 6 | 11 |
| `mondial_geo` | `geo_desert` | 6 | 17.5 |
| `works_cycles` | `specialofferproduct` | 5 | 12 |
| `works_cycles` | `productvendor` | 5 | 15 |
| `mondial_geo` | `city` | 5 | 15 |
| `works_cycles` | `purchaseorderdetail` | 4 | 15 |

# Retrieval: `bird_train_large` / full, evidence on

Suite file SHA-256 `16a8c1d4fabd2fdcabb44a047422930e3693b9f448dcd444771e543423bbab49`.

1222 cases with gold tables. Ranking = `rag.rank_schema_chunks`, before foreign-key neighbours. Sent = `retrieve_schema_context(top_k=6)`, neighbours included, what a run's `schema_recall` records. Percentages.

| k | 1 | 2 | 3 | 4 | 6 | 8 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| recall@k | 46.5 | 68.7 | 78.8 | 83.7 | 88.7 | 90.9 | 92.5 |
| coverage@k | 17.9 | 45.2 | 59.8 | 68.2 | 76.7 | 80.8 | 83.9 |

MRR 0.891. Sent at top 6: recall 94.8, every gold table sent in 89.5 % of cases.

## By hardness

| Hardness | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| easy | 152 | 0.885 | 95.7 | 94.7 | 98.7 | 98.7 |
| medium | 485 | 0.858 | 90.1 | 82.5 | 94.5 | 90.3 |
| hard | 264 | 0.936 | 84.7 | 65.9 | 93.2 | 84.5 |
| extra | 321 | 0.907 | 86.8 | 68.2 | 94.9 | 88.2 |

## By database

| Database | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| works_cycles | 464 | 0.886 | 85.5 | 71.1 | 93.4 | 86.9 |
| mondial_geo | 293 | 0.896 | 88.7 | 74.1 | 94.6 | 89.1 |
| soccer_2016 | 258 | 0.965 | 98.3 | 95.3 | 99.9 | 99.6 |
| hockey | 207 | 0.804 | 84.2 | 69.6 | 92.1 | 83.6 |

## Gold tables most often not sent at top 6

147 gold-table misses over 128 cases.

| Database | Table | Misses | Median rank when missed |
|---|---|---:|---:|
| `hockey` | `goalies` | 12 | 10.5 |
| `hockey` | `scoring` | 12 | 10.5 |
| `works_cycles` | `person` | 11 | 28 |
| `mondial_geo` | `located` | 9 | 7 |
| `works_cycles` | `emailaddress` | 8 | 13 |
| `mondial_geo` | `politics` | 8 | 9.5 |
| `works_cycles` | `personcreditcard` | 7 | 28 |
| `works_cycles` | `specialofferproduct` | 6 | 10 |
| `mondial_geo` | `encompasses` | 6 | 8 |
| `works_cycles` | `businessentityaddress` | 5 | 9 |
| `works_cycles` | `salesperson` | 4 | 15.5 |
| `hockey` | `teamssc` | 4 | 8 |
| `mondial_geo` | `city` | 4 | 14 |
| `works_cycles` | `purchaseorderdetail` | 3 | 15 |
| `works_cycles` | `workorder` | 3 | 32 |

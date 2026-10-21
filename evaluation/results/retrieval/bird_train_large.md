# Retrieval: `bird_train_large` / full, evidence on

Suite file SHA-256 `16a8c1d4fabd2fdcabb44a047422930e3693b9f448dcd444771e543423bbab49`.

1222 cases with gold tables. Ranking = `rag.rank_schema_chunks`, before foreign-key neighbours. Sent = `retrieve_schema_context(top_k=6)`, neighbours included, what a run's `schema_recall` records. Percentages.

| k | 1 | 2 | 3 | 4 | 6 | 8 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| recall@k | 47.8 | 69.8 | 80.0 | 86.4 | 91.7 | 93.9 | 95.1 |
| coverage@k | 18.8 | 44.5 | 60.3 | 71.8 | 81.8 | 86.8 | 89.3 |

MRR 0.905. Sent at top 6: recall 97.1, every gold table sent in 93.9 % of cases.

## By hardness

| Hardness | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| easy | 152 | 0.903 | 97.7 | 96.7 | 99.0 | 98.7 |
| medium | 485 | 0.890 | 93.1 | 87.8 | 97.3 | 95.3 |
| hard | 264 | 0.930 | 89.0 | 74.6 | 95.6 | 90.2 |
| extra | 321 | 0.910 | 88.8 | 71.3 | 97.1 | 92.8 |

## By database

| Database | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| works_cycles | 464 | 0.923 | 90.6 | 80.4 | 96.3 | 92.5 |
| mondial_geo | 293 | 0.887 | 92.6 | 79.2 | 98.4 | 95.6 |
| soccer_2016 | 258 | 0.974 | 98.4 | 96.5 | 99.9 | 99.6 |
| hockey | 207 | 0.807 | 84.3 | 70.0 | 93.6 | 87.9 |

## Gold tables most often not sent at top 6

80 gold-table misses over 74 cases.

| Database | Table | Misses | Median rank when missed |
|---|---|---:|---:|
| `hockey` | `scoring` | 9 | 9 |
| `mondial_geo` | `politics` | 7 | 12 |
| `works_cycles` | `person` | 6 | 48.5 |
| `hockey` | `goalies` | 4 | 12 |
| `hockey` | `teamssc` | 4 | 7 |
| `works_cycles` | `purchaseorderdetail` | 3 | 7 |
| `works_cycles` | `employee` | 3 | 18 |
| `works_cycles` | `emailaddress` | 3 | 8 |
| `works_cycles` | `productreview` | 3 | 9 |
| `works_cycles` | `salesorderheader` | 3 | 15 |
| `works_cycles` | `businessentityaddress` | 3 | 14 |
| `hockey` | `hof` | 3 | 19 |
| `works_cycles` | `salesorderdetail` | 2 | 24 |
| `works_cycles` | `salesperson` | 2 | 7 |
| `works_cycles` | `personcreditcard` | 2 | 7.5 |

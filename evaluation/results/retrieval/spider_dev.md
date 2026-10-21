# Retrieval: `spider_dev` / full, evidence off

Suite file SHA-256 `04f185608f946e75e2a37a65b078b5925798de8e4b9950631acebaa2a6ae0091`.

1034 cases with gold tables. Ranking = `rag.rank_schema_chunks`, before foreign-key neighbours. Sent = `retrieve_schema_context(top_k=6)`, neighbours included, what a run's `schema_recall` records. Percentages.

| k | 1 | 2 | 3 | 4 | 6 | 8 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| recall@k | 73.1 | 93.3 | 99.0 | 99.5 | 99.8 | 100.0 | 100.0 |
| coverage@k | 53.4 | 85.4 | 97.4 | 98.9 | 99.6 | 99.9 | 99.9 |

MRR 0.975. Sent at top 6: recall 100.0, every gold table sent in 100.0 % of cases.

## By hardness

| Hardness | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| easy | 248 | 0.980 | 100.0 | 100.0 | 100.0 | 100.0 |
| medium | 446 | 0.973 | 100.0 | 100.0 | 100.0 | 100.0 |
| hard | 174 | 0.967 | 99.7 | 99.4 | 100.0 | 100.0 |
| extra | 166 | 0.979 | 99.3 | 98.2 | 100.0 | 100.0 |

## By database

| Database | Cases | MRR | recall@6 | coverage@6 | sent recall | sent coverage |
|---|---:|---:|---:|---:|---:|---:|
| world_1 | 120 | 0.967 | 100.0 | 100.0 | 100.0 | 100.0 |
| car_1 | 92 | 0.967 | 100.0 | 100.0 | 100.0 | 100.0 |
| cre_Doc_Template_Mgt | 84 | 0.887 | 100.0 | 100.0 | 100.0 | 100.0 |
| dog_kennels | 82 | 0.992 | 100.0 | 100.0 | 100.0 | 100.0 |
| flight_2 | 80 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |
| student_transcripts_tracking | 78 | 0.981 | 97.9 | 94.9 | 100.0 | 100.0 |
| tvshow | 62 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |
| wta_1 | 62 | 0.989 | 100.0 | 100.0 | 100.0 | 100.0 |
| network_1 | 56 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |
| concert_singer | 45 | 0.967 | 100.0 | 100.0 | 100.0 | 100.0 |
| pets_1 | 42 | 0.881 | 100.0 | 100.0 | 100.0 | 100.0 |
| orchestra | 40 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |
| poker_player | 40 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |
| employee_hire_evaluation | 38 | 0.987 | 100.0 | 100.0 | 100.0 | 100.0 |
| course_teach | 30 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |
| singer | 30 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |
| museum_visit | 18 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |
| battle_death | 16 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |
| voter_1 | 15 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |
| real_estate_properties | 4 | 1.000 | 100.0 | 100.0 | 100.0 | 100.0 |

## Gold tables most often not sent at top 6

0 gold-table misses over 0 cases.

| Database | Table | Misses | Median rank when missed |
|---|---|---:|---:|

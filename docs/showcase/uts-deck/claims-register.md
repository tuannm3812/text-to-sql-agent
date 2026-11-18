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

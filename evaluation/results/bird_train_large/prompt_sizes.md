# Prompt sizes: `bird_train_large` (1222 cases)

Characters of the whole prompt per arm, system prompt and question included. A case is over budget when its characters exceed 32768 tokens x 1.6 chars/token = 52,428 chars.

| Database | Cases | max plain_ddl | max ddl_with_hints | max top_6 |
|---|---:|---:|---:|---:|
| `hockey` | 207 | 13,674 | 19,191 | 11,227 |
| `mondial_geo` | 293 | 17,052 | 17,586 | 9,042 |
| `soccer_2016` | 258 | 8,516 | 9,408 | 8,201 |
| `works_cycles` | 464 | 40,514 | 49,417 | 21,939 |

## Over budget

No case exceeds the budget in any arm.

Largest prompt overall: `plain_ddl` 40,514 chars, `ddl_with_hints` 49,417 chars, `top_6` 21,939 chars.

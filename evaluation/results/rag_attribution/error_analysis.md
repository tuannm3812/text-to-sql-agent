# Error analysis: what the hint and selection flips are made of (2026-10-13)

A fixed, seeded sample of the questions that flipped between the three
attribution arms, each sorted into one cause. This answers Codex's 2026-10-12
next step: look at helped and hurt questions before choosing a hint-quality
change. No model was called. Every claim below comes from the saved
`cases.csv` rows, from re-rendering the prompt's schema text at HEAD, and from
running the saved SQL read-only against the benchmark databases.

## 1. Method

**Arms.** All three ran on commit `7708295` with the same model
(`qwen3.5:9b-q4_K_M`, think off) and the same questions. They differ only in
the schema text:

| Arm | Schema context | Spider dev run | BIRD dev (evidence on) run |
|---|---|---|---|
| A | plain full DDL, RAG off | `2026-10-11T033934_..._f934dfb5_9f67` | `2026-10-11T042329_..._2e606bf4_a071` |
| B | full DDL plus value hints, `top_k=0` | `2026-10-11T233024_..._3a2be932_2dea` | `2026-10-12T001558_..._8844615e_b6ed` |
| C | top-6 selected tables plus hints, `top_k=6` (shipped) | `2026-10-10T071608_..._a8ebee81_e6c2` | `2026-10-10T080619_..._22491cc9_3ef9` |

**Flips.** "Helped" means correct in the new arm and not in the old one, and
"hurt" means the reverse. This is the same rule `compare.py` uses, and the
pools match its counts exactly: A to B, BIRD 80 helped and 51 hurt, Spider 56
and 29; B to C, BIRD 78 helped and 101 hurt.

**Sampling.** Every pool was sorted by ID numerically, since all IDs are integer
strings. One `random.Random(20261013)` instance then drew each group with
`rng.sample`, in the order the table below lists them. Each group was larger
than its quota, so none was taken whole.

| Group | Pool | n | IDs |
|---|---:|---:|---|
| Hints, BIRD, helped (A to B) | 80 | 15 | 48, 152, 174, 238, 242, 505, 743, 776, 781, 1052, 1224, 1304, 1321, 1459, 1508 |
| Hints, BIRD, hurt (A to B) | 51 | 15 | 50, 319, 381, 393, 427, 485, 859, 1008, 1009, 1072, 1102, 1157, 1182, 1486, 1488 |
| Hints, Spider, helped (A to B) | 56 | 10 | 356, 525, 624, 632, 912, 921, 922, 923, 927, 958 |
| Hints, Spider, hurt (A to B) | 29 | 10 | 77, 233, 391, 448, 516, 566, 599, 891, 941, 1032 |
| Selection, BIRD, hurt (B to C) | 101 | 15 | 160, 174, 238, 348, 472, 849, 914, 927, 1053, 1089, 1186, 1256, 1317, 1416, 1436 |
| Selection, BIRD, helped (B to C) | 78 | 10 | 171, 194, 351, 689, 762, 800, 892, 1005, 1097, 1182 |

Three BIRD IDs fall in two groups: 174 and 238 (wrong in A, right in B, wrong
in C) and 1182 (right in A, wrong in B, right in C). Each flips at every
prompt change, so they are counted once per pair.

**Re-rendering.** The context for arm B and arm C was rebuilt with
`retrieve_schema_context(db_path, runner.question_text(case, evidence=...), top_k=0 | 6)`.
Arm A's context is `get_schema(db_path)`. For every case of both suites, the
re-rendered table set was compared with the run's `retrieved_tables` cell:
1034 Spider and 1534 BIRD cases in each of arms B and C. **No mismatch was
found.** Arm A records no retrieved tables, because RAG is off.

**Rubric.** Each case gets one primary cause and, optionally, a secondary one:

- **useful-value**: a hint supplied a literal or a spelling that the correct
  SQL needs, and the arm without hints lacked it.
- **misleading-hint**: a hint pushed the model toward a wrong value, column or
  table.
- **missing-table**: selection dropped a table that the gold SQL needs.
- **extra-context**: an extra table or extra hints distracted the model,
  although the right table or column was present.
- **noise**: the two SQL texts differ in ways the context change does not
  plausibly explain.
- **reference-or-scoring**: a gold-SQL quirk, an ordering or a strict
  comparison drives the flip, not the model's understanding. Here this
  includes strict projection: the losing SQL returns the gold rows but with an
  extra column or with the columns in a different order. The v2 comparator
  matches columns by position and count. Every such claim was checked by
  running both queries.

Noise is the default. A case got a context cause only when the context
difference plausibly explains the flip.

## 2. Summary

| Group | n | useful-value | misleading-hint | missing-table | extra-context | noise | reference-or-scoring |
|---|---:|---:|---:|---:|---:|---:|---:|
| Hints, BIRD, helped | 15 | **3** | 0 | 0 | 0 | 9 | 3 |
| Hints, BIRD, hurt | 15 | 0 | **1** | 0 | 0 | 13 | 1 |
| Hints, Spider, helped | 10 | **5** | 0 | 0 | 0 | 3 | 2 |
| Hints, Spider, hurt | 10 | 0 | **1** | 0 | 0 | 7 | 2 |
| Selection, BIRD, hurt | 15 | 0 | 0 | **0** | **0** | 12 | 3 |
| Selection, BIRD, helped | 10 | 0 | 0 | 0 | 0 | 9 | 1 |
| **All** | **75** | **8** | **2** | **0** | **0** | **53** | **12** |

Two checks over every flip, not just the sample, back up the table:

- **Selection never dropped a gold table on a flipped question.** None of the
  179 BIRD selection flips (101 hurt, 78 helped) has `schema_recall` below
  1.0 in arm C. Across all of BIRD dev, 30 of 1534 cases do. For 56 of the 101
  hurt flips and 38 of the 78 helped flips, arm C sent exactly arm B's table
  set, so the only change was the order of the tables. Arm C sends every
  table on 904 of the 1534 BIRD cases.
- **Using a hinted literal is lopsided toward helped flips.** This proxy asks
  whether the winning arm's SQL contains a quoted literal that the gold SQL
  also contains, that appears in some hint line, and that the losing arm's
  SQL lacks. It holds for 19 to 20 of the 80 BIRD helped flips, depending on
  whether case is compared exactly or not, against 1 of the 51 hurt. For
  Spider it holds for 3 to 5 of the 56 helped and 0 of the 29 hurt. The proxy
  is a lower bound: it misses a `LIKE '%value%'` pattern and a casing fix that
  goes through `LOWER()`, which is how three of the five Spider useful-value
  cases below were written.

## 3. Cases

Each hint line is quoted exactly as the prompt renders it, under the DDL of
the table named in parentheses. "Order-only" means that arm C sent the same
table set as arm B, in a different order.

### Hints, BIRD, helped (A wrong, B correct)

- **48** · *Ratio of merged Unified to merged Elementary School District
  schools in Orange County?*
  - SQL: A counts `frpm."District Type"` and never filters on merged; B uses
    `schools` with `StatusType = 'Merged' AND DOC = 54/52`.
  - Hint: `-- StatusType sample values: Active, Closed, Merged, Pending`
    (schools).
  - **useful-value.** The gold SQL needs `'Merged'`, the evidence does not
    say where it lives, and only arm B had the hint that shows it.
- **152** · *Average 1995 crimes in regions over 4000 with accounts opened
  from 1997?*
  - SQL: A joins `account`, so a district counts once per account; B uses
    `EXISTS`.
  - Hint: none relevant (`frequency`, `A3`, `A7`).
  - **noise.** Duplication from the join is unrelated to the hints.
- **174** · *What year was account owner number 130 born?*
  - SQL: A filters `client_id = 130`; B joins `disp` with
    `type = 'OWNER' AND account_id = 130`.
  - Hint: `-- type sample values: OWNER, DISPONENT` (disp).
  - **noise**, secondary useful-value. The flip turns on `account_id` against
    `client_id`. Arm C had the same hint, also wrote `'OWNER'`, and went back
    to `client_id = 130`.
- **238** · *How many molecules have a triple bond type?*
  - SQL: A uses `bond_type LIKE '%triple%'`, which returns 0; B uses `= '#'`
    with `COUNT(DISTINCT molecule_id)`.
  - Hint: `-- bond_type sample values: -, =, #` (bond).
  - **useful-value**, secondary noise. The evidence already says `'#'`, but A
    ignored it and the hint backed it up. The switch to `DISTINCT` is noise:
    arm C, with the same hint, dropped it.
- **242** · *Molecules among atoms 21 to 25 that are carcinogenic*
  - SQL: both arms use the same filter; A also projects `m.label`.
  - Hint: `-- label sample values: -, +` (molecule), used by both arms.
  - **reference-or-scoring.** The extra column is the only difference.
- **505** · *Simplified Chinese translation of the set "Mirrodin"*
  - SQL: both arms join on the same filter; A also projects `s.name`.
  - **reference-or-scoring.** The extra column is the only difference.
- **743** · *Percentage of "Bad" superheroes, and how many from Marvel*
  - SQL: A compares `publisher_name = 'marvel comics'` case-sensitively,
    which returns 0, and inner-joins `publisher` into the denominator; B uses
    subqueries.
  - Hint: `-- alignment sample values: Bad, Good, N/A, Neutral`. Both arms
    lowercase this column, and `publisher_name` has no hint.
  - **noise.**
- **776** · *Hero name and race of Charles Chandler*
  - SQL: A uses a non-existent `superhero.race` column; B joins `race`.
  - Hint: `race` has no hint lines.
  - **noise.**
- **781** · *Heights of heroes with amber eyes*
  - SQL: A compares `eye_colour_id` with `'amber'`; B joins `colour`.
  - Hint: `colour` has no hint lines.
  - **noise.**
- **1052** · *Players under 130 weight whose preferred foot is left*
  - SQL: A matches `player_api_id` against `Player.id`.
  - Hint: `-- preferred_foot sample values: right, left`. Both arms used
    `'left'`.
  - **noise.**
- **1224** · *Highest total bilirubin, with patient ID, sex and birthday*
  - SQL: both arms return the same values; A puts `T-BIL` last, and the gold
    SQL puts it first.
  - **reference-or-scoring.** Column order is the only difference.
- **1304** · *Patients with normal glucose and no thrombosis*
  - SQL: A adds a spurious `"aCL IgA" IS NULL` filter.
  - **noise.**
- **1321** · *Student_Club events Sacha Harrison attended in 2019*
  - SQL: A adds `e.type LIKE '%student_club%'`, which returns 0; B drops it.
  - Hint: `-- type sample values: Meeting, Guest Speaker, Game, Community Service, Social, Budget`
    (event).
  - **noise**, secondary useful-value. The hint may have shown that no event
    type matches, but it lists 6 of 8 values and supplies no literal the gold
    SQL needs.
- **1459** · *Major of Garrett Gerke, and its department*
  - SQL: A projects `link_to_major` instead of `major_name`.
  - Hint: `major_name` has no hint.
  - **noise.**
- **1508** · *Czech gas-station transactions over 1000*
  - SQL: A uses `LOWER(Country) = 'czech republic'`, which returns 0; B uses
    `'cze'`.
  - Hint: `-- Country sample values: CZE, SVK` (gasstations).
  - **useful-value.** The evidence says `'CZE'`, A ignored it, and the hint
    backed up the stored code.

### Hints, BIRD, hurt (A correct, B wrong)

- **50** · *Postal street of the school with the 7th-highest math average*
  - SQL: B switches to `frpm`, orders by the FRPM percentage and drops the
    offset.
  - **noise**, secondary reference-or-scoring. A was correct only because
    `Street = MailStreet` for that school; both arms selected `Street`.
- **319** · *How many elements are in bond TR001_3_4?*
  - SQL: B counts every atom of the molecule through `bond` and ignores
    `connected`.
  - Hint: none relevant (`bond_type`, `label`).
  - **noise.**
- **381** · *Artists for cards in Chinese Simplified*
  - SQL: A joins `foreign_data.language`, as the gold SQL does; B switches to
    `set_translations`.
  - Hints: `-- language sample values: Japanese, French, German, Italian, Spanish, Portuguese (Brazil)`
    (foreign_data), and `-- language sample values: Chinese Simplified, Chinese Traditional, French, German, Italian, Japanese`
    (set_translations).
  - **misleading-hint.** `foreign_data.language` has 16 distinct values.
    `'Chinese Simplified'` is the 7th most frequent, with 20,106 rows, so the
    six-value cap hides it. The only list that shows it belongs to the other
    table.
- **393** · *John Avon cards whose foil is non-powerful*
  - SQL: B drops the `cardKingdomId IS NULL` half of the `OR`.
  - **noise.**
- **427** · *Languages of the set Archenemy (ARC)*
  - SQL: B uses `foreign_data` through `cards`, and `sets.name` instead of the
    `mcmName` the evidence names.
  - Hint: both `language` lists are present, and B picks the table whose list
    shows no Chinese.
  - **noise.**
- **485** · *When was the ruling for 'Reminisce' created?*
  - SQL: B uses `= (subquery)`, which keeps only the first `uuid`, where A
    uses `IN`.
  - **noise.**
- **859** · *Bruno Senna's Q1 in race 354*
  - SQL: B writes `'BRUNO'` and `'SENNA'` in upper case.
  - Hint: `drivers` has no hint lines.
  - **noise.**
- **1008** · *Lap of Hamilton's pit stop, 2011 Australian GP*
  - SQL: B filters `circuits.name LIKE '%australia%'`, which matches nothing.
  - Hint: only `-- time sample values: ...` on races.
  - **noise.**
- **1009** · *Each driver's pit-stop time, 2011 Australian GP*
  - SQL: B adds a `driverId` column and a redundant join to `results`.
  - **reference-or-scoring.** Without the extra column, B's 45 rows equal the
    gold's 45 (`EXCEPT` is empty).
- **1072** · *Aaron Doran's average overall rating*
  - SQL: B joins `player_api_id = Player.id`.
  - **noise.** Arm B made the same mistake on 1097 and arm C fixed it there.
- **1102** · *Oldest player rated 77 on 2016-06-23*
  - SQL: B drops the join to `Player`, so the query fails to execute.
  - **noise.**
- **1157** · *ID, sex and disease of severe-thrombosis patients*
  - SQL: B takes `Diagnosis` from `Examination` instead of from `Patient`.
  - Hint: `Diagnosis` has no hint in either table.
  - **noise.**
- **1182** · *Lab tests in 1995 for the SJS patient first seen 1991-06-13*
  - SQL: B adds an inner join to `Examination`, which returns 0.
  - **noise.** Arm C, which also has the hints, drops the join again.
- **1486** · *How many more SMEs pay in CZK than in EUR?*
  - SQL: B emits `... AS difference; FROM customers`, and the guard refuses
    it.
  - Hint: `-- Segment sample values: SME, LAM, KAM`, used correctly.
  - **noise.**
- **1488** · *KAM customer who consumed the most*
  - SQL: B writes T-SQL `SELECT TOP 1`.
  - **noise.**

### Hints, Spider, helped (A wrong, B correct)

- **356** · *Template IDs with the description 'Presentation'*
  - SQL: A searches `Templates.Template_Details`; B joins
    `Ref_Template_Types.Template_Type_Description`.
  - Hint: `-- Template_Type_Description sample values: Advertisement, Book, CV, Paper, Presentation`.
  - **useful-value.** The hint shows which column holds the literal.
- **525** · *Names and IDs of courses with at most 2 sections*
  - SQL: both arms return the same rows; A puts the ID first.
  - **reference-or-scoring.** Column order is the only difference.
- **624** · *Series with the episode "A Love of a Lifetime"*
  - SQL: A looks in `Cartoon.Title`; B looks in `TV_series.Episode`.
  - Hint: `-- Episode sample values: A Love of a Lifetime, Blowback, ...`
    (TV_series).
  - **useful-value.** The exact literal appears in the hint.
- **632** · *Package options and series names of HD channels*
  - SQL: A uses `= 'Yes'`, which returns 0; B uses `LOWER(...) = 'yes'`.
  - Hint: `-- Hight_definition_TV sample values: no, yes`.
  - **useful-value.** The hint gives the stored spelling.
- **912** · *How many likes does Kyle have?*
  - SQL: A invents a `liked_name` column; B joins `Highschooler`.
  - Hint: `-- name sample values: Gabriel, Jordan, ...`, which omits Kyle.
  - **noise**, secondary reference-or-scoring. B counts likes received, while
    the gold SQL counts likes given. Both are 1.
- **921** · *Average age of dogs that had treatments*
  - SQL: A's join duplicates dogs; B uses `IN`.
  - **noise.**
- **922** · *Professionals in Indiana or with more than 2 treatments*
  - SQL: A uses `state = 'IN'`; B uses `'Indiana'`.
  - Hint: `-- state sample values: Connecticut, Indiana, Alabama, ...`
    (Professionals).
  - **useful-value.**
- **923** · *The same question, reworded*
  - SQL: A compares `state` with `LOWER('indiana')`; B uses `'Indiana'`.
  - Hint: the same line.
  - **useful-value.** The hint gives the stored casing.
- **927** · *First names used by professionals or owners but not by dogs*
  - SQL: A lowercases every output value.
  - **reference-or-scoring.** Text compares exactly, so A's set differs from
    the gold only in case.
- **958** · *Arrival and departure dates of treated dogs*
  - SQL: A drops the `DISTINCT` that the gold SQL has.
  - **noise.**

### Hints, Spider, hurt (A correct, B wrong)

- **77** · *Pet ID of the student with last name Smith*
  - SQL: B returns `StuID AS PetID` from `Has_Pet`, with no join.
  - **noise.**
- **233** · *Airlines with a flight departing from 'AHD'*
  - SQL: A's `= 'AHD'` returns no rows, the same as the gold SQL; B's
    `LIKE '%AHD%'` finds 8 airlines and adds extra columns.
  - **reference-or-scoring.** `SourceAirport` is stored as `' AHD'`, with a
    leading space, so the gold answer is empty and A matches it by accident.
- **391** · *Hometown of the youngest teacher*
  - SQL: B self-joins on a per-teacher `MIN` and returns every teacher.
  - **noise.**
- **448** · *Players who won in both 2013 and 2016*
  - SQL: B writes `UNION` where the question needs `INTERSECT`.
  - **noise.**
- **516** · *Department with the most degrees*
  - SQL: B drops the join to `Degree_Programs`.
  - **noise.**
- **566** · *Earliest transcript date and its details*
  - SQL: B truncates the date with `strftime('%Y-%m-%d', ...)`.
  - **noise.**
- **599** · *Content of the TV channel with series name "Sky Radio"*
  - SQL: B answers `UNANSWERABLE_WITH_GIVEN_SCHEMA`.
  - Hint: `-- series_name sample values: Classica, Hip Hop TV, MTV Classic, MTV Dance, MTV Hits, MTV Live HD`.
  - **misleading-hint.** The column has 15 distinct values. The six shown omit
    `'Sky Radio'`, and the model read the list as complete.
- **891** · *Names of Kyle's friends*
  - SQL: B returns Kyle's own name, because the self-join is missing.
  - **noise.**
- **941** · *Owner who spent the most on their dogs*
  - SQL: B leaks commented reasoning and a second `SELECT` into the SQL, which
    then fails to parse.
  - **noise.** The first draft joined `Charges`, but that table is in both
    arms' DDL.
- **1032** · *Property type descriptions of properties*
  - SQL: B adds `property_type_code` to an otherwise identical list.
  - **reference-or-scoring.** The extra column is the only difference, and
    the question's wording is ambiguous.

### Selection, BIRD, hurt (B correct, C wrong)

The gold tables were present in arm C for every one of these cases.

- **160** · *Weekly-issuance accounts with a loan under 200000* (order-only)
  - SQL: C writes `frequency = LOWER('POPLATEK TYDNE')`, which returns 0.
  - **noise.**
- **174** · *Birth year of account owner 130*
  - Tables: C drops `card` only.
  - SQL: C filters `client_id = 130` where B filters `account_id`.
  - **noise.**
- **238** · *Molecules with a triple bond* (order-only)
  - SQL: C writes `COUNT(*)` instead of `COUNT(DISTINCT molecule_id)`.
  - **noise.**
- **348** · *Rulings for Sublime Epiphany, number 74s* (order-only)
  - SQL: C adds the `date`, `name` and `number` columns.
  - **reference-or-scoring.** The rows match apart from the extra columns.
- **472** · *Ice Age sets with an Italian translation* (order-only)
  - SQL: C applies `LOWER(setCode)` and compares it against upper-case codes.
  - **noise.**
- **849** · *Where is the introduction of races at Barcelona-Catalunya?*
  - Tables: C sends 6 of 13 tables, with `races` ranked first and `circuits`
    third.
  - SQL: C returns `races.url` where the gold SQL uses `circuits.url`.
  - **noise.** Both tables are in both arms, and "races" in the question fits
    either reading.
- **914** · *How many drivers have no code?*
  - SQL: C writes `LOWER(code) = ''`, although the evidence says `IS NULL`.
  - **noise.**
- **927** · *Driver with the fastest lap speed*
  - SQL: C writes `ORDER BY CAST(fastestLapSpeed AS REAL)` and adds a column.
  - **reference-or-scoring.** The gold SQL orders this TEXT column
    lexically, so its "fastest" lap is `91.610` against a numeric maximum of
    `257.320`.
- **1053** · *Short names of teams whose passing class is Risky*
  - SQL: C adds `team_fifa_api_id` and groups by name.
  - **reference-or-scoring.** C returns the same 92 names as the gold SQL
    (`EXCEPT` is empty), plus the extra column.
- **1089** · *Matches in the 2008/2009 season held in Belgium*
  - SQL: C derives the season from `date` arithmetic, which returns 0.
  - Hint: the `Match` table and its hints are present in both arms.
  - **noise.**
- **1186** · *Behcet patients examined in 1997* (order-only)
  - SQL: C takes `Patient.Diagnosis` where the gold SQL uses
    `Examination.Diagnosis`.
  - **noise.**
- **1256** · *Abnormal-CRP patients with no data recorded* (order-only)
  - SQL: C counts joined lab rows instead of distinct patients.
  - **noise.**
- **1317** · *Medium-shirt members who attended Women's Soccer*
  - Tables: C drops `expense`.
  - SQL: C invents a `major.college = 'School of Business'` filter.
  - **noise.** `major` and its hint are present in both arms.
- **1416** · *Business members with a Medium tee shirt*
  - SQL: B filters `college LIKE '%Business%'`, which returns 1; C follows the
    evidence with `major_name LIKE '%business%'`, which returns 2.
  - **noise**, secondary reference-or-scoring. B matched the gold count by
    coincidence.
- **1436** · *Event links for members who paid more than 50* (order-only)
  - SQL: C joins `income` and references a non-existent `expense.event_id`.
  - **noise.**

### Selection, BIRD, helped (B wrong, C correct)

- **171** · *Crime difference between East and North Bohemia in 1996*
  - Tables: C drops `loan`.
  - SQL: B invents a `date` filter on `district`.
  - **noise.**
- **194** · *IDs and ages of gold-card owners*
  - SQL: B reverses the age subtraction.
  - **noise.**
- **351** · *Cards with a Japanese alternative language* (order-only)
  - SQL: B omits `DISTINCT`.
  - **noise.**
- **689** · *Last editor of post 183*
  - SQL: B joins on `LastEditorUserId`, which returns no rows.
  - **noise.**
- **762** · *Most common superpower* (order-only)
  - SQL: B adds a count column.
  - **reference-or-scoring.**
- **800** · *Percentage of heroes with blue eyes* (order-only)
  - SQL: B follows the evidence's wording to
    `superhero_name LIKE '%blue%'`; C joins `colour`.
  - **noise.**
- **892** · *Driver with the most points*
  - SQL: B uses `results.points`; C uses `driverStandings`.
  - **noise.** Both tables are present in both arms.
- **1005** · *Longest pit-stop time*
  - SQL: B over-parses `duration` and produces a syntax error.
  - **noise.**
- **1097** · *Aaron Lennox's total crossing score*
  - SQL: B joins `player_api_id = Player.id`.
  - **noise.** This is the same mistake as 1072.
- **1182** · *Lab tests in 1995 for the SJS patient* (order-only)
  - SQL: B adds the spurious `Examination` join.
  - **noise.**

## 4. Findings

- **Most of each effect is noise.** 53 of the 75 sampled flips (71 %) are
  noise and 12 (16 %) are reference-or-scoring artefacts. Only 10 have a
  context mechanism. The same questions flip at every byte-level prompt change
  (174, 238, 1182). Among the 25 selection flips, 11 occur when arm C sends
  arm B's exact table set, in a different order. That is the noise floor any
  paired change of 1 to 2 points sits on.
- **The hint gain is partly mechanistic, more clearly on Spider than on
  BIRD.**
  - Useful-value explains 5 of the 10 Spider helped flips, against 1 of the 10
    hurt. It explains 3 of the 15 BIRD helped flips, against 1 of the 15 hurt.
  - Scaled to the pools, roughly 25 of Spider's net +27 cases are
    mechanistic, against roughly 13 of BIRD's net +29. These are rough
    figures: a 3/15 share has a 95 % interval of about 7 to 45 %.
  - The literal proxy over all flips gives the same picture: a hinted literal
    decides 19 to 20 of the 80 BIRD helped flips and 1 of the 51 hurt.
  - Each useful value comes from a low-cardinality text column: a status, a
    code, a yes/no flag, a state name or an episode title. Two of the three
    BIRD cases (238, 1508) only confirmed a literal that the evidence already
    gave and that arm A ignored.
- **Selection's BIRD loss is not explained by dropped tables.** The sample
  has no missing-table or extra-context case. Across all 179 BIRD selection
  flips, arm C's schema recall is 1.0. For 94 of the 179, arm C sent every
  table and changed only their order. The -1.5 point result is consistent
  with noise plus scoring artefacts. These flips give no support to a "never
  drop foreign-key neighbours" change. At BIRD's sizes, top-6 selection
  mostly reorders the schema.
- **Both misleading hints come from one mechanism, truncation.** On 381 and
  599, a column with 7 to 20 distinct values is cut to its six most frequent,
  the needed literal is the hidden 7th or later, and the model reads the list
  as complete. On 381 it switched to the table whose list did show the value;
  on 599 it declared the question unanswerable.
  - A crude proxy finds about 58 BIRD and 65 Spider answerable cases whose
    gold SQL uses a literal hidden by the cap. Short literals can match by
    accident, so the proxy over-counts.
  - **The candidate supported by this evidence:** show every value when a
    column is under the existing cardinality ceiling of 20, or label a cut
    list explicitly ("6 of 16 shown"). Both are cheap, since a qualifying
    column adds at most 14 values.
  - **Not supported:** extending hints to high-cardinality columns. No
    sampled flip needed a literal from an unhinted column that a hint would
    plausibly have supplied.
- **How to measure that change.** Score it on the cases it targets, the
  truncation proxy set, as well as with the full paired run against these
  fixed arms. Report extra-column and column-order mismatches apart from real
  errors, since they make up 12 of the 75 flips here. Better still, repeat
  each arm, because a single run cannot separate a 1-point effect from this
  model's prompt sensitivity.
- **Limits.** The sample is small: 75 flips, at most 15 per group, so every
  share has an interval tens of points wide. There is one model
  (`qwen3.5:9b-q4_K_M`, think off) and one run per arm. One reader did the
  classification, with no second rater, and inferred mechanisms from the SQL
  text rather than from the model. Noise is a residual category, so some
  context effects may be hidden in it, and some cases called mechanistic may
  be chance.

## Reproduce

The sampling, re-rendering and proxy helpers are not committed. The sample
can be rebuilt from this file's seed and its sorting rule. All of it is
read-only and makes no model calls.

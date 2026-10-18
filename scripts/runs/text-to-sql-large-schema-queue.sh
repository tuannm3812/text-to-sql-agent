#!/bin/bash
# Waits for the BIRD-without-evidence refresh to finish, then pins the worktree to 47284f5,
# gives it the bird_train_large suite and databases, and runs the three attribution arms on
# subset200 (phase "large" of text-to-sql-hint-label-runs.sh).
export PATH="/opt/homebrew/bin:$PATH"
W="/Users/tuannm3812/Documents/GitHub/1. Study/text-to-sql-agent-release-runs"
M="/Users/tuannm3812/Documents/GitHub/1. Study/aipa-text-to-sql-agent"
A="/Users/tuannm3812/Documents/GitHub/1. Study/text-to-sql-release-runs-archive/fe90991-results-duplicates"
L="$W/large-schema-runs.log"
until grep -q "PHASE bird-noev DONE" "$W/hint-label-runs.log"; do sleep 120; done
echo "=== $(date '+%F %T') bird-noev finished; preparing the worktree" >> "$L"
cd "$W" || exit 1
mkdir -p "$A"
for d in evaluation/results/2026-10-17T1*/ evaluation/results/2026-10-09T202125*/; do
  [ -d "$d" ] && [ -d "$M/$d" ] && mv "$d" "$A/"   # identical to the committed copies
done
git checkout -q --detach 47284f5 || { echo "checkout failed" >> "$L"; exit 1; }
cp "$M/evaluation/suites/bird_train_large.jsonl" evaluation/suites/
mkdir -p data/benchmarks/bird/train_databases
for db in works_cycles mondial_geo hockey soccer_2016; do
  [ -d "data/benchmarks/bird/train_databases/$db" ] || cp -R "$M/data/benchmarks/bird/train_databases/$db" data/benchmarks/bird/train_databases/
done
uv sync --extra engines -q
echo "=== $(date '+%F %T') worktree at $(git rev-parse --short HEAD), status: $(git status --porcelain --untracked-files=no | wc -l) dirty" >> "$L"
exec caffeinate -i "/Users/tuannm3812/Documents/GitHub/1. Study/text-to-sql-hint-label-runs.sh" large

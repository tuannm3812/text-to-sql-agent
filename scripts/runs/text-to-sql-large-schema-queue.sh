#!/bin/bash
# Pins the release-runs worktree to 47284f5, gives it the bird_train_large suite and
# databases from the main checkout, and runs the three attribution arms on subset200
# (phase "large" of text-to-sql-hint-label-runs.sh). The BIRD-without-evidence refresh it
# used to wait for finished on 2026-10-18 and is committed as c5afea2.
export PATH="/opt/homebrew/bin:$PATH"
M="$(cd "$(dirname "$0")/../.." && pwd)"  # the repo root (main checkout)
W="$M/.worktrees/release-runs"
L="$M/evaluation/run_logs/large-schema-runs.log"
echo "=== $(date '+%F %T') preparing the worktree" >> "$L"
cd "$W" || exit 1
git checkout -q --detach 47284f5 || { echo "checkout failed" >> "$L"; exit 1; }
cp "$M/evaluation/suites/bird_train_large.jsonl" evaluation/suites/
mkdir -p data/benchmarks/bird/train_databases
for db in works_cycles mondial_geo hockey soccer_2016; do
  [ -d "data/benchmarks/bird/train_databases/$db" ] || cp -R "$M/data/benchmarks/bird/train_databases/$db" data/benchmarks/bird/train_databases/
done
uv sync --extra engines -q
echo "=== $(date '+%F %T') worktree at $(git rev-parse --short HEAD), status: $(git status --porcelain --untracked-files=no | wc -l) dirty" >> "$L"
exec caffeinate -i "$M/scripts/runs/text-to-sql-hint-label-runs.sh" large

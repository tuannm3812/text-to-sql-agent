#!/bin/bash
# bird_train_large full suite (1,222 questions), shipped top 6 with question value matching
# on, evidence on, at the trial commit tagged trial/value-matches-on (3acc3b6: 753b6e6 with
# DEFAULT_VALUE_MATCHES flipped to True). Baseline: the top-6 full run at 47284f5
# (2026-10-18T164708_..._82113302_30ea). Same model and settings as
# text-to-sql-large-schema-full-runs.sh.
# Re-running resumes an incomplete run of the same configuration; a complete run is skipped.
export PATH="/opt/homebrew/bin:$PATH"
R="$(cd "$(dirname "$0")/../.." && pwd)"  # the repo root
cd "$R/.worktrees/release-runs" || exit 1
L="$R/evaluation/run_logs/value-matches-runs.log"
failed=0
M=(--mode llm --provider ollama --model qwen3.5:9b-q4_K_M --ollama-think off --max-retries 2 --retry-base-seconds 10)
B=(--work-limit 1000000000 --max-rows 100000)
[ "$(git rev-parse --short HEAD)" = "3acc3b6" ] || { echo "worktree not at 3acc3b6" >> "$L"; exit 1; }
[ -f evaluation/suites/bird_train_large.jsonl ] || { echo "suite file missing" >> "$L"; exit 1; }
run() {  # $1 = glob fragment identifying the run's directory; rest = suite args
  local pat="$1"; shift
  local resume=()
  for d in evaluation/results/*_${pat}_*/; do
    [ -f "$d/manifest.json" ] || continue
    grep -q '"commit": "'"$(git rev-parse HEAD)"'"' "$d/manifest.json" || continue
    if grep -q '"status": "complete"' "$d/manifest.json"; then
      echo "=== $(date '+%F %T') SKIP complete $d" >> "$L"; return 0
    fi
    resume=(--resume "$d")
  done
  echo "=== $(date '+%F %T') START $* ${resume[*]}" >> "$L"
  uv run python scripts/evaluate_v2.py "$@" "${M[@]}" "${B[@]}" "${resume[@]}" >> "$L" 2>&1
  local status=$?  # before $(date) below, which would reset $?
  echo "=== $(date '+%F %T') END exit=$status $*" >> "$L"
  [ "$status" -eq 0 ] || failed=1
  return "$status"
}
run "bird_train_large_full_ollama_*rag-on-k6-evidence-on-think-off" --suite bird_train_large --subset full --evidence on
if [ "$failed" -eq 0 ]; then echo "ALL DONE $(date '+%F %T')" >> "$L"; else echo "FAILED $(date '+%F %T'): at least one run exited nonzero" >> "$L"; fi
exit "$failed"

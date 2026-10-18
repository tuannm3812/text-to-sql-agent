#!/bin/bash
# bird_train_large full suite (1,222 questions), the three attribution arms, evidence on, at
# 47284f5: plain DDL, full DDL plus hints (top-k 0), then the shipped top 6. Follows the
# subset200 arms in 1326954. Expects the release-runs worktree prepared by
# text-to-sql-large-schema-queue.sh (suite file and the four train databases present).
# Re-running resumes an incomplete run of the same configuration; complete runs are skipped.
export PATH="/opt/homebrew/bin:$PATH"
R="$(cd "$(dirname "$0")/../.." && pwd)"  # the repo root
cd "$R/.worktrees/release-runs" || exit 1
L="$R/evaluation/run_logs/large-schema-full-runs.log"
M=(--mode llm --provider ollama --model qwen3.5:9b-q4_K_M --ollama-think off --max-retries 2 --retry-base-seconds 10)
B=(--work-limit 1000000000 --max-rows 100000)
[ "$(git rev-parse --short HEAD)" = "47284f5" ] || { echo "worktree not at 47284f5" >> "$L"; exit 1; }
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
  echo "=== $(date '+%F %T') END exit=$? $*" >> "$L"
}
run "bird_train_large_full_ollama_*rag-off-evidence-on-think-off" --suite bird_train_large --subset full --evidence on --no-rag
run "bird_train_large_full_ollama_*rag-on-k0-evidence-on-think-off" --suite bird_train_large --subset full --evidence on --rag-top-k 0
run "bird_train_large_full_ollama_*rag-on-k6-evidence-on-think-off" --suite bird_train_large --subset full --evidence on
echo "ALL DONE $(date '+%F %T')" >> "$L"

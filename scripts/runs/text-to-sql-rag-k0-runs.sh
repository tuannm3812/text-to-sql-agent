#!/bin/bash
# RAG attribution arm: full DDL plus value hints (RAG on, top-k 0), commit 7708295.
# Re-running this script resumes any incomplete run of the same configuration.
export PATH="/opt/homebrew/bin:$PATH"
R="$(cd "$(dirname "$0")/../.." && pwd)"  # the repo root
cd "$R/.worktrees/release-runs" || exit 1
L="$R/evaluation/run_logs/rag-k0-runs.log"
failed=0
M=(--mode llm --provider ollama --model qwen3.5:9b-q4_K_M --ollama-think off --rag-top-k 0 --max-retries 2 --retry-base-seconds 10)
B=(--work-limit 1000000000 --max-rows 100000)
run() {
  local pat="$1"; shift
  local resume=()
  for d in evaluation/results/*_${pat}_*/; do
    [ -f "$d/manifest.json" ] || continue
    if grep -q '"status": "complete"' "$d/manifest.json"; then
      echo "=== $(date '+%F %T') SKIP complete $d" >> "$L"; return 0
    fi
    resume=(--resume "$d")
  done
  echo "=== $(date '+%F %T') START $* ${resume[*]}" >> "$L"
  uv run python scripts/evaluate_v2.py "$@" "${M[@]}" "${resume[@]}" >> "$L" 2>&1
  local status=$?  # before $(date) below, which would reset $?
  echo "=== $(date '+%F %T') END exit=$status $*" >> "$L"
  [ "$status" -eq 0 ] || failed=1
  return "$status"
}
run "demo_full_ollama_*rag-on-k0-evidence-off-think-off" --suite demo
run "spider_dev_full_ollama_*rag-on-k0-evidence-off-think-off" --suite spider_dev --subset full "${B[@]}"
run "bird_dev_full_ollama_*rag-on-k0-evidence-on-think-off" --suite bird_dev --subset full --evidence on "${B[@]}"
if [ "$failed" -eq 0 ]; then echo "ALL DONE $(date '+%F %T')" >> "$L"; else echo "FAILED $(date '+%F %T'): at least one run exited nonzero" >> "$L"; fi
exit "$failed"

#!/bin/bash
# Full v2 release runs with Ollama thinking off (decided 2026-10-10): Spider dev, then BIRD dev
# with evidence on and off. Re-running this script resumes any incomplete run of the same
# configuration instead of starting a new one; complete runs are skipped.
export PATH="/opt/homebrew/bin:$PATH"
cd "/Users/tuannm3812/Documents/GitHub/1. Study/text-to-sql-agent-release-runs" || exit 1
L="release-runs-think-off.log"
M=(--mode llm --provider ollama --model qwen3.5:9b-q4_K_M --ollama-think off --max-retries 2 --retry-base-seconds 10)
B=(--work-limit 1000000000 --max-rows 100000)
run() {  # $1 = glob fragment identifying the run's directory; rest = suite args
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
  uv run python scripts/evaluate_v2.py "$@" "${M[@]}" "${B[@]}" "${resume[@]}" >> "$L" 2>&1
  echo "=== $(date '+%F %T') END exit=$? $*" >> "$L"
}
run "spider_dev_full_ollama_*evidence-off-think-off" --suite spider_dev --subset full
run "bird_dev_full_ollama_*evidence-on-think-off" --suite bird_dev --subset full --evidence on
run "bird_dev_full_ollama_*evidence-off-think-off" --suite bird_dev --subset full --evidence off
echo "ALL DONE $(date '+%F %T')" >> "$L"

#!/bin/bash
# Partial-list hint label trial (fe90991): shipped settings (RAG on, top 6, think off).
# Phase "target": the hiddenlit subsets. Phase "full": Spider dev, then BIRD dev with evidence.
# Re-running resumes an incomplete run of the same configuration; complete runs are skipped.
export PATH="/opt/homebrew/bin:$PATH"
cd "/Users/tuannm3812/Documents/GitHub/1. Study/text-to-sql-agent-release-runs" || exit 1
L="hint-label-runs.log"
M=(--mode llm --provider ollama --model qwen3.5:9b-q4_K_M --ollama-think off --max-retries 2 --retry-base-seconds 10)
B=(--work-limit 1000000000 --max-rows 100000)
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
if [ "$1" = "target" ]; then
  run "spider_dev_hiddenlit_ollama_*rag-on-k6-evidence-off-think-off" --suite spider_dev --subset hiddenlit
  run "bird_dev_hiddenlit_ollama_*rag-on-k6-evidence-on-think-off" --suite bird_dev --subset hiddenlit --evidence on
elif [ "$1" = "bird-noev" ]; then
  run "bird_dev_full_ollama_*rag-on-k6-evidence-off-think-off" --suite bird_dev --subset full --evidence off
elif [ "$1" = "large" ]; then  # bird_train_large subset200, the three attribution arms
  L="large-schema-runs.log"
  run "bird_train_large_subset200_ollama_*rag-off-evidence-on-think-off" --suite bird_train_large --subset subset200 --evidence on --no-rag
  run "bird_train_large_subset200_ollama_*rag-on-k0-evidence-on-think-off" --suite bird_train_large --subset subset200 --evidence on --rag-top-k 0
  run "bird_train_large_subset200_ollama_*rag-on-k6-evidence-on-think-off" --suite bird_train_large --subset subset200 --evidence on
elif [ "$1" = "full" ]; then
  run "spider_dev_full_ollama_*rag-on-k6-evidence-off-think-off" --suite spider_dev --subset full
  run "bird_dev_full_ollama_*rag-on-k6-evidence-on-think-off" --suite bird_dev --subset full --evidence on
fi
echo "PHASE $1 DONE $(date '+%F %T')" >> "$L"

#!/bin/bash
# One review round by Google Antigravity (agy CLI, Gemini 4 Hydrogen). Replaces Codex as
# the reviewer in the local review loop (owner's request, 2026-11-25); codex_review.sh is
# kept for history. Usage: scripts/agents/antigravity_review.sh <git range> [model]
#   e.g. scripts/agents/antigravity_review.sh 269ed8f..HEAD
# agy runs in plan mode inside its sandbox, so it cannot edit the repository. This script,
# not the agent, appends the review as one "Antigravity to Claude" entry at the end of
# docs/6_agent_log.md. The raw transcript goes to a temporary file outside the repository.
# AGY_BIN may point at a stub to test the launcher without a model call.
set -euo pipefail
RANGE="${1:?usage: antigravity_review.sh <git range> [model]}"
MODEL="${2:-${AGY_MODEL:-gemini-4-hydrogen-high}}"
R="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$R"
AGY="${AGY_BIN:-$(command -v agy || echo "$HOME/.local/bin/agy")}"
[ -x "$AGY" ] || { echo "antigravity_review: agy CLI not found" >&2; exit 2; }
git rev-parse --verify --quiet "${RANGE%%..*}^{commit}" >/dev/null \
  || { echo "antigravity_review: bad range start: $RANGE" >&2; exit 2; }
if [[ "$RANGE" == *..* ]]; then
  git rev-parse --verify --quiet "${RANGE##*..}^{commit}" >/dev/null \
    || { echo "antigravity_review: bad range end: $RANGE" >&2; exit 2; }
fi
TEMPLATE="$(cat scripts/agents/antigravity_review_prompt.md)"
PROMPT="${TEMPLATE//\{RANGE\}/$RANGE}"
[[ "$PROMPT" == *"$RANGE"* && "$PROMPT" != *"{RANGE}"* ]] \
  || { echo "antigravity_review: could not build the prompt" >&2; exit 2; }
LOGFILE="docs/6_agent_log.md"
RAW="${TMPDIR:-/tmp}/antigravity-review-$(date +%Y%m%dT%H%M%S).log"
status=0
"$AGY" --print "$PROMPT" --model "$MODEL" --mode plan --sandbox \
  --print-timeout 0s > "$RAW" 2>&1 || status=$?
if [ "$status" -eq 0 ] && [ -s "$RAW" ]; then
  # agy links files by absolute local path; make them relative to docs/.
  BODY="$(sed "s#file://$R/#../#g" "$RAW")"
  FIRST="$(printf '%s\n' "$BODY" | grep -m1 -v '^[[:space:]]*$' || true)"
  {
    echo
    if [[ "$FIRST" != "## "*"Antigravity to Claude"* ]]; then
      echo "## $(date +%Y-%m-%d) — Antigravity to Claude: review of $RANGE"
      echo
    fi
    printf '%s\n' "$BODY"
    echo
    echo "_Antigravity CLI (agy), model $MODEL, plan mode (read-only), on $RANGE" \
      "($(git rev-parse --short "${RANGE##*..}")); appended by antigravity_review.sh._"
  } >> "$LOGFILE"
fi
echo "agy model=$MODEL exit=$status log=$LOGFILE raw=$RAW"
exit "$status"

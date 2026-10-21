#!/bin/bash
# Start one Codex review round of the local Claude <-> Codex loop (owner's request,
# 2026-10-22). Usage: scripts/agents/codex_review.sh <range>, e.g. 140a816..HEAD.
# Uses the owner's own Codex config and sign-in (~/.codex), pinned to the model and effort
# the Codex app uses, sandboxed to this workspace, with no network beyond defaults. Codex
# appends one entry to docs/6_agent_log.md and nothing else; Codex's own transcript goes to
# a temporary file outside the repository (its path is printed), not into the repo.
set -u
RANGE="${1:?usage: codex_review.sh <git range>}"
R="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$R" || exit 1
LOG="${TMPDIR:-/tmp}/codex-review-$(date +%Y%m%dT%H%M%S).log"
PROMPT="$(sed "s/{RANGE}/$RANGE/" scripts/agents/codex_review_prompt.md)"
codex exec -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write \
  "$PROMPT" > "$LOG" 2>&1
status=$?
echo "codex exit=$status log=$LOG"
exit "$status"

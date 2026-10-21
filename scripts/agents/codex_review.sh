#!/bin/bash
# Start one Codex review round of the local Claude <-> Codex loop (owner's request,
# 2026-10-22). Usage: scripts/agents/codex_review.sh <range>, e.g. 140a816..HEAD.
# CODEX_BIN may point at a stub to test the launcher without a model call.
# Uses the owner's own Codex config and sign-in (~/.codex), pinned to the model and effort
# the Codex app uses, sandboxed to this workspace, with no network beyond defaults. Codex
# appends one entry to docs/6_agent_log.md and nothing else; Codex's own transcript goes to
# a temporary file outside the repository (its path is printed), not into the repo.
set -euo pipefail
RANGE="${1:?usage: codex_review.sh <git range>}"
R="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$R" || exit 1
LOG="${TMPDIR:-/tmp}/codex-review-$(date +%Y%m%dT%H%M%S).log"
# The CLI the Codex app itself ships is current with the app's model; the standalone one
# in ~/.local/bin can lag (0.145 rejected gpt-6-astra, 2026-10-22). CODEX_BIN overrides.
APP_CODEX="/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"
CODEX="${CODEX_BIN:-$([ -x "$APP_CODEX" ] && echo "$APP_CODEX" || command -v codex)}"
# The range must name commits, and it goes into the prompt as literal text: `sed s///`
# broke on the slash in this repo's branch name and left an empty prompt (Codex,
# 2026-10-22).
git rev-parse --verify --quiet "${RANGE%%..*}^{commit}" >/dev/null \
  || { echo "codex_review: bad range start: $RANGE" >&2; exit 2; }
if [[ "$RANGE" == *..* ]]; then
  git rev-parse --verify --quiet "${RANGE##*..}^{commit}" >/dev/null \
    || { echo "codex_review: bad range end: $RANGE" >&2; exit 2; }
fi
TEMPLATE="$(cat scripts/agents/codex_review_prompt.md)"
PROMPT="${TEMPLATE//\{RANGE\}/$RANGE}"
[[ -n "$PROMPT" && "$PROMPT" == *"$RANGE"* && "$PROMPT" != *"{RANGE}"* ]] \
  || { echo "codex_review: could not build the prompt" >&2; exit 2; }
status=0
"$CODEX" exec -m gpt-6-astra -c model_reasoning_effort=high -s workspace-write \
  "$PROMPT" > "$LOG" 2>&1 || status=$?
echo "codex ($("$CODEX" --version)) exit=$status log=$LOG"
exit "$status"

#!/usr/bin/env bash
# Observation-only PreToolUse hook. Records that a dispatch happened. Blocks nothing, ever.
#
# RUNTIME FAIL-OPEN, MEASUREMENT FAIL-CLOSED. A hook that can stop work is the opposite of
# what an observation phase needs, so every path here ends in exit 0 -- failures included.
# If it cannot write, it stays quiet and the reconciler notices: the dispatch appears in the
# transcript with no matching record and coverage drops. Silence is caught downstream.
#
# Deliberately stupid: no classification, no policy lookup, no network, no database. Any of
# those could hang, and a hook that hangs delays a dispatch even though it never blocks one.
set +e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="${CLAUDE_OBSERVER_LOG_DIR:-$HOME/.claude/observer}"
mkdir -p "$LOG_DIR" 2>/dev/null
# No `timeout` here. macOS ships without it unless coreutils is installed, so the wrapper
# silently found no command, wrote nothing, and still exited 0 -- the third silent failure
# this observer produced inside itself before observing anything. A hook that depends on a
# tool the host may not have is a hook that reports success while doing nothing.
#
# The bound is applied in Python instead, where it cannot go missing.
python3 "$DIR/observe_dispatch.py" "$LOG_DIR/dispatch.jsonl" "0.1.0" >/dev/null 2>&1
exit 0

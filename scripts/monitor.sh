#!/usr/bin/env bash
set -euo pipefail

# ClaudeHQ — Monitor: Watch running sessions and detect stuck projects
# This is called by `hq monitor` but can also be run standalone

HQ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$HQ_DIR/scripts/hq" monitor "$@"

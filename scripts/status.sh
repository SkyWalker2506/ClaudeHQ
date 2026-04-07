#!/usr/bin/env bash
set -euo pipefail

# ClaudeHQ — Status: Aggregate status dashboard
# This is called by `hq status` but can also be run standalone

HQ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$HQ_DIR/scripts/hq" status "$@"

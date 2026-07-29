#!/usr/bin/env python3
"""Writes one line per observed dispatch. Called by observe_dispatch.sh; never blocks.

Split out of the shell wrapper because the first version inlined it as a heredoc alongside a
here-string, which is not valid and made the hook exit 0 while writing nothing. Exit code
said success, log stayed empty -- the exact silent failure this whole phase exists to catch,
produced inside the observer itself and caught only because the test checked the log rather
than the exit status.
"""

import datetime
import hashlib
import json
import signal
import sys

#: Wall-clock bound, enforced here rather than by an external `timeout` binary that macOS
#: does not ship. The hook never blocks a dispatch, but it can still delay one, and a
#: dependency that may be absent is not a bound at all.
TIME_LIMIT_SECONDS = 5


def main():
    try:
        signal.signal(signal.SIGALRM, lambda *_: sys.exit(0))
        signal.alarm(TIME_LIMIT_SECONDS)
    except Exception:
        pass
    log_path, version = sys.argv[1], sys.argv[2]
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        payload = {}
    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    record = {
        "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "session_id": payload.get("session_id") or payload.get("sessionId"),
        "tool_use_id": payload.get("tool_use_id") or payload.get("toolUseId"),
        "tool_name": payload.get("tool_name") or payload.get("toolName"),
        "input_sha256": hashlib.sha256(
            json.dumps(tool_input, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest(),
        "observer_version": version,
        "status": "ok",
    }
    with open(log_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()

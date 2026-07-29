#!/usr/bin/env python3
"""exactly_once_hook_observation_coverage — did the observer see every dispatch, once?

The denominator never comes from the observer's own log. That is the whole point: a hook that
misses a dispatch also drops it from the denominator and reports excellent coverage, which is
how this ecosystem already produced a "zero violations" figure that was really UNDEFINED.
Truth comes from the transcripts, which the observer does not write.

Plain coverage is not enough either. A record can be duplicated, attached to the wrong
session, or invented, and a simple count would forgive all three. So the invariants are:

    exactly_once_hook_observation_coverage == 100%
    orphan_hook_record_count == 0

Runtime is fail-open; measurement is fail-closed. The hook never blocks. This does not
forgive.

    python3 reconcile_coverage.py [--since 2026-07-29]
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

DISPATCH_TOOLS = {"Agent", "Task"}


def transcript_dispatches(root):
    """(session_id, tool_use_id) for every dispatch the transcripts record."""
    found = {}
    for path in sorted(glob.glob(os.path.join(root, "*", "*.jsonl"))):
        for line in open(path, encoding="utf-8", errors="ignore"):
            try:
                record = json.loads(line)
            except Exception:
                continue
            session = record.get("sessionId") or record.get("session_id")
            content = (record.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if (isinstance(block, dict) and block.get("type") == "tool_use"
                        and block.get("name") in DISPATCH_TOOLS and block.get("id")):
                    found[(session, block["id"])] = {"tool": block["name"], "transcript": path}
    return found


def observer_records(log_path):
    counts = collections.Counter()
    malformed = 0
    if not os.path.isfile(log_path):
        return counts, malformed
    for line in open(log_path, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except Exception:
            malformed += 1
            continue
        counts[(record.get("session_id"), record.get("tool_use_id"))] += 1
    return counts, malformed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcripts", default=os.path.expanduser("~/.claude/projects"))
    parser.add_argument("--log", default=os.path.expanduser("~/.claude/observer/dispatch.jsonl"))
    args = parser.parse_args()

    truth = transcript_dispatches(args.transcripts)
    observed, malformed = observer_records(args.log)

    if not truth:
        print("PAYDA URETILEMEDI: transcript'lerde dispatch bulunamadi.", file=sys.stderr)
        print("SONUC: UNKNOWN (basarisiz degil — olculemedi)", file=sys.stderr)
        return 2

    exactly_once = sum(1 for key in truth if observed.get(key, 0) == 1)
    duplicated = sum(1 for key in truth if observed.get(key, 0) > 1)
    missing = sum(1 for key in truth if observed.get(key, 0) == 0)
    orphans = sum(count for key, count in observed.items() if key not in truth)

    coverage = 100.0 * exactly_once / len(truth)

    print(f"transcript dispatch (payda) : {len(truth)}")
    print(f"gozlemci kaydi              : {sum(observed.values())}"
          f"  (bozuk satir: {malformed})")
    print()
    print(f"tam bir kez eslesen         : {exactly_once}")
    print(f"eksik                       : {missing}")
    print(f"mukerrer                    : {duplicated}")
    print(f"oksuz (transcript'te yok)   : {orphans}")
    print()
    print(f"exactly_once_hook_observation_coverage = {coverage:.2f}%   (hedef 100.00%)")
    print(f"orphan_hook_record_count               = {orphans}         (hedef 0)")

    ok = coverage == 100.0 and orphans == 0 and malformed == 0
    print(f"\nSONUC: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

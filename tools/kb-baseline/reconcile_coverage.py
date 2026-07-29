#!/usr/bin/env python3
"""exactly_once_hook_observation_coverage — did the observer see every dispatch, once?

The denominator never comes from the observer's own log. A hook that misses a dispatch also
drops it from its own denominator and then reports excellent coverage, which is how this
ecosystem already produced a "zero violations" figure that was really UNDEFINED.

Three defects in the first version, all found by adversarial review rather than by testing,
and all of the same family: the denominator was independent but not COMPLETE.

  1. Subagent transcripts live one level deeper, under <sessionId>/subagents/. The glob saw
     only depth 2, so 237 of 926 dispatches -- 26 percent, intersection with depth 2 exactly
     zero -- were structurally outside the universe being measured. Coverage could have read
     100 percent while saying nothing about a quarter of all dispatches.

  2. Keying on (session_id, tool_use_id) counts one dispatch twice when a session is resumed
     or forked, because the new session file carries the old history. 19 ids appear under two
     different session ids here, which makes 100 percent unreachable by construction.

  3. --since was documented and not implemented, so the window spanned all history: 689
     historical dispatches against an empty observer log reads as roughly zero, which pushes
     the operator toward a hand-picked filter. That is the opening a false PASS walks through.
     The floor is now a recorded installation fact, and a manual window is announced loudly.

Runtime is fail-open; measurement is fail-closed. The hook never blocks. This does not forgive.

    python3 reconcile_coverage.py
    python3 reconcile_coverage.py --since 2026-07-29T14:00:00Z   # announced as hand-picked
"""

from __future__ import annotations

import argparse
import collections
import datetime
import glob
import json
import os
import sys

DISPATCH_TOOLS = {"Agent", "Task"}
DEFAULT_MARKER = os.path.expanduser("~/.claude/observer/installed_at.json")
DEFAULT_LOG = os.path.expanduser("~/.claude/observer/dispatch.jsonl")
DEFAULT_ROOT = os.path.expanduser("~/.claude/projects")


def parse_time(value):
    if not value:
        return None
    try:
        return datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def transcript_files(root):
    """Both depths. Subagent transcripts sit under <sessionId>/subagents/ and carry the
    parent's sessionId, so a glob that stops at depth 2 silently excludes every nested
    dispatch."""
    return sorted(set(glob.glob(os.path.join(root, "*", "*.jsonl")))
                  | set(glob.glob(os.path.join(root, "*", "*", "subagents", "*.jsonl")))
                  | set(glob.glob(os.path.join(root, "*", "*", "*.jsonl"))))


def transcript_dispatches(root, since):
    """tool_use_id -> {sessions, first_seen, tool}. Keyed by id ALONE: a resumed session
    replays the same tool_use_id under a new sessionId, and a compound key would count one
    dispatch as two and make the target unreachable."""
    found = {}
    for path in transcript_files(root):
        try:
            handle = open(path, encoding="utf-8", errors="ignore")
        except OSError:
            continue
        with handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except Exception:
                    continue
                content = (record.get("message") or {}).get("content")
                if not isinstance(content, list):
                    continue
                stamp = parse_time(record.get("timestamp"))
                for block in content:
                    if not (isinstance(block, dict) and block.get("type") == "tool_use"
                            and block.get("name") in DISPATCH_TOOLS and block.get("id")):
                        continue
                    if since and stamp and stamp < since:
                        continue
                    if since and not stamp:
                        continue          # undatable record cannot be placed in the window
                    entry = found.setdefault(block["id"],
                                             {"sessions": set(), "first_seen": stamp,
                                              "tool": block["name"]})
                    entry["sessions"].add(record.get("sessionId"))
                    if stamp and (entry["first_seen"] is None or stamp < entry["first_seen"]):
                        entry["first_seen"] = stamp
    return found


def observer_records(log_path, since):
    counts = collections.Counter()
    malformed = 0
    before_window = 0
    if not os.path.isfile(log_path):
        return counts, malformed, before_window
    for line in open(log_path, encoding="utf-8", errors="ignore"):
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except Exception:
            malformed += 1
            continue
        stamp = parse_time(record.get("observed_at"))
        if since and stamp and stamp < since:
            before_window += 1
            continue
        counts[record.get("tool_use_id")] += 1
    return counts, malformed, before_window


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcripts", default=DEFAULT_ROOT)
    parser.add_argument("--log", default=DEFAULT_LOG)
    parser.add_argument("--marker", default=DEFAULT_MARKER)
    parser.add_argument("--since", help="ISO time. Announced as hand-picked; the default "
                                        "floor is the recorded installation moment.")
    args = parser.parse_args()

    hand_picked = bool(args.since)
    since = parse_time(args.since)
    if not since and os.path.isfile(args.marker):
        with open(args.marker, encoding="utf-8") as handle:
            since = parse_time(json.load(handle).get("installed_at"))

    if since is None:
        print("PENCERE TABANI YOK: kurulum isaretcisi bulunamadi ve --since verilmedi.",
              file=sys.stderr)
        print("SONUC: UNKNOWN (basarisiz degil — olculemedi)", file=sys.stderr)
        return 2

    print(f"pencere tabani : {since.isoformat()}"
          + ("   *** ELLE SECILDI — pencereyi daraltmak sahte PASS'in giris kapisidir ***"
             if hand_picked else "   (kayitli kurulum ani)"))

    truth = transcript_dispatches(args.transcripts, since)
    observed, malformed, before_window = observer_records(args.log, since)

    files = len(transcript_files(args.transcripts))
    print(f"taranan transcript dosyasi: {files}")

    if not truth:
        print("\nPAYDA BOS: pencerede hic dispatch yok.")
        print("SONUC: UNKNOWN — gozlemci kuruldu ama olcecek bir sey olusmadi.")
        print("       Yeni bir oturumda birkac ajan cagirip tekrar calistirin.")
        return 2

    exactly_once = sum(1 for key in truth if observed.get(key, 0) == 1)
    duplicated = sum(1 for key in truth if observed.get(key, 0) > 1)
    missing = sum(1 for key in truth if observed.get(key, 0) == 0)
    orphans = sum(count for key, count in observed.items() if key not in truth)
    resumed = sum(1 for entry in truth.values() if len(entry["sessions"]) > 1)

    coverage = 100.0 * exactly_once / len(truth)

    print(f"\ntranscript dispatch (payda) : {len(truth)}")
    print(f"gozlemci kaydi (pencerede)  : {sum(observed.values())}"
          f"   (pencere oncesi atlanan: {before_window})")
    if resumed:
        print(f"birden fazla oturumda gorunen (resume/fork): {resumed}"
              f"  — id ile anahtarlandigi icin tek sayiliyor")
    print()
    print(f"tam bir kez eslesen : {exactly_once}")
    print(f"eksik               : {missing}")
    print(f"mukerrer            : {duplicated}")
    print(f"oksuz               : {orphans}")
    print(f"bozuk satir         : {malformed}")
    print()
    print(f"exactly_once_hook_observation_coverage = {coverage:6.2f}%   (hedef 100.00)")
    print(f"orphan_hook_record_count               = {orphans:6d}     (hedef 0)")
    print(f"malformed_hook_record_count            = {malformed:6d}     (hedef 0)")
    print(f"duplicate_match_count                  = {duplicated:6d}     (hedef 0)")

    ok = coverage == 100.0 and orphans == 0 and malformed == 0 and duplicated == 0
    print(f"\nSONUC: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

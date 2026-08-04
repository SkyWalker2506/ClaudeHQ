#!/usr/bin/env python3
"""
hq history profile — context budget profiler for Claude Code sessions.

Answers the Colibri question ("how much of the time was work, and how much was
just loading?") for our own context pipeline:

  DENSE   preamble paid on every single session (CLAUDE.md chain, MEMORY.md, hooks)
  STREAM  context pulled in mid-task by tools (Read/Bash/Agent/MCP results)
  WORK    tokens actually produced (thinking + text + tool arguments)

Token figures for STREAM/DENSE are approximations (chars/4) — the transcript
does not record per-tool-result token counts. Marked with '~' in the output.
Absolute values carry maybe +/-15%; ratios and trends are sound.

Read-only. Never writes to the transcript directory.
"""

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path(
    os.environ.get("CLAUDE_SESSIONS_DIR", Path.home() / ".claude" / "projects")
)
HOME = Path.home()

# Tool name -> reporting bucket
MCP_PREFIX = "mcp__"


def approx_tokens(chars):
    return chars // 4


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def project_of_dir(d):
    """~/.claude/projects/-Users-musabkara-Projects-Foo -> Foo"""
    return d.name.rsplit("-", 1)[-1]


def fmt_tok(n):
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def fmt_dur(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def pct(part, whole):
    return (part / whole * 100) if whole else 0.0


# ---------------------------------------------------------------- session pass


class SessionProfile:
    def __init__(self, path):
        self.path = path
        self.cwd = None
        self.started = None
        self.ended = None
        self.out_tokens = 0
        self.cache_read = 0
        self.cache_creation = 0
        self.stream_chars = Counter()  # tool name -> result chars
        self.tool_calls = Counter()  # tool name -> call count
        self.hook_chars = Counter()  # hook name -> preamble chars
        self.wait_seconds = 0.0
        self.gen_seconds = 0.0
        self.reads = Counter()  # file path -> read count
        self.effort = Counter()
        self.sidechain_out = 0
        self.turns = 0
        self.gen_measured = 0  # assistant turns with a measurable latency
        self.mentions = set()  # *.md / [[wikilink]] names seen anywhere


def usage_out(usage):
    """Top-level output_tokens is sometimes 0 with the real count in iterations."""
    if not isinstance(usage, dict):
        return 0, 0, 0
    out = usage.get("output_tokens") or 0
    cr = usage.get("cache_read_input_tokens") or 0
    cc = usage.get("cache_creation_input_tokens") or 0
    iters = usage.get("iterations") or []
    if isinstance(iters, list) and iters:
        i_out = sum(i.get("output_tokens") or 0 for i in iters)
        i_cr = sum(i.get("cache_read_input_tokens") or 0 for i in iters)
        i_cc = sum(i.get("cache_creation_input_tokens") or 0 for i in iters)
        out = max(out, i_out)
        cr = max(cr, i_cr)
        cc = max(cc, i_cc)
    return out, cr, cc


def content_chars(content):
    if isinstance(content, str):
        return len(content)
    if isinstance(content, list):
        total = 0
        for b in content:
            if isinstance(b, dict):
                total += len(b.get("text") or "")
            elif isinstance(b, str):
                total += len(b)
        return total
    return 0


MENTION_RE = re.compile(r"([A-Za-z0-9_-]+)\.md\b|\[\[([A-Za-z0-9_-]+)\]\]")


def profile_session(path, collect_mentions=False):
    p = SessionProfile(path)
    uuid_ts = {}
    pending = {}  # tool_use_id -> (tool_name, ts)
    tool_result_uuids = set()  # user messages that carry a tool_result
    seen_requests = {}  # requestId -> (out, cache_read, cache_creation)

    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if collect_mentions:
                for a, b in MENTION_RE.findall(line):
                    p.mentions.add(a or b)
            try:
                d = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                continue

            t = d.get("type")
            ts = parse_ts(d.get("timestamp"))
            uuid = d.get("uuid")
            if uuid and ts:
                uuid_ts[uuid] = ts
            if ts:
                if p.started is None or ts < p.started:
                    p.started = ts
                if p.ended is None or ts > p.ended:
                    p.ended = ts
            if p.cwd is None and d.get("cwd"):
                p.cwd = d["cwd"]

            sidechain = bool(d.get("isSidechain"))

            if t == "assistant":
                msg = d.get("message") or {}
                out, cr, cc = usage_out(msg.get("usage"))
                # One API request is written as several assistant lines (one per
                # content block), each repeating the same usage. Count it once.
                rid = d.get("requestId") or d.get("uuid")
                prev = seen_requests.get(rid)
                if prev is None:
                    seen_requests[rid] = (out, cr, cc)
                    if sidechain:
                        p.sidechain_out += out
                    else:
                        p.out_tokens += out
                        p.cache_read += cr
                        p.cache_creation += cc
                        p.turns += 1
                    if d.get("effort"):
                        p.effort[d["effort"]] += 1

                # Generation latency, measured only for turns that follow a
                # tool_result — a turn following a typed prompt would fold the
                # user's own idle time into the number.
                parent_uuid = d.get("parentUuid")
                if prev is None and parent_uuid in tool_result_uuids and ts:
                    parent = uuid_ts.get(parent_uuid)
                    if parent:
                        delta = (ts - parent).total_seconds()
                        if 0 <= delta < 900:
                            p.gen_seconds += delta
                            p.gen_measured += 1

                for block in msg.get("content") or []:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_use":
                        name = block.get("name") or "?"
                        p.tool_calls[name] += 1
                        if block.get("id") and ts:
                            pending[block["id"]] = (name, ts)
                        if name == "Read":
                            fp = (block.get("input") or {}).get("file_path")
                            if fp:
                                p.reads[fp] += 1

            elif t == "user":
                msg = d.get("message") or {}
                for block in msg.get("content") or []:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "tool_result":
                        continue
                    if uuid:
                        tool_result_uuids.add(uuid)
                    tid = block.get("tool_use_id")
                    name, use_ts = pending.pop(tid, ("?", None))
                    p.stream_chars[name] += content_chars(block.get("content"))
                    if use_ts and ts:
                        delta = (ts - use_ts).total_seconds()
                        if 0 <= delta < 3600:
                            p.wait_seconds += delta

            elif t == "attachment":
                att = d.get("attachment") or {}
                if att.get("type") == "hook_success":
                    hook = att.get("hookName") or "hook"
                    p.hook_chars[hook] = max(
                        p.hook_chars[hook], len(att.get("content") or "")
                    )

    return p


# --------------------------------------------------------------- dense on disk


def dense_files(cwd, session_dir):
    """Files paid for on every session: CLAUDE.md chain + project MEMORY.md."""
    files = []
    global_md = HOME / ".claude" / "CLAUDE.md"
    if global_md.exists():
        files.append(global_md)

    if cwd:
        cur = Path(cwd).resolve()
        chain = []
        while True:
            candidate = cur / "CLAUDE.md"
            if candidate.exists():
                chain.append(candidate)
            if cur == HOME or cur == cur.parent:
                break
            cur = cur.parent
        files.extend(reversed(chain))

    memory_md = session_dir / "memory" / "MEMORY.md"
    if memory_md.exists():
        files.append(memory_md)

    seen, out = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def unused_memory_files(session_dir, mentioned):
    """Memory files whose name never appeared anywhere in the window's
    transcripts — not read, not recalled, not linked. The 'expert that routing
    never reaches' analogue."""
    mem_dir = session_dir / "memory"
    if not mem_dir.is_dir():
        return 0, 0
    files = [f for f in mem_dir.glob("*.md") if f.name != "MEMORY.md"]
    unused = [f for f in files if f.stem not in mentioned]
    return len(unused), len(files)


# ------------------------------------------------------------------- reporting


def bucket(name):
    if name.startswith(MCP_PREFIX):
        return "MCP"
    return name


def build_report(project, session_dir, profiles, days):
    dense = []
    cwd = next((p.cwd for p in profiles if p.cwd), None)
    for f in dense_files(cwd, session_dir):
        try:
            size = f.stat().st_size
        except OSError:
            continue
        try:
            label = str(f.relative_to(HOME))
            label = "~/" + label
        except ValueError:
            label = str(f)
        dense.append({"file": label, "tokens": approx_tokens(size)})

    hooks = Counter()
    for p in profiles:
        for h, c in p.hook_chars.items():
            hooks[h] = max(hooks[h], c)
    for h, c in sorted(hooks.items(), key=lambda kv: -kv[1]):
        dense.append({"file": f"hook: {h}", "tokens": approx_tokens(c)})

    dense_total = sum(d["tokens"] for d in dense)
    n = len(profiles)

    stream = Counter()
    calls = Counter()
    for p in profiles:
        for name, chars in p.stream_chars.items():
            stream[bucket(name)] += approx_tokens(chars)
        for name, c in p.tool_calls.items():
            calls[bucket(name)] += c

    stream_total = sum(stream.values())
    work_total = sum(p.out_tokens for p in profiles)
    sidechain_total = sum(p.sidechain_out for p in profiles)
    dense_paid = dense_total * n
    budget_total = dense_paid + stream_total + work_total

    wait = sum(p.wait_seconds for p in profiles)
    gen = sum(p.gen_seconds for p in profiles)

    # re-reads within a session
    reread_sessions = 0
    reread_files = Counter()
    hot = Counter()
    for p in profiles:
        had = False
        for fp, c in p.reads.items():
            hot[fp] += c
            if c > 1:
                reread_files[fp] += c - 1
                had = True
        if had:
            reread_sessions += 1

    mentioned = set()
    for p in profiles:
        mentioned |= p.mentions
    unused_mem, total_mem = unused_memory_files(session_dir, mentioned)

    effort = Counter()
    for p in profiles:
        effort.update(p.effort)

    starts = [p.started for p in profiles if p.started]
    return {
        "project": project,
        "sessions": n,
        "days": days,
        "range": [
            min(starts).strftime("%Y-%m-%d") if starts else None,
            max(starts).strftime("%Y-%m-%d") if starts else None,
        ],
        "budget": {
            "dense_per_session": dense_total,
            "dense_paid": dense_paid,
            "stream": stream_total,
            "work": work_total,
            "sidechain_work": sidechain_total,
            "total": budget_total,
            "load_to_work": (dense_paid + stream_total) / work_total
            if work_total
            else None,
        },
        "replay": {
            "cache_read": sum(p.cache_read for p in profiles),
            "cache_creation": sum(p.cache_creation for p in profiles),
            "requests": sum(p.turns for p in profiles),
        },
        "dense": sorted(dense, key=lambda d: -d["tokens"]),
        "stream": [
            {"tool": t, "calls": calls.get(t, 0), "tokens": tok}
            for t, tok in stream.most_common()
        ],
        "time": {
            "wait_s": wait,
            "gen_s": gen,
            "gen_measured_turns": sum(p.gen_measured for p in profiles),
            "total_turns": sum(p.turns for p in profiles),
        },
        "reread": {
            "sessions_affected": reread_sessions,
            "wasted_reads": sum(reread_files.values()),
            "top": reread_files.most_common(5),
        },
        "hot": hot.most_common(8),
        "memory": {"unused": unused_mem, "total": total_mem},
        "effort": dict(effort),
    }


BOLD = "\033[1m"
GRAY = "\033[0;90m"
YEL = "\033[1;33m"
NC = "\033[0m"


def print_report(r):
    no_color = not sys.stdout.isatty() or os.environ.get("NO_COLOR")
    b, g, y, n = ("", "", "", "") if no_color else (BOLD, GRAY, YEL, NC)

    lo, hi = r["range"]
    print(
        f"\n{b}{r['project']}{n} · {r['sessions']} session · {lo} → {hi} "
        f"{g}(son {r['days']} gun){n}\n"
    )

    bud = r["budget"]
    total = bud["total"] or 1
    print(f"{b}CONTEXT BUTCESI{n}                      ~tok      %")
    for label, val, note in (
        ("DENSE  (her session, kosulsuz)", bud["dense_paid"], f"{r['sessions']}x odendi"),
        ("STREAM (araclarla cekilen)", bud["stream"], ""),
        ("WORK   (uretilen)", bud["work"], ""),
    ):
        print(
            f"  {label:<32} {fmt_tok(val):>6} {pct(val, total):5.0f}%"
            + (f"   {g}<- {note}{n}" if note else "")
        )
    if bud["sidechain_work"]:
        print(
            f"  {'subagent WORK (ayri)':<32} {fmt_tok(bud['sidechain_work']):>6}"
            f"       {g}sidechain{n}"
        )
    if bud["load_to_work"]:
        ratio = bud["load_to_work"]
        flag = f"   {y}! 3:1 uzeri{n}" if ratio > 3 else ""
        print(f"  {'load:work orani':<32} {ratio:>6.2f} : 1{flag}")

    rp = r["replay"]
    if rp["requests"]:
        per_req = rp["cache_read"] // rp["requests"]
        print(
            f"\n{b}BAGLAM TEKRARI{n} {g}(her istekte yeniden gonderilen){n}\n"
            f"  cache read toplam    {fmt_tok(rp['cache_read']):>8}"
            f"   {rp['requests']} istek, istek basi ~{fmt_tok(per_req)}\n"
            f"  cache write toplam   {fmt_tok(rp['cache_creation']):>8}"
            f"   {g}yeni yazilan bolum{n}"
        )

    print(f"\n{b}DENSE KIRILIMI{n}                       ~tok      %")
    dense_per = r["budget"]["dense_per_session"] or 1
    for d in r["dense"]:
        share = pct(d["tokens"], dense_per)
        flag = f"   {y}! dense'in %{share:.0f}'i{n}" if share >= 30 else ""
        print(f"  {d['file']:<34} {fmt_tok(d['tokens']):>6} {share:5.0f}%{flag}")

    print(f"\n{b}STREAM KIRILIMI{n}                   cagri   ~tok    ort")
    for s in r["stream"]:
        avg = s["tokens"] // s["calls"] if s["calls"] else 0
        print(f"  {s['tool']:<30} {s['calls']:>6} {fmt_tok(s['tokens']):>6} {avg:>6}")

    t = r["time"]
    tt = (t["wait_s"] + t["gen_s"]) or 1
    print(f"\n{b}ZAMAN{n}                                sure      %")
    print(f"  {'WAIT (arac round-trip)':<34} {fmt_dur(t['wait_s']):>8} {pct(t['wait_s'], tt):5.0f}%")
    print(f"  {'GEN  (model uretimi)':<34} {fmt_dur(t['gen_s']):>8} {pct(t['gen_s'], tt):5.0f}%")
    print(
        f"  {g}arac sonrasi {t['gen_measured_turns']}/{t['total_turns']} tur olculdu; "
        f"kullanici yazma suresi haric{n}"
    )

    rr = r["reread"]
    print(f"\n{b}TEKRAR OKUMA{n} {g}(cache miss analogu){n}")
    if rr["wasted_reads"]:
        for fp, c in rr["top"]:
            short = fp.replace(str(HOME), "~")
            print(f"  {short:<52} +{c}")
        print(
            f"  {g}{rr['wasted_reads']} gereksiz Read, "
            f"{rr['sessions_affected']}/{r['sessions']} session'da{n}"
        )
    else:
        print(f"  {g}yok{n}")

    print(f"\n{b}SICAK SET{n} {g}(hot.json adayi){n}")
    for fp, c in r["hot"]:
        print(f"  {fp.replace(str(HOME), '~'):<52} {c}x")
    mem = r["memory"]
    if mem["total"]:
        print(
            f"  {y}hic anilmayan memory dosyasi: {mem['unused']}/{mem['total']}{n}"
        )
    if r["effort"]:
        parts = " ".join(f"{k}:{v}" for k, v in sorted(r["effort"].items()))
        print(f"\n{b}EFFORT{n}  {parts}")
    print()


# ------------------------------------------------------------------------ main


def find_project_dir(project):
    if not SESSIONS_DIR.is_dir():
        sys.exit(f"No sessions dir at {SESSIONS_DIR}")
    dirs = [d for d in SESSIONS_DIR.iterdir() if d.is_dir()]
    exact = [d for d in dirs if project_of_dir(d).lower() == project.lower()]
    if exact:
        return max(exact, key=lambda d: len(d.name))
    partial = [d for d in dirs if project.lower() in d.name.lower()]
    if partial:
        return max(partial, key=lambda d: len(d.name))
    names = sorted(
        {
            d.name.lstrip("-").replace("-", "/")
            for d in dirs
            if any(d.glob("*.jsonl"))
        }
    )
    listing = "\n  ".join(names)
    sys.exit(f"No sessions for '{project}'. Known:\n  {listing}")


def main():
    ap = argparse.ArgumentParser(prog="hq history profile")
    ap.add_argument("project", nargs="?", help="project name (default: cwd)")
    ap.add_argument("--days", type=int, default=30, help="lookback window (0 = all)")
    ap.add_argument("--limit", type=int, default=0, help="max sessions (newest first)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    project = args.project or Path.cwd().name
    session_dir = find_project_dir(project)
    project = project_of_dir(session_dir)

    files = sorted(
        session_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True
    )
    if args.days > 0:
        cutoff = time.time() - args.days * 86400
        files = [f for f in files if f.stat().st_mtime >= cutoff]
    if args.limit:
        files = files[: args.limit]
    if not files:
        sys.exit(f"No sessions for '{project}' in the last {args.days} days.")

    profiles = [profile_session(f, collect_mentions=True) for f in files]
    report = build_report(project, session_dir, profiles, args.days)

    if args.json:
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        print()
    else:
        print_report(report)


if __name__ == "__main__":
    main()

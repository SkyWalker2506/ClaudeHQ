#!/usr/bin/env python3
"""Which instructions earn their tokens?

Boris Cherny's advice, as relayed second-hand: delete CLAUDE.md, the skills and the hooks, run
the model bare, and add instruction back only where you see it repeatedly stuck. That is a
testable claim rather than a philosophy, and a full A/B is expensive. This is the cheap half
that needs no A/B at all: for rules that can be checked mechanically against the transcript
record, classify each one by what actually happened.

    enforced   a gate or test makes violation fail -- not an instruction at all
    followed   stated, and no violation found
    ignored    stated, and violated
    inert      stated, and nothing in the record ever touched it

The distinction the advice blurs is the one that matters here. An instruction asks the model to
remember. A gate makes the wrong output fail. Everything that caught a real defect in this
ecosystem was in the second category, and the sharpest evidence is the hard ban on the
general-purpose agent: written in capitals, declared exceptionless, and violated in the
majority of calls.

Only mechanically checkable rules appear below. A rule whose observance needs judgement is
left out rather than guessed at, and the count of those is reported so the coverage of this
audit is visible instead of implied.

    python3 audit_rules.py
"""

from __future__ import annotations

import collections
import glob
import json
import os
import re
import sys

ROOT = os.path.expanduser("~/.claude/projects")

#: Instruction-layer files loaded into a session, and their sizes.
INSTRUCTION_FILES = [
    "~/.claude/CLAUDE.md",
    "~/Projects/CLAUDE.md",
    "~/Projects/ClaudeHQ/CLAUDE.md",
    "~/Projects/claude-config/CLAUDE.md",
    "~/Projects/claude-config/global/CLAUDE.md",
    "~/Projects/claude-config/global/charter.md",
    "~/Projects/claude-config/global/harness.md",
    "~/.claude/projects/-Users-musabkara-Projects-ClaudeHQ/memory/MEMORY.md",
]

#: Rules that can be decided from the record. Each returns (applicable, violations).
#: A rule that cannot be decided this way belongs in UNCHECKABLE, not here.
UNCHECKABLE = [
    "no history rewrite (amend / reset --hard / rebase / force-push) — the regex cannot tell "
    "a git command from the same words appearing INSIDE a command. Measured: 20 matches, of "
    "which one is a grep searching for that very text and most of the rest sit inside "
    "multi-line scripts. Reporting 0.6 percent would have been reporting my own prohibition "
    "text back to myself.",
    "dispatch size table (trivial / small / large) — needs judgement per task",
    "'proactive, not indecisive' — not observable",
    "'read only the relevant section, not the whole file' — partial reads not distinguishable",
    "secret values never printed — absence is not observable from transcripts alone",
    "push only when told — the instruction to push is in prose, not a tool call",
]


def reply_openings():
    """First assistant text of each reply -- the only place an opening tag could be."""
    patterns = [os.path.join(ROOT, "*", "*.jsonl"),
                os.path.join(ROOT, "*", "*", "subagents", "*.jsonl"),
                os.path.join(ROOT, "*", "*", "*.jsonl")]
    for path in sorted({p for pattern in patterns for p in glob.glob(pattern)}):
        try:
            handle = open(path, encoding="utf-8", errors="ignore")
        except OSError:
            continue
        previous_role = None
        with handle:
            for line in handle:
                try:
                    record = json.loads(line)
                except Exception:
                    continue
                message = record.get("message") or {}
                role = message.get("role")
                if role == "assistant" and previous_role == "user":
                    content = message.get("content")
                    text = None
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        text = next((b.get("text") for b in content
                                     if isinstance(b, dict) and b.get("type") == "text"
                                     and (b.get("text") or "").strip()), None)
                    if text and text.strip():
                        yield text.strip()
                if role in ("user", "assistant"):
                    previous_role = role


def walk_records():
    patterns = [os.path.join(ROOT, "*", "*.jsonl"),
                os.path.join(ROOT, "*", "*", "subagents", "*.jsonl"),
                os.path.join(ROOT, "*", "*", "*.jsonl")]
    for path in sorted({p for pattern in patterns for p in glob.glob(pattern)}):
        try:
            handle = open(path, encoding="utf-8", errors="ignore")
        except OSError:
            continue
        with handle:
            for line in handle:
                try:
                    yield json.loads(line)
                except Exception:
                    continue


def collect():
    """One pass over the record, gathering only what the rules below need."""
    facts = {
        "subagent_types": collections.Counter(),
        "bash_commands": [],
        "assistant_first_lines": [opening[:80] for opening in reply_openings()],
    }
    for record in walk_records():
        message = record.get("message") or {}
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            name, payload = block.get("name"), block.get("input") or {}
            if name in ("Agent", "Task"):
                facts["subagent_types"][payload.get("subagent_type") or "(unset)"] += 1
            elif name == "Bash":
                facts["bash_commands"].append(payload.get("command") or "")
    return facts


def rule_general_purpose_ban(facts):
    """harness.md: the general-purpose agent is banned, no exceptions."""
    types = facts["subagent_types"]
    applicable = sum(types.values())
    return applicable, types.get("general-purpose", 0)


def rule_jarvis_tag(facts):
    """CLAUDE.md: every reply opens with a (Jarvis) tag."""
    lines = [l for l in facts["assistant_first_lines"] if l]
    return len(lines), sum(1 for l in lines if not l.startswith("(Jarvis"))


RULES = [
    ("general-purpose agent banned", rule_general_purpose_ban,
     "harness.md, capitals, 'no exceptions'"),
    ("reply opens with (Jarvis)", rule_jarvis_tag,
     "CLAUDE.md, stated in three separate files"),
]


def main():
    print("INSTRUCTION LAYER — her oturumda yuklenen")
    total = 0
    for relative in INSTRUCTION_FILES:
        path = os.path.expanduser(relative)
        if not os.path.isfile(path):
            print(f"  {'yok':>8}  {relative}")
            continue
        size = os.path.getsize(path)
        total += size
        print(f"  {size:8,d} B  {relative.replace(os.path.expanduser('~'), '~')}")
    print(f"  {total:8,d} B  TOPLAM  (~{total // 4:,} token, tahmini)")

    print("\nMEKANIK OLARAK DENETLENEBILEN KURALLAR")
    facts = collect()
    for label, check, source in RULES:
        applicable, violations = check(facts)
        if applicable == 0:
            verdict, detail = "INERT", "kayitta hic uygulanabilir vaka yok"
        elif violations == 0:
            verdict, detail = "FOLLOWED", f"{applicable} vaka, 0 ihlal"
        else:
            rate = 100.0 * violations / applicable
            verdict, detail = "IGNORED", f"{violations}/{applicable} ihlal (%{rate:.1f})"
        print(f"  {verdict:9} {label:32} {detail}")
        print(f"            kaynak: {source}")

    print(f"\nsubagent_type dagilimi: {dict(facts['subagent_types'].most_common(6))}")

    print(f"\nDENETLENEMEYEN ({len(UNCHECKABLE)}) — bu denetimin kapsam disi kalan kismi")
    for item in UNCHECKABLE:
        print(f"  - {item}")
    print("\nBu liste, denetimin neyi SOYLEMEDIGINI gorunur kilmak icin var. Kapsamini")
    print("bildirmeyen bir olcum, kapsadigini iddia eder.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

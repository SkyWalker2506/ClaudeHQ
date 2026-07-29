#!/usr/bin/env python3
"""Baseline: what the hand-carried constraints in agent briefs cost today.

This is deliberately the first thing measured rather than the first thing designed. The
knowledge-layer proposal adds a contract to every dispatch, and the case for it collapses if
the contract costs more than the copy-paste it replaces. That comparison needs a number that
exists before the contract does.

It counts only the CONSTRAINT portion of a brief -- the prohibitions, the file boundaries, the
stop conditions -- because that is the part a contract would replace. The task description
itself is not in scope; nobody proposes to generate that.

Tokenisation is approximate and says so. No tiktoken here, so this uses a character ratio and
reports it as an estimate. When contracts exist they must be measured with the SAME function,
which is why the ratio lives in one constant rather than being applied ad hoc.

    python3 measure_manual_constraints.py [--transcripts DIR]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import statistics
import sys

#: Rough characters-per-token. An estimate, and labelled as one everywhere it surfaces.
#: Turkish and heavy punctuation both push the real number lower than English prose.
CHARS_PER_TOKEN = 4.0

#: Lines that carry a constraint rather than a task. Matched case-insensitively against the
#: brief's own lines, so a brief that never states a constraint scores zero rather than
#: being credited for its prose.
CONSTRAINT_PATTERNS = [
    r"Million_Dollars_Project",
    r"\bgit\b.*\b(commit|push|amend|reset|rebase|stash|checkout)\b",
    r"kesin yasak|yasak(lar)?\b|forbidden|do not touch|dokunma",
    r"durma [sş]art[ıi]|bitirme [sş]art[ıi]|stop condition|stopping",
    r"sadece oku|salt.?okunur|read.?only|yalniz(ca)? oku",
    r"dosya s[ıi]n[ıi]r|file boundar|kendi (cikti )?dosyan",
    r"es zamanl[ıi]|ayni anda|concurrent|paralel calis",
    r"uydurma|do not invent|tahmin etme",
]
COMPILED = [re.compile(p, re.I) for p in CONSTRAINT_PATTERNS]


def constraint_chars(prompt: str) -> int:
    """Characters on lines that state a constraint. Line-level, so a single mention does not
    claim the whole paragraph, and a paragraph of constraints is not reduced to one line."""
    total = 0
    for line in prompt.splitlines():
        if any(pattern.search(line) for pattern in COMPILED):
            total += len(line) + 1
    return total


def collect(root: str):
    """Yields (transcript_path, dispatch_prompt) for every Agent/Task dispatch found."""
    for path in sorted(glob.glob(os.path.join(root, "*", "*.jsonl"))):
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
                message = record.get("message") or {}
                content = message.get("content")
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    if block.get("name") not in ("Agent", "Task"):
                        continue
                    prompt = (block.get("input") or {}).get("prompt")
                    if isinstance(prompt, str) and prompt:
                        yield path, prompt


def quantiles(values):
    if not values:
        return {"n": 0}
    ordered = sorted(values)
    return {
        "n": len(ordered),
        "p50": statistics.median(ordered),
        "p95": ordered[min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1))))],
        "max": ordered[-1],
        "total": sum(ordered),
    }


def report(label, values, unit="token"):
    q = quantiles(values)
    if not q["n"]:
        print(f"{label}: veri yok")
        return q
    print(f"{label}")
    print(f"  n={q['n']}  p50={q['p50']:,.0f}  p95={q['p95']:,.0f}  "
          f"max={q['max']:,.0f}  toplam={q['total']:,.0f} {unit}")
    return q


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transcripts",
                        default=os.path.expanduser("~/.claude/projects"))
    args = parser.parse_args()

    per_dispatch = []
    per_run = {}
    brief_totals = []

    for path, prompt in collect(args.transcripts):
        constraint = constraint_chars(prompt) / CHARS_PER_TOKEN
        per_dispatch.append(constraint)
        brief_totals.append(len(prompt) / CHARS_PER_TOKEN)
        per_run[path] = per_run.get(path, 0.0) + constraint

    if not per_dispatch:
        print("Hicbir dispatch bulunamadi.", file=sys.stderr)
        return 1

    print(f"kaynak: {args.transcripts}")
    print(f"tokenizer: YOK — {CHARS_PER_TOKEN} karakter/token TAHMINI. Contract olcumu ayni")
    print(f"           fonksiyonla yapilmali, yoksa karsilastirma anlamsiz.\n")

    report("brief TOPLAMI (dispatch basina)", brief_totals)
    print()
    dispatch = report("KISIT maliyeti (dispatch basina)", per_dispatch)
    print()
    run = report("KISIT maliyeti (ana kosu basina)", list(per_run.values()))

    print(f"\nkisitlarin brief icindeki payi: "
          f"%{100 * sum(per_dispatch) / sum(brief_totals):.1f}")
    print("\nGECIS SARTI — contract bunlari ASMAMALI:")
    print(f"  contract_token_cost_per_dispatch    p50 <= {dispatch['p50']:,.0f}   "
          f"p95 <= {dispatch['p95']:,.0f}")
    print(f"  contract_token_cost_per_parent_run  p50 <= {run['p50']:,.0f}   "
          f"p95 <= {run['p95']:,.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

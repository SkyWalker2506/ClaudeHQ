#!/usr/bin/env bash
# hq-graph-docs.sh — Enrich graph-cache with Markdown/PDF concept nodes.
# Usage: hq graph docs <project>
set -euo pipefail

HQ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_ROOT="${HQ_PROJECTS_ROOT:-$HOME/Projects}"
PROJECTS_FILE="$HQ_DIR/projects.json"

RED=$'\033[0;31m'; GREEN=$'\033[0;32m'; YELLOW=$'\033[1;33m'; BLUE=$'\033[0;34m'; GRAY=$'\033[0;90m'; NC=$'\033[0m'

resolve_project_path() {
  local name="$1"
  if [[ -d "$name" && -f "$name/CLAUDE.md" ]]; then echo "$name"; return 0; fi
  if [[ -f "$PROJECTS_FILE" ]]; then
    local p
    p="$(python3 -c "
import json,os
try:
    d=json.load(open('$PROJECTS_FILE'))
    proj=d.get('projects',{}).get('$name')
    if proj: print(os.path.expanduser(proj.get('path','')))
except Exception: pass
" 2>/dev/null || true)"
    if [[ -n "$p" && -d "$p" ]]; then echo "$p"; return 0; fi
  fi
  [[ -d "$PROJECTS_ROOT/$name" ]] && { echo "$PROJECTS_ROOT/$name"; return 0; }
  return 1
}

name="${1:-}"
[[ -z "$name" ]] && { echo "${RED}error:${NC} project name required"; exit 1; }
root="$(resolve_project_path "$name")" || { echo "${RED}error:${NC} project '$name' not found"; exit 1; }
cache="$root/.claude/graph-cache.json"

[[ -f "$cache" ]] || { echo "${RED}error:${NC} run 'hq graph build $name' first"; exit 1; }

echo "${BLUE}Enriching docs for:${NC} $root"

have_pdftotext=0
command -v pdftotext >/dev/null 2>&1 && have_pdftotext=1
if [[ $have_pdftotext -eq 0 ]]; then
  echo "${YELLOW}warn:${NC} pdftotext not found — PDFs will be skipped (brew install poppler to enable)"
fi

# Pick Haiku via claude --print if available
claude_bin=""
for c in "$HOME/.local/bin/claude" "/usr/local/bin/claude" "/opt/homebrew/bin/claude"; do
  [[ -x "$c" ]] && { claude_bin="$c"; break; }
done

extract_doc() {
  local f="$1"
  local ext="${f##*.}"
  ext="$(echo "$ext" | tr '[:upper:]' '[:lower:]')"
  case "$ext" in
    md|mdx|rst|txt)
      head -c 10000 "$f" 2>/dev/null || true
      ;;
    pdf)
      [[ $have_pdftotext -eq 1 ]] && pdftotext -layout "$f" - 2>/dev/null | head -c 10000 || true
      ;;
  esac
}

# Build doc list
DOCS_LIST="$(cd "$root" && find . -type f \( -iname "*.md" -o -iname "*.mdx" -o -iname "*.rst" -o -iname "README*" -o -iname "*.pdf" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/.venv/*" -not -path "*/venv/*" \
  -not -path "*/.claude/*" -not -path "*/dist/*" -not -path "*/build/*" \
  2>/dev/null | sed 's|^\./||' | head -200)"
DOC_COUNT=$(printf "%s\n" "$DOCS_LIST" | grep -c . || true)

echo "${GRAY}Found ${DOC_COUNT} candidate docs${NC}"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

# Per-doc summary: if claude CLI available, use Haiku to extract concepts.
# Otherwise, use naive heuristic: top-level markdown headings + path mentions.

summarize_naive() {
  local f="$1" full="$2"
  python3 - "$f" "$full" <<'PY'
import sys, re, os, json
rel, full = sys.argv[1], sys.argv[2]
try:
    txt = open(full, "rb").read().decode("utf-8", errors="replace")
except Exception:
    txt = ""
# Concepts = H1/H2/H3 headings (md) up to 8
headings = re.findall(r"^\s{0,3}#{1,3}\s+(.+?)\s*$", txt, flags=re.M)[:8]
# Referenced file paths (heuristic: tokens with '/' and an extension, or **path**)
refs = set()
for m in re.finditer(r"[`']?([A-Za-z0-9_./-]+\.(?:py|js|ts|tsx|jsx|go|rs|md|sh|json|yaml|yml|html))[`']?", txt):
    p = m.group(1)
    if "/" in p or p in headings:
        refs.add(p)
result = {
    "id": f"doc::{rel}",
    "name": os.path.basename(rel),
    "path": rel,
    "type": "doc",
    "concepts": [h.strip() for h in headings if h.strip()],
    "refs": sorted(list(refs))[:25],
}
json.dump(result, sys.stdout)
PY
}

summarize_claude() {
  local f="$1" full="$2"
  local content
  content="$(extract_doc "$full")"
  [[ -z "$content" ]] && return 1
  local prompt
  prompt="$(cat <<EOF
Summarize this document. Reply ONLY with strict JSON (no fences) shape:
{"id":"doc::$f","name":"$(basename "$f")","path":"$f","type":"doc","concepts":["...up to 5..."],"refs":["file/path.ext","..."]}

Document:
$content
EOF
)"
  # Use haiku via env var override if set; otherwise default.
  local model_arg=""
  [[ -n "${HQ_GRAPH_DOCS_MODEL:-}" ]] && model_arg="--model $HQ_GRAPH_DOCS_MODEL"
  echo "$prompt" | timeout 60 "$claude_bin" --print $model_arg 2>/dev/null | \
    python3 -c "import sys,json,re; t=sys.stdin.read(); m=re.search(r'\{.*\}', t, re.S); print(m.group(0)) if m else sys.exit(1)"
}

: > "$tmpdir/docs.jsonl"
processed=0
failed=0

# Worker function
process_one() {
  local rel="$1"
  local full="$root/$rel"
  [[ -f "$full" ]] || return 0
  local out=""
  if [[ -n "$claude_bin" && "${HQ_GRAPH_DOCS_USE_CLAUDE:-0}" == "1" ]]; then
    out="$(summarize_claude "$rel" "$full" 2>/dev/null || true)"
  fi
  if [[ -z "$out" ]]; then
    out="$(summarize_naive "$rel" "$full" 2>/dev/null || true)"
  fi
  [[ -n "$out" ]] && echo "$out" >> "$tmpdir/docs.jsonl"
}

export -f process_one extract_doc summarize_naive summarize_claude
export root claude_bin tmpdir have_pdftotext
export HQ_GRAPH_DOCS_USE_CLAUDE="${HQ_GRAPH_DOCS_USE_CLAUDE:-0}"

if [[ $DOC_COUNT -gt 0 ]]; then
  while IFS= read -r rel; do
    [[ -z "$rel" ]] && continue
    process_one "$rel" && processed=$((processed+1)) || failed=$((failed+1))
  done <<< "$DOCS_LIST"
fi

echo "${GRAY}Processed $processed docs${NC}"

# Merge into cache
python3 - "$cache" "$tmpdir/docs.jsonl" <<'PY'
import json, sys, os
cache_path, docs_path = sys.argv[1], sys.argv[2]
with open(cache_path) as f:
    g = json.load(f)

nodes = g.setdefault("nodes", [])
edges = g.setdefault("edges", [])

# Index existing node ids and also by path
by_id = {n.get("id"): n for n in nodes}
by_path = {n.get("path"): n for n in nodes if n.get("path")}

doc_entries = []
try:
    with open(docs_path) as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                doc_entries.append(json.loads(line))
            except Exception:
                pass
except FileNotFoundError:
    pass

added = 0
ref_edges = 0
for d in doc_entries:
    doc_id = d["id"]
    if doc_id not in by_id:
        node = {
            "id": doc_id,
            "name": d.get("name"),
            "path": d.get("path"),
            "type": "doc",
            "degree": 0,
            "concepts": d.get("concepts", []),
        }
        nodes.append(node)
        by_id[doc_id] = node
        added += 1
    else:
        by_id[doc_id]["concepts"] = d.get("concepts", [])
        by_id[doc_id]["type"] = "doc"

    # code<->doc refs
    for ref in d.get("refs", []):
        target = by_path.get(ref)
        if target:
            edges.append({"source": doc_id, "target": target["id"], "kind": "refs"})
            by_id[doc_id]["degree"] = by_id[doc_id].get("degree", 0) + 1
            target["degree"] = target.get("degree", 0) + 1
            ref_edges += 1

g["nodes"] = nodes
g["edges"] = edges
g["docs_enriched_at"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"
with open(cache_path, "w") as f:
    json.dump(g, f, indent=2)

print(f"✓ merged: +{added} doc nodes, +{ref_edges} ref edges")
PY

echo "${GREEN}✓ docs layer complete${NC}"

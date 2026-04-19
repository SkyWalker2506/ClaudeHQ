#!/usr/bin/env bash
# hq-graph.sh — ClaudeHQ knowledge-graph subcommands (Graphify-inspired)
#
# Subcommands:
#   install <project>     Register SessionStart + post-commit hooks in project
#   uninstall <project>   Remove hooks
#   status                Table of graph-cache freshness across all projects
#   build <project>       Build / refresh .claude/graph-cache.json
#   docs <project>        Layer in Markdown / PDF concept nodes (loaded via hq-graph-docs.sh)
#   transcribe <file>     Whisper transcript (loaded via hq-graph-transcribe.sh)
#   view <project>        Open interactive HTML visualization (loaded via hq-graph-view.sh)
set -euo pipefail

HQ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTS_ROOT="${HQ_PROJECTS_ROOT:-$HOME/Projects}"
PROJECTS_FILE="$HQ_DIR/projects.json"
CONFIG_ROOT="$HOME/Projects/claude-config"
HOOKS_SRC="$CONFIG_ROOT/hooks"

RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
BLUE=$'\033[0;34m'
GRAY=$'\033[0;90m'
BOLD=$'\033[1m'
NC=$'\033[0m'

usage() {
  cat <<EOF
${BOLD}hq graph${NC} — knowledge-graph utilities

${BOLD}Usage:${NC}
  hq graph install <project>     Add SessionStart + post-commit hooks
  hq graph uninstall <project>   Remove hooks
  hq graph status                Show graph-cache freshness across projects
  hq graph build <project>       Build/refresh .claude/graph-cache.json
  hq graph docs <project>        Add Markdown/PDF concept layer
  hq graph transcribe <file>     Transcribe audio/video to text
  hq graph view <project>        Open interactive HTML visualization
EOF
}

resolve_project_path() {
  local name="$1"
  # Allow absolute paths directly
  if [[ -d "$name" && -f "$name/CLAUDE.md" ]]; then
    echo "$name"; return 0
  fi
  # Lookup in projects.json
  if [[ -f "$PROJECTS_FILE" ]] && command -v python3 &>/dev/null; then
    local p
    p="$(python3 -c "
import json,sys,os
try:
    d=json.load(open('$PROJECTS_FILE'))
    proj=d.get('projects',{}).get('$name')
    if proj:
        print(os.path.expanduser(proj.get('path','')))
except Exception:
    pass
" 2>/dev/null || true)"
    if [[ -n "$p" && -d "$p" ]]; then echo "$p"; return 0; fi
  fi
  # Fallback to ~/Projects/<name>
  if [[ -d "$PROJECTS_ROOT/$name" ]]; then
    echo "$PROJECTS_ROOT/$name"; return 0
  fi
  return 1
}

list_projects_json() {
  # Prints "name<TAB>path" for every project in projects.json (expanded).
  [[ -f "$PROJECTS_FILE" ]] || return 0
  python3 -c "
import json,os
d=json.load(open('$PROJECTS_FILE'))
for name,proj in d.get('projects',{}).items():
    p=os.path.expanduser(proj.get('path',''))
    if p:
        print(f'{name}\t{p}')
" 2>/dev/null || true
}

cmd_install() {
  local name="${1:-}"
  [[ -z "$name" ]] && { echo -e "${RED}error:${NC} project name required"; return 1; }
  local root
  root="$(resolve_project_path "$name")" || { echo -e "${RED}error:${NC} project '$name' not found"; return 1; }

  echo -e "${BLUE}Installing graph hooks in:${NC} $root"

  # 1. SessionStart hook via .claude/settings.local.json
  mkdir -p "$root/.claude"
  local settings="$root/.claude/settings.local.json"
  local hook_path="$HOME/.claude/hooks/session-start-graph.sh"

  python3 - "$settings" "$hook_path" <<'PY'
import json, os, sys
path, hook = sys.argv[1], sys.argv[2]
data = {}
if os.path.exists(path):
    try:
        data = json.load(open(path))
    except Exception:
        data = {}
hooks = data.setdefault("hooks", {})
ss = hooks.setdefault("SessionStart", [])
# Each entry is {"hooks":[{"type":"command","command":"..."}]}
already = False
for entry in ss:
    for h in (entry.get("hooks") or []):
        if h.get("command","").endswith("session-start-graph.sh"):
            already = True
if not already:
    ss.append({"hooks":[{"type":"command","command":f"bash {hook}"}]})
with open(path, "w") as f:
    json.dump(data, f, indent=2)
print("  ✓ SessionStart hook registered")
PY

  # 2. git post-commit hook (symlink for live updates)
  if [[ -d "$root/.git" ]]; then
    local git_hook="$root/.git/hooks/post-commit"
    local src_hook="$HOME/.claude/hooks/post-commit-graph-update.sh"
    mkdir -p "$root/.git/hooks"
    if [[ -L "$git_hook" || -f "$git_hook" ]]; then
      # Preserve existing hook content by chaining if not ours
      if [[ -L "$git_hook" ]] && [[ "$(readlink "$git_hook")" == "$src_hook" ]]; then
        echo "  ✓ post-commit hook already linked"
      elif grep -q "post-commit-graph-update.sh" "$git_hook" 2>/dev/null; then
        echo "  ✓ post-commit hook already chained"
      else
        # Append chain call
        {
          echo ""
          echo "# claude-graph chain"
          echo "bash \"$src_hook\" || true"
        } >> "$git_hook"
        chmod +x "$git_hook"
        echo "  ✓ post-commit hook chained to existing"
      fi
    else
      ln -sf "$src_hook" "$git_hook"
      chmod +x "$git_hook" 2>/dev/null || true
      echo "  ✓ post-commit hook linked"
    fi
  else
    echo -e "  ${GRAY}no .git — skipped post-commit hook${NC}"
  fi

  echo -e "${GREEN}✓ graph hooks installed${NC} for $name"
  echo -e "${GRAY}  Next: hq graph build $name${NC}"
}

cmd_uninstall() {
  local name="${1:-}"
  [[ -z "$name" ]] && { echo -e "${RED}error:${NC} project name required"; return 1; }
  local root
  root="$(resolve_project_path "$name")" || { echo -e "${RED}error:${NC} project '$name' not found"; return 1; }

  local settings="$root/.claude/settings.local.json"
  if [[ -f "$settings" ]]; then
    python3 - "$settings" <<'PY'
import json, sys
p = sys.argv[1]
try:
    d = json.load(open(p))
except Exception:
    sys.exit(0)
hooks = d.get("hooks", {})
ss = hooks.get("SessionStart", [])
new_ss = []
for entry in ss:
    filtered = [h for h in (entry.get("hooks") or []) if "session-start-graph.sh" not in h.get("command","")]
    if filtered:
        new_ss.append({"hooks": filtered})
if new_ss:
    hooks["SessionStart"] = new_ss
else:
    hooks.pop("SessionStart", None)
if not hooks:
    d.pop("hooks", None)
else:
    d["hooks"] = hooks
json.dump(d, open(p, "w"), indent=2)
print("  ✓ SessionStart hook removed")
PY
  fi

  local git_hook="$root/.git/hooks/post-commit"
  if [[ -L "$git_hook" ]]; then
    rm -f "$git_hook"
    echo "  ✓ post-commit symlink removed"
  elif [[ -f "$git_hook" ]] && grep -q "post-commit-graph-update.sh" "$git_hook" 2>/dev/null; then
    # Remove the chain block
    python3 - "$git_hook" <<'PY'
import sys, re
p = sys.argv[1]
txt = open(p).read()
txt = re.sub(r"\n# claude-graph chain\nbash .*post-commit-graph-update\.sh.*\n", "\n", txt)
open(p, "w").write(txt)
PY
    echo "  ✓ post-commit chain removed"
  fi

  echo -e "${GREEN}✓ graph hooks uninstalled${NC} from $name"
}

cmd_status() {
  printf "${BOLD}%-28s %-10s %-25s %-7s %-7s${NC}\n" "PROJECT" "CACHE" "BUILT" "NODES" "STALE"
  printf '━%.0s' {1..85}; echo ""

  while IFS=$'\t' read -r name path; do
    [[ -z "$name" ]] && continue
    local cache="$path/.claude/graph-cache.json"
    if [[ ! -f "$cache" ]]; then
      printf "%-28s ${GRAY}%-10s %-25s %-7s %-7s${NC}\n" "$name" "missing" "-" "-" "-"
      continue
    fi
    local built nodes stale
    read -r built nodes stale < <(python3 -c "
import json
try:
    d=json.load(open('$cache'))
    print(d.get('built_at','?'), len(d.get('nodes',[])), d.get('stale',False))
except Exception:
    print('?','0','?')
" 2>/dev/null)
    local status_c="$GREEN" status_s="fresh"
    if [[ "$stale" == "True" ]]; then status_c="$YELLOW"; status_s="STALE"; fi
    printf "%-28s ${status_c}%-10s${NC} %-25s %-7s %-7s\n" "$name" "$status_s" "${built:0:19}" "$nodes" "$stale"
  done < <(list_projects_json)

  echo ""
}

# ---- BUILD ----
# Two-mode build:
#   1. If CLAUDE_CLI is reachable + jcodemunch MCP configured, call it to run the indexing.
#   2. Else: basic fallback — walk file tree, produce file/folder topology graph.
cmd_build() {
  local name="${1:-}"
  [[ -z "$name" ]] && { echo -e "${RED}error:${NC} project name required"; return 1; }
  local root
  root="$(resolve_project_path "$name")" || { echo -e "${RED}error:${NC} project '$name' not found"; return 1; }

  mkdir -p "$root/.claude"
  local cache="$root/.claude/graph-cache.json"
  echo -e "${BLUE}Building graph-cache for:${NC} $root"

  local claude_bin=""
  for c in "$HOME/.local/bin/claude" "/usr/local/bin/claude" "/opt/homebrew/bin/claude"; do
    if [[ -x "$c" ]]; then claude_bin="$c"; break; fi
  done

  local mode="basic"
  if [[ -n "$claude_bin" ]] && [[ "${HQ_GRAPH_USE_CLAUDE:-0}" == "1" ]]; then
    mode="claude"
  fi

  case "$mode" in
    claude)
      echo -e "${GRAY}Mode: claude CLI + MCP (jcodemunch)${NC}"
      (
        cd "$root" || exit 1
        "$claude_bin" --print --output-format json <<EOF > "$cache.raw" 2>/dev/null || true
Use the jcodemunch MCP server to index this repository and build a knowledge graph.
1) Call mcp__jcodemunch__index_repo with path "$root"
2) Call mcp__jcodemunch__get_repo_outline to fetch the outline
3) Call mcp__jcodemunch__get_tectonic_map to fetch module clusters
Then synthesize a JSON document with shape:
{
  "version": 1,
  "built_at": "<iso-utc>",
  "stale": false,
  "nodes": [{"id": "...", "name": "...", "type": "file|symbol|doc|module", "degree": N}],
  "edges": [{"source": "...", "target": "...", "kind": "imports|calls|refs"}],
  "communities": [{"id": "...", "label": "...", "members": ["..."]}]
}
Output ONLY the JSON — no prose, no fences.
EOF
      )
      # Validate output
      if [[ -s "$cache.raw" ]] && python3 -c "import json; json.load(open('$cache.raw'))" 2>/dev/null; then
        mv "$cache.raw" "$cache"
        echo -e "${GREEN}✓ built via claude CLI${NC}"
      else
        echo -e "${YELLOW}claude mode produced invalid JSON — falling back to basic${NC}"
        rm -f "$cache.raw"
        mode="basic"
      fi
      ;;
  esac

  if [[ "$mode" == "basic" ]]; then
    echo -e "${GRAY}Mode: basic (file topology)${NC}"
    python3 - "$root" "$cache" <<'PY'
import json, os, sys
from datetime import datetime, timezone

root, out = sys.argv[1], sys.argv[2]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".claude", ".next",
             "dist", "build", ".idea", ".vscode", ".pytest_cache", "target", ".gradle",
             ".DS_Store", ".cache", "vendor"}
CODE_EXTS = {".py",".js",".ts",".tsx",".jsx",".go",".rs",".java",".kt",".swift",
             ".dart",".rb",".php",".cs",".cpp",".c",".h",".hpp",".sh",".bash"}
DOC_EXTS  = {".md",".mdx",".rst",".txt",".pdf"}

nodes = []
edges = []
seen = set()
dir_degree = {}

for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
    rel_dir = os.path.relpath(dirpath, root)
    if rel_dir == ".":
        rel_dir = ""
    if rel_dir and rel_dir not in seen:
        seen.add(rel_dir)
        nodes.append({"id": rel_dir, "name": os.path.basename(rel_dir) or rel_dir,
                      "type": "module", "degree": 0, "path": rel_dir})
        parent = os.path.dirname(rel_dir)
        if parent:
            edges.append({"source": parent, "target": rel_dir, "kind": "contains"})
            dir_degree[parent] = dir_degree.get(parent, 0) + 1
            dir_degree[rel_dir] = dir_degree.get(rel_dir, 0) + 1
    for fn in filenames:
        if fn.startswith("."):
            continue
        ext = os.path.splitext(fn)[1].lower()
        full = os.path.join(rel_dir, fn) if rel_dir else fn
        if ext in CODE_EXTS:
            ntype = "file"
        elif ext in DOC_EXTS:
            ntype = "doc"
        else:
            continue
        if full in seen:
            continue
        seen.add(full)
        nodes.append({"id": full, "name": fn, "type": ntype, "degree": 1, "path": full})
        parent = rel_dir or ""
        if parent:
            edges.append({"source": parent, "target": full, "kind": "contains"})
            dir_degree[parent] = dir_degree.get(parent, 0) + 1

# Write back directory degrees
for n in nodes:
    if n["type"] == "module":
        n["degree"] = dir_degree.get(n["id"], 0)

# Simple community detection: top-level directory
communities = {}
for n in nodes:
    key = (n.get("path") or n["id"]).split(os.sep)[0] or "root"
    communities.setdefault(key, {"id": key, "label": key, "members": []})
    communities[key]["members"].append(n["id"])

graph = {
    "version": 1,
    "built_at": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
    "stale": False,
    "mode": "basic",
    "root": root,
    "nodes": nodes,
    "edges": edges,
    "communities": list(communities.values()),
}
with open(out, "w") as f:
    json.dump(graph, f, indent=2)
print(f"✓ wrote {len(nodes)} nodes, {len(edges)} edges, {len(communities)} communities → {out}")
PY
  fi
}

cmd_docs() {
  bash "$SCRIPT_DIR/hq-graph-docs.sh" "$@"
}

cmd_transcribe() {
  bash "$SCRIPT_DIR/hq-graph-transcribe.sh" "$@"
}

cmd_view() {
  bash "$SCRIPT_DIR/hq-graph-view.sh" "$@"
}

# --- MAIN ---
case "${1:-}" in
  install)    shift; cmd_install "$@" ;;
  uninstall)  shift; cmd_uninstall "$@" ;;
  status)     shift; cmd_status "$@" ;;
  build)      shift; cmd_build "$@" ;;
  docs)       shift; cmd_docs "$@" ;;
  transcribe) shift; cmd_transcribe "$@" ;;
  view)       shift; cmd_view "$@" ;;
  --help|-h|"") usage ;;
  *) echo -e "${RED}Unknown subcommand:${NC} $1"; usage; exit 1 ;;
esac

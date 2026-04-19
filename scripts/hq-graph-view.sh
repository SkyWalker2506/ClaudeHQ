#!/usr/bin/env bash
# hq-graph-view.sh — Render graph-cache.json as an interactive HTML (vis.js) and open it.
# Usage: hq graph view <project> [--no-open]
set -euo pipefail

HQ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_ROOT="${HQ_PROJECTS_ROOT:-$HOME/Projects}"
PROJECTS_FILE="$HQ_DIR/projects.json"

RED=$'\033[0;31m'; GREEN=$'\033[0;32m'; BLUE=$'\033[0;34m'; GRAY=$'\033[0;90m'; NC=$'\033[0m'

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
    [[ -n "$p" && -d "$p" ]] && { echo "$p"; return 0; }
  fi
  [[ -d "$PROJECTS_ROOT/$name" ]] && { echo "$PROJECTS_ROOT/$name"; return 0; }
  return 1
}

name="${1:-}"
open_flag=1
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-open) open_flag=0; shift ;;
    *) shift ;;
  esac
done

[[ -z "$name" ]] && { echo "${RED}error:${NC} project name required"; exit 1; }
root="$(resolve_project_path "$name")" || { echo "${RED}error:${NC} project '$name' not found"; exit 1; }
cache="$root/.claude/graph-cache.json"
[[ -f "$cache" ]] || { echo "${RED}error:${NC} run 'hq graph build $name' first"; exit 1; }

html="$root/.claude/graph.html"
echo "${BLUE}Rendering:${NC} $html"

python3 - "$cache" "$html" "$name" <<'PY'
import json, sys, html as H, hashlib

cache_path, out_path, project = sys.argv[1], sys.argv[2], sys.argv[3]
with open(cache_path) as f:
    g = json.load(f)

nodes = g.get("nodes", [])
edges = g.get("edges", [])
communities = g.get("communities", [])

# Map node -> community
node_to_comm = {}
for c in communities:
    for m in c.get("members", []):
        node_to_comm[m] = c.get("id", "")

palette = ["#4F46E5","#059669","#DC2626","#D97706","#7C3AED","#0891B2","#DB2777","#65A30D",
           "#2563EB","#EA580C","#0D9488","#9333EA","#16A34A","#F59E0B","#EF4444","#14B8A6"]
def color_for(key):
    if not key: return "#6B7280"
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return palette[h % len(palette)]

type_shape = {"doc":"box","file":"dot","module":"diamond","symbol":"triangle"}

vis_nodes = []
for n in nodes:
    nid = n["id"]
    comm = node_to_comm.get(nid, "")
    deg = n.get("degree", 1) or 1
    size = 8 + min(deg, 40)
    vis_nodes.append({
        "id": nid,
        "label": n.get("name") or nid,
        "title": f"{n.get('type','?')}: {nid}<br>degree: {deg}" + (f"<br>community: {comm}" if comm else ""),
        "color": color_for(comm or n.get("type","")),
        "shape": type_shape.get(n.get("type"), "dot"),
        "size": size,
        "group": comm or n.get("type",""),
    })

vis_edges = []
for i, e in enumerate(edges):
    vis_edges.append({
        "id": i,
        "from": e.get("source"),
        "to": e.get("target"),
        "arrows": "to" if e.get("kind") in ("calls","refs","imports") else "",
        "color": {"color": "#D1D5DB", "opacity": 0.5},
        "smooth": False,
    })

data_json = json.dumps({"nodes": vis_nodes, "edges": vis_edges})

html_doc = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Graph — {H.escape(project)}</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
 html,body {{ margin:0; padding:0; background:#0F172A; color:#E2E8F0; font-family:system-ui,sans-serif; }}
 #bar {{ padding:10px 16px; background:#1E293B; border-bottom:1px solid #334155; display:flex; gap:16px; align-items:center; }}
 #bar b {{ color:#F1F5F9; }}
 #bar .stat {{ color:#94A3B8; font-size:12px; }}
 #net {{ width:100vw; height:calc(100vh - 52px); }}
 input {{ background:#0F172A; border:1px solid #334155; color:#E2E8F0; padding:6px 10px; border-radius:4px; width:220px; }}
</style>
</head>
<body>
<div id="bar">
  <b>{H.escape(project)}</b>
  <span class="stat">{len(nodes)} nodes · {len(edges)} edges · {len(communities)} communities</span>
  <input id="q" placeholder="filter nodes (substring)…"/>
</div>
<div id="net"></div>
<script>
 const raw = {data_json};
 const data = {{
   nodes: new vis.DataSet(raw.nodes),
   edges: new vis.DataSet(raw.edges),
 }};
 const opts = {{
   nodes: {{ font: {{ color:"#E2E8F0", size:11 }} }},
   edges: {{ width: 0.6 }},
   physics: {{ solver: "forceAtlas2Based",
              forceAtlas2Based: {{ gravitationalConstant:-50, springLength:80, avoidOverlap:0.5 }},
              stabilization: {{ iterations: 220 }} }},
   interaction: {{ hover:true, tooltipDelay:120 }},
 }};
 const network = new vis.Network(document.getElementById("net"), data, opts);

 document.getElementById("q").addEventListener("input", (e) => {{
   const q = e.target.value.toLowerCase();
   const matching = new Set();
   data.nodes.forEach(n => {{
     if (!q || (n.label||"").toLowerCase().includes(q) || (n.id||"").toLowerCase().includes(q)) {{
       matching.add(n.id);
     }}
   }});
   data.nodes.update(raw.nodes.map(n => ({{ id: n.id, hidden: q && !matching.has(n.id) }})));
 }});
</script>
</body>
</html>
"""
open(out_path, "w").write(html_doc)
print(f"✓ wrote {out_path} ({len(vis_nodes)} nodes, {len(vis_edges)} edges)")
PY

if [[ $open_flag -eq 1 ]]; then
  if command -v open >/dev/null 2>&1; then
    open "$html"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$html"
  else
    echo "${GRAY}open manually: $html${NC}"
  fi
fi
echo "${GREEN}✓ view generated${NC}"

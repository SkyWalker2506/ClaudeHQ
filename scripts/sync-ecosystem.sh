#!/usr/bin/env bash
set -euo pipefail

# sync-ecosystem.sh — Count from source of truth, update all downstream README pages
# Usage: ./scripts/sync-ecosystem.sh [--dry-run]
#
# Source of truth:
#   Agents     → claude-config/agents/**/*.md (excl README.md)
#   Categories → claude-config/agents/*/
#   Plugins    → ccplugin-* directories in ~/Projects
#   Skills     → claude-config/global/skills/*/
#   Marketplace → claude-marketplace/.claude-plugin/marketplace.json
#
# Downstream pages updated:
#   ClaudeHQ/README.md
#   claude-marketplace/README.md
#   claude-agent-catalog/README.md
#   claude-marketplace/.claude-plugin/marketplace.json (description)

PROJECTS_ROOT="${HOME}/Projects"
DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# --- COUNT FROM SOURCE OF TRUTH ---

AGENTS_DIR="$PROJECTS_ROOT/claude-config/agents"
SKILLS_DIR="$PROJECTS_ROOT/claude-config/global/skills"
MARKETPLACE_JSON="$PROJECTS_ROOT/claude-marketplace/.claude-plugin/marketplace.json"

agent_count=$(find "$AGENTS_DIR" -mindepth 2 -maxdepth 2 -name "AGENT.md" 2>/dev/null | wc -l | tr -d ' ')
category_count=$(find "$AGENTS_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
plugin_repo_count=$(find "$PROJECTS_ROOT" -maxdepth 1 -name "ccplugin-*" -type d 2>/dev/null | wc -l | tr -d ' ')
marketplace_count=$(jq '.plugins | length' "$MARKETPLACE_JSON" 2>/dev/null || echo 0)
skill_count=$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')

echo -e "${BOLD}Ecosystem stats (source of truth):${NC}"
echo "  Agents:       $agent_count (across $category_count categories)"
echo "  Plugins:      $plugin_repo_count repos, $marketplace_count in marketplace.json"
echo "  Skills:       $skill_count"
echo ""

# --- UPDATE DOWNSTREAM PAGES ---

changed=()

# Helper: sed in-place with macOS compatibility
sedi() {
  sed -i '' "$@"
}

# Helper: replace pattern in file, report result
replace_in() {
  local file="$1" pattern="$2" replacement="$3" label="$4"
  [[ -f "$file" ]] || { echo -e "  ${YELLOW}SKIP${NC} $(basename "$file") (not found)"; return 0; }

  if grep -qE "$pattern" "$file"; then
    if $DRY_RUN; then
      echo -e "  ${BLUE}[dry]${NC} $label → $(basename "$file")"
    else
      sedi -E "s#${pattern}#${replacement}#g" "$file"
      echo -e "  ${GREEN}OK${NC} $label → $(basename "$file")"
      # Track unique files
      local already=false
      for f in "${changed[@]+"${changed[@]}"}"; do [[ "$f" == "$file" ]] && already=true; done
      $already || changed+=("$file")
    fi
  fi
}

echo -e "${BOLD}Updating downstream pages:${NC}"

# ─── ClaudeHQ/README.md ─────────────────────────────────────────────
R="$PROJECTS_ROOT/ClaudeHQ/README.md"
replace_in "$R" \
  "Plugin marketplace — [0-9]+ plugins" \
  "Plugin marketplace — $plugin_repo_count plugins" \
  "plugin count (top)"
replace_in "$R" \
  "Agent catalog — [0-9]+ agents across [0-9]+ categories" \
  "Agent catalog — $agent_count agents across $category_count categories" \
  "agent count"
replace_in "$R" \
  "Multi-Agent OS — [0-9]+ agents" \
  "Multi-Agent OS — $agent_count agents" \
  "config agent count"
replace_in "$R" \
  "Plugin Marketplace — [0-9]+ plugins" \
  "Plugin Marketplace — $plugin_repo_count plugins" \
  "marketplace count (bottom)"

# ─── claude-config/README.md ─────────────────────────────────────────
R="$PROJECTS_ROOT/claude-config/README.md"
replace_in "$R" \
  "Multi-Agent OS for Claude Code.* — [0-9]+ agents, [0-9]+ plugins" \
  "Multi-Agent OS for Claude Code** — $agent_count agents, $plugin_repo_count plugins" \
  "header line"
replace_in "$R" \
  '\*\*[0-9]+ AI agents\*\* across [0-9]+ categories' \
  "**${agent_count} AI agents** across ${category_count} categories" \
  "agent count"
replace_in "$R" \
  '\*\*[0-9]+ plugins\*\* published' \
  "**${plugin_repo_count} plugins** published" \
  "plugin count"
replace_in "$R" \
  "[0-9]+ plugins, each in its own repo" \
  "${plugin_repo_count} plugins, each in its own repo" \
  "plugins section"
replace_in "$R" \
  "[0-9]+ agents across [0-9]+ categories\. Each agent" \
  "${agent_count} agents across ${category_count} categories. Each agent" \
  "agents section"
replace_in "$R" \
  "Plugin Marketplace.* — [0-9]+ plugins" \
  "Plugin Marketplace](https://github.com/SkyWalker2506/claude-marketplace) — $plugin_repo_count plugins" \
  "related links plugins"
replace_in "$R" \
  "Agent Catalog.* — [0-9]+ agents across [0-9]+ categories" \
  "Agent Catalog](https://github.com/SkyWalker2506/claude-agent-catalog) — $agent_count agents across $category_count categories" \
  "related links agents"

# ─── claude-marketplace/README.md ────────────────────────────────────
R="$PROJECTS_ROOT/claude-marketplace/README.md"
replace_in "$R" \
  '\*\*[0-9]+ plugins\*\*' \
  "**${plugin_repo_count} plugins**" \
  "plugin count"

# ─── claude-agent-catalog/README.md ─────────────────────────────────
R="$PROJECTS_ROOT/claude-agent-catalog/README.md"
replace_in "$R" \
  '\*\*[0-9]+ AI agents\*\*' \
  "**${agent_count} AI agents**" \
  "agent count"
replace_in "$R" \
  '\*\*[0-9]+ categories\*\*' \
  "**${category_count} categories**" \
  "category count"

# ─── marketplace.json description ────────────────────────────────────
if [[ -f "$MARKETPLACE_JSON" ]]; then
  current_desc=$(jq -r '.description' "$MARKETPLACE_JSON")
  if echo "$current_desc" | grep -qE '[0-9]+ plugins'; then
    new_desc=$(echo "$current_desc" | sed -E "s/[0-9]+ plugins/${marketplace_count} plugins/")
    if [[ "$current_desc" != "$new_desc" ]]; then
      if $DRY_RUN; then
        echo -e "  ${BLUE}[dry]${NC} description → marketplace.json"
      else
        jq --arg d "$new_desc" '.description = $d' "$MARKETPLACE_JSON" > "$MARKETPLACE_JSON.tmp"
        mv "$MARKETPLACE_JSON.tmp" "$MARKETPLACE_JSON"
        echo -e "  ${GREEN}OK${NC} description → marketplace.json"
        changed+=("$MARKETPLACE_JSON")
      fi
    fi
  fi
fi

# --- SUMMARY ---
echo ""
if [[ ${#changed[@]} -eq 0 ]]; then
  echo -e "${GREEN}All pages up to date.${NC}"
else
  echo -e "${YELLOW}${#changed[@]} file(s) updated across repos:${NC}"
  for f in "${changed[@]}"; do
    # Show repo-relative path
    local_path="${f#$PROJECTS_ROOT/}"
    repo_name="${local_path%%/*}"
    echo "  $repo_name → ${local_path#*/}"
  done
  echo ""
  echo "Review changes, then commit in each repo."
fi

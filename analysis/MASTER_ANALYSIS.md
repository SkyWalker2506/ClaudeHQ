# MASTER_ANALYSIS — Ecosystem Overhaul
Generated: 2026-04-14

## Sprint: Ecosystem Coherence

### Task 1 — Catalog README + CI sync [claude-agent-catalog]
- Update README table: all 196 agents, all 15 categories (currently 134/196)
- Add .github/workflows/sync-catalog.yml

### Task 2 — fix install.sh silent failures [claude-config]
- Line 245-255: explicit git clone validation
- Line 325+: skill source existence check
- Early permission check + MCP connectivity test

### Task 3 — ClaudeHQ projects table sync [ClaudeHQ]
- Add 11 missing projects to README
- Add Git Repo + Category columns

### Task 4 — Skills inventory [claude-config]
- Create global/SKILLS_INVENTORY.md (54 skills, not 34)
- Update README badge

### Task 5 — Agent-plugin mapping [claude-config]
- Create AGENT_PLUGIN_MAP.md from registry + plugin metadata

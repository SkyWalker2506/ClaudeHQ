# ClaudeHQ

**Central hub for the Claude Code ecosystem — by Musab Kara**

ClaudeHQ is the entry point to my Claude-powered development ecosystem. It connects all configuration, plugins, agents, and projects under one roof. Open this repo in Claude Code to manage your entire workspace from a single session.

---

## Quick Start

```bash
# Clone and install the ecosystem foundation
git clone https://github.com/SkyWalker2506/claude-config.git ~/Projects/claude-config
cd ~/Projects/claude-config && ./install.sh
```

That's it. `install.sh` sets up CLAUDE.md redirectors, MCP servers, skills, and agent registry across all your projects.

---

## Ecosystem

| Repository | Description | Link |
|-----------|-------------|------|
| **claude-config** | Rules, skills, agent definitions, plugin registry. Installed into every project. | [repo](https://github.com/SkyWalker2506/claude-config) |
| **claude-marketplace** | Plugin marketplace — 18 plugins and growing | [repo](https://github.com/SkyWalker2506/claude-marketplace) |
| **claude-agent-catalog** | Agent catalog — 134 agents across 15 categories | [repo](https://github.com/SkyWalker2506/claude-agent-catalog) |
| **ccplugin-*** | Individual plugin repos (notifications, jira, firebase, etc.) | [search](https://github.com/SkyWalker2506?tab=repositories&q=ccplugin) |

---

## Projects

Managed projects in the ecosystem:

| Project | Jira | Description |
|---------|------|-------------|
| ar-research | — | AR research & prototyping |
| ByteCraftHQ | — | ByteCraft studio HQ |
| Viralyze | — | Social media analytics |
| VocabLearningApp | VOC | Vocabulary learning app |
| football-ai-platform | — | Football AI / Tartismali Pozisyonlar |
| KnightOnlineAI | — | Knight Online AI bot |
| ProjeBirlik | — | Community project platform |
| trading-bot | — | Trading automation |
| transcriptr | — | Transcription tool |

---

## New Project

Set up a new project with the full Claude ecosystem:

```bash
# 1. Create the project
mkdir ~/Projects/my-new-project && cd ~/Projects/my-new-project
git init

# 2. Install claude-config
cd ~/Projects/claude-config && ./install.sh

# 3. (Optional) Add to projects.json in ClaudeHQ
# 4. (Optional) Create Jira project and link
```

The installer handles CLAUDE.md, .claudeignore, MCP configuration, and skill registration.

---

## HQ Usage

Open ClaudeHQ in Claude Code to work across projects:

```bash
cd ~/Projects/ClaudeHQ
claude
```

From here you can:

- **Cross-project tasks** — "Update the README in all projects"
- **Ecosystem management** — "Show me all plugin statuses"
- **New project setup** — "Create a new project called X"
- **Jira overview** — "What's in progress across all projects?"
- **Agent dispatch** — Route tasks to the right agent in any project

ClaudeHQ reads `projects.json` to know which projects exist and where they live. This file is local-only (gitignored) so each machine can have its own workspace layout.

---

## Architecture

```
ClaudeHQ (you are here)
  |
  +-- claude-config/        # Rules, skills, agents, plugins
  |     +-- install.sh      # Ecosystem installer
  |     +-- global/skills/  # Shared skills
  |     +-- agents/         # 134 agent definitions
  |     +-- config/         # Agent registry, model tiers, fallback chains
  |
  +-- claude-marketplace/   # Plugin discovery & distribution
  +-- ccplugin-*/           # Individual plugins
  +-- [your projects]/      # All managed projects
```

---

## Ecosystem

| Repo | Description |
|------|-------------|
| [claude-config](https://github.com/SkyWalker2506/claude-config) | Multi-Agent OS — 134 agents, local-first routing, cost-aware orchestration |
| [claude-marketplace](https://github.com/SkyWalker2506/claude-marketplace) | Claude Code Plugin Marketplace — 18 plugins, one-command install |
| [claude-agent-catalog](https://github.com/SkyWalker2506/claude-agent-catalog) | Agent catalog — 134 agents across 15 categories |
| [sdk-market](https://github.com/SkyWalker2506/sdk-market) | SDK Market — production-ready kits for Flutter and beyond |

---

*Built with Claude Code by Musab Kara*

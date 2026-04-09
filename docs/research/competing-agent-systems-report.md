# Competing Agent Systems — Research Report

> Date: 2026-04-09
> Researcher: K9 (AI Tool Evaluator)
> Scope: 11 agent systems analyzed for architecture, definition format, knowledge/memory patterns

---

## Executive Summary

We analyzed 11 agent/skill systems to understand how the industry defines, configures, and manages AI agents. Our Knowledge-First approach (AGENT.md + knowledge/ + memory/ per agent in a multi-agent registry) is **unique in combining all three dimensions** (persona, knowledge, memory) in a file-based, git-native format. The closest competitor is **GitAgent** (2.6k stars), which shares our philosophy but targets single-agent-per-repo rather than multi-agent orchestration.

---

## Systems Analyzed

| # | System | Stars | Definition Format | Persona | Knowledge Dir | Per-Agent Memory | Git-Native |
|---|--------|-------|-------------------|---------|---------------|-----------------|------------|
| 1 | **GitAgent** | 2.6k | SOUL.md + agent.yaml | Yes | Yes | Yes | Yes |
| 2 | **OpenAI Codex** | 67k+ | AGENTS.md (markdown) | No | No | Internal | Partial |
| 3 | **Anthropic Skills** | 113k | SKILL.md (YAML+md) | No | Optional | No | Yes |
| 4 | **Superpowers** | 142k | Skill folders | No | Distributed | No | Yes |
| 5 | **CrewAI** | N/A | YAML (role/goal/backstory) | Yes | Yes | Yes (code) | No |
| 6 | **Cursor** | N/A | .mdc (YAML+md) | Optional | No | No | Yes |
| 7 | **Windsurf** | N/A | .windsurfrules | No | Codemaps | Memories | No |
| 8 | **Devin** | N/A | .rules + playbooks | No | Knowledge Graph | Internal | No |
| 9 | **LangGraph** | N/A | Python code | No | Code-configured | Checkpoints | No |
| 10 | **MATE** | 42 | Database (PostgreSQL) | No | DB memory blocks | DB-backed | No |
| 11 | **AgentSkills Spec** | 15.5k | SKILL.md (YAML+md) | No | Optional | No | Yes |

---

## Detailed Findings

### Tier 1: Most Similar to Our Approach

**GitAgent (open-gitagent/gitagent)** — https://github.com/open-gitagent/gitagent
- SOUL.md for identity + agent.yaml for config + knowledge/ + memory/
- Uses git branches + PRs for human-in-the-loop memory updates
- Separates RULES.md and DUTIES.md from persona (we embed rules in AGENT.md)
- Single-agent-per-repo model (vs our multi-agent registry)

**CrewAI** — https://docs.crewai.com/en/concepts/agents
- YAML with role/goal/backstory + 25 parameters
- knowledge/ directory, knowledge_sources per agent, memory=True flag
- Requires Python runtime; agents are code-instantiated, not file-system-native

### Tier 2: Instruction-Injection Only (No Agent Identity)

**OpenAI Codex** — https://developers.openai.com/codex/guides/agents-md
- AGENTS.md hierarchical discovery (global -> project -> subdirectory)
- Skills via SKILL.md in .agents/skills/
- No persona, no per-agent knowledge, internal memory only

**Cursor** — https://cursor.com/docs/context/rules
- .cursor/rules/*.mdc with YAML frontmatter (description, alwaysApply, globs)
- Can include persona-style instructions but no structured persona
- No knowledge directory, no persistent memory

**Windsurf** — .windsurfrules + Memories feature
- Codemaps for codebase understanding
- Memories persist context but unstructured
- 5 parallel agents (Feb 2026)

### Tier 3: Code-First / Proprietary

**LangGraph** — https://www.langchain.com/langgraph
- Graph-based state management with typed schemas
- Most sophisticated memory (short-term checkpoints, long-term namespaces, episodic)
- Requires Python code; no declarative agent files

**Devin** — https://devin.ai
- Auto-indexes codebases into knowledge graph
- Playbooks for workflow instructions
- Proprietary, non-portable

**MATE** — https://github.com/antiv/mate
- Database-driven agent configs (PostgreSQL)
- RBAC, multi-tenant, agents can create other agents at runtime
- Enterprise-focused, not portable

### Tier 4: Skill-Only (No Agent Layer)

**Anthropic Skills** / **AgentSkills Spec** — Foundation format we already use
- SKILL.md with YAML frontmatter + markdown instructions
- We extend this with AGENT.md, knowledge/, memory/

**Superpowers** — https://github.com/obra/superpowers
- Workflow-triggered skills, platform adapters
- No agent identity or memory concept

---

## Key Insights

### 1. Our Unique Position
No other system combines: (a) per-agent persona files, (b) per-agent knowledge directories, (c) per-agent persistent memory, (d) multi-agent registry — all in a git-native, file-based format.

### 2. Industry Trends
- **2025-2026 shift:** From single-agent instructions to multi-agent orchestration
- **Skills as standard:** SKILL.md is becoming an industry standard (Anthropic, Codex, Superpowers all converge)
- **Memory is the frontier:** Every system is investing in memory persistence; LangGraph and Devin lead here

### 3. Opportunities
- **Adopt agent.yaml:** Add machine-readable manifest alongside AGENT.md (like GitAgent) for tooling
- **Separate RULES.md:** GitAgent's approach of splitting rules from persona is cleaner
- **Consider skill compatibility:** Ensure our skills remain compatible with AgentSkills spec for portability
- **Watch GitAgent:** Most philosophically aligned competitor; potential for format convergence

### 4. Risks
- GitAgent could gain traction as the "open standard" for file-based agents
- CrewAI's richer parameter set could attract users who want more control
- If Codex/Cursor add persona support, they'd reach our space with much larger user bases

---

## Sources

- https://github.com/open-gitagent/gitagent
- https://developers.openai.com/codex/guides/agents-md
- https://github.com/anthropics/skills
- https://github.com/obra/superpowers
- https://docs.crewai.com/en/concepts/agents
- https://cursor.com/docs/context/rules
- https://devin.ai/agents101
- https://www.langchain.com/langgraph
- https://github.com/antiv/mate
- https://github.com/agentskills/agentskills
- https://medium.com/@dave-patten/the-state-of-ai-coding-agents-2026-from-pair-programming-to-autonomous-ai-teams-b11f2b39232a
- https://deepfounder.ai/ai-coding-agents-2026-guide/

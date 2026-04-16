# Harness Engineering — Dispatch Package

> Her görev için: Agent, Model, Prompt hazır. Kullanıcı uygun modele iletir.

---

## GÖREV HARİTASI

| # | Görev | Agent | Model | Backend | Süre |
|---|-------|-------|-------|---------|------|
| T1 | N6 Knowledge Sharpening | K1 Web Researcher | GPT 5.4 | Codex CLI | ~5 dk |
| T2 | CLAUDE.md Dispatch Rule Fix | N6 AI Systems Architect | GPT 5.4 | Codex CLI | ~3 dk |
| T3 | Dispatch Knowledge Injection | N6 AI Systems Architect | GPT 5.4 | Codex CLI | ~10 dk |
| T4 | Telemetry Pipeline Fix | B2 Backend Coder | GPT 5.4 | Codex CLI | ~5 dk |
| T5 | CLAUDE.md Three-Layer Split | N6 AI Systems Architect | Gemini 3.1 Pro | Gemini CLI | ~15 dk |
| T6 | Review All Changes | C3 AI Reviewer | Gemini 3.1 Pro | Gemini CLI | ~5 dk |

**Sıra:** T1 → T2 → T3 → T4 → T5 → T6
**T2+T3 paralel yapılabilir** (farklı dosyalar)

---

## T1: N6 Knowledge Sharpening

**Agent:** K1 Web Researcher
**Model:** GPT 5.4
**Backend:** `codex exec --model gpt-5.4 --full-auto`
**Çalışma dizini:** `~/Projects/claude-config`

### Prompt:

```
You are K1 Web Researcher. Update knowledge files for agent N6 (AI Systems Architect).

Working directory: this repo (claude-config)
Target: agents/prompt-engineering/ai-systems-architect/knowledge/

## Task 1: APPEND to orchestration-patterns.md

Add a new section "## 2026 Harness Engineering Research" at the END of the file. Include:

### Meta-Harness (Stanford, March 2026)
- Automated harness optimization: proposer reads execution traces (~82 files), diagnoses failures, writes new harness
- Haiku with optimized harness outranked Opus on TerminalBench 2
- Self-evolution is THE ONLY consistently helpful module (+4.8 SWE-bench, +2.7 OS World)
- Verifiers actively hurt performance (-0.8 and -8.4 in ablation)
- Multi-candidate search hurt (-2.4 and -5.6)
- Harness optimized on one model transfers to 5 others

### LangChain TerminalBench 2 (rank 30+ to rank 5, harness only)
- Context assembly (feedforward guide): inject env info, tools, best practices upfront
- Self-verification loops: BUILD → TEST → VERIFY → FIX cycle
- Trace-driven debugging: analyze execution traces for patterns
- Loop detection: same tool+args 3x → intervene; 80% budget → warning
- Model-specific tuning per model

### Anthropic's 5 Canonical Patterns
1. Prompt Chaining — sequential for decomposable tasks
2. Routing — classify → specialized handler
3. Parallelization — independent subtasks or voting
4. Orchestrator-Workers — central LLM delegates to workers
5. Evaluator-Optimizer — generate + feedback loop

Do NOT delete existing content. Only append.

## Task 2: APPEND to context-engineering.md

Add "## 2026 Context Engineering Advances" at the END. Include:

### Manus Context Engineering (5 principles)
1. KV-cache hit rate is #1 metric — stable system prompts, append-only contexts
2. Mask tools (don't remove) — cache stability while controlling behavior
3. Filesystem as extended memory — working_memory.json, todo.md instead of compressing
4. todo.md recitation — agent rewrites todo.md continuously, keeps plan in attention window
5. Preserve error traces — don't hide failures, models learn from visible mistakes

### NLH Three-Layer Separation (Tingua, March 2026)
- Layer 1: Harness Logic — task-family control (roles, stages, verification gates)
- Layer 2: Runtime Charter — shared execution semantics and policies
- Layer 3: Deterministic Scripts — tools, tests, adapters (file-backed)
- Representation change alone: +16.8 benchmark points, runtime 361→141 min, LLM calls 1200→34

### Execution Contracts
- Required outputs (file paths, artifacts)
- Token/tool-call budgets
- Completion conditions (gates)
- Permissions and artifact output paths
- Like function signatures for agent calls

### AgentSpec Safety DSL
- Declarative rules: trigger → check → enforce
- Prevented 90%+ unsafe executions with millisecond overhead

## Task 3: CREATE new file harness-engineering-claude-config.md

```markdown
---
last_updated: 2026-04-16
refined_by: gpt-5.4
confidence: high
---

# Harness Engineering — claude-config Specifics

## Current Architecture
- Jarvis (A0): orchestrator, never implements, dispatches to 196 agents (15 categories)
- CLAUDE.md: 715-line monolithic rules file loaded every session as system prompt
- Dispatch flow: /dispatch skill → agent-router.sh → Agent tool with header
- Dispatch header fields: AGENT, MODEL, EFFORT, TASK, CALLER, WATCHDOG
- Agent registry: config/agent-registry.json (model, fallbacks, capabilities per agent)
- Agent definitions: agents/{category}/{slug}/AGENT.md + knowledge/ + memory/

## Critical Problems Identified
1. CLAUDE.md "dispatch-first" rule at line 680 of 715 — LLM ignores it
2. Sub-agents get NO knowledge — dispatch injects only a header, not AGENT.md or knowledge files
3. Telemetry broken — log_dispatch.py writes "unknown" for every event
4. No execution contracts — tasks dispatched with prose, no completion gates
5. No file-backed state — long tasks lose state on compaction

## Fix Targets
1. CLAUDE.md line 1-5: dispatch-first rule must be first thing model reads
2. Two-Tier Knowledge Loading:
   - Tier 1 (dispatch-time): Read AGENT.md + knowledge/_index.md, inject into prompt
   - Tier 2 (on-demand): Agent reads specific knowledge/*.md based on task
3. Sidecar telemetry: write dispatch metadata to /tmp/watchdog/current_dispatch.json before Agent tool
4. Three-layer split: CLAUDE.md → charter.md (behavior) + harness.md (control) + deterministic (config)
5. Execution contracts: structured header with required_outputs, completion_gate, max_tool_calls

## Key File Paths
- global/CLAUDE.md — master rules (target: restructure)
- global/skills/dispatch/SKILL.md — dispatch protocol (target: add knowledge injection)
- config/agent-dispatch.md — dispatch header template (target: add KNOWLEDGE + CONTRACT blocks)
- config/agent-registry.json — 196 agents, 41 active
- scripts/log_dispatch.py — telemetry logger (target: sidecar fallback)
- config/fallback-chains.json — model fallback per task type
- config/layer-contracts.json — Ultra Plan Mode structured output
```

Update _index.md to include the new file.

Commit with message: "feat(N6): sharpen knowledge with 2026 harness engineering research"
```

---

## T2: CLAUDE.md Dispatch Rule Fix

**Agent:** N6 AI Systems Architect
**Model:** GPT 5.4
**Backend:** `codex exec --model gpt-5.4 --full-auto`
**Çalışma dizini:** `~/Projects/claude-config`

### Prompt:

```
You are N6 AI Systems Architect.

## Task: Move dispatch-first rule to top of CLAUDE.md

Read global/CLAUDE.md. Prepend these exact lines at the VERY TOP (before all existing content):

# TEMEL KURAL — HER SEYDEN ONCE OKU
SEN JARVIS'SIN. ASLA KENDIN IS YAPMAZSIN.
Kod yazma, dosya duzenleme, test calistirma, debug — HICBIRINI yapma.
Her gorevi uygun agent'a dispatch et. Sen sadece orkestratorsun.
Bu kural istisnasiz ve tartismasizdir.

Then add one blank line, then ALL existing content follows unchanged.

Rules:
- Do NOT delete or modify any existing content
- Do NOT reorganize the file
- ONLY prepend these 6 lines (5 lines + 1 blank)
- The existing section 11 "Temel Kural" at line ~680 stays as the detailed version

Commit: "fix: move dispatch-first rule to line 1 for LLM attention priority"
```

---

## T3: Dispatch Knowledge Injection (Two-Tier Loading)

**Agent:** N6 AI Systems Architect
**Model:** GPT 5.4
**Backend:** `codex exec --model gpt-5.4 --full-auto`
**Çalışma dizini:** `~/Projects/claude-config`

### Prompt:

```
You are N6 AI Systems Architect. Your task is to fix the biggest harness problem: sub-agents start with zero knowledge.

## Problem
When /dispatch dispatches a sub-agent, it only sends a header (agent ID, model, capabilities). It does NOT inject:
- The agent's AGENT.md (identity, boundaries, process)
- The agent's knowledge/_index.md (knowledge map)
- Any knowledge file content

Sub-agents act like blank models because they never see their own definition.

## What to Fix

### 1. Update config/agent-dispatch.md

Read the current file. Add a new KNOWLEDGE block to the dispatch header template. The full template should look like:

---
AGENT: {id} — {name}
ROLE: {description}
MODEL: {primary_model} | EFFORT: {effort}
TASK: {task summary}
CALLER: {caller agent id or "user"}
WATCHDOG: {quick|medium|long} — max {N} tool call

KNOWLEDGE:
  identity: |
    {content from AGENT.md: Identity + Boundaries sections}
  knowledge_index: |
    {content from knowledge/_index.md}
  knowledge_path: agents/{category}/{slug}/knowledge/
  instruction: Read knowledge files relevant to your task from the path above before starting work.
---

### 2. Update global/skills/dispatch/SKILL.md

Read the current file. Find the section where the sub-agent prompt is assembled (where it builds the dispatch header). Add these steps BEFORE the Agent tool is called:

Step: Knowledge Assembly
1. From the selected agent's registry entry, get category and slug
2. Read file: agents/{category}/{slug}/AGENT.md — extract Identity and Boundaries sections
3. Read file: agents/{category}/{slug}/knowledge/_index.md — full content
4. Inject both into the KNOWLEDGE block of the dispatch header
5. Set knowledge_path so the agent knows where to find detailed files

Add this as a clear instruction in the skill's workflow, after agent selection and before sub-agent launch.

### 3. Update the AGENT.md frontmatter convention

Read agents/prompt-engineering/ai-systems-architect/AGENT.md as a reference.
The existing "slug" for path resolution should be derivable from the agent directory name.
No changes needed to AGENT.md files — the dispatch skill resolves paths from registry category + directory name.

## Rules
- Read each file before modifying
- Keep all existing content, only ADD the new sections
- Make minimal, surgical changes
- Test: after your changes, a dispatch to B7 (Bug Hunter) should include B7's identity and knowledge index in the prompt

Commit: "feat: two-tier knowledge loading — inject AGENT.md + knowledge index at dispatch time"
```

---

## T4: Telemetry Pipeline Fix

**Agent:** B2 Backend Coder
**Model:** GPT 5.4
**Backend:** `codex exec --model gpt-5.4 --full-auto`
**Çalışma dizini:** `~/Projects/claude-config`

### Prompt:

```
You are B2 Backend Coder. Fix the broken telemetry pipeline.

## Problem
scripts/log_dispatch.py tries to extract agent_id from tool_input.prompt in PostToolUse hook context. But Claude Code doesn't populate tool_input.prompt — every event logs agent_id: "unknown", model_used: "unknown", duration_seconds: 0.0.

## Fix: Sidecar File Pattern

### 1. Update global/skills/dispatch/SKILL.md

Add an instruction: BEFORE calling the Agent tool, write dispatch metadata to a sidecar file:

```bash
mkdir -p /tmp/watchdog
echo '{"agent_id":"{id}","agent_name":"{name}","model":"{primary_model}","task":"{task_summary}","ts":"'$(date -Iseconds)'"}' > /tmp/watchdog/current_dispatch.json
```

This goes right before the Agent tool call in the dispatch workflow.

### 2. Update scripts/log_dispatch.py

Read the current file. Add a fallback in the agent metadata extraction:

After the existing prompt-parsing logic (which tries tool_input.prompt), add:

```python
# Fallback: read sidecar file
if agent_id == "unknown":
    sidecar_path = "/tmp/watchdog/current_dispatch.json"
    try:
        import json
        with open(sidecar_path, 'r') as f:
            sidecar = json.load(f)
            agent_id = sidecar.get("agent_id", "unknown")
            agent_name = sidecar.get("agent_name", "unknown")
            model_used = sidecar.get("model", "unknown")
    except (FileNotFoundError, json.JSONDecodeError):
        pass
```

Keep the existing parsing as primary — sidecar is fallback only.

### Rules
- Read each file fully before editing
- Minimal changes — don't refactor unrelated code
- Keep backward compatibility

Commit: "fix: telemetry sidecar fallback — resolve unknown agent_id in dispatch events"
```

---

## T5: CLAUDE.md Three-Layer Split

**Agent:** N6 AI Systems Architect
**Model:** Gemini 3.1 Pro
**Backend:** Gemini CLI
**Çalışma dizini:** `~/Projects/claude-config`

### Prompt:

```
You are N6 AI Systems Architect. Split the monolithic CLAUDE.md into three layers.

## Context
global/CLAUDE.md is 715 lines mixing behavior rules, control logic, and reference data. Research shows three-layer separation improves agent performance by +16.8 points.

## What to Do

### 1. Create global/charter.md (~150 lines)
Extract these sections from CLAUDE.md:
- Section 1: Calisma tarzi (working style, response rules)
- Section 2: Tool-first ve maliyet  
- Section 3: Model ve dil (model selection, language rules, cost tables)
- Section 6: Secrets guvenligi
- Section 7: Skill'ler

This is the "Runtime Charter" — behavioral rules that apply always.

### 2. Create global/harness.md (~150 lines)
Extract these sections:
- Dispatch-First Rule
- Section 9: Task Discipline & Watchdog (all subsections 9a-9f)
- Section 10: Session sonu — ders cikarma
- Section 11: Multi-Agent Sistemi (dispatch protocol, agent truth, routing)

This is the "Harness Logic" — structural control of how work flows.

### 3. Rewrite global/CLAUDE.md as assembler (~80 lines)
Keep ONLY:
- Line 1-5: TEMEL KURAL (dispatch-first, already prepended by T2)
- A note saying "This file assembles rules from charter.md and harness.md"
- Section 4: jCodeMunch MCP (short, tool-specific)
- Section 5: Migration sistemi (short, signal-based)
- Section 8: Proje gelistirme kurallari (project rules — keep as-is, these are specific)
- At the top after TEMEL KURAL, add: "Oku: global/charter.md ve global/harness.md — tum kurallar orada."

### 4. PRUNE during extraction:
- Remove section 8g-2 (game rules protocol) — too niche, 15 lines
- Consolidate 3 model tables into 1 (keep the main table in charter.md)
- Remove RAM calculation formulas (keep just the reference table)
- Simplify section 8h report protocol to 10 lines (move detail to a hook script)
- Remove cost emoji definitions from charter (agent-registry already has this)

### Rules
- Read global/CLAUDE.md fully first
- Create charter.md and harness.md as NEW files
- Rewrite CLAUDE.md to be the thin assembler
- Every rule that exists in current CLAUDE.md must end up in exactly one of the three files
- Do NOT lose any rule — only prune the specific items listed above
- Verify: combined content of all 3 files covers everything in original (minus pruned items)

Commit: "refactor: three-layer CLAUDE.md split — charter + harness + assembler"
```

---

## T6: Review All Changes

**Agent:** C3 AI Reviewer
**Model:** Gemini 3.1 Pro
**Backend:** Gemini CLI
**Çalışma dizini:** `~/Projects/claude-config`

### Prompt:

```
You are C3 AI Reviewer. Review all recent changes in this repo.

Run: git log --oneline -10
Run: git diff HEAD~5

## Review Checklist

1. CLAUDE.md Structure:
   - Line 1-5 has dispatch-first rule?
   - charter.md exists with behavioral rules?
   - harness.md exists with control logic?
   - No rule was lost in the split?

2. Dispatch Knowledge Injection:
   - config/agent-dispatch.md has KNOWLEDGE block?
   - global/skills/dispatch/SKILL.md reads AGENT.md + knowledge/_index.md?
   - Knowledge path is correct for all agent categories?

3. Telemetry Fix:
   - scripts/log_dispatch.py has sidecar fallback?
   - dispatch/SKILL.md writes sidecar before Agent tool?

4. N6 Knowledge:
   - orchestration-patterns.md has 2026 research?
   - context-engineering.md has Manus/NLH findings?
   - harness-engineering-claude-config.md exists with architecture details?

5. General:
   - No existing functionality broken?
   - All commits have clear messages?
   - No secrets or sensitive data committed?

## Scoring (1-10)
Score each area. Overall score must be >= 8 to pass.
If score < 8, list specific issues that must be fixed.

Output format:
{
  "overall_score": 8,
  "areas": {
    "claude_md_structure": {"score": 9, "notes": "..."},
    "knowledge_injection": {"score": 8, "notes": "..."},
    "telemetry_fix": {"score": 7, "notes": "..."},
    "n6_knowledge": {"score": 8, "notes": "..."},
    "general": {"score": 9, "notes": "..."}
  },
  "blocking_issues": [],
  "recommendations": []
}
```

---

## ÇALIŞTIRMA KILAVUZU

### Codex CLI (GPT 5.4):
```bash
cd ~/Projects/claude-config
codex exec --model gpt-5.4 --full-auto "PROMPT_BURAYA"
```

### Gemini CLI:
```bash
cd ~/Projects/claude-config
gemini "PROMPT_BURAYA"
```

### Sıra:
1. T1 çalıştır → knowledge dosyaları güncellenir
2. T2 + T3 paralel çalıştır → CLAUDE.md fix + dispatch knowledge injection
3. T4 çalıştır → telemetry fix
4. T5 çalıştır → three-layer split (T2'nin commit'i gerekli)
5. T6 çalıştır → review

### Her task sonrası kontrol:
```bash
git log --oneline -1  # commit atıldı mı
git diff HEAD~1 --stat  # hangi dosyalar değişti
```

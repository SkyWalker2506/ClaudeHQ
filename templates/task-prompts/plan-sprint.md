# HQ Task: Plan Sprint

You are planning **Sprint {{SPRINT_NUMBER}}** for **{{PROJECT_NAME}}**.

## Project Path
{{PROJECT_PATH}}

## Instructions

1. Analyze the project's current state:
   - Read the README, CLAUDE.md, and key source files
   - Check recent git history to understand what's been done
   - Look at open issues or TODOs in the code
   - Identify the tech stack and architecture

2. Design the sprint:
   - Identify 3-7 actionable tasks based on project priorities
   - Each task should be completable in a single Claude session
   - Order tasks by dependency (independent tasks first)
   - Assign realistic scope — not too big, not too small

3. Create the sprint file at `{{SPRINT_DIR}}/sprint-{{SPRINT_NUMBER}}.json`:

```json
{
  "project": "{{PROJECT_NAME}}",
  "sprint": {{SPRINT_NUMBER}},
  "goal": "<one-line sprint goal>",
  "status": "active",
  "startDate": "<today's date>",
  "endDate": "",
  "tasks": [
    {
      "id": "T1",
      "title": "<task title>",
      "status": "todo",
      "description": "<detailed description of what to implement>",
      "branch": "feature/<branch-name>",
      "assignedPrompt": "advance"
    }
  ]
}
```

4. Output a summary of the sprint plan for review.

## Task ID Convention
- Use T1, T2, T3... for sequential tasks
- Use descriptive branch names: `feature/`, `fix/`, `refactor/`

## Prompt Types
Available `assignedPrompt` values:
- `advance` — Implement the task (default)
- `review` — Code review and blocker detection
- `status-report` — Generate status report

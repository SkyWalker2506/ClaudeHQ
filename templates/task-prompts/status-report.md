# HQ Task: Status Report

Generate a status report for **{{PROJECT_NAME}}**.

## Contract
- **Required outputs:** Status JSON in progress file
- **Completion gate:** {{COMPLETION_GATE}}
- **Max tool calls:** {{MAX_TOOL_CALLS}}
- **Timeout behavior:** {{TIMEOUT_BEHAVIOR}}

## Environment
- **Project:** {{PROJECT_NAME}}
- **Path:** {{PROJECT_PATH}}
- **Branch:** {{CURRENT_BRANCH}}
- **Tech stack:** {{TECH_STACK}}
- **Recent commits:** {{RECENT_COMMITS}}
- **Test command:** {{TEST_COMMAND}}
- **Build command:** {{BUILD_COMMAND}}

## Instructions

1. Analyze the project:
   - Check git log for recent activity
   - Read README and CLAUDE.md for project context
   - Look at the current branch state
   - Run `{{BUILD_COMMAND}}` and `{{TEST_COMMAND}}` to check health

2. Generate a status report and write it to `{{PROGRESS_DIR}}/{{PROJECT_NAME}}.json`:

```json
{
  "project": "{{PROJECT_NAME}}",
  "status": "completed",
  "lastUpdate": "<ISO timestamp>",
  "report": {
    "summary": "<2-3 sentence project summary>",
    "recentActivity": "<what happened recently>",
    "health": "healthy|warning|critical",
    "openIssues": ["<list of identified issues>"],
    "nextSteps": ["<recommended next actions>"],
    "techDebt": ["<any tech debt identified>"],
    "lastCommit": "<date and message of last commit>",
    "branch": "<current branch>"
  }
}
```

3. Be honest about the project state — flag real issues, don't sugarcoat.

# HQ Task: Review & Blocker Detection

Review **{{PROJECT_NAME}}** and identify any blockers or issues.

## Contract
- **Required outputs:** Review report with quality score
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

## Sprint Context
- Sprint: {{SPRINT_NUMBER}}
- Sprint Goal: {{SPRINT_GOAL}}

## Instructions

1. Review the codebase:
   - Run `{{BUILD_COMMAND}}` — check for compilation/build errors
   - Run `{{TEST_COMMAND}}` — check test status
   - Look for obvious bugs or anti-patterns
   - Check dependency health (outdated, vulnerable)
   - Review recent changes for quality

2. Identify blockers:
   - Missing dependencies or configuration
   - Broken builds or failing tests
   - Architectural issues that prevent progress
   - Missing environment setup or credentials

3. Score the codebase (1-10) based on: build health, test coverage, code quality, dependency health, documentation

4. Write the review to `{{PROGRESS_DIR}}/{{PROJECT_NAME}}.json`:

```json
{
  "project": "{{PROJECT_NAME}}",
  "status": "completed",
  "lastUpdate": "<ISO timestamp>",
  "review": {
    "score": 8,
    "buildStatus": "passing|failing|unknown",
    "testStatus": "passing|failing|no-tests",
    "blockers": [
      {
        "severity": "critical|warning|info",
        "description": "<what's blocking>",
        "suggestion": "<how to fix>"
      }
    ],
    "codeQuality": "<brief assessment>",
    "recommendations": ["<actionable recommendations>"]
  }
}
```

5. If critical blockers are found, set the top-level status to "blocked" instead of "completed".
6. **Completion gate:** Review score must be >= 8. If score < 8, list the specific issues that must be fixed.

## Self-Monitoring Rules

- If you've called the same tool with the same arguments 3 times → stop, try a different approach
- If you've used 80% of your tool call budget → wrap up and report findings so far
- If you encounter the same error after 2 fix attempts → report as blocked, don't loop

# HQ Task: Review & Blocker Detection

Review **{{PROJECT_NAME}}** and identify any blockers or issues.

## Sprint Context
- Sprint: {{SPRINT_NUMBER}}
- Sprint Goal: {{SPRINT_GOAL}}

## Instructions

1. Review the codebase:
   - Check for compilation/build errors
   - Run existing tests if available
   - Look for obvious bugs or anti-patterns
   - Check dependency health (outdated, vulnerable)
   - Review recent changes for quality

2. Identify blockers:
   - Missing dependencies or configuration
   - Broken builds or failing tests
   - Architectural issues that prevent progress
   - Missing environment setup or credentials

3. Write the review to `{{PROGRESS_DIR}}/{{PROJECT_NAME}}.json`:

```json
{
  "project": "{{PROJECT_NAME}}",
  "status": "completed",
  "lastUpdate": "<ISO timestamp>",
  "review": {
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

4. If critical blockers are found, set the top-level status to "blocked" instead of "completed".

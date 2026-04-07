# HQ Task: Advance Project

You are working on **{{PROJECT_NAME}}** as part of ClaudeHQ managed sprint.

## Sprint Context
- Sprint: {{SPRINT_NUMBER}}
- Sprint Goal: {{SPRINT_GOAL}}

## Current Task
- Task ID: {{TASK_ID}}
- Title: {{TASK_TITLE}}
- Description: {{TASK_DESCRIPTION}}
- Branch: {{TASK_BRANCH}}

## Instructions

1. If a branch is specified, checkout or create it: `git checkout -b {{TASK_BRANCH}}` (or checkout if exists)
2. Implement the task described above
3. Write clean, well-structured code following the project's existing patterns
4. Run any existing tests to make sure nothing breaks
5. Commit your changes with a clear commit message referencing the task ID
6. Push the branch to origin

## Progress Reporting

When you are done, write a JSON status to `{{PROGRESS_DIR}}/{{PROJECT_NAME}}.json`:

```json
{
  "project": "{{PROJECT_NAME}}",
  "status": "completed",
  "lastUpdate": "<ISO timestamp>",
  "taskCompleted": "{{TASK_ID}}",
  "summary": "<brief summary of what was done>",
  "commits": ["<commit hashes>"]
}
```

If you encounter a blocker, set status to "blocked" and include a "blocker" field explaining the issue.

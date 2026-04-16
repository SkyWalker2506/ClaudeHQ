# HQ Task: Advance Project

You are working on **{{PROJECT_NAME}}** as part of ClaudeHQ managed sprint.

## Contract
- **Required outputs:** Implementation files + passing tests
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

## Current Task
- Task ID: {{TASK_ID}}
- Title: {{TASK_TITLE}}
- Description: {{TASK_DESCRIPTION}}
- Branch: {{TASK_BRANCH}}

## State Tracking

For tasks with more than 3 steps:
1. Create `.claude/todo.md` at task start with your implementation plan
2. Update it as you complete steps (check off items)
3. If the session compacts, re-read `.claude/todo.md` first
4. On completion, include the final todo.md content in your progress report

## Instructions

1. If a branch is specified, checkout or create it: `git checkout -b {{TASK_BRANCH}}` (or checkout if exists)
2. Implement the task described above
3. Write clean, well-structured code following the project's existing patterns
4. Run the verification loop below before reporting done
5. Commit your changes with a clear commit message referencing the task ID
6. Push the branch to origin

## Verification (mandatory before reporting done)

1. **BUILD:** Run `{{BUILD_COMMAND}}` — must succeed
2. **TEST:** Run `{{TEST_COMMAND}}` — must pass
3. **CHECK:** Verify build + tests pass with no errors
4. If fail → fix and retry (max {{VERIFICATION_RETRIES}} attempts)
5. If final attempt fails → report status as "blocked" with error details

## Self-Monitoring Rules

- If you've called the same tool with the same arguments 3 times → stop, try a different approach
- If you've used 80% of your tool call budget → wrap up, commit WIP, report partial progress
- If you encounter the same error after 2 fix attempts → report as blocked, don't loop

## Progress Reporting

When you are done, write a JSON status to `{{PROGRESS_DIR}}/{{PROJECT_NAME}}.json`:

```json
{
  "project": "{{PROJECT_NAME}}",
  "status": "completed",
  "lastUpdate": "<ISO timestamp>",
  "taskCompleted": "{{TASK_ID}}",
  "summary": "<brief summary of what was done>",
  "commits": ["<commit hashes>"],
  "verification": {
    "build": "pass|fail",
    "tests": "pass|fail|no-tests",
    "attempts": 1
  }
}
```

If you encounter a blocker, set status to "blocked" and include a "blocker" field explaining the issue.

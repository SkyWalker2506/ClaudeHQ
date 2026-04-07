#!/usr/bin/env bash
set -euo pipefail

# ClaudeHQ — Dispatch: Build prompts and launch Claude sessions for projects

HQ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_FILE="$HQ_DIR/projects.json"
SPRINTS_DIR="$HQ_DIR/sprints"
PROGRESS_DIR="$HQ_DIR/progress"
TEMPLATES_DIR="$HQ_DIR/templates"

get_project_info() {
    local name="$1"
    jq --arg name "$name" '.[] | select(.name == $name)' "$PROJECTS_FILE"
}

get_active_sprint() {
    local name="$1"
    local sprint_num
    sprint_num=$(jq -r --arg name "$name" '.[] | select(.name == $name) | .currentSprint // empty' "$PROJECTS_FILE" 2>/dev/null || true)

    if [[ -n "$sprint_num" && "$sprint_num" != "null" ]]; then
        local sprint_file="$SPRINTS_DIR/$name/sprint-${sprint_num}.json"
        if [[ -f "$sprint_file" ]]; then
            cat "$sprint_file"
            return 0
        fi
    fi
    echo ""
}

get_next_task() {
    local sprint_json="$1"
    if [[ -z "$sprint_json" ]]; then
        echo ""
        return
    fi
    echo "$sprint_json" | jq -r '.tasks[] | select(.status == "todo" or .status == "in-progress") | . ' | jq -s 'first // empty'
}

build_prompt() {
    local project_name="$1"
    local project_info
    project_info=$(get_project_info "$project_name")

    local project_path
    project_path=$(echo "$project_info" | jq -r '.path')

    # Get active sprint and next task
    local sprint_json
    sprint_json=$(get_active_sprint "$project_name")

    local task_json=""
    local prompt_type="advance"

    if [[ -n "$sprint_json" ]]; then
        task_json=$(get_next_task "$sprint_json")

        if [[ -n "$task_json" ]]; then
            # Use the task's assigned prompt type if specified
            local assigned
            assigned=$(echo "$task_json" | jq -r '.assignedPrompt // "advance"')
            if [[ -n "$assigned" && "$assigned" != "null" ]]; then
                prompt_type="$assigned"
            fi
        fi
    fi

    # Load template
    local template_file="$TEMPLATES_DIR/task-prompts/${prompt_type}.md"
    if [[ ! -f "$template_file" ]]; then
        template_file="$TEMPLATES_DIR/task-prompts/advance.md"
    fi

    local prompt
    prompt=$(cat "$template_file")

    # Inject variables
    local sprint_number=""
    local sprint_goal=""
    local task_title=""
    local task_description=""
    local task_branch=""
    local task_id=""

    if [[ -n "$sprint_json" ]]; then
        sprint_number=$(echo "$sprint_json" | jq -r '.sprint // ""')
        sprint_goal=$(echo "$sprint_json" | jq -r '.goal // ""')
    fi

    if [[ -n "$task_json" ]]; then
        task_id=$(echo "$task_json" | jq -r '.id // ""')
        task_title=$(echo "$task_json" | jq -r '.title // ""')
        task_description=$(echo "$task_json" | jq -r '.description // ""')
        task_branch=$(echo "$task_json" | jq -r '.branch // ""')
    fi

    prompt="${prompt//\{\{PROJECT_NAME\}\}/$project_name}"
    prompt="${prompt//\{\{PROJECT_PATH\}\}/$project_path}"
    prompt="${prompt//\{\{SPRINT_NUMBER\}\}/$sprint_number}"
    prompt="${prompt//\{\{SPRINT_GOAL\}\}/$sprint_goal}"
    prompt="${prompt//\{\{TASK_ID\}\}/$task_id}"
    prompt="${prompt//\{\{TASK_TITLE\}\}/$task_title}"
    prompt="${prompt//\{\{TASK_DESCRIPTION\}\}/$task_description}"
    prompt="${prompt//\{\{TASK_BRANCH\}\}/$task_branch}"
    prompt="${prompt//\{\{PROGRESS_DIR\}\}/$PROGRESS_DIR}"
    prompt="${prompt//\{\{HQ_DIR\}\}/$HQ_DIR}"

    echo "$prompt"
}

run_session() {
    local project_name="$1"
    local project_info
    project_info=$(get_project_info "$project_name")

    local project_path
    project_path=$(echo "$project_info" | jq -r '.path')

    local prompt
    prompt=$(build_prompt "$project_name")

    local progress_file="$PROGRESS_DIR/${project_name}.json"
    local log_file="$PROGRESS_DIR/${project_name}.log"

    mkdir -p "$PROGRESS_DIR"

    # Update progress
    jq --arg time "$(date -Iseconds)" '.status = "running" | .lastUpdate = $time' "$progress_file" > "${progress_file}.tmp" 2>/dev/null && mv "${progress_file}.tmp" "$progress_file" || true

    # Mark current task as in-progress in sprint file
    local sprint_num
    sprint_num=$(jq -r --arg name "$project_name" '.[] | select(.name == $name) | .currentSprint // empty' "$PROJECTS_FILE" 2>/dev/null || true)
    if [[ -n "$sprint_num" && "$sprint_num" != "null" ]]; then
        local sprint_file="$SPRINTS_DIR/$project_name/sprint-${sprint_num}.json"
        if [[ -f "$sprint_file" ]]; then
            local task_id
            task_id=$(jq -r '[.tasks[] | select(.status == "todo")] | first | .id // empty' "$sprint_file" 2>/dev/null || true)
            if [[ -n "$task_id" ]]; then
                jq --arg id "$task_id" '(.tasks[] | select(.id == $id) | .status) = "in-progress"' "$sprint_file" > "${sprint_file}.tmp" && mv "${sprint_file}.tmp" "$sprint_file"
            fi
        fi
    fi

    # Launch Claude
    cd "$project_path"
    claude -p \
        --model sonnet \
        --name "hq-${project_name}" \
        --append-system-prompt "$prompt" \
        "Continue working on this project according to the sprint plan and current task." \
        > "$log_file" 2>&1

    local exit_code=$?

    # Update progress on completion
    local final_status="completed"
    if [[ $exit_code -ne 0 ]]; then
        final_status="failed"
    fi

    jq --arg status "$final_status" --arg time "$(date -Iseconds)" --argjson exit "$exit_code" \
        '.status = $status | .lastUpdate = $time | .exitCode = $exit' \
        "$progress_file" > "${progress_file}.tmp" && mv "${progress_file}.tmp" "$progress_file"
}

# --- MAIN ---
case "${1:-}" in
    build-prompt)
        build_prompt "${2:?Project name required}"
        ;;
    run)
        run_session "${2:?Project name required}"
        ;;
    *)
        echo "Usage: dispatch.sh <build-prompt|run> <project-name>"
        exit 1
        ;;
esac

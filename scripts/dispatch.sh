#!/usr/bin/env bash
set -euo pipefail

# ClaudeHQ — Dispatch: Build prompts and launch Claude sessions for projects
# Enhanced with: context assembly, execution contracts, environment injection

HQ_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECTS_FILE="$HQ_DIR/projects.json"
SPRINTS_DIR="$HQ_DIR/sprints"
PROGRESS_DIR="$HQ_DIR/progress"
TEMPLATES_DIR="$HQ_DIR/templates"
CONTRACT_DEFAULTS="$TEMPLATES_DIR/contract-defaults.json"

get_project_info() {
    local name="$1"
    jq --arg name "$name" '.projects[$name] // empty' "$PROJECTS_FILE"
}

get_active_sprint() {
    local name="$1"
    local sprint_num
    sprint_num=$(jq -r --arg name "$name" '.projects[$name].currentSprint // empty' "$PROJECTS_FILE" 2>/dev/null || true)

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

# --- Context Assembly Helpers ---

detect_tech_stack() {
    local path="$1"
    local stacks=()

    [[ -f "$path/pubspec.yaml" ]] && stacks+=("Flutter/Dart")
    [[ -f "$path/package.json" ]] && stacks+=("Node.js")
    [[ -f "$path/tsconfig.json" ]] && stacks+=("TypeScript")
    [[ -f "$path/Cargo.toml" ]] && stacks+=("Rust")
    [[ -f "$path/requirements.txt" || -f "$path/pyproject.toml" ]] && stacks+=("Python")
    [[ -f "$path/go.mod" ]] && stacks+=("Go")
    [[ -d "$path/Assets" && -d "$path/ProjectSettings" ]] && stacks+=("Unity/C#")
    [[ -f "$path/Gemfile" ]] && stacks+=("Ruby")
    [[ -f "$path/pom.xml" || -f "$path/build.gradle" ]] && stacks+=("Java/Kotlin")

    if [[ ${#stacks[@]} -gt 0 ]]; then
        printf '%s' "${stacks[*]}"
    else
        echo "unknown"
    fi
}

detect_test_command() {
    local path="$1"

    [[ -f "$path/pubspec.yaml" ]] && echo "flutter test" && return
    if [[ -f "$path/package.json" ]]; then
        if jq -e '.scripts.test' "$path/package.json" >/dev/null 2>&1; then
            echo "npm test"
        else
            echo "no test script configured"
        fi
        return
    fi
    [[ -f "$path/Cargo.toml" ]] && echo "cargo test" && return
    [[ -f "$path/pyproject.toml" ]] && echo "pytest" && return
    [[ -f "$path/requirements.txt" ]] && echo "pytest" && return
    [[ -f "$path/go.mod" ]] && echo "go test ./..." && return

    echo "no test command detected"
}

detect_build_command() {
    local path="$1"

    [[ -f "$path/pubspec.yaml" ]] && echo "flutter build" && return
    if [[ -f "$path/package.json" ]]; then
        if jq -e '.scripts.build' "$path/package.json" >/dev/null 2>&1; then
            echo "npm run build"
        else
            echo "no build script configured"
        fi
        return
    fi
    [[ -f "$path/Cargo.toml" ]] && echo "cargo build" && return
    [[ -f "$path/pyproject.toml" ]] && echo "python -m build" && return
    [[ -f "$path/go.mod" ]] && echo "go build ./..." && return

    echo "no build command detected"
}

get_contract_value() {
    local prompt_type="$1"
    local field="$2"
    local default="$3"

    if [[ -f "$CONTRACT_DEFAULTS" ]]; then
        local val
        val=$(jq -r --arg pt "$prompt_type" --arg f "$field" '.[$pt][$f] // empty' "$CONTRACT_DEFAULTS" 2>/dev/null || true)
        if [[ -n "$val" && "$val" != "null" ]]; then
            echo "$val"
            return
        fi
    fi
    echo "$default"
}

build_prompt() {
    local project_name="$1"
    local project_info
    project_info=$(get_project_info "$project_name")

    local project_path
    project_path=$(echo "$project_info" | jq -r '.path // empty')
    # Expand ~ to home dir
    project_path="${project_path/#\~/$HOME}"

    # Get active sprint and next task
    local sprint_json
    sprint_json=$(get_active_sprint "$project_name")

    local task_json=""
    local prompt_type="advance"

    if [[ -n "$sprint_json" ]]; then
        task_json=$(get_next_task "$sprint_json")

        if [[ -n "$task_json" ]]; then
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

    # --- Sprint & Task variables ---
    local sprint_number="" sprint_goal=""
    local task_title="" task_description="" task_branch="" task_id=""

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

    # --- Context Assembly: Environment ---
    local current_branch="unknown"
    local recent_commits="none"
    local tech_stack="unknown"
    local test_command="no test command detected"
    local build_command="no build command detected"

    if [[ -d "$project_path" ]]; then
        current_branch=$(cd "$project_path" && git branch --show-current 2>/dev/null || echo "unknown")
        recent_commits=$(cd "$project_path" && git log --oneline -3 2>/dev/null || echo "none")
        tech_stack=$(detect_tech_stack "$project_path")
        test_command=$(detect_test_command "$project_path")
        build_command=$(detect_build_command "$project_path")
    fi

    # --- Contract values ---
    local completion_gate max_tool_calls timeout_behavior verification_retries
    completion_gate=$(get_contract_value "$prompt_type" "completion_gate" "Task completed successfully")
    max_tool_calls=$(get_contract_value "$prompt_type" "max_tool_calls" "50")
    timeout_behavior=$(get_contract_value "$prompt_type" "timeout_behavior" "commit WIP and report")
    verification_retries=$(get_contract_value "$prompt_type" "verification_retries" "3")

    # --- Inject all variables ---
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
    prompt="${prompt//\{\{SPRINT_DIR\}\}/$SPRINTS_DIR/$project_name}"

    # Environment variables
    prompt="${prompt//\{\{CURRENT_BRANCH\}\}/$current_branch}"
    prompt="${prompt//\{\{RECENT_COMMITS\}\}/$recent_commits}"
    prompt="${prompt//\{\{TECH_STACK\}\}/$tech_stack}"
    prompt="${prompt//\{\{TEST_COMMAND\}\}/$test_command}"
    prompt="${prompt//\{\{BUILD_COMMAND\}\}/$build_command}"

    # Contract variables
    prompt="${prompt//\{\{COMPLETION_GATE\}\}/$completion_gate}"
    prompt="${prompt//\{\{MAX_TOOL_CALLS\}\}/$max_tool_calls}"
    prompt="${prompt//\{\{TIMEOUT_BEHAVIOR\}\}/$timeout_behavior}"
    prompt="${prompt//\{\{VERIFICATION_RETRIES\}\}/$verification_retries}"

    echo "$prompt"
}

run_session() {
    local project_name="$1"
    local project_info
    project_info=$(get_project_info "$project_name")

    local project_path
    project_path=$(echo "$project_info" | jq -r '.path // empty')
    project_path="${project_path/#\~/$HOME}"

    local prompt
    prompt=$(build_prompt "$project_name")

    local progress_file="$PROGRESS_DIR/${project_name}.json"
    local log_file="$PROGRESS_DIR/${project_name}.log"

    mkdir -p "$PROGRESS_DIR"

    # Update progress
    if [[ -f "$progress_file" ]]; then
        jq --arg time "$(date -Iseconds)" '.status = "running" | .lastUpdate = $time' "$progress_file" > "${progress_file}.tmp" 2>/dev/null && mv "${progress_file}.tmp" "$progress_file" || true
    fi

    # Mark current task as in-progress in sprint file
    local sprint_num
    sprint_num=$(jq -r --arg name "$project_name" '.projects[$name].currentSprint // empty' "$PROJECTS_FILE" 2>/dev/null || true)
    if [[ -n "$sprint_num" && "$sprint_num" != "null" ]]; then
        local sprint_file="$SPRINTS_DIR/$project_name/sprint-${sprint_num}.json"
        if [[ -f "$sprint_file" ]]; then
            local in_task_id
            in_task_id=$(jq -r '[.tasks[] | select(.status == "todo")] | first | .id // empty' "$sprint_file" 2>/dev/null || true)
            if [[ -n "$in_task_id" ]]; then
                jq --arg id "$in_task_id" '(.tasks[] | select(.id == $id) | .status) = "in-progress"' "$sprint_file" > "${sprint_file}.tmp" && mv "${sprint_file}.tmp" "$sprint_file"
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

    if [[ -f "$progress_file" ]]; then
        jq --arg status "$final_status" --arg time "$(date -Iseconds)" --argjson exit "$exit_code" \
            '.status = $status | .lastUpdate = $time | .exitCode = $exit' \
            "$progress_file" > "${progress_file}.tmp" && mv "${progress_file}.tmp" "$progress_file"
    else
        echo "{\"project\":\"$project_name\",\"status\":\"$final_status\",\"lastUpdate\":\"$(date -Iseconds)\",\"exitCode\":$exit_code}" > "$progress_file"
    fi
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

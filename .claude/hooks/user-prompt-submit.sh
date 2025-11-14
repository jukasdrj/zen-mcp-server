#!/bin/bash
# Claude Code User-Prompt-Submit Hook
# Receives JSON via stdin when user submits a prompt
# JSON structure: {"session_id": "...", "cwd": "...", "transcript_path": "...", ...}

set -euo pipefail

# Read JSON from stdin
INPUT=$(cat)

# Parse session information
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')
CWD=$(echo "$INPUT" | jq -r '.cwd // "unknown"')

# Log hook execution
LOG_DIR="/Users/justingardner/Downloads/xcode/zen-mcp-server/.claude/hooks"
mkdir -p "$LOG_DIR"
echo "[$(date)] UserPromptSubmit: session=$SESSION_ID, cwd=$CWD" >> "$LOG_DIR/hook.log"

# Check if we're in a git repository with uncommitted changes
if [[ -d "$CWD/.git" ]]; then
  cd "$CWD"

  # Check for uncommitted changes
  if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    CHANGED_FILES=$(git diff --name-only | wc -l | tr -d ' ')
    if [[ "$CHANGED_FILES" -gt 10 ]]; then
      echo "ℹ️  Note: You have $CHANGED_FILES uncommitted files. Consider committing your work."
    fi
  fi
fi

# Always allow prompt submission
exit 0

#!/bin/bash
# Claude Code Pre-Tool-Use Hook
# Receives JSON via stdin containing tool information
# JSON structure: {"session_id": "...", "tool_name": "...", "tool_input": {...}, ...}

set -euo pipefail

# Read JSON from stdin
INPUT=$(cat)

# Parse tool information
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // "{}"')

# Log hook execution (for debugging)
# Use git root to make paths portable
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)")
LOG_DIR="$REPO_ROOT/.claude/hooks"
mkdir -p "$LOG_DIR"
echo "[$(date)] PreToolUse: $TOOL_NAME" >> "$LOG_DIR/hook.log"

# Hook logic based on tool name
case "$TOOL_NAME" in
  "Write"|"Edit"|"mcp__filesystem-with-morph__write_file"|"mcp__filesystem-with-morph__edit_file")
    # Check if writing/editing Python files
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // .path // ""')

    if [[ "$FILE_PATH" == *.py ]]; then
      echo "[$(date)] Python file operation: $FILE_PATH" >> "$LOG_DIR/hook.log"

      # Check for sensitive patterns
      CONTENT=$(echo "$TOOL_INPUT" | jq -r '.content // .code_edit // ""')

      if echo "$CONTENT" | grep -qE "(API_KEY|PASSWORD|SECRET)" && ! echo "$FILE_PATH" | grep -q "test"; then
        echo "⚠️  Warning: Detected potential sensitive data in $FILE_PATH"
        echo "[$(date)] WARNING: Sensitive data pattern in $FILE_PATH" >> "$LOG_DIR/hook.log"
      fi
    fi

    # Check for .env files
    if [[ "$FILE_PATH" == *.env* ]] || [[ "$FILE_PATH" == *credentials* ]]; then
      echo "❌ Blocked: Attempting to write sensitive file: $FILE_PATH"
      echo "[$(date)] BLOCKED: Sensitive file $FILE_PATH" >> "$LOG_DIR/hook.log"

      # Return blocking response
      echo '{"blocked": true, "message": "Writing sensitive files (.env, credentials) is not allowed"}'
      exit 2
    fi
    ;;

  "Bash")
    # Check for dangerous bash commands
    COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // ""')

    if echo "$COMMAND" | grep -qE "rm -rf /|dd if=|mkfs|:(){ :|:&};:"; then
      echo "❌ Blocked: Dangerous command detected"
      echo "[$(date)] BLOCKED: Dangerous bash command" >> "$LOG_DIR/hook.log"

      echo '{"blocked": true, "message": "Dangerous command blocked by pre-tool-use hook"}'
      exit 2
    fi
    ;;
esac

# Allow by default
exit 0

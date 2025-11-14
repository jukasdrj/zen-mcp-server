#!/bin/bash
# Claude Code Post-Tool-Use Hook
# Receives JSON via stdin containing tool information and response
# JSON structure: {"session_id": "...", "tool_name": "...", "tool_input": {...}, "tool_response": {...}, ...}

set -euo pipefail

# Read JSON from stdin
INPUT=$(cat)

# Parse tool information
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // "{}"')
TOOL_RESPONSE=$(echo "$INPUT" | jq -r '.tool_response // "{}"')

# Log hook execution
LOG_DIR="/Users/justingardner/Downloads/xcode/zen-mcp-server/.claude/hooks"
mkdir -p "$LOG_DIR"
echo "[$(date)] PostToolUse: $TOOL_NAME" >> "$LOG_DIR/hook.log"

# Hook logic based on tool name
case "$TOOL_NAME" in
  "Write"|"Edit"|"mcp__filesystem-with-morph__write_file"|"mcp__filesystem-with-morph__edit_file")
    FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.file_path // .path // ""')

    # If a Python file was written, optionally run quick validation
    if [[ "$FILE_PATH" == *.py ]] && [[ -f "$FILE_PATH" ]]; then
      echo "[$(date)] Validating Python file: $FILE_PATH" >> "$LOG_DIR/hook.log"

      # Quick Python syntax check
      if ! python3 -m py_compile "$FILE_PATH" 2>/dev/null; then
        echo "⚠️  Warning: Python syntax error in $FILE_PATH"
        echo "[$(date)] WARNING: Syntax error in $FILE_PATH" >> "$LOG_DIR/hook.log"
      fi
    fi
    ;;

  "Bash")
    # Log bash commands that were executed
    COMMAND=$(echo "$TOOL_INPUT" | jq -r '.command // ""')
    echo "[$(date)] Bash executed: $COMMAND" >> "$LOG_DIR/hook.log"
    ;;
esac

# Always allow post-tool hooks to complete
exit 0

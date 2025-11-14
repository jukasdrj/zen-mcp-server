#!/bin/bash

# MCP Server Pre-Commit Hook
# Based on backend template, customized for MCP development

set -e

echo "🤖 Running MCP pre-commit checks..."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

FAILED=0

# 1. Check for sensitive files
echo "🔐 Checking for sensitive files..."
SENSITIVE_FILES=(
  "*.env"
  "*.key"
  "*.pem"
  "*credentials*.json"
  "*secrets*.json"
)

for pattern in "${SENSITIVE_FILES[@]}"; do
  if git diff --cached --name-only | grep -q "$pattern"; then
    echo -e "${RED}✗ Blocked: Attempting to commit sensitive file: $pattern${NC}"
    FAILED=1
  fi
done

if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✓ No sensitive files detected${NC}"
fi

# 2. TypeScript type checking (if available)
if command -v npm &> /dev/null && [ -f "package.json" ]; then
  echo "🔍 Running TypeScript type check..."
  if npm run typecheck --if-present 2>&1 | grep -q "error"; then
    echo -e "${RED}✗ TypeScript errors found${NC}"
    FAILED=1
  else
    echo -e "${GREEN}✓ TypeScript type check passed${NC}"
  fi
fi

# 3. ESLint (if available)
if command -v npm &> /dev/null && [ -f ".eslintrc.json" ] || [ -f ".eslintrc.js" ]; then
  echo "🎨 Running ESLint..."
  STAGED_TS=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|js)$' || true)

  if [ -n "$STAGED_TS" ]; then
    if ! npm run lint --if-present -- $STAGED_TS 2>&1; then
      echo -e "${YELLOW}⚠ Warning: ESLint found issues${NC}"
      echo "  Run: npm run lint:fix"
    else
      echo -e "${GREEN}✓ ESLint passed${NC}"
    fi
  fi
fi

# 4. Check for console.log statements
echo "🐛 Checking for debug statements..."
DEBUG_COUNT=$(git diff --cached | grep -c "console.log(" || true)

if [ $DEBUG_COUNT -gt 0 ]; then
  echo -e "${YELLOW}⚠ Warning: Found $DEBUG_COUNT console.log() statements${NC}"
  echo "  Consider using proper logging"
fi

# 5. Check package.json changes
if git diff --cached --name-only | grep -q "package.json"; then
  echo "📦 Checking package.json..."

  if git diff --cached package.json | grep -q "<<<<<<"; then
    echo -e "${RED}✗ Merge conflicts in package.json${NC}"
    FAILED=1
  else
    echo -e "${GREEN}✓ package.json looks clean${NC}"
  fi
fi

# 6. MCP Schema validation (if tools exist)
if git diff --cached --name-only | grep -qE "src/tools/|src/resources/"; then
  echo "🔧 Checking MCP schema changes..."
  echo -e "${YELLOW}⚠ MCP tools/resources changed${NC}"
  echo "  Ensure schemas are valid and follow MCP spec"
fi

# Final result
echo ""
if [ $FAILED -eq 1 ]; then
  echo -e "${RED}❌ Pre-commit checks failed. Commit blocked.${NC}"
  exit 1
else
  echo -e "${GREEN}✅ All pre-commit checks passed!${NC}"
  exit 0
fi

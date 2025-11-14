# Code Review Prompt Template

**Purpose:** Systematic code review checklist for AI assistants.

---

## 📋 Pre-Review Checklist

Before reviewing code:
- [ ] Understand the feature/fix being implemented
- [ ] Read related documentation (CLAUDE.md, .robit/patterns.md)
- [ ] Check for existing tests
- [ ] Review recent git history for context

---

## 🔍 Review Categories

### 1. Code Quality

**Check for:**
- [ ] Type hints on all functions (Python 3.9+)
- [ ] Pydantic models for tool requests (not plain dicts)
- [ ] Docstrings for public functions
- [ ] Descriptive variable names
- [ ] No commented-out code
- [ ] No debug print statements (use logger)

**Questions:**
- Is the code self-documenting?
- Can a new developer understand this in 6 months?
- Are abstractions appropriate (not over/under-engineered)?

---

### 2. Python Patterns

**Check for:**
- [ ] F-strings for formatting (not % or .format())
- [ ] Explicit None checks (not truthiness)
- [ ] Specific exception handling (not bare except:)
- [ ] Async/await for I/O operations
- [ ] Type hints from `typing` module

**Anti-patterns to avoid:**
- ❌ Subprocess for MCP tools (loses conversation memory)
- ❌ Hardcoded API keys
- ❌ Synchronous provider calls
- ❌ Plain dict requests (no validation)
- ❌ Manual model-to-provider mapping

---

### 3. MCP Protocol Compliance

**Check for:**
- [ ] Tool names lowercase, hyphen-separated
- [ ] Pydantic request validation
- [ ] UUID validation for continuation_id
- [ ] Proper tool registration in server.py

**MCP Rules:**
- Conversation memory only works with persistent processes
- continuation_id must be valid UUID format
- File paths must be absolute
- Model resolution via registry (not hardcoded)

---

### 4. Architecture Alignment

**Check for:**
- [ ] Follows Simple or Workflow tool pattern
- [ ] Uses ModelProviderRegistry for model routing
- [ ] Conversation memory via utils/conversation_memory.py
- [ ] Provider inherits from ModelProvider base class

**Workflow Tools:**
- [ ] Step tracking (step_number, total_steps, next_step_required)
- [ ] Confidence levels progress logically
- [ ] File embedding strategy (step 1 = refs, later = full content)

---

### 5. Security

**Check for:**
- [ ] No hardcoded secrets (use environment variables)
- [ ] UUID validation before using continuation_id
- [ ] File path validation (absolute, exists, no traversal)
- [ ] Input sanitization (Pydantic handles most)

**Security Rules:**
- NEVER hardcode API keys
- ALWAYS validate UUID format
- CHECK file paths before reading
- SANITIZE user input via Pydantic

---

### 6. Performance

**Check for:**
- [ ] Async I/O for all network calls
- [ ] File deduplication in conversation memory
- [ ] Token budget management (refs vs full content)
- [ ] Connection pooling for providers

**Optimization Opportunities:**
- Use VCR cassettes for tests (fast, free)
- Load files conditionally (step 1 = refs only)
- Deduplicate files (newest-first priority)
- Reuse HTTP sessions (aiohttp.ClientSession)

---

### 7. Testing

**Check for:**
- [ ] Unit tests with VCR cassettes
- [ ] Simulator tests for cross-tool workflows
- [ ] Integration tests marked with @pytest.mark.integration
- [ ] Test coverage for new code

**Testing Rules:**
- Unit: pytest with VCR for API mocking
- Simulator: End-to-end conversation flows
- Integration: Real APIs with approved models (Gemini/Grok)

---

## 🎯 Review Process

### Step 1: Initial Scan (5 min)
- Read changed files
- Understand intent
- Check for obvious issues

### Step 2: Deep Review (15 min)
- Verify patterns compliance
- Check architecture alignment
- Look for security issues
- Assess performance

### Step 3: Testing Review (5 min)
- Verify tests exist
- Check test coverage
- Validate test quality

### Step 4: Documentation (3 min)
- Check if .robit/ needs updates
- Verify CLAUDE.md is current
- Confirm docstrings are clear

---

## ✅ Sign-Off Checklist

Before approving:
- [ ] All review categories checked
- [ ] No critical or high severity issues
- [ ] Tests pass (./code_quality_checks.sh)
- [ ] Documentation updated if needed
- [ ] No TODOs or FIXMEs without issues filed

**Approval Criteria:**
- Zero warnings from Ruff/Black/isort
- All tests pass (unit + simulator)
- Follows .robit/patterns.md
- Aligns with .robit/architecture.md

---

## 💬 Feedback Template

**Severity Levels:**
- 🔴 **Critical** - Blocks PR, must fix (security, crashes)
- 🟡 **High** - Blocks PR, should fix (bugs, anti-patterns)
- 🟢 **Medium** - Suggest fix, not blocking (style, optimization)
- ⚪ **Low** - Nice to have (nitpicks, suggestions)

**Feedback Format:**
```
🟡 HIGH: patterns.md:50 - Using subprocess for MCP tools
  Issue: This loses conversation memory (see patterns.md:26)
  Fix: Use persistent server process instead
  
🟢 MEDIUM: chat.py:142 - No type hint on return value
  Issue: Return type unclear
  Fix: Add -> dict[str, Any]
```

---

## 📚 References

- Patterns: `.robit/patterns.md`
- Architecture: `.robit/architecture.md`
- Context: `.robit/context.md`
- CLAUDE.md: Root directory
- Tests: `tests/`, `simulator_tests/`

---

**Use this checklist for every code review to ensure consistency and quality.**

# Systematic Debugging Guide

**Purpose:** Step-by-step debugging approach for Zen MCP Server issues.

---

## 🎯 Debugging Philosophy

1. **Reproduce First** - Consistent reproduction is 50% of the solution
2. **Hypothesis-Driven** - Form theories, test systematically
3. **Bisect the Problem** - Binary search to isolate root cause
4. **Document Findings** - Keep notes, track what you've tried
5. **Fix Root Cause** - Not just symptoms

---

## 🔍 Initial Triage

### Step 1: Gather Information

**Questions to Answer:**
- When did it start failing?
- What changed recently? (code, config, dependencies)
- Does it happen consistently or intermittently?
- What's the exact error message?
- Which tool/provider is affected?

**Data to Collect:**
```bash
# Check logs
tail -n 500 logs/mcp_server.log
tail -n 100 logs/mcp_activity.log

# Check git history
git log --oneline -10

# Check environment
env | grep -E "(GEMINI|OPENAI|XAI|CUSTOM)_API"

# Check Python version
python --version
```

---

### Step 2: Reproduce the Issue

**Create Minimal Reproduction:**
1. Simplify the request to bare minimum
2. Remove optional parameters
3. Test with different models
4. Test with different tools

**Example:**
```python
# Start complex
chat with gemini-2.5-pro using files foo.py, bar.py about refactoring

# Simplify to minimal
chat with gemini-2.5-pro: "Hello"

# If minimal works, add back complexity incrementally
```

---

## 🐛 Common Issue Patterns

### Pattern 1: Conversation Memory Not Working

**Symptoms:**
- Tools don't remember previous conversation
- File context lost between tool calls
- continuation_id doesn't work

**Root Causes:**
1. Subprocess invocations (each starts fresh)
2. Server restarted between calls
3. Invalid UUID format
4. Thread expired (3-hour TTL)

**Debug Steps:**
```python
# Check if using persistent process
# Look for subprocess.run() calls in code

# Validate UUID format
import uuid
try:
    uuid.UUID(continuation_id)
except ValueError:
    print("Invalid UUID!")

# Check thread exists
from utils.conversation_memory import get_thread
thread = get_thread(continuation_id)
print(f"Thread found: {thread is not None}")
```

**Fix:**
- Use persistent MCP server (Claude Desktop)
- Validate UUIDs before use
- Check thread hasn't expired

---

### Pattern 2: Provider Not Found / Model Unavailable

**Symptoms:**
- "Model not found" error
- "Provider unavailable"
- Model doesn't appear in list

**Root Causes:**
1. API key not set
2. Model not in conf/*.json
3. Provider not registered
4. Typo in model name

**Debug Steps:**
```bash
# Check API keys
env | grep API_KEY

# Check model config
cat conf/gemini_models.json | grep "model_name"

# Check provider registration
grep "register_provider" server.py

# Test model directly
python
>>> from providers.registry import ModelProviderRegistry
>>> registry = ModelProviderRegistry()
>>> print(registry.get_available_model_names())
```

**Fix:**
- Set API keys in .env
- Add model to conf/*.json
- Register provider in server.py
- Check spelling/aliases

---

### Pattern 3: Async/Await Errors

**Symptoms:**
- "coroutine was never awaited"
- "Task was destroyed but it is pending"
- Timeout errors

**Root Causes:**
1. Missing `await` keyword
2. Mixing sync/async code
3. Not using async context manager

**Debug Steps:**
```python
# ❌ WRONG: Missing await
response = provider.generate(request)

# ✅ CORRECT: Awaiting coroutine
response = await provider.generate(request)

# ❌ WRONG: Sync in async function
def execute(self, request):
    response = await provider.generate(request)

# ✅ CORRECT: Async all the way
async def execute(self, request):
    response = await provider.generate(request)
```

**Fix:**
- Add `await` to all async calls
- Make functions async if they call async code
- Use async context managers (`async with`)

---

### Pattern 4: Pydantic Validation Errors

**Symptoms:**
- "Field required"
- "Validation error"
- Type mismatch errors

**Root Causes:**
1. Missing required field
2. Wrong field type
3. Invalid enum value
4. Failed custom validator

**Debug Steps:**
```python
# Check request model
class ChatRequest(ToolRequest):
    prompt: str = Field(..., description="Required!")
    model: str = Field(..., description="Required!")

# Test validation
try:
    request = ChatRequest(prompt="Hi")  # Missing 'model'
except ValidationError as e:
    print(e.errors())
```

**Fix:**
- Provide all required fields
- Match field types exactly
- Use valid enum values
- Fix custom validator logic

---

### Pattern 5: File Not Found / Path Issues

**Symptoms:**
- "File not found"
- "Permission denied"
- "Invalid path"

**Root Causes:**
1. Relative path used (need absolute)
2. File doesn't exist
3. Wrong permissions
4. Typo in path

**Debug Steps:**
```python
import os
from pathlib import Path

# Check if path is absolute
path = "/path/to/file.py"
print(f"Absolute: {os.path.isabs(path)}")

# Check if file exists
print(f"Exists: {Path(path).exists()}")

# Check permissions
print(f"Readable: {os.access(path, os.R_OK)}")
```

**Fix:**
- Use absolute paths only
- Verify file exists before reading
- Check file permissions
- Validate path format

---

## 🔬 Advanced Debugging

### Using Python Debugger

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or use breakpoint() in Python 3.7+
breakpoint()

# Commands:
# n - next line
# s - step into
# c - continue
# p variable - print variable
# l - list code around current line
```

### Logging Strategy

```python
import logging

logger = logging.getLogger(__name__)

# Add debug logs
logger.debug(f"Request: {request}")
logger.debug(f"Provider: {provider}")
logger.debug(f"Response: {response}")

# Check logs
tail -f logs/mcp_server.log | grep DEBUG
```

### Testing Hypothesis

```python
# Hypothesis: File deduplication bug
# Test: Check if newest file takes precedence

files_turn_1 = ["/path/foo.py", "/path/bar.py"]
files_turn_2 = ["/path/foo.py", "/path/baz.py"]

# Expected: baz.py, foo.py (from turn 2), bar.py (from turn 1)
# Actual: ?

# Add logging to verify
logger.debug(f"Deduplicated files: {deduplicated_files}")
```

---

## 📊 Debug Workflow

### 1. Reproduce (10 min)
- Create minimal reproduction
- Document exact steps
- Verify happens consistently

### 2. Hypothesize (5 min)
- What could cause this?
- What changed recently?
- Similar issues before?

### 3. Test Hypothesis (15 min)
- Add logging
- Use debugger
- Test edge cases

### 4. Fix Root Cause (30 min)
- Implement fix
- Add test to prevent regression
- Update documentation if needed

### 5. Verify (5 min)
- Run tests
- Check logs
- Test manually

---

## ✅ Debugging Checklist

- [ ] Issue reproduced consistently
- [ ] Hypothesis formed and tested
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Tests added
- [ ] Documentation updated
- [ ] Verified fix works

---

## 🚨 When to Ask for Help

**Ask for help if:**
- Can't reproduce issue after 30 min
- Hypothesis tested but doesn't explain symptoms
- Fix causes other issues
- Issue involves multiple components

**Before asking:**
- Document what you've tried
- Provide minimal reproduction
- Include relevant logs
- Show your hypothesis

---

## 📚 References

- Logs: `logs/mcp_server.log`, `logs/mcp_activity.log`
- Patterns: `.robit/patterns.md`
- Architecture: `.robit/architecture.md`
- Tests: `tests/`, `simulator_tests/`

---

**Remember: Debugging is detective work. Follow the evidence, test hypotheses systematically.**

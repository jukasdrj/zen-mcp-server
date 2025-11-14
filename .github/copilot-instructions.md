# GitHub Copilot Instructions for Zen MCP Server

**Version:** 9.1.3
**Python:** 3.9+ | **Last Updated:** November 2025

---

## 🎯 Project Overview

Zen MCP Server is a Model Context Protocol server connecting AI CLI tools to multiple AI providers (Gemini, X.AI Grok, OpenRouter, etc.) for enhanced code analysis, debugging, and collaborative development.

**Tech Stack:**
- Python 3.9+ with async/await
- Pydantic v2 for validation
- MCP SDK for protocol implementation
- pytest with VCR cassettes for testing

---

## 🚨 Critical Rules (NEVER VIOLATE)

### 1. Always Use Type Hints
```python
# ✅ CORRECT
def get_provider(self, model_name: str) -> Optional[ModelProvider]:
    return self.providers.get(model_name)

# ❌ WRONG
def get_provider(self, model_name):
    return self.providers.get(model_name)
```

### 2. Pydantic Models for Requests
```python
# ✅ CORRECT
class ChatRequest(ToolRequest):
    prompt: str = Field(..., description="User prompt")
    model: str = Field(..., description="Model to use")

# ❌ WRONG
def execute(self, request: dict):
    prompt = request.get("prompt")
```

### 3. Async/Await for I/O
```python
# ✅ CORRECT
async def generate(self, request: dict) -> ModelResponse:
    async with self.session.post(url, json=request) as response:
        return await response.json()

# ❌ WRONG
def generate(self, request: dict) -> dict:
    return requests.post(url, json=request).json()
```

### 4. Use Provider Registry
```python
# ✅ CORRECT
provider = self.registry.get_provider_for_model(model_name)

# ❌ WRONG
if model_name.startswith("gemini"):
    provider = GeminiProvider()
```

---

## 📁 Project Structure

```
zen-mcp-server/
├── tools/              # 15 specialized AI tools
│   ├── simple/         # Single-shot tools (chat, challenge)
│   ├── workflow/       # Multi-step tools (debug, codereview)
│   └── shared/         # Shared utilities
├── providers/          # AI provider integrations (7 providers)
│   ├── base.py        # Abstract provider interface
│   ├── gemini.py      # Google Gemini
│   ├── xai.py         # X.AI (Grok)
│   └── registry.py    # Provider routing
├── utils/              # Utilities
│   └── conversation_memory.py  # Cross-tool memory
├── systemprompts/      # System prompts per tool
├── conf/               # Model configs (JSON)
└── tests/              # Unit tests with VCR cassettes
```

---

## 🎨 Code Patterns

### Imports (use isort ordering)
```python
# 1. Standard library
import logging
from typing import Optional

# 2. Third-party
from pydantic import Field

# 3. Local
from tools.simple.base import SimpleTool
```

### String Formatting (f-strings only)
```python
# ✅ CORRECT
message = f"Model {model_name} returned {token_count} tokens"

# ❌ WRONG
message = "Model %s returned %d tokens" % (model_name, token_count)
```

### Error Handling (specific exceptions)
```python
# ✅ CORRECT
try:
    response = await provider.generate(request)
except ValueError as e:
    logger.error(f"Invalid request: {e}")
except asyncio.TimeoutError:
    logger.error("Request timed out")

# ❌ WRONG
try:
    response = await provider.generate(request)
except:
    return {"error": "Failed"}
```

---

## 🔧 Tool Development

### Simple Tool Template
```python
from tools.simple.base import SimpleTool
from tools.shared.base_models import ToolRequest

class MyToolRequest(ToolRequest):
    prompt: str = Field(..., description="User prompt")
    model: str = Field(..., description="Model to use")

class MyTool(SimpleTool):
    def get_name(self) -> str:
        return "mytool"
    
    def get_description(self) -> str:
        return "Brief description for AI assistants"
    
    async def execute_impl(self, request: MyToolRequest) -> dict:
        response = await self.call_model(request.prompt, request.model)
        return {"success": True, "response": response}
```

### Workflow Tool Template
```python
from tools.workflow.base import WorkflowTool
from tools.shared.base_models import WorkflowRequest

class MyWorkflowRequest(WorkflowRequest):
    step: str = Field(...)
    step_number: int = Field(..., ge=1)
    total_steps: int = Field(..., ge=1)
    next_step_required: bool = Field(...)
    findings: str = Field(...)
    model: str = Field(...)

class MyWorkflow(WorkflowTool):
    async def execute_impl(self, request: MyWorkflowRequest) -> dict:
        if request.step_number == 1:
            return self._plan_investigation(request)
        elif request.next_step_required:
            return self._continue_investigation(request)
        else:
            return self._complete_investigation(request)
```

---

## 🧪 Testing

### Unit Test with VCR
```python
import pytest
from tools.chat import ChatTool, ChatRequest

@pytest.mark.vcr(cassette_name="chat_basic.yaml")
def test_chat_basic():
    tool = ChatTool()
    request = ChatRequest(
        prompt="Explain async/await",
        model="gemini-2.5-pro",
        working_directory_absolute_path="/tmp"
    )
    result = tool.execute(request)
    assert result["success"]
```

### Running Tests
```bash
# All unit tests
pytest tests/ -v -m "not integration"

# Specific test
pytest tests/test_chat.py::test_chat_basic -v

# With coverage
pytest tests/ --cov=. --cov-report=html -m "not integration"
```

---

## 🚫 Anti-Patterns

### 1. Subprocess for MCP Tools
```python
# ❌ WRONG: Loses conversation memory
subprocess.run(["python", "server.py"])

# ✅ CORRECT: Use persistent server process
# Let Claude Desktop maintain the process
```

### 2. Hardcoded API Keys
```python
# ❌ WRONG
GEMINI_API_KEY = "AIzaSy..."

# ✅ CORRECT
from utils.env import get_env
api_key = get_env("GEMINI_API_KEY")
```

### 3. Manual Model Mapping
```python
# ❌ WRONG
if model.startswith("gpt"):
    provider = openai_provider

# ✅ CORRECT
provider = registry.get_provider_for_model(model)
```

---

## 📊 Available Models (November 2025)

**Gemini (3 models):**
- `gemini-2.5-pro` - 1M context, thinking, vision (score: 18)
- `gemini-2.5-pro-computer-use` - UI automation (score: 19)
- `gemini-2.5-flash-preview-09-2025` - Fast (score: 11)

**X.AI Grok (4 models):**
- `grok-4` - 256K context (score: 18)
- `grok-4-heavy` - Most powerful (score: 19)
- `grok-4-fast-reasoning` - Ultra-fast (score: 17)
- `grok-code-fast-1` - Code specialist (score: 17)

**Aliases:**
- `pro` → `gemini-2.5-pro`
- `grok4` → `grok-4`
- `grokcode` → `grok-code-fast-1`

---

## 🔄 Conversation Memory

**Critical:** Conversation memory ONLY works with persistent MCP server processes!

```python
# First call
response = chat_tool.execute(ChatRequest(...))
continuation_id = response["continuation_id"]

# Second call - continues thread
response = codereview_tool.execute(CodeReviewRequest(
    continuation_id=continuation_id,  # Same UUID
    ...
))
```

**Rules:**
- continuation_id must be valid UUID
- Threads expire after 3 hours
- Maximum 20 turns per thread
- Works across different tools

---

## 📝 Commit Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

**Version Bumping:**
- `feat:` - New feature (MINOR bump)
- `fix:` - Bug fix (PATCH bump)
- `perf:` - Performance (PATCH bump)

**Breaking Changes:**
- `feat!:` - Breaking change (MAJOR bump)
- `fix!:` - Breaking change (MAJOR bump)

**No Version Bump:**
- `chore:` - Maintenance
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `ci:` - CI/CD changes

---

## 🛠️ Development Workflow

### Before Coding
```bash
source venv/bin/activate
./code_quality_checks.sh
tail -n 50 logs/mcp_server.log
```

### After Changes
```bash
./code_quality_checks.sh
pytest tests/ -v -m "not integration"
python communication_simulator_test.py --quick
```

### Before Committing
```bash
./code_quality_checks.sh
./run_integration_tests.sh
git add .
git commit -m "feat: your feature description"
```

---

## 📚 Key Files Reference

- **Patterns:** `.robit/patterns.md` - Code standards
- **Architecture:** `.robit/architecture.md` - Design decisions
- **Context:** `.robit/context.md` - Codebase structure
- **CLAUDE.md:** Root directory - Active development guide
- **Tools:** `tools/` - 15 specialized tools
- **Providers:** `providers/` - 7 provider integrations

---

## 🔍 Quick Reference

### Adding a Tool
1. Create `tools/mytool.py` with request model
2. Inherit from `SimpleTool` or `WorkflowTool`
3. Register in `server.py`
4. Add system prompt to `systemprompts/`
5. Add tests to `tests/`

### Adding a Provider
1. Create `providers/myprovider.py`
2. Inherit from `ModelProvider`
3. Add model config to `conf/myprovider_models.json`
4. Register in `server.py`
5. Add tests

### Debugging
```bash
# View logs
tail -f logs/mcp_server.log

# View tool activity
tail -f logs/mcp_activity.log

# Search for errors
grep "ERROR" logs/mcp_server.log
```

---

**This file is optimized for GitHub Copilot. For detailed documentation, see `.robit/` directory.**

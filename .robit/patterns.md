# Zen MCP Server Code Patterns & Best Practices

**Version:** 9.1.3
**Python:** 3.9+ | **Updated:** November 2025

This document defines code standards, patterns, and anti-patterns for Zen MCP Server. AI assistants MUST follow these rules when generating code.

---

## 🚨 Critical Rules (NEVER VIOLATE)

### 1. Conversation Memory Requires Persistent Process

**NEVER use conversation memory with subprocess invocations!**

```python
# ❌ WRONG: Each subprocess loses memory
subprocess.run(["python", "server.py", "--tool", "chat"])
# Conversation memory resets every time!

# ✅ CORRECT: Persistent MCP server process
# Claude Desktop maintains persistent server
# Memory preserved across tool calls
```

**Rule:** Conversation memory (`utils/conversation_memory.py`) ONLY works with persistent MCP server processes, NOT subprocess invocations.

---

### 2. Always Use Type Hints (Python 3.9+)

**NEVER omit type hints for function signatures!**

```python
# ❌ WRONG: No type hints
def get_provider(model_name):
    return self.providers.get(model_name)

# ✅ CORRECT: Full type hints
def get_provider(self, model_name: str) -> Optional[ModelProvider]:
    return self.providers.get(model_name)

# ✅ CORRECT: Async with type hints
async def generate(self, request: dict[str, Any]) -> ModelResponse:
    response = await self.client.generate(**request)
    return ModelResponse(content=response)
```

**Rule:** Use type hints for all function parameters and return values. Import from `typing` for Python 3.9 compatibility.

---

### 3. Pydantic Models for Request/Response

**NEVER use plain dicts for tool requests!**

```python
# ❌ WRONG: Plain dict (no validation)
def execute(self, request: dict):
    prompt = request.get("prompt", "")
    model = request.get("model", "auto")

# ✅ CORRECT: Pydantic model (automatic validation)
class ChatRequest(ToolRequest):
    prompt: str = Field(..., description="User prompt")
    model: str = Field(..., description="Model to use")
    absolute_file_paths: list[str] = Field(default_factory=list)

def execute(self, request: ChatRequest) -> dict:
    # request.prompt is guaranteed to exist and be a string
    pass
```

**Rule:** All tool requests MUST use Pydantic models inheriting from `ToolRequest` or `WorkflowRequest`.

---

### 4. Async/Await for Provider Calls

**NEVER block on provider API calls!**

```python
# ❌ WRONG: Synchronous blocking call
def generate(self, request: dict) -> str:
    response = requests.post(self.api_url, json=request)
    return response.text

# ✅ CORRECT: Async non-blocking call
async def generate(self, request: dict[str, Any]) -> ModelResponse:
    async with self.session.post(self.api_url, json=request) as response:
        content = await response.text()
        return ModelResponse(content=content)
```

**Rule:** All provider `generate()` methods MUST be async. Use `aiohttp` for HTTP calls, not `requests`.

---

### 5. Model Name Resolution via Registry

**NEVER hardcode model-to-provider mapping!**

```python
# ❌ WRONG: Hardcoded provider selection
if model_name.startswith("gemini"):
    provider = GeminiProvider()
elif model_name.startswith("grok"):
    provider = XAIProvider()

# ✅ CORRECT: Registry-based resolution
provider = self.registry.get_provider_for_model(model_name)
capabilities = provider.get_capabilities(model_name)
```

**Rule:** Use `ModelProviderRegistry` for all model resolution. It handles aliases, availability, and provider routing.

---

## 🎨 Python Patterns

### Imports Organization

**Order imports using isort:**

```python
# 1. Standard library
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

# 2. Third-party
from pydantic import Field

# 3. TYPE_CHECKING imports (avoid circular deps)
if TYPE_CHECKING:
    from providers.shared import ModelCapabilities
    from tools.models import ToolModelCategory

# 4. Local imports
from config import TEMPERATURE_BALANCED
from systemprompts import CHAT_PROMPT
from tools.shared.base_models import ToolRequest

# 5. Relative imports
from .simple.base import SimpleTool
```

**Rule:** Run `isort .` before committing. Follows Black-compatible 120-char line limit.

---

### String Formatting

**Prefer f-strings over .format() or %:**

```python
# ❌ WRONG: Old-style formatting
message = "Model %s returned %d tokens" % (model_name, token_count)
message = "Model {} returned {} tokens".format(model_name, token_count)

# ✅ CORRECT: f-strings (Python 3.6+)
message = f"Model {model_name} returned {token_count} tokens"

# ✅ CORRECT: Multi-line f-strings
error_msg = (
    f"Provider {provider_name} failed to generate response "
    f"for model {model_name}. Reason: {error}"
)
```

**Rule:** Use f-strings for readability. Use parentheses for multi-line strings, not backslashes.

---

### Error Handling

**Use specific exceptions, not broad `except:`:**

```python
# ❌ WRONG: Catch-all exception
try:
    response = await provider.generate(request)
except:
    return {"error": "Something failed"}

# ✅ CORRECT: Specific exceptions
try:
    response = await provider.generate(request)
except ValueError as e:
    logger.error(f"Invalid request: {e}")
    return {"error": f"Invalid request: {e}"}
except asyncio.TimeoutError:
    logger.error(f"Request timed out for model {request.model}")
    return {"error": "Request timed out"}
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    return {"error": f"Unexpected error: {e}"}
```

**Rule:** Catch specific exceptions. Use `logger.exception()` for unexpected errors to include traceback.

---

### Optional Handling

**Use explicit None checks, not truthiness:**

```python
# ❌ WRONG: Truthiness can be ambiguous
if continuation_id:
    history = get_conversation_history(continuation_id)

# ✅ CORRECT: Explicit None check
if continuation_id is not None:
    history = get_conversation_history(continuation_id)

# ✅ CORRECT: Optional type hint
def get_history(continuation_id: Optional[str] = None) -> list[dict]:
    if continuation_id is not None:
        return load_history(continuation_id)
    return []
```

**Rule:** Use `is not None` for Optional types. Prevents bugs with empty strings, 0, or False.

---

## 🛠️ MCP Protocol Patterns

### Tool Registration

**Register tools with consistent naming:**

```python
# ✅ CORRECT: Tool registration in server.py
from tools.chat import ChatTool
from tools.debug import DebugTool
from tools.codereview import CodeReviewTool

server = Server("zen-mcp")

# Register tools
server.add_tool(ChatTool())
server.add_tool(DebugTool())
server.add_tool(CodeReviewTool())
```

**Rule:** Tool names should be lowercase, hyphen-separated (e.g., `code-review`, not `codeReview` or `CodeReview`).

---

### Tool Request Handling

**Validate requests with Pydantic:**

```python
class DebugRequest(WorkflowRequest):
    """Request model for debug workflow"""

    step: str = Field(..., description="Investigation step content")
    step_number: int = Field(..., ge=1, description="Current step (starts at 1)")
    total_steps: int = Field(..., ge=1, description="Estimated total steps")
    next_step_required: bool = Field(..., description="More steps needed?")
    findings: str = Field(..., description="Investigation findings")
    model: str = Field(..., description="AI model to use")

    @model_validator(mode="after")
    def validate_step_progression(self) -> "DebugRequest":
        """Validate step_number <= total_steps"""
        if self.step_number > self.total_steps:
            raise ValueError(
                f"step_number ({self.step_number}) cannot exceed total_steps ({self.total_steps})"
            )
        return self
```

**Rule:** Use Pydantic validators for complex validation logic. Keep field descriptions clear for AI assistants.

---

### Continuation ID Handling

**Always validate UUID format:**

```python
import uuid

# ✅ CORRECT: Validate UUID
def get_thread(continuation_id: str) -> Optional[ConversationThread]:
    try:
        uuid.UUID(continuation_id)  # Validate format
    except ValueError:
        logger.warning(f"Invalid continuation_id format: {continuation_id}")
        return None

    return CONVERSATION_THREADS.get(continuation_id)

# ❌ WRONG: No validation
def get_thread(continuation_id: str) -> Optional[ConversationThread]:
    return CONVERSATION_THREADS.get(continuation_id)
```

**Rule:** Validate continuation_id is a valid UUID before using. Prevents injection attacks.

---

## 🔧 Provider Patterns

### Provider Abstract Base Class

**All providers MUST inherit from ModelProvider:**

```python
from abc import ABC, abstractmethod
from providers.base import ModelProvider
from providers.shared import ModelResponse, ProviderType

class MyProvider(ModelProvider):
    """Custom provider implementation"""

    # Static model capabilities
    MODEL_CAPABILITIES = {
        "my-model": ModelCapabilities(
            model_name="my-model",
            context_window=100000,
            max_output_tokens=8192,
            ...
        )
    }

    def get_provider_type(self) -> ProviderType:
        """Return provider identity"""
        return ProviderType.CUSTOM

    async def generate(
        self,
        messages: list[dict],
        model: str,
        temperature: float = 0.5,
        **kwargs
    ) -> ModelResponse:
        """Generate response from model"""
        # Provider-specific logic
        return ModelResponse(...)
```

**Rule:** Implement all abstract methods. Use `MODEL_CAPABILITIES` for static model metadata.

---

### Model Capabilities Definition

**Define capabilities completely:**

```python
MODEL_CAPABILITIES = {
    "grok-4": ModelCapabilities(
        model_name="grok-4",
        friendly_name="X.AI (Grok-4)",
        aliases=["grok4", "grok-4"],  # Short names
        intelligence_score=18,  # 1-20 scale
        description="Grok-4 (256K context, real-time search)",
        context_window=256000,
        max_output_tokens=128000,
        supports_extended_thinking=True,  # Thinking mode
        supports_system_prompts=True,
        supports_streaming=False,
        supports_function_calling=True,
        supports_json_mode=True,
        supports_images=True,
        supports_temperature=True,
        max_image_size_mb=20.0,
        allow_code_generation=True,  # Can generate full code
    )
}
```

**Rule:** All fields should be accurate. `intelligence_score` affects auto-mode selection order.

---

### Provider Initialization

**Use environment variables for API keys:**

```python
from utils.env import get_env

class GeminiProvider(ModelProvider):
    def __init__(self):
        api_key = get_env("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        super().__init__(api_key=api_key)
        # Initialize client
        self.client = GeminiClient(api_key=api_key)
```

**Rule:** NEVER hardcode API keys. Use `utils.env.get_env()` for environment variables.

---

## 🔄 Workflow Patterns

### Step-by-Step Workflow

**Workflow tools use step tracking:**

```python
class DebugTool(WorkflowTool):
    def execute(self, request: DebugRequest) -> dict:
        # Step 1: Initial investigation
        if request.step_number == 1:
            return {
                "step_number": 1,
                "total_steps": 3,
                "next_step_required": True,
                "findings": "Starting investigation...",
                "continuation_id": self._create_thread(request)
            }

        # Steps 2-N: Continue investigation
        elif request.next_step_required:
            return self._continue_investigation(request)

        # Final step: Expert validation
        else:
            return self._complete_investigation(request)
```

**Rule:** Always track `step_number`, `total_steps`, and `next_step_required`. Use `continuation_id` for thread persistence.

---

### Confidence Level Tracking

**Track confidence as investigation progresses:**

```python
class DebugRequest(WorkflowRequest):
    confidence: Literal[
        "exploring",
        "low",
        "medium",
        "high",
        "very_high",
        "almost_certain",
        "certain"
    ] = Field(default="exploring")

# Progression:
# exploring → low → medium → high → very_high → almost_certain → certain

# Special handling:
if request.confidence == "certain":
    # Skip external validation
    return self._finalize_investigation(request)
else:
    # Trigger external model validation
    return self._validate_with_expert(request)
```

**Rule:** Use `very_high` instead of `certain` unless 100% confident. `certain` skips external validation.

---

### File Embedding Strategy

**Context-aware file loading:**

```python
def _embed_files(self, request: WorkflowRequest) -> str:
    """Embed files with context-aware strategy"""

    if request.step_number == 1:
        # Step 1: Reference files only (no full content)
        return self._reference_files(request.relevant_files)
    else:
        # Later steps: Full file content for analysis
        return self._load_full_files(request.relevant_files)

def _reference_files(self, files: list[str]) -> str:
    """Create file references without content"""
    return "\n".join([f"File: {file}" for file in files])

def _load_full_files(self, files: list[str]) -> str:
    """Load complete file content"""
    content = []
    for file_path in files:
        with open(file_path) as f:
            content.append(f"=== {file_path} ===\n{f.read()}")
    return "\n\n".join(content)
```

**Rule:** Step 1 references files, later steps load full content. Prevents token waste in planning phase.

---

## 🧪 Testing Patterns

### Unit Test with VCR

**Mock API calls with VCR cassettes:**

```python
import pytest

@pytest.mark.vcr(cassette_name="chat_basic.yaml")
def test_chat_tool_basic():
    """Test basic chat functionality"""
    tool = ChatTool()
    request = ChatRequest(
        prompt="Explain async/await in Python",
        model="gemini-2.5-pro",
        working_directory_absolute_path="/tmp"
    )

    result = tool.execute(request)

    assert result["success"]
    assert "async" in result["response"].lower()
    assert "await" in result["response"].lower()
```

**Rule:** Use VCR for deterministic testing. Cassettes stored in `tests/{provider}_cassettes/`.

---

### Simulator Test Pattern

**End-to-end scenario testing:**

```python
def test_cross_tool_continuation():
    """Test conversation continuation across tools"""

    # Step 1: Start with analyze tool
    analyze_request = {
        "step": "Analyze codebase",
        "step_number": 1,
        "total_steps": 2,
        "next_step_required": True,
        "findings": "Starting analysis",
        "model": "gemini-2.5-pro",
        "relevant_files": ["/path/to/file.py"]
    }
    analyze_response = run_tool("analyze", analyze_request)
    continuation_id = analyze_response["continuation_id"]

    # Step 2: Continue with codereview tool
    review_request = {
        "continuation_id": continuation_id,
        "step": "Review findings",
        "step_number": 1,
        "total_steps": 2,
        "next_step_required": True,
        "findings": "Reviewing...",
        "model": "grok-4"
    }
    review_response = run_tool("codereview", review_request)

    # Verify context preserved
    assert "continuation_id" in review_response
    assert review_response["continuation_id"] == continuation_id
```

**Rule:** Simulator tests validate cross-tool workflows. Test conversation memory, file deduplication, model selection.

---

### Integration Test with Approved Models

**Test real API calls with approved models:**

```python
@pytest.mark.integration
def test_chat_with_gemini():
    """Integration test using approved Gemini model"""
    tool = ChatTool()
    request = ChatRequest(
        prompt="What is 2+2?",
        model="gemini-2.5-pro",
        working_directory_absolute_path="/tmp"
    )

    result = tool.execute(request)
    assert result["success"]
    assert "4" in result["response"]
```

**Rule:** Mark with `@pytest.mark.integration`. Run with `pytest -m integration`. Uses approved models (Gemini/Grok) with real API keys.

---

## 🚫 Anti-Patterns

### 1. Subprocess for MCP Tools

```python
# ❌ WRONG: Loses conversation memory
subprocess.run(["python", "server.py", "--tool", "chat"])

# ✅ CORRECT: Use persistent server
# Let Claude Desktop or client maintain server process
```

---

### 2. Hardcoded API Keys

```python
# ❌ WRONG: Hardcoded secret
GEMINI_API_KEY = "AIzaSyABC123..."

# ✅ CORRECT: Environment variable
GEMINI_API_KEY = get_env("GEMINI_API_KEY")
```

---

### 3. Synchronous Provider Calls

```python
# ❌ WRONG: Blocking call
def generate(self, request: dict) -> str:
    response = requests.post(url, json=request)
    return response.text

# ✅ CORRECT: Async call
async def generate(self, request: dict) -> ModelResponse:
    async with self.session.post(url, json=request) as response:
        return ModelResponse(content=await response.text())
```

---

### 4. Plain Dict Requests

```python
# ❌ WRONG: No validation
def execute(self, request: dict):
    prompt = request.get("prompt", "")

# ✅ CORRECT: Pydantic model
def execute(self, request: ChatRequest):
    prompt = request.prompt  # Guaranteed to exist
```

---

### 5. Manual Model-to-Provider Mapping

```python
# ❌ WRONG: Hardcoded mapping
if model.startswith("gpt"):
    provider = openai_provider
elif model.startswith("gemini"):
    provider = gemini_provider

# ✅ CORRECT: Registry lookup
provider = registry.get_provider_for_model(model)
```

---

## ✅ Code Quality Checklist

Before committing code:

- [ ] Type hints on all functions
- [ ] Pydantic models for requests
- [ ] Async/await for I/O operations
- [ ] Specific exception handling (not bare `except`)
- [ ] Environment variables for secrets
- [ ] VCR cassettes for unit tests
- [ ] isort + Black + Ruff formatting
- [ ] Docstrings for public functions
- [ ] Logger usage (not print statements)
- [ ] No hardcoded model mappings

---

## 🎯 Style Guide Summary

**Python Version:** 3.9+
**Line Length:** 120 characters
**Formatter:** Black
**Import Sorter:** isort
**Linter:** Ruff

**Run quality checks:**
```bash
./code_quality_checks.sh
```

**Enforces:**
- pycodestyle (PEP 8)
- pyflakes (unused imports, variables)
- bugbear (common bugs)
- comprehensions (list/dict comprehension style)
- pyupgrade (Python 3.9+ idioms)

---

**These patterns are enforced by code review and CI. Violations block PRs.**

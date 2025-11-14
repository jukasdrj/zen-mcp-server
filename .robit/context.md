# Zen MCP Server Codebase Context

**Version:** 9.1.3
**Last Updated:** November 2025

This document provides AI assistants with essential context about the Zen MCP Server codebase structure, domain logic, and key patterns.

---

## 📱 Project Overview

**Zen MCP Server** is a Model Context Protocol server that connects AI CLI tools (Claude Code, Gemini CLI, Codex CLI, etc.) to multiple AI providers for enhanced code analysis, problem-solving, and collaborative development.

Users can:
- Chat with multiple AI models within a single prompt (Gemini, X.AI Grok)
- Use specialized tools for code review, debugging, planning, consensus building
- Continue conversations across tools while preserving full context
- Bridge external CLI tools (clink) for isolated subagent workflows

**Tech Stack:**
- **Server:** Python 3.9+, asyncio, Pydantic, MCP SDK
- **Providers:** Gemini, X.AI (Grok), OpenRouter, Azure OpenAI, DIAL, Custom
- **Testing:** pytest, VCR cassettes, simulator tests, integration tests
- **Configuration:** JSON model configs, environment variables
- **File Operations:** Morph MCP (enhanced filesystem tools with smart editing)

---

## 🗂️ Morph MCP Filesystem Tools

**Zen MCP Server integrates with the Morph MCP filesystem tools for enhanced file operations:**

**Available Tools:**
- `mcp__filesystem-with-morph__read_file` - Read files with head/tail support
- `mcp__filesystem-with-morph__read_multiple_files` - Batch file reading (more efficient than individual reads)
- `mcp__filesystem-with-morph__write_file` - Create or overwrite files
- `mcp__filesystem-with-morph__edit_file` - **PRIMARY EDITING TOOL** - Smart editing with minimal context
- `mcp__filesystem-with-morph__tiny_edit_file` - Line-based edits for small changes
- `mcp__filesystem-with-morph__create_directory` - Create directory structures
- `mcp__filesystem-with-morph__list_directory` - Directory listings
- `mcp__filesystem-with-morph__list_directory_with_sizes` - Directory listings with size sorting
- `mcp__filesystem-with-morph__directory_tree` - Recursive JSON tree view
- `mcp__filesystem-with-morph__move_file` - Move or rename files
- `mcp__filesystem-with-morph__search_files` - Recursive file search with exclude patterns
- `mcp__filesystem-with-morph__get_file_info` - File metadata (size, timestamps, permissions)

**Key Features:**

1. **Smart Editing (`edit_file`)**
   - Uses placeholders like `// ... existing code ...` to show only changed lines
   - More efficient than traditional search/replace
   - Reduces token usage by showing minimal context
   - Example:
   ```python
   # Instead of showing entire file, just show changes:
   def my_function():
       # ... existing code ...
       new_line_here()  # Added
       # ... existing code ...
   ```

2. **Batch Operations**
   - `read_multiple_files` - Read several files in one call
   - More efficient than multiple individual reads
   - Useful for code analysis across multiple files

3. **Enhanced Search**
   - Recursive pattern matching
   - Exclude patterns support
   - Case-insensitive options

**Usage Guidelines:**
- **Prefer `edit_file`** for most editing tasks (primary tool)
- Use `tiny_edit_file` only for single-line or very small edits
- Use `read_multiple_files` when analyzing related files together
- All paths must be absolute (no relative paths)

---

## 🏗️ Architecture

### Project Structure

```
zen-mcp-server/
├── server.py                       # Main MCP server entry point
├── config.py                       # Configuration and constants
├── tools/                          # 15 specialized AI tools
│   ├── simple/                     # Single-shot tools (chat, challenge, apilookup)
│   ├── workflow/                   # Multi-step tools (debug, codereview, planner)
│   ├── shared/                     # Shared tool utilities
│   ├── chat.py                     # General dev chat
│   ├── debug.py                    # Root cause analysis
│   ├── codereview.py               # Systematic code review
│   ├── planner.py                  # Task planning
│   ├── consensus.py                # Multi-model decision making
│   ├── thinkdeep.py                # Complex problem analysis
│   ├── analyze.py                  # Codebase analysis
│   ├── refactor.py                 # Refactoring opportunities
│   ├── tracer.py                   # Execution flow tracing
│   ├── testgen.py                  # Test generation
│   ├── docgen.py                   # Documentation generation
│   ├── precommit.py                # Pre-commit validation
│   ├── secaudit.py                 # Security audit
│   ├── clink.py                    # CLI-to-CLI bridge
│   └── listmodels.py               # Model listing
├── providers/                      # AI provider integrations
│   ├── base.py                     # Abstract provider interface
│   ├── gemini.py                   # Google Gemini provider
│   ├── xai.py                      # X.AI (Grok) provider
│   ├── openrouter.py               # OpenRouter provider (fallback)
│   ├── azure_openai.py             # Azure OpenAI provider (optional)
│   ├── dial.py                     # DIAL provider (optional)
│   ├── custom.py                   # Custom provider (optional)
│   ├── registry.py                 # Model provider registry
│   └── shared/                     # Shared provider utilities
├── utils/                          # Shared utilities
│   ├── conversation_memory.py      # Cross-tool conversation persistence
│   ├── client_info.py              # Client detection
│   ├── file_types.py               # File type detection
│   └── env.py                      # Environment variable handling
├── systemprompts/                  # System prompts for each tool
│   ├── chat_prompt.py              # Chat system prompt
│   ├── debug_prompt.py             # Debug system prompt
│   ├── codereview_prompt.py        # Code review system prompt
│   └── ... (15 total)
├── conf/                           # Model configuration files
│   ├── gemini_models.json          # Gemini model metadata
│   ├── xai_models.json             # X.AI (Grok) model metadata
│   ├── openrouter_models.json      # OpenRouter model metadata
│   └── ... (7 total)
├── clink/                          # CLI-to-CLI bridge
│   ├── registry.py                 # CLI client registry
│   └── models.py                   # CLI request/response models
├── tests/                          # Unit tests (111 files)
├── simulator_tests/                # End-to-end scenario tests (40 files)
├── logs/                           # Runtime logs
│   ├── mcp_server.log              # Main server log
│   └── mcp_activity.log            # Tool activity log
└── docs/                           # Documentation (24 files)
```

---

## 🗄️ Core Modules

### Tools Module (`tools/`)

**Two Types of Tools:**

1. **Simple Tools** (`tools/simple/base.py`)
   - Single-shot tools that complete in one interaction
   - Examples: `chat`, `challenge`, `apilookup`
   - Direct request → response pattern

2. **Workflow Tools** (`tools/workflow/base.py`)
   - Multi-step tools with investigation phases
   - Examples: `debug`, `codereview`, `planner`, `consensus`
   - Step-by-step workflow with confidence tracking
   - Support for external model validation

**Key Tools:**

| Tool | Type | Purpose |
|------|------|---------|
| `chat` | Simple | General dev chat and brainstorming |
| `debug` | Workflow | Root cause analysis with hypothesis testing |
| `codereview` | Workflow | Systematic code review with severity levels |
| `planner` | Workflow | Task planning with branching |
| `consensus` | Workflow | Multi-model decision making |
| `thinkdeep` | Workflow | Complex problem analysis |
| `analyze` | Workflow | Codebase architecture analysis |
| `refactor` | Workflow | Refactoring opportunities |
| `tracer` | Workflow | Execution flow tracing |
| `testgen` | Workflow | Test generation with edge cases |
| `docgen` | Workflow | Documentation generation |
| `precommit` | Workflow | Pre-commit validation |
| `secaudit` | Workflow | Security audit (OWASP Top 10) |
| `clink` | Simple | CLI-to-CLI bridge for subagents |
| `listmodels` | Simple | List available models |

---

### Providers Module (`providers/`)

**Provider Abstraction:**

```python
class ModelProvider(ABC):
    """Abstract base class for all model backends"""

    @abstractmethod
    def get_provider_type(self) -> ProviderType

    @abstractmethod
    async def generate(self, request: dict) -> ModelResponse

    def get_capabilities(self, model_name: str) -> ModelCapabilities
```

**Primary Providers:**

1. **Gemini** (`providers/gemini.py`)
   - Models: `gemini-2.5-pro`, `gemini-2.5-pro-computer-use`, `gemini-2.5-flash-preview-09-2025`
   - Supports: Extended thinking, vision, 1M context window

2. **X.AI Grok** (`providers/xai.py`)
   - Models: `grok-4`, `grok-4-heavy`, `grok-4-fast-reasoning`, `grok-code-fast-1`
   - Supports: Extended thinking, 256K-2M context window, real-time search

**Optional Fallback Providers:**

3. **OpenRouter** (`providers/openrouter.py`)
   - 200+ models from multiple providers
   - Dynamic model discovery

4. **Azure OpenAI** (`providers/azure_openai.py`)
   - Enterprise OpenAI models (optional)

5. **DIAL** (`providers/dial.py`)
   - Custom DIAL protocol support (optional)

6. **Custom** (`providers/custom.py`)
   - User-defined custom models (optional)

**Model Registry System:**

```python
class ModelProviderRegistry:
    """Central registry for all providers and models"""

    def get_provider_for_model(self, model_name: str) -> ModelProvider
    def get_available_model_names(self) -> list[str]
    def is_model_available(self, model_name: str) -> bool
```

---

### Conversation Memory (`utils/conversation_memory.py`)

**Purpose:** Enable multi-turn conversations and cross-tool continuation in stateless MCP environment.

**Key Features:**
- **UUID-based threads** - Unique conversation thread identification
- **Cross-tool continuation** - Switch tools while preserving context
- **File deduplication** - Newest-first prioritization when files appear in multiple turns
- **Turn limiting** - Maximum 20 turns to prevent runaway conversations
- **3-hour TTL** - Automatic thread expiration
- **Thread-safe** - Concurrent access support

**Example Flow:**

```python
# Tool A creates thread
thread_id = create_thread("analyze", request_data)

# Tool A adds response
add_turn(thread_id, "assistant", response, files=[...], tool_name="analyze")

# Tool B continues thread
thread = get_thread(thread_id)
history = build_conversation_history(thread_id, token_budget=50000)

# Tool B adds its response
add_turn(thread_id, "assistant", response, tool_name="codereview")
```

**Critical Rules:**
- ONLY works with persistent MCP server processes (not subprocesses)
- Memory is in-process, not shared across subprocess boundaries
- Simulator tests require special handling to work with conversation memory

---

## 🚀 Key Services

### ModelProviderRegistry (`providers/registry.py`)

**Purpose:** Centralized provider and model management.

**Key Methods:**
- `get_provider_for_model(model_name)` - Routes model to correct provider
- `get_available_model_names()` - Lists all models from enabled providers
- `is_model_available(model_name)` - Checks if model is accessible

**Provider Selection Logic:**
```python
# Auto-selects provider based on model name
provider = registry.get_provider_for_model("gemini-2.5-pro")  # Returns GeminiProvider
provider = registry.get_provider_for_model("grok-4")  # Returns XAIProvider
provider = registry.get_provider_for_model("grok-4-heavy")  # Returns XAIProvider
```

---

### WorkflowTool (`tools/workflow/base.py`)

**Purpose:** Base class for multi-step workflow tools with investigation phases.

**Key Features:**
- **Step tracking** - `step_number`, `total_steps`, `next_step_required`
- **Confidence levels** - `exploring`, `low`, `medium`, `high`, `very_high`, `almost_certain`, `certain`
- **File embedding** - Context-aware file loading with deduplication
- **Issue tracking** - Severity-based issue classification
- **Expert validation** - Optional external model review

**Workflow Pattern:**

```python
class DebugTool(WorkflowTool):
    def execute(self, request: DebugRequest) -> dict:
        # Step 1: Investigation planning
        if request.step_number == 1:
            return self._plan_investigation(request)

        # Steps 2-N: Execute investigation
        elif request.next_step_required:
            return self._continue_investigation(request)

        # Final step: Expert validation (optional)
        else:
            return self._complete_investigation(request)
```

---

### SimpleTool (`tools/simple/base.py`)

**Purpose:** Base class for single-shot tools.

**Key Features:**
- **Direct execution** - Single request → response
- **File support** - Optional file context
- **Image support** - Optional image context
- **Conversation continuation** - Via `continuation_id`

**Simple Pattern:**

```python
class ChatTool(SimpleTool):
    def execute(self, request: ChatRequest) -> dict:
        # Load conversation history if continuing
        history = self._load_conversation_history(request.continuation_id)

        # Execute single-shot request
        response = await self.provider.generate({
            "prompt": request.prompt,
            "files": request.absolute_file_paths,
            "history": history
        })

        return {"response": response}
```

---

## 🎨 Request/Response Patterns

### Tool Request Models (Pydantic)

**All tools use Pydantic models for strict typing:**

```python
class DebugRequest(WorkflowRequest):
    """Request model for debug workflow"""

    step: str = Field(..., description="Investigation step content")
    step_number: int = Field(..., description="Current step (starts at 1)")
    total_steps: int = Field(..., description="Estimated total steps")
    next_step_required: bool = Field(..., description="More steps needed?")
    findings: str = Field(..., description="Investigation findings")
    hypothesis: str = Field(..., description="Current theory")
    confidence: ConfidenceLevel = Field(..., description="Confidence in analysis")
    files_checked: list[str] = Field(default_factory=list)
    relevant_files: list[str] = Field(default_factory=list)
    model: str = Field(..., description="AI model to use")
```

### Common Fields

**All workflow tools share:**
- `step` - Current step narrative
- `step_number` - Current step index (1-based)
- `total_steps` - Estimated total steps
- `next_step_required` - Whether more steps are needed
- `findings` - Accumulated findings
- `model` - AI model to use
- `continuation_id` - Optional thread continuation

**Conversation Fields:**
- `continuation_id` - UUID for cross-tool continuation
- `absolute_file_paths` - Files to include in context
- `images` - Images to include (absolute paths or base64)

---

## ☁️ Configuration

### Model Configuration (`conf/*.json`)

**Each provider has a JSON config file:**

```json
{
  "_README": {
    "description": "Model metadata for provider",
    "field_descriptions": { ... }
  },
  "models": [
    {
      "model_name": "gemini-2.5-pro",
      "friendly_name": "Google (Gemini 2.5 Pro)",
      "aliases": ["pro", "gemini-pro"],
      "intelligence_score": 18,
      "description": "Gemini 2.5 Pro (1M context, thinking, vision)",
      "context_window": 1000000,
      "max_output_tokens": 128000,
      "supports_extended_thinking": true,
      "supports_json_mode": true,
      "supports_images": true,
      "allow_code_generation": true
    }
  ]
}
```

**Available Models (Nov 2025):**

**Gemini (3 models):**
- `gemini-2.5-pro` (1M context, thinking, vision) - Score 18
- `gemini-2.5-pro-computer-use` (1M context, UI automation) - Score 19
- `gemini-2.5-flash-preview-09-2025` (1M context, fast) - Score 11

**X.AI Grok (4 models):**
- `grok-4` (256K context, real-time search) - Score 18
- `grok-4-heavy` (256K context, most powerful) - Score 19
- `grok-4-fast-reasoning` (2M context, ultra-fast) - Score 17
- `grok-code-fast-1` (2M context, code specialist) - Score 17

**Intelligence Score:** 1-20 rating used for auto-mode model selection (higher = more capable)

---

### Environment Configuration

**Required Environment Variables:**

```bash
# Provider API Keys (Primary)
GEMINI_API_KEY=...              # Google AI Studio key
XAI_API_KEY=...                 # X.AI (Grok) key
OPENROUTER_API_KEY=...          # OpenRouter key
AZURE_OPENAI_API_KEY=...        # Azure OpenAI key
DIAL_API_KEY=...                # DIAL key
CUSTOM_API_KEY=...              # Custom provider key

# Optional Configuration
DEFAULT_MODEL=auto              # Default model (or "auto" for intelligent selection)
LOCALE=                         # Language/locale (e.g., "fr-FR", "ja-JP")
MAX_MCP_OUTPUT_TOKENS=25000     # MCP transport limit
```

**Configuration Constants (`config.py`):**

```python
__version__ = "9.1.3"
__updated__ = "2025-10-22"

DEFAULT_MODEL = "auto"          # Auto model selection by Claude
TEMPERATURE_ANALYTICAL = 0.2    # Code review, debugging
TEMPERATURE_BALANCED = 0.5      # General chat
TEMPERATURE_CREATIVE = 0.7      # Architecture, deep thinking
MCP_PROMPT_SIZE_LIMIT = 60_000  # Characters (calculated from MAX_MCP_OUTPUT_TOKENS)
```

---

## 🧪 Testing

### Three-Tier Testing Strategy

**1. Unit Tests (`tests/`)**
- **111 test files** with pytest
- **VCR cassettes** for API mocking
- **Coverage:** Provider logic, tool execution, request validation
- **Run:** `pytest tests/ -v -m "not integration"`

**2. Simulator Tests (`simulator_tests/`)**
- **40 end-to-end scenario tests**
- **Tests:** Cross-tool continuation, conversation memory, model selection
- **Run:** `python communication_simulator_test.py --quick`

**3. Integration Tests**
- **Uses approved models:** Gemini and Grok with real API keys
- **Tests:** Real API calls, provider integration
- **Run:** `./run_integration_tests.sh`

### Test Patterns

**Unit Test with VCR:**

```python
@pytest.mark.vcr(cassette_name="debug_basic.yaml")
def test_debug_tool():
    tool = DebugTool()
    request = DebugRequest(
        step="Investigate bug",
        step_number=1,
        total_steps=3,
        next_step_required=True,
        findings="Starting investigation",
        model="gemini-2.5-pro"
    )
    result = tool.execute(request)
    assert result["success"]
```

**Simulator Test:**

```python
def test_cross_tool_continuation():
    """Test conversation continuation across tools"""
    # Start with analyze tool
    response1 = run_tool("analyze", {...})
    continuation_id = response1["continuation_id"]

    # Continue with codereview tool
    response2 = run_tool("codereview", {
        "continuation_id": continuation_id,
        ...
    })

    # Verify context preserved
    assert "findings from analyze" in response2["content"]
```

---

## 🚨 Critical Rules

### 1. Conversation Memory Persistence

**CRITICAL:** Conversation memory ONLY works with persistent MCP server processes!

```python
# ✅ CORRECT: Persistent server (Claude Desktop)
# Memory persists across tool calls

# ❌ WRONG: Subprocess invocations (simulator tests)
# Each subprocess starts with empty memory
```

**Rule:** When testing conversation memory, use persistent server or special simulator handling.

---

### 2. Model Selection

**Auto Mode (DEFAULT_MODEL="auto"):**
- Claude intelligently selects model based on task
- Uses `intelligence_score` for ordering
- Presents only models from enabled providers

**Explicit Mode:**
- User specifies model name or alias
- Provider automatically determined by registry
- Falls back to auto mode if model not found

**Examples:**

```python
# Auto mode - Claude picks best model
request = {"prompt": "Review this code", "model": "auto"}

# Explicit mode - User picks model
request = {"prompt": "Review this code", "model": "gemini-2.5-pro"}
request = {"prompt": "Review this code", "model": "grok-4-heavy"}
request = {"prompt": "Review this code", "model": "grok-4"}

# Alias mode - User uses short name
request = {"prompt": "Review this code", "model": "pro"}  # gemini-2.5-pro
request = {"prompt": "Review this code", "model": "grok4"}  # grok-4
request = {"prompt": "Review this code", "model": "grokcode"}  # grok-code-fast-1
```

---

### 3. File Context Handling

**Deduplication Rules:**
- Same file path in multiple turns: **newest takes precedence**
- Token budget exceeded: **oldest files excluded first**
- Cross-tool continuation: **files from all turns preserved**

**Example:**

```python
# Turn 1: analyze tool
files = ["/path/foo.py", "/path/bar.py"]

# Turn 2: codereview tool (continues)
files = ["/path/foo.py", "/path/baz.py"]  # foo.py updated

# Effective file list (newest-first):
# 1. /path/baz.py (Turn 2)
# 2. /path/foo.py (Turn 2) - overrides Turn 1
# 3. /path/bar.py (Turn 1)
```

---

### 4. Workflow Confidence Levels

**Confidence Progression:**
```
exploring → low → medium → high → very_high → almost_certain → certain
```

**Special Handling:**
- `certain` = Skip external validation (100% confidence)
- `very_high` or `almost_certain` = Trigger external validation
- `exploring` → `low` = Early investigation phases

**Rule:** Use `very_high` instead of `certain` unless you're absolutely sure external validation isn't needed.

---

## 📚 Key Documentation

- **CLAUDE.md** (root) - Active development quick reference
- **AGENTS.md** (root) - Repository guidelines and build commands
- **docs/README.md** - Documentation hub
- **docs/tools/** - Tool-specific documentation
- **docs/adding_tools.md** - Tool creation guide
- **docs/adding_providers.md** - Provider integration guide
- **docs/advanced-usage.md** - Advanced patterns
- **docs/configuration.md** - Configuration guide

---

## 🔍 Common Patterns

### Adding a Tool

```python
# 1. Create tool class
class MyTool(SimpleTool):  # or WorkflowTool
    def get_name(self) -> str:
        return "mytool"

    def get_description(self) -> str:
        return "My tool description"

    def execute(self, request: MyToolRequest) -> dict:
        # Tool logic here
        return {"success": True, "response": "..."}

# 2. Create request model
class MyToolRequest(ToolRequest):
    prompt: str = Field(..., description="User prompt")
    model: str = Field(..., description="Model to use")

# 3. Register in server.py
from tools.mytool import MyTool
server.add_tool(MyTool())
```

### Adding a Provider

```python
# 1. Create provider class
class MyProvider(ModelProvider):
    MODEL_CAPABILITIES = {
        "my-model": ModelCapabilities(
            model_name="my-model",
            friendly_name="My Model",
            context_window=100000,
            ...
        )
    }

    def get_provider_type(self) -> ProviderType:
        return ProviderType.CUSTOM

    async def generate(self, request: dict) -> ModelResponse:
        # Provider logic here
        return ModelResponse(...)

# 2. Register in providers/__init__.py
from providers.myprovider import MyProvider

# 3. Add to registry in server.py
registry.register_provider(MyProvider(api_key=...))
```

### Using Conversation Continuation

```python
# Tool A
response = {
    "continuation_id": "uuid-here",
    "response": "Initial analysis..."
}

# Tool B (continues)
request = {
    "continuation_id": "uuid-here",  # Same UUID
    "prompt": "Continue with review",
    "model": "grok-4-heavy"
}

# Tool B has access to:
# - All previous conversation turns
# - Files from previous tools
# - Original thread metadata
```

---

**This context file is AI-optimized. Refer to `docs/` for human-readable documentation.**
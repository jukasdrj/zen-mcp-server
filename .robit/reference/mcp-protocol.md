# MCP Protocol Essentials for Zen MCP Server

**MCP Version:** 2024-11-05
**Last Updated:** November 2025

---

## 🎯 MCP Protocol Overview

**Model Context Protocol (MCP)** is a stateless protocol for connecting AI assistants to external tools and resources.

**Key Concepts:**
- **Stateless** - Each request is independent
- **Tool-based** - Functionality exposed as discrete tools
- **Request/Response** - Simple JSON-RPC style
- **Type-safe** - Pydantic models for validation

---

## 🔧 Tool Definition

**Every MCP tool must provide:**
1. **Name** - Lowercase, hyphen-separated (e.g., `code-review`)
2. **Description** - Brief purpose for AI to understand when to use it
3. **Input Schema** - Pydantic model defining required/optional fields
4. **Execute Method** - Async function that processes requests

**Example:**
```python
class ChatTool(SimpleTool):
    def get_name(self) -> str:
        return "chat"  # Tool identifier
    
    def get_description(self) -> str:
        return "General development chat"  # When to use
    
    def get_request_model(self):
        return ChatRequest  # Input schema
    
    async def execute_impl(self, request: ChatRequest) -> dict:
        # Processing logic
        return {"response": "..."}  # Output
```

---

## 📦 Request/Response Format

**Request Structure:**
```json
{
  "tool": "chat",
  "arguments": {
    "prompt": "Explain async/await",
    "model": "gemini-2.5-pro",
    "working_directory_absolute_path": "/path/to/project"
  }
}
```

**Response Structure:**
```json
{
  "success": true,
  "response": "Async/await explanation...",
  "continuation_id": "uuid-here",
  "metadata": {
    "model_used": "gemini-2.5-pro",
    "provider": "google"
  }
}
```

---

## 🔄 Conversation Continuation

**Problem:** MCP is stateless - tools don't remember previous interactions.

**Solution:** Zen's conversation memory system with UUID-based threads.

**Usage:**
```python
# First call - creates thread
response1 = chat_tool.execute(ChatRequest(
    prompt="Analyze this code",
    model="gemini-2.5-pro"
))
continuation_id = response1["continuation_id"]

# Second call - continues thread
response2 = codereview_tool.execute(CodeReviewRequest(
    continuation_id=continuation_id,  # Same UUID
    prompt="Review findings from analysis",
    model="grok-4"
))
```

**Key Rules:**
- continuation_id must be valid UUID
- Threads expire after 3 hours
- Works across different tools
- Preserves file context and conversation history

---

## 🚨 Critical MCP Constraints

### 1. Token Limit

**MCP transport has combined request+response limit:**
- Default: 25,000 tokens (~60,000 characters for input)
- Configurable via MAX_MCP_OUTPUT_TOKENS env variable
- Zen automatically manages this with token budgeting

**What IS limited:**
- User input from MCP client
- Tool response to MCP client

**What is NOT limited:**
- Internal prompts to AI providers
- File content processing
- Conversation history (stored separately)

### 2. Absolute Paths Only

**All file paths MUST be absolute:**
```python
# ❌ WRONG
absolute_file_paths=["src/file.py", "./data.json"]

# ✅ CORRECT
absolute_file_paths=["/full/path/to/src/file.py", "/full/path/to/data.json"]
```

### 3. Stateless by Design

**Each request is independent:**
- No persistent state between calls
- Use continuation_id for multi-turn
- Conversation memory is Zen's solution, not part of MCP spec

---

## 📚 References

- MCP Spec: https://spec.modelcontextprotocol.io/
- Zen Implementation: `server.py`, `tools/`, `providers/`
- Conversation Memory: `utils/conversation_memory.py`
- Patterns: `.robit/patterns.md`

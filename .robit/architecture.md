# Zen MCP Server Architecture

**Version:** 9.1.3
**Last Updated:** November 2025

This document explains the high-level system design decisions, trade-offs, and architectural decision records (ADRs).

---

## 🎯 Design Goals

1. **Multi-Provider Support** - 7+ AI providers with consistent interface
2. **Cross-Tool Conversation** - Preserve context when switching tools
3. **Workflow Flexibility** - Single-shot and multi-step tools
4. **MCP Compliance** - Stateless protocol with stateful memory
5. **Extensibility** - Easy to add tools and providers
6. **Performance** - Async operations, efficient token usage
7. **Testing** - Three-tier strategy (unit, simulator, integration)
8. **Developer Experience** - Clear patterns, type safety, comprehensive docs

---

## 🏗️ System Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client (Claude Code)                  │
└──────────────────────────────┬──────────────────────────────┘
                               │ MCP Protocol
┌──────────────────────────────▼──────────────────────────────┐
│                      MCP Server (server.py)                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────────┐ │
│  │   Tools    │  │ Providers  │  │  Conversation Memory   │ │
│  │  Registry  │  │  Registry  │  │   (Thread-based)       │ │
│  └────────────┘  └────────────┘  └────────────────────────┘ │
└───────┬──────────────┬──────────────────────┬───────────────┘
        │              │                      │
   ┌────▼─────┐   ┌───▼────────┐    ┌────────▼──────┐
   │  Simple  │   │  Workflow  │    │  Conversation │
   │  Tools   │   │   Tools    │    │    Memory     │
   │ (Chat,   │   │ (Debug,    │    │  (In-Memory)  │
   │ Challenge)│   │ CodeReview)│    └───────────────┘
   └──────────┘   └─────┬──────┘
                        │
              ┌─────────▼─────────┐
              │  Model Providers  │
              │ ┌───────────────┐ │
              │ │    Gemini     │ │
              │ │   X.AI Grok   │ │
              │ │  OpenRouter   │ │
              │ │   Azure AI    │ │
              │ │     DIAL      │ │
              │ │    Custom     │ │
              │ └───────────────┘ │
              └───────────────────┘
```

---

## 📋 Architecture Decision Records (ADRs)

### ADR-001: In-Memory Conversation Storage

**Status:** Accepted
**Date:** November 2025
**Context:**

MCP protocol is stateless by design. Each tool invocation is independent with no built-in memory. However, users need:
- Multi-turn conversations within a single tool
- Cross-tool context preservation (e.g., analyze → codereview)
- File context deduplication across turns

**Decision:**

Implement in-process, thread-based conversation memory using Python dictionaries with UUID-keyed threads.

**Alternatives Considered:**

1. **External Database (Redis, PostgreSQL)**
   - ❌ Adds deployment complexity
   - ❌ Requires additional infrastructure
   - ✅ Survives restarts
   - ✅ Supports multiple processes

2. **File-based Storage**
   - ❌ Slower I/O performance
   - ❌ Concurrent access issues
   - ✅ Survives restarts
   - ❌ More complex

3. **In-Memory (Chosen)**
   - ✅ Fast access (sub-millisecond)
   - ✅ Simple implementation
   - ✅ No external dependencies
   - ✅ Perfect for single-user desktop
   - ❌ Lost on restart
   - ❌ Doesn't work with subprocesses

**Consequences:**

- ✅ Excellent performance for desktop use case
- ✅ Zero configuration required
- ❌ Threads lost on server restart (acceptable for desktop)
- ❌ Simulator tests require special handling
- ⚠️ 3-hour TTL and 20-turn limit prevent memory leaks

**Implementation:** `utils/conversation_memory.py`

---

### ADR-002: Two-Tool Architecture (Simple vs Workflow)

**Status:** Accepted
**Date:** November 2025
**Context:**

Different tasks have different complexity levels:
- Simple tasks: Single question, immediate answer (e.g., "Explain async/await")
- Complex tasks: Multi-step investigation with hypothesis testing (e.g., "Debug this performance issue")

**Decision:**

Create two distinct tool base classes:
1. **SimpleTool** - Single-shot execution, minimal overhead
2. **WorkflowTool** - Multi-step with confidence tracking, expert validation

**Alternatives Considered:**

1. **Single Unified Base Class**
   - ❌ Forces all tools to use workflow pattern
   - ❌ Overhead for simple tasks
   - ✅ Simpler codebase

2. **No Base Classes (Ad-hoc)**
   - ❌ Code duplication
   - ❌ Inconsistent patterns
   - ❌ Harder to maintain

3. **Two Base Classes (Chosen)**
   - ✅ Appropriate complexity per tool
   - ✅ Clear patterns for each type
   - ✅ Shared utilities in base classes
   - ❌ Slight duplication between bases

**Consequences:**

- ✅ Simple tools remain fast and lightweight
- ✅ Workflow tools get step tracking, confidence levels, expert validation
- ✅ Clear guidance for new tool authors
- ⚠️ Some duplication in base class utilities (mitigated by shared module)

**Implementation:** 
- `tools/simple/base.py` - SimpleTool base
- `tools/workflow/base.py` - WorkflowTool base
- `tools/shared/` - Shared utilities

---

### ADR-003: Provider Registry Pattern

**Status:** Accepted
**Date:** November 2025
**Context:**

With 7+ providers and 15+ tools, we need a way to:
- Route model requests to correct provider
- Support model aliases (e.g., "pro" → "gemini-3.1-pro-preview")
- Handle provider availability (missing API keys)
- Enable/disable providers dynamically

**Decision:**

Implement centralized `ModelProviderRegistry` with:
- Model-to-provider mapping
- Alias resolution
- Availability checking
- Dynamic provider registration

**Alternatives Considered:**

1. **Hardcoded if/else Chains**
   - ❌ Brittle, hard to maintain
   - ❌ Duplicated across tools
   - ❌ Difficult to test

2. **Tool-Level Provider Selection**
   - ❌ Inconsistent behavior
   - ❌ Code duplication
   - ❌ Hard to add providers

3. **Registry Pattern (Chosen)**
   - ✅ Centralized logic
   - ✅ Easy to add providers
   - ✅ Consistent across tools
   - ✅ Testable in isolation
   - ❌ Slight abstraction overhead

**Consequences:**

- ✅ Adding new provider requires one registration call
- ✅ Alias support "just works" for all tools
- ✅ Provider availability checked in one place
- ⚠️ Small performance overhead (mitigated by caching)

**Implementation:** `providers/registry.py`

---

### ADR-004: Multi-Provider Strategy (Primary + Fallback)

**Status:** Accepted
**Date:** November 2025
**Context:**

Users want access to best models without vendor lock-in. However:
- Some providers are essential (Gemini, X.AI)
- Others are optional fallbacks (OpenRouter, Azure)
- API key management should be simple

**Decision:**

Implement tiered provider strategy:
- **Primary:** Gemini, X.AI (Grok) - Required for core functionality
- **Optional Fallback:** OpenRouter (200+ models when primary unavailable)
- **Enterprise Optional:** Azure OpenAI (for corporate environments)
- **Custom/DIAL:** User-defined providers

**Alternatives Considered:**

1. **All Providers Required**
   - ❌ Users must configure 7+ API keys
   - ❌ Confusing setup
   - ❌ Costly

2. **Single Provider Only**
   - ❌ Vendor lock-in
   - ❌ No fallback options
   - ❌ Limited model choice

3. **Tiered Strategy (Chosen)**
   - ✅ Core functionality with 1-2 keys
   - ✅ Flexibility for power users
   - ✅ Enterprise-friendly
   - ⚠️ More complex provider logic

**Consequences:**

- ✅ Minimal setup for most users (1 key = Gemini or Grok)
- ✅ OpenRouter as safety net (fallback to 200+ models)
- ✅ Enterprise can use Azure without touching other providers
- ⚠️ Documentation must clarify provider tiers

**Implementation:** 
- `server.py` - Provider registration logic
- `conf/*.json` - Model metadata per provider

---

### ADR-005: File Deduplication Strategy (Newest-First)

**Status:** Accepted
**Date:** November 2025
**Context:**

Multi-turn conversations often reference same files multiple times:
- Turn 1: Analyze `foo.py` (version A)
- Turn 2: User edits `foo.py` → version B
- Turn 3: Review changes to `foo.py`

Without deduplication:
- Wasted tokens (same file sent multiple times)
- Stale content (older version might be used)
- MCP token limit exceeded

**Decision:**

Implement "newest-first" deduplication:
1. Track file paths across all turns
2. When duplicate found, keep **newest version only**
3. Preserve turn order for non-duplicates
4. Apply token budget (oldest files excluded first if over budget)

**Alternatives Considered:**

1. **No Deduplication**
   - ❌ Wasted tokens
   - ❌ Stale content bugs
   - ❌ MCP limit exceeded

2. **Oldest-First (First Mention Wins)**
   - ❌ Stale content used
   - ❌ Doesn't reflect user edits

3. **Newest-First (Chosen)**
   - ✅ Always uses latest content
   - ✅ Saves 20-30% tokens
   - ✅ Respects user edits
   - ⚠️ Slightly more complex logic

**Consequences:**

- ✅ Token savings enable longer conversations
- ✅ Latest file content always used
- ✅ Works across tool boundaries
- ⚠️ Must track file ages carefully

**Implementation:** `utils/conversation_memory.py:deduplicate_files()`

---

### ADR-006: Async-First Design

**Status:** Accepted
**Date:** November 2025
**Context:**

AI provider APIs are network I/O bound:
- Gemini API: 2-10 second response times
- Streaming responses can take minutes
- Users expect concurrent operations

Python 3.9+ has excellent async/await support.

**Decision:**

Make all I/O operations async:
- Provider `generate()` methods
- Tool `execute()` methods
- HTTP requests (aiohttp, not requests)

**Alternatives Considered:**

1. **Synchronous (Threading)**
   - ❌ GIL limits true parallelism
   - ❌ More complex debugging
   - ❌ Higher memory overhead

2. **Multiprocessing**
   - ❌ Loses conversation memory (separate process)
   - ❌ Higher overhead
   - ❌ More complex

3. **Async/Await (Chosen)**
   - ✅ Efficient I/O concurrency
   - ✅ Lower memory overhead
   - ✅ Cleaner code (no callbacks)
   - ⚠️ Requires discipline (await everywhere)

**Consequences:**

- ✅ Can handle multiple concurrent requests
- ✅ Better resource utilization
- ✅ Streaming responses possible
- ⚠️ Mixing sync/async is error-prone (linter helps)

**Implementation:** 
- All provider `generate()` methods are async
- All tool `execute_impl()` methods are async
- Uses `aiohttp` for HTTP

---

### ADR-007: Pydantic for Request Validation

**Status:** Accepted
**Date:** November 2025
**Context:**

MCP tools receive JSON requests from clients. Need to:
- Validate required fields
- Type-check parameters
- Provide clear error messages
- Document schema for AI assistants

**Decision:**

Use Pydantic v2 models for all tool requests:
- Each tool defines request model
- Inherits from `ToolRequest` or `WorkflowRequest`
- Automatic validation on instantiation
- Field descriptions shown to AI

**Alternatives Considered:**

1. **Manual Dict Validation**
   - ❌ Boilerplate code
   - ❌ Inconsistent error messages
   - ❌ Easy to miss fields

2. **Dataclasses**
   - ❌ No validation
   - ❌ Less rich features
   - ✅ Standard library

3. **Pydantic (Chosen)**
   - ✅ Automatic validation
   - ✅ Clear error messages
   - ✅ JSON schema generation
   - ✅ IDE autocomplete support
   - ⚠️ External dependency

**Consequences:**

- ✅ Zero validation bugs (all caught at request parsing)
- ✅ Self-documenting APIs
- ✅ AI assistants understand schemas
- ⚠️ Pydantic dependency (acceptable, widely used)

**Implementation:** 
- `tools/shared/base_models.py` - Base classes
- Each tool defines `XxxRequest` model

---

### ADR-008: Three-Tier Testing Strategy

**Status:** Accepted
**Date:** November 2025
**Context:**

Need to test:
- Individual functions (unit level)
- Cross-tool workflows (integration level)
- Real API behavior (end-to-end)

But also need:
- Fast CI/CD (< 5 minutes)
- Free tests (not burning API credits)
- Confidence in production behavior

**Decision:**

Implement three-tier testing:
1. **Unit Tests** - VCR cassettes (free, fast, mock APIs)
2. **Simulator Tests** - Real APIs with approved models (thorough, moderate cost)
3. **Integration Tests** - Real APIs with approved models (validates real behavior)

**Alternatives Considered:**

1. **Unit Tests Only**
   - ❌ Misses integration bugs
   - ❌ Doesn't validate real API behavior

2. **Integration Tests Only**
   - ❌ Slow (minutes)
   - ❌ Expensive (API costs)
   - ❌ Flaky (network issues)

3. **Three-Tier (Chosen)**
   - ✅ Fast feedback (unit tests)
   - ✅ Confidence (integration tests)
   - ✅ Balanced cost
   - ⚠️ More complex test infrastructure

**Consequences:**

- ✅ CI/CD runs in ~2 minutes (unit tests only)
- ✅ Full test suite pre-commit (~10 minutes)
- ✅ VCR cassettes = free unlimited tests
- ⚠️ Must record cassettes initially

**Implementation:**
- `tests/` - Unit tests with VCR
- `simulator_tests/` - End-to-end scenarios
- `pytest.ini` - Test markers and configuration

---

### ADR-009: Token Budget Management

**Status:** Accepted
**Date:** November 2025
**Context:**

MCP protocol has token limits:
- MAX_MCP_OUTPUT_TOKENS = 25,000 tokens (~60k chars)
- Workflow tools need to reference files
- Conversation history grows over time

Without management:
- MCP transport errors
- Truncated responses
- Lost context

**Decision:**

Implement two-phase token strategy:
1. **Step 1** - File references only (no full content)
   - Saves tokens for planning phase
   - AI can see what files are available
   - Example: "File: /path/to/foo.py (200 lines)"

2. **Step 2+** - Full file content
   - Embeds complete file content for analysis
   - Token budget applied (oldest files excluded first)
   - Conversation history limited to recent turns

**Alternatives Considered:**

1. **Always Full Content**
   - ❌ Wastes tokens in planning phase
   - ❌ Hits MCP limit faster

2. **Always References**
   - ❌ AI can't analyze code
   - ❌ Defeats purpose of workflow tools

3. **Two-Phase (Chosen)**
   - ✅ Efficient token usage
   - ✅ Planning phase fast
   - ✅ Analysis phase thorough
   - ⚠️ Tools must implement correctly

**Consequences:**

- ✅ 40-50% token savings in workflow tools
- ✅ Fewer MCP transport errors
- ✅ Longer conversations possible
- ⚠️ Workflow tools must handle both phases

**Implementation:** 
- `tools/workflow/base.py` - File embedding logic
- `utils/conversation_memory.py` - History limiting

---

### ADR-010: Model Intelligence Scoring

**Status:** Accepted
**Date:** November 2025
**Context:**

"Auto mode" needs to select best model for task. Criteria:
- Reasoning capability
- Context window size
- Speed vs. quality trade-off
- Cost considerations

**Decision:**

Assign 1-20 intelligence score to each model:
- Higher score = more capable
- Used for ordering in auto mode
- AI assistant sees best models first
- Factors: reasoning, thinking mode, context window

**Scoring Examples:**
- Gemini 2.5 Pro Computer Use: 19 (highest capability)
- Grok-4 Heavy: 19 (top tier reasoning)
- Gemini 2.5 Pro: 18 (strong reasoning)
- Grok-4: 18 (strong reasoning)
- Grok-4 Fast Reasoning: 17 (optimized speed)
- Grok Code Fast: 17 (code specialist)
- Gemini 2.5 Flash Preview: 11 (fast, lightweight)

**Alternatives Considered:**

1. **No Scoring (Alphabetical)**
   - ❌ Random model selection
   - ❌ Doesn't reflect capability

2. **Complex Multi-Factor Scoring**
   - ❌ Hard to maintain
   - ❌ Overengineered

3. **Simple 1-20 Score (Chosen)**
   - ✅ Easy to understand
   - ✅ Simple to update
   - ✅ Effective ordering
   - ⚠️ Subjective (team consensus required)

**Consequences:**

- ✅ Auto mode selects appropriate models
- ✅ Users can override with explicit model names
- ✅ Easy to add new models
- ⚠️ Scores may need periodic review

**Implementation:** 
- `conf/*.json` - Model metadata with scores
- `providers/registry.py` - Score-based ordering

---

### ADR-011: Conversation Thread TTL and Limits

**Status:** Accepted
**Date:** November 2025
**Context:**

In-memory conversation threads can grow unbounded:
- Long-running conversations (100+ turns)
- Abandoned threads (user forgets)
- Memory leaks

**Decision:**

Implement safeguards:
1. **3-hour TTL** - Threads expire after 3 hours inactivity
2. **20-turn limit** - Maximum 20 turns per thread
3. **Periodic cleanup** - Remove expired threads

**Alternatives Considered:**

1. **No Limits**
   - ❌ Memory leaks
   - ❌ Unbounded growth

2. **Aggressive Limits (1 hour, 5 turns)**
   - ❌ Interrupts workflows
   - ❌ Poor user experience

3. **Balanced Limits (Chosen)**
   - ✅ Prevents memory leaks
   - ✅ Allows reasonable workflows
   - ✅ Automatic cleanup
   - ⚠️ Users might hit limits (rare)

**Consequences:**

- ✅ Memory usage bounded
- ✅ No manual cleanup required
- ✅ 20 turns sufficient for most workflows
- ⚠️ Very long workflows might need to restart (acceptable)

**Implementation:** 
- `utils/conversation_memory.py` - TTL and limit checks
- Cleanup runs on every thread access

---

### ADR-012: MCP Stateless with Stateful Memory

**Status:** Accepted
**Date:** November 2025
**Context:**

MCP protocol is intentionally stateless (each request independent). However:
- Users expect conversations to flow naturally
- Cross-tool context is essential
- File context should persist

**Decision:**

Embrace the paradox:
- **MCP layer:** Remain stateless (no server-side session)
- **Application layer:** Maintain conversation memory
- **Bridge:** Use `continuation_id` (UUID) as session key

Each request can optionally include `continuation_id`:
- If provided: Load conversation history
- If missing: Start fresh

**Alternatives Considered:**

1. **Pure Stateless (No Memory)**
   - ❌ Poor user experience
   - ❌ Can't build on previous work

2. **MCP Protocol Extension (Session Support)**
   - ❌ Not part of MCP spec
   - ❌ Breaks compatibility

3. **Stateless Protocol + Stateful App (Chosen)**
   - ✅ MCP compliant
   - ✅ Great user experience
   - ✅ Flexible (memory is optional)
   - ⚠️ Requires UUID discipline

**Consequences:**

- ✅ Remains MCP compliant
- ✅ Natural conversation flow
- ✅ Works with any MCP client
- ⚠️ Memory tied to process lifetime

**Implementation:**
- MCP server treats each request independently
- Application layer manages `continuation_id` → thread mapping
- UUID validation prevents injection attacks

---

## 🔀 Design Patterns Used

### 1. Abstract Factory (Providers)
- `ModelProvider` abstract base class
- Concrete implementations: `GeminiProvider`, `XAIProvider`, etc.
- Registry pattern for dynamic provider selection

### 2. Template Method (Tools)
- `SimpleTool` and `WorkflowTool` base classes
- Subclasses override specific steps
- Base classes handle common logic (logging, errors, etc.)

### 3. Strategy Pattern (Model Selection)
- `ModelProviderRegistry` encapsulates selection logic
- Can swap providers without changing tool code
- Supports multiple selection strategies (explicit, alias, auto)

### 4. Decorator Pattern (VCR Cassettes)
- `@pytest.mark.vcr` wraps tests
- Records/replays API calls
- Transparent to test code

### 5. Repository Pattern (Conversation Memory)
- `ConversationMemory` abstracts storage
- Could swap in-memory → database without changing tools
- Clean separation of concerns

---

## 📊 Performance Optimizations

### 1. File Deduplication
- **Problem:** Same files sent multiple times across turns
- **Solution:** Track file paths, keep newest version only
- **Impact:** 20-30% token savings

### 2. Two-Phase File Embedding
- **Problem:** Full files waste tokens in planning phase
- **Solution:** Step 1 = references, Step 2+ = full content
- **Impact:** 40-50% token savings in workflow tools

### 3. Async I/O
- **Problem:** Blocking API calls slow down server
- **Solution:** Async/await throughout
- **Impact:** Can handle concurrent requests efficiently

### 4. Connection Pooling
- **Problem:** Creating new HTTP connections expensive
- **Solution:** Reuse `aiohttp.ClientSession` instances
- **Impact:** Faster API calls, lower latency

### 5. Token Budget Management
- **Problem:** MCP transport has 25k token limit
- **Solution:** Exclude oldest files first when over budget
- **Impact:** Fewer MCP transport errors

---

## 🚨 Known Limitations

### 1. In-Memory Storage
- **Limitation:** Threads lost on server restart
- **Mitigation:** 3-hour TTL means users rarely notice
- **Future:** Could add database persistence if needed

### 2. Single-Process Only
- **Limitation:** Conversation memory doesn't work with subprocesses
- **Mitigation:** Simulator tests use special handling
- **Future:** External storage would enable multi-process

### 3. MCP Token Limits
- **Limitation:** Cannot send unlimited context
- **Mitigation:** Token budget, file deduplication, two-phase embedding
- **Future:** MCP spec might increase limits

### 4. Provider API Rate Limits
- **Limitation:** Subject to provider rate limits
- **Mitigation:** Async design prevents blocking
- **Future:** Could add retry logic with backoff

---

## 📚 References

- Context: `.robit/context.md` - Codebase structure
- Patterns: `.robit/patterns.md` - Code standards
- CLAUDE.md: Root directory - Active development guide
- MCP Spec: https://spec.modelcontextprotocol.io/
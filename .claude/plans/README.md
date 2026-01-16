# PAL MCP Planning Directory

This directory contains planning documents for PAL MCP Server development. Plans are created and managed by Claude Code using the native planning-with-files workflow.

## What is PAL MCP?

PAL MCP (Provider Abstraction Layer MCP, formerly Zen MCP) is a Python-based Model Context Protocol server that enables multi-model AI orchestration. It connects AI CLI tools (Claude Code, Gemini CLI, Codex CLI, etc.) to multiple AI providers (Anthropic, Google, OpenAI, Grok, Azure, Ollama, etc.) within a single workflow.

**Core Capabilities:**
- Multi-model orchestration (chat, consensus, code review, debugging, planning, etc.)
- CLI-to-CLI bridging via `clink` tool
- Conversation continuity across models and tools
- Systematic investigation workflows (thinkdeep, codereview, debug, secaudit, etc.)
- Vision capabilities for analyzing screenshots and diagrams
- Local model support for privacy and zero API costs

## Planning Context for MCP Development

When planning work on PAL MCP, consider these MCP-specific patterns:

### 1. Tool Design Patterns
- **Tool schemas:** All tools use JSON Schema validation (see `tools/*/schemas.py`)
- **Input validation:** Pydantic models for request validation
- **Response format:** Structured responses with metadata
- **Error handling:** Proper MCP error types and user-friendly messages
- **Continuation support:** Most tools support `continuation_id` for multi-turn workflows

### 2. Protocol Compliance
- **Transport:** stdio for MCP communication (see `server.py`)
- **JSON-RPC 2.0:** All requests/responses follow JSON-RPC format
- **Tool discovery:** Tools register via `list_tools()` endpoint
- **Resource management:** Proper cleanup on shutdown
- **Error propagation:** MCP-compliant error codes and messages

### 3. Provider Integration
- **Provider abstraction:** `providers/` directory contains model adapters
- **Model configuration:** `conf/*.json` files define available models
- **Unified interface:** All providers implement common interface
- **Fallback handling:** Graceful degradation when providers unavailable
- **Cost tracking:** Monitor API usage across providers

### 4. Testing Strategy
- **Unit tests:** `tests/` directory with pytest
- **Integration tests:** `simulator_tests/` for end-to-end workflows
- **Mock providers:** Test tools without hitting real APIs
- **Schema validation:** Test all tool inputs/outputs
- **Error scenarios:** Test failure modes and error handling

### 5. Documentation
- **Tool docs:** Each tool has `docs/tools/*.md` documentation
- **Provider docs:** Provider-specific setup in `docs/providers/`
- **System prompts:** `systemprompts/` contains role definitions
- **Example workflows:** `examples/` directory
- **CHANGELOG.md:** Track all changes for users

## Plan Structure

Plans in this directory follow the planning-with-files workflow:

### Core Files
- **`task_plan.md`** - Main task breakdown with steps, dependencies, and progress tracking
- **`findings.md`** - Investigation notes, discoveries, and important observations
- **`progress.md`** - Execution log with timestamps, decisions, and next steps

### MCP-Specific Sections

When planning MCP features, include:

#### Tool Development Plans
```markdown
## Tool: [tool_name]

### Schema Design
- Input parameters (required/optional)
- Response format
- Error conditions
- Continuation support

### Implementation Steps
1. Define Pydantic models
2. Implement tool handler
3. Add schema validation
4. Register in server.py
5. Write unit tests
6. Document in docs/tools/

### Testing Strategy
- Unit tests for business logic
- Integration tests for MCP protocol
- Error handling scenarios
```

#### Provider Integration Plans
```markdown
## Provider: [provider_name]

### Configuration
- Model IDs to support
- API credentials required
- Rate limits and quotas
- Special capabilities (vision, streaming, etc.)

### Implementation Steps
1. Create provider adapter in providers/
2. Add model config to conf/
3. Implement common interface methods
4. Handle provider-specific errors
5. Add cost tracking
6. Document setup in docs/providers/

### Testing Strategy
- Mock API responses
- Test rate limiting
- Validate cost tracking
- Error handling (auth, quota, network)
```

#### Protocol Enhancement Plans
```markdown
## Protocol Enhancement: [feature_name]

### MCP Compliance
- Which MCP spec version?
- New capabilities to advertise
- Backward compatibility concerns
- Client impact analysis

### Implementation Steps
1. Review MCP specification
2. Update server.py protocol handlers
3. Add capability discovery
4. Update client examples
5. Migration guide for users

### Testing Strategy
- Protocol conformance tests
- Client compatibility tests
- Error handling validation
```

## Workflow Examples

### Feature Development
1. Create `task_plan.md` with tool/provider/feature design
2. Document findings in `findings.md` as you explore codebase
3. Track progress in `progress.md` with implementation steps
4. Update plans as requirements change

### Bug Investigation
1. Create `findings.md` with bug report and reproduction steps
2. Document investigation in `progress.md` with timestamps
3. Create `task_plan.md` when fix approach is clear
4. Track testing and verification steps

### Refactoring Work
1. Create `task_plan.md` with refactoring scope and goals
2. Use `findings.md` to document current architecture issues
3. Track migration in `progress.md` with before/after metrics
4. Include rollback plan and testing strategy

## Best Practices

### For MCP Tool Development
- **Schema-first design:** Define schemas before implementation
- **Validate early:** Use Pydantic models for all inputs
- **Test edge cases:** Empty inputs, invalid types, missing fields
- **Document examples:** Show real-world usage in tool docs
- **Version carefully:** Breaking changes require major version bump

### For Provider Integration
- **Provider isolation:** Keep provider code self-contained
- **Graceful degradation:** Handle missing API keys, rate limits
- **Cost awareness:** Log token usage, warn on expensive operations
- **Local fallback:** Support Ollama for privacy/offline use
- **Test mocking:** Don't hit real APIs in tests

### For Protocol Work
- **MCP spec compliance:** Follow official MCP specification
- **Backward compatibility:** Don't break existing clients
- **Error clarity:** User-friendly error messages, not stack traces
- **Capability discovery:** Advertise features clients can query
- **Documentation:** Update examples when protocol changes

## File Organization

```
.claude/plans/
├── README.md              # This file
├── SETUP.md              # Setup instructions for planning workflow
├── task_plan.md          # Active task breakdown (created per-task)
├── findings.md           # Investigation notes (created per-task)
├── progress.md           # Execution log (created per-task)
└── archived/             # Completed plans (optional)
    ├── 2026-01-feature-x/
    │   ├── task_plan.md
    │   ├── findings.md
    │   └── progress.md
    └── 2026-01-bug-y/
        ├── task_plan.md
        └── progress.md
```

## Related Documentation

- **[AGENTS.md](../../AGENTS.md)** - Pre-configured agent roles (planner, codereviewer, etc.)
- **[CLAUDE.md](../../CLAUDE.md)** - Development guidelines and architecture
- **[CONTRIBUTING.md](../../CONTRIBUTING.md)** - Contribution workflow
- **[docs/](../../docs/)** - Full tool and provider documentation
- **[tests/](../../tests/)** - Test suite examples

## Quick Links

**Tool Documentation:**
- [chat](../../docs/tools/chat.md) - Multi-model collaboration
- [clink](../../docs/tools/clink.md) - CLI-to-CLI bridging
- [codereview](../../docs/tools/codereview.md) - Systematic code review
- [debug](../../docs/tools/debug.md) - Root cause analysis
- [planner](../../docs/tools/planner.md) - Interactive planning

**Provider Setup:**
- [Anthropic](../../docs/providers/anthropic.md)
- [Google (Gemini)](../../docs/providers/google.md)
- [OpenAI](../../docs/providers/openai.md)
- [Ollama (Local)](../../docs/providers/ollama.md)

---

**Last Updated:** 2026-01-16
**Planning Mode:** Native (planning-with-files workflow)
**MCP Version:** 1.0.0
**Server Version:** 1.1.0

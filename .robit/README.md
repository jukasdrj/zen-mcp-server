# 🧘 Zen MCP Server AI Development Configuration

**Version:** 9.1.3
**Python:** 3.9+ | **MCP Protocol:** 2024-11-05 | **Updated:** November 2025

This directory contains AI-optimized context and configuration for development tools (Claude Code, GitHub Copilot, etc.). Designed for Zen MCP Server and reusable across Python/MCP projects.

---

## 🎯 Purpose

The `.robit/` directory provides:
- **Structured context** for AI assistants to understand your codebase
- **Reusable patterns** for Python 3.9+, async/await, MCP protocol, multi-provider architecture
- **Consistent workflows** across different AI tools
- **Project-specific rules** that override default AI behaviors

---

## 📁 Directory Structure

```
.robit/
├── README.md                    # This file - overview and usage
├── context.md                   # Codebase structure and key concepts
├── patterns.md                  # Python best practices and code patterns
├── architecture.md              # System design and architectural decisions
├── prompts/                     # Reusable prompt templates
│   ├── code-review.md          # Code review checklist
│   ├── debug-guide.md          # Systematic debugging approach
│   ├── adding-tool.md          # Step-by-step tool creation
│   └── adding-provider.md      # Provider integration guide
├── reference/                   # Quick reference materials
│   ├── mcp-protocol.md         # MCP protocol essentials
│   ├── python-async.md         # Async/await best practices
│   ├── pydantic-models.md      # Request/response patterns
│   └── testing-guide.md        # Unit + simulator + integration testing
└── workflows/                   # AI-assisted development workflows
    ├── adding-features.md      # Feature development workflow
    ├── testing-changes.md      # Testing workflow
    └── provider-debugging.md   # Debugging provider issues

```

---

## 🚀 Quick Start

### For AI Assistants (Auto-Loaded)

When you open this project in Claude Code, GitHub Copilot, or other AI tools, they should automatically:
1. Read `context.md` to understand the codebase
2. Reference `patterns.md` for code standards
3. Consult `architecture.md` for design decisions

### For Developers

**Use prompts for common tasks:**
```bash
# Code review with AI
# Reference: .robit/prompts/code-review.md

# Add a new tool
# Reference: .robit/prompts/adding-tool.md

# Debug provider issue
# Reference: .robit/workflows/provider-debugging.md
```

**Check patterns before coding:**
- Python async patterns: `.robit/reference/python-async.md`
- MCP protocol patterns: `.robit/reference/mcp-protocol.md`
- Testing guide: `.robit/reference/testing-guide.md`

---

## 🤖 AI Tool Integration

### Claude Code
- Reads all `.robit/*.md` files automatically
- Uses `context.md` for codebase understanding
- References `patterns.md` for code generation
- Consults `CLAUDE.md` (root) for project-specific overrides

### GitHub Copilot
- Uses `.robit/patterns.md` for inline suggestions
- References `.github/copilot-instructions.md` (if exists)
- Respects Python 3.9+ patterns

### Cursor
- Integrates with `.robit/` context files
- Uses patterns for code completion
- Consults architecture for system-level decisions

---

## 📚 Key Files Explained

### `context.md` - Codebase Overview
**Purpose:** Help AI understand your project structure, dependencies, and domain logic.

**Contains:**
- Project architecture (MCP server + multi-provider + workflow system)
- Core modules (tools, providers, utils, systemprompts)
- Key services (ModelProviderRegistry, ConversationMemory, WorkflowTool)
- 15 specialized tools (chat, debug, codereview, planner, etc.)
- 7 provider integrations (Gemini, OpenAI, X.AI, OpenRouter, etc.)

**When to update:**
- New tool added
- New provider integrated
- Architecture changes
- Major refactoring

---

### `patterns.md` - Code Standards
**Purpose:** Enforce Python best practices and project-specific patterns.

**Contains:**
- Python 3.9+ patterns (type hints, async/await, Pydantic models)
- MCP protocol patterns (tool registration, request/response, continuation_id)
- Workflow patterns (step tracking, confidence levels, file embedding)
- Provider patterns (abstract base, capabilities, model resolution)
- Anti-patterns (what NOT to do)
- Testing patterns (pytest, VCR cassettes, simulator tests)

**When to update:**
- New coding standard adopted
- Common bug pattern discovered
- Python version upgrade
- Team consensus on best practice

---

### `architecture.md` - System Design
**Purpose:** Document high-level decisions and trade-offs.

**Contains:**
- Multi-provider strategy
- Workflow system design (step-by-step vs single-shot)
- Conversation memory architecture
- File deduplication strategy
- Testing strategy (unit → simulator → integration)
- Performance optimizations

**When to update:**
- Major refactoring completed
- New provider integrated
- Architectural decision made
- Performance optimization implemented

---

## 🔄 Exporting to Other Projects

This `.robit/` configuration is designed for **90% reusability** across Python/MCP projects.

### Universal Files (100% reusable)
- `README.md` (this file) - Minimal changes needed
- `prompts/` - Language-agnostic templates
- `workflows/` - General development workflows

### Python-Specific Files (95% reusable)
- `patterns.md` - Update for project-specific conventions
- `reference/python-async.md` - Universal Python async rules
- `reference/pydantic-models.md` - Reuse if using Pydantic

### Project-Specific Files (80% reusable)
- `context.md` - Replace with your project structure
- `architecture.md` - Document your system design
- `reference/mcp-protocol.md` - Reuse if using MCP

### Export Steps
1. Copy entire `.robit/` directory to new project
2. Update `context.md` with new project structure
3. Review `patterns.md` for project-specific conventions
4. Update `architecture.md` with new system design
5. Keep `prompts/` and `workflows/` as-is (universal)

**Estimated export time:** 30-60 minutes

---

## 📖 Documentation Hierarchy

This project uses a **layered documentation strategy**:

```
📄 CLAUDE.md (root)              ← Active development quick reference
📄 .robit/context.md             ← AI context (codebase structure)
📄 .robit/patterns.md            ← Code standards (Python, MCP, async)
📄 .robit/architecture.md        ← System design (high-level decisions)
📁 docs/                         ← Human-readable documentation
   ├── tools/                    ← Tool-specific documentation
   ├── advanced-usage.md         ← Advanced usage patterns
   ├── configuration.md          ← Configuration guide
   └── adding_providers.md       ← Provider integration guide
```

**Rule of thumb:**
- **AI reads:** `.robit/*` + `CLAUDE.md`
- **Humans read:** `docs/*` + `CLAUDE.md`
- **Both read:** `CLAUDE.md` (single source of truth for active standards)

---

## 🛠️ Maintenance

### Weekly
- [ ] Review AI-generated code for pattern compliance
- [ ] Update `patterns.md` if new standards emerge

### Monthly
- [ ] Sync `context.md` with major feature changes
- [ ] Archive outdated patterns to `docs/archive/`

### Per Release
- [ ] Update version numbers in this README
- [ ] Document new architectural decisions in `architecture.md`
- [ ] Verify all `.robit/reference/*` files are current

---

## 🆘 Troubleshooting

### AI not following project patterns?
1. Check if `CLAUDE.md` (root) has conflicting instructions
2. Verify `.robit/patterns.md` is clear and specific
3. Add examples to patterns if AI misunderstands

### AI generating incorrect architecture?
1. Update `.robit/architecture.md` with constraints
2. Add "CRITICAL" or "NEVER" markers for hard rules
3. Document trade-offs and rationale

### Export to new project not working?
1. Verify target project has similar structure (Python/MCP)
2. Update `context.md` first (highest impact)
3. Adapt `patterns.md` to target language conventions

---

## 🎯 Best Practices

### For AI Assistants
- **Always read** `context.md` before suggesting code
- **Reference** `patterns.md` for Python/MCP compliance
- **Consult** `architecture.md` for system constraints
- **Defer to** `CLAUDE.md` (root) for overrides

### For Developers
- **Update** `.robit/*` when project evolves
- **Review** AI suggestions against patterns
- **Document** new patterns as they emerge
- **Export** configuration to new projects for consistency

### For Teams
- **Sync** `.robit/patterns.md` across projects
- **Share** prompts in `.robit/prompts/`
- **Version** configuration changes with git
- **Review** AI-generated code for compliance

---

## 📦 Related Files

- **Root:** `CLAUDE.md` - Project-specific overrides and active standards
- **Root:** `AGENTS.md` - Repository guidelines and build commands
- **Docs:** `docs/README.md` - Human-readable documentation hub
- **GitHub:** `.github/copilot-instructions.md` - Copilot configuration (if exists)

---

## 🌟 What Makes This Setup Special

### 1. **Multi-AI Compatibility**
- Works with Claude Code, Copilot, and other AI tools
- No vendor lock-in
- Consistent behavior across tools

### 2. **90% Reusable**
- Export to any Python/MCP project in 30-60 minutes
- Language-agnostic prompts and workflows
- Project-specific files clearly marked

### 3. **Living Documentation**
- Git-versioned configuration
- Evolves with project
- Team consensus enforced

### 4. **Zero Boilerplate**
- No repeated context in every prompt
- AI reads once, remembers project structure
- Faster, more accurate code generation

---

## 🚀 Next Steps

### For This Project
1. ✅ `.robit/` configuration complete
2. ⏳ Train team on AI workflows
3. ⏳ Monitor AI adherence to patterns
4. ⏳ Refine patterns based on feedback

### For Other Projects
1. Copy `.robit/` directory
2. Update `context.md` (30 min)
3. Review `patterns.md` (15 min)
4. Test with AI assistant (15 min)
5. Enjoy consistent AI assistance!

---

**Last Updated:** November 2025
**Maintainer:** Zen MCP Team
**License:** MIT (configuration only, not server code)
**Status:** ✅ Production-Ready
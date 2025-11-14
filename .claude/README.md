# Claude Code Agent Setup (Zen MCP Server)

**Synced from:** bookstrack-backend
**Tech Stack:** TypeScript, Node.js, MCP Protocol

## Available Agents

### ✅ Universal Agents (Synced from Backend)
- **project-manager** - Orchestration and delegation
- **zen-mcp-master** - Deep analysis (14 Zen MCP tools)

### 🚧 MCP-Specific Agent (TODO)
- **mcp-dev-agent** - MCP server development, testing, deployment

## Quick Start

```bash
# For complex workflows
/skill project-manager

# For analysis/review/debugging
/skill zen-mcp-master

# For MCP development (after creating mcp-dev-agent)
/skill mcp-dev-agent
```

## Next Steps

### 1. Create mcp-dev-agent (Required)

Create `.claude/skills/mcp-dev-agent/skill.md` with MCP-specific capabilities:

- TypeScript development patterns
- MCP protocol testing
- npm package management
- Integration testing with Claude Desktop
- Server deployment and monitoring

### 2. Customize project-manager

Edit `.claude/skills/project-manager/skill.md`:
- Replace `cloudflare-agent` references with `mcp-dev-agent`
- Update delegation patterns for MCP development workflows

### 3. Add Hooks (Optional)

**Pre-commit hook** (`.claude/hooks/pre-commit.sh`):
- TypeScript type checking
- ESLint validation
- Test suite execution
- MCP protocol validation

**Post-tool-use hook** (`.claude/hooks/post-tool-use.sh`):
- Suggest `mcp-dev-agent` when npm commands are used
- Suggest `zen-mcp-master` for TypeScript file changes

## Documentation

- `ROBIT_OPTIMIZATION.md` - Complete agent architecture
- `ROBIT_SHARING_FRAMEWORK.md` - How sharing works
- Backend repo: https://github.com/jukasdrj/bookstrack-backend/.claude/

## Future Updates

Run `../bookstrack-backend/scripts/sync-robit-to-repos.sh` to sync updates from backend.

# Claude Code Agent Setup (Zen MCP Server)

## Available Skills

- **project-manager** - Top-level orchestration and delegation
- **zen-mcp-master** - Deep analysis via 14 Zen MCP tools (debug, codereview, secaudit, etc.)
- **mcp-dev-agent** - MCP server development, testing, deployment

## Quick Start

```bash
# For complex workflows
/project-manager

# For analysis/review/debugging
/zen-mcp-master

# For MCP development
/mcp-dev-agent
```

## Structure

- `skills/` - Skill definitions with frontmatter
- `rules/` - Modular instruction files imported by CLAUDE.md
- `hooks/` - Pre/post tool-use and prompt submission hooks
- `plans/` - Planning documents
- `settings.json` - Shared project permissions and hooks
- `settings.local.json` - Local-only settings (plugins, etc.)

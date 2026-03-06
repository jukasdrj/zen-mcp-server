# Planning Workflow Setup - PAL MCP Server

This document explains how to use the planning-with-files workflow for PAL MCP development.

## Overview

PAL MCP Server uses **native planning mode** (planning-with-files workflow). This means:

- **No plugin required** - Just Claude Code's built-in planning skills
- **File-based tracking** - Plans stored in `.claude/plans/` directory
- **Git-friendly** - Plans are markdown files you can commit
- **Flexible structure** - Adapt to your workflow needs

## How It Works

### 1. Activating Planning Mode

When starting complex work, ask Claude Code to create a plan:

```
Create a plan for adding a new MCP tool for semantic code search
```

Claude will create three files in `.claude/plans/`:
- `task_plan.md` - Task breakdown with steps and dependencies
- `findings.md` - Investigation notes and discoveries
- `progress.md` - Execution log with timestamps

### 2. Plan Structure

#### task_plan.md
Hierarchical task breakdown with status tracking:

```markdown
# Task: Add Semantic Code Search Tool

## Goal
Create MCP tool for semantic code search using embeddings

## Dependencies
- Vectorize integration (external)
- Embedding provider (Google or OpenAI)

## Tasks

### 1. Design Tool Schema ⏳
**Status:** In Progress
**Assignee:** Claude
**Dependencies:** None

- [ ] Define input parameters (query, file_types, scope)
- [ ] Design response format (results with similarity scores)
- [ ] Plan error handling (no embeddings, rate limits)

### 2. Implement Provider Adapter 📋
**Status:** Not Started
**Dependencies:** Task 1

- [ ] Create embeddings provider interface
- [ ] Implement Google Gemini embedding adapter
- [ ] Add fallback to OpenAI embeddings
```

#### findings.md
Investigation notes and discoveries:

```markdown
# Findings: Semantic Code Search Tool

## 2026-01-16 14:30 - Initial Investigation

### Existing Patterns
Found similar embedding logic in:
- `providers/google_provider.py` - text-embedding-004 model
- `tools/chat.py` - Uses embeddings for context retrieval

### Technical Constraints
- MCP protocol: Max response size 1MB
- Embedding dimensions: 768 (text-embedding-004)
- Cost: $0.00001 per 1K tokens (cheap!)

### Open Questions
- Should we cache embeddings in file metadata?
- How to handle large codebases (>10K files)?
- Which embedding model: Google vs OpenAI?
```

#### progress.md
Execution log with decisions:

```markdown
# Progress: Semantic Code Search Tool

## 2026-01-16 14:00 - Started
**Decision:** Use Google text-embedding-004 for cost efficiency

## 2026-01-16 14:30 - Schema Design Complete
**Completed:**
- Input schema with Pydantic validation
- Response format with similarity scores
- Error handling for rate limits

**Next Steps:**
- Implement provider adapter
- Add caching layer for embeddings

## 2026-01-16 15:00 - Provider Adapter Implementation
**Blocker:** Need to test with real API - requires Google API key setup
**Workaround:** Use mock responses for initial testing
```

### 3. Working with Plans

**Update plans as you work:**
```
Update the plan - schema design is complete, starting provider implementation
```

**Check progress:**
```
Show me the current plan status
```

**Pivot when needed:**
```
Update findings - discovered we need to add file chunking for large files
```

**Complete tasks:**
```
Mark task 1 as complete in the plan
```

## MCP-Specific Planning Patterns

### Tool Development

When planning a new MCP tool:

1. **Schema Design** (task_plan.md)
   - Input parameters with types and validation
   - Output format with examples
   - Error conditions and codes

2. **Investigation** (findings.md)
   - Review similar existing tools
   - Check MCP spec compliance
   - Document provider capabilities needed

3. **Implementation** (progress.md)
   - Create Pydantic models
   - Implement handler function
   - Write tests (unit + integration)
   - Document in `docs/tools/`

**Example Plan:**
```markdown
# Task: Add mcp__pal__refactor Tool

## Tasks
1. [ ] Design schema (input: code, focus_areas; output: suggestions)
2. [ ] Create Pydantic models in tools/refactor/schemas.py
3. [ ] Implement handler in tools/refactor/refactor.py
4. [ ] Add multi-model support (Gemini Pro + O3)
5. [ ] Write tests in tests/tools/test_refactor.py
6. [ ] Document in docs/tools/refactor.md
```

### Provider Integration

When adding a new AI provider:

1. **Configuration** (task_plan.md)
   - Models to support
   - API requirements (auth, endpoints)
   - Special capabilities (vision, function calling)

2. **Research** (findings.md)
   - Provider API documentation review
   - Rate limits and pricing
   - Error codes and handling

3. **Development** (progress.md)
   - Create provider adapter
   - Add model config JSON
   - Test with real API
   - Document setup steps

**Example Plan:**
```markdown
# Task: Add Mistral AI Provider

## Findings
- API: https://api.mistral.ai/v1
- Models: mistral-large, mistral-medium, mistral-small
- Auth: API key in Authorization header
- Rate: 100 req/min (tier 1)
- Cost: $0.002/1K tokens (medium)

## Tasks
1. [ ] Create providers/mistral_provider.py
2. [ ] Add conf/mistral_models.json
3. [ ] Implement chat completion
4. [ ] Add vision support (mistral-large only)
5. [ ] Test rate limiting
6. [ ] Document in docs/providers/mistral.md
```

### Bug Investigation

For complex bugs:

1. **Reproduction** (findings.md)
   - Steps to reproduce
   - Error messages and stack traces
   - Environment details

2. **Root Cause** (findings.md)
   - Hypothesis testing
   - Code inspection notes
   - Related issues/commits

3. **Fix Plan** (task_plan.md)
   - Code changes needed
   - Tests to add
   - Regression prevention

**Example Plan:**
```markdown
# Bug: clink tool fails with large responses

## Findings
- Error: "Response exceeds 1MB MCP limit"
- Occurs when CLI output >1MB (e.g., long code reviews)
- Root cause: MCP protocol constraint, not our code

## Fix Plan
1. [ ] Add response streaming for large outputs
2. [ ] Implement chunking in clink/handler.py
3. [ ] Update schema to support pagination
4. [ ] Test with 5MB+ responses
5. [ ] Document limitation in docs/tools/clink.md
```

## Plan Lifecycle

### Starting New Work

```
Create a plan for [feature/bug/refactor]
```

Claude creates initial plan files.

### During Development

```
Update findings - discovered [new information]
```

```
Mark task X as complete
```

```
Add new task: [task description]
```

### Completing Work

```
Archive the plan - work is complete
```

Claude can move plan files to `archived/` directory (optional).

### Abandoning Work

```
Close the plan - decided not to proceed with this approach
```

Add note in progress.md about why work was stopped.

## Best Practices

### ✅ Do

- **Create plans for multi-step work** - Anything >3 steps benefits from planning
- **Update findings frequently** - Document discoveries as you go
- **Track blockers** - Note dependencies and blockers in progress.md
- **Keep plans focused** - One feature/bug/refactor per plan
- **Commit completed plans** - Plans are documentation of your work

### ❌ Don't

- **Don't plan trivial tasks** - Simple bug fixes don't need formal plans
- **Don't let plans go stale** - Update or close plans that are no longer relevant
- **Don't create parallel plans** - Focus on one plan at a time
- **Don't skip findings** - Investigation notes are valuable for future work

## Directory Structure

```
.claude/plans/
├── README.md              # Planning guide (this file)
├── SETUP.md              # Setup instructions (this file)
├── task_plan.md          # Current active task plan
├── findings.md           # Current investigation notes
├── progress.md           # Current execution log
└── archived/             # Completed plans (optional)
    ├── 2026-01-tool-x/
    │   ├── task_plan.md
    │   ├── findings.md
    │   └── progress.md
    └── 2026-01-bug-y/
        └── findings.md
```

## Integration with Git

Plans are git-friendly:

```bash
# Commit plan with feature work
git add .claude/plans/task_plan.md
git add src/tools/new_tool.py
git commit -m "feat: add semantic search tool (see .claude/plans/task_plan.md)"

# Archive completed plans
mkdir .claude/plans/archived/2026-01-semantic-search
mv .claude/plans/*.md .claude/plans/archived/2026-01-semantic-search/
git add .claude/plans/archived/
git commit -m "docs: archive semantic search tool plan"
```

## Troubleshooting

### Plan files not being created

**Issue:** Claude doesn't create plan files when asked

**Solution:** Be explicit:
```
Create a planning-with-files plan for [task]
```

### Plans getting too large

**Issue:** task_plan.md has 100+ tasks

**Solution:** Break into multiple plans:
```
Split this plan into separate plans for: (1) provider integration, (2) tool implementation, (3) testing
```

### Lost track of current plan

**Issue:** Multiple plan files in directory

**Solution:** Check progress.md timestamps:
```
Show me the most recent plan based on progress.md timestamps
```

## Examples

### Example 1: New Tool Development

```
User: Create a plan for adding a SQL query debugging tool

Claude: I'll create a plan for the SQL debugging tool.

[Creates task_plan.md with schema design, provider selection, implementation steps]

User: I've found that PostgreSQL errors are most common in our logs. Update findings.

Claude: I've updated findings.md with PostgreSQL error analysis.

User: Let's focus on PostgreSQL first, defer MySQL support. Update the plan.

Claude: I've updated task_plan.md to prioritize PostgreSQL, moved MySQL to future work.
```

### Example 2: Bug Investigation

```
User: Create a plan to investigate why consensus tool is slow with 5+ models

Claude: I'll create an investigation plan.

[Creates findings.md with reproduction steps, initial profiling]

User: Update findings - I see sequential API calls, no parallelization

Claude: Updated findings.md with parallelization issue. Should I add a fix task to the plan?

User: Yes, add task to parallelize model API calls

Claude: Added parallelization task to task_plan.md with estimated 70% latency reduction.
```

### Example 3: Refactoring Project

```
User: Plan a refactor to extract common provider code into base class

Claude: I'll create a refactoring plan.

[Creates task_plan.md with code analysis, migration steps, rollback plan]

User: Show affected providers

Claude: Based on findings.md, 8 providers will be affected:
- google_provider.py
- openai_provider.py
- anthropic_provider.py
[...list continues...]

User: Start with google_provider as pilot, update progress

Claude: Updated progress.md - starting pilot with google_provider, will validate before migrating others.
```

## Related Commands

### Planning Skills
- `/plan` - Create a plan (if skill available)
- Standard chat works fine for native mode

### PAL MCP Tools
- `mcp__pal__planner` - Interactive planning tool
- `mcp__pal__thinkdeep` - Deep investigation
- `mcp__pal__codereview` - Code review workflow

## Questions?

See:
- **[README.md](README.md)** - Planning directory overview
- **[../../CLAUDE.md](../../CLAUDE.md)** - Development guidelines
- **[../../docs/tools/planner.md](../../docs/tools/planner.md)** - PAL planner tool docs

---

**Last Updated:** 2026-01-16
**Planning Mode:** Native (planning-with-files)
**Claude Code Version:** 2.0.64+

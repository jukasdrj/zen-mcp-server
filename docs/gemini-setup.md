# Gemini CLI Setup

This guide explains how to configure PAL MCP Server to work with [Gemini CLI](https://github.com/google-gemini/gemini-cli).

## Available Gemini Models

When using the native Gemini API with PAL MCP Server, you have access to:

**Preview Models (Latest Generation):**
- **`gemini-3-pro-preview`** (alias: `pro`) - Latest reasoning-first model with 1M context, 65K output, adaptive thinking
- **`gemini-3-flash-preview`** (alias: `flash3`) - Best multimodal model with strong coding and state-of-the-art reasoning
- Both support extended thinking, function calling, JSON mode, and vision

**Stable Production Models:**
- **`gemini-2.5-pro`** (alias: `pro25`) - Stable Pro with 2M context, advanced reasoning
- **`gemini-2.5-flash`** (alias: `flash`) - Lightning-fast stable version with 1M context
- **`gemini-2.5-flash-lite`** (alias: `lite`) - Ultra-lightweight for speed and cost efficiency

**Convenience Aliases:**
- `gemini-flash-latest` → `gemini-2.5-flash`
- `gemini-pro-latest` → `gemini-2.5-pro`

All models are defined in `/Users/juju/dev_repos/zen-mcp-server/conf/gemini_models.json`.

## Prerequisites

- PAL MCP Server installed and configured
- Gemini CLI installed
- At least one API key configured in your `.env` file

## Configuration

1. Edit `~/.gemini/settings.json` and add:

```json
{
  "mcpServers": {
    "pal": {
      "command": "/path/to/pal-mcp-server/pal-mcp-server"
    }
  }
}
```

2. Replace `/path/to/pal-mcp-server` with your actual PAL MCP installation path (the folder name may still be `pal-mcp-server`).

3. If the `pal-mcp-server` wrapper script doesn't exist, create it:

```bash
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
exec .pal_venv/bin/python server.py "$@"
```

Then make it executable: `chmod +x pal-mcp-server`

4. Restart Gemini CLI.

All 15 PAL tools are now available in your Gemini CLI session.

## Troubleshooting

### Common Issues

**403/404 Errors with Gemini API:**

If you encounter 403 Forbidden or 404 Not Found errors when using Gemini models, this is typically caused by using deprecated or incorrect model names. As of January 2026, ensure you're using the correct model names:

**Correct Model Names:**
- `gemini-3-pro-preview` (not `gemini-3-pro`)
- `gemini-3-flash-preview` (not `gemini-3-flash`)
- `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite` (stable models)

**Using Aliases:**
The easiest approach is to use short aliases which are automatically mapped to the correct models:
- `pro` → `gemini-3-pro-preview`
- `flash3` → `gemini-3-flash-preview`
- `flash` → `gemini-2.5-flash`
- `pro25` → `gemini-2.5-pro`
- `lite` → `gemini-2.5-flash-lite`

These aliases are defined in `conf/gemini_models.json` and ensure you always use the correct model names.

**API Key Issues:**

For Gemini 3.0 Preview models, ensure you're using a paid API key. Free tier keys may have limited access to preview models.

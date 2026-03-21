# Claude Development Guide for PAL MCP Server

This file contains essential commands and workflows for developing and maintaining the PAL MCP Server when working with Claude. Detailed instructions are in `.claude/rules/`.

@.claude/rules/code-quality.md
@.claude/rules/testing.md
@.claude/rules/development-workflow.md
@.claude/rules/troubleshooting.md

## Server Management

### Setup/Update the Server
```bash
# Run setup script (handles everything)
./run-server.sh
```

This script will:
- Set up Python virtual environment
- Install all dependencies
- Create/update .env file
- Configure MCP with Claude
- Verify API keys

### View Logs
```bash
# Follow logs in real-time
./run-server.sh -f

# Or manually view logs
tail -f logs/mcp_server.log
```

## File Structure Context

- `./code_quality_checks.sh` - Comprehensive quality check script
- `./run-server.sh` - Server setup and management
- `communication_simulator_test.py` - End-to-end testing framework
- `simulator_tests/` - Individual test modules
- `tests/` - Unit test suite
- `tools/` - MCP tool implementations
- `providers/` - AI provider implementations
- `systemprompts/` - System prompt definitions
- `logs/` - Server log files

## Environment Requirements

- Python 3.9+ with virtual environment
- All dependencies from `requirements.txt` installed
- Proper API keys configured in `.env` file

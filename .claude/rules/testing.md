# Testing

## Unit Tests

```bash
# Run all unit tests (excluding integration tests that require API keys)
python -m pytest tests/ -v -m "not integration"

# Run specific test file
python -m pytest tests/test_refactor.py -v

# Run specific test function
python -m pytest tests/test_refactor.py::TestRefactorTool::test_format_response -v

# Run tests with coverage
python -m pytest tests/ --cov=. --cov-report=html -m "not integration"
```

## Integration Tests (requires API keys)

```bash
# Run integration tests that make real API calls
./run_integration_tests.sh

# Run integration tests + simulator tests
./run_integration_tests.sh --with-simulator
```

Integration tests use the local-llama model via Ollama (free, unlimited). Requires `CUSTOM_API_URL` set to your local Ollama endpoint. Excluded from code quality checks to keep them fast.

## Simulator Tests

Simulation tests test the MCP server in a 'live' scenario using configured API keys.

**IMPORTANT**: After any code changes, restart your Claude session for the changes to take effect.

```bash
# Quick test mode - 6 essential tests for maximum coverage
python communication_simulator_test.py --quick

# Full suite
python communication_simulator_test.py

# List all available tests
python communication_simulator_test.py --list-tests

# Run individual test (recommended for isolation)
python communication_simulator_test.py --individual <test_name>

# Verbose output for debugging
python communication_simulator_test.py --individual <test_name> --verbose
```

Quick mode tests: `cross_tool_continuation`, `conversation_chain_validation`, `consensus_workflow_accurate`, `codereview_validation`, `planner_validation`, `token_allocation_validation`.

All simulator tests should be run individually for optimal testing and better error isolation.

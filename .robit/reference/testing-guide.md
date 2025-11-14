# Testing Guide for Zen MCP Server

**Framework:** pytest
**Coverage:** unit, simulator, integration
**Last Updated:** November 2025

---

## 🎯 Three-Tier Testing Strategy

### 1. Unit Tests (`tests/`)
- **Purpose:** Test individual functions/classes
- **Speed:** Fast (~30 seconds)
- **Cost:** Free (VCR cassettes)
- **Run:** `pytest tests/ -v -m "not integration"`

### 2. Simulator Tests (`simulator_tests/`)
- **Purpose:** End-to-end workflow validation
- **Speed:** Medium (~5 minutes)
- **Cost:** Uses real APIs
- **Run:** `python communication_simulator_test.py --quick`

### 3. Integration Tests
- **Purpose:** Real API validation with approved models
- **Speed:** Medium (~5 minutes)
- **Cost:** Uses real API keys (Gemini/Grok)
- **Run:** `./run_integration_tests.sh`

---

## 🔧 Unit Testing with VCR

### Basic Pattern

```python
import pytest
from tools.chat import ChatTool, ChatRequest

@pytest.mark.vcr(cassette_name="chat_basic.yaml")
def test_chat_basic():
    """Test basic chat functionality"""
    tool = ChatTool()
    request = ChatRequest(
        prompt="Explain async/await",
        model="gemini-2.5-pro",
        working_directory_absolute_path="/tmp"
    )
    
    result = tool.execute(request)
    
    assert result["success"]
    assert "async" in result["response"].lower()
```

### VCR Cassettes

**Location:** `tests/{provider}_cassettes/`

**Recording new cassette:**
```bash
# Delete old cassette
rm tests/gemini_cassettes/chat_basic.yaml

# Run test (records new cassette)
pytest tests/test_chat.py::test_chat_basic -v
```

---

## 🔄 Simulator Testing

### Quick Mode (Recommended)

```bash
# Run 6 essential tests (~2 minutes)
python communication_simulator_test.py --quick
```

### Individual Test

```bash
# Run specific test with verbose output
python communication_simulator_test.py --individual cross_tool_continuation --verbose
```

### Available Tests

- `basic_conversation` - Basic chat flow
- `cross_tool_continuation` - Cross-tool memory
- `conversation_chain_validation` - Thread validation
- `consensus_workflow_accurate` - Consensus tool
- `token_allocation_validation` - Token management

---

## 🧪 Integration Testing

### Setup

Integration tests use the approved Gemini and Grok models. Ensure your API keys are configured:

```bash
# Set environment variables
export GEMINI_API_KEY="your-gemini-key"
export XAI_API_KEY="your-xai-key"
```

### Run Tests

```bash
# All integration tests (uses approved models)
./run_integration_tests.sh

# With simulator tests
./run_integration_tests.sh --with-simulator

# Specific test
pytest tests/test_prompt_regression.py -v -m integration
```

---

## ✅ Quality Checks

```bash
# Run all quality checks
./code_quality_checks.sh

# Manual checks
ruff check . --fix
black .
isort .
pytest tests/ -v -m "not integration"
```

---

## 📚 References

- Tests: `tests/`, `simulator_tests/`
- Patterns: `.robit/patterns.md`
- CI/CD: `.github/workflows/`

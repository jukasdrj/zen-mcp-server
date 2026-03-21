# Troubleshooting

## Server Issues

```bash
# Check if Python environment is set up correctly
./run-server.sh

# View recent errors
grep "ERROR" logs/mcp_server.log | tail -20

# Check virtual environment
which python
# Should show: .../pal-mcp-server/.pal_venv/bin/python
```

## Test Failures

```bash
# First try quick test mode to see if it's a general issue
python communication_simulator_test.py --quick --verbose

# Run individual failing test with verbose output
python communication_simulator_test.py --individual <test_name> --verbose

# Check server logs during test execution
tail -f logs/mcp_server.log

# Run tests with debug output
LOG_LEVEL=DEBUG python communication_simulator_test.py --individual <test_name>
```

## Log Files

```bash
# Main server log (all activity including debug info) - 20MB max, 10 backups
tail -f logs/mcp_server.log

# Tool activity only (TOOL_CALL, TOOL_COMPLETED, etc.) - 20MB max, 5 backups
tail -f logs/mcp_activity.log

# Search for specific patterns
grep "ERROR" logs/mcp_server.log
grep "tool_name" logs/mcp_activity.log
```

For programmatic log analysis (used by tests):
```python
from simulator_tests.log_utils import LogUtils
recent_logs = LogUtils.get_recent_server_logs(lines=500)
errors = LogUtils.check_server_logs_for_errors()
matches = LogUtils.search_logs_for_pattern("TOOL_CALL.*debug")
```

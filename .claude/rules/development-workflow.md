# Development Workflow

## Before Making Changes
1. Ensure virtual environment is activated: `source .pal_venv/bin/activate`
2. Run quality checks: `./code_quality_checks.sh`
3. Check logs to ensure server is healthy: `tail -n 50 logs/mcp_server.log`

## After Making Changes
1. Run quality checks again: `./code_quality_checks.sh`
2. Run integration tests locally: `./run_integration_tests.sh`
3. Run quick test mode for fast validation: `python communication_simulator_test.py --quick`
4. Run relevant specific simulator tests if needed: `python communication_simulator_test.py --individual <test_name>`
5. Check logs for any issues: `tail -n 100 logs/mcp_server.log`
6. Restart Claude session to use updated code

## Before Committing/PR
1. Final quality check: `./code_quality_checks.sh`
2. Run integration tests: `./run_integration_tests.sh`
3. Run quick test mode: `python communication_simulator_test.py --quick`
4. Run full simulator test suite (optional): `./run_integration_tests.sh --with-simulator`
5. Verify all tests pass 100%
